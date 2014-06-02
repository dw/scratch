#!/usr/bin/env python2.5

import httplib
import logging
import mimetypes
import os
import re
import sys

import webob

mimetypes.add_type('image/vnd.microsoft.icon', 'ico')

LOG = logging.getLogger('routinglib')
LOG.setLevel(logging.INFO)

VAR_RE = re.compile(r'\${([^}]+)}')


def _re(o, flags, full):
    if isinstance(o, (tuple, list)):
        o = '|'.join(o)
    if full:
        o += '$'
    return re.compile(o, flags)

def _req(env):
    req = env.get('routinglib.Request')
    if not req:
        env['routinglib.Request'] = req = webob.Request(env)
    return req

def _make_expander(s):
    bits = VAR_RE.split(s)
    if len(bits) == 1:
        return lambda env: s
    expr_bits = []
    while bits:
        expr_bits.append(repr(bits.pop()))
        expr_bits.append('str(%s)' % bits.pop())
        expr_bits.append(repr(bits.pop()))
    cod = compile('+'.join(reversed(expr_bits)), '', 'eval')
    def expand(env):
        env2 = env.copy()
        env2['req'] = _req(env)
        return eval(cod, env2)
    return expand

def _log(_name, fn, *args, **kwargs):
    if LOG.level > logging.DEBUG:
        return fn
    args = filter(None, [
        ', '.join(repr(a) for a in args),
        ', '.join('%s=%r' % p for p in kwargs.iteritems()) ])
    frame = sys._getframe(2) # inspect is noticeably slow.
    msg = '%s:%d: %s(%s)' % (os.path.basename(frame.f_code.co_filename),
                             frame.f_lineno, _name, ', '.join(args))
    def logger(*args):
        result = fn(*args)
        LOG.info('%s -> %r', msg, result)
        return result
    return logger

# Predicates.
def host(pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('host', lambda env: match(env.get('HTTP_HOST', '')),
                pat=pat, flags=flags, full=full)

def ssl(on):
    on = 'on' if on else 'off'
    return _log('ssl', lambda env: env.get('HTTPS') == on,
                on=on)

def path(pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('path', lambda env: match(env.get('PATH_INFO', '')),
                pat=pat, flags=flags, full=full)

def getvar(name, pat='.*', flags=0, full=True):
    match = _re(pat, flags, full).match
    def pred(env):
        value = _req(env).GET.get(name)
        return value is not None and match(value)
    return _log('getvar', pred, name=name, pat=pat, flags=flags, full=full)

def postvar(name, pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('postvar',
                lambda env: match(_req(env).POST.get(name, '')),
                name=name, pat=pat, flags=flags, full=full)

def method(pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('method',
                lambda env: match(env.get('REQUEST_METHOD', '')),
                pat=pat, flags=flags, full=full)

def url(pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('url', lambda env: match(_req(env).path_url),
                pat=pat, flags=flags, full=full)

def urlqs(pat, flags=0, full=True):
    match = _re(pat, flags, full).match
    return _log('urlqs', lambda env: match(_req(env).url),
                pat=pat, flags=flags, full=full)

def admin():
    return _log('admin', lambda env: env.get('USER_ID_ADMIN') == '1')

def allof(*preds):
    return _log('allof', lambda env: all(p(env) for p in preds))

def anyof(*preds):
    return _log('anyof', lambda env: any(p(env) for p in preds))

def invert(pred):
    return _log('invert', lambda env: not pred(env))

def always(boolean=True):
    return _log('always', lambda env: boolean, boolean=boolean)

# Helpers.
def ae_handler(klass, **extra):
    if extra:
        klass = type(klass.__name__ + 'Custom', (klass,), extra)
    return _log('ae_handler', webapp.WSGIApplication([('.*', klass)]),
                klass=klass, extra=extra)

def ae_ext_module(modpath, **extra):
    dirname, modname = os.path.split(modpath)
    modname = os.path.splitext(modname)[0]
    dirname = os.path.abspath(dirname)
    def app(env, start_response):
        sys_path = sys.path[:]
        sys.path.insert(0, dirname)
        try:
            return __import__(modname).main()
        finally:
            sys.path[:] = sys_path
    return _log('ae_ext_module', app, modpath=modpath, extra=extra)

def proxy(dest):
    from google.appengine.api import urlfetch
    def app(env, start_response):
        headers = _req(env).headers
        headers['X-Forwarded-For'] = env.get('REMOTE_ADDR')
        response = urlfetch.fetch(dest, headers=headers)
        code = response.status_code
        status = '%s %s' % (code, httplib.responses.get(code, code))
        start_response(status, response.headers.items())
        return response.content,
    return _log('proxy', app, dest=dest)

def redirect(dest, permanent=True):
    return respond(301 if permanent else 302, Location=dest)

def respond(code, entity=None, **headers):
    msg = '%s %s' % (code, httplib.responses.get(code, code))
    headers = [(k.replace('_', '-').title(), v) for (k, v) in headers.iteritems()]
    entity_ = entity

    if 'Content-Type' not in (h[0] for h in headers):
        headers.append(('Content-Type', 'text/html'))
        entity = '<h1>%s</h1>' % msg
    entity = () if entity is None else entity,

    def app(env, start_response):
        start_response(msg, headers)
        return entity
    return _log('status', app, code, entity=entity_, headers=headers)

def static(path, expires=60*60*24*7, ctype=None, **headers):
    expand = _make_expander(path)
    headers = headers.items()

    e404 = respond(404)

    import stat
    def app(env, start_response):
        path = expand(env)
        try:
            st = os.stat(path)
        except OSError:
            st = None
        if not (st and stat.S_ISREG(st.st_mode)):
            return e404(env, start_response)
        ctype_ = ctype or mimetypes.guess_type(path)[0]
        resp = webob.Response(body=file(path).read(),
                              last_modified=st.st_mtime,
                              content_type=ctype_,
                              headerlist=headers,
                              conditional_response=True)
        resp.cache_expires(expires)
        return resp(env, start_response)
    return app

def ae_main(app):
    from google.appengine.ext.webapp import util
    import __main__ as mod
    # "if caller is main"
    if sys._getframe(1).f_code.co_filename == mod.__file__:
        mod.main = lambda: util.run_wsgi_app(app)
        mod.main()

# Modifiers.
def rebase(pat, repl='', flags=0, prefix=True, full=False):
    if isinstance(pat, (tuple, list)):
        pat = '|'.join(pat)
    if prefix:
        pat = '^(?:%s)' % pat
    sub = _re(pat, flags, full).sub

    def rebaser(env):
        env['PATH_INFO'] = sub(repl, env.get('PATH_INFO', ''))
    return _log('rebase', rebaser,
                pat=pat, repl=repl, flags=flags, prefix=prefix, full=full)

# Router.
def chain(*pairs):
    def app(env, start_response):
        for p in pairs:
            if type(p) is tuple:
                if p[0](env): # pred,app pair
                    return p[1](env, start_response)
            else: # modifier
                p(env)
    return _log('chain', app)

API = dict((fn.__name__, fn) for fn in (
    host, ssl, path, getvar, postvar, method, admin, allof, anyof, invert,
    ae_handler, ae_ext_module, proxy, respond, static, redirect, ae_main,
    rebase, chain, always, url, urlqs
))

def install(dct, debug=False):
    dct.update(API)
    if debug:
        LOG.setLevel(logging.DEBUG)

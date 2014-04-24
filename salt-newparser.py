import fnmatch
import re
import sys

_GRAMMAR_SOURCE = """
    wschar = ' ' | '\\t' | '\\n' | '\\r' | '\\v'
    bws = wschar+

    colon_word = <(~':' anything)+>
    comma_word = <~((',' | wschar) anything)+>
    ws_word = <(~' ' anything)+>

    ip_octet = digit{1,3}:oct ?(0 <= int(oct, 10) <= 255)
    subnet_mask = digit{1,2}:subn ?(0 <= int(subn, 10) <= 32)
    ip_addr = <ip_octet ('.' ip_octet){3}>
    subnet = <ip_addr '/' subnet_mask>

    glob_list = comma_word:one (',' comma_word)+:rest -> [one]+rest

    grain_rule = 'G' '@' colon_word:name ':' ws_word:pat
        -> lambda m,name=name,pat=pat: match(pat, m.get_grain(name) or '')

    pcre_id_rule = 'E' '@' word:pat
        -> lambda m,pat=pat: re.match(pat, m.name)

    grain_pcre_rule = 'P' '@' colon_word:name ':' word:pat
        -> lambda m,pat=pat,nat=name: re.match(pat, m.get_grain(name) or '')

    minion_list_rule = 'L' '@' glob_list:pats
        -> lambda m,pats=pats: any(match(pat, m.name) for pat in pats)

    pillar_rule = 'I' '@' comma_word:name ':' word:pat
        -> lambda m,name=name,pat=pat: match(m.get_pillar(name) or '')

    subnet_rule = 'S' '@' subnet:subnet
        -> lambda m,subnet=subnet: in_subnet(subnet, m.get_grain('ipv4'))

    ip_rule = 'S' '@' ip_addr:ip
        -> lambda m,ip=ip: m.get_grain('ipv4') == ip

    glob_rule = word:pat
        -> lambda m,pat=pat: match(pat, m.name)

    compound_rule = grain_rule
        | pcre_id_rule
        | grain_pcre_rule
        | minion_list_rule
        | pillar_rule
        | subnet_rule
        | ip_rule
        | glob_rule

    paren_expr = '(' ws expr:E ws ')'
        -> E

    not_expr = 'n' 'o' 't' bws expr:E
        -> lambda m,E=E: not E(m)

    or_expr = expr:L bws 'o' 'r' bws expr:R
        -> lambda m,L=L,R=R: L(m) or R(m)

    and_expr = expr:L bws 'a' 'n' 'd' bws expr:R
        -> lambda m,L=L,R=R: L(m) and R(m)

    expr = paren_expr
        | not_expr
        | or_expr
        | and_expr
        | compound_rule
"""

try:
    import _parser
except ImportError:
    try:
        import ometa.builder
        import ometa.grammar
    except ImportError:
        sys.stderr.write('%s: pymeta must be installed if _parser.py\n'
                         'has not been generated.\n' % (__name__,))
        raise
    _parser = None


class MinionInfo(object):
    def __init__(self, opts, name):
        self.name = name

    def get_grain(self, name, default=None):
        return '123'

    def get_pillar(self, name, default=None):
        return '123'



om = ometa.grammar.OMeta(_GRAMMAR_SOURCE)
tree = om.parseGrammar('dave')

print ometa.builder.writePython(tree, _GRAMMAR_SOURCE)
exit()


x.makeGrammar(_GRAMMAR_SOURCE, {
    'in_subnet': lambda *_: False,
    'match': fnmatch.fnmatch
}, name='foo')

_matcher_cache = {}

def get_matcher(expr):
    if expr not in _matcher_cache:
        _matcher_cache[expr] = GRAMMAR(expr).expr()
    return _matcher_cache[expr]


matcher = get_matcher('G@pants:321')
minion = MinionInfo({}, 'saltmaster')
print matcher(minion)

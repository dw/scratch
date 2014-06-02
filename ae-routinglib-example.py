#!/usr/bin/env python

import routinglib

routinglib.install(globals(), True)


EXIM_PYTHON = chain(
    rebase(r'/exim-python(\.php|/)?', '/'),

    (path('/docs.css'),
     redirect('http://exim-python.googlecode.com/files/docs.css')),
    (path('/exim-4.32py1.html'),
     redirect('http://exim-python.googlecode.com/files/exim-4.32py1.html')),
    (path('/exim-4.32py1.patch'),
     redirect('http://exim-python.googlecode.com/files/exim-4.32py1.patch')),
    (path('/exim-4.32py1.tar.bz2'),
     redirect('http://exim-python.googlecode.com/files/exim-4.32py1.tar.bz2')),
    (path('/exim-4.60py1.html'),
     redirect('http://exim-python.googlecode.com/files/exim-4.60py1.html')),
    (path('/exim-4.60py1.patch'),
     redirect('http://exim-python.googlecode.com/files/exim-4.60py1.patch')),
    (path('/exim-4.60py1.tar.bz2'),
     redirect('http://exim-python.googlecode.com/files/exim-4.60py1.tar.bz2')),

    (path(('/exim-4.30-py0.1.tar.gz',
           '/exim-4.30-python.diff',
           '/exim-4.30py1.patch',
           '/exim-4.31-py1.tar.gz',
           '/exim-4.31-python.diff',
           '/exim-4.31py1.patch')),
     status(410)),

    (path('.*'),
     redirect('http://code.google.com/p/exim-python/')),
)


DW = chain(
    rebase(r'/dw(homepage.php|/)?', '/'),

    (path('/'),
     redirect('http://www.dmw.me.uk/')),
    (path('/py-usoap.php'),
     status(410)),
    (path('/exim-python.*'),
     EXIM_PYTHON),

    # Stupid RSS readers.
    (anyof(allof(path('/weblog(.php)?'), getvar('rss')),
           path('/weblog/rss')),
     proxy('http://www.dmw.me.uk/weblog/rss')),

    (path('/weblog(.php)?'),
     redirect('http://www.dmw.me.uk/weblog/')),

    # P(r'/dw/clips.*', 'http://www.dmw.me.uk/clips\\1') no substitutions
    (path('/(misc-)?software.php'),
     redirect('http://freshmeat.net/~davemw/')),
    (path('/schlog.php'),
     redirect('http://code.google.com/p/schlog/')),
    (path('/greasemonkey/?'),
     redirect('http://userscripts.org/users/1147/scripts')),
    (path('/greasemonkey/sourceforge-ddl.user.js'),
     redirect('http://userscripts.org/scripts/source/611.user.js')),

    (path(r'/py-asterisk(|\.php)?'),
     redirect('http://py-asterisk.berlios.de/')),
    (path(r'/cdr_mysql(|\.php)?'),
     redirect('http://py-asterisk.berlios.de/cdr_mysql.php')),
    (path(r'/pbx_config_mgr(|\.php)?'),
     redirect('http://py-asterisk.berlios.de/pbx_config_mgr.php')),

    (path('/schlog/schlog-0.5.tar.bz2'),
     redirect('http://schlog.googlecode.com/files/schlog-0.5.tar.bz2')),
    (path('/img/schlog.png'),
     redirect('http://schlog.googlecode.com/files/schlog.png')),
    (path('/img/schlog2.png'),
     redirect('http://schlog.googlecode.com/files/schlog2.png')),
    (path('/remote-addr.php'),
     redirect('http://ip-address.domaintools.com/')),

    (path('/tmp/Reference/paramiko.*'),
     redirect('http://www.lag.net/paramiko/')),
    (path('/tmp/astdoc,*'),
     redirect('http://www.asterisk.org/index.php?menu=download')),
    (path('/tmp/.*'),
     status(410)),
    (path('.*'),
     status(404))
)


APP = chain(
    (path('/'),
     redirect('https://mail.google.com/a/botanicus.net/')),

    (path('/dw/?.*'),
     DW),

    (path('.*'),
     status(404))
)


ae_main(APP)

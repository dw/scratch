
import re
import sys

import czipfile
import lxml.etree
import lxml.html


class Target(object):
    bad = set('{http://www.w3.org/1999/xhtml}%s' % s for s in
              'head'.split())
    blk = set('{http://www.w3.org/1999/xhtml}%s' % s for s in
              'br p div blockquote section ul ol h1 h2 h3 h4 h5 h6'.split())

    def __init__(self):
        self.curbad = 0
        self.bits = []

    def start(self, tag, attr):
        if self.curbad or (tag in self.bad):
            self.curbad += 1

    def end(self, tag):
        if self.curbad:
            self.curbad -= 1
            if tag in self.blk:
                self.bits.append(' ')

    def data(self, data):
        if not self.curbad:
            self.bits.append(data)

    def comment(self, text):
        pass

    def close(self):
        return ''.join(self.bits)


fn = 'World Order Kissinger.epub'
def x():
    zf = czipfile.ZipFile(fn)
    for name in zf.namelist():
        if name.endswith('html'):
            s = zf.read(name)
            targ = Target()
            pp = lxml.etree.XMLParser(target=targ)
            pp.feed(s)
            sys.stdout.write(pp.close().encode('utf-8'))

x()


import lxml.html
import urllib
import urlparse

url = 'https://mail.python.org/pipermail/pypy-dev/'

fp = urllib.urlopen('https://mail.python.org/pipermail/pypy-dev/')
doc = lxml.html.parse(fp)

links = []
for a in doc.getroot().cssselect('a'):
    if a.attrib['href'].endswith('.gz'):
        links.append(urlparse.urljoin(url, a.attrib['href']))


links.reverse()
for link in links:
    print link

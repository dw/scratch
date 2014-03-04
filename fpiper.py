
import os
import lxml.html
import urllib
import urlparse


replace = [s.split() for s in '''January 01
    February 02
    March 03
    April 04
    May 05
    June 06
    July 07
    August 08
    September 09
    October 10
    November 11
    December 12'''.splitlines()]


url = 'https://mail.python.org/pipermail/python-list/'

fp = urllib.urlopen(url)
doc = lxml.html.parse(fp)

links = []
for a in doc.getroot().cssselect('a'):
    if a.attrib['href'].endswith('.gz'):
        links.append(urlparse.urljoin(url, a.attrib['href']))


links.reverse()
for link in links:
    olink = link
    for k, v in replace:
        link = link.replace(k, v)
    print 'wget -O', os.path.basename(link), olink

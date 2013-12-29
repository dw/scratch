
import urllib2

url = 'http://uwstream1.somafm.com:80'

req = urllib2.Request(url, headers={
    'Icy-MetaData': '1'
})

fp = urllib2.urlopen(req)
fp.status = fp.readline()
fp.headers = {}

for line in fp:
    k, _, v = line.rstrip('\r\n').partition(':')
    if not k:
        break
    fp.headers[k] = v


interval = int(fp.headers['icy-metaint'])
seen = 0

while True:
    if seen == interval:
        mlength = ord(fp.read(1)) * 16
        if mlength:
            meta = fp.read(mlength).rstrip('\0')
            print meta
        seen = 0

    chunk = min(4096, interval - seen)
    data = fp.read(chunk)
    if not data:
        break
    seen += len(data)

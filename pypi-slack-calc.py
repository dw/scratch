
import hashlib
import os
import gzip
import zlib
import bz2
import tarfile
import zipfile



def read_zip(path):
    zf = zipfile.ZipFile(open(path, 'rb'))
    for name in zf.namelist():
        yield name, zf.read(name)


def read_tgz(path):
    tf = tarfile.open(path, 'r:gz')
    for member in tf:
        try:
            fp = tf.extractfile(member)
            if fp:
                yield member.name, fp.read()
        except KeyError:
            pass

def read_bz2(path):
    tf = tarfile.open(path, 'r:bz2')
    for member in tf:
        try:
            fp = tf.extractfile(member)
            if fp:
                yield member.name, fp.read()
        except KeyError:
            pass


def consider(path):
    if path[-4:].lower() in '.egg.whl.zip':
        return read_zip, (path,)
    elif path.endswith('.tar.gz') or path.endswith('.tgz'):
        return read_tgz, (path,)
    elif path.endswith('.tar.bz2') or path.endswith('.tbz') \
            or path.endswith('.tbz2'):
        return read_bz2, (path,)


def scan():
    for path, dirs, files in os.walk('.'):
        for dirname in dirs:
            dirpath = os.path.join(path, dirname)
            c = consider(dirpath)
            if c:
                for name, data in c[0](*c[1]):
                    yield name, data

        for filename in files:
            filepath = os.path.join(path, filename)
            c = consider(filepath)
            if c:
                for name, data in c[0](*c[1]):
                    yield name, data



unique = 0
slack = 0
slack_count = 0
md5s = {}

def stat():
    waste = float(unique) / (slack or 1)
    print 'unique count=%d slack count=%d  uniqueMB=%d slackMB=%d waste=%f'%\
        (len(md5s), slack_count, unique/1048576., slack/1048576., waste)

i = 0
for name, data in scan():
    i += 1
    if not (i % 1000):
        stat()
    h = hashlib.md5(data).digest()
    size = md5s.get(h)
    if size is not None:
        slack += size
        slack_count += 1
    else:
        size = len(zlib.compress(data))
        unique += size
        md5s[h] = size

stat()

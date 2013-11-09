
# Iteratively build up 'hashes' pickle from a bunch of known paths. hashes is a
# set of the MD5 of the first 4kb of data from every file from those paths.
# Used by uncrash-dehashinate.py.

import cPickle as pickle
import hashlib
import os


try:
    with open('hashes', 'rb') as fp:
        known = pickle.load(fp)
except IOError:
    known = set()


# bases = 'Music', 'Pictures'
#bases = '/Applications', '/Library'
bases = '/System',

for basedir in bases:
    for dirpath, dirs, files in os.walk(basedir):
        for filename in files:
            path = os.path.join(dirpath, filename)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, 'rb') as fp:
                    md5 = hashlib.md5(fp.read(4096)).digest()
                    known.add(md5)
                print path
            except IOError:
                print '!!', path
                continue

with open('hashes', 'wb') as fp:
    fp.write(pickle.dumps(known, 2))

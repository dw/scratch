
# Use '../hashes' pickle created by uncrash-dehashinate.py to walk the contents
# of the current directory looking for dups. The purpose of this script is to
# eliminate backed up files from photorec output, following the failure (and
# recovery) of a disk.

import cPickle as pickle
import hashlib
import os

yes = no = 0

with open('../hashes', 'rb') as fp:
    known = pickle.load(fp)


for basedir in '.':
    for dirpath, dirs, files in os.walk(basedir):
        for filename in files:
            path = os.path.join(dirpath, filename)
            with open(path, 'rb') as fp:
                md5 = hashlib.md5(fp.read(4096)).digest()
            if md5 in known:
                print path
                yes += 1
            else:
                no += 1


print yes, no, float(yes) / no


#
# ntfs-3g and Tuxera NTFS allow creation of Unixey filenames containing various
# invalid characters. Unfortunately ntfs-3g fsck sucks, so one must use Windows
# CHKDSK, which will immediately replace all the invalid characters with
# Unicode ordinals in the private use plane.
#
# Additionally different OS have different approaches for normalizing Unicode
# characters during editing.
#
# That really sucks if the filesystem in question is a huge backup that's now
# horribly out of sync. This script fixes the impedence mismatch by restoring
# the original Unixey filenames after CHKDSK has completed, and normalizing
# them to 'NFD' decomposde form.
#
# tl;dr DONT STORE UNIX-NATIVE TREES ON NTFS
#

import shutil
import os
import unicodedata

replace = {
    0xf022: u':',
    0xf025: u'?',
    0xf028: u' ',
    0xf029: u'.',
    0xf021: u'*',
}

def normal(name):
    u = name.decode('utf-8')
    ut = u.translate(replace)
    un = unicodedata.normalize('NFD', ut)
    return un.encode('utf-8')


if 0:
    bad = set()
    for path, dirs, files in os.walk('.'):
        for filename in files:
            fullpath = os.path.join(path, filename)
            for ch in fullpath.decode('utf-8'):
                o = ord(ch)
                if 0xE000 <= o <= 0xF8FF:
                    if o not in bad and o not in replace:
                        print [hex(o), fullpath]
                        bad.add(o)



elif 1:
    for path, dirs, files in os.walk('.'):
        for dirname in dirs:
            dirname2 = normal(dirname)
            if dirname != dirname2:
                print['rename', dirname, dirname2]
                continue
                new = os.path.join(path, dirname2)
                if os.path.exists(new):
                    shutil.rmtree(new)
                os.rename(os.path.join(path, dirname),
                          os.path.join(path, dirname2))
                dirs[dirs.index(dirname)] = dirname2

        for filename in files:
            filename2 = normal(filename)
            if filename != filename2:
                print['rename', filename, filename2]
                continue
                os.rename(os.path.join(path, filename),
                          os.path.join(path, filename2))

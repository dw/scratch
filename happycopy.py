#!/usr/bin/env python

# Picture the scene: converting a drive from HFS+ to NTFS so your TV can play
# movies from it directly.
#
# Problem: copying media files from partition at the end of the drive to the
# new partition at the start of the drive.
#
# Attempt #1: Finder / rsync: 10.4mb/sec, disk rattles like crazy.
# Investigating, since this is a removable disk, write caching is minimal.
# Result: read bandwidth is artificially starved because writes are being
# forced to disk sooner than necessary. Result: huge amount of time wasted on
# disk seeks.
#
# Attempt #2: happycopy.py!@#"!one. Beat rsync at its own game by a clean
# 4mb/sec, with 10% lower CPU utilization. Read 1gb at a time, then write that
# buffer out, rinse repeat. Result: nice fast sequential reads.
#
# Attempt 1 IO graphs:
#   Read: /-?_\-/_|?-\-/-|_?_|/-\/--\/
#   Write: /-?_\-/_|?-\-/-|_?_|/-\/--\/
#
# Attempt 2 IO graphs:
#   Read:  /------------\_____________/--------------\_______
#   Write: _____________/-------------\______________/-------
#
# Result: happy :)
#

import os
import sys
import time

MAX_BUF = 1048576 * 1024 * 1


def die(msg):
    print msg
    raise SystemExit(1)

def target_path(src_dir, dst_dir, path):
    rel = os.path.relpath(path, src_dir)
    return os.path.join(dst_dir, rel)


seen = 0
start = time.time()

def do_copy(src_path, dst_path):
    if os.path.exists(dst_path) and \
            os.path.getsize(src_path) == os.path.getsize(dst_path):
        print 'skip', src_path
        return

    global seen

    ifp = file(src_path, 'rb')
    ofp = file(dst_path, 'wb')
    while True:
        got = ifp.read(MAX_BUF)
        if not got:
            break

        print 'write', dst_path, len(got)
        ofp.write(got)
        seen += len(got)
        dur = time.time() - start
        print '%.2fMb/sec' % ((float(seen) / dur) / 1048576)
        got = ''

def main():
    if len(sys.argv) != 3:
        die('Usage: prog src_dir dst_dir')

    src_dir, dst_dir = sys.argv[1:]
    if not os.path.isdir(src_dir):
        die('src dir must be dir')

    for dirpath, dirnames, filenames in os.walk(src_dir):
        tgt = target_path(src_dir, dst_dir, dirpath)
        if not os.path.exists(tgt):
            os.makedirs(tgt)
        elif not os.path.isdir(tgt):
            print 'gah!', tgt

        for filename in filenames:
            path = os.path.join(dirpath, filename)
            new_path = target_path(src_dir, dst_dir, path)
            do_copy(path, new_path)


if __name__ == '__main__':
    main()

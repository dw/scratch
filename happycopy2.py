#!/usr/bin/env python

#
# Like happycopy.py, but make efforts to fill the buffer when encountering many
# small files (e.g. OS X .sparsebundle)
#

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


def stats(s, size, dur):
    print >> sys.stderr, s, '%.2fMb/sec' % ((float(size) / dur) / 1048576)


def read_phase(to_copy):
    buffered = 0
    buffers = []
    while to_copy and buffered < MAX_BUF:
        src, dst, start = to_copy.pop()
        with open(src, 'rb') as fp:
            fp.seek(start)
            buf = fp.read(MAX_BUF - buffered)
        if buf:
            buffered += len(buf)
            buffers.append((src, dst, start, buf))
            to_copy.append((src, dst, start + len(buf)))

    return buffered, buffers


def write_phase(buffers):
    for src_path, dst_path, start, buf in buffers:
        with file(dst_path, 'wb') as fp:
            fp.seek(start)
            fp.write(buf)
            fp.truncate()
        print 'write', dst_path, len(buf)


def do_copy(to_copy):
    start_ts = time.time()
    read = 0
    read_secs = 0
    written = 0
    write_secs = 0

    while to_copy:
        t0 = time.time()
        buffered, buffers = read_phase(to_copy)
        read_secs += time.time() - t0
        read += buffered
        stats('Read', read, read_secs)

        t0 = time.time()
        write_phase(buffers)
        write_secs += time.time() - t0
        written += buffered
        stats('Write', written, write_secs)
        stats('Throughput', written, time.time() - start_ts)


def main():
    if len(sys.argv) != 3:
        die('Usage: prog src_dir dst_dir')

    src_dir, dst_dir = sys.argv[1:]
    if not os.path.isdir(src_dir):
        die('src dir must be dir')

    to_copy = []

    for dirpath, dirnames, filenames in os.walk(src_dir):
        tgt = target_path(src_dir, dst_dir, dirpath)
        if not os.path.exists(tgt):
            os.makedirs(tgt)
        elif not os.path.isdir(tgt):
            print 'gah!', tgt

        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            dst_path = target_path(src_dir, dst_dir, src_path)
            if os.path.exists(dst_path) and \
                    os.path.getsize(src_path) == os.path.getsize(dst_path):
                print 'skip', src_path
            else:
                to_copy.append((src_path, dst_path, 0))

    print 'going to copy', len(to_copy), 'files'
    to_copy.reverse()
    do_copy(to_copy)


if __name__ == '__main__':
    main()

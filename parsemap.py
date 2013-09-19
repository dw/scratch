
#
# parsemap.py <pid> <addr>
# Figure out what memory mapping <addr> belongs to and print it, along with the
# absolute offset into the mapping (or file).
#

import sys


maps = []

for line in file('/proc/%s/maps' % sys.argv[1]):
    bits = line.rstrip().split(None, 5)
    low, _, high = bits[0].partition('-')
    path = bits[5] if len(bits) > 5 else '<anon>'
    maps.append((int(low, 16), int(high, 16), int(bits[2], 16), path))



addr = int(sys.argv[2], 16)

for low, high, offset, path in maps:
    if low <= addr <= high:
        print hex(low), '-', hex(high), path, '@', hex(offset + (addr - low))
        break



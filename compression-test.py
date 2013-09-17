
from zlib import compress
from acid.keylib import pack_int

target = 4000
cur = []

total_un = 0
total_co = 0
total_ba = 0
total_li = 0


def longest_common_prefix(strs):
    plen = min(len(s) for s in str)
    prefix = strs[0][:plen]



def pack_sizes(cur):
    s = pack_int('', len(cur))
    s += 
    return pack_int('', len(cur)) + ''.join('   ' + pack_int('', len(l)) for l in cur)

def do_out():
    global cur, out
    out = pack_sizes(cur)
    out += compress('\n'.join(cur))

def do_stats():
    global total_un, total_co, total_ba, total_li
    total_un += len('\n'.join(cur))
    total_co += len(out)
    total_ba += 1
    total_li += len(cur)


for line in open('/var/log/messages'):
    cur.append(line)
    do_out()
    if len(out) > target:
        cur.pop()
        do_out()
        do_stats()
        cur = [line]
        print total_li / total_ba

do_out()
do_stats()
del out, cur


pprint(globals())

print float(total_un) / total_co

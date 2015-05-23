# because I can never remember what package/tool provides this
import time

def parse(line):
    bits = line.split()
    return (bits[0].rstrip(':'),
            int(bits[1]),
            int(bits[2]),
            int(bits[9]),
            int(bits[10]),
            int(bits[11]))

def get(idx):
    with open('/proc/net/dev') as fp:
        lines = fp.readlines()
    return parse(lines[2+idx])


lrbytes = lrpkt = lwbytes = lwpkt = lwcoll = 0
while 1:
    g = get(2)
    name, rbytes, rpkt, wbytes, wpkt, wcoll = g
    print '%s: rx %5.2f Mbps %5.2f MiB/s %5d pps tx %5.2f Mbps %5.2f MiB/s %5d pps' %\
        (name,
        ((8 * (rbytes - lrbytes)) / 1e6),
        (((rbytes - lrbytes)) / (1024. * 1024)),
        (rpkt - lrpkt),
        ((8 * (wbytes - lwbytes)) / 1e6),
        (((wbytes - lwbytes)) / (1024. * 1024)),
        (wpkt - lwpkt))
    lrbytes, lrpkt, lwbytes, lwpkt, lwcoll = rbytes, rpkt, wbytes, wpkt, wcoll
    time.sleep(1)

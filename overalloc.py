
def d(n):
    tp = (n>>4) + (n>>3)
    if tp < 64:
        tp = 64
    if tp > 2048:
        tp = 2048
    print[n,tp]


for x in range(0, 9999, 512):
    d(x)

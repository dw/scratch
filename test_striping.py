
# write for 0.5 sec to one stripe, 0.5 to next stripe, rinse repeat
# use iostat to verify writes are hitting independent drives

# lvcreate -n lmdb -L 4G -I 4 -i 2 k2 /dev/sda2 /dev/sdb1
# iostat -x 1 /dev/sda2 /dev/sdb1

import os
from time import time

sec = '0' * 4096

f = open('/dev/k2/gubby', 'w', 4096)
while True:
    for flip_flop in 0, 1:
        stop = time() + 0.5
        f.seek(4096 * flip_flop)
        while time() < stop:
            f.write(sec)
            f.flush()
            f.seek(f.tell() + 4096)
        os.system('sync')


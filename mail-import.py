
import mailbox

import acid
import acid.encoders



store = acid.open('LmdbEngine', path='/tmp/email.lmdb', map_size=1048576000000,
                     writemap=True)
coll = store.add_collection('emails')



def bat():
    last_key = ()
    while last_key is not None:
        txn = store.engine.begin(write=True)
        found, made, last_key = coll.batch(
            lo=last_key, txn=txn, max_bytes=32767,
            packer=acid.encoders.ZLIB_PACKER)
        txn.commit()
        print 'found=', found, 'made=', made


'''
mbox = mailbox.Maildir('/home/backup/eldil/mail/botanicus')
it = iter(mbox)
env = store.engine.env
idx = 0

while True:
    with env.begin(write=True) as txn:
        txn = type(store.engine)(env=env, txn=txn)
        print idx, store.engine.env.stat()
        try:
            for _ in xrange(1000):
                coll.put(str(next(it)), txn=txn)
        except StopIteration:
            break

        idx += 1000
'''


import os
fp = os.popen('find /home/backup/eldil/mail/botanicus -type f')
it = iter(fp)

env = store.engine.env
idx = 0

while True:
    with env.begin(write=True) as txn:
        txn = type(store.engine)(env=env, txn=txn)
        print idx, store.engine.env.stat()
        try:
            for _ in xrange(1000):
                coll.put(file(next(it).strip()).read(), txn=txn,
                         packer=acid.encoders.ZLIB_PACKER)
        except StopIteration:
            break

        idx += 1000

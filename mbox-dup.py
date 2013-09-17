
import hashlib
import mailbox



def key_func(msg):
    bits = []
    for key in ('From', 'To', 'Cc', 'Date', 'Subject'):
        bits.append(msg.get(key, ''))
    bits.append(msg.fp.read())
    return hashlib.md5(''.join(bits)).digest(), bits[:-1]


mb = mailbox.Maildir('gm', create=False)

keys = set()

dups = 0
count = 0

for msgkey, msg in mb.iteritems():
    key, desc = key_func(msg)
    if key in keys:
        print 'found dup:', desc
        dups += 1
    count += 1
    keys.add(key)



print 'dups %d, count %d' % (dups, count)

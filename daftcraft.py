
# abuse a hash to behave like a cipher. never do this

import hashlib
import hmac
import os

def transform(s, key, iv):
    h = hashlib.sha512(key+iv)
    buf = bytearray(s)
    blen = len(buf)
    digest = h.digest()
    try:
        i = 0
        while i < blen:
            h.update(digest)
            digest = h.digest()
            for char in bytearray(digest):
                buf[i] ^= char
                i += 1
    except IndexError:  # (blen % len(digest)) > 0
        pass
    return str(buf)

def box(s, tkey, skey):
    iv = os.urandom(16)
    msg = transform(s, tkey, iv)
    mac = hmac.HMAC(skey, iv+msg, hashlib.sha256).digest()
    return ''.join([mac, iv, msg])

def unbox(box, tkey, skey):
    mac = box[:hashlib.sha256().digest_size]
    iv_msg = box[len(mac):]
    if mac == hmac.HMAC(skey, iv_msg, hashlib.sha256).digest():
        return transform(iv_msg[16:], tkey, iv_msg[:16])

def box64(s, tkey, skey):
    boxed = box(s, tkey, skey)
    return boxed.encode('base64').replace('\n', '').rstrip('=\n')

def unbox64(b64, tkey, skey):
    try:
        boxed = (b64 + ('=' * (len(b64)%4))).decode('base64')
    except:
        return
    return unbox(boxed, tkey, skey)


if __name__ == '__main__':
    key = os.urandom(64)
    for x in range(3):
        boxed = box64('test123', key, key)
        print [len(boxed), len(box('text123', key, key)),
               boxed, unbox64(boxed, key, key),
               unbox64(boxed.upper(), key, key)]

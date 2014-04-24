
s = """7|3|12|https://groups.google.com/forum/|122677A9A2C79957CE525475379B4DB1|7v|AK7YvITdHGXr6wTmucaIKRnu209R_jU9VQ:1395743752486|_|isNewerMessageAvailableInTopic|k|82|org.joda.time.ReadableInstant|docker-dev|3paGTWD6xyw|8l|1|2|3|4|5|6|4|7|8|9|9|7|10|10|0|0|11|12|USRG7yw|0|"""


ss = lambda s: tbl[int(s) - 1]
more = lambda: bits.pop(0)

bits = s.split('|')
print 'proto ver', more()
flags = int(more())
print 'flags', flags
tbllen = int(more())
print 'tbllen', tbllen
tbl = bits[:tbllen]
bits = bits[tbllen:]
print 'tbl', tbl
print
print 'rest', bits

print 'base url', ss(more())
print 'policy name', ss(more())
if flags & 2:
    print 'token.value', ss(more())
    print 'token.xsrf', ss(more())

print 'interface', ss(more())
print 'method name', ss(more())
nargs = int(more())
print 'nargs', nargs
print ss(more())

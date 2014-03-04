
import cffi

ffi = cffi.FFI()
ffi.cdef('typedef size_t off_t;')
ffi.cdef('ssize_t pread(int fd, void *buf, size_t count, off_t offset);')
ffi.cdef('void perror(const char *);')

lib = ffi.dlopen(None)
pread = lib.pread

start = 0x7fff2537b000

thing = ffi.new('char[]', 8192)
thingbuf = ffi.buffer(thing)


fp = open('/proc/15928/mem', 'rb')
fd = fp.fileno()

print pread(fd, thing, len(thing), start)
file('thing', 'w').write(thingbuf[:])

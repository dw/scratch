
import cffi

ffi = cffi.FFI()
ffi.cdef('typedef size_t off_t;')
ffi.cdef('ssize_t pread(int fd, void *buf, size_t count, off_t offset);')
ffi.cdef('void perror(const char *);')

lib = ffi.dlopen(None)
pread = lib.pread


thing = ffi.new('char[]', 4096)
thingbuf = ffi.buffer(thing)


fp = open('/proc/7404/mem', 'rb')
fd = fp.fileno()

print pread(fd, thing, len(thing), 0x7f8e825ad000)
print thingbuf[:]

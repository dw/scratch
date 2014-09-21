
import struct
import zlib
from cStringIO import StringIO

from PySide import *
import numpy as np

app = QtGui.QApplication([])

path = '/Users/dmw/src/xxxxxxxxxxxxxxxxxxxxxxxx/images-old/image1.png'

image = QtGui.QImage(path)
width = image.width()
height = image.height()

print image, width, height
print image.format(), 'wxh', width, height
print image.allGray()
print 

def toarray():
    return np.ndarray((height, width*4), dtype=np.uint8, buffer=image.bits())

nda = toarray()
print nda
print

#tsl = toscanline()

crc = lambda s, n=None: uint32(zlib.crc32(s, n) & 0xffffffff)
uint32 = lambda n: struct.pack('>L', n)

png_header = ''.join(chr(c) for c in (137, 80, 78, 71, 13, 10, 26, 10))
chunk = lambda n, b: [uint32(len(b)), n, b, crc(b, zlib.crc32(n))]

def writepng(wl):
    scanlines = np.insert(nda, 0, values=0, axis=1)
    wl([png_header])
    wl(chunk('IHDR', struct.pack('>LLBBBBB', width, height,
                                 8,    # bit depth
                                 2+4,  # colour type
                                 0,    # compression method
                                 0,    # filter method
                                 0)))  # interlace method
    wl(chunk('IDAT', zlib.compress(buffer(scanlines), 1)))
    wl(chunk('IEND', ''))

writepng(open('out.png', 'wb').writelines)

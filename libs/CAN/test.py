import ctypes
import struct

lib = ctypes.CDLL('./CANlib.so')
#f = lib.init
f = lib.init
f.restype = None
f()
#f.restype = ctypes.POINTER(ctypes.c_ubyte* 5)
#f.argtypes = [ctypes.c_ubyte]
#g = ctypes.CDLL('./library.so').change
g = lib.readBrake
g.restype = ctypes.POINTER(ctypes.c_ubyte * 8)
h = lib.readGun
h.restype = ctypes.POINTER(ctypes.c_ubyte * 8)
while True:
    #read = g().contents
    read = h().contents
    print('---------------------------')
    for i in read:
        print(i)
#g()
#for i in f(0x1f).contents:
    #if i == '\x00':
        #print(struct.unpack('B',i)[0])
#        print(i)

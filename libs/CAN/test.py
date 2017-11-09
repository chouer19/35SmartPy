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
#g()
#for i in f(0x1f).contents:
    #if i == '\x00':
        #print(struct.unpack('B',i)[0])
#        print(i)

import ctypes
import struct

class GNSS:
    def __init__(self):
        self.lib = ctypes.CDLL('/home/ubuntu/workspace/35SmartPy/libs/UART/UARTlib.so')
        self.init = self.lib.init
        self.init()

        self.readGNSS = self.lib.readGNSS
        self.readGNSS.restype = ctypes.POINTER(ctypes.c_ubyte * 60)
        self.bytes = self.readGNSS().contents
        self.bytes_new = self.readGNSS().contents

    def read(self):

        self.bytes = self.bytes_new
        self.byte_new = self.readGNSS().contents
        mark = 0
        for i in range(0,59):
            mark = i
            if self.bytes[i] == 0xaa and self.bytes[i+1] = 0x55:
                break
        
        if mark == 59 and not(self.bytes[59] == 0xaa and self.bytes_new[0] = 0x55):
            mark = 60

        res = self.bytes[mark:60]

        for i in range(0,mark):
            res.append(self.bytes_new[i])

        self.length, = struct.unpack('B',bytearray(res[2]))
        self.mode, = struct.unpack('B',bytearray(res[3]))
        self.time1, = struct.unpack('H',bytearray(res[4:6]))
        self.time2, = struct.unpack('i',bytearray(res[6:10]))
        self.num, = struct.unpack('B',bytearray(res[10]))
        self.lat, = float(struct.unpack('i',bytearray(res[10:14]))) / (10**7)
        self.lon, = float(struct.unpack('i',bytearray(res[14:18]))) / (10**7)
        self.height, = float(struct.unpack('i',bytearray(res[18:22]))) / (1000)
        self.v_n, = float(struct.unpack('i',bytearray(res[22:26]))) / (1000)
        self.v_e, = float(struct.unpack('i',bytearray(res[26:30]))) / (1000)
        self.v_earth, = float(struct.unpack('i',bytearray(res[30:34]))) / (1000)
        self.roll, = float(struct.unpack('i',bytearray(res[34:38]))) / (1000)
        self.pitch, = float(struct.unpack('i',bytearray(res[38:42]))) / (1000)
        self.head, = float(struct.unpack('I',bytearray(res[42:46]))) / (1000)
        self.a_n, = float(struct.unpack('h',bytearray(res[46:48]))) / (1000)
        self.a_e, = float(struct.unpack('h',bytearray(res[48:50]))) / (1000)
        self.a_earth, = float(struct.unpack('h',bytearray(res[50:52]))) / (1000)
        self.v_roll, = float(struct.unpack('h',bytearray(res[52:54]))) / (1000)
        self.v_pitch, = float(struct.unpack('h',bytearray(res[54:56]))) / (1000)
        self.v_head, = float(struct.unpack('h',bytearray(res[56:58]))) / (1000)
        self.status, = struct.unpack('B',bytearray(res[59]))

import thread
import time
import ctypes

lib = ctypes.CDLL('/home/ubuntu/workspace/35SmartPy/CAN/brain/CANlib.so')
init = lib.init
read = lib.readGun
read.restype = ctypes.POINTER(ctypes.c_ubyte * 8)
send = lib.sendBrake

init()



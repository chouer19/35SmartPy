import ctypes

lib = ctypes.CDLL('./CANlib.so')

init = lib.init
f = lib.sendBrake
g = lib.sendGun

init()
f(0,0)
g(0,0)

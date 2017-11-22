import ctypes

lib = ctypes.CDLL('./CANlib.so')

init = lib.init
f = lib.sendBrake
g = lib.sendGun
h = lib.sendSteer

init()
f(0,0)
g(0,0)
h(15,0,0,0)

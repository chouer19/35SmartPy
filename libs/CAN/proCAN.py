import ctypes
import struct

#msg for CAN of 35 smart car
#ID: 0x199, read this gun message from CAN
class Gun_read:
    def __init__(self, Mode=0x00 , Depth=0x00 , speed=0x00 ):
        #byte[0] 0:manual control, 1: pc control
        self.Mode = Mode
        #byte[1] control depth
        self.Depth = Depth
        #byte[7] speed
        self.speed = speed
        pass

#ID: 0x200, send this gun message to CAN
class Gun_send:
    def __init__(self, Mode = 0x00 , Depth = 0x00 ):
        #byte[0] control mode, 0:manual control, 1:pc control
        self.Mode = Mode
        #byte[1] control depth
        self.Depth = Depth
        pass

#ID: 0X100, read this brake message from CAN
class Brake_read:
    def __init__(self, motorTime=0x0000 , remoteStatus=0x00 , buttonStatus=0x00 , pedalStatus=0x00 , canStatus=0x00 , remoteControl=0x00 , realStatus=0x00 ):
        # byte[0] & byte[1], time of brake-motor runing 0x00  0x00 0x00 , time = byte[0x00 ] * 256 + byte[1]
        self.motorTime = motorTime
        # byte[2], if the brake button is pressed down 0x00 , 0x00  is false and 1 is true
        self.buttonStatus = buttonStatus
        # byte[3], if the remote brake control is pressed down 0x00 , 0x00 is false and 1 is true
        self.remoteStatus = remoteStatus
        # byte[4], if the pedal is pressed down 0x00 ,
        self.pedalStatus = pedalStatus
        # byte[5], if the can send brake message 0x00 ,
        self.canStatus = canStatus
        # byte[6], reserve for the pc, reverse once remote control is pressed down
        self.remoteControl = remoteControl
        # byte[7], real status of brake, effect of brake
        self.realStatus = realStatus
        pass

#ID: 0x99, send this message of brake to CAN
class Brake_send:
    def __init__(self, Mode=0x00 , Depth=0x00 ):
        #byte[0], 0:start braking, 1:stop braking
        self.Mode = Mode
        #byte[1], control depth
        self.Depth = Depth

#ID: 0x401, read this steer message from CAN
class Steer_read:
    def __init__(self, Mode=0x00 , torque= 0x00 , exception= 0x00 , angleH= 0x00 , angleL= 0x00 , calib= 0x00 , check= 0x00 ):
        #byte[0], 0x00:stop control, 0x10: manul control, 0x20: pc control, 0x55: xor check error
        self.Mode = Mode
        #byte[1], torque
        self.torque = torque
        #byte[2], error message
        #0x21    0x22    0x23    0x24    0x25    0x26
        #0x32    0x34    0x35
        #0x31
        self.exception = exception
        #byte[3]
        self.angleH = angleH
        #byte[4], angle = byte[3] * 256 + byte[4] - 1024
        self.angleL = angleL
        #byte[5], no, done, failed, success
        self.calib = calib
        self.by6 = 0x00
        #byte[7], xor check
        self.check = check

class Steer_send:
    def __init__(self, Mode= 0x00, angleH = 0x00, angleL= 0x00 , angle_calib= 0x00):
        #byte[0], 0x00:stop control, 0x10:manual control, 0x20:pc control
        self.Mode = Mode
        #byte[3]
        self.angleH = angleH
        #byte[4]
        self.angleL = angleL
        #byte[5], 0x55, only worked when manual control
        self.calib = angle_calib



class CAN:
    def __init__(self):
        self.gunRead = Gun_read()
        self.gunSend = Gun_send()
        self.brakeRead = Brake_read()
        self.brakeSend = Brake_send()
        self.steerRead = Steer_read()
        self.steerSend = Steer_send()

        #self.lib = ctypes.CDLL('/home/ubuntu/workspace/35SmartPy/CAN/brain/CANlib.so')
        self.lib = ctypes.CDLL('./CANlib.so')
        self.CANinit = self.lib.init

        self.CANreadGun = self.lib.readGun
        self.CANreadGun.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANreadBrake = self.lib.readBrake
        self.CANreadGun.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANreadSteer= self.lib.readSteer
        self.CANreadSteer.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANsendGun = self.lib.sendGun
        self.CANsendGun.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte]

        self.CANsendBrake = self.lib.sendBrake
        self.CANsendBrake.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte]

        self.CANsendSteer= self.lib.sendSteer
        self.CANsendSteer.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

        #run init for ***
        self.CANinit()

    def readGun(self):
        read = self.CANreadGun().contents
        self.gunRead.Mode = read[0]
        self.gunRead.Depth = read[1]
        self.gunRead.speed = read[7]

    def readBrake(self):
        read = self.CANreadBrake().contents
        self.brakeRead.motorTime = read[0] * 256 + read[1]
        self.brakeRead.buttonStatus = read[2]
        self.brakeRead.remoteStatus = read[3]
        self.brakeRead.pedalStatus = read[4]
        self.brakeRead.canStatus = read[5]
        self.brakeRead.remoteControl = read[6]
        self.brakeRead.realStatus = read[7]

    def readSteer(self):
        read = self.CANreadSteer().contents
        self.steerRead.Mode = read[0]
        self.steerRead.torque = read[1]
        self.steerRead.exception = read[2]
        self.steerRead.angleH = read[3]
        self.steerRead.angleL = read[4]
        self.steerRead.calib = read[5]
        self.steerRead.by6 = read[6]
        self.steerRead.check = read[7]

    def sendBrake(self,mode, depth):
        self.brakeSend.Mode = mode
        self.brakeSend.Depth = depth
        self.CANsendBrake(mode,depth)

    def sendGun(self,mode, depth):
        self.gunSend.Mode = mode
        self.gunSend.Depth = depth
        self.CANsendGun(mode, depth)

    def sendSteer(self, mode, angle, calib):
        angleH = int((angle + 1024)/256)
        angleL = int ((angle + 1024) % 256)
        self.steerSend.Mode = mode
        self.CANsendSteer(mode, angleH, angleL, calib)

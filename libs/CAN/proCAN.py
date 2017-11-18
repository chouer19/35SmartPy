import ctypes

#msg for CAN of 35 smart car
#ID: 0x199, read this gun message from CAN
class Gun_read:
    def __init__(self, Mode=0x00 , Depth=0x00 , Speed=0x00 ):
        #byte[0] 0:manual control, 1: pc control
        self.Mode = Mode
        #byte[1] control Depth
        self.Depth = Depth
        #byte[7] Speed
        self.Speed = Speed
        pass

#ID: 0x200, send this gun message to CAN
class Gun_send:
    def __init__(self, Mode = 0x00 , Depth = 0x00 ):
        #byte[0] control Mode, 0:manual control, 1:pc control
        self.Mode = Mode
        #byte[1] control Depth
        self.Depth = Depth
        pass

#ID: 0X100, read this brake message from CAN
class Brake_read:
    def __init__(self, motorTime=0x0000 , remoteStatus=0x00 , buttonStatus=0x00 , pedalStatus=0x00 , canStatus=0x00 , remoteControl=0x00 , realStatus=0x00 ):
        # byte[0] & byte[1], time of brake-motor runing 0x00  0x00 0x00 , time = byte[0x00 ] * 256 + byte[1]
        self.Time = motorTime
        # byte[2], if the brake button is pressed down 0x00 , 0x00  is false and 1 is true
        self.Button = buttonStatus
        # byte[3], if the remote brake control is pressed down 0x00 , 0x00 is false and 1 is true
        self.Remoter = remoteStatus
        # byte[4], if the pedal is pressed down 0x00 ,
        self.Pedal = pedalStatus
        # byte[5], if the can send brake message 0x00 ,
        self.Can = canStatus
        # byte[6], reserve for the pc, reverse once remote control is pressed down
        self.RemoterS = remoteControl
        # byte[7], real status of brake, effect of brake
        self.Real = realStatus
        pass

#ID: 0x99, send this message of brake to CAN
class Brake_send:
    def __init__(self, Mode=0x00 , Depth=0x00 ):
        #byte[0], 0:start braking, 1:stop braking
        self.Mode = Mode
        #byte[1], control Depth
        self.Depth = Depth

#ID: 0x401, read this steer message from CAN
class Steer_read:
    def __init__(self, Mode=0x00 , torque= 0x00 , exception= 0x00 , AngleH= 0x00 , AngleL= 0x00 , Calib= 0x00 , check= 0x00 ):
        #byte[0], 0x00:stop control, 0x10: manul control, 0x20: pc control, 0x55: xor check error
        self.Mode = Mode
        #byte[1], torque
        self.Torque = torque
        #byte[2], error message
        #0x21    0x22    0x23    0x24    0x25    0x26
        #0x32    0x34    0x35
        #0x31
        self.EException = exception
        #byte[3]
        self.AngleH = AngleH
        #byte[4], Angle = byte[3] * 256 + byte[4] - 1024
        self.AngleL = AngleL
        #byte[5], no, done, failed, success
        self.Calib = Calib
        self.By6 = 0x00
        #byte[7], xor check
        self.Check = check

class Steer_send:
    def __init__(self, Mode= 0x00, AngleH = 0x00, AngleL= 0x00 , Calib= 0x00):
        #byte[0], 0x00:stop control, 0x10:manual control, 0x20:pc control
        self.Mode = Mode
        #byte[3]
        self.AngleH = AngleH
        #byte[4]
        self.AngleL = AngleL
        #byte[5], 0x55, only worked when manual control
        self.Calib = Calib



class CAN:
    def __init__(self):
        self.gunRead = Gun_read()
        self.gunSend = Gun_send()
        self.brakeRead = Brake_read()
        self.brakeSend = Brake_send()
        self.steerRead = Steer_read()
        self.steerSend = Steer_send()

        #self.lib = ctypes.CDLL('/home/ubuntu/workspace/35SmartPy/CAN/brain/CANlib.so')
        #self.lib = ctypes.CDLL('/home/xuechong/workspace/35Smart/35SmartPy/libs/CAN/CANlib.so')
        self.lib = ctypes.CDLL('/home/xuechong/workspace/35Smart/35SmartPy/libs/CAN/CANlib.so')
        #self.lib = ctypes.CDLL('./CAN/CANlib.so')
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

        #run init
        self.CANinit()

    def readGun(self):
        read = self.CANreadGun().contents
        self.gunRead.Mode = read[0]
        self.gunRead.Depth = read[1]
        self.gunRead.Speed = read[7]

    def readBrake(self):
        read = self.CANreadBrake().contents
        self.brakeRead.Time = read[0] * 256 + read[1]
        self.brakeRead.Button = read[2]
        self.brakeRead.Remoter = read[3]
        self.brakeRead.Pedal = read[4]
        self.brakeRead.Can = read[5]
        self.brakeRead.RemoterS = read[6]
        self.brakeRead.Real = read[7]

    def readSteer(self):
        read = self.CANreadSteer().contents
        self.steerRead.Mode = read[0]
        self.steerRead.Torque = read[1]
        self.steerRead.EException = read[2]
        self.steerRead.AngleH = read[3]
        self.steerRead.AngleL = read[4]
        self.steerRead.Calib = read[5]
        self.steerRead.By6 = read[6]
        self.steerRead.Check = read[7]

    def sendBrake(self):
        self.CANsendBrake(0x00,0x00)
        self.CANsendBrake(self.brakeSend.Mode,self.brakeSend.Depth)

    def sendGun(self):
        self.CANsendBrake(0x00,0x00)
        self.CANsendGun(self.gunSend.Mode, self.gunSend.Depth)

    def sendSteer(self):
        #AngleH = int((Angle + 1024)/256)
        #AngleL = int ((Angle + 1024) % 256)
        self.CANsendSteer(self.steerSend.Mode, self.steerSend.AngleH, self.steerSend.AngleL, self.steerSend.Calib)


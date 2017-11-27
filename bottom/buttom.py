import sys
import time
import thread
import math
sys.path.append("../libs")
from proContext import *
from proMCU import *
from proUTM import *
import UTM

global speed_set
global speed_back
global speed_mode
global output
global speed_way

output = 0

def main():

    ctx = proContext()

    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8080')

    pubCAN = ctx.socket(zmq.PUB)
    pubCAN.bind('tcp://*:8088')

    mcu = MCU()
    canSpeed = 0
    uartSpeed = 0
    canSteer = 0

    def readGNSS():
        i = 0
        while True:
            mcu.readGNSS()
            content = {"Length":mcu.gnssRead.length,"Mode":mcu.gnssRead.mode,"Time1":mcu.gnssRead.time1,"Time2":mcu.gnssRead.time2, \
                       "Num":mcu.gnssRead.num,"Lat":mcu.gnssRead.lat,"Lon":mcu.gnssRead.lon,"Height":mcu.gnssRead.height, \
                       "V_n":mcu.gnssRead.v_n,"V_e":mcu.gnssRead.v_e,"V_earth":mcu.gnssRead.v_earth, \
                       "Roll":mcu.gnssRead.roll,"Pitch":mcu.gnssRead.pitch,"Head":mcu.gnssRead.head, \
                       "A_n":mcu.gnssRead.a_n,"A_e":mcu.gnssRead.a_e,"A_earth":mcu.gnssRead.a_earth, \
                       "V_roll":mcu.gnssRead.v_roll,"V_pitch":mcu.gnssRead.v_pitch,"V_head":mcu.gnssRead.v_head, \
                       "Status":mcu.gnssRead.status}
            uartSpeed = math.sqrt (mcu.gnssRead.v_n ** 2 + mcu.gnssRead.v_e ** 2 + mcu.gnssRead.v_earth ** 2 )
            i = (i+1) % 9999
            if i%20 ==0:
                print(content)
                print('***************')
                print('*************************************')
            pub.sendPro('CurGNSS',content)
        pass

    def readGun():
        while True:
            time.sleep(0.05)
            mcu.readGun()
            content = {'Mode':mcu.gunRead.Mode, 'Depth':mcu.gunRead.Depth, 'Speed':mcu.gunRead.Speed}
            mcuSpeed = mcu.gunRead.Speed
            pub.sendPro('CANGun',content)
        pass

    def readBrake():
        while True:
            time.sleep(0.05)
            mcu.readBrake()
            content = {'Time':mcu.brakeRead.Time, 'Button':mcu.brakeRead.Button, 'Remoter':mcu.brakeRead.Remoter,\
                       'Pedal':mcu.brakeRead.Pedal, 'Can':mcu.brakeRead.Pedal, 'RemoterS':mcu.brakeRead.RemoterS, \
                       'Real':mcu.brakeRead.Real}
            pubCAN.sendPro('CANBrake',content)

            mcu.readGun()
            content = {'Mode':mcu.gunRead.Mode, 'Depth':mcu.gunRead.Depth, 'Speed':mcu.gunRead.Speed}
            mcuSpeed = mcu.gunRead.Speed
            pubCAN.sendPro('CANGun',content)

            mcu.readSteer()
            content = {'Mode':mcu.steerRead.Mode, 'Torque':mcu.steerRead.Torque, 'EException':mcu.steerRead.EException, \
                       'AngleH':mcu.steerRead.AngleH, 'AngleL':mcu.steerRead.AngleL, 'Calib':mcu.steerRead.Calib, \
                       'By6':mcu.steerRead.By6, 'Check':mcu.steerRead.Check}
            canSteer = mcu.steerRead.AngleH * 256 + mcu.steerRead.AngleL - 1024 + 15
            pubCAN.sendPro('CANSteer',content)
        pass

    def readSteer():
        while True:
            time.sleep(0.05)
            mcu.readSteer()
            content = {'Mode':mcu.steerRead.Mode, 'Torque':mcu.steerRead.Torque, 'EException':mcu.steerRead.EException, \
                       'AngleH':mcu.steerRead.AngleH, 'AngleL':mcu.steerRead.AngleL, 'Calib':mcu.steerRead.Calib, \
                       'By6':mcu.steerRead.By6, 'Check':mcu.steerRead.Check}
            pub.sendPro('CANSteer',content)
        pass

    def alpha(v):
        return 100/ (v**2)

    def sendCmd(content):
        if content['Who'] == 'Brake':
            mcu.brakeSend.Mode = content['Mode']
            mcu.brakeSend.Depth = content['Value']
            mcu.sendBrake()
            pass
        elif content['Who'] == 'Gun':
            mcu.gunSend.Mode = content['Mode']
            mcu.gunSend.Depth = content['Value']
            speed = math.min(canSpeed/3.6, uartSpeed)
            if math.fabs(steer) > alpha(speed)):
                mcu.gunSend.Depth = 0x00
            mcu.sendGun()
            pass
        elif content['Who'] == 'Steer':
            speed = math.min(canSpeed/3.6, uartSpeed)
            steer = content['Value']
            steer = matn.min( steer, alpha(speed) )
            mcu.steerSend.Mode = content['Mode']
            mcu.steerSend.AngleH =  int(steer + 1024)/256)
            mcu.steerSend.AngleL =  int (steer + 1024) % 256)
            mcu.sendSteer()
            pass
        pass

    def recvControl():
        subCAN = ctx.socket(zmq.SUB)
        subCAN.connect('tcp://localhost:8082')
        subCAN.setsockopt(zmq.SUBSCRIBE,'Cmd')
        while True:
            content = subCAN.recvPro()
            sendCmd(content)
        pass

    def recvSteer():
        subSteer = ctx.socket(zmq.SUB)
        subSteer.connect('tcp://localhost:8081')
        subSteer.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
        while True:
            content = subSteer.recvPro()
            content = {'Who':'Steer','Mode':content['Mode'],'Value':content['Value']}
            sendCmd(content)
        pass

    thread.start_new_thread(readGNSS, ())
    #thread.start_new_thread(readGun, ())
    thread.start_new_thread(readBrake, ())
    #thread.start_new_thread(readSteer, ())
    thread.start_new_thread(recvControl, ())
    thread.start_new_thread(recvSteer, ())

    i = 0
    while True:
        i = (i+1) % 9999
        time.sleep(1)

if __name__ == "__main__":
    main()

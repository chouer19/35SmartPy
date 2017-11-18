import sys
import time
import thread

sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *

global speed_set
global speed_back
global speed_mode
global output
global speed_way

output = 0

def main():

    global speed_set
    global speed_back
    global speed_mode
    global speed_way
    can = CAN()
    #publish current all can status
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8080')

    #subcribe current plan about speed and steer
    #steer
    subSteer = ctx.socket(zmq.SUB)
    subSteer.connect('tcp://localhost:8081')
    subSteer.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
    #speed
    subSpeed = ctx.socket(zmq.SUB)
    subSpeed.connect('tcp://localhost:8081')
    subSpeed.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')

    #read from canGun
    speed_back = 0

    #read from planned speed
    speed_set = 0
    speed_mode = 0x00

    #if gun, send gun ,if brake brake.
    speed_way = 'gun'

    #read from CAN BUS, and publish from localhost:8080
    def readAndPub():
        global speed_set
        global speed_back
        global speed_mode
        global output
        global speed_way
        
        i = 0
        while True:
            i = i + 1
            #read and pub gun msg, update speed_back from canBUS
            can.readGun()
            content = {'Mode':can.gunRead.Mode, 'Depth':can.gunRead.Depth, 'Speed':can.gunRead.Speed}
            if i == 25:
                print('--->>>')
                print('readGun : ',content)
            #pub.sendPro('CANgun',content)
            #speed_back = can.gunRead.Speed
            if can.gunRead.SpeedCur - can.gunRead.Speed > 10:
                can.gunRead.SpeedCur = can.gunRead.Speed
            speed_back = can.gunRead.Speed
            #speed_back = s1

            #read and pub brake msg
            can.readBrake()
            content = {'Time':can.brakeRead.Time, 'Button':can.brakeRead.Button, 'Remoter':can.brakeRead.Remoter, 'Pedal':can.brakeRead.Pedal, 'Can':can.brakeRead.Pedal, 'RemoterS':can.brakeRead.RemoterS, 'Real':can.brakeRead.Real}
            if i == 25:
                print('--->>>')
                print('readBrake : ',content)
            #pub.sendPro('CANbrake',content)

            #read and pub steer msg
            can.readSteer()
            content = {'Mode':can.steerRead.Mode, 'Torque':can.steerRead.Torque, 'EException':can.steerRead.EException, 'AngleH':can.steerRead.AngleH, 'AngleL':can.steerRead.AngleL, 'Calib':can.steerRead.Calib, 'By6':can.steerRead.By6, 'Check':can.steerRead.Check}
            #if i == 25:
                #print('--->>>')
                #print('readSteer : ',content)
                #print('******************************************************************************')
                #print('******************************************************************************')
                #i = 0
            #pub.sendPro('CANsteer',content)

            time.sleep(0.02)

    #receive comand from plan(decision) system
    def recvAndSet():
        global speed_set
        global speed_back
        global speed_mode
        global output
        global speed_way
        while True:
            #receive speed
            content = subSpeed.recvPro()
            print('=============================================')
            print('recved speed msg from 8081', content)
            print('=============================================')
            speed_mode = content['Mode']
            can.brakeSend.Mode = speed_mode
            can.gunSend.Mode = speed_mode
            speed_set = content['Value']

            #receive steer
            #content = subSteer.recvPro()
            #print('recved steer msg from 8081', content)
            #can.steerSend.Mode = content['Mode']
            #can.steerSend.AngleH =  int((content['Value']+ 1024)/256)
            #can.seerSend.AngleL =  int ((content['Value'] + 1024) % 256)

    #send msg to CAN BUS
    def sendCmd():
        global speed_set
        global speed_back
        global speed_mode
        global output
        global speed_way
        while True:
            if speed_way == 'brake':
                can.sendBrake()
            if speed_way == 'gun':
                can.sendGun()
            can.sendSteer()
            time.sleep(0.1)

    def control():
        global speed_set
        global speed_back
        global speed_mode
        global output
        global speed_way

        pid10 = PID(P=5.6, I = 9.8, D = 0.0)
        pid10.SetPoint = speed_set
        pid10.setWindup(6.0)

        pid15 = PID(P=5.6, I = 12.8, D = 0.0)
        pid15.SetPoint = speed_set
        pid15.setWindup(6.0)

        pid20 = PID(P=5.0, I = 2.8, D = 0.0)
        pid20.SetPoint = speed_set

        pid30 = PID(P= 5.0, I = 4.8, D = 0.0)
        pid30.SetPoint = speed_set

        pid40 = PID(P= 5.0 , I = 6.0, D = 0.0)
        pid40.SetPoint = speed_set
       
        pid50 = PID(P= 5.0 , I = 6.0, D = 0.0)
        pid50.SetPoint = speed_set

        i = 0 
        while True:
            if speed_set > 55:
                speed_set = 55
            pid10.SetPoint = speed_set
            pid10.update(speed_back)
            pid15.SetPoint = speed_set
            pid15.update(speed_back)
            pid20.SetPoint = speed_set
            pid20.update(speed_back)
            pid30.SetPoint = speed_set
            pid30.update(speed_back)
            pid40.SetPoint = speed_set
            pid40.update(speed_back)
            pid50.SetPoint = speed_set
            pid50.update(speed_back)
            if speed_set <= 10:
                output  = pid10.output
            elif speed_set <= 15:
                output  = pid15.output
            elif speed_set <= 25:
                output  = pid20.output
            elif speed_set <= 35:
                output = pid30.output
            elif speed_set <= 45:
                output = pid40.output
            elif speed_set <= 55:
                output = pid50.output
            print('speed_set is : ',speed_set, 'speed_back', speed_back)
            print('output is : ',output)

            if output > 0:
                speed_way = 'gun'
                can.gunSend.Mode = speed_mode
                #can.gunSend.Depth = min(25, int(output * 5.6))
                if(speed_set <= 10):
                    can.gunSend.Depth = min(35, int(0.42*output))
                if(speed_set <= 15):
                    can.gunSend.Depth = min(35, int(0.42*output))
                elif(speed_set <= 25):
                    can.gunSend.Depth = min(40, int(0.80*output))
                elif(speed_set <= 35):
                    can.gunSend.Depth = min(50, int(0.58*output))
                else:
                    can.gunSend.Depth = min(60, int(0.46*output))
            if output < 0:
                speed_way = 'brake'
                can.brakeSend.Mode = speed_mode
                can.gunSend.Depth = 0
                can.brakeSend.Depth = int(-0.1 * output)
            if output == 0:
                can.brakeSend.Mode = 0x00
                can.brakeSend.Depth = 0x00
                can.gunSend.Mode = 0x00
                can.gunSend.Depth = 0x00
            print('speed_way : ',speed_way, 'gun mode', can.gunSend.Mode, 'depth ',can.gunSend.Depth)
            time.sleep(0.25)

    #recv decision speed, steer, mode
    thread.start_new_thread(recvAndSet, ())
    #read, update can,as fallcack
    thread.start_new_thread(readAndPub, ())
    #control ,update value of cmd to CAN BUS
    thread.start_new_thread(control, ())
    #send, send know control depth
    thread.start_new_thread(sendCmd, ())

    i = 0
    while True:
        i = i + 1
        if i== 5:
            print(i)
        time.sleep(1)

if __name__ == "__main__":
    main()

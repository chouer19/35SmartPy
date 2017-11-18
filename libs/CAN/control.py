import sys
import time
import thread

sys.path.append("../")
from proCAN import *
from proContext import *
from proPID import *

def main():

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
        while True:
            #read and pub gun msg, update speed_back from canBUS
            can.readGUn()
            content = {'Mode':can.gunRead.Mode, 'Depth':can.gunRead.Depth, 'Speed':can.gunRead.Speed}
            pub.sendPro('CANgun',content)
            speed_back = can.gunRead.Speed

            #read and pub brake msg
            can.readBrake()
            content = {'Time':can.brakeRead.Time, 'Button':can.brakeRead.Button, 'Remoter':can.brakeRead.Remoter, 'Pedal':can.brakeRead.Pedal, 'Can':can.brakeRead.Pedal, 'RemoterS':can.brakeRead.RemoterS, 'Real':can.brakeRead.Real}
            pub.sendPro('CANbrake',content)

            #read and pub steer msg
            can.readSteer()
            content = {'Mode':can.brakeRead.Mode, 'Torque':can.brakeRead.Torque, 'EException':can.brakeRead.EException, 'AngleH':can.brakeRead.AngleH, 'AngleL':can.brakeRead.AngleL, 'Calib':can.brakeRead.Calib, 'By6':can.brakeRead.By6, 'Check':can.brakeRead.Check}
            pub.sendPro('CANsteer',content)
            time.sleep(0.02)
            pass
        pass

    #receive comand from plan(decision) system
    def recvAndSet():
        while True:
            #receive speed
            content = subSpeed.recvPro()
            speed_mode = content['Mode']
            can.sendBrake.Mode = speed_mode
            can.sendGun.Mode = speed_mode
            speed_set = content['Value']

            #receive steer
            content = subSteer.recvPro()
            can.sendSteer.Mode = content['Mode']
            can.sendSteer.AngleH =  int((content['Value']+ 1024)/256)
            can.sendSteer.AngleL =  int ((content['Value'] + 1024) % 256)
            pass
        pass

    #send msg to CAN BUS
    def sendCmd():
        while True:
            if speed_way == 'brake':
                can.sendBrake()
            if speed_way == 'gun':
                can.sendGun()
            can.sendSteer()
            time.sleep(0.1)
            pass
        pass

    def control():
        pid = PID()
        pid.clear()
        pid.SetPoint = speed_set
        pid.setSampleTime(10)
        
        while True:
            pid.SetPoint = speed_set
            pid.update(speed_back)
            output = pid.output

            if output > 0:
                speed_way = 'gun'
                can.sendGun.Mode = speed_mode
                can.sendGun.Depth = output * 1.0
            if output < 0:
                speed_way = 'brake'
                can.sendBrake.Mode = speed_mode
                can.sendBrake.Depth = -1 * output * 0.1

            time.sleep(0.05)
            pass
        pass

    #read, update can,as fallcack
    thread.start_new_thread(readAndPub,())
    #control ,update value of cmd to CAN BUS
    thread.start_new_thread(control,())
    #recv decision speed, steer, mode
    threading.start(recvAndSet)
    #send, send know control depth
    threading.start(sendCmd)

if __name__ == "__main__":
    main()

import sys
import time
import thread
sys.path.append("../libs")
from proContext import *
from proPID import *

global speed_set
global speed_back
global speed_mode
global output
output = 0

def main():
    global speed_set
    global speed_back
    global speed_mode

    #publish current all can status
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8082')

    #speed
    #read from canGun
    speed_back = 0
    #read from planned speed
    speed_set = 0
    speed_mode = 0x00

    #receive comand from plan(decision) system
    def recvSpeedAndSet():
        global speed_set
        global speed_mode
        subPlanSpeed = ctx.socket(zmq.SUB)
        subPlanSpeed.connect('tcp://localhost:8081')
        subPlanSpeed.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')
        while True:
            content = subPlanSpeed.recvPro()
            speed_mode = content['Mode']
            speed_set = content['Value']

    def recvSpeedAndBack():
        global speed_back
        subCANSpeed = ctx.socket(zmq.SUB)
        subCANSpeed.connect('tcp://localhost:8080')
        subCANSpeed.setsockopt(zmq.SUBSCRIBE,'CANGun')
        while True:
            content = subCANSpeed.recvPro()
            speed_back = content['Speed']

    def control():
        global speed_set
        global speed_back
        global speed_mode
        global output

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

            if output > 0:
                Depth = 0
                if(speed_set <= 10):
                    Depth = min(35, int(0.42*output))
                if(speed_set <= 15):
                    Depth = min(35, int(0.42*output))
                elif(speed_set <= 25):
                    Depth = min(40, int(0.80*output))
                elif(speed_set <= 35):
                    Depth = min(50, int(0.58*output))
                else:
                    Depth = min(60, int(0.46*output))
                content = {'Who':'Gun','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
            if output < -5:
                Depth = int(-0.1 * output)
                content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
            if output == 0:
                Depth = 0x00
                content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
                Depth = 0x00
                content = {'Who':'Gun','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)

    thread.start_new_thread(recvSpeedAndSet, ())
    thread.start_new_thread(recvSpeedAndBack, ())
    #read, update can,as fallcack
    thread.start_new_thread(control, ())

    i = 0
    while True:
        i = i + 1
        i = i % 999999
        time.sleep(1)

if __name__ == "__main__":
    main()

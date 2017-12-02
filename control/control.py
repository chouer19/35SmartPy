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
global speed_gear
output = 0

def main():
    global speed_set
    global speed_back
    global speed_mode
    global speed_gear
    speed_gear = 0

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
        global speed_gear
        subPlanSpeed = ctx.socket(zmq.SUB)
        subPlanSpeed.connect('tcp://localhost:8081')
        subPlanSpeed.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')
        while True:
            content = subPlanSpeed.recvPro()
            speed_mode = content['Mode']
            speed_set = content['Value']
            speed_gear = content['Gear']

    def recvSpeedAndBack():
        global speed_back
        subCANSpeed = ctx.socket(zmq.SUB)
        subCANSpeed.connect('tcp://localhost:8088')
        subCANSpeed.setsockopt(zmq.SUBSCRIBE,'CANGun')
        while True:
            content = subCANSpeed.recvPro()
            #print(content)
            speed_back = content['Speed']

    def control():
        global speed_set
        global speed_back
        global speed_mode
        global speed_gear
        global output

        pid10 = PID(P=2.6, I = 9.8, D = 0.0)
        pid10.SetPoint = speed_set
        pid10.setWindup(6.0)

        pid15 = PID(P=3.6, I = 12.8, D = 0.0)
        pid15.SetPoint = speed_set
        pid15.setWindup(6.0)

        pid20 = PID(P=4.0, I = 2.6, D = 0.6)
        pid20.SetPoint = speed_set

        pid30 = PID(P= 4.5, I = 3.8, D = 0.8)
        pid30.SetPoint = speed_set

        pid40 = PID(P= 5.3 , I =4.8, D = 1.0)
        pid40.SetPoint = speed_set
       
        pid50 = PID(P= 6.6 , I = 5.9, D = 1.2)
        pid50.SetPoint = speed_set

        pid60 = PID(P= 7.8 , I = 6.9, D = 1.5)
        pid60.SetPoint = speed_set

        i = 0 
        while True:
            i = (i + 1) % 9999
            time.sleep(0.2)
            if speed_set > 60:
                speed_set = 60
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
            pid60.SetPoint = speed_set
            pid60.update(speed_back)
            #slow speed
            if speed_back - speed_set > 5:
                content = {'Who':'Brake','Mode':speed_mode,'Value':57.5 + int(speed_gear * 22.5) }
                pub.sendPro('Cmd',content)
                continue
                pass

            #brake to stop
            if speed_set < 0 :
                speed_set = max(speed_set,-6)
                content = {'Who':'Brake','Mode':speed_mode,'Value':57.5 + math.fabs(int(speed_set * 22.5))}
                pub.sendPro('Cmd',content)
                continue
                pass

            #different args for different speed_set
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
            elif speed_set <= 65:
                output = pid60.output

            if i % 4 == 0:
                print('output is : ',output)
            #accelerate
            if output > 0:
                Depth = 0
                if(speed_set <= 10):
                    Depth = min(35 + speed_gear * 5, int(0.42*output))
                if(speed_set <= 15):
                    Depth = min(35 + speed_gear * 5, int(0.42*output))
                elif(speed_set <= 25):
                    Depth = min(40 + speed_gear * 5, int(0.80*output))
                elif(speed_set <= 35):
                    Depth = min(50 + speed_gear * 5, int(0.58*output))
                elif(speed_set <= 45):
                    Depth = min(60 + speed_gear * 5, int(0.47*output))
                elif(speed_set <= 55):
                    Depth = min(65 + speed_gear * 5, int(0.47*output))
                else:
                    Depth = min(70 + speed_gear * 5, int(0.46*output))
                content = {'Who':'Gun','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
                if i % 4 == 0:
                    print('control depth is : ',Depth)
            #slow down
            if output < 0:
                if output > -50:
                    Depth = 0
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif  output > -66:
                    Depth = int(-0.35 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif  output > -71:
                    Depth = int(-0.45 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif output > -79:
                    Depth = int(-0.5 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif output > -85:
                    Depth = int(-0.6 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif output > -90:
                    Depth = int(-0.8 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
                elif output < 0 :
                    Depth = int(-1.0 * output)
                    content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                    pub.sendPro('Cmd',content)
                    if i % 4 == 0:
                        print('control depth is : ',Depth)
            if output == 0:
                Depth = 0x00
                content = {'Who':'Brake','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
                Depth = 0x00
                content = {'Who':'Gun','Mode':speed_mode,'Value':Depth}
                pub.sendPro('Cmd',content)
            if i % 4 == 0:
                print('speedBack is : ',speed_back)
                print('speedSet is : ',speed_set)
                print('speedMode is : ',speed_mode)
                print('=======================================')

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

import sys
import time
import thread
sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM


def main():

    ctx = proContext()
    def logGNSS():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M.gnss", time.localtime())

        f = open(filename,'w')
        i = 0
        while True:
            content = sub.recvPro()
            i = (i+1) % 9999999
            f.write(str(time.time()))
            f.write('\t')
            #f.write(str(content))
            content = str(content['Lat']) + '\t' + str(content['Lon']) + '\t' + str(content['Head']) + '\t' + str(content['Status']) + '\n'
            print(content)
            f.write((content))
        pass

    def logPlanSpeed():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.speed", time.localtime())
        f = open(filename,'w')
        while True:
            f.write(str(time.time()))
            f.write('\t')
            content = sub.recvPro()
            f.write(content)
            f.write('\n')
        pass

    def logPlanSteer():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.steer", time.localtime())
        f = open(filename,'w')
        while True:
            f.write(str(time.time()))
            f.write('\t')
            content = sub.recvPro()
            f.write(content)
            f.write('\n')
        pass

    def logNav():
        pass

    def logCtrl():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'Cmd')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.cmd", time.localtime())
        f = open(filename,'w')
        while True:
            content = sub.recvPro()
            f.write(str(time.time()))
            f.write('\t')
            f.write(content)
            f.write('\n')
        pass

    def logCAN():
        pass

    #recv decision speed, steer, mode
    thread.start_new_thread(logGNSS, ())
    #recv decision speed, steer, mode
    #thread.start_new_thread(logPlanSteer, ())
    #recv decision speed, steer, mode
    #thread.start_new_thread(logPlanSpeed, ())
    #read, update can,as fallcack
    #thread.start_new_thread(logNav, ())
    #control ,update value of cmd to CAN BUS
    #thread.start_new_thread(logCtrl, ())

    i = 0
    while True:
        i = i + 1
        i = i % 999999
        time.sleep(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
import sys 
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
from proPID import *
import UTM 
import math

def main():
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8081')

    subMap = ctx.socket(zmq.SUB)
    subMap.connect('tcp://localhost:8083')
    subMap.setsockopt(zmq.SUBSCRIBE,'Diff')

    pidDis = PID(P=12.8, I = 3.6, D = 0.0)
    pidHead = PID(P=7.8, I = 2.0, D = 0.0)
    def recvMap():
        j = 0
        while True:
            content = subMap.recvPro()
            pidDis.SetPoint = 0.0
            pidDis.update(content['Dis'])
            outDis = pidDis.output * -1

            pidHead.SetPoint = 0
            pidHead.update(content['Head'])
            outHead = pidHead.output * -1

            steer = outDis + outHead
            speed = math.fabs(10 * math.cos( math.radians(content['DHead'])*5 ) )

            content = {'Mode':0x20,'Value':steer - 15}
            pub.sendPro('PlanSteer',content)
            j = (j + 1) % 999999
            if j % 5 == 0:
                print('PlanSteer--->', content)
            content = {'Mode':0x00,'Value':speed}
            if j % 5 == 0:
                print('PlanSpeed>>>',content)
                print('.......................................................')
            pub.sendPro('PlanSpeed',content)
            pass
    pass
    recvMap()

if __name__ == '__main__':
    main()
    pass


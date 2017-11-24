#!/usr/bin/env python
import sys 
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
from proPID import *
import UTM 

def main():
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8083')

    subMap = ctx.socket(zmq.SUB)
    subMap.connect('tcp://localhost:8083')
    subMap.setsockopt(zmq.SUBSCRIBE,'Diff')

    pidDis = PID(P=0.8, I = 0.0, D = 0.0)
    pidHead = PID(P=1.0, I = 0.0, D = 0.0)
    def recvMap():
        while True:
            content = subMap.recvPro()
            pidDis.setPoint(0.0)
            pidDis.update(content['Dis'])
            outDis = pidDis.output

            pidHead.setPoint(0.0)
            pidHead.update(content['Head'])
            outHead = pidHead.output

            steer = outDis + outHead
            content = {'Mode':0x20,'Value':steer}
            pub.sendPro('PlanSteer',content)

            speed = 10 * math.cos(content['DHead'])
            content = {'Mode':0x02,'Value':speed}
            pub.sendPro('PlanSpeed',content)
            pass
    pass

if __name__ == '__main__':
    main()
    pass


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

    pidDis = PID(P= 10.8, I = 0.0, D = 0.0)
    pidDis.setWindup(50.0)
    pidHead = PID(P= 3.8, I = 0.0, D = 0.0)
    pidHead.setWindup(50.0)
    pidDHead = PID(P=2.8, I = 0.0, D = 0.0)
    pidDHead.setWindup(25.0)

    

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

            pidDHead.SetPoint = 0
            pidDHead.update(content['DHead'])
            outDHead = pidHead.output * -1

            steer = outDis + outHead + outDHead
            #if math.fabs(steer) > 70:
            #    steer = steer * 1.1
            #elif math.fabs(steer) > 90:
            #    steer = steer * 1.2
            #elif math.fabs(steer) > 110:
            #    steer = steer * 1.3
            #elif math.fabs(steer) > 130:
            #    steer = steer * 1.4
            #elif math.fabs(steer) > 140:
            #    steer = steer * 1.5
            #if steer > 500:
            #    steer = 500
            #if steer < -500:
            #    steer = -500
            speed = math.fabs(10 * math.cos( math.radians(content['DHead'])*5 ) )

            content = {'Mode':0x20,'Value':int(steer)  }
            #pub.sendPro('PlanSteer',content)
            j = (j + 1) % 999999
            if j % 1 == 0:
                print('PlanSteer--->', content)
                print('.......................................................')
            content = {'Mode':0x00,'Value':speed}
            #pub.sendPro('PlanSpeed',content)
            pass
    pass
    recvMap()

if __name__ == '__main__':
    main()
    pass


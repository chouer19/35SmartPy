import sys
import time
import thread

sys.path.append("../libs")
from proContext import *

ctx = proContext()
#subcribe current plan about speed and steer
#steer
subSteer = ctx.socket(zmq.SUB)
subSteer.connect('tcp://localhost:8081')
subSteer.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
#speed
subSpeed = ctx.socket(zmq.SUB)
subSpeed.connect('tcp://localhost:8081')
subSpeed.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')

while True:
    content = subSpeed.recvPro()
    print("recv speed msg")
    print(content)

    print("recv steer msg")
    content = subSteer.recvPro()
    print(content)



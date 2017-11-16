import sys
import time
import thread

sys.path.append("../libs")
from proContext import *

ctx = proContext()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:8081')

mode = 0
speed = 0

def f():
    while True:
        content = {'Mode':mode, 'Value':speed}
        pub.sendPro('PlaneSpeed', content)
#        print('pub: ',content)
        time.sleep(0.5)

#thread.start_new_thread(f, ())

while True:
    print("input speed mode and speed like this:0,12")
    modeIn, speedIn = input()
    mode = modeIn
    speed = speedIn


    content = {'Mode':mode, 'Value':speed}
    print("sended content: ",content)
    pub.sendPro('PlanSpeed',content)

    #print("input steer mode and angle like this:0,10")
    #mode, angle = input()
    #content = {'Mode':mode, 'Value':angle}
    #pub.sendPro('PlanSteer',content)

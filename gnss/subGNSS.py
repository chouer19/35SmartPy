#!/usr/bin/env python
import sys
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
from proUTM import *
import UTM
#convert string to dict
import yaml
#draw something
#import pygame, sys
#from pygame.locals import *

global node
node = {'Lat':0,'Lon':0,'Head':0,'Status':0,'V_e':0,'V_n':0,'V_earth':0}
def main():
    #recieve and search
    ctx = proContext()
    subGPS = ctx.socket(zmq.SUB)
    subGPS.connect('tcp://localhost:8080')
    subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
    i = 0
    while True:
        content = subGPS.recvPro()
        node = content
        print(content)
        i = (i+1) % 999
        if i % 20 == 0:
            pass

if __name__ == '__main__':
    main()


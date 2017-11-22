#!/usr/bin/env python

import sys,time,math,thread,copy

sys.path.append("../libs")

from proContext import *

ctx = proContext()

subGPS = ctx.socket(zmq.SUB)
subGPS.connect('tcp://localhost:8082')
subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')


class MapCreator(object):
    def __init__(self,name="map.txt",point_interval = 0.1):
        self.file           = open(name,'w')
        self.interval       = point_interval
        self.recording      = False
        self.last_point     = None
        self.point_count    = 0
        
    def process(self,data):
        def DisBetweenPoints(latA,lonA,latB,lonB):
            R = 6371004
            C = math.sin(latA) * math.sin(latB) * math.cos(lonA - lonB) + math.cos(latA) * math.cos(latB)
            return R * math.acos(C) * math.pi / 180

        if self.recording is False or DisBetweenPoints(self.last_point[0],self.last_point[1],data['Lat'],data['Lon']) >= self.interval:
            self.recording      = True
            self.point_count    = self.point_count + 1
            self.last_point     = data['Lat'],data['Lon']
            road_point_s        = "%d\t%.7f\t%.7f\t0\t0\t%d\t%d\n"%(self.point_count,data['Lat'],data['Lon'],0,0)
            self.file.writelines(road_point_s)

def recvGpsAndSet(args):
    mapcreator, = args
    while True:
        content = subGPS.recvPro()
        mapcreator.process(content)


if __name__ == '__main__':
    mapcreator = MapCreator()
    #thread.start_new_thread(recvGpsAndSet,(mapcreator,))

    i = 0
    while True:
        content = subGPS.recvPro()
        mapcreator.process(content)
        i = i + 1
        i = i % 999999
        if i % 20 == 0:
            print(content)
    while True:
        time.sleep(1)

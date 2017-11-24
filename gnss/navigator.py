﻿#!/usr/bin/env python
import sys
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
import UTM

def main():
    hdMap = []
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8083')
    def loadmap():
        with open('map.txt','r') as fi:
            for line in fi.readlines():
                args = line.split('\t')
                time = args[1]
                content = args[2]
                hdMap.append(content)
            pass
    pass
    loadmap()

    def searchmap(node):
        curDis = 9999
        curPoint = 0
        tarDis = 9999
        tarPoint = 0
        easting,northing,zone,zone_letter = UTM.from_latlon(node['Lat'],node['Lon'])
        for i in range(0,len(hdMap)):
            if math.abs( node['Head']  - hdMap[i]['Head'] > 90 ) :
            #if math.abs( node['Head']  - hdMap[i]['Head'] > 90 ) or hdMap[i]['Status'] != 2:
                continue
            curEasting,curNorthing,curZone,curZone_letter = UTM.from_latlon(hdMap[i]['Lat'] ,hdMap[i]['Lon'] )
            dis = math.sqrt( math.pow(easting - curEasting,2) + math.pow(northing - curNorthing,2)  )
            if dis < curDis:
                curDis = dis
                curPoint = i
        #current v
        v = math.sqrt( math.pow( node['v_n'],2 ) + math.pow( node['v_e'],2 )  + math.pow( node['v_earth'],2 ) )
        for i in range(curPoint,len(hdMap)):
            curEasting,curNorthing,curZone,curZone_letter = UTM.from_latlon(hdMap[i]['Lat'] ,hdMap[i]['Lon'] )
            dis = math.abs( math.sqrt( math.pow(easting - curEasting,2) + \
                  math.pow(northing - curNorthing,2)  ) - 0.1 * v )
            if dis < tarDis:
                tarDis = dis
                tarPoint = i

        dis = curDis
        curEasting,curNorthing,curZone,curZone_letter = \
                         UTM.from_latlon(hdMap[curPoint]['Lat'] ,hdMap[curPoint]['Lon'] )
        head = hdMap[tarPoint]['Head']
        head = head - node['Head']
        if head < -180:
            head = head + 360
        if head > 180:
            head = head - 360
        #dis with target point
        if head < 0:
            dis = dis * -1
        dhead = 0
        ddhead = 0
        if curPoint < len(hdMap) - 1 and curPoint > 0:
            dhead = hdMap[curPoint + 1]/2 - hdMap[curPoint - 1]/2
        if curPoint < len(hdMap) - 2 and curPoint > 1:
            ddhead = hdMap[curPoint + 2]/4 - hdMap[curPoint - 2]/4 + hdMap[curPoint] / 2
        return dis,head,dhead,ddhead
    
    ctx = proContext()
    subGPS = ctx.socket(zmq.SUB)
    subGPS.connect('tcp://localhost:8082')
    subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
    while True:
        content = subGPS.recvPro()
        dis,head,dhead,ddhead = searchmap(content)
        content = {'Dis':dis,'Head':head,'DHead':dhead,'DDHead':ddhead}
        pub.sendPro('Diff',content)
        pass

if __name__ == '__main__':
    main()


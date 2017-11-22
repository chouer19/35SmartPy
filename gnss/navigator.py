#!/usr/bin/env python
import sys
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
import UTM

def main():
    hdMap = []
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8083')
    def loadmap():
        with open('map.txt','r') as fi:
            for line in fi.readlines()
                args = line.split('\t')
                time = args[1]
                content = args[2]
                hdMap.append(content)
            pass

    pass


    def searchmap(node):
        
        curDis = 9999
        curPoint = 0
        tarDis = 9999
        tarPoint = 0
        easting,northing,zone,zone_letter = UTM.from_latlon(node['Lat'],node['Lon'])
        for i in range(0,len(hdMap)):
            if math.abs( node['Head']  - hdMap[i]['Head'] > 90 ) or hdMap[i]['Status'] != 2:
                pass
                continue
            curEasting,curNorthing,curZone,curZone_letter = UTM.from_latlon(hdMap[i]['Lat'] ,hdMap[i]['Lon'] )
            dis = math.sqrt( math.pow(easting - curEasting,2) + math.pow(northing - curNorthing,2)  )
            if dis < curDis:
                curDis = dis
                curPoint = i
                pass


        v = math.sqrt( math.pow( node['v_n'],2 ) + math.pow( node['v_e'],2 )  + math.pow( node['v_earth'],2 ) )
        for i in range(curPoint,len(hdMap)):
            curEasting,curNorthing,curZone,curZone_letter = UTM.from_latlon(hdMap[i]['Lat'] ,hdMap[i]['Lon'] )
            dis = math.abs( math.sqrt( math.pow(easting - curEasting,2) + math.pow(northing - curNorthing,2)  ) - 0.1 * v )
            if dis < tarDis:
                tarDis = dis
                tarPoint = i
                pass

        dis = curDis
        #judge left or right
        hCur = node['Head']
        curEasting,curNorthing,curZone,curZone_letter = UTM.from_latlon(hdMap[curPoint]['Lat'] ,hdMap[curPoint]['Lon'] )
        hCos = curEasting - easting
        hSin = curNorthing - northing
        re = hSin * math.cos(hCur) - hCos * math.sin(hCur)
        if re < 0:
            dis = dis * -1
        head = hdMap[tarPoint]['Head']
        dhead = 0
        if tarPoint > 0 and tarPoint < len(hdMap) - 1:
            dhead = (hdMap[tarPoint + 1]['Head'] - hdMap[tarPoint - 1]['Head']  )/2
        ddhead = 0
        if tarPoint > 1 and tarPoint < len(hdMap) - 2:
            ddhead = ( hdMap[tarPoint + 2]['Head'] - hdMap[tarPoint - 2]['Head'] + 2 * hdMap[tarPoint]['Head'] )/4
        pass
        #dis with target point
        return dis,head,dhead,ddhead
    
    while True:
        ctx = proContext()
        subGPS = ctx.socket(zmq.SUB)
        subGPS.connect('tcp://localhost:8082')
        subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
        content = subGPS.recvPro()
        dis,head,dhead,ddhead = searchmap(content)
        content = {'Dis':dis,'Head':head,'DHead':dhead,'DDHead':ddhead}
        pub.sendPro('Diff',content)
        pass


def __name__ == '__main__':
    main()


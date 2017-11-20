#!/usr/bin/env python
import sys
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *

ctx = proContext()

pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:8081')

subGPS = ctx.socket(zmq.SUB)
subGPS.connect('tcp://localhost:8082')
subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')

cur_index   = 0
cur_lon     = 0.
cur_lat     = 0.
cur_heading = 0.


laststeer   = 0.
lastspeed   = 0.

gpsLine     = []
gpsMapLine  = []

MAX_SPEED   = 10

def angToRad(angle_d): 
    return angle_d * math.pi / 180

def DisBetweenPoints(latA,lonA,latB,lonB):
    R = 6371004
    C = math.sin(latA) * math.sin(latB) * math.cos(lonA - lonB) + math.cos(latA) * math.cos(latB)

    return R * math.acos(C) * math.pi / 180

def getDist2(x1, y1,x2,y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

def BLH2XYZ(B,L,H):
    '''B: lat纬度  L: lon经度  H: height'''
    Lat,Lon = B,L

    N, E, h = 0,0,0
    L0 = (int((L - 1.5) / 3.0) + 1 ) * 3.0  	#根据经度求中央子午线经度
    
    a = 6378245.0            	                #地球半径  北京6378245
    F = 298.257223563        	                #地球扁率
    iPI = 0.0174532925199433 	                #2pi除以360，用于角度转换

    f = 1 / F
    b = a * (1 - f)
    ee = (a * a - b * b) / (a * a)
    e2 = (a * a - b * b) / (b * b)
    n = (a - b) / (a + b) 
    n2 = (n * n)
    n3 = (n2 * n)
    n4 = (n2 * n2)
    n5 = (n4 * n)
    al = (a + b) * (1 + n2 / 4 + n4 / 64) / 2
    bt = -3 * n / 2 + 9 * n3 / 16 - 3 * n5 / 32
    gm = 15 * n2 / 16 - 15 * n4 / 32
    dt = -35 * n3 / 48 + 105 * n5 / 256
    ep = 315 * n4 / 512

    B = B * iPI
    L = L * iPI
    L0 = L0 * iPI
    l = L - L0
    cl = (math.cos(B) * l) 
    cl2 = (cl * cl)
    cl3 = (cl2 * cl)
    cl4 = (cl2 * cl2)
    cl5 = (cl4 * cl)
    cl6 = (cl5 * cl)
    cl7 = (cl6 * cl)
    cl8 = (cl4 * cl4)

    lB = al * (B + bt * math.sin(2 * B) + gm * math.sin(4 * B) + dt * math.sin(6 * B) + ep * math.sin(8 * B))
    t = math.tan(B)
    t2 = (t * t) 
    t4 = (t2 * t2) 
    t6 = (t4 * t2)
    Nn = a / math.sqrt(1 - ee * math.sin(B) * math.sin(B))
    yt = e2 * math.cos(B) * math.cos(B)
    N = lB
    N += t * Nn * cl2 / 2
    N += t * Nn * cl4 * (5 - t2 + 9 * yt + 4 * yt * yt) / 24
    N += t * Nn * cl6 * (61 - 58 * t2 + t4 + 270 * yt - 330 * t2 * yt) / 720
    N += t * Nn * cl8 * (1385 - 3111 * t2 + 543 * t4 - t6) / 40320

    E = Nn * cl
    E += Nn * cl3 * (1 - t2 + yt) / 6
    E += Nn * cl5 * (5 - 18 * t2 + t4 + 14 * yt - 58 * t2 * yt) / 120
    E += Nn * cl7 * (61 - 479 * t2 + 179 * t4 - t6) / 5040

    E += 500000

    N = 0.9999 * N
    E = 0.9999 * (E - 500000.0) + 250000.0

    return E,N #x,y

def getAngle(lon1, lat1, lon2, lat2):
   angle        = 0.
   averageLat   = (lat1 + lat2) / 2

   if abs(lat1 - lat2) <= 1e-6:
        angle = (1 if lon1 > lon2 else 0) * 180 + 90
   else:
        angle = (1 if lat1 > lat2 else 0) * 180 + math.atan((lon1-lon2)*math.cos(angToRad(averageLat))/(lat1-lat2)) * 180 / math.pi 

   return ( 1 if angle < 0 else 0 ) * 360 + angle 

class RoadPoint():
    def __init__(self,x=0.,y=0.,lat=0.,lon=0.,azimuth=0.,mode1=0,mode2=0):
        self.valid   = False
        self.x       = x
        self.y       = y
        self.Lat     = lat
        self.Lon     = lon
        self.Azimuth = azimuth
        self.Mode1   = mode1
        self.Mode2   = mode2

    def __str__(self):
        return "%f,%f" % (self.Lon,self.Lat)


def load_gps_map(map="map.txt"):
    global gpsMapLine
    gps_point_list = []

    with open(map,'r') as fp:
        for line in fp.readlines():
            args = line.split('\t')

            rp = RoadPoint()

            rp.Lat    = float(args[1])
            rp.Lon    = float(args[2])
            rp.x,rp.y = BLH2XYZ(rp.Lat, rp.Lon, 0)
            rp.Mode1  = int(args[3])
            rp.Mode2  = rp.Mode1

            gps_point_list.append(rp) 

        gpsMapLine = gps_point_list

    return gps_point_list

def control_strategy(centerLine):
    '''generic control strategy '''
    global laststeer,lastspeed

    if len(centerLine) == 0: return (0.,0.)

    startDistanceNear,endDistanceNear,startDistanceFar,endDistanceFar = 1,4,4,8
    KEpos,KEang,EPos,EAng = 6,16,0.0,0.0
    near,far,dissum = list(),list(),0

    for i in range(0,len(centerLine)- 1):
        dissum += getDist2(centerLine[i].x, centerLine[i].y, centerLine[i + 1].x, centerLine[i + 1].y)

        if dissum >= startDistanceNear and dissum <= endDistanceNear:
            near.append(centerLine[i])
        if dissum >= startDistanceFar and dissum <= endDistanceFar:
            far.append(centerLine[i])

    EPos = 0 if len(near) == 0 else getAverageDeviation(near)
    EAng = 0 if len(far)  == 0 else getAverageDeflection(far)

    steer = KEang * EAng + KEpos * EPos

    LimitSteer = 500.

    if EPos < 10.:
        speed = (1.0 - 0.8*steer /LimitSteer) * MAX_SPEED 
        steer = max(min(steer,LimitSteer),-LimitSteer)
    else:
        speed = 0.
        steer = 0.

    laststeer,lastspeed = steer,speed 

    return (speed,steer)

def GetDistance(p1,p2):
    return math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y))

def getmetercount(gpsline, meter):
    index,sumdis = 1,0.

    while index < len(gpsline) and sumdis < meter:
        sumdis += GetDistance(gpsline[index - 1], gpsline[index])
        index = index + 1

    if index == len(gpsline) or abs(sumdis - meter) > abs(sumdis - GetDistance(gpsline[index - 1], gpsline[index]) - meter): 
        return index - 1
    else:
        return index

def getAverageDeviation(near):
    sum_d,max_size = 0,len(near)

    for i in range(0,min(5, max_size)):
        sum_d += near[i].x

    return sum_d / min(5, max_size)


def getAverageDeflection(far):
    sum_x,sum_y,max_size = 0,0,len(far)

    for i in range(0,min(5, max_size)):
        sum_x += far[i].x
        sum_y += abs(far[i].y)

    average_y = sum_y / min(5, max_size)
    average_x = sum_x / min(5, max_size)

    return math.atan(average_x / average_y) / math.pi * 180


def recvGPSAndSet():
    global cur_lat,cur_lon,cur_heading
    global subGPS

    while True:
        #receive speed
        content = subGPS.recvPro()

        cur_lat     = content['Lat']
        cur_lon     = content['Lon']
        cur_heading = content['Head']

        time.sleep(0.1)
    

def navigate_gps_handler():

    global gpsLine,gpsMapLine,cur_index
    global cur_lon,cur_lat,cur_heading

    while True:
        gpsget        = list()
        rp            = RoadPoint()

        rp.Lon        = cur_lon
        rp.Lat        = cur_lat

        rp.x,rp.y     = BLH2XYZ(rp.Lat, rp.Lon, 0)

        rp.Azimuth    = cur_heading

        flag          = True 
        num           = 0
        markDis       = 1e100

        markSendPoint = cur_index

        for j in range(cur_index,len(gpsMapLine)):
            if abs(gpsMapLine[j].x-rp.x) < 20 and abs(gpsMapLine[j].y-rp.y) < 20:
                tmpdis = getDist2(rp.x, rp.y, gpsMapLine[j].x, gpsMapLine[j].y)

                if markDis > tmpdis: 
                    markDis       = tmpdis
                    markSendPoint = j

                if flag: 
                    flag = False
            else:
                if flag == False and num >= 3: 
                    break

                num = num + 1

        for j in range(max(0,markSendPoint),min(markSendPoint+160,len(gpsMapLine))):

            distance = getDist2(rp.x, rp.y, gpsMapLine[j].x, gpsMapLine[j].y)
            angel    = getAngle(rp.Lon, rp.Lat, gpsMapLine[j].Lon, gpsMapLine[j].Lat) 
            angel1   = angel - (rp.Azimuth + 2) 

            if angel1 > -360 and angel1 <= 360:
                if angel1 > -360 and angel1 <= -270: 
                    angel1 = angel1 + 360
                if angel1 > 270 and angel1 <= 360: 
                    angel1 = angel1 - 360

                y = distance * math.cos(angel1 * math.pi / 180)

                x = (-1 if angel1 < 0 else 1) * distance * abs(math.sin(angel1 * math.pi / 180))
                x = (-1 if y < 0 and (angel1 > 180 or angel1 < -180) else 1) * x 
	        
                rp_get = RoadPoint()
                rp_get.x,rp_get.y,rp_get.Mode1,rp_get.Mode2 = x, y, gpsMapLine[j].Mode1, gpsMapLine[j].Mode2 
                gpsget.append(rp_get)

        if len(gpsget) > 1: 
            gpsLine = copy.deepcopy(gpsget)

        cur_index = markSendPoint

        time.sleep(0.05)

def navigate_ruihu_main(*args):
    global gpsLine
    global pub

    while True:
        final_ctrl  = control_strategy(gpsLine)

        content = {'Mode':1, 'Value':final_ctrl[0]}
        pub.sendPro('PlanSpeed',content)

        content = {'Mode':1, 'Value':final_ctrl[1]}
        pub.sendPro('PlanSteer', content)

        time.sleep(0.1)

if __name__ == '__main__':

    load_gps_map()

    thread.start_new_thread(navigate_ruihu_main, ())
    thread.start_new_thread(navigate_gps_handler, ())

    thread.start_new_thread(recvGPSAndSet, ())

    i = 0

    while True:
        i = i + 1
        i = i % 999999
        time.sleep(1)

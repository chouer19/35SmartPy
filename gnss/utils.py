#!/usr/bin/python
import math,copy

Pi = 3.1415926535897932384626433832795


cur_lon,cur_lat,cur_heading = 0,0,0

DistanceGPS,LimitSteer = 0.1,500

def angToRad(angle_d): return angle_d * Pi / 180

def DisBetweenPoints(latA,lonA,latB,lonB):
    R,C = 6371004,math.sin(latA) * math.sin(latB) * math.cos(lonA - lonB) + math.cos(latA) * math.cos(latB)
    #print 'R:',R,'  C:',C
    if C > 1:
        C = 1
    if C < -1:
        C = -1
    return R * math.acos(C) * Pi / 180

def getDist2(x1, y1,x2,y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

def BLH2XYZ(B,L,H):
    Lat,Lon = B,L

    N, E, h = 0,0,0
    L0 = (int((L - 1.5) / 3.0) + 1 ) * 3.0
    
    a = 6378245.0
    F = 298.257223563
    iPI = 0.0174532925199433

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

def getAngle(lat1, lon1, lat2, lon2):
   angle,averageLat = 0,(lat1 + lat2) / 2

   if abs(lat1 - lat2) <= 1e-6:
       angle = 90
       if lon1 > lon2: angle = angle + 180
   else:
       angle = math.atan((lon1-lon2)*math.cos(angToRad(averageLat))/(lat1-lat2)) * 180 / math.pi
       if lat1 > lat2: angle = (angle+180) 

   if angle < 0:angle = 360 + angle

   return angle

def getRelatedXY(LatA,LonA,LatB,LonB,Head):
   x1,y1 = BLH2XYZ(LatA,LonA,0)
   x2,y2 = BLH2XYZ(LatB,LonB,0)
   
   distance = getDist2(x1,y1,x2,y2)
   angel = getAngle(LatA,LonA,LatB,LonB)

   angel1 = angel - Head 
   if angel1 > -360 and angel1 <= 360:
      if angel1 > -360 and angel1 <= -270: 
         angel1 = angel1 + 360
      if angel1 > 270 and angel1 <= 360: 
         angel1 = angel1 - 360
      y = distance * math.cos(angel1 * math.pi / 180)
      if angel1 < 0:
         x = -distance * abs(math.sin(angel1 * math.pi / 180))
      else:
         x = distance * abs(math.sin(angel1 * math.pi / 180))
      if y < 0 and (angel1 > 180 or angel1 < -180): 
         x = -x

   return x,y

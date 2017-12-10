#!/usr/bin/env python
import sys
import time,math,thread,copy

sys.path.append("../libs")
from proContext import *
from proUTM import *
import UTM
#convert string to dict
#draw something
import pygame, sys
from pygame.locals import *

global node
global current
global target
node = (0,0,0,0,0,0,0)
def main():
    global node
    global current
    global target
    target = 0
    current = 0
    hdMap = []
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8083')
    def loadmap():
        print('loading map............')
        fi =  open('./map/map.txt','r')
        i = 0 
        lastE = 0 
        lastN = 0 
        line = fi.readlines()[0]
        fi.close()
        fi =  open('./map/map.txt','r')
        lastargs = line.split('\t')
        for line in fi.readlines():
            i = (i + 1) % 99999
            args = line.split('\t')
            E,N,Z,Z_l = UTM.from_latlon( float((args[1])) , float((args[2])) )
            #ids = math.pow(E-lastE,2) + math.pow(N-lastN,2)
            #print(ids)
            if( math.pow(E-lastE,2) + math.pow(N-lastN,2) > 0.25  ):  
                hdMap.append( (float(lastargs[1])/2 + float(args[1])/2 ,  float(args[2])/2  + float(lastargs[2])/2 ,float(args[3])/2  + float(lastargs[3])/2   , float(args[4])/2  + float(lastargs[4]) /2 ) )
                hdMap.append( (float(args[1]),float(args[2]),float(args[3]),float(args[4])) )
                lastE = E 
                lastN = N 
                lastargs[1],lastargs[2],lastargs[3],lastargs[4] = args[1],args[2],args[3],args[4]
        fi.close()
        print('length map is ',len(hdMap))
    loadmap()
    print('finished loading map')

    def alpha(ve):
        #return 1 * ve
        #return 2.5 * math.log1p(ve)
        #return  ( ( math.log1p(ve) ) ** 3 + math.log1p(ve) ) / 2
        #return 6
        #return  ( ( ve * math.log1p(ve) ) ) / 2 + ve + 2
        #return  ( ( math.log1p(ve) ) )  + ve + 2
        #if ve < 4:
        #    return math.log1p(ve)
        #return  ve * 2/3 + 3
        #return  ve  + 1
        return  math.log1p(ve * 5) * 2.5 # 12.05

        if ve < 3:
            return math.log1p(ve) + 1
        return  ve + 1

    def searchmap():
        global node
        global current
        global target
        j = 0
        while True:
            #time.sleep(0.05)
            args = node
            lat,lon,head,status,gnssSpeed,Steer = float(args[1]),float(args[2]),float(args[3]) ,float(args[4]),float(args[5]),float(args[6])
            if status < 0 or status > 4:
                continue
            curDis = 9999
            curPoint = 0
            tarDis = 9999
            tarPoint = 0
            #try:
            easting,northing,zone,zone_letter = UTM.from_latlon(lat, lon)
            for i in range(0,len(hdMap)):
                if math.fabs( int(head  - hdMap[i][2]) ) > 90 :
                    continue
                #get nearest point ---> curPoint
                E,N,Z,Z_l = UTM.from_latlon(hdMap[i][0] ,hdMap[i][1] )
                dis = math.sqrt (math.fabs( math.pow(easting - E,2) + math.pow(northing - N,2) ) )
                if dis < curDis:
                    curDis = dis
                    curPoint = i
                    current = i
            #current v
            v = gnssSpeed
            tarDis = 0
            tarPoint = curPoint
            LE,LN,Z,Z_l= UTM.from_latlon(hdMap[curPoint][0] ,hdMap[curPoint][1] )
            for i in range(curPoint + 1,len(hdMap)):
                E,N,Z,Z_l= UTM.from_latlon(hdMap[i][0] ,hdMap[i][1] )
                tarDis = tarDis + math.fabs( math.sqrt( math.pow(LE - E,2) + \
                      math.pow(LN - N,2)  ) )
                LE,LN = E,N
                if tarDis > alpha(v):
                    tarPoint = i
                    target = i
                    break
            Head = hdMap[tarPoint][2]
            Head = Head - head
            if Head < -180:
                Head = Head + 360
            if Head > 180:
                Head = Head - 360
            #hai lun
            if curPoint == 0:
                curPoint = curPoint + 3
            if curPoint >= len(hdMap) - 3:
                curPoint = curPoint - 3
            E1,N1,Z1,Z_l1 = \
                             UTM.from_latlon(hdMap[curPoint + 3][0] ,hdMap[curPoint + 3][1] )
            E2,N2,Z2,Z_l2 = \
                             UTM.from_latlon(hdMap[curPoint - 3][0] ,hdMap[curPoint - 3][1] )
            a = math.sqrt( math.pow(easting - E1 ,2)  + math.pow(northing - N1  ,2)  )
            b = math.sqrt( math.pow(easting - E2 ,2)  + math.pow(northing - N2  ,2)  )
            c = math.sqrt( math.pow(E1 - E2 ,2)  + math.pow(N1 - N2  ,2)  )
            p = (a + b + c)/2
            h = 0
            if c > 0:
                h = math.sqrt( math.fabs((p * (p-a) * (p-b) * (p-c)) ) ) * 2 / c
            x1 = (E1 - easting) * math.cos( math.radians(head) ) - (N1 - northing) * math.sin( math.radians(head) )
            if x1 < 0:
                dis = dis * -1
                h = h * -1
                pass
            dis = x1
            dhead = 0
            ddhead = 0
            if curPoint + curPoint - tarPoint > 0:
                dhead = hdMap[tarPoint][2]/2 - hdMap[curPoint][2]/2
            if curPoint + curPoint - tarPoint > 0:
                ddhead = hdMap[tarPoint][2]/4 - hdMap[curPoint - 2][2]/2 + hdMap[curPoint - tarPoint + curPoint][2] / 4
            content = {'Dis':h,'Head':Head,'DHead':dhead,'DDHead':ddhead}
            pub.sendPro('Diff',content)
            j = (j + 1) % 9999
            time.sleep(0.05)
            if j%5 ==0:
                print('                   v is ',v,'        alpha(v) is ',alpha(v))
                print('tar - cur is : ',tarPoint -  curPoint  )
                #print('Dis:',h,'  Head:',Head,'  DHead:',dhead)
                #print(content)
                print('========================================================================================')
            #except Exception:
    thread.start_new_thread(searchmap, ())

    def draw():
        global current
        global target
        kk = 20
        W = 1000
        H = 1000
        pygame.init()
        screen = pygame.display.set_mode((W,H))
        #screen = pygame.display.set_mode((1361,1001))
        pygame.display.set_caption("ququuququququuuq")
        FPS = 50
        fpsClock = pygame.time.Clock()
        BLACK = (0,0,0)
        WHITE = (255,255,255)
        RED = (255,0,0)
        DARKPINK = (255,20,147)
        DARKRED = (138,0,0)
        PURPLE = (160,32,240)
        YELLOW = (255,255,0)
        GREEN = (00,255,0)
        BLUE = (0,0,255)
        LIGHTBLUE = (176,226,255)
        ORANGE4 = (139,69,0)
        screen.fill(BLACK)
        while True:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            mat = []
            centerE,centerN,Z,Z_l = UTM.from_latlon( float(node[1]), float(node[2]) )
            for content in hdMap:
                E,N,Z,Z_l = UTM.from_latlon( content[0], content[1] )
                #print(E - centerE)
                #mat.append( [int ((E-centerE) * 20) + 300 , int ((N - centerN)* 20)+  300] )
                #print(mat)
                pygame.draw.circle(screen, WHITE, [int ((E-centerE) * kk) + W/2 , int (-1 * (N - centerN)* kk)+  H/2] , 1, 0)
            #pygame.draw.lines(screen, WHITE,False, mat, 1)
            pygame.draw.circle(screen,BLUE,[W/2,H/2] , 3 , 0)
            
            E,N,Z,Z_l = UTM.from_latlon( hdMap[current][0], hdMap[current][1] )
            pygame.draw.circle(screen, DARKPINK, [int ((E-centerE) * kk) + W/2 , int (-1 * (N - centerN)* kk)+  H/2] , 4, 0)
            E,N,Z,Z_l = UTM.from_latlon( hdMap[target][0], hdMap[target][1] )
            pygame.draw.circle(screen, RED, [int ((E-centerE) * kk) + W/2 , int (-1 * (N - centerN)* kk)+ H/2] , 3, 0)
            off = 0.5
            NN = -1000 * math.cos( math.radians(float(node[3]) + off )  )
            EE = 1000 * math.sin( math.radians(float(node[3]) + off ) )
            pygame.draw.line(screen, RED, [W/2, H/2], [W/2 + EE, H/2 + NN], 2)
            pygame.display.update()
            fpsClock.tick(FPS)

        pass

    thread.start_new_thread(draw, ())

    #recieve and search
    ctx = proContext()
    subGPS = ctx.socket(zmq.SUB)
    subGPS.connect('tcp://localhost:8080')
    subGPS.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
    i = 0
    while True:
        content = subGPS.recvPro()
        node = content

        i = (i+1) % 999
        if i % 20 == 0:
            pass

if __name__ == '__main__':
    main()


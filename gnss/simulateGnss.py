import sys
import time
import thread
sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM

ctx = proContext()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:8080')
while True:
     i = 0
     with open('offline.txt','r') as fi:
        for line in fi.readlines():
            i = (i+1) % 9999
            args = line.split('\t')
            #rg= args[0]
            #gnssLat = float(args[1])
            #gnssLon  = float(args[2])
            #gnssHead = float(args[3])
            #gnssStatus = float(args[4])
            #gnssV = float(args[5])
    
            #canBrakeMode = float(args[6])
            #canBrakeTime = float(args[7])
            #canBrakeButton = float(args[8])
            #canBrakeRemoter = float(args[9])
            #canBrakePedal = float(args[10])
            #canBrakeRemoterS = float(args[11])
            #canBrakeReal = float(args[12])
        
            #canGunMode = float(args[13])
            #canGunDepth = float(args[14])
            #canGunSpeed = float(args[15])
        
            #canSteerMode = float(args[16])
            #canSteerTorque = float(args[17])
            #canSteerException = float(args[18])
            #canSteerAngleH = float(args[19])
            #canSteerAngleL = float(args[20])
            #canSteerCalib = float(args[21])
            #canSteerBy6 = float(args[22])
            #canSteerCheck = float(args[23])
    
            #planSpeed = float(args[24])
            #planSpeedMode = float(args[25])
            #planSpeedGear = float(args[26])
            #planSteer = float(args[27])
            #planSteerMode = float(args[28])
    
            #navDis = float(args[29])
            #navHead = float(args[30])
            #navDHead = float(args[31])
            #navDDHead = float(args[32])
    
            #controlWho = float(args[33])
            #controlMode = float(args[34])
            #controlValue= float(args[35])

            pub.sendPro('CurGNSS',args)
            if i%25 == 0:
                print('V : ', float(args[5]) * 3.6, '  Steer : ', int( float(args[19]) * 256 + float(args[20]) - 1024) )
                print('*********************************************************************************************************************************')
            time.sleep(0.05)
        pass
#        break


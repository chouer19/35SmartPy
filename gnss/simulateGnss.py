import sys
import time
import thread
sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM
import yaml


ctx = proContext()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:8080')
while True:
     i = 0
     with open('offline3.txt','r') as fi:
        for line in fi.readlines():
            i = (i+1) % 9999
            args = line.split('\t')
            rg= args[0]
            lat,lon,head,status,canSpeed,gnssSpeed,Steer = args[1],args[2],args[3],args[4],args[5],args[6],args[7]
            content = (args[1],args[2],args[3],args[4],args[5],args[6],args[7])
            pub.sendPro('CurGNSS',content)
            if i%25 == 0:
                print('V : ',float(gnssSpeed) * 3.6, '  Steer : ',float(Steer) )
                print('*********************************************************************************************************************************')
            time.sleep(0.05)
        pass
#        break


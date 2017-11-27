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
            content = args[1]
            content = yaml.load(content)
            pub.sendPro('CurGNSS',content)
            if i%20 == 0:
                print(content)
                print('*********************************************************************************************************************************')
            time.sleep(0.2)
        pass
#        break


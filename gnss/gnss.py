import sys
import time
import thread

sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM

def main():
    gnss = GNSS()
    ctx = proContext()
    pub = ctx.socket(zmq.PUB)
    pub.bind('tcp://*:8082')

    i=0
    while True:
        gnss.read()
        content = {"Length":gnss.length,"Mode":gnss.mode,"Time1":gnss.time1,"Time2":gnss.time2, \
                   "Num":gnss.num,"Lat":gnss.lat,"Lon":gnss.lon,"Height":gnss.height, \
                   "V_n":gnss.v_n,"V_e":gnss.v_e,"V_earth":gnss.v_earth, \
                   "Roll":gnss.roll,"Pitch":gnss.pitch,"Head":gnss.head, \
                   "A_n":gnss.a_n,"A_e":gnss.a_e,"A_earth":gnss.a_earth, \
                   "V_roll":gnss.v_roll,"V_pitch":gnss.v_pitch,"V_head":gnss.v_head, \
                   "Status":gnss.status}
        pub.sendPro('CurGNSS',content)
        i = (i + 1) % 999999
        if i % 10 ==0:
            print(content)
            print('************************')
            print('************************')
        time.sleep(0.02)

if __name__ == "__main__":
    main()

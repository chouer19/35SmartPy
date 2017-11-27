import sys
import time
import thread
import math
sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM

def main():

    ctx = proContext()
    gnssLat = 0
    gnssLon = 0
    gnssHead = 0
    gnssStatus = 0
    gnssV = 0

    canBrakeMode = 0
    canBrakeTime = 0
    canBrakeButton = 0
    canBrakeRemoter = 0
    canBrakePedal = 0
    canBrakeRemoterS = 0
    canBrakeReal = 0
    
    canGunMode = 0
    canGunDepth = 0
    canGunSpeed = 0
    
    canSteerMode = 0
    canSteerTorque = 0
    canSteerException = 0
    canSteerAngleH = 0
    canSteerAngleL = 0
    canSteerCalib = 0
    canSteerBy6 = 0
    canSteerCheck = 0
    
    def logGNSS():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8088')
        sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M.gnss", time.localtime())

        f = open(filename,'w')
        i = 0
        while True:
            content = sub.recvPro()
            i = (i+1) % 9999999
            f.write(str(time.time()))
            f.write('\t')
            #f.write(str(content))
            gnssLat = content['Lat']
            gnssLon = content['Lon']
            gnssHead = content['Head']
            gnssStatus = content['Status']
            gnssV = math.sqrt( content['V_n']**2 + content['V_e']**2 + content['V_earth']**2 )
            content = str(content['Lat']) + '\t' + str(content['Lon']) + '\t' + str(content['Head']) + '\t' + str(content['Status']) + '\n'
            print(content)
            f.write((content))
        pass

    def logCANBrake():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'CANBrake')
        while True:
            content = sub.recvPro()
            canBrakeTime = content['Time']
            canBrakeButton = content['Button']
            canBrakeRemoter = content['Remoter']
            canBrakePedal = content['Pedal']
            canBrakeRemoterS = content['BrakeRemoterS']
            canBrakeReal = content['Real']
        pass

    def logCANSteer():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'CANSteer')
        while True:
            content = sub.recvPro()
            canSteerMode = content['Mode']
            canSteerTorque = content['Torque']
            canSteerException = content['EException']
            canSteerAngleH = content['AngleH']
            canSteerAngleL = content['AngleL']
            canSteerCalib = content['Calib']
            canSteerBy6 = content['By6']
            canSteerCheck = content['Check']
        pass

    def logCANGun():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'CANBrake')
        while True:
            content = sub.recvPro()
            canGunMode = content['Mode']
            canGunDepth = content['Depth']
            canGunSpeed = content['Speed']
        pass

    def logPlanSpeed():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.speed", time.localtime())
        f = open(filename,'w')
        while True:
            f.write(str(time.time()))
            f.write('\t')
            content = sub.recvPro()
            f.write(content)
            f.write('\n')
        pass

    def logPlanSteer():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.steer", time.localtime())
        f = open(filename,'w')
        while True:
            f.write(str(time.time()))
            f.write('\t')
            content = sub.recvPro()
            f.write(content)
            f.write('\n')
        pass

    def logNav():
        pass

    def logCtrl():
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'Cmd')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.cmd", time.localtime())
        f = open(filename,'w')
        while True:
            content = sub.recvPro()
            f.write(str(time.time()))
            f.write('\t')
            f.write(content)
            f.write('\n')
        pass

    def logCAN():
        pass

    #recv decision speed, steer, mode
    thread.start_new_thread(logGNSS, ())
    #recv decision speed, steer, mode
    thread.start_new_thread(logPlanSteer, ())
    #recv decision speed, steer, mode
    thread.start_new_thread(logPlanSpeed, ())
    #read, update can,as fallcack
    thread.start_new_thread(logNav, ())
    #control ,update value of cmd to CAN BUS
    thread.start_new_thread(logCtrl, ())
    thread.start_new_thread(logCANBrake, ())
    thread.start_new_thread(logSteer, ())
    thread.start_new_thread(logCANGun, ())

    filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.all", time.localtime())
    f = open(filename,'w')

    i = 0
    while True:
        i = i + 1
        i = i % 999999
    gnssLat = 0
    gnssLon = 0
    gnssHead = 0
    gnssStatus = 0
    gnssV = 0

    canBrakeMode = 0
    canBrakeTime = 0
    canBrakeButton = 0
    canBrakeRemoter = 0
    canBrakePedal = 0
    canBrakeRemoterS = 0
    canBrakeReal = 0
    
    canGunMode = 0
    canGunDepth = 0
    canGunSpeed = 0
    
    canSteerMode = 0
    canSteerTorque = 0
    canSteerException = 0
    canSteerAngleH = 0
    canSteerAngleL = 0
    canSteerCalib = 0
    canSteerBy6 = 0
    canSteerCheck = 0
        time.sleep(0.1)

if __name__ == "__main__":
    main()

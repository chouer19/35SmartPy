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

global    gnssLat
global    gnssLon 
global    gnssHead
global    gnssStatus 
global    gnssV 
global    canBrakeMode 
global    canBrakeTime 
global    canBrakeButton 
global    canBrakeRemoter 
global    canBrakePedal 
global    canBrakeRemoterS 
global    canBrakeReal 
global    canGunMode 
global    canGunDepth 
global    canGunSpeed 
global    canSteerMode 
global    canSteerTorque
global    canSteerException
global    canSteerAngleH
global    canSteerAngleL
global    canSteerCalib
global    canSteerBy6
global    canSteerCheck
global    planSpeed
global    planSpeedMode
global planSpeedGear
global    planSteer
global    planSteerMode
global    navDis
global    navHead
global    navDHead
global    navDDHead
global    controlWho 
global    controlMode
global    controlValue

def main():
    global    gnssLat
    global    gnssLon 
    global    gnssHead
    global    gnssStatus 
    global    gnssV 

    global    canBrakeMode 
    global    canBrakeTime 
    global    canBrakeButton 
    global    canBrakeRemoter 
    global    canBrakePedal 
    global    canBrakeRemoterS 
    global    canBrakeReal 

    global    canGunMode 
    global    canGunDepth 
    global    canGunSpeed 

    global    canSteerMode 
    global    canSteerTorque
    global    canSteerException
    global    canSteerAngleH
    global    canSteerAngleL
    global    canSteerCalib
    global    canSteerBy6
    global    canSteerCheck

    global    planSpeed
    global    planSpeedMode
    global    planSteer
    global    planSteerMode

    global    navDis
    global    navHead
    global    navDHead
    global    navDDHead

    global    controlWho 
    global    controlMode
    global    controlValue

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

    planSpeed = 0
    planSpeedMode = 0
    planSpeedGear = 0
    planSteer = 0
    planSteerMode = 0

    navDis = 0
    navHead = 0
    navDHead = 0
    navDDHead = 0

    controlWho = 'No'
    controlMode = 0x00
    controlValue = 0x00
    
    def logGNSS():
        global    gnssLat
        global    gnssLon 
        global    gnssHead
        global    gnssStatus 
        global    gnssV 
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8080')
        sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
        filename = time.strftime("./data/%Y_%m_%d_%H_%M.anay", time.localtime())

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
	    #print(content)
            f.write((content))
        pass

    def logCANBrake():
        global    canBrakeMode 
        global    canBrakeTime 
        global    canBrakeButton 
        global    canBrakeRemoter 
        global    canBrakePedal 
        global    canBrakeRemoterS 
        global    canBrakeReal 

        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8088')
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
        global    canSteerMode 
        global    canSteerTorque
        global    canSteerException
        global    canSteerAngleH
        global    canSteerAngleL
        global    canSteerCalib
        global    canSteerBy6
        global    canSteerCheck

        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8088')
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
        global    canGunMode 
        global    canGunDepth 
        global    canGunSpeed 

        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8088')
        sub.setsockopt(zmq.SUBSCRIBE,'CANBrake')
        while True:
            content = sub.recvPro()
            canGunMode = content['Mode']
            canGunDepth = content['Depth']
            canGunSpeed = content['Speed']
        pass

    def logPlanSpeed():
        global    planSpeed
        global    planSpeedMode
        global planSpeedGear
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSpeed')
        while True:
            content = sub.recvPro()
            planSpeedMode = content['Mode']
            planSpeed = content['Value']
            planSpeedGear = content['Gear']
        pass

    def logPlanSteer():
        global    planSteer
        global    planSteerMode

        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8081')
        sub.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
        while True:
            content = sub.recvPro()
            planSteerMode = content['Mode']
            planSteer = content['Value']
        pass

    def logNav():
        global    navDis
        global    navHead
        global    navDHead
        global    navDDHead

        subMap = ctx.socket(zmq.SUB)
        subMap.connect('tcp://localhost:8083')
        subMap.setsockopt(zmq.SUBSCRIBE,'Diff')
        while True:
            content = subMap.recvPro()
            navDis = content['Dis']
            navHead = content['Head']
            navDHead = content['DHead']
            navDDHead = content['DDHead']
        pass

    def logCtrl():
        global    controlWho 
        global    controlMode
        global    controlValue
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:8082')
        sub.setsockopt(zmq.SUBSCRIBE,'Cmd')
        while True:
            content = sub.recvPro()
            controlWho = content['Who']
            controlMode = content['Mode']
            controlValue = content['Value']
        pass

    thread.start_new_thread(logGNSS, ())
    thread.start_new_thread(logCANBrake, ())
    thread.start_new_thread(logCANSteer, ())
    thread.start_new_thread(logCANGun, ())
    thread.start_new_thread(logPlanSpeed, ())
    thread.start_new_thread(logPlanSteer, ())
    thread.start_new_thread(logNav, ())
    thread.start_new_thread(logCtrl, ())

    filename = time.strftime("./data/%Y_%m_%d_%H_%M_%S.all", time.localtime())
    f = open(filename,'w')

    i = 0
    while True:
        i = i + 1
        i = i % 999999
        time.sleep(0.1)
        line = (str(time.time()) + '\t' + \
        str(gnssLat)  + '\t' + \
        str(gnssLon)  + '\t' + \
        str(gnssHead) + '\t' + \
        str(gnssStatus) + '\t' + \
        str(gnssV) + '\t' + \

        str(canBrakeMode) + '\t' + \
        str(canBrakeTime) + '\t' + \
        str(canBrakeButton) + '\t' + \
        str(canBrakeRemoter) + '\t' + \
        str(canBrakePedal) + '\t' + \
        str(canBrakeRemoterS) + '\t' + \
        str(canBrakeReal) + '\t' + \
        
        str(canGunMode) + '\t' + \
        str(canGunDepth) + '\t' + \
        str(canGunSpeed) + '\t' + \
        
        str(canSteerMode) + '\t' + \
        str(canSteerTorque) + '\t' + \
        str(canSteerException) + '\t' + \
        str(canSteerAngleH) + '\t' + \
        str(canSteerAngleL) + '\t' + \
        str(canSteerCalib) + '\t' + \
        str(canSteerBy6) + '\t' + \
        str(canSteerCheck) + '\t' + \

        str(planSpeed) + '\t' + \
        str(planSpeedMode) + '\t' + \
        str(planSpeedGear) + '\t' + \
        str(planSteer) + '\t' + \
        str(planSteerMode) + '\t' + \

        str(navDis) + '\t' + \
        str(navHead) + '\t' + \
        str(navDHead) + '\t' + \
        str(navDDHead) + '\t' + \

        str(controlWho) + '\t' + \
        str(controlMode) + '\t' + \
        str(controlValue) + '\n')
        if i % 10 == 0:
            print(line)

        f.write(line)

if __name__ == '__main__':
    main()
    pass


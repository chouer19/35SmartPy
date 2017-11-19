#!/usr/bin/env python
import rospy
from std_msgs.msg import String

from struct import pack,unpack,calcsize
import os
import time
import serial
import select
import math
import json

import threading,signal
import argparse
from MAPSpaceTime.msg import imu

is_exit = False

def main():
   parser = argparse.ArgumentParser()
   #input parameters
   #parser.add_argument('--islog')
   parser.add_argument('--init_from', type=str, default='file', help='read from COM or a file?')
   parser.add_argument('--device_name', type=str, default='/dev/ttyUSB0', help = 'the device name read from')
   parser.add_argument('--file_name', type=str, default='logs/ManyBigCircle.json', help = 'the file name read from')
   parser.add_argument('--log_dir', type=str, default='logs', help='save the data read to a file for record')
   parser.add_argument('--topic', type=str, default='CurIMUInfo', help='Publish Current IMU Info by a Topic Name')
   parser.add_argument('--node_name', type=str, default='imu_dev0', help='The Node publish messages by a Node Name')
   parser.add_argument('--baudrate', type=int, default=115200, help='the baudrate of SerialPort')
   parser.add_argument('--readout', type=int, default=50, help='the max len of serial port')
   parser.add_argument('--qlenPub', type=int, default=10, help='the max len of pub queue')
   parser.add_argument('--timeout', type=int, default=10, help='the max time of reading from COM')

   args = parser.parse_args()
   
   if args.init_from == 'device':
      #Init serail port and must be succeed
      args.ser = Init_Serial(args)
      #The device must be exsisted
      assert args.ser is not None,"assigned serial device can not be opened"
      #Init publisher
      #args.pub = Init_Pub(args)
 
      #logfile
      args.log_name = time.strftime("ImuLog%Y-%m-%d_%H:%M:%S.json", time.localtime())
      args.log_file = os.path.join(args.log_dir,args.log_name )
      args.fp = open(args.log_file, 'w+')
      data = '['
      args.fp.write(data)
   elif args.init_from == 'file':
      assert os.path.isfile(args.file_name),"src file file or directory not exist"

   assert args.init_from == 'device' or args.init_from == 'file',"Please be sure init_from device or file"

   #Init publisher
   args.pub = Init_Pub(args)

   #log(args, data)
   #read_tread
   signal.signal(signal.SIGINT, handler)
   signal.signal(signal.SIGTERM, handler)

   if args.init_from == 'device':
      args.read_thread = threading.Thread(target= serial_read, args = (args,"ReadSerialThread",))
      args.read_thread.setDaemon(True)
      args.read_thread.start()
   else:
      #print 'will enter the file_read thread'
      args.read_thread = threading.Thread(target= file_read, args = (args,"ReadSerialThread",))
      args.read_thread.setDaemon(True)
      args.read_thread.start()

   while True:
      alive=False
      alive = alive or args.read_thread.isAlive()
      if not alive:
         break
   
   if args.init_from == 'device':
      data = '{\"GPSTime1\":0,\"GPSTime2\":0, \"N_Satellite\":0,\"Lat\":0,\"Lon\":0,\"Height\":0,\"V_North\":0,\"V_East\":0,\"V_Earth\":0,\"V\":0,\"Roll\":0,\"Pitch\":0,\"Head\":0,\"A_North\":0,\"A_East\":0,\"A_Earth\":0,\"A\":0,\"V_Roll\":0,\"V_Pitch\":0,\"V_Head\":0,\"RTK_Status\":0}'
      log(args,data)   
      data = ']'
      args.fp.write(data)
      args.fp.close()

#write ontime-date in logfiles
def log(args, data):
   #json.dump(data,args.fp)
   args.fp.write(data)

#is_exit,guarantee write end before kill
def handler(signum, frame):
   global is_exit
   is_exit = True
   #print "receive a signal %d,is_exit = %d"%(signum, is_exit)

#init serial port
def Init_Serial(args):
   ser = serial.Serial(args.device_name, args.baudrate, timeout= args.timeout)
   if(ser.isOpen()):
      return ser
   else:
      return None

def file_read(args,name):
   global is_exit
   args.fp = open(args.file_name) 
   #print 'file opened'
   ontime_data = json.load(args.fp)
   i=600
   length = len(ontime_data)
   while not is_exit:
      if i == length - 800:
         i=600

      args.GPSTime1 = ontime_data[i]['GPSTime1']
      args.GPSTime2 = ontime_data[i]['GPSTime2']

      args.N_Satellite = ontime_data[i]['N_Satellite']

      args.Lat = ontime_data[i]['Lat']
      args.Lon = ontime_data[i]['Lon']
      args.Height = ontime_data[i]['Height']

      args.V_North = ontime_data[i]['V_North']
      args.V_East = ontime_data[i]['V_East']
      args.V_Earth = ontime_data[i]['V_Earth']
      args.V = ontime_data[i]['V']

      args.Roll = ontime_data[i]['Roll']
      args.Pitch = ontime_data[i]['Pitch']
      args.Head = ontime_data[i]['Head']

      args.A_North = ontime_data[i]['A_North']
      args.A_East = ontime_data[i]['A_East']
      args.A_Earth = ontime_data[i]['A_Earth']
      args.A = ontime_data[i]['A']

      args.V_Roll = ontime_data[i]['V_Roll']
      args.V_Pitch = ontime_data[i]['V_Pitch']
      args.V_Head = ontime_data[i]['V_Head']

      #args.RTK_Status = ontime_data[i]['RTK_Status']
      args.RTK_Status = 2

      args.pub.publish(imu(GPSTime1 = args.GPSTime1,
                           GPSTime2 = args.GPSTime2,
                           N_Satellite=args.N_Satellite,
                           Lat=args.Lat,
                           Lon=args.Lon,
                           Height=args.Height,
                           V_North=args.V_North,
                           V_East=args.V_East,
                           V_Earth=args.V_Earth,
                           V=args.V,
                           Roll=args.Roll,
                           Pitch=args.Pitch,
                           Head=args.Head,
                           A_North=args.A_North,
                           A_East=args.A_East,
                           A_Earth=args.A_Earth,
                           A=args.A,
                           V_Roll=args.V_Roll,
                           V_Pitch=args.V_Pitch,
                           V_Head=args.V_Head,
                           RTK_Status=args.RTK_Status))
      loginfo='{\"GPSTime1\":'+str(args.GPSTime1)+',\"GPSTime2\" :'+str(args.GPSTime2)+', \"N_Satellite\":'+str(args.N_Satellite)+',\"Lat\" :'+str(args.Lat)+',\"Lon\" :'+str(args.Lon)+',\"Height\" :'+str(args.Height)+',\"V_North\":'+str(args.V_North)+',\"V_East\":'+str(args.V_East)+',\"V_Earth\":'+str(args.V_Earth)+',\"V\":'+str(args.V)+',\"Roll\":'+str(args.Roll)+',\"Pitch\":'+str(args.Pitch)+',\"Head\":'+str(args.Head)+',\"A_North\":'+str(args.A_North)+',\"A_East\":'+str(args.A_East)+',\"A_Earth\":'+str(args.A_Earth)+',\"A\":'+str(args.A)+',\"V_Roll\":'+str(args.V_Roll)+',\"V_Pitch\":'+str(args.V_Pitch)+',\"V_Head\":'+str(args.V_Head)+',\"RTK_Status\":'+str(args.RTK_Status)+'}'

      #rospy.loginfo("==================================================")
      if i % 20 == 0:
         rospy.loginfo("[RTK_Status:%d,Lat:%f,Lon:%f,Head:%f]"%(args.RTK_Status,args.Lat,args.Lon,args.Head))

      #print i
      time.sleep(0.01)
      i = i+1


def serial_read(args,name):
   global is_exit
   head1, head2 = 0xAA,0x55
   head_first, head_second = 0x00,0x00
   #print 'come in serial_read function'
   while not is_exit:
      data = args.ser.read(1)
      if not data: continue
      head_second, = unpack('B', data)
      #print head_second
      if head_first == head1 and head_second == head2 :
         data = args.ser.read(1)  #length of this data
         data = args.ser.read(1)  #zuhe moshi

         data = args.ser.read(2)  #GPSTime1 unsigned short 2
         args.GPSTime1, = unpack('H',data) 
         #print 'GPSTime1:',args.GPSTime1
         data = args.ser.read(4)  #GPSTime2  Long 4
         args.GPSTime2, = unpack('i',data)
         #print 'GPSTime2:',args.GPSTime2
         data = args.ser.read(1)  #N_Satellite unsigned char 1
         args.N_Satellite, = unpack('B',data)
         #print 'N_Satallite:',args.N_Satellite
         
         data = args.ser.read(4)  #Lat  Long 4
         args.Lat, = unpack('i',data)
         args.Lat = float (args.Lat) / (10 ** 7)
         #print 'Lat:',args.Lat

         data = args.ser.read(4)  #Lon Long 4
         args.Lon, = unpack('i',data)
         args.Lon = float (args.Lon) / (10 ** 7)
         #print 'Lon:',args.Lon

         data = args.ser.read(4)  #Height Long 4
         args.Height, = unpack('i',data)
         args.Height = float (args.Height) / (10 ** 3)
         #print 'Height:',args.Height

         data = args.ser.read(4)  #V_North Long 4
         args.V_North, = unpack('i',data)
         args.V_North = float (args.V_North) / 1000
         #print 'V_North:',args.V_North

         data = args.ser.read(4)  #V_East Long 4
         args.V_East, = unpack('i',data)
         args.V_East = float(args.V_East) / 1000
         #print 'V_East:',args.V_East

         data = args.ser.read(4)  #V Long 4
         args.V_Earth, = unpack('i',data)
         args.V_Earth = float(args.V_Earth) / 1000
         #print 'V_Earth:',args.V_Earth

         args.V = math.sqrt(args.V_North**2 + args.V_East**2 + args.V_Earth**2)
         #print 'V:',args.V

         data = args.ser.read(4)  #Roll Long 4
         args.Roll, = unpack('i',data)
         args.Roll = float(args.Roll) / 1000
         #print 'Roll:',args.Roll

         data = args.ser.read(4)  #Pitch Long 4
         args.Pitch, = unpack('i',data)
         args.Pitch = float(args.Pitch) / 1000
         #print 'Pitch:',args.Pitch

         data = args.ser.read(4)  #Head usigned Long 4
         args.Head, = unpack('I',data)
         args.Head = float(args.Head) / 1000
         #print 'Head:',args.Head

         data = args.ser.read(2)  #A_North short 2
         args.A_North, = unpack('h',data)
         args.A_North = float(args.A_North) / 1000
         #print 'A_North:',args.A_North

         data = args.ser.read(2)  #A_East short 2
         args.A_East, = unpack('h',data)
         args.A_East = float(args.A_East) / 1000
         #print 'A_East:',args.A_East

         data = args.ser.read(2)  #A short 2
         args.A_Earth, = unpack('h',data)
         args.A_Earth = float(args.A_Earth) / 1000
         #print 'A_Earth:',args.A_Earth

         args.A = math.sqrt(args.A_North**2 + args.A_East**2 + args.A_Earth**2)
         #print 'A:',args.A

         data = args.ser.read(2)  #V_Roll short 2
         args.V_Roll, = unpack('h',data)
         args.V_Roll = float(args.V_Roll) / 1000
         #print 'V_Roll:',args.V_Roll

         data = args.ser.read(2)  #V_Pitch short 2
         args.V_Pitch, = unpack('h',data)
         args.V_Pitch = float(args.V_Pitch) / 1000
         #print 'V_Pitch:',args.V_Pitch

         data = args.ser.read(2)  #V_Head short 2
         args.V_Head, = unpack('h',data)
         args.V_Head = float(args.V_Head) / 1000
         #print 'V_Head:',args.V_Head        

         data = args.ser.read(1)  #V_Head short 2
         args.RTK_Status, = unpack('B',data)
         #print 'RTK_Status:',args.RTK_Status

         args.pub.publish(imu(GPSTime1 = args.GPSTime1, 
                              GPSTime2 = args.GPSTime2, 
                              N_Satellite=args.N_Satellite,
                              Lat=args.Lat,
                              Lon=args.Lon,
                              Height=args.Height,
                              V_North=args.V_North,
                              V_East=args.V_East,
                              V_Earth=args.V_Earth,
                              V=args.V,
                              Roll=args.Roll,
                              Pitch=args.Pitch,
                              Head=args.Head,
                              A_North=args.A_North,
                              A_East=args.A_East,
                              A_Earth=args.A_Earth,
                              A=args.A,
                              V_Roll=args.V_Roll,
                              V_Pitch=args.V_Pitch,
                              V_Head=args.V_Head,
                              RTK_Status=args.RTK_Status))
         loginfo='{\"GPSTime1\":'+str(args.GPSTime1)+',\"GPSTime2\" :'+str(args.GPSTime2)+', \"N_Satellite\":'+str(args.N_Satellite)+',\"Lat\" :'+str(args.Lat)+',\"Lon\" :'+str(args.Lon)+',\"Height\" :'+str(args.Height)+',\"V_North\":'+str(args.V_North)+',\"V_East\":'+str(args.V_East)+',\"V_Earth\":'+str(args.V_Earth)+',\"V\":'+str(args.V)+',\"Roll\":'+str(args.Roll)+',\"Pitch\":'+str(args.Pitch)+',\"Head\":'+str(args.Head)+',\"A_North\":'+str(args.A_North)+',\"A_East\":'+str(args.A_East)+',\"A_Earth\":'+str(args.A_Earth)+',\"A\":'+str(args.A)+',\"V_Roll\":'+str(args.V_Roll)+',\"V_Pitch\":'+str(args.V_Pitch)+',\"V_Head\":'+str(args.V_Head)+',\"RTK_Status\":'+str(args.RTK_Status)+'}'
         log(args, loginfo)
         data = ','
         #log(args, data)
         args.fp.write(data)
         rospy.loginfo("==================================================")
         rospy.loginfo("[RTK_Status:%d,Lat:%f,Lon:%f,Head:%f]"%(args.RTK_Status,args.Lat,args.Lon,args.Head))
         time.sleep(0.025)

         head_first, head_second = 0x00, 0x00
      head_first = head_second
   if is_exit:
      print "%s done"%name


def Init_Pub(args):
   #pub = rospy.Publisher(args.topic, imu, args.qlenPub)
   pub = rospy.Publisher(args.topic, imu, queue_size=10)
   rospy.init_node(args.node_name, anonymous=True)
   return pub


if __name__ == '__main__':
   main()

import navigator as car
import os
import random
import numpy as np
import argparse
import time
import json
import threading, signal

def doStress(args):
   global is_exit
   idx = 5
#    while not is_exit:
#        if (idx < 10000):
#            print "[%s]: idx=%d"%(name, idx)
#            idx = idx + 5
#        else:
#            break
#   args.Car.listen(args)
   if is_exit:
      print "receive a signal to exit, stop."
   else:
      print "thread complete."

def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)


def main():
   parser = argparse.ArgumentParser()
   #input parameters
   parser.add_argument('--map_file', type=str, default='logs/map.json', help='read from COM or a file?')
   parser.add_argument('--topic', type=str, default='CurIMUInfo', help='Publish Current IMU Info by a Topic Name')
   parser.add_argument('--node_name', type=str, default='imu_dev0_listener', help='The Node publish messages by a Node Name')
   parser.add_argument('--gap', type=int, default=1, help = 'how far can car run away from planned path')
   parser.add_argument('--min_dis', type=float, default=0.2, help= 'min distance between two points')
   
   args = parser.parse_args()

   #assert os.path.isfile(args.map_file),"%s file does not exit"

   print 'before entering the function worm_car'
   worm_car = car.Navigator(args)
   print 'succeeded, a new object'


if __name__ == "__main__":
#   main()
   parser = argparse.ArgumentParser()
   #input parameters
   parser.add_argument('--map_file', type=str, default='logs/map.json', help='read from COM or a file?')
   parser.add_argument('--topic', type=str, default='CurIMUInfo', help='Publish Current IMU Info by a Topic Name')
   parser.add_argument('--node_name', type=str, default='imu_dev0_listener', help='The Node publish messages by a Node Name')
   parser.add_argument('--gap', type=int, default=1, help = 'how far can car run away from planned path')
   parser.add_argument('--min_dis', type=float, default=0.2, help= 'min distance between two points')

   args = parser.parse_args()

   #assert os.path.isfile(args.map_file),"%s file does not exit"

   print 'before entering the function worm_car'
   args.Car = car.Navigator(args)
   print 'succeeded, a new object'


   signal.signal(signal.SIGINT, handler)
   signal.signal(signal.SIGTERM, handler)
   t = threading.Thread(target=doStress, args = (args,) )
   t.setDaemon(True)
   t.start()

   while 1:
      image_data,reward,terminal = args.Car.go_step()
      alive = False
      alive = alive or t.isAlive()
      if not alive:
         break
      


#!/usr/bin/env python
import rospy
from std_msgs.msg import String
import numpy as np
from struct import pack,unpack,calcsize
import os
import sys
import pygame
import pygame.surfarray as surfarray
from pygame.locals import *
import time
import serial
import select
import math

import json
import threading
import argparse
from MAPSpaceTime.msg import imu
import utils
# parameter definition

updata1=True
Lat1=Lat2=Lon1=Lon2=Head1=Head2=Height1=Height2=None
FPS = 20
SCREENWIDTH = 800
SCREENHEIGHT = 320 

PIXEL_PER_METER = 10
START_WIDTH = SCREENWIDTH / 8
START_HEIGHT = SCREENHEIGHT / 2

CAR_WIDTH = 5
CAR_HEIGHT = 2

CENTER_LINE_WIDTH = 5

pygame.init()
FPSCLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('wormQcar')

WHITE = (255 ,255 , 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

def main():
   parser = argparse.ArgumentParser()
   #input parameters
   #parser.add_argument('--islog')
   parser.add_argument('--map_file', type=str, default='logs/map3_OneBigCircle.json', help='the map')
   parser.add_argument('--image_dir', type=str, default='imgs/', help = 'save the image to')
   parser.add_argument('--log_dir', type=str, default='logs', help='save the data read to a file for record')
   parser.add_argument('--topic', type=str, default='CurIMUInfo', help='Publish Current IMU Info by a Topic Name')
   parser.add_argument('--node_name', type=str, default='imu_dev0', help='The Node publish messages by a Node Name')
   #parser.add_argument('',)
   
   args = parser.parse_args()
   args.gap = 2 
   args.min_dis = 0.2
   args.behind_road = 35 
   args.ahead_road = 105
   args.behind_num = args.behind_road / args.min_dis
   args.ahead_num = args.ahead_road / args.min_dis 

   #check and load map
   assert os.path.isfile(args.map_file),"does not exist the map_file"
   fp = open(args.map_file,'r')
   args.map = json.load(fp)
   args.map2 = args.map + args.map + args.map + args.map + args.map
   
   listen(args)


#one step return current path,in image
def go_step(args):

   #print 'go_step------------------------------------------->'
   pygame.event.pump()

   reward = 0.1
      
   terminal = False

   #if updata1:
   #   self.Lat,self.Lon,self.Head,self.Height = Lat2,Lon2,Head2,Height2
   #else:
   #   self.Lat,self.Lon,self.Head,self.Height = Lat1,Lon1,Head1,Height1

   index,dist = get_nearest(args)
   #print 'the nearest point is ',index,',the distance is ',dist
   if dist > args.gap:
      terminal = True
      reward = -1

   if index < args.behind_num:
      index = index + len(args.map)
   
   #print self.map

   args.startID = index - args.behind_num
   args.endID = index + args.ahead_num

   args.path = get_path(args)
   #print args.path
   # get top and bottom boarder
   top_pixel_list = []
   bottom_pixel_list = []
   center_pixel_list = []
   #print 'come to here'
   x0,y0 = args.path[0][0],args.path[0][1]
   i = 1
   while i < len(args.path):
      path_point = args.path[i]
      i = i+1
      x,y = path_point[0],path_point[1]
      distance = math.sqrt((y-y0)**2 + (x - x0) ** 2)
      #print 'between distance is : ',distance
      #detaX = args.gap * math.fabs(y - y0) / math.sqrt((y-y0)**2 + (x - x0) ** 2)
      #detaY = args.gap * math.fabs(x - x0) / math.sqrt((y-y0)**2 + (x - x0) ** 2)

      detaX = -1 * args.gap * (y - y0) / math.sqrt((y-y0) ** 2 + (x - x0) ** 2)
      detaY = args.gap * (x - x0) / math.sqrt((y-y0) ** 2 + (x - x0) ** 2)


      top_x = int((y + detaY ) * PIXEL_PER_METER + START_WIDTH)
      bottom_x = int((y - detaY ) * PIXEL_PER_METER + START_WIDTH)
         
      top_y = int ((x + detaX) * PIXEL_PER_METER + START_HEIGHT)
      bottom_y = int ((x - detaX) * PIXEL_PER_METER + START_HEIGHT)

      center_x = int(y * PIXEL_PER_METER + START_WIDTH)
      center_y = int(x * PIXEL_PER_METER + START_HEIGHT)

      #if center_x >=0 and center_x < 800 and center_y >=0 and center_y < 800:
      #   center_pixel_list.append([center_x,center_y])


      if top_x >=0 and top_x <SCREENWIDTH and top_y>=0 and top_y < SCREENHEIGHT and bottom_x >=0 and bottom_x <SCREENWIDTH and bottom_y>=0 and bottom_y < SCREENHEIGHT:
         top_pixel_list.append([top_x, top_y])
         bottom_pixel_list.append([bottom_x,bottom_y])
         center_pixel_list.append([center_x,center_y])
      
      x0,y0 = x,y

   road = top_pixel_list
   for point in bottom_pixel_list:
      road = [point] + road

   #print 'come to here'
   #top_pixel_list = [[0,0]] + top_pixel_list + [[SCREENWIDTH-1 , 0 ]]
   #bottom_pixel_list = [[0, SCREENHEIGHT-1 ]] + bottom_pixel_list + [[ SCREENWIDTH - 1, SCREENHEIGHT - 1 ]]
   car_pixel_list = [[START_WIDTH - CAR_WIDTH * PIXEL_PER_METER/2 ,START_HEIGHT - CAR_HEIGHT * PIXEL_PER_METER/2 ],[START_WIDTH + CAR_WIDTH * PIXEL_PER_METER /2 ,START_HEIGHT - CAR_HEIGHT * PIXEL_PER_METER /2 ],[START_WIDTH + CAR_WIDTH * PIXEL_PER_METER / 2 , START_HEIGHT + CAR_HEIGHT * PIXEL_PER_METER/2 ],[START_WIDTH - CAR_WIDTH * PIXEL_PER_METER/2,START_HEIGHT + CAR_HEIGHT * PIXEL_PER_METER/2 ]]
   #background filled with Black
   SCREEN.fill(BLACK)

   #print top_pixel_list
   #print 'come to here'
   #pygame.draw.polygon(SCREEN, RED, top_pixel_list)
   #pygame.draw.polygon(SCREEN, RED, bottom_pixel_list)
   pygame.draw.polygon(SCREEN, RED, road)
   pygame.draw.lines(SCREEN, WHITE, False, center_pixel_list, CENTER_LINE_WIDTH)
   pygame.draw.polygon(SCREEN, BLUE, car_pixel_list) 

   image_data = pygame.surfarray.array3d(pygame.display.get_surface())
   pygame.display.update()
   #FPSCLOCK.tick(FPS)

   #return image_data, reward, termial

      #draw
      

def get_path(args):
   path = []
   i = int(args.startID)
 
   while i < args.endID:
      x,y = utils.getRelatedXY(args.Lat, args.Lon, args.map2[i]['Lat'], args.map2[i]['Lon'], args.Head)
      path.append([x,y])
      i = i + 1
   return path

def get_nearest(args):
   dist = 999999
   index = 0;
   for i in range(len(args.map)):
      temp =  utils.DisBetweenPoints(args.Lat,args.Lon,args.map[i]['Lat'],args.map[i]['Lon'])
      if dist > temp and math.fabs(args.Head - args.map[i]['Head']) < 90:
         dist = temp
         index = i

   return index,dist


def callback(data,args):

   GPSTime1,GPSTime2,N_Satellite = data.GPSTime1,data.GPSTime2,data.N_Satellite
   Lat,Lon,Height = data.Lat,data.Lon,data.Height
   V_North,V_East,V_Earth,V= data.V_North,data.V_East,data.V_Earth,data.V
   Roll,Pitch,Head= data.Roll,data.Pitch,data.Head
   A_North,A_East,A_Earth,A = data.A_North,data.A_East,data.A_Earth,data.A
   V_Roll,V_Pitch,V_Head = data.V_Roll,data.V_Pitch,data.V_Head
   RTK_Status = data.RTK_Status
   
   #if RTK_Status == 2:
   #   if updata1:
   #      Lat1,Lon1,Head1,Height1 = Lat,Lon,Head,Height
   #   else:
   #      Lat2,Lon2,Head2,Height2 = Lat,Lon,Head,Height

   #   updata1 = not updata1
   #print 'received data'
   args.Lat,args.Lon,args.Head = Lat,Lon,Head
   go_step(args)

   rospy.loginfo("==============================================================")
   rospy.loginfo("[Lat:%f,Lon:%f,Head:%f]"%(Lat,Lon,Head))

def listen(args):
   rospy.init_node(args.node_name, anonymous=True)
   #print 'ros node init finished'
   rospy.Subscriber(args.topic, imu, callback,args)
   rospy.spin()


if __name__ == '__main__':
    main()

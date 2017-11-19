#!/usr/bin/env python
import os
import json
import argparse

import utils

def main():
   parser = argparse.ArgumentParser()
   #input parameters
   #parser.add_argument('--islog')
   parser.add_argument('--src_file', type=str, default='logs/ontime.json', help = 'the file name read from')
   parser.add_argument('--dst_dir', type=str, default='logs/', help = 'the file name read from')
   parser.add_argument('--dst_name', type=str, default='map.json', help = 'the file name read from')
   parser.add_argument('--min_dis', type=float, default=0.2 , help = 'the file name read from')

   args = parser.parse_args()

   assert os.path.isfile(args.src_file),"the src_file is not exist"
   #assert os.path.isfile(args.dst_file),"the src_file is not exist"
   assert os.path.isdir(args.dst_dir),"the dst_dir is not exist" 

   #os.path.join(args.dst_dir,args.dst_name)

   generate_map(args)
   #print 'args.map is',args.map
   #fp = open(args.dst_name,'w+')
   #json.dump(args.map,fp) 


def generate_map(args):
   point_p = {'Lat':0.00001,'Lon':0.00001,'Height':0.00001,'Head':0.00001}
   point_q = {'Lat':0.00001,'Lon':0.00001,'Height':0.00001,'Head':0.00001}
   point_0 = {'Lat':0.00001,'Lon':0.00001,'Height':0.00001,'Head':0.00001} #present start
   point_9 = {'Lat':0.00001,'Lon':0.00001,'Height':0.00001,'Head':0.00001} #present end
   path = []
   startID=0
   endID=0
   fp = open(args.src_file)
   # map file for saving point
   ffpp = open(os.path.join(args.dst_dir,args.dst_name), 'w+')
   src_map = json.load(fp)
   endID = len(src_map) - 1
   point_0['Lat'], point_0['Lon'], point_0['Height'],point_0['Head'] =src_map[0]['Lat'],src_map[0]['Lon'],src_map[0]['Height'],src_map[0]['Height']
   # fine a start point
   for i in range(len(src_map)):
      #print 'generating a map:',i,'/',len(src_map)
      point_p['Lat'], point_p['Lon'], point_p['Height'],point_p['Head'] =src_map[i]['Lat'],src_map[i]['Lon'],src_map[i]['Height'],src_map[i]['Head']
      if utils.DisBetweenPoints(point_0['Lat'], point_0['Lon'], point_p['Lat'], point_p['Lon']) > 8 :
         startID = i
         point_0['Lat'], point_0['Lon'], point_0['Height'],point_0['Head'] = point_p['Lat'], point_p['Lon'], point_p['Height'],point_p['Head']
         break
   print 'find the startID',startID

   data = "[{\"Lat\":"+ str(point_p['Lat']) +","+"\"Lon\":"+str(point_p['Lon']) +"," +"\"Height\":"+str(point_p['Height']) +"," +"\"Head\":"+str(point_p['Head'])+ "}"
   ffpp.write(data)

   currentID = startID + 1
   i = 0
   while currentID < len(src_map):
      #print 'generating a map:',currentID,'/',len(src_map)
      if utils.DisBetweenPoints(src_map[currentID]['Lat'], src_map[currentID]['Lon'], point_p['Lat'], point_p['Lon']) > args.min_dis :
         point_p['Lat'], point_p['Lon'], point_p['Height'],point_p['Head'] =src_map[currentID]['Lat'],src_map[currentID]['Lon'],src_map[currentID]['Height'],src_map[currentID]['Head']
         #path.append(point_p)
         data = ",{\"Lat\":"+ str(point_p['Lat']) +","+"\"Lon\":"+str(point_p['Lon']) +"," +"\"Height\":"+str(point_p['Height']) +"," +"\"Head\":"+str(point_p['Head'])+ "}"
         ffpp.write(data)
         print 'selected the ',currentID,' th/',len(src_map),' point'
         i = i + 1
         if utils.DisBetweenPoints(src_map[startID]['Lat'], src_map[startID]['Lon'], src_map[currentID]['Lat'], src_map[currentID]['Lon']) < 2 and i > 11 :
            endID = currentID
            print 'find the endID',endID
            break
      currentID = currentID + 1

   sumdist = 0;
   i = 0;
   while currentID < len(src_map):
      #print 'generating a map:',currentID,'/',len(src_map)
      dist = utils.DisBetweenPoints(src_map[currentID]['Lat'], src_map[currentID]['Lon'], point_p['Lat'], point_p['Lon'])
      if dist > args.min_dis :
         point_p['Lat'], point_p['Lon'], point_p['Height'] = src_map[currentID]['Lat'], src_map[currentID]['Lon'],src_map[currentID]['Height']
         #path.append(point_p)
         data = ",{\"Lat\":"+ str(point_p['Lat']) +","+"\"Lon\":"+str(point_p['Lon']) +"," +"\"Height\":"+str(point_p['Height']) +"," +"\"Head\":"+str(point_p['Head'])+ "}"
         ffpp.write(data)
         print 'selected the ',currentID,' th/',len(src_map),' point'
         sumdist = sumdist + dist
         if sumdist > 1.6:
            break;
      currentID = currentID + 1

   fp.close()
   data=']'
   ffpp.write(data)
   ffpp.close()

   print 'finished generating a map'


if __name__ == '__main__':
   main()

#!/usr/bin/env python
import os
import json
import argparse

sys.path.append("../libs")
from proCAN import *
from proContext import *
from proPID import *
from proGNSS import *
import UTM


def main():
    parser = argparse.ArgumentParser()
    #input parameters
    #parser.add_argument('--islog')
    parser.add_argument('--src', type=str, default='logs/ontime.json', help = 'the file name read from')
    parser.add_argument('--dst_dir', type=str, default='logs/', help = 'the file name read from')
    parser.add_argument('--dst_name', type=str, default='map.json', help = 'the file name read from')
    parser.add_argument('--min_dis', type=float, default=0.2 , help = 'the file name read from')

    args = parser.parse_args()

    assert os.path.isfile(args.src),"the src is not exist"

    utm_list = []
    last_utm = {"easting":0, "norting":0, "zone_num":0, "zone_letter":'N' }
    utm = {"easting":0, "norting":0, "zone_num":0, "zone_letter":'N' }
    with open(args.src) as f:
        for line in f:
            content = line
            lat = content['Lat']
            lon = content['Lon']
            easting, northing, zone_num, zone_letter = UTM.from_latlon(lat,lon)
            #utm =  {"easting":easting, "northing":northing,"zone_num":zone_num, "zone_letter":zone_letter }
            utm['easting'] = easting
            utm['northing'] = northing
            utm['zone_num'] = zone_num
            utm['zone_letter'] = zone_letter
            #utm_last = {"easting":easting, "northing":northing,"zone_num":zone_num, "zone_letter":zone_letter }
            break

    with open(args.src) as f:
        for line in f:
            content = line
            lat = content['Lat']
            lon = content['Lon']
            easting, northing, zone_num, zone_letter = UTM.from_latlon(lat,lon)
            utm_list.append( {"easting":easting, "northing":northing,"zone_num":zone_num, "zone_letter":zone_letter }  )
            if ( (utm['easting'] - easting) ** 2 + (utm['northing'] - northing ) ** 2 ) < (args.min_dis) ** 2:
                i = 1


            if ( (utm['easting'] - easting) ** 2 + (utm['northing'] - northing ) ** 2 ) > (args.min_dis * 2) ** 2:
                dist = math.sqrt(( utm['easting'] - easting) ** 2 + (utm['northing'] - northing ) ** 2 )
                chazhi_num = int ( dist / args.min_dis)
                deltaE =pass 
                for i in range(1,chazhi_num):
                    
                    pass
            
            utm['easting'] = easting
            utm['northing'] = northing
            utm['zone_num'] = zone_num
            utm['zone_letter'] = zone_letter

if __name__ == '__main__':
    main()

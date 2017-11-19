#!/usr/bin/env python
import os
import json
import argparse


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

    utm_list

    with open(args.src) as f:
        for line in f:
            content = line

if __name__ == '__main__':
    main()

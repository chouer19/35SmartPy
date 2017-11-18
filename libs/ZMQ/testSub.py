
import zmq
from proContext import *
import time

ctx = proContext()
sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:6001')
sub.setsockopt(zmq.SUBSCRIBE,'shabi')

sub2 = ctx.socket(zmq.SUB)
sub2.connect('inproc://localhost:6001')
sub2.setsockopt(zmq.SUBSCRIBE,'test')
#content = {'name':'xuechong', 'age':24, 'school':}
i = 0

while True:
    content = sub.recvPro()
    print(i)
    i = i+1
    i = i % 1000
    print("topic : shabi")
    print('name :',content['name'], 'age : ',content['age'], 'school : ', content['school'])
    content = sub2.recvPro()
    print("topic : xuechong")
    print('name :',content['name'], 'age : ',content['age'], 'school : ', content['school'])


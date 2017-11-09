
import zmq
from serialTopicSocket import *
import time

ctx = SerialTopicContext()
sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:6001')
#sub.setsockopt(zmq.SUBSCRIBE,'test')
sub.setsockopt(zmq.SUBSCRIBE,'shabi')

#content = {'name':'xuechong', 'age':24, 'school':}


while True:
    content = sub.recvSerialTopic()
    print("topic : shabi")
    print('name :',content['name'], 'age : ',content['age'], 'school : ', content['school'])

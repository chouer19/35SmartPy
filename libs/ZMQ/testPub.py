
import zmq
from serialTopicSocket import *
import time

ctx = SerialTopicContext()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:6001')

content = {'name':'xuechong', 'age':24, 'school':'Tsinghua'}
content_ = {'name':'shabi', 'age':100, 'school':'Tuttle'}


while True:
    pub.sendSerialTopic('test',content)
    time.sleep(0.2)
    pub.sendSerialTopic('shabi',content_)
    time.sleep(0.2)

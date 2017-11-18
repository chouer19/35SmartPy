
import zmq
import zlib
import pickle

class SerialTopicSocket(zmq.Socket):

    def sendPro(self, topic , obj,flags=0, protocol = -1):
        pobj = pickle.dumps(obj, protocol)
        zobj = zlib.compress(pobj)
        return self.send_multipart([topic, zobj])

    def recvPro(self, flags=0):
        topic,zobj = self.recv_multipart(flags)
        pobj = zlib.decompress(zobj)
        return pickle.loads(pobj)

class proContext(zmq.Context):
    _socket_class = SerialTopicSocket

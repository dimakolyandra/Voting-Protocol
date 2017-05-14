import zmq
import pickle
from Crypto.PublicKey import RSA


class ClientVote:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(port)

    def send_msg(self, cmd, msg):
        self.socket.send(pickle.dumps((cmd, msg)))
        ans = pickle.loads(self.socket.recv())
        return ans

    def register_request(self):
        ans = self.send_msg('register_request','')
        if ans != 'ok':
            raise MyException

    def go(self):
        self.register_request()


if __name__=="__main__":
    client = ClientVote('tcp://127.0.0.1:9090')
    client.go()
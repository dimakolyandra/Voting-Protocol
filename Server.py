import zmq
import pickle


class ServerVote:

    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)

    def go(self, port):
        self.socket.bind(port)
        while True:
            cmd, msg = pickle.loads(self.socket.recv())
            print(cmd, msg)
            self.socket.send(pickle.dumps('ok'))

server = ServerVote()
server.go('tcp://127.0.0.1:9090')
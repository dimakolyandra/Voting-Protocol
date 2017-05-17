import zmq
import pickle
import RunningCommandException as myexc
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class ClientVote:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(port)
        self.client_private_key = RSA.generate(2048)
        self.server_open_key = ""
        f = open('client_private_key.txt','w')
        f.write(str(self.client_private_key.exportKey()))
        f.close()
        f = open('client_public_key.txt','w')
        self.client_public_key = self.client_private_key.publickey()
        f.write(str(self.client_public_key.exportKey()))
        f.close()

    def send_msg(self, *msg):
        self.socket.send(pickle.dumps(msg))
        ans = pickle.loads(self.socket.recv())
        return ans

    def encrypt_msg(self, msg):
        encr_msg = self.encrypt_obj.encrypt(msg.encode(),0)
        return encr_msg

    def register_request(self):
        d, self.server_open_key = self.send_msg('register_request', '')
        self.encrypt_obj = RSA.importKey(self.server_open_key.exportKey())
        sort_dict = sorted(d.keys())
        for key in sort_dict:
            print(key, end=": ")
            need_data = input()
            d[key] = self.encrypt_msg(need_data)
        ans = self.send_msg('finish_register', d,self.client_public_key)
        if ans != 'ok':
            raise myexc.RunningCommandException()

    def go(self):
        try:
            self.register_request()
        except myexc.RunningCommandException:
            print(myexc.RunningCommandException.text)


if __name__ == "__main__":
    client = ClientVote('tcp://127.0.0.1:9090')
    client.go()
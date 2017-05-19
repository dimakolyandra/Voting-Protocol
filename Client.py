import zmq
import pickle
import RunningCommandException as myexc
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class ClientVote:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(port)
        self.client_private_key = RSA.generate(2048)
        self.server_open_key = ""
        self.id = -1
        f = open('client_private_key.txt','w')
        f.write(str(self.client_private_key.exportKey()))
        f.close()
        f = open('client_public_key.txt','w')
        self.client_public_key = self.client_private_key.publickey()
        f.write(str(self.client_public_key.exportKey()))
        f.close()

    def send_msg(self, *msg):
        """ Отправить сообщение """
        self.socket.send(pickle.dumps(msg))
        ans = pickle.loads(self.socket.recv())
        return ans

    def encrypt_msg(self, msg, session_key):
        """ Зашифровать сообщение"""
        iv = Random.new().read(16)
        obj = AES.new(session_key, AES.MODE_CFB, iv)
        encrypted_msg = iv + obj.encrypt(msg)
        encr_session_key = self.encrypt_obj.encrypt(session_key, 0)
        return encr_session_key, encrypted_msg

    def register_request(self, session_key):
        """ Запрос на решистрацию"""
        d, self.server_open_key = self.send_msg('register_request', '', '-1', '-1', self.id)
        if d == -1:
            print('You already have been registered!')
        else:
            self.encrypt_obj = RSA.importKey(self.server_open_key.exportKey())
            sort_dict = sorted(d.keys())
            for key in sort_dict:
                print(key, end=": ")
                need_data = input()
                encr_session_key, d[key] = self.encrypt_msg(need_data, session_key)
            ans, id = self.send_msg('finish_register', d, encr_session_key, self.client_public_key,'-1')
            if ans != 'ok':
                raise myexc.RunningCommandException()
            else:
                self.id = id

    def begin_voting(self, session_key):

        self.send_msg('begin_voting','',)


    def go(self):
        """ Основной цикл работы"""
        while True:
            try:
                session_key = Random.new().read(32)
                cmd = input()
                if cmd == "-r":
                    self.register_request(session_key)
                if cmd == "-v":
                    self.begin_voting(session_key)
            except myexc.RunningCommandException:
                print(myexc.RunningCommandException.text)


if __name__ == "__main__":
    client = ClientVote('tcp://127.0.0.1:8090')
    client.go()

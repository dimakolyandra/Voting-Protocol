import zmq
import pickle
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random

class ServerVote:
    def __init__(self):
        """ Начальная инициализация """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.data_of_constituency = []
        self.server_private_key = RSA.generate(2048)
        self.decryption_obj = RSA.importKey(self.server_private_key.exportKey())
        f = open('server_private_key.txt', 'w')
        f.write(str(self.server_private_key.exportKey()))
        f.close()
        self.server_public_key = self.server_private_key.publickey()
        f = open('server_public_key.txt', 'w')
        f.write(str(self.server_public_key.exportKey()))
        f.close()

    def register_in_base(self, d):
        """ Зарегистрировать в базе """
        dictionary = {'id': '', 'first_name': '', 'second_name': '', 'open_key': ''}
        id = len(self.data_of_constituency) + 1
        dictionary['id'] = id
        dictionary['first_name'] = d['first_name']
        dictionary['second_name'] = d['second_name']
        dictionary['open_key'] = d['open_key']
        self.data_of_constituency.append(dictionary)
        return id

    #def encrypt_msg(self, msg, session_key, id):
    #    """ Зашифровать сообщение"""
    #    encrypt_obj = RSA.importKey(self.server_open_key.exportKey())
    #    iv = Random.new().read(16)
    #    obj = AES.new(session_key, AES.MODE_CFB, iv)
    #    encrypted_msg = iv + obj.encrypt(msg)
    #    encr_session_key = encrypt_obj.encrypt(session_key, 0)
    #    return encr_session_key, encrypted_msg

    def decrypt_msg(self, msg, session_key):
        """ Расшифровать сообщение """
        iv = msg[:16]
        obj = AES.new(session_key, AES.MODE_CFB, iv)
        decrypt_msg = obj.decrypt(msg)
        return decrypt_msg[16:]

    def begin_register(self,id):
        if id != -1:
            self.socket.send(pickle.dumps(-1))
        else:
            d = {'first_name': '', 'second_name': ''}
            self.socket.send(pickle.dumps((d, self.server_public_key)))

    def finish_register(self,msg,session_key,client_public_key):
        decr_session_key = self.decryption_obj.decrypt(session_key)
        msg['first_name'] = self.decrypt_msg(msg['first_name'], decr_session_key)
        msg['second_name'] = self.decrypt_msg(msg['second_name'], decr_session_key)
        msg['open_key'] = client_public_key.exportKey()
        id = self.register_in_base(msg)
        self.socket.send(pickle.dumps(('ok', id)))
        print(self.data_of_constituency)

    def go(self, port):
        """ Главный цикл """
        self.socket.bind(port)
        while True:
            cmd, msg, session_key, client_public_key, id = pickle.loads(self.socket.recv())
            if cmd == 'register_request':
                self.begin_register(id)
            if cmd == 'finish_register':
                self.finish_register(msg,session_key,client_public_key)

if __name__ == "__main__":
    server = ServerVote()
    server.go('tcp://127.0.0.1:8090')

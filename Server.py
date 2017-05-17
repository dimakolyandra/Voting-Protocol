import zmq
import pickle
from Crypto.PublicKey import RSA
import random

class ServerVote:

    """ Класс, реализующий голосование """

    def __init__(self):

        """ Начальная инициализация """

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.data_of_constituency = [{'id':'','data':{}}]
        self.server_private_key = RSA.generate(2048)
        self.decryption_obj = RSA.importKey(self.server_private_key.exportKey())
        f = open('server_private_key.txt', 'w')
        f.write(str(self.server_private_key.exportKey()))
        f.close()
        self.server_public_key = self.server_private_key.publickey()
        f = open('server_public_key.txt', 'w')
        f.write(str(self.server_public_key.exportKey()))
        f.close()

    #def register_in_base(self,d):
    #    id = random.random(0,100)
    #    dictionary = {'id': '', 'first_name': '', 'second_name': '', 'open_key': ''}
    #    if dictionary['id'] != '':



    def run_cmd(self, cmd, msg):

        """ Выполнение запроса клиента """

        if cmd == 'register_request':
            d = {'first_name':'','second_name':''}
            self.socket.send(pickle.dumps((d,self.server_public_key)))
            cmd, new_dict, client_pub_key = pickle.loads(self.socket.recv())
            if cmd == "finish_register":
                new_dict['first_name'] = self.decryption_obj.decrypt(new_dict['first_name'])
                new_dict['second_name'] = self.decryption_obj.decrypt(new_dict['second_name'])
                new_dict['open_key'] = client_pub_key.exportKey()
                # self.register_in_base()
                self.socket.send(pickle.dumps('ok'))
            print(new_dict)

    def go(self, port):

        """ Главный цикл """

        self.socket.bind(port)
        while True:
            try:
                cmd, msg = pickle.loads(self.socket.recv())
                self.run_cmd(cmd,msg)
            except Exception:
                self.socket.send(pickle.dumps('error'))

if __name__ == "__main__":
    server = ServerVote()
    server.go('tcp://127.0.0.1:9090')
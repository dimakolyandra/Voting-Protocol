import zmq
import pickle
import Cryptographer as crypt
import datetime
import Timer
import os

class ServerVote:
    def __init__(self):
        """ Начальная инициализация """
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.data_of_constituency = []
        self.cryptographer = crypt.Cryptographer()
        self.encrypt_results = []
        self.is_end_of_voting = False
        self.form_of_voting = [
            {'FIO': 'Ivanov Ivan Ivanovich',
             'rating': ''},
            {'FIO': 'Sergeev Andrew Andreevich',
             'rating': ''},
            {'FIO': 'Putin Vladimir Vladimirovich',
             'rating': ''}
        ]
        f = open('server_private_key.txt', 'w')
        f.write(str(self.cryptographer.decryption_obj))
        f.close()
        f = open('server_public_key.txt', 'w')
        f.write(str(self.cryptographer.public_key.exportKey()))
        f.close()
        self.time_of_start = datetime.datetime.now()

    def register_in_base(self, d):
        """ Зарегистрировать в базе """
        dictionary = {'id': '',
                      'first_name': '',
                      'second_name': '',
                      'open_key': '',
                      'secret_key':'-1',
                      'form': [],
                      'closed':'-1'}
        id = len(self.data_of_constituency) + 1
        dictionary['id'] = id
        dictionary['first_name'] = d['first_name']
        dictionary['second_name'] = d['second_name']
        dictionary['open_key'] = d['open_key']
        dictionary['is_voted'] = False
        self.data_of_constituency.append(dictionary)
        return id

    def find_client_open_key(self, id):
        for el in self.data_of_constituency:
            if el['id'] == id:
                return el['open_key']

    def find_index_client(self, id):
        for i in range(0, len(self.data_of_constituency)):
            if self.data_of_constituency[i]['id'] == id:
                return i

    def begin_register(self, id):
        if id != -1:
            self.socket.send(pickle.dumps(-1))
        else:
            d = {'first_name': '', 'second_name': ''}
            self.socket.send(pickle.dumps((d, self.cryptographer.public_key)))

    def finish_register(self, msg, session_key, client_public_key, new_session_key):
        decr_session_key = self.cryptographer.decrypt_session_key(session_key)
        msg['first_name'] = self.cryptographer.decrypt_msg(msg['first_name'], decr_session_key)
        msg['second_name'] = self.cryptographer.decrypt_msg(msg['second_name'], decr_session_key)
        msg['open_key'] = client_public_key.exportKey()
        id = self.register_in_base(msg)
        encr_id = self.cryptographer.encrypt_msg(repr(id), new_session_key)
        encr_session_key = self.cryptographer.encrypt_session_key(new_session_key, client_public_key.exportKey())
        self.socket.send(pickle.dumps(('ok', encr_session_key, encr_id)))

    def begin_voting(self,session_key, id):
        public_key = self.find_client_open_key(id)
        enc_form = []
        for field in self.form_of_voting:
            enc_dict = {'FIO': '', 'rating': ''}
            enc_dict['FIO'] = self.cryptographer.encrypt_msg(field['FIO'], session_key)
            enc_form.append(enc_dict)
        encr_session_key = self.cryptographer.encrypt_session_key(session_key, public_key)
        self.socket.send(pickle.dumps((encr_session_key, enc_form)))

    def get_status(self, thread):
        if self.is_end_of_voting:
            self.socket.send(pickle.dumps('The results are available on the server'))
        elif thread.is_alive():
            self.socket.send(pickle.dumps('Voting!'))
        else:
            self.socket.send(pickle.dumps('Voting end!'))

    def save_results_of_voting(self, msg,enc_session_key, enc_id):
        dec_session_key = self.cryptographer.decrypt_session_key(enc_session_key)
        dec_id = self.cryptographer.decrypt_msg(enc_id, dec_session_key)
        index = self.find_index_client(int(dec_id))
        need_client = self.data_of_constituency[index]
        if len(need_client['form']) == 0:
            need_client['form'] = msg
            self.socket.send(pickle.dumps('Wait results!'))
        else:
            self.socket.send(pickle.dumps('You have already sent results!'))

    def is_all_secret_key(self):
        for el in self.data_of_constituency:
            if el['secret_key'] == '-1':
                return False

    def save_secret_key(self,enc_secret_key, enc_session_key, id):
        decr_session_key = self.cryptographer.decrypt_session_key(enc_session_key)
        dec_id = self.cryptographer.decrypt_msg(id, decr_session_key)
        decr_secret_key = self.cryptographer.decrypt_session_key(enc_secret_key)
        index = self.find_index_client(int(dec_id))
        d = self.data_of_constituency[index]
        d['secret_key'] = decr_secret_key
        self.socket.send(pickle.dumps('The votes are counted'))

    def decrypt_results(self):
        for d in self.data_of_constituency:
            secr_key = d['secret_key']
            for el in d['form']:
                el['rating'] = self.cryptographer.decrypt_msg(el['rating'], secr_key)
                el['FIO'] = self.cryptographer.decrypt_msg(el['FIO'], secr_key)

    def print_results_of_voting(self, results):
        self.is_end_of_voting = True
        print("-"*10)
        print("Results of voting!")
        for key in results.keys():
            print(key,": ",results[key])
        print("-"*10)

    def counting_votes(self):
        self.decrypt_results()
        result_dict = {}
        for d in self.data_of_constituency:
            for el in d['form']:
                result_dict[el['FIO']] = 0
        for d in self.data_of_constituency:
            for el in d['form']:
               rating = str(el['rating']).split("'")
               result_dict[el['FIO']] += int(rating[1])
        self.print_results_of_voting(result_dict)

    def is_all_clients_quit(self):
        for d in self.data_of_constituency:
            if d['closed'] == '-1':
                return False
        return True

    def add_to_closed(self, id):
        for d in self.data_of_constituency:
            if d['id'] == id:
                d['closed'] = '1'

    def go(self, port):
        """ Главный цикл """
        self.socket.bind(port)
        t = Timer.start_timer(self.time_of_start)
        while t.is_alive():
            new_session_key = self.cryptographer.get_session_key()
            cmd, msg, session_key, client_public_key, id = pickle.loads(self.socket.recv())
            if cmd == 'register_request':
                self.begin_register(id)
            if cmd == 'finish_register':
                self.finish_register(msg, session_key, client_public_key, new_session_key)
            if cmd == 'begin_voting':
                self.begin_voting(new_session_key, id)
            if cmd == 'vote_result':
                self.save_results_of_voting(msg, session_key, id)
            if cmd == 'get_status':
                self.get_status(t)
            if cmd == 'secret_key':
                self.save_secret_key(msg, session_key, id)
        print("Time of voting is end!")
        while self.is_all_secret_key() == False:
            cmd, msg, session_key, client_public_key, id = pickle.loads(self.socket.recv())
            if cmd == 'get_status':
                self.get_status(t)
            if cmd == 'secret_key':
                self.save_secret_key(msg, session_key, id)
        self.counting_votes()
        while self.is_all_clients_quit() == False:
            cmd, msg, session_key, client_public_key, id = pickle.loads(self.socket.recv())
            if cmd == 'get_status':
                self.get_status(t)
                self.add_to_closed(id)

if __name__ == "__main__":
    server = ServerVote()
    server.go('tcp://127.0.0.1:8090')

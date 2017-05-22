import zmq
import pickle
import Cryptographer as crypt
import RunningCommandException as myexc


class ClientVote:

    def __init__(self, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(port)
        self.server_open_key = ""
        self.id = -1
        self.is_vote = False
        self.is_end_of_time = False
        self.is_send_results = False
        self.close_client = False
        self.cryptographer = crypt.Cryptographer()
        f = open('client_private_key.txt','w')
        f.write(str(self.cryptographer.decryption_obj))
        f.close()
        f = open('client_public_key.txt','w')
        f.write(str(self.cryptographer.public_key.exportKey()))
        f.close()

    def send_msg(self, *msg):
        """ Отправить сообщение """
        self.socket.send(pickle.dumps(msg))
        ans = pickle.loads(self.socket.recv())
        return ans

    def register_request(self, session_key):
        """ Запрос на решистрацию"""
        if self.id != -1:
            print('You already have been registered!')
            return
        if self.is_vote:
            print('You already start voting!')
            return
        d, self.server_open_key = self.send_msg('register_request', '', '-1', '-1', self.id)
        sort_dict = sorted(d.keys())
        for key in sort_dict:
            print(key, end=": ")
            need_data = input()
            d[key] = self.cryptographer.encrypt_msg(need_data, session_key)
        encr_session_key = self.cryptographer.encrypt_session_key(session_key, self.server_open_key.exportKey())
        ans, encr_session_key, id = self.send_msg('finish_register', d, encr_session_key, self.cryptographer.public_key,'-1')
        if ans != 'ok':
            raise myexc.RunningCommandException()
        else:
            dec_key = self.cryptographer.decrypt_session_key(encr_session_key)
            dec_id = self.cryptographer.decrypt_msg(id, dec_key)
            print("Your id: ", int(dec_id))
            self.id = int(dec_id)

    def begin_voting(self, session_key):
        if self.is_vote:
            print('You already start voting!')
            return
        if self.id == -1:
            print('You need register!')
            return
        self.is_vote = True
        enc_session_key, enc_form = self.send_msg('begin_voting', '', '', '', self.id)
        dec_session_key = self.cryptographer.decrypt_session_key(enc_session_key)
        dec_form = []
        for el in enc_form:
            dec_dict = {'FIO': '', 'rating': ''}
            dec_dict['FIO'] = self.cryptographer.decrypt_msg(el['FIO'], dec_session_key)
            dec_form.append(dec_dict)
        self.form = self.fill_form(dec_form)


    def is_right_rating(self, rating):
        if rating.isdigit() and int(rating) > 0 and int(rating) < 6:
            return True
        else:
            return False

    def fill_form(self, form):
        print('For each candidate enter range from 1 to 5!')
        for el in form:
            print('FIO: ', el['FIO'])
            print('Enter rating:', )
            rating = input()
            while self.is_right_rating(rating) == False:
                print('Wrong rating!')
                rating = input()
            el['rating'] = repr(rating)
        return form

    def send_result_of_voting(self, session_key):
        if self.is_send_results == True:
            print("Time of voting is end!")
            return
        if self.is_vote == False:
            print("You did not start voting!")
            return
        self.is_send_results = True
        self.secret_key = self.cryptographer.get_session_key()
        for el in self.form:
            el['FIO'] = self.cryptographer.encrypt_msg(el['FIO'],self.secret_key)
            el['rating'] = self.cryptographer.encrypt_msg(el['rating'], self.secret_key)
        encr_id = self.cryptographer.encrypt_msg(repr(self.id), session_key)
        encr_sesion_key = self.cryptographer.encrypt_session_key(session_key, self.server_open_key.exportKey())
        ans = self.send_msg('vote_result', self.form, encr_sesion_key, '-1', encr_id)
        print(ans)

    def get_status(self):
        ans = self.send_msg('get_status', '-1', '-1', '-1', self.id)
        if ans == 'The results are available on the server':
            self.close_client = True
        if ans == 'Voting end!':
            self.is_end_of_time = True
        print(ans)

    def send_secret_key(self, session_key):
        if self.is_send_results == False:
            print('You did not start voting!')
            return
        enc_secret_key = self.cryptographer.encrypt_session_key(self.secret_key, self.server_open_key.exportKey())
        enc_session_key = self.cryptographer.encrypt_session_key(session_key, self.server_open_key.exportKey())
        enc_id = self.cryptographer.encrypt_msg(repr(self.id), session_key)
        ans = self.send_msg('secret_key',  enc_secret_key, enc_session_key, '-1', enc_id)
        print(ans)

    def go(self):
        """ Основной цикл работы"""
        while True:
            try:
                #session_key = Random.new().read(32)
                if self.close_client:
                    break
                session_key = self.cryptographer.get_session_key()
                cmd = input()
                if cmd == "-reg":
                    self.register_request(session_key)
                if cmd == "-vote":
                    self.begin_voting(session_key)
                if cmd == '-send':
                    self.send_result_of_voting(session_key)
                if cmd == '-res':
                    self.get_status()
                if cmd == '-secr':
                    if self.is_end_of_time:
                        self.send_secret_key(session_key)
                    else:
                        print("Voting is not end!")
            except myexc.RunningCommandException:
                print(myexc.RunningCommandException.text)
        print("Good luck!")

if __name__ == "__main__":
    client = ClientVote('tcp://127.0.0.1:8090')
    client.go()

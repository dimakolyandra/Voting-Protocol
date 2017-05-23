from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class Cryptographer:

    def __init__(self):
        """ Инициализация """
        self.private_key = RSA.generate(2048)
        self.decryption_obj = RSA.importKey(self.private_key.exportKey())
        self.public_key = self.private_key.publickey()

    def get_session_key(self):
        """ Генерация сессионного ключа """
        return Random.new().read(32)

    def encrypt_session_key(self, session_key, public_key):
        """ Зашифровка сесионного ключа """
        self.encrypt_obj = RSA.importKey(public_key)
        return self.encrypt_obj.encrypt(session_key, 0)

    def encrypt_msg(self, msg, session_key):
        """ Зашифровать сообщение"""
        iv = Random.new().read(16)
        obj = AES.new(session_key, AES.MODE_CFB, iv)
        encrypted_msg = iv + obj.encrypt(msg)
        return encrypted_msg

    def decrypt_session_key(self, session_key):
        """ Расшифровать сессионный ключ """
        return self.decryption_obj.decrypt(session_key)

    def decrypt_msg(self, msg, session_key):
        """ Расшифровать сообщение """
        iv = msg[:16]
        obj = AES.new(session_key, AES.MODE_CFB, iv)
        decrypt_msg = obj.decrypt(msg)
        return decrypt_msg[16:]

import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
################################################################
# szyfrowanie i ogolnie kryptografia
################################################################

################################################################
# funkcja hashujaca haslo (SHA-256)
################################################################
def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

################################################################
# Funkcja generująca klucz z hasła użytkownika i pinu
################################################################
def generate_key(answer, pin, salt):
    combined = answer + pin + base64.b64encode(salt).decode('utf-8')
    key = hashlib.sha256(combined.encode()).digest()
    return key

################################################################
# Funkcja szyfrująca hasło serwisu (AES)
################################################################
def encrypt_service_password(service_password, key):
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(service_password.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

################################################################
# Funkcja deszyfrująca hasło serwisu (AES)
################################################################
def decrypt_service_password(enc_service_password, key):
    enc_service_password = base64.b64decode(enc_service_password)
    nonce = enc_service_password[:16]
    tag = enc_service_password[16:32]
    ciphertext = enc_service_password[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    service_password = cipher.decrypt_and_verify(ciphertext, tag)
    return service_password.decode('utf-8')

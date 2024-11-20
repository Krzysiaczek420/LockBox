import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64

################################################################
# Generate encryption key from password (PBKDF2)
################################################################
def generate_encryption_key_from_password(password, salt=None, iterations=100000):
    # Use a random salt if none is provided
    if salt is None:
        salt = get_random_bytes(16)  # Random 16 bytes salt
    # Generate a key of 32 bytes length for AES-256
    return PBKDF2(password, salt, dkLen=32, count=iterations)


################################################################
# Function to encrypt data (AES)
################################################################
def encrypt_data(data, encryption_key):
    if len(encryption_key) not in (16, 24, 32):  # Validate key length
        raise ValueError(f"Invalid AES key length: {len(encryption_key)} bytes")
    
    cipher = AES.new(encryption_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

################################################################
# Function to decrypt data (AES)
################################################################
def decrypt_data(encrypted_data, encryption_key):
    if len(encryption_key) not in (16, 24, 32):  # Validate key length
        raise ValueError(f"Invalid AES key length: {len(encryption_key)} bytes")
    
    data = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

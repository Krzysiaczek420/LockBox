import bcrypt
import pymongo
from Crypto.Random import get_random_bytes
import base64
import Szyfrowanie
################################################################
#       dane bazy danych
################################################################
DATABASE_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "LockBox"
USERS_COLLECTION_NAME = "users"

client = None
users_collection = None
################################################################
# funkcja do laczenia z baza danych
################################################################
def connect_to_database():
    global client, users_collection
    client = pymongo.MongoClient(DATABASE_URL)
    database = client[DATABASE_NAME]
    users_collection = database[USERS_COLLECTION_NAME]
    print("Połączenie z bazą danych zostało otwarte.")


################################################################
# funkcja do zamkniecia polaczenia z baza danych
#################################################################
def close_database_connection():
    if client:
        client.close()
        print("Połączenie z bazą danych zostało zamknięte.")

#################################################################
# dodawanie nowego uzytkownika (rejestracja)
#################################################################
def add_user(username, password, security_question, answer, pin_code):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        return {"success": False, "message": "Username already exists."}
    
    # Hashowanie hasła, odpowiedzi na pytanie i pinu za pomocą bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_pin = bcrypt.hashpw(pin_code.encode('utf-8'), bcrypt.gensalt())
    hashed_answer = bcrypt.hashpw(answer.encode('utf-8'), bcrypt.gensalt())

    # Generowanie losowego klucza i soli
    key = get_random_bytes(32)
    salt = get_random_bytes(16)

    # Tworzenie klucza szyfrowania klucza
    key_encryption_key = Szyfrowanie.generate_key(answer, pin_code, salt)
    encrypted_key = Szyfrowanie.encrypt_service_password(base64.b64encode(key).decode('utf-8'), key_encryption_key)

    user_data = {
        "username": username,
        "password": hashed_password.decode('utf-8'),
        "security_question": security_question,
        "answer": hashed_answer.decode('utf-8'),
        "salt": base64.b64encode(salt).decode('utf-8'),
        "pin_code": hashed_pin.decode('utf-8'),
        "encrypted_key": encrypted_key,
        "systems": []
    }
    users_collection.insert_one(user_data)
    return {"success": True, "message": "User has been added successfully."}


#################################################################
# reset hasla uzytkownika(forget password)
#################################################################
def reset_user_password(username, new_password):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "User does not exist."}

    new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    users_collection.update_one(
        {"username": username},
        {"$set": {
            "password": new_hashed_password.decode('utf-8'),
        }}
    )

    return {"success": True, "message": "Password has been changed succesfully."}

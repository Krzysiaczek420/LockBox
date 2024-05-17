import bcrypt
import pymongo
from Crypto.Random import get_random_bytes
import base64
import Szyfrowanie

DATABASE_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "LockBox"
USERS_COLLECTION_NAME = "users"

client = None
users_collection = None

def connect_to_database():
    global client, users_collection
    client = pymongo.MongoClient(DATABASE_URL)
    database = client[DATABASE_NAME]
    users_collection = database[USERS_COLLECTION_NAME]
    print("Połączenie z bazą danych zostało otwarte.")

def close_database_connection():
    if client:
        client.close()
        print("Połączenie z bazą danych zostało zamknięte.")

def add_user(username, password, security_question, answer, pin_code):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        return {"success": False, "message": "Użytkownik o tej nazwie już istnieje."}
    
    # Haszowanie hasła użytkownika
    hashed_password = Szyfrowanie.hash_password(password)
    
    # Generowanie losowego klucza symetrycznego
    key = get_random_bytes(32)
    salt = get_random_bytes(16)
    
    # Szyfrowanie klucza za pomocą hasła użytkownika i pinu
    key_encryption_key = Szyfrowanie.generate_key_from_password_and_pin(password, pin_code, salt)
    encrypted_key = Szyfrowanie.encrypt_service_password(base64.b64encode(key).decode('utf-8'), key_encryption_key)

    user_data = {
        "username": username,
        "password": hashed_password,
        "security_question": security_question,
        "answer": answer,
        "pin_code": pin_code,
        "salt": base64.b64encode(salt).decode('utf-8'),
        "encrypted_key": encrypted_key,
        "systems": []
    }
    users_collection.insert_one(user_data)
    return {"success": True, "message": "Użytkownik został pomyślnie dodany."}

def change_user_password(username, new_password):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Użytkownik nie istnieje."}

    # Generowanie nowego hasła
    new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Aktualizacja użytkownika w bazie danych
    users_collection.update_one(
        {"username": username},
        {"$set": {
            "password": new_hashed_password.decode('utf-8'),
        }}
    )

    return {"success": True, "message": "Hasło zostało zmienione."}
def reset_user_password(username, new_password, security_answer, pin_code):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Użytkownik nie istnieje."}

    # Weryfikacja odpowiedzi na pytanie bezpieczeństwa
    if user["answer"] != security_answer:
        return {"success": False, "message": "Niepoprawna odpowiedź na pytanie bezpieczeństwa."}

    # Weryfikacja kodu pin
    if user["pin_code"] != pin_code:
        return {"success": False, "message": "Niepoprawny kod pin."}

    # Odszyfrowanie starego klucza szyfrującego
    salt = base64.b64decode(user["salt"])
    old_key_encryption_key = Szyfrowanie.generate_key(user["answer"], pin_code, salt)
    old_encrypted_key = base64.b64decode(user["encrypted_key"])
    old_key = base64.b64decode(Szyfrowanie.decrypt_service_password(old_encrypted_key, old_key_encryption_key))

    # Haszowanie nowego hasła użytkownika
    new_hashed_password = Szyfrowanie.hash_password(new_password)

    # Aktualizacja użytkownika w bazie danych
    users_collection.update_one(
        {"username": username},
        {"$set": {
            "password": new_hashed_password,
            # Nie zmieniamy klucza, pozostawiamy go taki sam
        }}
    )

    return {"success": True, "message": "Hasło zostało zresetowane."}

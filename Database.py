from datetime import datetime
import bcrypt
import pymongo
from Crypto.Random import get_random_bytes
import base64
import Encryption
from bson.binary import Binary

DATABASE_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "LockBox"
USERS_COLLECTION_NAME = "users"

client = None
users_collection = None

# Function to connect to the database
def connect_to_database():
    global client, users_collection
    client = pymongo.MongoClient(DATABASE_URL)
    database = client[DATABASE_NAME]
    users_collection = database[USERS_COLLECTION_NAME]
    print("Połączenie z bazą danych zostało otwarte.")

# Function to close the database connection
def close_database_connection():
    if client:
        client.close()
        print("Połączenie z bazą danych zostało zamknięte.")

# Function to generate encryption key from answer and pin code
# Function to generate encryption key from answer and pin code
def generate_encryption_key(answer, pin_code):
    # Combine answer and pin code to generate a consistent key
    combined_key = f"{answer}{pin_code}".encode('utf-8')
    # Generate a proper length key (32 bytes for AES-256)
    return Encryption.generate_encryption_key_from_password(combined_key, salt=None, iterations=100000)[:32]


# Function to add a new user (registration)
def add_user(username, password, security_question, answer, pin_code):
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        return {"success": False, "message": "Username already exists."}
    
    # Hashing password, pin, and answer using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_pin = bcrypt.hashpw(pin_code.encode('utf-8'), bcrypt.gensalt())
    hashed_answer = bcrypt.hashpw(answer.encode('utf-8'), bcrypt.gensalt())

    # Generating encryption key
    encryption_key = generate_encryption_key(answer, pin_code)

    # Creating user data
    user_data = {
        "username": username,
        "password": hashed_password.decode('utf-8'),
        "security_question": security_question,
        "answer": hashed_answer.decode('utf-8'),
        "pin_code": hashed_pin.decode('utf-8'),
        "encrypted_key": Binary(encryption_key),  # Store the encryption key as Binary type
        "systems": []
    }
    users_collection.insert_one(user_data)
    return {"success": True, "message": "User has been added successfully."}
def get_user_by_username(username):
    # Retrieve user data from the database
    user = users_collection.find_one({"username": username})
    return user

# Function to add a new system for a user
def add_system_for_user(username, system_name, login, password, note):
    user = users_collection.find_one({"username": username})
    
    if not user:
        return {"success": False, "message": "User not found."}

    # Directly retrieve the encryption key from the database without Base64 decoding
    encryption_key = user['encrypted_key']  # Klucz jest teraz w formacie binarnym

    if len(encryption_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. The key should be 16, 24, or 32 bytes long.")

    # Encrypt system data
    encrypted_system_name = Encryption.encrypt_data(system_name, encryption_key)
    encrypted_login = Encryption.encrypt_data(login, encryption_key)
    encrypted_password = Encryption.encrypt_data(password, encryption_key)
    encrypted_note = Encryption.encrypt_data(note, encryption_key)
    creation_date = datetime.now().isoformat()  # Konwersja daty na format tekstowy
    encrypted_creation_date = Encryption.encrypt_data(creation_date, encryption_key)


    # Add the system to the user's data
    system_data = {
        "system_name": encrypted_system_name,
        "login": encrypted_login,
        "password": encrypted_password,
        "note": encrypted_note,
        "creation_date": encrypted_creation_date
    }

    users_collection.update_one(
        {"username": username},
        {"$push": {"systems": system_data}}
    )
    
    return {"success": True, "message": "System added successfully."}

# Function to get user systems (for decryption)
def get_user_systems(username):
    user = users_collection.find_one({"username": username})
    
    if not user:
        return {"success": False, "message": "User not found."}

    # Retrieve the encryption key directly from the database
    encryption_key = user['encrypted_key']  # No need for Base64 decoding

    if len(encryption_key) not in (16, 24, 32):
        raise ValueError("Invalid AES key length. The key should be 16, 24, or 32 bytes long.")
    
    systems_list = []
    for system in user.get('systems', []):
        decrypted_system_name = Encryption.decrypt_data(system["system_name"], encryption_key)
        decrypted_login = Encryption.decrypt_data(system["login"], encryption_key)
        decrypted_password = Encryption.decrypt_data(system["password"], encryption_key)
        decrypted_note = Encryption.decrypt_data(system["note"], encryption_key)

        systems_list.append({
            "system_name": decrypted_system_name,
            "login": decrypted_login,
            "password": decrypted_password,
            "note": decrypted_note
        })

    return {"success": True, "systems": systems_list}

def get_user_systems(username):
    # Pobierz użytkownika z bazy na podstawie username
    user_data = get_user_by_username(username)
    
    if not user_data or 'systems' not in user_data:
        return []
    
    decrypted_systems = []
    
    for system in user_data['systems']:
        decrypted_systems.append({
            "system_name": Encryption.decrypt_data(system["system_name"], user_data['encrypted_key']),  # Odszyfrowanie nazwy systemu
            "login": Encryption.decrypt_data(system["login"], user_data['encrypted_key']),  # Odszyfrowanie loginu
            "password": Encryption.decrypt_data(system["password"], user_data['encrypted_key']),  # Odszyfrowanie hasła
            "note": Encryption.decrypt_data(system["note"], user_data['encrypted_key']),
            "creation_date": Encryption.decrypt_data(system["creation_date"], user_data['encrypted_key'])
        })
    
    return decrypted_systems
# Function to delete a specific system for a user
def delete_user_system(username, system_name):
    # Pobierz użytkownika z bazy
    user = users_collection.find_one({"username": username})

    if not user:
        return {"success": False, "message": "User not found."}

    encryption_key = user['encrypted_key']

    # Przechodzimy przez systemy użytkownika, aby znaleźć dopasowanie
    for system in user['systems']:
        decrypted_system_name = Encryption.decrypt_data(system["system_name"], encryption_key)
        
        # Sprawdź, czy odszyfrowana nazwa systemu pasuje do podanej
        if decrypted_system_name == system_name:
            # Usuń system z listy
            result = users_collection.update_one(
                {"username": username},
                {"$pull": {"systems": {"system_name": system["system_name"]}}}
            )
            if result.modified_count > 0:
                return {"success": True, "message": "System deleted successfully."}
            else:
                return {"success": False, "message": "Error deleting system."}
    
    return {"success": False, "message": "System not found."}

def check_existing_system(username, system_name, login):
    # Pobierz użytkownika na podstawie nazwy użytkownika
    user = users_collection.find_one({"username": username})

    if not user:
        return False  # Jeśli użytkownik nie istnieje, zwracamy False
    
    # Przechodzimy przez zaszyfrowane systemy użytkownika, aby sprawdzić zgodność
    for system in user.get('systems', []):
        decrypted_system_name = Encryption.decrypt_data(system["system_name"], user['encrypted_key'])
        decrypted_login = Encryption.decrypt_data(system["login"], user['encrypted_key'])

        if decrypted_system_name == system_name and decrypted_login == login:
            return True  # Znaleziono dopasowanie

    return False
def update_user_system(username, original_system_name, new_system_name, new_login, new_password, new_note):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "User not found."}

    encryption_key = user['encrypted_key']
    
    # Przejdź przez systemy użytkownika, aby znaleźć dopasowanie
    for system in user['systems']:
        decrypted_system_name = Encryption.decrypt_data(system["system_name"], encryption_key)
        if decrypted_system_name == original_system_name:
            # Przygotuj zaktualizowane dane
            encrypted_new_system_name = Encryption.encrypt_data(new_system_name, encryption_key)
            encrypted_new_login = Encryption.encrypt_data(new_login, encryption_key)
            encrypted_new_password = Encryption.encrypt_data(new_password, encryption_key)
            encrypted_new_note = Encryption.encrypt_data(new_note, encryption_key)
            
            # Aktualizuj istniejący dokument w MongoDB
            result = users_collection.update_one(
                {"username": username, "systems.system_name": system["system_name"]},
                {
                    "$set": {
                        "systems.$.system_name": encrypted_new_system_name,
                        "systems.$.login": encrypted_new_login,
                        "systems.$.password": encrypted_new_password,
                        "systems.$.note": encrypted_new_note
                    }
                }
            )
            if result.modified_count > 0:
                return {"success": True, "message": "System updated successfully."}
            else:
                return {"success": False, "message": "No changes made to the system."}
    
    return {"success": False, "message": "System not found."}

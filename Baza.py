import pymongo

# Adres URL bazy danych MongoDB
DATABASE_URL = "mongodb://localhost:27017/"

# Nazwa bazy danych
DATABASE_NAME = "LockBox"

# Nazwa kolekcji dla użytkowników
USERS_COLLECTION_NAME = "users"

# Globalne zmienne przechowujące obiekty klienta i kolekcję
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
    # Sprawdzenie, czy użytkownik o podanej nazwie już istnieje
    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        print("uzytkownik o tej nazwie już istnieje") 
        return {"success": False, "message": "Użytkownik o tej nazwie już istnieje."}
    
    # Jeśli użytkownik nie istnieje, dodajemy go do bazy danych
    user_data = {
        "username": username,
        "password": password,
        "security_question": security_question,
        "answer": answer,
        "pin_code": pin_code,
        "systems": []
    }
    users_collection.insert_one(user_data)
    return {"success": True, "message": "Użytkownik został pomyślnie dodany."}

def add_system_to_user(username, service_name, service_password, note):
    # Sprawdzenie, czy użytkownik już ma system o podanej nazwie
    existing_system = users_collection.find_one({"username": username, "systems.service_name": service_name})
    if existing_system:
        return {"success": False, "message": "Użytkownik już ma system o tej nazwie."}
    
    # Jeśli użytkownik nie ma jeszcze systemu o podanej nazwie, dodajemy nowy system
    users_collection.update_one(
        {"username": username},
        {"$push": {
            "systems": {
                "service_name": service_name,
                "service_password": service_password,
                "note": note
            }
        }}
    )
    return {"success": True, "message": "System został pomyślnie dodany do użytkownika."}

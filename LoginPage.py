import threading
import bcrypt
import customtkinter as ctk
import tkinter as tk
import Register_Page
import Database as db
import json
import Pin_Window as pin
import Main_Window as main
import Forget_Password_Window as forgetPW
from Settings import set_theme_and_color, load_setting, load_translation

#########################################################
# główne okno strony logowania
#########################################################
window = ctk.CTk()
window.geometry("700x500")
window.title("LockBox - Login")
window.resizable(False, False)
file_path = 'settings.json'
dialog_active = False
current_thread = None

#########################################################
# funkcja do ustawiania motywu i koloru w zaleznosci od danych z settings.json
#########################################################
theme, color = set_theme_and_color(file_path)
ctk.set_appearance_mode(theme)
ctk.set_default_color_theme(color)

#########################################################
# wczytanie ustawień i tłumaczeń
#########################################################
setting = load_setting(file_path)
language = setting.get('language', 'en')
translation = load_translation(language, 'LoginPage')
current_error = None

#########################################################
# ustawianie focusu na główne okno (anulowanie wpisywania)
#########################################################
def cancel_focus(event=None):
    if event:
        widget = window.winfo_containing(event.x_root, event.y_root)
        if widget == window:
            window.focus_set()
    else:
        window.focus_set()

#########################################################
# funkcja odpowiedzialna za pokazywanie hasła po zaznaczeniu checkboxa
#########################################################
def show_password():
    if show_password_var.get() == 1:
        password_input.configure(show="")
    else:
        password_input.configure(show="*")

#########################################################
# funkcja odpowiedzialna za zmienianie widoku logowania na widok rejestracji
#########################################################
def new_user_pressed():
    hide_login_page()
    show_register_page()

#########################################################
# funkcja odpowiedzialna za zmienianie widoku logowania na widok odyzskiwania hasła
#########################################################
def forget_password_pressed():
    hide_login_page()
    show_forget_page()

#########################################################
# funkcja zmieniajaca jezyk w przypadku wybrania innego jezyka z comboboxa
#########################################################
def change_language(event):
    global translation
    selected_language = language_mapping[language.get()]
    translation = load_translation(selected_language, 'LoginPage')
    update_translations()
    setting['language'] = selected_language
    with open(file_path, 'w') as setting_file:
        json.dump(setting, setting_file)
    language.set(language_mapping_inv[selected_language])

#########################################################
# blizniaczo podobne funkcje 
# disable_close_button - "anuluje" działanie przycisku zamknij, 
#   uzywane gdy wyswietla sie okno dialogowe z potwierdzeniem zamknciecia
# enable_close_button - przywraca dzialanie przycisku zamknij, 
#   uzywana po nacisnieciu guzika anulujacego zamykanie w wyzej wspomnianym oknie dialogowym
#########################################################
def disable_close_button():
    window.protocol("WM_DELETE_WINDOW", lambda: None)

def enable_close_button():
    window.protocol("WM_DELETE_WINDOW", close_window)

#########################################################
# działanie po nacisnieciu guzika zamknij
# definicja okna dialogowego z potwierdzeniem zamkniecia
# funkcje do zamykania wszystkich okien bądz anulowania w zaleznosci od wybranego guzika
#########################################################
def close_window():
    global dialog_active

    if window.state() == 'iconic': 
        window.deiconify()

    dialog_frame = ctk.CTkFrame(window, border_width=2, width=200, height=100,)
    dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
    dialog_frame.grab_set()
    dialog_active = True
    disable_close_button()
    dialog_frame.custom_name = "dialog_frame"

    def confirm_close():
        global dialog_active
        if window is not None and window.winfo_exists():
            db.close_database_connection()
            window.destroy()
        dialog_active = False

    def cancel_close():
        global dialog_active
        dialog_frame.destroy()
        dialog_active = False
        window.grab_set()
        enable_close_button()

    yes_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=translation["yes"], command=confirm_close)
    no_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=translation["no"], command=cancel_close)
    close_label = ctk.CTkLabel(dialog_frame, width=196, text=translation["close"], anchor="center")

    close_label.place(x=2, y=15)
    yes_button.place(x=25, y=60)
    no_button.place(x=125, y=60)

#########################################################
# aktualizowanie jezyka (zmiana tekstów w widgetach po zmianie jezyka)
#########################################################
def update_translations():
    login_label.configure(text=translation["login_label"])
    login_input.configure(placeholder_text=translation["username_placeholder"])
    password_input.configure(placeholder_text=translation["password_placeholder"])
    show_password_cb.configure(text=translation["show_password"])
    login_button.configure(text=translation["log_in_button"])
    new_user_button.configure(text=translation["new_account_button"])
    new_account_label.configure(text=translation["new_user_label"])
    forget_password.configure(text=translation["forget_password_button"])
    language_label.configure(text=translation["language_label"])

    if current_error == "incorrect_password":
        error_Label.configure(text=translation["incorrect_password"])
    elif current_error == "no_user":
        error_Label.configure(text=translation["no_user"])
    else:
        error_Label.configure(text="")
    window.focus_set()

#########################################################
# funkcja sprawdzajaca czy pola tekstowe maja jakąkolwiek zawartość, jesli są puste guzik logowania jest nieaktywny
#########################################################
def check_if_empty(event=None):
    if (login_input.get() == "" or password_input.get() == ""):
        login_button.configure(state="disabled")
    else:
        login_button.configure(state="normal")

#########################################################
# funkcja odpowiedzialna za logowanie
# sprawdza czy nazwa uzytkownika wpisana wystepuje w bazie, 
# jesli tak porownuje hash hasła wpisanego z hashem hasła zawaretgo w bazie dla tego uzytkownika  
#########################################################
def login():
    global current_error
    username_in = login_input.get()
    password_in = password_input.get()

    username_db = db.users_collection.find_one({"username": username_in})

    if username_db:
        stored_password = username_db.get("password", "")
        if bcrypt.checkpw(password_in.encode('utf-8'), stored_password.encode('utf-8')):
            hide_login_page()
            password_input.delete(0, tk.END)
            password_input.configure(placeholder_text=translation["password_placeholder"])
            error_Label.configure(text="")
            show_main_page(username_in, show_login_page)
        else:
            current_error = 1
            error_Label.configure(text=translation["incorrect_password"])
    else:
        current_error = 2
        error_Label.configure(text=translation["no_user"])

#########################################################
# uruchamianie aplikacji
# stworzenie okna aplikacji, łączenie z bazą danych
#########################################################
def run_LoginPage():
    db.connect_to_database()
    window.protocol("WM_DELETE_WINDOW", close_window)
    window.bind("<Button-1>", cancel_focus)
    window.mainloop()

#########################################################
# Funkcja do wyświetlania strony logowania
#########################################################
def show_login_page():
    password_input.delete(0, tk.END)
    password_input.configure(placeholder_text=translation["password_placeholder"], show="*")
    login_label.place(x=275, y=165)
    login_input.place(x=275, y=200)
    password_input.place(x=275, y=250)
    show_password_cb.place(x=275, y=300)
    error_Label.place(x=0, y=400)
    login_button.place(x=375, y=350)
    forget_password.place(x=255, y=350)
    new_account_label.place(x=15, y=465)
    new_user_button.place(x=220, y=460)
    language.place(x=590, y=460)
    language_label.place(x=490, y=465)
    login_button.configure(state="disabled")
    show_password_cb.deselect()

#########################################################
# funkcja do ukrywania strony logowania
#########################################################
def hide_login_page():
    login_label.place_forget()
    login_input.place_forget()
    password_input.place_forget()
    show_password_cb.place_forget()
    error_Label.place_forget()
    login_button.place_forget()
    forget_password.place_forget()
    new_account_label.place_forget()
    new_user_button.place_forget()
    language.place_forget()
    language_label.place_forget()

#########################################################
# trzy blizniaczo podobne funkcje
# show_register_page - wyswietla widok rejestracji
# show_main_page - wyswietla glowny widok aplikacji
# show_forget_page - wyswietla widok resetu hasła
#########################################################
def show_register_page():
    Register_Page.show_register_page(window, show_login_page)


def show_main_page(username_in, show_login_page):
    global current_thread

    # Jeśli istnieje poprzedni wątek, czekamy na jego zakończenie
    if current_thread and current_thread.is_alive():
        current_thread.join()

    # Tworzymy nowy wątek dla funkcji ładowania
    current_thread = threading.Thread(target=load_and_show_main_window, args=(username_in, show_login_page))
    current_thread.start()

# Funkcja, która ładuje dane w tle i uruchamia główny widok
def load_and_show_main_window(username_in, show_login_page):
    def load_user_data():
        # Pobieramy szczegóły użytkownika z bazy
        user_details = db.users_collection.find_one({"username": username_in})
        return user_details

    # Pobieramy dane
    user_details = load_user_data()

    # Przekazujemy dane do głównego wątku, aby zaktualizować interfejs
    window.after(0, lambda: display_main_window(username_in, show_login_page, user_details))

# Funkcja, która usuwa ekran ładowania i wyświetla główny widok aplikacji
def display_main_window(username_in, show_login_page, user_details):
    global current_thread

    # Wyświetlamy główne okno i resetujemy wątek
    main.MainWindow(window, show_login_page, username_in)
    current_thread = None
def show_forget_page():
    forgetPW.select_username(window, show_login_page)

#########################################################
# Definiowanie widgetów okna logowania
#########################################################
login_input = ctk.CTkEntry(window, 
    width=150, 
    height=30, 
    placeholder_text=translation["username_placeholder"])

password_input = ctk.CTkEntry(window, 
    width=150, 
    height=30, 
    placeholder_text=translation["password_placeholder"], 
    show ="*")

show_password_var = tk.IntVar()
show_password_cb = ctk.CTkCheckBox(window, 
    text=translation["show_password"], 
    width=150, 
    height=30,
    checkbox_width=20,
    checkbox_height=20,
    border_width=2,
    variable=show_password_var, 
    command=show_password)

login_button = ctk.CTkButton(window, 
    text=translation["log_in_button"], 
    width=60, 
    height=30,
    command=login,
    state="disabled")

new_user_button = ctk.CTkButton(window, 
    text=translation["new_account_button"], 
    width=60, 
    height=30, 
    command=new_user_pressed)

new_account_label = ctk.CTkLabel(window, 
    text=translation["new_user_label"], 
    width=180, 
    height=20,
    anchor="e")

login_label = ctk.CTkLabel(window, 
    text=translation["login_label"], 
    width=140, 
    height=20)

error_Label = ctk.CTkLabel(window, 
    text="", 
    width=700, 
    height=20,
    text_color="red")

forget_password = ctk.CTkButton(window, 
    text=translation["forget_password_button"], 
    width=60, 
    height=30,
    command=forget_password_pressed)

language_label = ctk.CTkLabel(window, 
    text = translation["language_label"], 
    width=100, 
    height=20)

language_mapping = {"Polish": "pl", "English": "en"}
language_mapping_inv = {v: k for k, v in language_mapping.items()}

language = ctk.CTkComboBox(window, 
    values=list(language_mapping.keys()),
    width= 90,
    height=30,
    state="readonly",
    command=change_language)

language.set(language_mapping_inv[setting['language']])
language.bind("<<ComboboxSelected>>", change_language)
login_input.bind("<KeyRelease>", check_if_empty)
password_input.bind("<KeyRelease>", check_if_empty)

show_login_page()


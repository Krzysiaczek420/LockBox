
import bcrypt
import customtkinter as ctk
import tkinter as tk
import RegisterPage
import Baza as baza
import json
import PinWindow as pin
import MainWindow as main
import ForgetPasswordWindow as forgetPW
from Settings import ustaw_motyw_i_kolor, wczytaj_ustawienia, wczytaj_tlumaczenie_modulu

#########################################################
# główne okno strony logowania
#########################################################
window = ctk.CTk()
window.geometry("700x500")
window.title("LockBox - Login")
window.resizable(False, False)
sciezka_do_pliku = 'settings.json'

#########################################################
# funkcja do ustawiania motywu i koloru w zaleznosci od danych z settings.json
#########################################################
motyw, kolor = ustaw_motyw_i_kolor(sciezka_do_pliku)
ctk.set_appearance_mode(motyw)
ctk.set_default_color_theme(kolor)

# wczytanie ustawień i tłumaczeń
ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
jezyk = ustawienia.get('language', 'en')
tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'LoginPage')
current_error = None

def cancel_focus(event=None):
    if event:
        widget = window.winfo_containing(event.x_root, event.y_root)
        if widget == window:
            window.focus_set()
    else:
        window.focus_set()

def show_password():
    if show_password_var.get() == 1:
        password_input.configure(show="")
    else:
        password_input.configure(show="*")

def NewUserButtonPressing():
    hide_login_page()
    show_register_page()  # Zamiast otwierać nowe okno, przechodzimy do strony rejestracji

def change_language(event):
    global tlumaczenie
    jezyk = language_mapping[language.get()]
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'LoginPage')
    update_translations()
    ustawienia['language'] = jezyk
    with open(sciezka_do_pliku, 'w') as plik:
        json.dump(ustawienia, plik)
    language.set(language_mapping_inv[jezyk])

def close_window():
    dialog_frame = ctk.CTkFrame(window, width=200, height=100)
    dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
    dialog_frame.grab_set()

    close_label = ctk.CTkLabel(dialog_frame, width=200, text=tlumaczenie["close"],anchor="center")
    close_label.place(x=0, y=15)

    # Funkcja do zamknięcia aplikacji
    def confirm_close():
        if window is not None and window.winfo_exists():
            baza.close_database_connection()  # zamknięcie połączenia z bazą danych
            #overlay.destroy()  # Usunięcie półprzezroczystego `Frame`
            window.destroy()  # zamknięcie głównego okna

    # Funkcja do anulowania zamknięcia
    def cancel_close():
        dialog_frame.destroy()
        window.grab_set()
        window.protocol("WM_DELETE_WINDOW", close_window)  # Usunięcie półprzezroczystego `Frame`

    # Przyciski "Tak" i "Nie"
    yes_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=tlumaczenie["yes"], command=confirm_close)
    no_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=tlumaczenie["no"], command=cancel_close)

    yes_button.place(x=25, y=60)
    no_button.place(x=125, y=60)

    # Zapewnij, że przy zamknięciu głównego okna, półprzezroczysty `Frame` zostanie usunięty
    window.protocol("WM_DELETE_WINDOW", cancel_close)

def update_translations():
    loginLabel.configure(text=tlumaczenie["login_label"])
    login_input.configure(placeholder_text=tlumaczenie["username_placeholder"])
    password_input.configure(placeholder_text=tlumaczenie["password_placeholder"])
    show_password_cb.configure(text=tlumaczenie["show_password"])
    login_button.configure(text=tlumaczenie["log_in_button"])
    newUserButton.configure(text=tlumaczenie["new_account_button"])
    newAccountLabel.configure(text=tlumaczenie["new_user_label"])
    forgetPassword.configure(text=tlumaczenie["forget_password_button"])
    languageLabel.configure(text=tlumaczenie["language_label"])

    if current_error == "incorrect_password":
        error_Label.configure(text=tlumaczenie["incorrect_password"])
    elif current_error == "no_user":
        error_Label.configure(text=tlumaczenie["no_user"])
    else:
        error_Label.configure(text="")

def forget_password_pressed():
    hide_login_page()
    show_forget_page()

def check_if_empty(event=None):
    if (login_input.get() == "" or password_input.get() == ""):
        login_button.configure(state="disabled")
    else:
        login_button.configure(state="normal")

def check_user_in_database(username):
    user = baza.users_collection.find_one({"username": username})
    return user is not None

def login():
    global current_error
    username_in = login_input.get()
    password_in = password_input.get()
    username_db = baza.users_collection.find_one({"username": username_in})

    if check_user_in_database(username_in):
        stored_password = username_db.get("password", "")
        if bcrypt.checkpw(password_in.encode('utf-8'), stored_password.encode('utf-8')):
            hide_login_page()
            password_input.delete(0, tk.END)
            password_input.configure(placeholder_text=tlumaczenie["password_placeholder"])
            error_Label.configure(text="")
            show_main_page(username_in,show_login_page)
        else:
            current_error = 1
            error_Label.configure(text=tlumaczenie["incorrect_password"])
    else:
        current_error = 2
        error_Label.configure(text=tlumaczenie["no_user"])

def run_LoginPage():
    baza.connect_to_database()
    window.protocol("WM_DELETE_WINDOW", close_window)
    window.bind("<Button-1>", cancel_focus)
    window.mainloop()

# Funkcja do wyświetlania strony logowania
def show_login_page():
    loginLabel.place(x=275, y=165)
    login_input.place(x=275, y=200)
    password_input.place(x=275, y=250)
    show_password_cb.place(x=275, y=300)
    error_Label.place(x=0, y=400)
    login_button.place(x=375, y=350)
    forgetPassword.place(x=255, y=350)
    newAccountLabel.place(x=15, y=465)
    newUserButton.place(x=220, y=460)
    language.place(x=590, y=460)
    languageLabel.place(x=490, y=465)

def hide_login_page():
    loginLabel.place_forget()
    login_input.place_forget()
    password_input.place_forget()
    show_password_cb.place_forget()
    error_Label.place_forget()
    login_button.place_forget()
    forgetPassword.place_forget()
    newAccountLabel.place_forget()
    newUserButton.place_forget()
    language.place_forget()
    languageLabel.place_forget()

# Funkcja do wyświetlania strony rejestracji
def show_register_page():
    RegisterPage.show_register_page(window, show_login_page)

def show_main_page(username_in,show_login_page):
    main.MainWindow(window, show_login_page, username_in)
def show_forget_page():
    forgetPW.select_username(window, show_login_page)

# Definiowanie widgetów okna logowania
login_input = ctk.CTkEntry(window, 
    width=150, 
    height=30, 
    placeholder_text=tlumaczenie["username_placeholder"])

password_input = ctk.CTkEntry(window, 
    width=150, 
    height=30, 
    placeholder_text=tlumaczenie["password_placeholder"], 
    show ="*")

show_password_var = tk.IntVar()
show_password_cb = ctk.CTkCheckBox(window, 
    text=tlumaczenie["show_password"], 
    width=150, 
    height=30,
    variable=show_password_var, 
    command=show_password)

login_button = ctk.CTkButton(window, 
    text=tlumaczenie["log_in_button"], 
    width=60, 
    height=30,
    command=login, #ZMIENIONE NA POTRZEBY TESTOW
    state="disabled")

newUserButton = ctk.CTkButton(window, 
    text=tlumaczenie["new_account_button"], 
    width=60, 
    height=30, 
    command=NewUserButtonPressing)

newAccountLabel = ctk.CTkLabel(window, 
    text=tlumaczenie["new_user_label"], 
    width=180, 
    height=20,
    anchor="e")

loginLabel = ctk.CTkLabel(window, 
    text=tlumaczenie["login_label"], 
    width=140, 
    height=20)

error_Label = ctk.CTkLabel(window, 
    text="", 
    width=700, 
    height=20,
    text_color="red")

forgetPassword = ctk.CTkButton(window, 
    text=tlumaczenie["forget_password_button"], 
    width=60, 
    height=30,
    command=forget_password_pressed)

languageLabel = ctk.CTkLabel(window, 
    text = tlumaczenie["language_label"], 
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

language.set(language_mapping_inv[jezyk])
language.bind("<<ComboboxSelected>>", change_language)
login_input.bind("<KeyRelease>", check_if_empty)
password_input.bind("<KeyRelease>", check_if_empty)

# Umieszczamy elementy na ekranie logowania
show_login_page()

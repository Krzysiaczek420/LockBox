import asyncio
import customtkinter as ctk
import tkinter as tk
import RegisterPage
import Baza as baza
import json
import PinWindow as pin
import MainWindow as main
import ForgetPasswordWindow as forgetPW
import Szyfrowanie
from Settings import ustaw_motyw_i_kolor, wczytaj_ustawienia, wczytaj_tlumaczenie_modulu
#################################################################
# główne okno strony logowania
#################################################################

################################################################
# definicja głównego okna logowania
################################################################
login_window = ctk.CTk()
login_window.geometry("700x500")
login_window.title("LockBox-Log in")
login_window.resizable(False,False)
sciezka_do_pliku = 'settings.json'


################################################################
# funkcja do ustawiania motywu i koloru w zaleznosci od danych z settings.json
################################################################
motyw, kolor = ustaw_motyw_i_kolor(sciezka_do_pliku)
ctk.set_appearance_mode(motyw)
ctk.set_default_color_theme(kolor)

################################################################
# wczytanie ustawień i tłumaczeń
################################################################
ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
jezyk = ustawienia.get('language', 'en')
tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'LoginPage')
current_error = None

################################################################
# funkcja do anulowania focusa na oknie logowania w przypadku kilkniecia poza widgety
################################################################
def cancel_focus(event=None):
    if event:
        widget = login_window.winfo_containing(event.x_root, event.y_root)
        if widget == login_window:
            login_window.focus_set()
    else:
        login_window.focus_set()

################################################################
#funkcja odpowiedzialana za dzialanie checkboxu "Show Password"
################################################################
def show_password():
    if show_password_var.get() == 1:  # If checkbox is checked
        password_input.configure(show="")
    else:  # If checkbox is not checked
        password_input.configure(show="*")

################################################################
# funkcja odpowiedzialna za przycisk "NewUser"
# zamykanie okna logowania i otwarcie okna rejestracji
################################################################
def NewUserButtonPressing():
    login_window.withdraw()
    RegisterPage.open_register_window(login_window)

################################################################
# funkcje odpowiedzialne za dzialanie comboboxa do zmiany jezyka
################################################################
def change_language(event):
    global tlumaczenie
    jezyk = language_mapping[language.get()]
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'LoginPage')
    update_translations()
    
    # Zapisz wybrany język do pliku settings.json
    ustawienia['language'] = jezyk
    with open(sciezka_do_pliku, 'w') as plik:
        json.dump(ustawienia, plik)
    language.set(language_mapping_inv[jezyk])

################################################################
# funkcja do zmieniania jezyka w aplikacji po wybraniu innego jezyka z comboboxa
################################################################
def update_translations():
    loginLabel.configure(text=tlumaczenie["login_label"])
    login_input.configure(placeholder_text = tlumaczenie["username_placeholder"])
    password_input.configure(placeholder_text = tlumaczenie["password_placeholder"])
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
################################################################
# funkcja odpowiedzialna za przycisk "ForgetPassword"
# zamykanie okna logowania i otwarcie okna resetowania hasla
################################################################
def forget_password_pressed():
    login_window.withdraw()
    forgetPW.select_username(login_window, run_LoginPage)

################################################################
# funkcja do sprawdzania czy textboxy nie sa puste
################################################################
def check_if_empty(event=None):
    if (login_input.get() == "" or password_input.get() == ""):
        login_button.configure(state="disabled")
    else:
        login_button.configure(state="normal")

################################################################
# dzialania po zamknieciu okna logowania
################################################################
def on_closing():
    if login_window:
        try:
            baza.close_database_connection()
            login_window.after(100, login_window.destroy)
        except tk.TclError:
            pass

################################################################
# funkcja do logowania
################################################################

def check_user_in_database(username):
    user = baza.users_collection.find_one({"username": username})

    return user is not None
def login():
    global current_error
    username_in = login_input.get()
    password_in = Szyfrowanie.hash_password(password_input.get())
    username_db = baza.users_collection.find_one({"username": username_in})
    # username_db = baza.users_collection.find_one({"username": username_in})
    # password_db = username_db.get("password", "")

    #if username_db:
    if check_user_in_database(username_in):
        if password_in == username_db.get("password", ""):
            login_window.withdraw()
            password_input.delete(0, tk.END)
            password_input.configure(placeholder_text = tlumaczenie["password_placeholder"])
            error_Label.configure(text="")
            if show_password_var.get() == 1:
                show_password_cb.toggle()
            asyncio.run(main.MainWindow(login_window, username_in))
            
        else:
            current_error = "incorrect_password"
            error_Label.configure(text=tlumaczenie["incorrect_password"])
    else:
        current_error = "no_user"
        error_Label.configure(text=tlumaczenie["no_user"])

################################################################
# dzialania po uruchomieniu okna logowania
################################################################
def run_LoginPage():
    baza.connect_to_database()
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.bind("<Button-1>", cancel_focus)
    login_window.mainloop()

################################################################
# definiowanie widgetow okna logowania
################################################################
login_input = ctk.CTkEntry(login_window, 
    width=150, 
    height=30, 
    placeholder_text=tlumaczenie["username_placeholder"])

password_input = ctk.CTkEntry(login_window, 
    width=150, 
    height=30, 
    placeholder_text=tlumaczenie["password_placeholder"], 
    show ="*")

show_password_var = tk.IntVar()
show_password_cb = ctk.CTkCheckBox(login_window, 
    text=tlumaczenie["show_password"], 
    width=150, 
    height=30,
    variable=show_password_var, 
    command=show_password)

login_button = ctk.CTkButton(login_window, 
    text=tlumaczenie["log_in_button"], 
    width=60, 
    height=30,
    command=login,
    state="disabled")

newUserButton = ctk.CTkButton(login_window, 
    text=tlumaczenie["new_account_button"], 
    width=60, 
    height=30, 
    command=NewUserButtonPressing)

newAccountLabel = ctk.CTkLabel(login_window, 
    text=tlumaczenie["new_user_label"], 
    width=180, 
    height=20,
    anchor="e")

loginLabel = ctk.CTkLabel(login_window, 
    text=tlumaczenie["login_label"], 
    width=140, 
    height=20)

error_Label = ctk.CTkLabel(login_window, 
    text="", 
    width=700, 
    height=20,
    text_color="red")

forgetPassword = ctk.CTkButton(login_window, 
    text=tlumaczenie["forget_password_button"], 
    width=60, 
    height=30,
    command=forget_password_pressed)

languageLabel = ctk.CTkLabel(login_window, 
    text = tlumaczenie["language_label"], 
    width=100, 
    height=20)

language_mapping = {"Polish": "pl", "English": "en"}
language_mapping_inv = {v: k for k, v in language_mapping.items()}

language = ctk.CTkComboBox(login_window, 
    values=list(language_mapping.keys()),
    width= 90,
    height=30,
    state="readonly",
    command=change_language)

language.set(language_mapping_inv[jezyk])
language.bind("<<ComboboxSelected>>", change_language)
login_input.bind("<KeyRelease>", check_if_empty)
password_input.bind("<KeyRelease>", check_if_empty)

loginLabel.place(x=265, y=165)
login_input.place(x=265, y=200)
password_input.place(x=265, y=250)
show_password_cb.place(x=265, y=300)
error_Label.place(x=0, y=400)
login_button.place(x=365, y=350)
forgetPassword.place(x=245, y=350)
newAccountLabel.place(x=15, y=465)
newUserButton.place(x=220, y=460)
language.place(x=590, y=460)
languageLabel.place(x=490, y=465)

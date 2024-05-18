import customtkinter as ctk
import tkinter as tk
import RegisterPage
import Baza as baza
import PinWindow as pin
import ForgetPasswordWindow as forgetPW
from Motyw import ustaw_motyw_i_kolor
#################################################################
# główne okno strony logowania
#################################################################

################################################################
# definicja głównego okna logowania
################################################################
login_window = ctk.CTk()
login_window.geometry("700x500")
login_window.title("LockBox")
login_window.resizable(False,False)
sciezka_do_pliku = 'settings.json'

################################################################
# funkcja do ustawiania motywu i koloru w zaleznosci od danych z settings.json
################################################################
motyw, kolor = ustaw_motyw_i_kolor(sciezka_do_pliku)
ctk.set_appearance_mode(motyw)
ctk.set_default_color_theme(kolor)

################################################################
# funkcja do anulowania focusa na oknie logowania w przypadku kilkniecia poza widgety
################################################################
def cancel_focus(event):
    widget = login_window.winfo_containing(event.x_root, event.y_root)
    if widget == login_window:
        login_window.focus_set()

################################################################
#funkcja odpowiedzialana za dzialanie checkboxu "Show Password"
################################################################
def show_password():
    if password_input.cget("show") == "*":
        password_input.configure(show="")
    else:
        password_input.configure(show="*")

################################################################
# funkcja odpowiedzialna za przycisk "NewUser"
# zamykanie okna logowania i otwarcie okna rejestracji
################################################################
def NewUserButtonPressing():
    login_window.withdraw()
    RegisterPage.open_register_window(login_window)

################################################################
# funkcja odpowiedzialna za przycisk "ForgetPassword"
# zamykanie okna logowania i otwarcie okna resetowania hasla
################################################################
def forget_password_pressed():
    login_window.withdraw()
    forgetPW.select_username(login_window, run_LoginPage)

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
# dzialania po uruchomieniu okna logowania
################################################################
def run_LoginPage():
    baza.connect_to_database()
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.mainloop()

################################################################
# definiowanie widgetow okna logowania
################################################################
login_input = ctk.CTkEntry(login_window, 
    width=150, 
    height=30, 
    placeholder_text="Username")

password_input = ctk.CTkEntry(login_window, 
    width=150, 
    height=30, 
    placeholder_text="Password", 
    show ="*")

show_password_cb = ctk.CTkCheckBox(login_window, 
    text="Show password", 
    width=150, 
    height=30, 
    command=show_password)

login_button = ctk.CTkButton(login_window, 
    text="Log in", 
    width=60, 
    height=30)

newUserButton = ctk.CTkButton(login_window, 
    text="New account", 
    width=60, 
    height=30, 
    command=NewUserButtonPressing)

newAccountLabel = ctk.CTkLabel(login_window, 
    text="New user? Create account", 
    width=140, 
    height=20)

loginLabel = ctk.CTkLabel(login_window, 
    text="Login", 
    width=140, 
    height=20)

forgetPassword = ctk.CTkButton(login_window, 
    text="Forget password", 
    width=60, 
    height=30,
    command=forget_password_pressed)

loginLabel.place(x=265, y=165)
login_input.place(x=265, y=200)
password_input.place(x=265, y=250)
show_password_cb.place(x=265, y=300)
login_button.place(x=365, y=350)
forgetPassword.place(x=245, y=350)
newAccountLabel.place(x=15, y=465)
newUserButton.place(x=180, y=460)

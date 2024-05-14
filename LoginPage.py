import customtkinter as ctk
import tkinter as tk
import RegisterPage
import Baza as baza
import pin_window as pin
#=========================================================================
#           główne okno strony logowania
#=========================================================================
login_window = ctk.CTk()
login_window.geometry("700x500")
login_window.title("LockBox")
login_window.resizable(False,False)
#fajnie byloby miec jakis patern w tle

#=========================================================================
    # Funkcje
#=========================================================================
    #funkcja do anulowania focusu w momencie nacisniecia gdzies indziej niz textbox
def cancel_focus(event):
    widget = login_window.winfo_containing(event.x_root, event.y_root)
    if widget == login_window:
        login_window.focus_set()
        #if security_question_combobox.get() == "":
#pokazywanie hasla po kliknieciu checkboxa
def show_password():
    if password_input.cget("show") =="*":
        password_input.configure(show="")
    else:
        password_input.configure(show="*")

#uruchomienie okna rejestracji
def NewUserButtonPressing():
    login_window.withdraw()
    RegisterPage.open_register_window(login_window)
    try:
        login_window.deiconify()
    except tk.TclError:
        pass
    pin.pin_window(login_window)

login_window.bind("<Button-1>", cancel_focus)

#=========================================================================
    # Widgety
#=========================================================================
    #wpisywanie loginu
login_input = ctk.CTkEntry(login_window,
    width=150,
    height=30,
    placeholder_text="login")

    #wpisywanie hasła
password_input = ctk.CTkEntry(login_window,
    width=150,
    height=30,
    placeholder_text="password",
    show ="*")

    #przycisk pokazujacy haslo
show_password = ctk.CTkCheckBox(login_window,
    text = "show password",
    width=150,
    height=30,
    command=show_password)

    #przycisk logowania
login_button = ctk.CTkButton(
    login_window,
    text = "Log in",
    width=60,
    height=30)
     
    #przycisk rejestracji
newUserButton = ctk.CTkButton(
    login_window,
    text = "New account",
    width=60,
    height=30,
    command=NewUserButtonPressing)

newAccountLabel = ctk.CTkLabel(
    login_window,
    text = "New user? Create account",
    width = 140,
    height= 20)

loginLabel = ctk.CTkLabel(
    login_window,
    text = "logowanie",
    width = 140,
    height= 20)

    #przycisk zapomniałeś hasła
forgetPassword = ctk.CTkButton(
    login_window,
    text="Forget password",
    width=60,
    height=30)

#=========================================================================
#    umieszczenie widgetow
#=========================================================================
loginLabel.place(x=265, y = 165)
login_input.place(x = 265, y = 200)
password_input.place(x = 265, y = 250)
show_password.place(x = 265, y = 300)
login_button.place(x = 365, y = 350)
forgetPassword.place(x=245, y = 350)
newAccountLabel.place(x = 15, y = 465)
newUserButton.place(x=180, y=460)

#=========================================================================
#       run
#=========================================================================
# def run_LoginPage():
#     #BazaDanych.open_db()
#     client = BazaDanych.open_db()
#     login_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(client))
#     login_window.mainloop()
#     login_window.destroyed = False

# def run_LoginPage():
#     login_window.mainloop()
#     login_window.destroyed = False

# def on_closing(client):
#     #print(type(client))
#     baza.close_db(client)
#     login_window.destroy()


def on_closing():
    if login_window:
        try:
            baza.close_database_connection()
            login_window.destroy()
        except tk.TclError:
            pass

def run_LoginPage():
    baza.connect_to_database()
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    login_window.mainloop()
run_LoginPage()
# emilka jest w bazie danych
#    client = baza.open_db()
#    baza.create_db()
#    login_window.protocol("WM_DELETE_WINDOW", lambda: on_closing(client)

import json
import re
import tkinter as tk
import bcrypt
import customtkinter as ctk
import Database
from Settings import load_setting, load_translation
import Encryption

sciezka_do_pliku = 'settings.json'
ustawienia = load_setting(sciezka_do_pliku)
jezyk = ustawienia.get('language', 'en')
tlumaczenie = load_translation(jezyk, 'ForgetWindow')

def read_language_from_settings():
    with open('settings.json', 'r') as plik:
        ustawienia = json.load(plik)
    return ustawienia.get('language', 'en')

def update_translations_in_other_windows():
    global tlumaczenie
    jezyk = read_language_from_settings()
    tlumaczenie = load_translation(jezyk, 'ForgetWindow')
##########################################################
# wybór uzytkownika
##########################################################
def select_username(window, show_login_callback):
    window.geometry("350x200")
    window.title("LockBox - Reset Password")
    read_language_from_settings()
    update_translations_in_other_windows()

    def go_back_to_login():
        for widget in window.winfo_children():
            widget.place_forget()
        window.title("LockBox - Login")
        window.geometry("700x500")
        show_login_callback()

    def switch_to_collect_data(username):
        hide_select_username_page()
        collect_data(window, show_login_callback, username)

    def check_user_in_database(username):
        user = Database.users_collection.find_one({"username": username})
        return user is not None

    def on_submit():
        user = username_entry.get()
        if check_user_in_database(user):
            submit_button.configure(state="disabled")
            window.after(100, lambda: switch_to_collect_data(user))
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["User_not_found"], text_color="red")

    def clear_textboxes():
        username_entry.delete(0, ctk.END)
        username_entry.configure(placeholder_text=tlumaczenie["Username"])
        window.focus_set()
        submit_button.configure(state="disabled")

    def check_username():
        if username_entry.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    username_label = ctk.CTkLabel(window, width=350, height=30,compound="center", text=tlumaczenie["Select_username"])
    username_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Username"])
    submit_button = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_submit)
    error_label = ctk.CTkLabel(window, width=350, height=30, text="", compound="center")
    cancel_button = ctk.CTkButton(window, width=50, height=30, text=tlumaczenie["Cancel"], command=go_back_to_login)
    # Umieszczanie widżetów na ekranie
    # bg_color="transparent", fg_color="transparent"
    username_label.place(x=0, y=55)
    username_entry.place(x=70, y=95)
    submit_button.place(x=230, y=95)
    cancel_button.place(x=10, y=10)
    error_label.place(x=0, y=165)

    username_entry.bind("<KeyRelease>", lambda event: check_username())

    def hide_select_username_page():
        username_entry.place_forget()
        submit_button.place_forget()
        error_label.place_forget()
        username_label.place_forget()
##########################################################
# sprawdzanie czy dane sa poprawne
##########################################################
def collect_data(window, show_login_callback, username):
    """Wyświetla ekran weryfikacji danych (PIN i odpowiedź na pytanie)."""
    read_language_from_settings()
    update_translations_in_other_windows()

    def switch_to_change_password():
        hide_collect_data_page()
        change_password(window, show_login_callback, username)

    def get_security_question():
        user = Database.users_collection.find_one({"username": username})
        if user:
            return user.get("security_question", "")
        return ""

    def on_submit():
        user_pin = pin_entry.get()
        user_answer = answer_entry.get()

        correct_pin = Database.users_collection.find_one({"username": username}, {"pin_code": 1}).get("pin_code", "")
        correct_answer = Database.users_collection.find_one({"username": username}, {"answer": 1}).get("answer", "")

        if bcrypt.checkpw(user_pin.encode('utf-8'), correct_pin.encode('utf-8')) and bcrypt.checkpw(user_answer.encode('utf-8'), correct_answer.encode('utf-8')):
            submit_button.configure(state="disabled")
            window.after(100, switch_to_change_password)
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["Invalid_data"], justify="center")

    def clear_textboxes():
        answer_entry.delete(0, ctk.END)
        pin_entry.delete(0, ctk.END)
        window.focus_set()
        submit_button.configure(state="disabled")

    def check_data():
        if answer_entry.get() == "" or pin_entry.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    # Definiowanie widżetów
    question_label = ctk.CTkLabel(window, width=170, height=30,compound="center", wraplength=170, text=get_security_question())
    answer_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Answer"])
    pin_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["PIN"])
    submit_button = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_submit)
    error_label = ctk.CTkLabel(window, width=350, height=30, text="", text_color="red", compound="center")

    # Umieszczanie widżetów na ekranie
    question_label.place(x=0, y=55)
    answer_entry.place(x=180, y=55)
    pin_entry.place(x=180, y=95)
    submit_button.place(x=150, y=135)
    error_label.place(x=0, y=165)

    answer_entry.bind("<KeyRelease>", lambda event: check_data())
    pin_entry.bind("<KeyRelease>", lambda event: check_data())

    def hide_collect_data_page():
        question_label.place_forget()
        answer_entry.place_forget()
        pin_entry.place_forget()
        submit_button.place_forget()
        error_label.place_forget()
##########################################################
# zmienianie hasla
##########################################################
def change_password(window, show_login_callback, username):
    """Wyświetla ekran zmiany hasła."""
    read_language_from_settings()
    update_translations_in_other_windows()

    def clear_textbox():
        password_entry.delete(0, ctk.END)
        confirm_password_entry.delete(0, ctk.END)
        window.focus_set()
        submit.configure(state="disabled")


    def on_password_change():
        new_password = password_entry.get()
        if check_password_validity(new_password):
            if new_password == confirm_password_entry.get():
                result = Database.reset_user_password(username, new_password)
                if result["success"]:
                    show_login_callback()
                    hide_change_password_page()
                else:
                    clear_textbox()
                    error_label.configure(text=result["message"], text_color="red")
            else:
                clear_textbox()
                error_label.configure(text=tlumaczenie["Passwords_do_not_match"], text_color="red")
        else:
            clear_textbox()
            error_label.configure(text=tlumaczenie["Password_requirements"], text_color="red")
    
    def check_password_validity(password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        # else:
        #     print("tu jest kurwa błąd")
        #     error_label.configure(text=tlumaczenie["Password_requirements"])
        #     return False
        
    def check_data():
        if password_entry.get() == "" or confirm_password_entry.get() == "":
            submit.configure(state="disabled")
        else:
            submit.configure(state="normal")

    def show_password_button():
        if show_password_var.get() == 1:
            password_entry.configure(show="")
            confirm_password_entry.configure(show="")
        else:
            password_entry.configure(show="*")
            confirm_password_entry.configure(show="*")
    # Definiowanie widżetów
    password_label = ctk.CTkLabel(window, width=150, text = "podaj nowe haslo")
    password_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["New_password"], show="*")
    confirm_password_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Confirm_password"], show="*")
    submit = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_password_change)
    error_label = ctk.CTkLabel(window, width=340, wraplength=340, height=30,justify="center", text="", text_color="red", compound="center")
    show_password_var = tk.IntVar()
    show_password = ctk.CTkCheckBox(window, width=50,checkbox_width=20,variable=show_password_var, command=show_password_button, checkbox_height=20, text="pokaz haslo")

    # Umieszczanie widżetów na ekranie
    password_label.place(x=100,y=30)
    password_entry.place(x=20, y=70)
    confirm_password_entry.place(x=180, y=70)
    submit.place(relx=0.65, y=110)
    error_label.place(x=5, y=150)
    show_password.place(x=40, y=110)

    password_entry.bind("<KeyRelease>", lambda event: check_data())
    confirm_password_entry.bind("<KeyRelease>", lambda event: check_data())

    def hide_change_password_page():
        password_entry.place_forget()
        confirm_password_entry.place_forget()
        submit.place_forget()
        error_label.place_forget()

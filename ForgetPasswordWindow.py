import json
import re
import customtkinter as ctk
import Baza
from Settings import wczytaj_ustawienia, wczytaj_tlumaczenie_modulu
import Szyfrowanie

sciezka_do_pliku = 'settings.json'
ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
jezyk = ustawienia.get('language', 'en')
tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'ForgetWindow')

def read_language_from_settings():
    with open('settings.json', 'r') as plik:
        ustawienia = json.load(plik)
    return ustawienia.get('language', 'en')

def update_translations_in_other_windows():
    global tlumaczenie
    jezyk = read_language_from_settings()
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'ForgetWindow')
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
        user = Baza.users_collection.find_one({"username": username})
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

    def check_username():
        if username_entry.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    # Definiowanie widżetów
    username_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Username"])
    submit_button = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_submit)
    error_label = ctk.CTkLabel(window, width=450, height=30, text="", compound="center")
    cancel_button = ctk.CTkButton(window, width=50, height=30, text=tlumaczenie["Cancel"], command=go_back_to_login)
    # Umieszczanie widżetów na ekranie
    username_entry.place(x=120, y=75)
    submit_button.place(x=280, y=75)
    cancel_button.place(x=15, y=15)
    error_label.place(x=0, y=150)

    username_entry.bind("<KeyRelease>", lambda event: check_username())

    def hide_select_username_page():
        username_entry.place_forget()
        submit_button.place_forget()
        error_label.place_forget()
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
        user = Baza.users_collection.find_one({"username": username})
        if user:
            return user.get("security_question", "")
        return ""

    def on_submit():
        user_pin = pin_entry.get()
        user_answer = answer_entry.get()

        correct_pin = Baza.users_collection.find_one({"username": username}, {"pin_code": 1}).get("pin_code", "")
        correct_answer = Baza.users_collection.find_one({"username": username}, {"answer": 1}).get("answer", "")

        if Szyfrowanie.hash_password(user_pin) == correct_pin and Szyfrowanie.hash_password(user_answer) == correct_answer:
            submit_button.configure(state="disabled")
            window.after(100, switch_to_change_password)
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["Invalid_data"], justify="center")

    def clear_textboxes():
        answer_entry.delete(0, ctk.END)
        pin_entry.delete(0, ctk.END)

    def check_data():
        if answer_entry.get() == "" or pin_entry.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    # Definiowanie widżetów
    question_label = ctk.CTkLabel(window, width=180, height=30, text=get_security_question())
    answer_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Answer"])
    pin_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["PIN"])
    submit_button = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_submit)
    error_label = ctk.CTkLabel(window, width=450, height=30, text="", text_color="red", compound="center")

    # Umieszczanie widżetów na ekranie
    question_label.place(x=35, y=30)
    answer_entry.place(x=235, y=30)
    pin_entry.place(x=235, y=80)
    submit_button.place(x=200, y=130)
    error_label.place(x=0, y=160)

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

    def on_password_change():
        new_password = password_entry.get()
        if check_password_validity(new_password):
            if new_password == confirm_password_entry.get():
                result = Baza.reset_user_password(username, new_password)
                if result["success"]:
                    show_login_callback()
                    hide_change_password_page()
                else:
                    error_label.configure(text=result["message"], text_color="red")
            else:
                error_label.configure(text=tlumaczenie["Passwords_do_not_match"], text_color="red")

    def check_password_validity(password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            error_label.configure(text=tlumaczenie["Password_requirements"])
            return False

    # Definiowanie widżetów
    password_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["New_password"], show="*")
    confirm_password_entry = ctk.CTkEntry(window, width=150, height=30, placeholder_text=tlumaczenie["Confirm_password"], show="*")
    submit_button = ctk.CTkButton(window, state="disabled", width=50, height=30, text=tlumaczenie["Submit"], command=on_password_change)
    error_label = ctk.CTkLabel(window, width=450, height=30, text="", text_color="red", compound="center")

    # Umieszczanie widżetów na ekranie
    password_entry.place(x=65, y=40)
    confirm_password_entry.place(x=235, y=40)
    submit_button.place(x=285, y=90)
    error_label.place(x=0, y=160)

    def hide_change_password_page():
        password_entry.place_forget()
        confirm_password_entry.place_forget()
        submit_button.place_forget()
        error_label.place_forget()

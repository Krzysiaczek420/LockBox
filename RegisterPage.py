import re
import Baza as Baza
import customtkinter as ctk
import PinWindow as pin
import tkinter as tk
from Settings import ustaw_motyw_i_kolor, wczytaj_ustawienia, wczytaj_tlumaczenie_modulu

sciezka_do_pliku = 'settings.json'

motyw, kolor = ustaw_motyw_i_kolor(sciezka_do_pliku)
ctk.set_appearance_mode(motyw)
ctk.set_default_color_theme(kolor)
current_error = None

def show_register_page(window, show_login_callback):
    window.title("LockBox-Register")

    ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
    jezyk = ustawienia.get('language', 'en')
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'RegisterPage')
    
    def go_back_to_login():
        for widget in window.winfo_children():
            widget.place_forget()
        window.title("LockBox - Login")
        show_login_callback()

    def check_if_empty(event=None):
        if (username_input.get() == "" or 
            password_input.get() == "" or 
            confirm_password_input.get() == ""):
            register_button.configure(state="disabled")
        else:
            register_button.configure(state="normal")

    def check_passwords():
        global same_passwords
        same_passwords = False
        password = password_input.get()
        confirm_password = confirm_password_input.get()
        if password == confirm_password and (confirm_password != "" and password != ""):
            same_passwords = True
        else:
            clear_textboxes()
            window.focus_set()
            error_label.configure(text=tlumaczenie["Passwords_are_not_the_same"])

################################################################
# funkcja sprawdzjaca czy textboxy nie sa puste
# jesli nie aktywowanie przycisku rejestracji
################################################################
    def check_if_empty(event=None):
        if (username_input.get() == "" or password_input.get() == "" or
            confirm_password_input.get() == "" or answer_input.get() == "" or
            security_question_combobox.get() in (tlumaczenie["Select_question"], "")):
            register_button.configure(state="disabled")
        else:
            register_button.configure(state="normal")

################################################################
# funkcja sprawdzajaca czy login ma poprawna dlugosc (5 znakow)
################################################################
    def check_username_length():
        username = username_input.get()
        if ' ' in username:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["No_spaces"])
            return False
        elif len(username) >= 5:
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["Username_length"])
            return False

################################################################
# funckaj sprawdzajca czy haslo spelnia odpowiednie wymagania
# jelsi nie komunikat i czyszczenie textboxow
################################################################
    def check_password_validity():
        password = password_input.get()
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$.!%*?&])[A-Za-z\d@$.!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["Password_requirements"], justify="center", compound="center")
            return False

################################################################
# obsluga checkboxu do wyswietlania hasla
################################################################
    def show_password_button():
        if show_password_var.get() == 1:
            password_input.configure(show="")
            confirm_password_input.configure(show="")
        else:
            password_input.configure(show="*")
            confirm_password_input.configure(show="*")

################################################################
# funkcja odpowiedzialna za combobox
# jesli zostanie wybrana opcja "Other..." to pozwala na wpisanie
# w innym wypadku wpisywanie jest zablokowane
################################################################
    def on_other_selected(choice):
        if security_question_combobox.get() == tlumaczenie["Other"]:
            security_question_combobox.configure(state="normal")
            security_question_combobox.set("")
        else:
            security_question_combobox.configure(state="readonly")
        check_if_empty()

################################################################
# funkcja do czyszczenia textboxow
################################################################
    def clear_textboxes():
        username_input.delete(0, tk.END)
        username_input.configure(placeholder_text=tlumaczenie["Username"])
        password_input.delete(0, tk.END)
        password_input.configure(placeholder_text=tlumaczenie["Password"])
        confirm_password_input.delete(0, tk.END)
        confirm_password_input.configure(placeholder_text=tlumaczenie["Confirm_password"])
        security_question_combobox.set(tlumaczenie["Select_question"])
        answer_input.delete(0, tk.END)
        answer_input.configure(placeholder_text=tlumaczenie["Answer"])
        error_label.configure(text="")
        register_button.configure(state="disabled")
        window.focus_set()

################################################################
# funkcja odpowiedzialna za przycisk rejestracji
################################################################
    def register_action():
        if check_username_length() and check_password_validity():
            check_passwords()
            if same_passwords:
                pin_value = pin.generate_random_pin()
                result = Baza.add_user(
                    username=username_input.get(),
                    password=password_input.get(),
                    security_question=security_question_combobox.get(),
                    answer=answer_input.get(),
                    pin_code=pin_value
                )
                if result["success"]:
                    pin.pin_window(window, pin_value, show_login_callback)
                else:
                    error_label.configure(text=result["message"])

################################################################
# widgety
################################################################
    username_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Username"], )
    
    show_password_var = tk.IntVar()
    show_password_register = ctk.CTkCheckBox(window, 
        text=tlumaczenie["Show_password"], 
        width=150, 
        height=30,
        variable=show_password_var, 
        command=show_password_button)
    
    password_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Password"], 
        show="*")
    
    confirm_password_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Confirm_password"], 
        show="*")

################################################################
# wartosci comboboxa (pytania bezpieczenstwa)
################################################################
    security_question_values = [
        tlumaczenie["Security_question1"],
        tlumaczenie["Security_question2"],
        tlumaczenie["Security_question3"],
        tlumaczenie["Security_question4"],
        tlumaczenie["Security_question5"],
        tlumaczenie["Other"]]

    security_question_combobox = ctk.CTkComboBox(window, 
        state="readonly", 
        width=150, 
        height=30, 
        values=security_question_values, 
        command=on_other_selected)
    
    security_question_combobox.set(tlumaczenie["Select_question"])
    security_question_combobox.bind("<<ComboboxSelected>>", on_other_selected)

    answer_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Answer"])
    
    register_button = ctk.CTkButton(
        window, 
        state="disabled", 
        text=tlumaczenie["Register"], 
        command=register_action)
    
    error_label = ctk.CTkLabel(
        window, 
        text="",
        compound="center", 
        width=700, 
        height=50, 
        fg_color="transparent", 
        text_color="red")
    back_button = ctk.CTkButton(
        window, 
        text = tlumaczenie["Back"],
        width=70,
        command = go_back_to_login)
                                

    username_input.bind("<KeyRelease>", check_if_empty)
    password_input.bind("<KeyRelease>", check_if_empty)
    confirm_password_input.bind("<KeyRelease>", check_if_empty)
    answer_input.bind("<KeyRelease>", check_if_empty)

    register_label = ctk.CTkLabel(window, 
        text="Registration", 
        width=140, 
        height=20)

    username_input.place(x=275, y=150)
    password_input.place(x=275, y=200)
    confirm_password_input.place(x=275, y=250)
    security_question_combobox.place(x=195, y=300)
    answer_input.place(x=365, y=300)
    show_password_register.place(x=275, y=350)
    register_button.place(x=275, y=400)
    error_label.place(x=0, y=430)
    back_button.place(x=25,y=25)

import re
import Database as Database
import customtkinter as ctk
import Pin_Window as pin
import tkinter as tk
from Settings import set_theme_and_color, load_setting, load_translation

settings_file_path = 'settings.json'

theme, color = set_theme_and_color(settings_file_path)
ctk.set_appearance_mode(theme)
ctk.set_default_color_theme(color)
current_error = None

def show_register_page(window, show_login_callback):
    window.title("LockBox - Register")

    settings = load_setting(settings_file_path)
    language = settings.get('language', 'en')
    translation = load_translation(language, 'RegisterPage')
    
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
            error_label.configure(text=translation["Passwords_are_not_the_same"])

################################################################
# funkcja sprawdzjaca czy textboxy nie sa puste
# jesli nie aktywowanie przycisku rejestracji
################################################################
    def check_if_empty(event=None):
        if (username_input.get() == "" or password_input.get() == "" or
            confirm_password_input.get() == "" or answer_input.get() == "" or
            security_question_combobox.get() in (translation["Select_question"], "")):
            register_button.configure(state="disabled")
        else:
            register_button.configure(state="normal")

################################################################
# funkcja sprawdzajaca czy login ma poprawna dlugosc (5 znakow)
################################################################
    def check_username_length():
        username = username_input.get()
        if username.endswith(' '):
            username = username.rstrip()
            username_input.delete(0, "end")
            username_input.insert(0, username)  
        if ' ' in username:
            clear_textboxes()
            error_label.configure(text=translation["No_spaces"])
            return False
        elif len(username) >= 5:
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text=translation["Username_length"])
            return False

################################################################
# funckaj sprawdzajca czy haslo spelnia odpowiednie wymagania
# jelsi nie komunikat i czyszczenie textboxow
################################################################
    def check_password_validity():
        password = password_input.get()

        if password.endswith(' '):
            password = password.rstrip()
            password_input.delete(0, "end")
            password_input.insert(0, password)

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$.!%*?&])[A-Za-z\d@$.!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text=translation["Password_requirements"], justify="center", compound="center")
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
        if security_question_combobox.get() == translation["Other"]:
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
        username_input.configure(placeholder_text=translation["Username"])
        password_input.delete(0, tk.END)
        password_input.configure(placeholder_text=translation["Password"])
        confirm_password_input.delete(0, tk.END)
        confirm_password_input.configure(placeholder_text=translation["Confirm_password"])
        security_question_combobox.set(translation["Select_question"])
        answer_input.delete(0, tk.END)
        answer_input.configure(placeholder_text=translation["Answer"])
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
                result = Database.add_user(
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
        placeholder_text=translation["Username"], )
    
    show_password_var = tk.IntVar()
    show_password = ctk.CTkCheckBox(window, 
        text=translation["Show_password"], 
        width=150, 
        height=30,
        checkbox_width=20,
        checkbox_height=20,
        border_width=2,
        variable=show_password_var, 
        command=show_password_button)
    
    password_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=translation["Password"], 
        show="*")
    
    confirm_password_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=translation["Confirm_password"], 
        show="*")

################################################################
# wartosci comboboxa (pytania bezpieczenstwa)
################################################################
    security_question_values = [
        translation["Security_question1"],
        translation["Security_question2"],
        translation["Security_question3"],
        translation["Security_question4"],
        translation["Security_question5"],
        translation["Other"]]

    security_question_combobox = ctk.CTkComboBox(window, 
        state="readonly", 
        width=150, 
        height=30, 
        values=security_question_values, 
        command=on_other_selected)
    
    security_question_combobox.set(translation["Select_question"])
    security_question_combobox.bind("<<ComboboxSelected>>", on_other_selected)

    answer_input = ctk.CTkEntry(window, 
        width=150, 
        height=30, 
        placeholder_text=translation["Answer"])
    
    register_button = ctk.CTkButton(
        window, 
        state="disabled", 
        text=translation["Register"], 
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
        text = translation["Back"],
        width=70,
        command = go_back_to_login)
                                
    username_input.bind("<KeyRelease>", check_if_empty)
    password_input.bind("<KeyRelease>", check_if_empty)
    confirm_password_input.bind("<KeyRelease>", check_if_empty)
    answer_input.bind("<KeyRelease>", check_if_empty)

    username_input.place(x=275, y=150)
    password_input.place(x=275, y=200)
    confirm_password_input.place(x=275, y=250)
    security_question_combobox.place(x=195, y=300)
    answer_input.place(x=365, y=300)
    show_password.place(x=275, y=350)
    register_button.place(x=275, y=400)
    error_label.place(x=0, y=430)
    back_button.place(x=15,y=15)

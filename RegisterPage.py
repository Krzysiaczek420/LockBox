import re
import customtkinter as ctk
from CTkToolTip import *
import tkinter as tk
from PIL import Image, ImageTk
import pin_window as pin
import Baza

#=========================================================================
#do zrobienia:
# 3. funkcja do minimalnej dlugosci hasla i nazwy
# 4. zapis do bazy
# 5. naprawic label z komunikatami
#     if haslo jest za krotkie: label= "haslo jest za krotkie" funkcja ktora to sprawdza 
# 6. po zrobieniu zapisu do bazy trzeba sprawdzac czy login juz nie wystepuje w bazie
# 7. szyfrowanie hasel
# 8. jesli sie zarejestrowalismy, wyswietlamy okno z pinem do ozdzywskiwania hasla, przed zamknieciem tego okna dodatkowe okno upewnienia czy zamknac
#                                                                                    po zamknieciu go zamykamy okno rejestracji i otwieramy logowanie 
# 10.
#=========================================================================


#=========================================================================
#           definiowanie okna rejestracji
#=========================================================================
def open_register_window(login_window):
    register_window = ctk.CTk()
    register_window.geometry("700x500")
    register_window.title("LockBox-Registration")
    register_window.resizable(False, False) 
#=========================================================================
#   funkcje
#=========================================================================
    #sprawdza czy hasla sa takie same
    def check_passwords(): 
        global same_passwords
        same_passwords = False
        password = password_input.get()
        confirm_password = confirm_password_input.get()
        if password == confirm_password and (confirm_password != "" and password != ""):
            print("Passwords are the same")
            same_passwords = True
        else:
            clear_textboxes()
            register_window.focus_set()
            error_label.configure(text="Passwords are not the same")

    #funkcja do sprawdzania czy pola nie sa puste
    def check_if_empty(event=None):
        username_value = username_input.get()
        password_value = password_input.get()
        confirm_password_value = confirm_password_input.get()
        answer_value = answer_input.get()
        security_question_combo_value = security_question_combobox.get()

        if (username_value == "" or 
            password_value == "" or 
            confirm_password_value == "" or 
            answer_value == "" or
            security_question_combo_value in ("Select Question", "")):
                register_button.configure(state="disabled")
        else:
            register_button.configure(state="normal")

        #funkcja do sprawdzania czy nazwa uzytkownika ma odpowiednia dlugosc
    def check_username_length():
        username = username_input.get()
        if ' ' in username:
            clear_textboxes()
            error_label.configure(text="Username cannot contain spaces")
            return False
        elif len(username) >= 5:
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            #cancel_focus(event=None)
            error_label.configure(text="Username must be at least 5 characters long")
            return False
        

        
    def check_password_validity():
        password = password_input.get()
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text="Password must contain at least 12 characters including at least one uppercase letter, one lowercase letter, one digit, and one special character")
            return False

    def cancel_focus(event=None):  # Set a default value for event
        if event:
            widget = register_window.winfo_containing(event.x_root, event.y_root)
            if widget == register_window:
                register_window.focus_set()
                if security_question_combobox.get() == "":
                    security_question_combobox.set("Select Question")
        else:
            register_window.focus_set()
            if security_question_combobox.get() == "":
                security_question_combobox.set("Select Question")

    #Funkcja pokazujaca haslo
    def show_password_button(): 
        if password_input.cget("show") =="*" or confirm_password_input.cget("show")=="*":
            password_input.configure(show=""),
            confirm_password_input.configure(show="")
        else:
            password_input.configure(show="*"),
            confirm_password_input.configure(show="*")

    #funkcja wyboru pytania zabezpieczajacego pozwalajaca edytowac pytanie zabezpieczajace po wybraniu opcji "Other"
    def on_other_selected(choice): 
        if security_question_combobox.get() == "Other...":
            security_question_combobox.configure(state="normal")
            security_question_combobox.set("")
        else:
            security_question_combobox.configure(state="readonly")
        check_if_empty()

    #funkcja do sprawdzania czy combobox nie jest pusty
    def check_combobox_empty():
        security_question_combo_value = security_question_combobox.get()
        if security_question_combo_value == "Other...":
            register_button.configure(state="disabled")
        else:
            check_if_empty()

    #funkcja czyszczaca pola tekstowe
    def clear_textboxes(): #funkcja czyszczaca pola tekstowe
        username_input.delete(0, tk.END)
        username_input.configure(placeholder_text="Username")
        password_input.delete(0, tk.END)
        password_input.configure(placeholder_text="Password")
        confirm_password_input.delete(0, tk.END)
        confirm_password_input.configure(placeholder_text="Confirm password")
        security_question_combobox.set("Select Question")
        answer_input.delete(0, tk.END)
        answer_input.configure(placeholder_text="Security Question Answer")
        error_label.configure(text="")
        register_button.configure(state="disabled")
        cancel_focus()

    #dzialania po kliknieciu przycisku zarejestruj
    def register_action(): 
        if check_username_length() and check_password_validity():
            check_passwords()
            if same_passwords == True:
                pin_value = pin.generate_random_pin()
                result = Baza.add_user(
                    username=username_input.get(),
                    password=password_input.get(),
                    security_question=security_question_combobox.get(),
                    answer=answer_input.get(),
                    pin_code=pin_value
                )
                if result["success"]:
                    pin.pin_window()
                    on_closing()
                else:
                    error_label.configure(text=result["message"])

    #otwiera okno logowania po zamknieciu okna rejestracji   
    def on_closing():
        if register_window:
            try:
                register_window.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
            except tk.TclError:
                pass
    register_window.protocol("WM_DELETE_WINDOW", on_closing)
    register_window.bind("<Button-1>", cancel_focus)

#=========================================================================
#    tooltipy
#=========================================================================
    # tooltip1 = CTkToolTip(button, message="text")
    # def show_text():
    #     print(tooltip1)
    # tooltip1 = CTkToolTip(button, message="text")
#=========================================================================
    # Widgety
#=========================================================================
    #nazwa uzytkownika
    username_input = ctk.CTkEntry(register_window,
        width=150,
        height=30,
        placeholder_text="Username")

    #przycisk pokazujacy haslo
    show_password_register = ctk.CTkCheckBox(register_window,
        text = "show password",
        width=150,
        height=30,
        command=show_password_button)
    
    #wpisywanie hasła
    password_input = ctk.CTkEntry(register_window,
        width=150,
        height=30,
        placeholder_text="Password",
        show="*")
        #command=show_text)
    
    #potwierdzenie hasla
    confirm_password_input = ctk.CTkEntry(register_window,
        width=150,
        height=30,
        placeholder_text="Confirm Password",
        show="*")

    #zawartosc comboboxa pytan
    security_question_values = [
        "What is your mother's maiden name?",
        "What is the name of your",
        "Where were you born?",
        "Other..."]

        #wybór pytania zabezpieczającego
    security_question_combobox = ctk.CTkComboBox(register_window,
        state="readonly",
        width=150,
        height=30,
        values=security_question_values,
        command=on_other_selected
        )
    security_question_combobox.set("Select Question")
    security_question_combobox.bind("<<ComboboxSelected>>", on_other_selected)

    #odpowiedź na pytanie zabezpieczające
    answer_input = ctk.CTkEntry(register_window,
        width=150,
        height=30,
        placeholder_text="Security Question Answer")

    #przycisk rejestracji
    register_button = ctk.CTkButton(
        register_window,
        state="disabled",
        text="Register",
        command=register_action)
    
    #error message
    error_label = ctk.CTkLabel(register_window,
        text="",
        text_color="red")
    
# #=========================================================================
# #    tooltipy
# #=========================================================================
    tooltip1 = CTkToolTip(password_input, justify="left", message="Password need coitein:\n•12 charakters\n•1 Uppercase letter\n•1 Lowercase letter\n•1 Digit\n•1 Special character")
    # def show_text():
    #     print(tooltip1.get())
#=========================================================================
#    umieszczenie widgetow
#=========================================================================
    username_input.place(x=275, y=150)
    password_input.place(x=275, y=200)
    confirm_password_input.place(x=275, y=250)
    security_question_combobox.place(x=195, y=300)
    answer_input.place(x=365, y=300)
    show_password_register.place(x=275, y=350)
    register_button.place(x=275, y=400)
    error_label.place(x=275, y=450)
    
#=========================================================================
#    bindowanie(uruchamianie) funkcji
#=========================================================================

    security_question_combobox.bind("<<ComboboxSelected>>", lambda event: on_other_selected(security_question_combobox.get()))
    security_question_combobox.bind("<KeyRelease>", lambda event: check_combobox_empty())
    username_input.bind("<KeyRelease>", check_if_empty)
    password_input.bind("<KeyRelease>", check_if_empty)
    confirm_password_input.bind("<KeyRelease>", check_if_empty)
    answer_input.bind("<KeyRelease>", check_if_empty)

#=========================================================================
#       run
#=========================================================================
    register_window.mainloop()

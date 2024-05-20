import re
import tkinter as tk
import customtkinter as ctk 
import Baza
from Settings import wczytaj_ustawienia, wczytaj_tlumaczenie_modulu
import Szyfrowanie
################################################################
# funkcja do odzyskiwania hasla 
################################################################
sciezka_do_pliku = 'settings.json'
ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
jezyk = ustawienia.get('language', 'en')
tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'ForgetWindow')
################################################################
# pierwsze okienko, wpisywanie nazwy uzytkownika
################################################################
def select_username(login_window, run_LoginPage):

###################################################################
# zmiana okien po nacisnieciu submit
###################################################################
    def switch_windows(username):
        select_username.destroy()
        collect_data(login_window, run_LoginPage,username)

################################################################
# funkcja do sprawdzania czy uzytkownik istnieje w bazie danych
################################################################
    def check_user_in_database(username):
        user = Baza.users_collection.find_one({"username": username})
        return user is not None

################################################################
# dzialanie przycisku "submit"
# jesli uzytkownik istnieje w bazie danych to przejdz do kolejnego okna
# jesli uzytkownik nie istnieje w bazie danych to wyczysc pola i pokazac komunikat
################################################################
    def on_click():
        user = username.get()
        if check_user_in_database(user):
            submit_button.configure(state="disabled")
            select_username.after(100, lambda: switch_windows(user))
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["User_not_found"],text_color="red")
            select_username.focus_set() 

#################################################################
# funkcja aktywujaca guzik gdy pole nie jest puste
#################################################################   
    def check_username(event=None):
        if username.get() == "":  
            submit_button.configure(state="disabled")  
        else:
            submit_button.configure(state="normal")

##################################################################
# funckaj do przenoszenia skupienia na okno glowne
# w przypadku klikniecia poza textbox
##################################################################
    def cancel_focus(event=None):
        if event:
            widget = select_username.winfo_containing(event.x_root, event.y_root)
            if widget == select_username:
                select_username.focus_set()

 ##################################################################
 # funkcja do czyszczenia textboxow (bledna nazwa uzytkownika)
 ###################################################################   
    def clear_textboxes():
        username.delete(0, tk.END)
        username.configure(placeholder_text=tlumaczenie["Username"])
    
###################################################################
# definiowanie okna glownego
###################################################################
    select_username = ctk.CTk()
    select_username.geometry("450x200")
    select_username.title("LockBox-Forget Password")
    select_username.resizable(False, False)
    select_username.protocol("WM_DELETE_WINDOW", lambda: on_closing(select_username, login_window))
    select_username.bind("<Button-1>", cancel_focus)

    username = ctk.CTkEntry(select_username, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Username"])
    
    submit_button = ctk.CTkButton(select_username,
        state="disabled", 
        width=50, 
        height=30, 
        text=tlumaczenie["Submit"], 
        command=on_click)
    
    error_label = ctk.CTkLabel(select_username, 
        width=450, 
        height=30, 
        text="",
        compound="center")

    username.place(x=120, y=75)
    submit_button.place(x=280, y=75)
    error_label.place(x=0, y=150)

    username.bind("<KeyRelease>", lambda event: check_username())
    select_username.mainloop()

###################################################################
# drugie okno, wpisywanie odpowiedzi na pytanie bezpieczenstwa i pinu
###################################################################
def collect_data(login_window, run_LoginPage,username):

###################################################################
# funkcja do zmieniania okien po nacisnieciu submit
###################################################################
    def switch_windows():
        collect_data.destroy()
        change_password(login_window, run_LoginPage,username)

###################################################################
# funkcja wpisujaca do textboxa "question" pytanie bezpieczenstwa
# przypisane do wczesniej wybranego uzytkownika
###################################################################
    def get_security_question():
        user = Baza.users_collection.find_one({"username": username})
        if user:
            return user.get("security_question", "")
        return ""

###################################################################
# fuunkcja odpowiedzialna za przycisk "submit"
# sprawdzanie czy pin i odpowiedz sa poprawne
# jesli tek nastepne okno, jesli nie komunikat i czyszczenie textboxow
###################################################################
    def on_click():
        pin = pin_number.get()
        hashed_pin = Szyfrowanie.hash_password(pin)

        user_answer = answer.get()
        hashed_answer = Szyfrowanie.hash_password(user_answer)

        correct_pin = Baza.users_collection.find_one({"username": username}, {"pin_code": 1}).get("pin_code", "")
        correct_answer = Baza.users_collection.find_one({"username": username}, {"answer": 1}).get("answer", "")

        if correct_pin == hashed_pin and correct_answer == hashed_answer:
            submit_button.configure(state="disabled")
            collect_data.after(100, switch_windows)
        else:
            clear_textboxes()
            error_label.configure(text=tlumaczenie["Invalid_data"],justify="center")
            collect_data.focus_set()

###################################################################
# funkcja sprawdzajaca czy textboxy nie sa puste
# jesli pola sa puste guzik jest nieaktywny
###################################################################
    def check_data(event=None): 
        if (answer.get() == "" or pin_number.get() == ""):
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")  

###################################################################
# funkcja do czyszczenia textboxow
###################################################################
    def clear_textboxes():
        answer.delete(0, tk.END)
        answer.configure(placeholder_text=tlumaczenie["Answer"])
        pin_number.delete(0, tk.END)
        pin_number.configure(placeholder_text=tlumaczenie["PIN"])

###################################################################
# definiowanie drugiego okna
###################################################################
    collect_data = ctk.CTk()
    collect_data.geometry("450x200")
    collect_data.title("LockBox-Forget Password")
    collect_data.resizable(False, False)
    collect_data.protocol("WM_DELETE_WINDOW", lambda: on_closing(collect_data, login_window))

    question = ctk.CTkEntry(collect_data, 
        width=180, 
        height=30, 
        placeholder_text=tlumaczenie["Question"])
    
    answer = ctk.CTkEntry(collect_data, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["Answer"])
    
    pin_number = ctk.CTkEntry(collect_data, 
        width=150, 
        height=30, 
        placeholder_text=tlumaczenie["PIN"])
    
    submit_button = ctk.CTkButton(collect_data, 
        state="disabled", 
        width=50, 
        height=30, 
        text=tlumaczenie["Submit"], 
        command=on_click)
    
    error_label = ctk.CTkLabel(collect_data, 
        width=450, 
        height=30, 
        text="",
        text_color="red",
        compound="center")

    question.place(x=35, y=30)
    answer.place(x=235, y=30)
    pin_number.place(x=235, y=80)
    submit_button.place(x=200, y=130)
    error_label.place(x=0, y=160)

    security_question = get_security_question()
    question.insert(0, security_question)
    question.configure(state="disabled")

    answer.bind("<KeyRelease>", lambda event: check_data())
    pin_number.bind("<KeyRelease>", lambda event: check_data())
    collect_data.mainloop()

###################################################################
# trzecie okno, wpisywanie nowego hasla
###################################################################
def change_password(login_window, run_LoginPage, username):

###################################################################
# funkcja do ponownego otwarcia okna logowania po nacisnieciu submit
###################################################################
    def switch_windows():
        change_password.destroy()
        login_window.deiconify()

###################################################################
# funkcja sprawdzajaca poprawnosc hasla
###################################################################
    def check_password_validity(password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            error_label.configure(text=tlumaczenie["Password_requirements"])
            return False

###################################################################
# funkcja odpowiedzialna za przycisk "submit"
###################################################################
    def on_click():
        new_password = password.get()
        if check_password_validity(new_password):
            if check_password_match():
                result = Baza.reset_user_password(username, new_password)
                if result["success"]:
                    show_confirmation_window()
                    password.configure(state="disabled")
                    confirm_password.configure(state="disabled")
                else:
                    error_label.configure(text=result["message"], text_color="red")
        else:
            error_label.configure(text=tlumaczenie["Invalid_password"], text_color="red")

    def check_password_match():
        if password.get() == confirm_password.get():
            return True
        else:
            error_label.configure(text=tlumaczenie["Passwords_do_not_match"], text_color="red")
            return False

###################################################################
# checkbox wyswietlajacy haslo
###################################################################
    def show_password():
        if password.cget("show") == "*" or confirm_password.cget("show") == "*":
            password.configure(show="")
            confirm_password.configure(show="")
        else:
            password.configure(show="*")
            confirm_password.configure(show="*")

###################################################################
# funkcja sprawdzajaca czy pola nie sa puste
###################################################################
    def check_password():
        if password.get() == "" or confirm_password.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

###################################################################
# dodatkowe okno z potwierdzeniem zmian hasla
###################################################################
    def show_confirmation_window():
        confirmation_window = ctk.CTkToplevel(change_password)
        confirmation_window.geometry("300x100")
        confirmation_window.title("Confirmation")

        confirmation_label = ctk.CTkLabel(confirmation_window, 
            text=tlumaczenie["Changed"], 
            width=250, 
            height=30)
        
        confirmation_button = ctk.CTkButton(confirmation_window, 
            text="OK", 
            command=lambda: confirmation_window.after(100, on_ok_click, confirmation_window))

        confirmation_label.pack(pady=10)
        confirmation_button.pack(pady=10)

        change_password.attributes("-disabled", True)
        confirmation_window.protocol("WM_DELETE_WINDOW", lambda: on_ok_click(confirmation_window))

###################################################################
# funkcja odpowiedzialna za przycisk "OK" w oknie potwierdzajac
# zamykanie okna zmiany hasla, okna potwierdzajacego i otwieranie okna logowania
###################################################################
    def on_ok_click(confirmation_window):
        confirmation_window.destroy()
        change_password.destroy()
        login_window.deiconify()

###################################################################
# definiowanie trzeciego okna
###################################################################
    change_password = ctk.CTk()
    change_password.geometry("450x200")
    change_password.title("LockBox-Forget Password")
    change_password.resizable(False, False)
    change_password.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_password, login_window))

    password = ctk.CTkEntry(change_password, 
        width=150, 
        height=30, 
        show="*", 
        placeholder_text=tlumaczenie["New_password"])
    
    confirm_password = ctk.CTkEntry(change_password, 
        width=150, 
        height=30, 
        show="*", 
        placeholder_text=tlumaczenie["Confirm_password"])
    
    submit_button = ctk.CTkButton(change_password, 
        state="disabled", 
        width=50, 
        height=30, 
        text=tlumaczenie["Submit"], 
        command=on_click)
    
    show_password = ctk.CTkCheckBox(change_password, 
        width=50, 
        height=30, 
        text=tlumaczenie["Show_password"], 
        command=show_password)
    
    error_label = ctk.CTkLabel(change_password, 
        width=450, 
        height=30, 
        text="", 
        compound="center", 
        fg_color="transparent", 
        text_color="red")

    password.place(x=65, y=40)
    confirm_password.place(x=235, y=40)
    show_password.place(x=65, y=90)
    submit_button.place(x=285, y=90)
    error_label.place(x=0, y=160)

    password.bind("<KeyRelease>", lambda event: check_password())
    confirm_password.bind("<KeyRelease>", lambda event: check_password())

    change_password.mainloop()

###################################################################
# funkcja powodujaca otwarcie okna logowania w przypadku zamkniecia ktoregokolwiek z okien
###################################################################
def on_closing(window, login_window):
    window.destroy()
    login_window.deiconify()

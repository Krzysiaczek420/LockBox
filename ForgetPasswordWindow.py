import re
import tkinter as tk
import customtkinter as ctk 
import Baza

def select_username(login_window, run_LoginPage):
    def switch_windows(username):
        select_username.destroy()
        collect_data(login_window, run_LoginPage,username)

    def check_user_in_database(username):
        user = Baza.users_collection.find_one({"username": username})
        return user is not None

    def on_click():
        user = username.get()
        if check_user_in_database(user):
            submit_button.configure(state="disabled")  # Wyłącz przycisk, aby uniknąć wielokrotnego kliknięcia
            select_username.after(100, lambda: switch_windows(user))  # Oczekaj 100ms przed przejściem do następnego okna
        else:
            clear_textboxes()
            error_label.configure(text="Username not found. Please try again.",text_color="red")
            select_username.focus_set() 
    
    def check_username(event=None):
        if username.get() == "":  # Sprawdź, czy pole nazwy użytkownika jest puste
            submit_button.configure(state="disabled")  # Wyłącz przycisk, jeśli pole jest puste
        else:
            submit_button.configure(state="normal")

    def cancel_focus(event=None):
        if event:
            widget = select_username.winfo_containing(event.x_root, event.y_root)
            if widget == select_username:
                select_username.focus_set()
            #else:
                #select_username.focus_set()

    
    def clear_textboxes():
        username.delete(0, tk.END)
        username.configure(placeholder_text="Username")
    

    select_username = ctk.CTk()
    select_username.geometry("450x200")
    select_username.title("LockBox-Forget Password")
    select_username.resizable(False, False)
    select_username.protocol("WM_DELETE_WINDOW", lambda: on_closing(select_username, login_window))
    select_username.bind("<Button-1>", cancel_focus)

    username = ctk.CTkEntry(select_username, width=150, height=30, placeholder_text="Username")
    submit_button = ctk.CTkButton(select_username,state="disabled", width=50, height=30, text="Submit", command=on_click)
    error_label = ctk.CTkLabel(select_username, width=450, height=30, text="",compound="center")

    username.place(x=120, y=75)
    submit_button.place(x=280, y=75)
    error_label.place(x=0, y=150)

    username.bind("<KeyRelease>", lambda event: check_username())
    select_username.mainloop()

def collect_data(login_window, run_LoginPage,username):
    def switch_windows():
        collect_data.destroy()
        change_password(login_window, run_LoginPage,username)

    def get_security_question():
        user = Baza.users_collection.find_one({"username": username})
        if user:
            return user.get("security_question", "")
        return ""

    def on_click():
        pin = pin_number.get()
        user_answer = answer.get()
        correct_pin = Baza.users_collection.find_one({"username": username}, {"pin_code": 1}).get("pin_code", "")
        correct_answer = Baza.users_collection.find_one({"username": username}, {"answer": 1}).get("answer", "")

        if correct_pin == pin and correct_answer == user_answer:
            submit_button.configure(state="disabled")
            collect_data.after(100, switch_windows)
        else:
            clear_textboxes()
            error_label.configure(text="Invalid PIN or Answer. Please try again.",justify="center")
            collect_data.focus_set()
        
    def check_data(event=None): 
        if (answer.get() == "" or pin_number.get() == ""):
            submit_button.configure(state="disabled")  # Wyłącz przycisk, jeśli pole jest puste
        else:
            submit_button.configure(state="normal")  

    def clear_textboxes():
        answer.delete(0, tk.END)
        answer.configure(placeholder_text="Answer")
        pin_number.delete(0, tk.END)
        pin_number.configure(placeholder_text="PIN")

    collect_data = ctk.CTk()
    collect_data.geometry("450x200")
    collect_data.title("LockBox-Forget Password")
    collect_data.resizable(False, False)
    collect_data.protocol("WM_DELETE_WINDOW", lambda: on_closing(collect_data, login_window))

    question = ctk.CTkEntry(collect_data, width=180, height=30, placeholder_text="Question")
    answer = ctk.CTkEntry(collect_data, width=150, height=30, placeholder_text="Answer")
    pin_number = ctk.CTkEntry(collect_data, width=150, height=30, placeholder_text="PIN")
    submit_button = ctk.CTkButton(collect_data, state="disabled", width=50, height=30, text="Submit", command=on_click)
    error_label = ctk.CTkLabel(collect_data, width=450, height=30, text="",text_color="red",compound="center")

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

def change_password(login_window, run_LoginPage, username):
    def switch_windows():
        change_password.destroy()
        login_window.deiconify()

    def check_password_validity(password):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            error_label.configure(text="Password must contain at least 12 characters including at least one uppercase letter, one lowercase letter, one digit, and one special character")
            return False

    def on_click():
        new_password = password.get()
        if check_password_validity(new_password):
            result = Baza.change_user_password(username, new_password)
            if result["success"]:
                show_confirmation_window()
                password.configure(state="disabled")
                confirm_password.configure(state="disabled")
            else:
                error_label.configure(text=result["message"], text_color="red")
        else:
            error_label.configure(text="New password is not valid.", text_color="red")

    def show_password():
        if password.cget("show") == "*" or confirm_password.cget("show") == "*":
            password.configure(show="")
            confirm_password.configure(show="")
        else:
            password.configure(show="*")
            confirm_password.configure(show="*")

    def check_password():
        if password.get() == "" or confirm_password.get() == "":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    def show_confirmation_window():
        confirmation_window = ctk.CTkToplevel(change_password)
        confirmation_window.geometry("300x100")
        confirmation_window.title("Confirmation")

        confirmation_label = ctk.CTkLabel(confirmation_window, text="Hasło zostało zmienione", width=250, height=30)
        confirmation_button = ctk.CTkButton(confirmation_window, text="OK", command=lambda: confirmation_window.after(100, on_ok_click, confirmation_window))

        confirmation_label.pack(pady=10)
        confirmation_button.pack(pady=10)

        change_password.attributes("-disabled", True)
        confirmation_window.protocol("WM_DELETE_WINDOW", lambda: on_ok_click(confirmation_window))

    def on_ok_click(confirmation_window):
        confirmation_window.destroy()
        change_password.destroy()
        login_window.deiconify()

    change_password = ctk.CTk()
    change_password.geometry("450x200")
    change_password.title("LockBox-Forget Password")
    change_password.resizable(False, False)
    change_password.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_password, login_window))

    password = ctk.CTkEntry(change_password, width=150, height=30, show="*", placeholder_text="New Password")
    confirm_password = ctk.CTkEntry(change_password, width=150, height=30, show="*", placeholder_text="Confirm Password")
    submit_button = ctk.CTkButton(change_password, state="disabled", width=50, height=30, text="Submit", command=on_click)
    show_password = ctk.CTkCheckBox(change_password, width=50, height=30, text="Show Password", command=show_password)
    error_label = ctk.CTkLabel(change_password, width=450, height=30, text="", compound="center", fg_color="transparent", text_color="red")

    password.place(x=65, y=40)
    confirm_password.place(x=235, y=40)
    show_password.place(x=65, y=90)
    submit_button.place(x=285, y=90)
    error_label.place(x=0, y=160)

    password.bind("<KeyRelease>", lambda event: check_password())
    confirm_password.bind("<KeyRelease>", lambda event: check_password())

    change_password.mainloop()

def on_closing(window, login_window):
    window.destroy()
    login_window.deiconify()

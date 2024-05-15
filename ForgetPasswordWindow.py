import tkinter as tk
import customtkinter as ctk 

def select_username(login_window, run_LoginPage):
    def switch_windows():
        select_username.destroy()
        collect_data(login_window, run_LoginPage)

    def on_click():
        submit_button.configure(state="disabled")  # Wyłącz przycisk, aby uniknąć wielokrotnego kliknięcia
        select_username.after(100, switch_windows)  # Oczekaj 100ms przed przejściem do następnego okna

    select_username = ctk.CTk()
    select_username.geometry("450x200")
    select_username.title("LockBox-Forget Password")
    select_username.resizable(False, False)
    select_username.protocol("WM_DELETE_WINDOW", lambda: on_closing(select_username, login_window))

    username = ctk.CTkEntry(select_username, width=150, height=30, placeholder_text="Username")
    submit_button = ctk.CTkButton(select_username, width=50, height=30, text="Submit", command=on_click)
    error_label = ctk.CTkLabel(select_username, width=300, height=30, text="")

    username.place(x=120, y=75)
    submit_button.place(x=280, y=75)
    error_label.place(x=20, y=150)

    select_username.mainloop()

def collect_data(login_window, run_LoginPage):
    def switch_windows():
        collect_data.destroy()
        change_password(login_window, run_LoginPage)

    def on_click():
        submit_button.configure(state="disabled")  # Wyłącz przycisk, aby uniknąć wielokrotnego kliknięcia
        collect_data.after(100, switch_windows)  # Oczekaj 100ms przed przejściem do następnego okna

    collect_data = ctk.CTk()
    collect_data.geometry("450x200")
    collect_data.title("LockBox-Forget Password")
    collect_data.resizable(False, False)
    collect_data.protocol("WM_DELETE_WINDOW", lambda: on_closing(collect_data, login_window))

    question = ctk.CTkEntry(collect_data, width=150, height=30, placeholder_text="Question")
    answer = ctk.CTkEntry(collect_data, width=150, height=30, placeholder_text="Answer")
    pin_number = ctk.CTkEntry(collect_data, width=150, height=30, placeholder_text="PIN")
    submit_button = ctk.CTkButton(collect_data, width=50, height=30, text="Submit", command=on_click)
    error_label = ctk.CTkLabel(collect_data, width=300, height=30, text="")

    question.place(x=65, y=50)
    answer.place(x=235, y=50)
    pin_number.place(x=235, y=100)
    submit_button.place(x=200, y=150)
    error_label.place(x=20, y=180)

    collect_data.mainloop()

def change_password(login_window, run_LoginPage):
    def switch_windows():
        change_password.destroy()
        login_window.deiconify()

    def on_click():
        submit_button.configure(state="disabled")  # Wyłącz przycisk, aby uniknąć wielokrotnego kliknięcia
        change_password.after(100, switch_windows)  # Oczekaj 100ms przed przejściem do następnego okna

    change_password = ctk.CTk()
    change_password.geometry("450x200")
    change_password.title("LockBox-Forget Password")
    change_password.resizable(False, False)
    change_password.protocol("WM_DELETE_WINDOW", lambda: on_closing(change_password, login_window))

    password = ctk.CTkEntry(change_password, width=150, height=30, placeholder_text="New Password")
    confirm_password = ctk.CTkEntry(change_password, width=150, height=30, placeholder_text="Confirm Password")
    submit_button = ctk.CTkButton(change_password, width=50, height=30, text="Submit", command=on_click)
    error_label = ctk.CTkLabel(change_password, width=300, height=30, text="")

    password.place(x=65, y=50)
    confirm_password.place(x=235, y=50)
    submit_button.place(x=200, y=100)
    error_label.place(x=20, y=150)

    change_password.mainloop()

def on_closing(window, login_window):
    window.destroy()
    login_window.deiconify()

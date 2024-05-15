import tkinter as tk
import customtkinter as ctk 
#import LoginPage as loginPage


def select_username(login_window, run_LoginPage):
    select_username = ctk.CTk()
    select_username.geometry("450x200")
    select_username.title("LockBox-Forget Password")
    select_username.resizable(False, False)
    
    def switch_windows():
        select_username.withdraw()  
        collect_data(login_window, run_LoginPage)  # Wyświetla okno 2

    def on_click():
        print("clicked")
        select_username.after(100, lambda: switch_windows())

    # def on_closing():
    #     select_username.destroy()
    #     run_login_page()
    def on_closing():
        if select_username:
            try:
                select_username.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
            except tk.TclError:
                pass

    select_username.protocol("WM_DELETE_WINDOW", on_closing)

    username = ctk.CTkEntry(select_username, 
        width=150, 
        height=30, 
        placeholder_text="Username")
    submit_button = ctk.CTkButton(select_username,
        width=50,
        height=30,
        text="Submit",
        command=on_click)
    error_label = ctk.CTkLabel(select_username,
        width=300,
        height=30,
        text="")
    
    username.place(x=120, y=75)
    submit_button.place(x=280, y=75)
    error_label.place(x=20, y=150)
    select_username.mainloop()

def collect_data(login_window, run_LoginPage):
    collect_data = ctk.CTk()
    collect_data.geometry("450x200")
    collect_data.title("LockBox-Forget Password")
    collect_data.resizable(False, False)

    def switch_windows():
        collect_data.withdraw()  
        change_password(login_window, run_LoginPage)  

    def on_click():
        print("clicked")
        collect_data.after(100, lambda: switch_windows())

    # def on_closing_collect_data():
    #     collect_data.destroy()
    #     run_login_page()
    def on_closing_collect_data():
        if collect_data:
            try:
                collect_data.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
            except tk.TclError:
                pass

    collect_data.protocol("WM_DELETE_WINDOW", on_closing_collect_data)

    question = ctk.CTkEntry(collect_data, 
        width=150, 
        height=30, 
        placeholder_text="")
    
    answer = ctk.CTkEntry(collect_data, 
        width=150, 
        height=30, 
        placeholder_text="Answer")
    
    pin_number = ctk.CTkEntry(collect_data, 
        width=150, 
        height=30, 
        placeholder_text="PIN")
    
    submit2_button = ctk.CTkButton(collect_data,
        width=50,
        height=30,
        text="Submit",
        command=on_click) 
    
    error_label = ctk.CTkLabel(collect_data,
        width=300,
        height=30,
        text="")
    
    pin_label = ctk.CTkLabel(collect_data,
        width=50,
        height=30,
        text="Podaj PIN")
    
    question.place(x=65, y = 50)
    answer.place(x=235, y = 50)
    pin_number.place(x=235, y=100)
    pin_label.place(x=100, y=100)
    submit2_button.place(x=200, y=150)
    error_label.place(x=20, y=180)
    collect_data.mainloop()


def change_password(login_window, run_LoginPage):
    change_password = ctk.CTk()
    change_password.geometry("450x200")
    change_password.title("LockBox-Forget Password")
    change_password.resizable(False, False)

    # def on_closing_change_password():
    #     change_password.destroy()
    #     run_login_page()

    def on_closing_change_password():
        if change_password and change_password.winfo_exists():
            try:
                # change_password.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
                    change_password.destroy()
            except tk.TclError:
                pass

    change_password.protocol("WM_DELETE_WINDOW", on_closing_change_password)

    password = ctk.CTkEntry(change_password, 
        width=150, 
        height=30, 
        placeholder_text="password",)
    
    confirm_password = ctk.CTkEntry(change_password, 
        width=150, 
        height=30, 
        placeholder_text="confirm password")
    
    submit2_button = ctk.CTkButton(change_password,
        width=50,
        height=30,
        text="Submit") 
    
    error_label = ctk.CTkLabel(change_password,
        width=300,
        height=30,
        text="")
    password.place(x=65, y = 50)
    confirm_password.place(x=235, y = 50)
    submit2_button.place(x=200, y=100)
    error_label.place(x=20, y=150)
    change_password.mainloop()




    # username.place(x=120, y=75)
    # submit_button.place(x=280, y=75)
    # error_label.place(x=20, y=150)
    # select_username.mainloop()

    # question.place(x=65, y = 50)
    # answer.place(x=235, y = 50)
    # pin_number.place(x=235, y=100)
    # pin_label.place(x=100, y=100)
    # submit2_button.place(x=200, y=150)
    # error_label.place(x=20, y=180)
    # collect_data.mainloop()

    # password.place(x=65, y = 50)
    # confirm_password.place(x=235, y = 50)
    # submit2_button.place(x=200, y=100)
    # error_label.place(x=20, y=150)
    # change_password.mainloop()

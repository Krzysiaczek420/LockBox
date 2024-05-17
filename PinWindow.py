import customtkinter as ctk
import tkinter as tk
import random
import string

def generate_random_pin():
    return ''.join(random.choices(string.digits, k=9))

def pin_window(register_window, login_window,pin_value):
    pin_window = ctk.CTk()
    pin_window.geometry("450x200")
    pin_window.title("LockBox-Pin")
    pin_window.resizable(False, False)

    #pin_value = generate_random_pin()

    def on_closing():
        if pin_window:
            try:
                if hasattr(pin_window, "_after_id"):
                    pin_window.after_cancel(pin_window._after_id)
                if register_window and register_window.winfo_exists():
                    register_window.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
                pin_window.destroy()
            except tk.TclError:
                pass

    def ok_button_press():
        #on_closing()
        pin_window.after(200, on_closing)
    def copy_button_press():
        pin_entry.clipboard_clear()
        pin_entry.clipboard_append(pin_value)
        info_label.configure(text="PIN copied to clipboard")

    pin_window.protocol("WM_DELETE_WINDOW", on_closing)

    pin_label = ctk.CTkLabel(pin_window, text="Your PIN is:\n PIN code is nessesery in password recovery", width=450, height=60,compound="center")
    #pin_label.place(x=250, y=180)

    pin_entry = ctk.CTkEntry(pin_window, width=150, height=30)
    pin_entry.insert(0, pin_value)
    pin_entry.configure(state="readonly")
    #pin_entry.place(x=265, y=230)
    copy_button = ctk.CTkButton(pin_window, text="Copy", width=60, height=30, command=copy_button_press)
    ok_button = ctk.CTkButton(pin_window, text="OK", width=60, height=30, command=ok_button_press)
    info_label = ctk.CTkLabel(pin_window, text="", width=450, height=30,compound="center")

    pin_label.place(x=0, y=20)
    pin_entry.place(x=150, y=70)
    copy_button.place(x=320, y=70)
    ok_button.place(x=195, y=120)
    info_label.place(x=0, y=150)

    pin_window.mainloop()


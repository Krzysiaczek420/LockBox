import customtkinter as ctk
import tkinter as tk
import random
import string

def generate_random_pin():
    return ''.join(random.choices(string.digits, k=6))

def pin_window(register_window, login_window):
    pin_window = ctk.CTk()
    pin_window.geometry("700x500")
    pin_window.title("LockBox-Pin")
    pin_window.resizable(False, False)

    pin_value = generate_random_pin()

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

    pin_window.protocol("WM_DELETE_WINDOW", on_closing)

    pin_label = ctk.CTkLabel(pin_window, text="Your PIN is:", width=200, height=50)
    pin_label.place(x=250, y=180)

    pin_entry = ctk.CTkEntry(pin_window, width=150, height=30)
    pin_entry.insert(0, pin_value)
    pin_entry.configure(state="readonly")
    pin_entry.place(x=265, y=230)

    ok_button = ctk.CTkButton(pin_window, text="OK", width=60, height=30, command=ok_button_press)
    ok_button.place(x=320, y=300)

    pin_window.mainloop()


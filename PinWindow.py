import customtkinter as ctk
import CTkToolTip
import random

#=========================================================================
#   dodatkowe okno do pinu
#=========================================================================

def generate_random_pin():
        # Generowanie trzech 3-cyfrowych liczb
    part1 = str(random.randint(100, 999))
    part2 = str(random.randint(100, 999))
    part3 = str(random.randint(100, 999))
        # Łączenie ich z myślnikami
    return f"{part1}-{part2}-{part3}"
def pin_window(register_window, login_window):

    def copy():
        pin_text = pin_textbox.get()  # Pobranie tekstu z pola tekstowego
        pin_window.clipboard_clear()  # Wyczyść zawartość schowka
        pin_window.clipboard_append(pin_text)
        print(pin_text)


    def on_ok(register_window):
        if register_window and register_window.winfo_exists():
            register_window.destroy()

        if login_window and login_window.winfo_exists():
            login_window.deiconify()

        pin_window.destroy()


    pin_value = generate_random_pin()  # Zmieniłem nazwę zmiennej na "pin_value"
    pin_window = ctk.CTk()
    pin_window.geometry("300x150")
    pin_window.title("LockBox-Pin")
    pin_window.resizable(False, False)
    pin_label = ctk.CTkLabel(pin_window, 
        text = "PIN code, necessary for password recovery",
        width=150, 
        height=30)
    pin_textbox = ctk.CTkEntry(pin_window, 
        width=100, 
        height=30)
    copy_button = ctk.CTkButton(pin_window, 
        text="Copy",
        width = 50, 
        height=30, 
        command=copy)
    
    ok_button = ctk.CTkButton(pin_window, 
        text="Ok",
        width = 50, 
        height=30, 
        command=on_ok)


    pin_label.place(x=25, y=20)
    pin_textbox.place(x=80, y=60)
    copy_button.place(x=190, y=60)
    ok_button.place(x=125, y=100)
    pin_textbox.insert(0, pin_value)  # Zmieniłem nazwę zmiennej na "pin_value"
    pin_textbox.configure(state="readonly")
    pin_window.mainloop()


#pin_window()

import json
import customtkinter as ctk
import tkinter as tk
import random
import string
from Settings import wczytaj_ustawienia, wczytaj_tlumaczenie_modulu
################################################################
# Okno pinu po rejestracji
################################################################

################################################################
# funkcja generujaca losowy pin
################################################################
def generate_random_pin():
    return ''.join(random.choices(string.digits, k=9))

################################################################
# definiowanie okna pinu
################################################################
def pin_window(main_window,pin_value, show_login_callback):
    pin_window = ctk.CTk()
    pin_window.geometry("450x200")
    pin_window.title("LockBox-Pin")
    pin_window.resizable(False, False)
    sciezka_do_pliku = 'settings.json'

################################################################
# wczytanie ustawień i tłumaczeń
################################################################
    ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
    jezyk = ustawienia.get('language', 'en')
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'PinWindow')

    def go_back_to_login():
        for widget in main_window.winfo_children():
            widget.place_forget()
        main_window.title("Lockbox - Login")
        show_login_callback()

    def read_language_from_settings():
        with open('settings.json', 'r') as plik:
            ustawienia = json.load(plik)
        return ustawienia.get('language', 'en')

    def update_translations_in_other_windows():
        global tlumaczenie
        jezyk = read_language_from_settings()
        tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'PinWindow')

################################################################
# dzialania po zamknieciu okna
# zamyknaie okna pinu i rejestracji, otwieranie okna logowania
################################################################
    def on_closing():
        if pin_window:
            try:
                if hasattr(pin_window, "_after_id"):
                    pin_window.after_cancel(pin_window._after_id)
                pin_window.destroy()
                go_back_to_login()
            except tk.TclError:
                pass

################################################################
#funkcja odpowiedzialna za przycisk ok
# to samo co funkcja "on_closing()"
################################################################
    def ok_button_press():
        pin_window.after(200, on_closing)

################################################################
# funkcja odpowiedzialna za przycisk copy
# kopiowanie kodu do schowka
################################################################
    def copy_button_press():
        pin_entry.clipboard_clear()
        pin_entry.clipboard_append(pin_value)
        info_label.configure(text=tlumaczenie["Copied"])

    pin_window.protocol("WM_DELETE_WINDOW", on_closing)

    pin_label = ctk.CTkLabel(pin_window, 
        text=tlumaczenie["Pin_info"], 
        width=450, 
        height=60,
        compound="center")

################################################################
# widgety
################################################################
    pin_entry = ctk.CTkEntry(pin_window, 
        width=150, 
        height=30)
    pin_entry.insert(0, pin_value)
    pin_entry.configure(state="readonly")

    copy_button = ctk.CTkButton(pin_window, 
        text=tlumaczenie["Copy_PIN"], 
        width=60, 
        height=30, 
        command=copy_button_press)
    
    ok_button = ctk.CTkButton(pin_window, 
        text="OK", 
        width=60, 
        height=30, 
        command=ok_button_press)
    
    info_label = ctk.CTkLabel(pin_window, 
        text="", 
        width=450, 
        height=30,
        compound="center")

    pin_label.place(x=0, y=20)
    pin_entry.place(x=150, y=70)
    copy_button.place(x=320, y=70)
    ok_button.place(x=195, y=120)
    info_label.place(x=0, y=150)

    pin_window.mainloop()

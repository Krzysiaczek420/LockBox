import customtkinter as ctk
import tkinter as tk
import math
from datetime import datetime
from Settings import ustaw_motyw_i_kolor, wczytaj_ustawienia, wczytaj_tlumaczenie_modulu

sciezka_do_pliku = 'settings.json'
timeout_duration = 1000 * 10
warning_duration = timeout_duration - 1000 * 5
def MainWindow(window,show_login_callback, username_in):
    window.geometry("1000x700")
    window.title("LockBox")
    window.resizable(False, False)
    user = username_in

    ustawienia = wczytaj_ustawienia(sciezka_do_pliku)
    jezyk = ustawienia.get('language', 'en')
    tlumaczenie = wczytaj_tlumaczenie_modulu(jezyk, 'MainWindow')
    active = True

    for widget in window.winfo_children():
        widget.place_forget()
    
    def go_back_to_login():
        nonlocal active
        active = False
        cancel_timers()
        for widget in window.winfo_children():
            widget.place_forget()
        window.title("LockBox - Login")
        window.geometry("700x500")
        show_login_callback()

    def update_time(label):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label.configure(text=current_time)
        label.after(1000, update_time, label)
    
    def switch_to_main():
        nonlocal active
        active = True
        reset_timer()

    # warning_frame = ctk.CTkFrame(window, width=200, height=100)
    # warning_label = ctk.CTkLabel(warning_frame, text="zaraz cie wyloguje")
    # continue_button = ctk.CTkButton(warning_frame, text="continue",command=reset_timer)
    # warning_label.place(relx=0.5, rely=0.35, anchor="center")
    # continue_button.place(relx=0.5, rely=0.7, anchor="center")

    timer_id = None
    warning_timer_id = None

    def show_warning():
        nonlocal warning_frame, warning_timer_id
        warning_frame.place(relx=0.5, rely=0.5, anchor="center")
        warning_frame.lift()  # Wyśrodkowanie ramki w oknie
        warning_timer_id = window.after(warning_duration, timeout)  # Uruchom timer wylogowania

    def hide_warning():
        warning_frame.place_forget()  # Ukryj ramkę komunikatu

    def timeout():
        if active:  # Only timeout if still active
            hide_warning()  # Hide the warning frame
            go_back_to_login()
            show_logout_info()
    
    def show_logout_info():
        def accept():
            logout_frame.place_forget()
            window.grab_set()
        logout_frame = ctk.CTkFrame(window, width=200, height=100)
        logout_label = ctk.CTkLabel(logout_frame, text="wylogowano cie z powodu zbyt dlugiego czasu bez aktywnosci")
        logout_button = ctk.CTkButton(logout_frame, text="ok",command=accept)
        logout_label.place(relx=0.5, rely=0.35, anchor="center")
        logout_button.place(relx=0.5, rely=0.7, anchor="center")
        logout_frame.place(relx=0.5, rely=0.5, anchor="center")
        logout_frame.grab_set()

    def reset_timer(event=None):
        if active:
            cancel_timers()  # Cancel any existing timers
            hide_warning()  # Hide the warning frame
            start_timer()  # Uruchom nowy timer

    def start_timer():
        nonlocal timer_id
        timer_id = window.after(timeout_duration, show_warning)

    def cancel_timers():
        nonlocal timer_id, warning_timer_id
        if timer_id:
            window.after_cancel(timer_id)  # Cancel the timeout timer
        if warning_timer_id:
            window.after_cancel(warning_timer_id)  # Cancel the warning timer


    timer_id = window.after(timeout_duration, show_warning)

    window.bind_all("<Any-KeyPress>", reset_timer)
    window.bind_all("<Button>", reset_timer)

    warning_frame = ctk.CTkFrame(window, width=200, height=100)
    warning_label = ctk.CTkLabel(warning_frame, text="zaraz cie wyloguje")
    continue_button = ctk.CTkButton(warning_frame, text="continue",command=reset_timer)
    warning_label.place(relx=0.5, rely=0.35, anchor="center")
    continue_button.place(relx=0.5, rely=0.7, anchor="center")

    def logout():
        dialog_frame = ctk.CTkFrame(window, width=200, height=100)
        dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
        dialog_frame.grab_set()

        close_label = ctk.CTkLabel(dialog_frame, width=200, text="wyloguj",anchor="center")
        close_label.place(x=0, y=15)

        # Funkcja do zamknięcia aplikacji
        def confirm_close():
            go_back_to_login()
            window.grab_set()

        # Funkcja do anulowania zamknięcia
        def cancel_close():
            dialog_frame.destroy()
            window.grab_set()

        yes_button = ctk.CTkButton(dialog_frame, width=50, height=30, text="yes", command=confirm_close)
        no_button = ctk.CTkButton(dialog_frame, width=50, height=30, text="no", command=cancel_close)

        yes_button.place(x=25, y=60)
        no_button.place(x=125, y=60)

    sidebar = ctk.CTkFrame(window, width=200, height=670, corner_radius=0)
    logout = ctk.CTkButton(sidebar, width=150,text="Logout", command=logout)
    logout.place(x=25, y=500)
    info_frame = ctk.CTkFrame(window, width=1000, height=30, corner_radius=0)

    hello_label = ctk.CTkLabel(sidebar, width=200, height=80, text=f"{tlumaczenie["Hello"]} \n{user}", font=("default", 24))
    time_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="right")
    info_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="left")
    pages_label = ctk.CTkLabel(window, text="")

    # Ustawienie głównej ramki na zawartość
    content_frame = ctk.CTkFrame(window, width=700, height=600)
    content_frame.place(x=250, y=30)

    sidebar.place(x=0, y=0)
    info_frame.place(x=0, y=670)
    hello_label.place(x=0, y=25)
    time_label.place(x=860, y=0)
    info_label.place(x=20, y=0)
    pages_label.place(x=760, y=640)

    update_time(time_label)  # Rozpoczęcie aktualizacji czasu

    # Funkcja tworzenia poszczególnych elementów
    def create_item_frame(parent, index):
        frame = ctk.CTkFrame(parent, width=670, height=185, border_width=2, border_color="black")
        system_label = ctk.CTkLabel(frame, text="system", width=40, height=20, anchor="w")
        system = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        login_label = ctk.CTkLabel(frame, text="login", width=100, height=20, anchor="w")
        haslo_label = ctk.CTkLabel(frame, text="haslo", width=100, height=20, anchor="w")
        note_label = ctk.CTkLabel(frame, text="note", width=100, height=15, anchor="w")
        login = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        copy = ctk.CTkButton(frame, text="copy password", width=100)
        delete = ctk.CTkButton(frame, text="delete", width=100)
        edit = ctk.CTkButton(frame, text="edit", width=100)
        show_pw = ctk.CTkButton(frame, width=100, text="pokaz haslo")
        haslo = ctk.CTkEntry(frame, width=230, height=30, show="*", border_width=0, fg_color=("#FF0000", "#1D1E1E"))

        def toggle_password():
            if haslo.cget("show") == "*":
                haslo.configure(show="")
                show_pw.configure(text="ukryj haslo")
            else:
                haslo.configure(show="*")
                show_pw.configure(text="pokaz haslo")

        show_pw.configure(command=toggle_password)

        note = ctk.CTkTextbox(frame, width=260, height=140)
        system_label.place(x=30, y=5)
        system.place(x=20, y=25)
        login_label.place(x=30, y=60)
        login.place(x=20, y=80)
        haslo_label.place(x=30, y=115)
        haslo.place(x=20, y=135)
        note_label.place(x=285, y=6)
        note.place(x=275, y=25)
        copy.place(x=550, y=20)
        edit.place(x=550, y=60)
        delete.place(x=550, y=100)
        show_pw.place(x=550, y=140)

        return frame

    # Konfiguracja stronicowania i tworzenie elementów
    items_per_page = 3
    current_page = 0
    total_items = 4
    item_frames = []
    max_pages = math.ceil(total_items / items_per_page)

    def print_current_page_info(current_page, max_pages):
        if pages_label and pages_label.winfo_exists():
            pages_label.configure(text=f"Current page: {current_page + 1}/{max_pages}")

    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i)
        item_frames.append(item_frame)

    # Funkcja wyświetlania strony
    def show_page(page):
        top_y_position = 10
        x_position = 15

        for item_frame in item_frames:
            item_frame.place_forget()

        for i in range(page * items_per_page, min((page + 1) * items_per_page, total_items)):
            item_frame = item_frames[i]
            item_frame.place(x=x_position, y=top_y_position, in_=content_frame)
            top_y_position += 200

    def next_page():
        nonlocal current_page
        if (current_page + 1) * items_per_page < total_items:
            current_page += 1
            show_page(current_page)
            print_current_page_info(current_page, max_pages)
            unblock_buttons()

    def prev_page():
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            show_page(current_page)
            print_current_page_info(current_page, max_pages)
            unblock_buttons()

    def block_buttons():
        prev_button.configure(state='disabled')
        next_button.configure(state='disabled')

    def unblock_buttons():
        if current_page == 0 and max_pages==1:
            prev_button.configure(state='disabled')
            next_button.configure(state='disabled')
        elif current_page == 0 and max_pages!=1:
            prev_button.configure(state='disabled')
            next_button.configure(state='normal')
        elif (current_page + 1) * items_per_page >= total_items:
            prev_button.configure(state='normal')
            next_button.configure(state='disabled')
        else:
            prev_button.configure(state='normal')
            next_button.configure(state='normal')

    prev_button = ctk.CTkButton(window, text="<", width=20, height=20, command=prev_page)
    next_button = ctk.CTkButton(window, text=">", width=20, height=20, command=next_page)

    prev_button.place(x=895, y=640)
    next_button.place(x=925, y=640)

    def show_first_page():
        top_y_position = 10
        x_position = 15
        for i in range(min(items_per_page, total_items)):
            item_frame = item_frames[i]
            item_frame.place(x=x_position, y=top_y_position, in_=content_frame)
            top_y_position += 200

    unblock_buttons()
    show_first_page()
    print_current_page_info(current_page, max_pages)

import random
import string
import customtkinter as ctk
import Database as db
from Database import get_user_systems
import tkinter as tk
import math
from datetime import datetime
from Settings import load_setting, load_translation

sciezka_do_pliku = 'settings.json'
timeout_duration = 1000 * 90
warning_duration = timeout_duration - 1000 * 60

#########################################################
# funkcja odpowiedzialna za glowne okno aplikacji
# (wszystko co widzimy po zalogowaniu)
#########################################################
def MainWindow(window,show_login_callback, username_in):
    window.geometry("1000x700")
    window.title("LockBox")
    window.resizable(False, False)
    user = username_in
    ustawienia = load_setting(sciezka_do_pliku)
    jezyk = ustawienia.get('language', 'en')
    tlumaczenie = load_translation(jezyk, 'MainWindow')
    active = True
    timer_id = None
    warning_timer_id = None
    systems_list = get_user_systems(username_in)
    filtered_list = systems_list
    search_timer_id = None

    for widget in window.winfo_children():
        widget.place_forget()

    loading_frame = ctk.CTkFrame(window, fg_color="transparent", width=10000, height=7000)
    loading_frame.place(x=0, y=0)

    def remove_loading_frame():
        loading_frame.destroy()

#########################################################
# funkcja do anulowania focusu
#########################################################
    def cancel_focus(event):
        if not isinstance(event.widget, (tk.Text, tk.Entry)):
            window.focus_force()

#########################################################
# funkcja zmieniajaca zawartosc labelu informacyjnego
#########################################################
    def info_label_change(text):
        info_label.configure(text=text)
        info_label.after(10000, lambda: info_label.configure(text=""))

#########################################################
# funkcja wylogowywania
#########################################################
    def go_back_to_login():
        nonlocal active
        active = False
        cancel_timers()
        for widget in window.winfo_children():
            widget.place_forget()
        window.title("LockBox - Login")
        window.geometry("700x500")
        window.focus_force()
        show_login_callback()

#########################################################
# funkcja do pokazywania ostrzerzenia przed automatycznym wylogowaniem
#########################################################
    def show_warning():
        nonlocal warning_frame, warning_timer_id
        warning_frame.place(relx=0.5, rely=0.5, anchor="center")
        warning_frame.lift()
        warning_timer_id = window.after(warning_duration, timeout)

#########################################################
# funkcja do ukrywania ostrzerzenia
#########################################################
    def hide_warning():
        warning_frame.place_forget()

#########################################################
# funkcja do automatycznego wylogowywania przez brak aktywnosci
#########################################################
    def timeout():
        if active:
            hide_warning()
            go_back_to_login()
            show_logout_info()

#########################################################
# funkcja do wyswietlania informacji o tym ze nastapilo wylogowanie z powodu braku aktywnosci
#########################################################
    def show_logout_info():
        def accept():
            logout_frame.place_forget()
            window.grab_set()
        logout_frame = ctk.CTkFrame(window,border_width=2, width=200, height=100)
        logout_label = ctk.CTkLabel(logout_frame, width=196,wraplength=196, text=tlumaczenie['Logout_info'])
        logout_button = ctk.CTkButton(logout_frame, text="Ok",command=accept)
        logout_label.place(relx=0.5, rely=0.3, anchor="center")
        logout_button.place(relx=0.5, rely=0.7, anchor="center")
        logout_frame.place(relx=0.5, rely=0.5, anchor="center")
        logout_frame.grab_set()

#########################################################
# funkcja do resetowania timera ktory odlicza czas do wylogowania
#########################################################
    def reset_timer(event=None):
        if active:
            cancel_timers()
            hide_warning()
            start_timer()
    window.bind_all("<Any-KeyPress>", reset_timer)
    window.bind_all("<Button>", reset_timer)
#########################################################
# funkcja uruchamiajaca timer
#########################################################
    def start_timer():
        nonlocal timer_id
        timer_id = window.after(timeout_duration, show_warning)

#########################################################
# funkcja wylaczajaca timery po wylogowaniu
#########################################################
    def cancel_timers():
        nonlocal timer_id, warning_timer_id
        if timer_id:
            window.after_cancel(timer_id)
        if warning_timer_id:
            window.after_cancel(warning_timer_id)

#########################################################
# funkcja aktualizujaca czas (wyswietlanie godziny)
#########################################################
    def update_time(label):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label.configure(text=current_time)
        label.after(1000, update_time, label)
    timer_id = window.after(timeout_duration, show_warning)

#########################################################
# definicja ramki z ostrzezeniem o planowanym automatycznym wylogowaniem
#########################################################
    warning_frame = ctk.CTkFrame(window, border_width=2, width=200, height=100)
    warning_label = ctk.CTkLabel(warning_frame, width=196, wraplength=196, height=30, text=tlumaczenie["Warning_label"])
    continue_button = ctk.CTkButton(warning_frame, text=tlumaczenie["Continue"],command=reset_timer)
    warning_label.place(relx=0.5, rely=0.32, anchor="center")
    continue_button.place(relx=0.5, rely=0.75, anchor="center")

#########################################################
# funkcja do wylogowywania
#########################################################
    def logout():
        dialog_frame = ctk.CTkFrame(window, width=200, height=100,border_width=2)
        dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
        dialog_frame.grab_set()

        close_label = ctk.CTkLabel(dialog_frame, width=196, text="wyloguj",anchor="center")
        close_label.place(x=2, y=15)

        # potwierdzenie wylogowania
        def confirm_logout():
            go_back_to_login()
            window.grab_set()

        # anulowanie wylogowania
        def cancel_logout():
            dialog_frame.destroy()
            window.grab_set()

        yes_button = ctk.CTkButton(dialog_frame, width=50, height=30, text="yes", command=confirm_logout)
        no_button = ctk.CTkButton(dialog_frame, width=50, height=30, text="no", command=cancel_logout)

        yes_button.place(x=25, y=60)
        no_button.place(x=125, y=60)

#########################################################
# funkcja do tworzenia ramek(frame)ktore wyskakuja w momencie wybrania
# funkcji do dodawania witryn, funkcji do edytowania
# ustawień, generatora i strongness_checkera
# poniewaz wszystkie te ramki maja być takie same tylko zawartosc ma sie różnic
#########################################################
    def side_frame():
        frame = ctk.CTkFrame(window, width=400, height=676,border_width=2, corner_radius=20)
        frame.place(x=176, y=-2)
        sidebar.lift()
        info_frame.lift()
        return frame

#########################################################
# funkcja do dodawania witryn/aplikacji
#########################################################
    def add_system():
        add_frame = side_frame()

        def cancel_add():
            add_frame.place_forget()

        # dzialania po nacisnieciu guzika "save"
        def save_system():
            nonlocal filtered_list
            system_name = system_entry.get("1.0", "end-1c")
            login = login_entry.get("1.0", "end-1c")
            password = password_entry.get("1.0", "end-1c")
            note = note_entry.get("1.0", "end-1c")

            if not system_name or not login or not password:
                error_label.configure(text="Wszystkie pola są wymagane!")
                return
            
            existing_system = db.check_existing_system(user, system_name, login)

            if existing_system:
                error_label.configure(text="System z tą nazwą i loginem już istnieje!")
                return

            result = db.add_system_for_user(user, system_name, login, password, note)

            if result["success"]:
                systems_list = get_user_systems(user)
                filtered_list = systems_list
                add_frame.place_forget()
                search_systems()  
                info_label_change("System został dodany pomyślnie!")
            else:
                error_label.configure(text="Błąd podczas dodawania systemu!")

        system_label = ctk.CTkLabel(add_frame, text="System Name:")
        system_label.place(x=44, y=20)
        system_entry = ctk.CTkTextbox(add_frame, width=200, height=30)
        system_entry.place(x=174, y=20)

        login_label = ctk.CTkLabel(add_frame, text="Login:")
        login_label.place(x=44, y=60)
        login_entry = ctk.CTkTextbox(add_frame, width=200, height=30)
        login_entry.place(x=174, y=60)

        password_label = ctk.CTkLabel(add_frame, text="Password:")
        password_label.place(x=44, y=100)
        password_entry = ctk.CTkTextbox(add_frame, width=200, height=30)
        password_entry.place(x=174, y=100)

        note_label = ctk.CTkLabel(add_frame, text="Note:")
        note_label.place(x=44, y=140)
        note_entry = ctk.CTkTextbox(add_frame, width=200, height=100)
        note_entry.place(x=174, y=140)

        error_label = ctk.CTkLabel(add_frame, text="", text_color="red")
        error_label.place(x=174, y=250)

        save_button = ctk.CTkButton(add_frame, width=75, text="Save", command=save_system)
        save_button.place(x=174, y=300)

        cancel_button = ctk.CTkButton(add_frame, width=75, text="Cancel", command=cancel_add)
        cancel_button.place(x=274, y=300)

#########################################################
# funkcja do generowania haseł losowych
#########################################################
    def password_generator():
        def cancel():
            generator_frame.place_forget()

        def copy():
            content = output.get("0.0", ctk.END)  # Pobiera zawartość z CTkEntry
            window.clipboard_clear()  # Czyści schowek
            window.clipboard_append(content)
            info_label_change("losowe hasło skopiowano do schowka.")  # Dodaje zawartość do schowka
            window.update()

        def generate(single_run=False):
            # Pobieranie wybranych opcji
            include_upper = upper_case_letters.get()
            include_lower = lower_case_letters.get()
            include_special = special_characters.get()
            include_numbers = numbers.get()

            # Pobieranie długości hasła
            length = int(lenght_slider.get())

            # Tworzenie zestawu znaków na podstawie zaznaczonych checkboxów
            charset = ""
            if include_upper:
                charset += string.ascii_uppercase
            if include_lower:
                charset += string.ascii_lowercase
            if include_special:
                charset += string.punctuation
            if include_numbers:
                charset += string.digits

            # Funkcja do generowania hasła i wyświetlania ich w serii
            if charset:
                def generate_password_with_delay(count=50):
                    if count > 0 and not single_run:
                        # Generowanie losowego hasła
                        password = ''.join(random.choice(charset) for _ in range(length))
                        output.delete("0.0", ctk.END)
                        output.insert(ctk.END, password)
                        # Generowanie kolejnego hasła po 50ms
                        generator_frame.after(10, generate_password_with_delay, count - 1)
                    else:
                        # Wyświetlanie finalnego hasła
                        final_password = ''.join(random.choice(charset) for _ in range(length))
                        output.delete("0.0", ctk.END)
                        output.insert(ctk.END, final_password)

                generate_password_with_delay()
            else:
                output.delete("0.0", ctk.END)
                output.insert(ctk.END, "Select options")

        def sync_slider_to_text(event=None):
            lenght_value.delete(0, ctk.END)
            lenght_value.insert(ctk.END, str(int(lenght_slider.get())))
            auto_generate()

        def sync_text_to_slider(event=None):
            try:
                value = int(lenght_value.get())
                value = max(1, min(64, value))  # Ograniczenie do przedziału 1-64
                lenght_slider.set(value)
                auto_generate()
            except ValueError:
                lenght_slider.set(1)

        def clear_text(event):
            lenght_value.delete(0, ctk.END)

        # Ramka generatora
        generator_frame = side_frame()

        # Checkboxy
        upper_case_letters = ctk.CTkCheckBox(generator_frame, text="upper case letters", width=150, height=30, onvalue=1, offvalue=0)
        lower_case_letters = ctk.CTkCheckBox(generator_frame, text="lower case letters", width=150, height=30, onvalue=1, offvalue=0)
        special_characters = ctk.CTkCheckBox(generator_frame, text="special characters", width=150, height=30, onvalue=1, offvalue=0)
        numbers = ctk.CTkCheckBox(generator_frame, text="numbers", width=150, height=30, onvalue=1, offvalue=0)

        # Domyślnie zaznaczone checkboxy
        upper_case_letters.select()
        lower_case_letters.select()
        special_characters.select()
        numbers.select()

        # Suwak i pole tekstowe długości
        lenght_slider = ctk.CTkSlider(generator_frame, width=200, height=20, from_=1, to=64, number_of_steps=63, command=sync_slider_to_text)
        lenght_slider.set(16)

        lenght_value = ctk.CTkEntry(generator_frame, width=50, height=30)
        lenght_value.insert(0, "16")
        lenght_value.bind("<KeyRelease>", sync_text_to_slider)
        lenght_value.bind("<FocusIn>", clear_text)

        # Pole wyjściowe
        output = ctk.CTkTextbox(generator_frame, width=250, height=30)

        # Przyciski
        cancel_button = ctk.CTkButton(generator_frame, width=75, height=30, text="Cancel", command=cancel)
        copy_button = ctk.CTkButton(generator_frame, width=75, height=30, text="Copy",command=copy)
        regenerate_button = ctk.CTkButton(generator_frame, width=75, height=30, text="Re-generate", command=lambda: generate(single_run=False))

        # Ustawianie elementów
        x = 44
        upper_case_letters.place(x=x, y=20)
        lower_case_letters.place(x=x, y=70)
        special_characters.place(x=x, y=120)
        numbers.place(x=x, y=170)
        lenght_slider.place(x=x, y=220)
        lenght_value.place(x=x + 210, y=215)
        output.place(x=x, y=270)
        cancel_button.place(x=x, y=320)
        copy_button.place(x=x + 100, y=320)
        regenerate_button.place(x=x + 200, y=320)

        # Zmienna do śledzenia zaplanowanego zadania
        pending_task = None

        # Funkcja automatycznego generowania serii haseł
        def auto_generate(event=None):
            nonlocal pending_task
            if pending_task is not None:
                generator_frame.after_cancel(pending_task)
            pending_task = generator_frame.after(250, generate)

        # Przypisanie funkcji auto_generate do elementów interfejsu
        upper_case_letters.configure(command=auto_generate)
        lower_case_letters.configure(command=auto_generate)
        special_characters.configure(command=auto_generate)
        numbers.configure(command=auto_generate)
        lenght_slider.configure(command=lambda v: [sync_slider_to_text(), auto_generate()])

        # Pierwsze jednorazowe generowanie hasła
        generate(single_run=True)

#########################################################
# funkcja do cyszczenia pola wyszukiwania
#########################################################
    def clear_search():
        search_input.delete(0, 'end')
        search_input.configure(placeholder_text="Search")
        on_search_input_change(None)
#########################################################
# definicja pola bocznego, pola informacyjnego, informacji o stronach, ramki systemow 
#########################################################
    sidebar = ctk.CTkFrame(window, width=200, height=672, corner_radius=0)
    sidebar.place(x=0, y=0)
    info_frame = ctk.CTkFrame(window, width=1000, height=30, corner_radius=0)
    info_frame.place(x=0, y=670)
    pages_label = ctk.CTkLabel(window, text="")
    pages_label.place(x=735, y=635)

    time_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="right")
    info_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="left")
    info_label.place(x=20, y=0)
    time_label.place(x=860, y=0)

    content_frame = ctk.CTkFrame(window, width=700, height=600)
    content_frame.place(x=250, y=30)
    no_systems_label = ctk.CTkLabel(content_frame, width = 700, height = 50, text = "brak systemów")

    hello_label = ctk.CTkLabel(sidebar, width=200, height=80, text=f"{tlumaczenie["Hello"]} \n{user}", font=("default", 24))
    search_input = ctk.CTkEntry(sidebar, width=150, height=30, placeholder_text="Search")
    clear_button = ctk.CTkButton(sidebar, width=150, height=30, text="clear",command=clear_search)
    logout = ctk.CTkButton(sidebar, width=150,text="Logout", command=logout)
    add_system_button = ctk.CTkButton(sidebar, width=150, text="Add System", command=add_system)
    sort_label = ctk.CTkLabel(sidebar, width=150, anchor="w", height=30, text="Sort by:")
    settings_button = ctk.CTkButton(sidebar, width=150, height=30, text="settings")
    generator_button = ctk.CTkButton(sidebar, width=150, height=30, text="password generator", command=password_generator)
    strongness_checker_button = ctk.CTkButton(sidebar, width=150, height=30, text="strongness checker")

    sidebar.place(x=0, y=0)
    hello_label.place(x=0, y=35)
    search_input.place(x=25, y=150) 
    clear_button.place(x=25, y=190) #220
    add_system_button.place(x=25, y=255) #285
    generator_button.place(x=25, y=320) #350
    strongness_checker_button.place(x=25, y=370) #400
    sort_label.place(x=25, y=450) #480+30=510
    settings_button.place(x=25, y=565) #590
    logout.place(x=25, y=615) #635

#########################################################
# pobieranie danych uzytkownika i stałe odnosnie wyswietlania danych witryn
#########################################################
    systems_list = get_user_systems(username_in)
    total_items = len(systems_list)
    items_per_page = 3
    current_page = 0
    item_frames = []
    max_pages = math.ceil(total_items / items_per_page)
    if total_items == 0:
        max_pages = 1
        no_systems_label.place(relx=0, rely=0.5)

#########################################################
# funkcja do wyszukiwania witryn po nazwie
#########################################################
    def search_systems():
        nonlocal systems_list, filtered_list, total_items, max_pages, current_page, item_frames
        systems_list = get_user_systems(user)
        filtered_list = systems_list

        search_text = search_input.get().strip().lower()
        filtered_list = [
            system for system in systems_list
            if search_text in system['system_name'].lower()
        ]
        selected_option = sort_combobox.get()
        sort_systems(selected_option)
        total_items = len(filtered_list)
        max_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        current_page = 0

        refresh_systems()

#########################################################
# dzialania po rozpoczeciu wpisywania w pole wyszukiwania
#########################################################
    def on_search_input_change(event):
        nonlocal search_timer_id, filtered_list 
        systems_list = get_user_systems(user)  # Fetch updated list
        filtered_list = systems_list
        if search_timer_id:
            window.after_cancel(search_timer_id)
        search_timer_id = window.after(250, search_systems)

    search_input.bind("<KeyRelease>", on_search_input_change)
#########################################################
# funkcja do sortowania wynikow
#########################################################
    def sort_systems(selected_option):
        nonlocal filtered_list
        selected_option = sort_combobox.get()
        if selected_option == "Name (A-Z)":
            filtered_list.sort(key=lambda x: x['system_name'].casefold())
        elif selected_option == "Name (Z-A)":
            filtered_list.sort(key=lambda x: x['system_name'].casefold(), reverse=True)
        elif selected_option == "Creation Date (Oldest First)":
            filtered_list.sort(key=lambda x: x.get('creation_date', datetime.min))
        elif selected_option == "Creation Date (Newest First)":
            filtered_list.sort(key=lambda x: x.get('creation_date', datetime.min), reverse=True)
        refresh_systems()

    sort_options = [
        "Name (A-Z)",
        "Name (Z-A)",
        "Creation Date (Newest First)",
        "Creation Date (Oldest First)"
    ]
    sort_combobox = ctk.CTkComboBox(sidebar, width=150, height=30, values=sort_options,command=sort_systems)
    sort_combobox.set("Creation Date (Oldest First)")
    sort_combobox.place(x=25, y=480)
    sort_combobox.bind("<<ComboboxSelected>>", lambda: sort_systems())
#########################################################
# funkcja do odswierzania okna po jakichkolwiek zmianach(wyszukiwanie, dodawanie, usuwanie itp)
#########################################################
    def refresh_systems():
        nonlocal total_items, max_pages, current_page, item_frames

        total_items = len(filtered_list)  # Zaktualizuj liczbę elementów na podstawie przefiltrowanej listy
        max_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
        current_page = min(current_page, max_pages - 1)  # Ustaw na bieżącą stronę lub maksymalną dostępną, jeśli lista jest krótsza

        for item_frame in item_frames:
            item_frame.destroy()
        item_frames.clear()

        for i in range(total_items):
            item_frame = create_item_frame(content_frame, i, filtered_list)  # Dodajemy `filtered_list` jako argument do `create_item_frame`
            item_frames.append(item_frame)

        unblock_buttons()
        show_page(current_page)
        print_current_page_info(current_page, max_pages)

        if total_items == 0:
            no_systems_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            no_systems_label.place_forget()

#########################################################
# tworzenie kafelków z danymi witryn
#########################################################
    def create_item_frame(parent, index, display_list):
        def copy_password():
            content = haslo.get()  # Pobiera zawartość z CTkEntry
            window.clipboard_clear()  # Czyści schowek
            window.clipboard_append(content)
            info_label_change("Hasło skopiowano do schowka.")  # Dodaje zawartość do schowka
            window.update()

        #pokazywanie hasla
        def toggle_password():
            if haslo.cget("show") == "*":
                haslo.configure(show="")
                show_pw.configure(text="Ukryj hasło")
            else:
                haslo.configure(show="*")
                show_pw.configure(text="Pokaż hasło")

        # edytowanie danej witryny
        def edit_system():
            nonlocal filtered_list
            edit_frame = side_frame()

            system_data = display_list[index]
            system_name_value = system_data["system_name"]
            login_value = system_data["login"]
            password_value = system_data["password"]
            note_value = system_data["note"]

            # anulowanie edycji
            def cancel_edit():
                edit_frame.place_forget()

            # dzialania po zatwierdzeniu edycji
            def save_system():
                nonlocal filtered_list
                new_system_name = system_entry.get("1.0", "end-1c").strip()
                new_login = login_entry.get("1.0", "end-1c").strip()
                new_password = password_entry.get("1.0", "end-1c").strip()
                new_note = note_entry.get("1.0", "end-1c").strip()

                if not new_system_name or not new_login or not new_password:
                    error_label.configure(text="Wszystkie pola są wymagane!")
                    return

                update_result = db.update_user_system(
                    user, 
                    original_system_name=system_name_value, 
                    new_system_name=new_system_name,
                    new_login=new_login, 
                    new_password=new_password, 
                    new_note=new_note)

                if update_result["success"]:
                    systems_list = get_user_systems(user)  # Fetch updated list
                    filtered_list = systems_list  # Refresh filtered_list
                    edit_frame.place_forget()
                    search_systems()
                    info_label_change("System został zaktualizowany pomyślnie!")
                else:
                    error_label.configure(text="Błąd podczas aktualizacji systemu!")

            system_label = ctk.CTkLabel(edit_frame, text="System Name:")
            system_label.place(x=44, y=20)
            system_entry = ctk.CTkTextbox(edit_frame, width=200, height=30)
            system_entry.insert("0.0", system_name_value)
            system_entry.place(x=174, y=20)

            login_label = ctk.CTkLabel(edit_frame, text="Login:")
            login_label.place(x=44, y=60)
            login_entry = ctk.CTkTextbox(edit_frame, width=200, height=30)
            login_entry.insert("0.0", login_value)
            login_entry.place(x=174, y=60)

            password_label = ctk.CTkLabel(edit_frame, text="Password:")
            password_label.place(x=44, y=100)
            password_entry = ctk.CTkTextbox(edit_frame, width=200, height=30)
            password_entry.insert("0.0", password_value)
            password_entry.place(x=174, y=100)

            note_label = ctk.CTkLabel(edit_frame, text="Note:")
            note_label.place(x=44, y=140)
            note_entry = ctk.CTkTextbox(edit_frame, width=200, height=100)
            note_entry.insert("0.0", note_value)
            note_entry.place(x=174, y=140)

            error_label = ctk.CTkLabel(edit_frame, text="", text_color="red")
            error_label.place(x=174, y=250)

            # Przycisk zapisu i anulowania
            save_button = ctk.CTkButton(edit_frame, width=75, text="Save", command=save_system)
            save_button.place(x=174, y=300)

            cancel_button = ctk.CTkButton(edit_frame, width=75, text="Cancel", command=cancel_edit)
            cancel_button.place(x=274, y=300)

        # usuwanie danej witryny
        def delete_system(index):
            system_data = display_list[index]

            confirm_frame = ctk.CTkFrame(window, width=200, height=100, border_width=2)
            confirm_frame.place(relx=0.5, rely=0.5, anchor='center')
            confirm_frame.grab_set()

            confirm_label = ctk.CTkLabel(confirm_frame, wraplength=196, width=196, text="Are you sure you want to delete this item?", anchor="center")
            confirm_label.place(x=2, y=15)
            
            # potwierdzenie usuniecia
            def confirm_deletion():
                nonlocal filtered_list
                result = db.delete_user_system(user, system_data["system_name"])
                if result.get("success"):
                    systems_list = get_user_systems(user)  # Odśwież `systems_list`
                    filtered_list = systems_list
                    refresh_systems()
                    info_label_change("System successfully deleted!")
                else:
                    info_label_change("Error deleting system.")
                    
                confirm_frame.destroy()
                window.grab_set()

            # anulowanie usuniecia
            def cancel_deletion():
                confirm_frame.destroy()
                window.grab_set()

            yes_button = ctk.CTkButton(confirm_frame, width=50, height=30, text="Yes", command=confirm_deletion)
            no_button = ctk.CTkButton(confirm_frame, width=50, height=30, text="No", command=cancel_deletion)

            yes_button.place(x=25, y=60)
            no_button.place(x=125, y=60)

        system_data = display_list[index]
        frame = ctk.CTkFrame(parent, width=670, height=185, border_width=2)

        # Tworzenie kafelkow z witrynami
        system_label = ctk.CTkLabel(frame, text="Witryna:", width=40, height=20, anchor="w")
        system = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        system.insert("0.0", system_data["system_name"])

        login_label = ctk.CTkLabel(frame, text="Login:", width=100, height=20, anchor="w")
        login = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        login.insert("0.0", system_data["login"])

        haslo_label = ctk.CTkLabel(frame, text="Hasło:", width=100, height=20, anchor="w")
        haslo = ctk.CTkEntry(frame, width=230, height=30, show="*", border_width=0, fg_color=("#FF0000", "#1D1E1E"))
        haslo.insert(0, system_data["password"])

        note_label = ctk.CTkLabel(frame, text="Notatka:", width=100, height=15, anchor="w")
        note = ctk.CTkTextbox(frame, width=260, height=140)
        if system_data["note"] == "":
            note.insert("0.0", "Brak notatki")
            note.configure(text_color="#808080")
        else:
            note.insert("0.0", system_data["note"])

        copy = ctk.CTkButton(frame, text="Skopiuj hasło", width=100, command=copy_password)
        delete = ctk.CTkButton(frame, text="Usuń", width=100, command=lambda: delete_system(index))
        edit = ctk.CTkButton(frame, text="Edytuj", width=100, command=edit_system)
        show_pw = ctk.CTkButton(frame, width=100, text="Pokaż hasło", command=toggle_password)

        # Umiejscowienie widgetów w ramce
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
        login.configure(state="disabled")
        haslo.configure(state="readonly")
        system.configure(state="disabled")
        note.configure(state="disabled")

        return frame
    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i, filtered_list)
        item_frames.append(item_frame)

#########################################################
# Funkcja wyświetlania strony
#########################################################
    def show_page(page):
        top_y_position = 10
        x_position = 15

        for item_frame in item_frames:
            item_frame.place_forget()

        for i in range(page * items_per_page, min((page + 1) * items_per_page, total_items)):
            item_frame = item_frames[i]
            item_frame.place(x=x_position, y=top_y_position, in_=content_frame)
            top_y_position += 200
#########################################################     
# funkcja do zmiany informacji odnosnie strony
#########################################################
    def print_current_page_info(current_page, max_pages):
        if pages_label and pages_label.winfo_exists():
            pages_label.configure(text=f"Current page: {current_page + 1}/{max_pages} (items: {total_items})")

    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i, filtered_list)
        item_frames.append(item_frame)

#########################################################
# funkcja do zmiany strony na nastepna
#########################################################
    def next_page():
        nonlocal current_page
        if (current_page + 1) * items_per_page < total_items:
            current_page += 1
            show_page(current_page)
            print_current_page_info(current_page, max_pages)
            unblock_buttons()

#########################################################
# funkcja do zmiany stronny na poprzednia
# ######################################################### 
    def prev_page():
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            show_page(current_page)
            print_current_page_info(current_page, max_pages)
            unblock_buttons()

#########################################################
# funkcja do zarzadzamia guzikami nawigacji zaleznie od ilosci stron 
# a takze od tego na ktorej stronie znajduje sie uzytkownik
#########################################################
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

#########################################################
# funkcja do wyswietlania pierwszej strony
#########################################################
    def show_first_page():
        top_y_position = 10
        x_position = 15
        for i in range(min(items_per_page, total_items)):
            item_frame = item_frames[i]
            item_frame.place(x=x_position, y=top_y_position, in_=content_frame)
            top_y_position += 200

    unblock_buttons()
    show_first_page()
    update_time(time_label)
    print_current_page_info(current_page, max_pages)
    window.after(500, remove_loading_frame)
    window.bind_all("<Button-1>", cancel_focus)

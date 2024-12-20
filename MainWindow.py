from concurrent.futures import ThreadPoolExecutor
import json
import random
import re
import string
import threading
import bcrypt
import customtkinter as ctk
import Database as db
from Database import change_email, change_user_password, change_username, delete_all_user_systems, delete_user, get_user_by_username, get_user_systems, toggle_2fa
import tkinter as tk
import math
from datetime import datetime
from Encryption import xor
from Mailer import send_email
from Settings import COLOR_THEMES, load_setting, load_translation, save_settings

file_path = 'settings.json'
time_to_warning = 1000 * 90
warning_time = 1000 * 60
#wylogowanie nastapuje po time_to_warning + warning_time np time_to_warning = 10 time_to_warning = 10, wyloguje po 13 sekundach
#########################################################
# funkcja odpowiedzialna za glowne okno aplikacji
# (wszystko co widzimy po zalogowaniu)
#########################################################
def MainWindow(window,show_login_callback, username_in):
    window.geometry("1000x700")
    window.title("LockBox")
    window.resizable(False, False)
    user = username_in
    app_settings = load_setting(file_path)
    language = app_settings.get('language', 'en')
    translation = load_translation(language, 'MainWindow')
    item_frames = []
    active = True
    timer_id = None
    warning_timer_id = None
    systems_list = get_user_systems(username_in)
    filtered_list = systems_list
    search_timer_id = None
    active_frame = None
    active_frame_type = None

    for widget in window.winfo_children():
        widget.place_forget()

    loading_frame = ctk.CTkFrame(window, fg_color="transparent", width=10000, height=7000)
    loading_frame.place(x=0, y=0)
    
    def remove_loading_frame():
        loading_frame.destroy()

    # def on_widget_click(event):
    #         widget = event.widget
    #         # Wyświetlenie szczegółowych informacji o każdym widgetcie
    #         print("Widget:")
    #         print(f"  Nazwa: {widget.winfo_name()}")
    #         print(f"  Typ: {widget.winfo_class()}")
    #         print(f"  Identyfikator: {widget.winfo_id()}")
    #         #print(f"  custom name: {widget.custom_name()}")

#########################################################
# funkcja do aktualizowania tłumaczeń
#########################################################
    def update_translations_main_window():
        hello_label.configure(text=f"{translation['Hello']} \n{user}")
        search_input.configure(placeholder_text=translation["Search"])
        clear_button.configure(text=translation["Clear"])
        add_system_button.configure(text=translation["Add_system"])
        generator_button.configure(text=translation["Password_generator"])
        strongness_checker_button.configure(text=translation["Strongness_checker"])
        sort_label.configure(text=translation["Sort"])
        settings_button.configure(text=translation["Settings"])
        logout.configure(text=translation["Logout"])
        no_systems_label.configure(text=translation["No_system_found"])
        sort_combobox.configure(values=[
            translation["Name(A-Z)"],
            translation["Name(Z-A)"],
            translation["Newest_first"],
            translation["Oldest_first"]])
        sort_combobox.set(translation["Oldest_first"])
        print_current_page_info(current_page, max_pages)
        refresh_systems()
        warning_label.configure(text=translation["Warning_label"])
        continue_button.configure(text=translation["Continue"])

    def refresh_widgets(root):
        for widget in root.winfo_children():
            if isinstance(widget, ctk.CTkEntry):
                if hasattr(widget, 'custom_name') and widget.custom_name == "haslo":
                    widget.configure(
                        fg_color=ctk.ThemeManager.theme["CTkTextbox"]["fg_color"],
                        text_color=ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
                else:
                    widget.configure(
                        fg_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"],
                        text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
            elif isinstance(widget, ctk.CTkTextbox) and hasattr(widget, 'custom_name') and widget.custom_name == "note":
                note_text = widget.get("0.0", "end-1c").strip()
                if not note_text or note_text == translation["No_note"]:
                    widget.configure(text_color="#808080")
                else:
                    widget.configure(text_color=ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
            elif isinstance(widget, ctk.CTkTextbox):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkTextbox"]["fg_color"],
                    text_color=ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
            elif isinstance(widget, ctk.CTkButton):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    text_color=ctk.ThemeManager.theme["CTkButton"]["text_color"],
                    hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkLabel"]["fg_color"],
                    text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkCheckBox"]["fg_color"],
                    hover_color=ctk.ThemeManager.theme["CTkCheckBox"]["hover_color"],
                    text_color=ctk.ThemeManager.theme["CTkCheckBox"]["text_color"])
            elif isinstance(widget, ctk.CTkSwitch):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkSwitch"]["fg_color"],
                    text_color=ctk.ThemeManager.theme["CTkSwitch"]["text_color"])
            elif isinstance(widget, ctk.CTkSlider):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkSlider"]["fg_color"],
                    button_color=ctk.ThemeManager.theme["CTkSlider"]["button_color"])
            elif isinstance(widget, ctk.CTkProgressBar):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkProgressBar"]["fg_color"],
                    progress_color=ctk.ThemeManager.theme["CTkProgressBar"]["progress_color"])
            elif isinstance(widget, ctk.CTkSegmentedButton):
                widget.configure(
                    fg_color=ctk.ThemeManager.theme["CTkSegmentedButton"]["fg_color"],
                    text_color=ctk.ThemeManager.theme["CTkSegmentedButton"]["text_color"])
            elif isinstance(widget, ctk.CTkScrollableFrame):
                widget.configure(
                    label_fg_color=ctk.ThemeManager.theme["CTkScrollableFrame"]["label_fg_color"])
            # Obsłuż dzieci widgetu rekurencyjnie
            if widget.winfo_children():
                refresh_widgets(widget)

#########################################################
# funkcja do anulowania focusu połączona z anulowaniem timera
#########################################################
    def cancel_focus(event):
        if not isinstance(event.widget, (tk.Text, tk.Entry)):
            window.focus_force()

    def mouse_action(event=None):
        cancel_focus(event)
        reset_timer(event)

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
            if getattr(widget, 'custom_name', None) == "dialog_frame":
                continue
            else: 
                widget.place_forget()
        window.title("LockBox - Login")
        window.geometry("700x500")
        window.focus_force()
        window.unbind_all("<Button-1>")
        window.unbind_all("<Any-KeyPress>")
        window.unbind_all("<Button>")
        
        show_login_callback()

#########################################################
# funkcja do pokazywania ostrzerzenia przed automatycznym wylogowaniem
#########################################################
    def show_warning():
        nonlocal warning_frame, warning_timer_id
        warning_frame.place(relx=0.5, rely=0.5, anchor="center")
        warning_frame.lift()
        warning_timer_id = window.after(warning_time, timeout)

#########################################################
# funkcja do ukrywania ostrzerzenia o timeoucie
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
        logout_label = ctk.CTkLabel(logout_frame, width=196,wraplength=196, text=translation['Logout_info'])
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

#########################################################
# funkcja uruchamiajaca timer
#########################################################
    def start_timer():
        nonlocal timer_id
        timer_id = window.after(time_to_warning, show_warning)

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
    timer_id = window.after(time_to_warning, show_warning)

#########################################################
# definicja ramki z ostrzezeniem o planowanym automatycznym wylogowaniem
#########################################################
    warning_frame = ctk.CTkFrame(window, border_width=2, width=200, height=100)
    warning_label = ctk.CTkLabel(warning_frame, width=196, wraplength=196, height=30, text=translation["Warning_label"])
    continue_button = ctk.CTkButton(warning_frame, text=translation["Continue"],command=reset_timer)
    warning_label.place(relx=0.5, rely=0.32, anchor="center")
    continue_button.place(relx=0.5, rely=0.75, anchor="center")

#########################################################
# funkcja do wylogowywania
#########################################################
    def logout():
        dialog_frame = ctk.CTkFrame(window, width=200, height=100,border_width=2)
        dialog_frame.place(relx=0.5, rely=0.5, anchor='center')
        dialog_frame.grab_set()

        close_label = ctk.CTkLabel(dialog_frame, width=196, wraplength=196, text=translation["Logout_question"],anchor="center")
        close_label.place(x=2, y=15)

        # potwierdzenie wylogowania
        def confirm_logout():
            go_back_to_login()
            window.grab_set()

        # anulowanie wylogowania
        def cancel_logout():
            dialog_frame.destroy()
            window.grab_set()

        yes_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=translation["Yes"], command=confirm_logout)
        no_button = ctk.CTkButton(dialog_frame, width=50, height=30, text=translation["No"], command=cancel_logout)

        yes_button.place(x=25, y=60)
        no_button.place(x=125, y=60)

#########################################################
# funkcja do tworzenia ramek(frame)ktore wyskakuja w momencie wybrania
# funkcji do dodawania witryn, funkcji do edytowania
# ustawień, generatora i strongness_checkera
# poniewaz wszystkie te ramki maja być takie same tylko zawartosc ma sie różnic
#########################################################
    def side_frame(frame_type):
        nonlocal active_frame, active_frame_type

        if active_frame and active_frame_type == frame_type:
            active_frame.place_forget()
            active_frame = None
            active_frame_type = None
            return

        if active_frame:
            active_frame.place_forget()

        frame = ctk.CTkFrame(window, width=400, height=676, border_width=2, corner_radius=20)
        frame.place(x=176, y=-2)

        active_frame = frame
        active_frame_type = frame_type

        active_frame.lift()
        sidebar.lift()
        info_frame.lift()

        return frame

#########################################################
# funkcja do dodawania witryn/aplikacji razem z funkcja do importowania z pliku .json/.txt
#########################################################
    def add_system():
        add_frame = side_frame("add_system")
        if not add_frame:
            return

        def close_add():
            nonlocal active_frame, active_frame_type
            if active_frame:
                active_frame.place_forget()
            active_frame = None
            active_frame_type = None

        def save_system():
            nonlocal filtered_list
            system_name = system_entry.get("1.0", "end-1c")
            login = login_entry.get("1.0", "end-1c")
            password = password_entry.get("1.0", "end-1c")
            note = note_entry.get("1.0", "end-1c")

            if not system_name or not login or not password:
                error_label.configure(text=translation["Requirements"])
                return
            
            existing_system = db.check_existing_system(user, system_name, login)

            if existing_system:
                error_label.configure(text=translation["Existing_system"])
                return

            result = db.add_system_for_user(user, system_name, login, password, note)

            if result["success"]:
                nonlocal active_frame, active_frame_type
                systems_list = get_user_systems(user)
                filtered_list = systems_list
                add_frame.place_forget()
                active_frame = None
                active_frame_type = None
                search_systems()
                info_label_change(translation["Added"])
            else:
                error_label.configure(text=translation["Adding_error"])
        def import_from_file():
            nonlocal filtered_list
            import tkinter.filedialog as fd

            def background_import():
                file_path = fd.askopenfilename(filetypes=[("JSON and Text files", "*.json *.txt")])
                if not file_path:
                    return
                try:
                    systems_data = []
                    if file_path.endswith(".json"):
                        with open(file_path, 'r', encoding='utf-8') as file:
                            systems_data = json.load(file)
                            if not isinstance(systems_data, list):
                                raise ValueError("Invalid JSON format: expected a list of systems.")
                    elif file_path.endswith(".txt"):
                        with open(file_path, 'r', encoding='utf-8') as file:
                            entries = file.read().strip().split(";")
                            for entry in entries:
                                parts = entry.split(",")
                                if len(parts) >= 3:
                                    systems_data.append({
                                        "system_name": parts[0].strip(),
                                        "login": parts[1].strip(),
                                        "password": parts[2].strip(),
                                        "note": parts[3].strip() if len(parts) > 3 else ""
                                    })
                    else:
                        import_error_label.configure(text=translation["Unsupported_file_format"])
                        return

                    imported_count = len(systems_data)
                    if imported_count == 0:
                        import_error_label.configure(text=translation["No_valid_systems"])
                        return

                    def add_system_to_db(system):
                        system_name = system.get("system_name", "").strip()
                        login = system.get("login", "").strip()
                        password = system.get("password", "").strip()
                        note = system.get("note", "").strip()

                        if not system_name or not login or not password:
                            return False  # Skipped due to missing data

                        existing_system = db.check_existing_system(user, system_name, login)
                        if existing_system:
                            return False  # Skipped due to existing record

                        result = db.add_system_for_user(user, system_name, login, password, note)
                        return result["success"]

                    def confirm_add():
                        nonlocal filtered_list
                        added_count = 0
                        skipped_count = 0

                        with ThreadPoolExecutor(max_workers=5) as executor:
                            results = list(executor.map(add_system_to_db, systems_data))

                        for success in results:
                            if success:
                                added_count += 1
                            else:
                                skipped_count += 1

                        systems_list = get_user_systems(user)
                        filtered_list = systems_list
                        search_systems()
                        info_label_change(translation["Import_added"].format(added=added_count, skipped=skipped_count))
                        popup.destroy()
                        close_add()

                    def cancel_import():
                        popup.destroy()

                    popup = ctk.CTkFrame(window, width=200, height=100, border_width=2)
                    popup.place(relx=0.5, rely=0.5, anchor="center")

                    message_label = ctk.CTkLabel(popup, width=196, wraplength=196, text=translation["Import_detected"].format(imported=imported_count))
                    message_label.place(x=2, y=10)

                    confirm_button = ctk.CTkButton(popup, width=50, height=30, text=translation["Yes"], command=confirm_add)
                    cancel_button = ctk.CTkButton(popup, width=50, height=30, text=translation["No"], command=cancel_import)
                    cancel_button.place(x=25, y=60)
                    confirm_button.place(x=125, y=60)

                except json.JSONDecodeError:
                    import_error_label.configure(text=translation["Invalid_json_file"])
                except Exception as e:
                    import_error_label.configure(text=translation["File_error"])
                    print(f"Error during file import: {e}")

            threading.Thread(target=background_import, daemon=True).start()
        frame = ctk.CTkFrame(add_frame, width=360, height=650)
        frame.place(x=24, y=10)

        system_label = ctk.CTkLabel(frame, text=translation["System_name"])
        system_label.place(x=20, y=20)
        system_entry = ctk.CTkTextbox(frame, width=200, height=30)
        system_entry.place(x=150, y=20)

        login_label = ctk.CTkLabel(frame, text=translation["Login"])
        login_label.place(x=20, y=60)
        login_entry = ctk.CTkTextbox(frame, width=200, height=30)
        login_entry.place(x=150, y=60)

        password_label = ctk.CTkLabel(frame, text=translation["Password"])
        password_label.place(x=20, y=100)
        password_entry = ctk.CTkTextbox(frame, width=200, height=30)
        password_entry.place(x=150, y=100)

        note_label = ctk.CTkLabel(frame, text=translation["Note"])
        note_label.place(x=20, y=140)
        note_entry = ctk.CTkTextbox(frame, width=200, height=100)
        note_entry.place(x=150, y=140)

        error_label = ctk.CTkLabel(frame,width=360, text="", text_color="red")
        error_label.place(x=0, y=285)

        save_button = ctk.CTkButton(frame, width=75, text=translation["Submit"], command=save_system)
        save_button.place(x=150, y=250)

        cancel_button = ctk.CTkButton(frame, width=75, text=translation["Cancel"], command=close_add)
        cancel_button.place(x=250, y=250)

        border = ctk.CTkFrame(frame,width=360, height=2,fg_color=["gray65","gray28"])
        border.place(x=0,y=330)

        or_label = ctk.CTkLabel(frame,width=30,height=20,text=translation["Or"],text_color=["gray75","gray38"])
        or_label.place(relx=0.5, y=320)

        import_label = ctk.CTkLabel(frame,width=190, text=translation["Import_from_file"])
        import_label.place(x=0, y=350)

        import_button = ctk.CTkButton(frame, width=150, text=translation["Import_file"], command=import_from_file)
        import_button.place(x=200, y=350)
        
        example_json_label = ctk.CTkLabel(frame,width=150,text=translation["Example_json"],anchor="w")
        example_json_label.place(x=30,y=390)

        example_json = ctk.CTkTextbox(frame,width=150, height=180,border_width=2, border_color=["gray65","gray28"])
        example_json.place(x=30, y=420)

        example_txt_label = ctk.CTkLabel(frame,width=150,text=translation["Example_txt"],anchor="w")
        example_txt_label.place(x=190,y=390)

        example_txt = ctk.CTkTextbox(frame,width=150, height=180,border_width=2, border_color=["gray65","gray28"])
        example_txt.place(x=190, y=420)

        import_error_label = ctk.CTkLabel(frame,width=360, text="", text_color="red")
        import_error_label.place(x=0, y=610)

        example_json_content = """[\n{"system_name": "...",\n"login": "...",\n"password": "...",\n"note": "..."},\n\n{"system_name": "...",\n"login": "...",\n"password": "..."}\n]"""
        example_json.insert("0.0",example_json_content)
        example_txt.insert("0.0",translation["Example_txt_content"])
        example_json.configure(state="disabled")
        example_txt.configure(state="disabled")
#########################################################
# funkcja do generowania haseł losowych
#########################################################
    def password_generator():
        def cancel():
            generator_frame.place_forget()
            nonlocal active_frame, active_frame_type
            active_frame = None
            active_frame_type = None

        def copy():
            content = output.get("0.0", ctk.END)
            window.clipboard_clear()
            window.clipboard_append(content)
            info_label_change(translation["Copied"])
            window.update()

        def generate(single_run=False):
            include_upper = upper_case_letters.get()
            include_lower = lower_case_letters.get()
            include_special = special_characters.get()
            include_numbers = numbers.get()

            length = int(lenght_slider.get())
            charset = ""
            if include_upper:
                charset += string.ascii_uppercase
            if include_lower:
                charset += string.ascii_lowercase
            if include_special:
                charset += string.punctuation
            if include_numbers:
                charset += string.digits

            if charset:
                def generate_password_with_delay(count=20):
                    if count > 0 and not single_run:
                        password = ''.join(random.choice(charset) for _ in range(length))
                        output.delete("0.0", ctk.END)
                        output.insert(ctk.END, password)
                        generator_frame.after(10, generate_password_with_delay, count - 1)
                    else:
                        final_password = ''.join(random.choice(charset) for _ in range(length))
                        output.delete("0.0", ctk.END)
                        output.insert(ctk.END, final_password)
                generate_password_with_delay()
            else:
                output.delete("0.0", ctk.END)
                output.insert(ctk.END, translation["Select_options"])

        def sync_slider_to_text(event=None):
            lenght_value.delete(0, ctk.END)
            lenght_value.insert(ctk.END, str(int(lenght_slider.get())))
            auto_generate()

        def sync_text_to_slider(event=None):
            try:
                value = int(lenght_value.get())
                value = max(1, min(64, value))
                lenght_slider.set(value)
                auto_generate()
            except ValueError:
                lenght_slider.set(1)

        def clear_text(event):
            lenght_value.delete(0, ctk.END)

        generator_frame = side_frame("password_generator")
        if not generator_frame:
            return
        frame = ctk.CTkFrame(generator_frame, width=360, height=650)
        frame.place(x=24, y=10)
        upper_case_letters = ctk.CTkCheckBox(frame, text=translation["Upper_case"], width=150, height=30, onvalue=1, offvalue=0)
        lower_case_letters = ctk.CTkCheckBox(frame, text=translation["Lower_case"], width=150, height=30, onvalue=1, offvalue=0)
        special_characters = ctk.CTkCheckBox(frame, text=translation["Special"], width=150, height=30, onvalue=1, offvalue=0)
        numbers = ctk.CTkCheckBox(frame, text=translation["Numbers"], width=150, height=30, onvalue=1, offvalue=0)

        upper_case_letters.select()
        lower_case_letters.select()
        special_characters.select()
        numbers.select()


        lenght_slider = ctk.CTkSlider(frame, width=200, height=20, from_=1, to=64, number_of_steps=63, command=sync_slider_to_text)
        lenght_slider.set(16)

        lenght_value = ctk.CTkEntry(frame, width=50, height=30)
        lenght_value.insert(0, "16")
        lenght_value.bind("<KeyRelease>", sync_text_to_slider)
        lenght_value.bind("<FocusIn>", clear_text)

        output = ctk.CTkTextbox(frame, width=250, height=30)
        cancel_button = ctk.CTkButton(frame, width=75, height=30, text=translation["Cancel"], command=cancel)
        copy_button = ctk.CTkButton(frame, width=75, height=30, text=translation["Copy"],command=copy)
        regenerate_button = ctk.CTkButton(frame, width=75, height=30, text=translation["Re-generate"], command=lambda: generate(single_run=False))

        x = 20
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

        pending_task = None
        def auto_generate(event=None):
            nonlocal pending_task
            if pending_task is not None:
                generator_frame.after_cancel(pending_task)
            pending_task = generator_frame.after(250, generate)
            if not (upper_case_letters.get() or lower_case_letters.get() or 
                    special_characters.get() or numbers.get()):
                output.delete("0.0", ctk.END)
                output.insert(ctk.END, translation["Select_options"])
                return

        upper_case_letters.configure(command=auto_generate)
        lower_case_letters.configure(command=auto_generate)
        special_characters.configure(command=auto_generate)
        numbers.configure(command=auto_generate)
        lenght_slider.configure(command=lambda v: [sync_slider_to_text(), auto_generate()])

        generate(single_run=True)

#########################################################
# funkcja do sprawdzania sily hasła
#########################################################
    def strongness_checker():
        def cancel():
            sc_frame.place_forget()
            nonlocal active_frame, active_frame_type
            active_frame = None
            active_frame_type = None
        
        def oblicz_entropie(haslo):
            dlugosc = len(haslo)
            zbiory = 0
            
            if re.search(r'[a-z]', haslo):
                zbiory += 26
            if re.search(r'[A-Z]', haslo):
                zbiory += 26
            if re.search(r'[0-9]', haslo):
                zbiory += 10
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', haslo):
                zbiory += 32

            if zbiory > 0:
                entropia = math.log2(zbiory ** dlugosc)
            else:
                entropia = 0
            
            return round(entropia, 2)

        def sprawdz_sile_hasla(haslo):
            dlugosc_punktow = len(haslo) * 2
            wielkie_litery = bool(re.search(r'[A-Z]', haslo))
            male_litery = bool(re.search(r'[a-z]', haslo))
            cyfry = bool(re.search(r'[0-9]', haslo))
            znaki_specjalne = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', haslo))

            unikalne_znaki = len(set(haslo))
            
            punkty = dlugosc_punktow
            if wielkie_litery:
                punkty += 10
            if male_litery:
                punkty += 10
            if cyfry:
                punkty += 10
            if znaki_specjalne:
                punkty += 20

            entropia = oblicz_entropie(haslo)

            if unikalne_znaki <= 3:
                punkty -= 20

            if entropia < 28:
                return 0, translation["Very_weak"], entropia
            elif entropia < 35:
                return 30, translation["Weak"], entropia
            elif entropia < 50:
                return 60, translation["Moderate"], entropia
            else:
                return 100, translation["Strong"], entropia

        def ocen_haslo(event=None):
            haslo = input_entry.get()
            if not haslo:
                progress.set(0)
                result_label.configure(text=translation["Insert_password"])
                strongness.configure(progress_color="")
                return
            wynik, opis, entropia = sprawdz_sile_hasla(haslo)
            progress.set(wynik / 100)
            result_label.configure(text=f"{opis} (Entropia: {entropia} bitów)")
            
            if wynik < 30:
                strongness.configure(progress_color="red")
            elif wynik < 60:
                strongness.configure(progress_color="orange")
            else:
                strongness.configure(progress_color="green")

        sc_frame = side_frame("strongness_checker")
        if not sc_frame:
            return
        frame = ctk.CTkFrame(sc_frame, width=360, height=650)
        frame.place(x=24, y=10)
        input_entry = ctk.CTkEntry(frame, width=200, height=30, placeholder_text=translation["Insert_password"])
        input_entry.place(x=50,y=100)
        cancel_button = ctk.CTkButton(frame, width=75, height=30, text=translation["Cancel"], command=cancel)
        cancel_button.place(x=20, y=22)
        progress = ctk.DoubleVar()
        strongness = ctk.CTkProgressBar(frame, width=200, height=20, variable=progress, progress_color="")
        strongness.place(x=50, y=150)
        
        result_label = ctk.CTkLabel(frame, text=translation["Insert_password"])
        result_label.place(x=50,y=205)

        input_entry.bind("<KeyRelease>", ocen_haslo)

#########################################################
# ustawienia
#########################################################
    def settings():
        settings_frame = side_frame("settings")
        if not settings_frame:
            return
        settings = ctk.CTkTabview(settings_frame,width=360, height=640)
        settings.place(x=24,y=10)
        settings.add("tab1")
        settings.add("tab2")

        def close_settings():
            settings_frame.place_forget()
            nonlocal active_frame, active_frame_type
            active_frame = None
            active_frame_type = None

        cancel_button = ctk.CTkButton(settings_frame,width=20,height=20,text="X",command=close_settings)
        cancel_button.place(x=354,y=40)
        cancel_button.lift()
        ####################
        # tab 1 (usawienia aplikacji)
        ####################
        color_mapping = {
            "blue": translation["Blue"],
            "green": translation["Green"],
            "yellow": translation["Yellow"],
            "red": translation["Red"],
            "orange": translation["Orange"],
            "violet": translation["Violet"],
            "pink": translation["Pink"]}
        
        theme_mapping = {
            "dark": translation["Dark"],
            "light": translation["Light"]}

        color_mapping_inv = {v: k for k, v in color_mapping.items()}
        theme_mapping_inv = {v: k for k, v in theme_mapping.items()}
        language_mapping = {"Polski": "pl", "English": "en"}
        language_mapping_inv = {v: k for k, v in language_mapping.items()}

        def apply_changes():
            window.after(200,close_settings)
            selected_color = color_mapping_inv[color.get()]
            selected_theme = theme_mapping_inv[theme.get()]
            selected_language = language.get()

            if selected_language in language_mapping:
                language_code = language_mapping[selected_language]
            else:
                language_code = "en"
            ctk.set_appearance_mode(selected_theme)

            color_theme_path = COLOR_THEMES.get(selected_color)
            if color_theme_path:
                ctk.set_default_color_theme(color_theme_path)

            updated_settings = {
                "theme": selected_theme,
                "color": selected_color,
                "language": language_code
            }
            save_settings(updated_settings)
            nonlocal translation
            translation = load_translation(language_code, 'MainWindow')

            update_translations_main_window()

            update_preview_theme(selected_theme)
            update_previev_color(selected_color)
            refresh_widgets(window)

        def update_previev_color(choice):
            if choice == "blue":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#3B8ED0",hover_color="#36719F")
            elif choice == "green":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#2E7D32",hover_color="#388E3C")
            elif choice == "red":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#f44336",hover_color="#e53935")
            elif choice == "orange":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#FF7900",hover_color="#FFA533")
            elif choice == "pink":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#fc2bbe",hover_color="#e812ab")
            elif choice == "violet":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#944DC1",hover_color="#8C48B3")
            elif choice == "yellow":
                for widget in preview.winfo_children():
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkButton):
                                sub_widget.configure(fg_color = "#FFF700",hover_color="#FFEB3B")
        
        def update_preview_theme(choice):
            if choice == "dark":
                preview.configure(fg_color="#2B2B2B")
                for widget in preview.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        widget.configure(fg_color="#3B3B3B")
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkTextbox):
                                sub_widget.configure(fg_color="#1E1E1E", text_color="#FFFFFF")
                            elif isinstance(sub_widget, ctk.CTkEntry):
                                sub_widget.configure(fg_color="#1E1E1E", text_color="#FFFFFF")
            elif choice == "light":
                preview.configure(fg_color="#EFEFEF")
                for widget in preview.winfo_children():
                    if isinstance(widget, ctk.CTkFrame):
                        widget.configure(fg_color="gray86")
                        for sub_widget in widget.winfo_children():
                            if isinstance(sub_widget, ctk.CTkTextbox):
                                sub_widget.configure(fg_color="#F9F9F9", text_color="gray10")
                            elif isinstance(sub_widget, ctk.CTkEntry):
                                sub_widget.configure(fg_color="#F9F9F9", text_color="gray10")

        languages = list(language_mapping.keys())
        color_values = list(color_mapping.values())
        theme_values = list(theme_mapping.values())
        color_label = ctk.CTkLabel(settings.tab("tab1"),width=150, height=30, text=translation["Choose_color"],anchor="w")
        color = ctk.CTkComboBox(settings.tab("tab1"), width=100, height=30, values=color_values)
        theme_label = ctk.CTkLabel(settings.tab("tab1"),width=150, height=30, text=translation["Choose_theme"],anchor="w")
        theme = ctk.CTkComboBox(settings.tab("tab1"), width=100, height=30, values=theme_values)
        language_label = ctk.CTkLabel(settings.tab("tab1"),width=150, height=30, text=translation["Choose_language"],anchor="w")
        language = ctk.CTkComboBox(settings.tab("tab1"), width=100, height=30, values=languages)
        apply_button = ctk.CTkButton(settings.tab("tab1"),width=50,height=30,text=translation["Submit"])

        color_label.place(x=10,y=30)
        color.place(x=200, y=30)
        theme_label.place(x=10, y=80)
        theme.place(x=200, y=80)
        language_label.place(x=10, y=130)
        language.place(x=200, y=130)
        apply_button.place(x=135, y=550)

        current_settings = load_setting()
        color.set(color_mapping[current_settings.get("color", "blue")])
        theme.set(theme_mapping[current_settings.get("theme", "dark")])
        language.set(language_mapping_inv[current_settings.get("language", "pl")])
        apply_button.configure(command=apply_changes)

        # previev
        scale_x = 0.47
        scale_y = 0.47
        preview_label = ctk.CTkLabel(settings.tab("tab1"),width=150, height=30, text=translation["Preview"],anchor="w")
        preview = ctk.CTkFrame(settings.tab("tab1"),border_width=2,width=330, height=283)
        for i in range(3):
            frame = ctk.CTkFrame(preview, width=670 * scale_x, height=185 * scale_y, border_width=2)

            system = ctk.CTkTextbox(frame, wrap="none",font=("Roboto", 4), width=230 * scale_x, height=8,state="disabled")

            login = ctk.CTkTextbox(frame, wrap="none",font=("Roboto", 4), width=230 * scale_x, height=8,state="disabled")

            haslo = ctk.CTkTextbox(frame,font=("Roboto", 5),state="disabled", width=230 * scale_x, height=30 * 0.6)

            note = ctk.CTkTextbox(frame,font=("Roboto", 5), width=260 * scale_x, height=140 * scale_y)

            copy = ctk.CTkButton(frame,font=("Roboto", 5),  width=100 * scale_x,height=15,text="")
            delete = ctk.CTkButton(frame,font=("Roboto", 5),  width=100 * scale_x,height=15,text="")
            edit = ctk.CTkButton(frame,font=("Roboto", 5),  width=100 * scale_x, height=15,text="")
            show_pw = ctk.CTkButton(frame,font=("Roboto", 5), width=100 * scale_x, height=15,text="")

            system.place(x=20 * scale_x, y=20 * scale_y)
            login.place(x=20 * scale_x, y=75 * scale_y)
            haslo.place(x=20 * scale_x, y=130 * scale_y)
            note.place(x=275 * scale_x, y=25 * scale_y)
            copy.place(x=550 * scale_x, y=20 * scale_y)
            edit.place(x=550 * scale_x, y=60 * scale_y)
            delete.place(x=550 * scale_x, y=100 * scale_y)
            show_pw.place(x=550 * scale_x, y=140 * scale_y)

            frame.place(x=7, y=5+(i * 195 * scale_y))
        preview_label.place(x=10,y=190)
        preview.place(x=10, y=230)
        theme.configure(command=lambda choice: update_preview_theme(theme_mapping_inv[choice]),state="readonly")
        color.configure(command=lambda choice: update_previev_color(color_mapping_inv[choice]),state="readonly")
        language.configure(state="readonly")
        
        ####################
        # tab 2 (usawienia konta)
        ####################
        user_data = db.get_user_by_username(username_in)
        current_login = user_data.get("username", "")
        current_email = xor(user_data.get("email", ""))

        def confirmation(message, action):
            def accept():
                action()
                confirm_frame.place_forget()
                window.grab_set()
                close_settings()
            def cancel_confirm():
                confirm_frame.place_forget()
                window.grab_set()
            confirm_frame = ctk.CTkFrame(window,border_width=2, width=200, height=120)
            confirm_label = ctk.CTkLabel(confirm_frame, width=196,wraplength=196, text=message)
            confirm_button = ctk.CTkButton(confirm_frame,width = 50, text=translation["Submit"],command=accept)
            cancel = ctk.CTkButton(confirm_frame,width = 50, text=translation["Cancel"],command=cancel_confirm)
            confirm_label.place(relx=0.5, rely=0.3, anchor="center")
            confirm_button.place(relx=0.25, rely=0.75, anchor="center")
            confirm_frame.place(relx=0.5, rely=0.5, anchor="center")
            cancel.place(relx=0.75,rely=0.75, anchor="center")
            confirm_frame.grab_set()

        positions = [101,206,325,455,525]
        def create_borders(y):
            border = ctk.CTkFrame(settings.tab("tab2"),width=360, height=2,fg_color=["gray65","gray28"])
            border.place(x=0,y=y)
        for pos in positions:
            create_borders(pos)

        # zmiana loginu
        def on_username_change(event):
            current_value = new_login.get().strip()
            
            if not current_value:
                error_label_login.configure(text=translation["Empty_login"])
                submit_login.configure(state="disabled")
            elif current_value == current_login:
                error_label_login.configure(text=translation["Login_not_changed"])
                submit_login.configure(state="disabled")
            elif len(current_value) < 5:
                error_label_login.configure(text=translation["Login_min_lenght"])
                submit_login.configure(state="disabled")
            elif get_user_by_username(current_value) is not None:
                error_label_login.configure(text=translation["Username_exist"])
                submit_login.configure(state="disabled")
            else:
                error_label_login.configure(text="")
                submit_login.configure(state="normal")

        def change_login_action():
            new_username = new_login.get().strip()
            confirmation(
                translation["Change_login_info"],
                lambda: execute_login_change(new_username)
            )

        def execute_login_change(new_username):
            result = change_username(user_data["username"], new_username)
            if result["success"]:
                window.after(500, go_back_to_login)
                send_email(translation["Login_changed_subject"], current_email, translation["Login_changed_content"].format(username=new_username))
            else:
                error_label_login.configure(text=result["message"])


        change_login = ctk.CTkLabel(settings.tab("tab2"),width=200, height=30, text=translation["Change_login"],anchor="w")
        new_login = ctk.CTkEntry(settings.tab("tab2"),width=200, height=30, placeholder_text=translation["New_login"])
        submit_login = ctk.CTkButton(settings.tab("tab2"),state="disabled",width=50, height=30,text=translation["Submit"])
        error_label_login = ctk.CTkLabel(settings.tab("tab2"),width=350, height=30, wraplength=350, text="",text_color="red")
        
        new_login.delete(0, ctk.END)
        new_login.insert(0, current_login)
        new_login.bind("<KeyRelease>", on_username_change)

        
        change_login.place(x=10, y=0)
        new_login.place(x=30, y=40)
        submit_login.place(x=240, y=40)
        error_label_login.place(x=0,y=70)
        submit_login.configure(command=change_login_action)

        #  zmiana hasła
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$.!%*?&])[A-Za-z\d@$.!%*?&]{12,}$"

        def on_password_change(event):
            current_value = new_password.get().strip()
            
            if not current_value:
                error_label_password.configure(text=translation["Empty_password"])
                submit_password.configure(state="disabled")
            elif not re.match(password_pattern, current_value):
                error_label_password.configure(text=translation["Password_requirements"])
                submit_password.configure(state="disabled")
            else:
                error_label_password.configure(text="")
                submit_password.configure(state="normal")

        def change_password_action(new_password_value):
            result = change_user_password(user_data["username"], new_password_value)
            if result["success"]:
                info_label_change(translation["Password_changed"])
                send_email(translation["Password_changed_subject"],current_email,translation["Password_changed_content"])
            else:
                error_label_password.configure(text=result["message"])

        b1 = positions[0]
        change_password_label = ctk.CTkLabel(settings.tab("tab2"),width=200, height=30, text=translation["Change_password"],anchor="w")
        new_password = ctk.CTkEntry(settings.tab("tab2"),width=200, height=30, placeholder_text=translation["New_password"])
        submit_password = ctk.CTkButton(settings.tab("tab2"),state="disabled",width=50, height=30,text=translation["Submit"])
        error_label_password = ctk.CTkLabel(settings.tab("tab2"),width=350, height=30, wraplength=350, text="",text_color="red")

        change_password_label.place(x=10, y=b1+5)
        new_password.place(x=30, y=b1+45)
        submit_password.place(x=240, y=b1+45)
        error_label_password.place(x=0, y=b1+75)
        submit_password.configure(command=lambda: confirmation(
            translation["Change_password_info"], 
            lambda: change_password_action(new_password.get())
        ))
        new_password.bind("<KeyRelease>", on_password_change)

        # zmiana emaila
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        def on_email_change(event):
            current_value = new_email.get().strip()
            
            if not current_value:
                error_label_email.configure(text=translation["Empty_email"])
                submit_email.configure(state="disabled")
            elif not re.match(email_pattern, current_value):
                error_label_email.configure(text=translation["Invalid_email"])
                submit_email.configure(state="disabled")
            elif current_value == current_email:
                error_label_email.configure(text=translation["Email_not_changed"])
                submit_email.configure(state="disabled")
            else:
                error_label_email.configure(text="")
                submit_email.configure(state="normal")

        def change_email_action(new_email_value):
            result = change_email(user_data["username"], new_email_value)
            if result["success"]:
                info_label_change(translation["Email_changed"])
                send_email(translation["Email_changed_subject"],new_email_value,translation["Email_changed_content"])

            else:
                error_label_email.configure(text=result["message"])
        
        b2 = positions[1]
        change_email_label = ctk.CTkLabel(settings.tab("tab2"),width=200, height=30, text=translation["Change_email"],anchor="w")
        new_email = ctk.CTkEntry(settings.tab("tab2"),width=200, height=30, placeholder_text=translation["New_email"])
        submit_email = ctk.CTkButton(settings.tab("tab2"),state="disabled",width=50, height=30,text=translation["Submit"])
        error_label_email = ctk.CTkLabel(settings.tab("tab2"),width=350, height=30, wraplength=350, text="",text_color="red")

        new_email.delete(0,ctk.END)
        new_email.insert(0,current_email)

        change_email_label.place(x=10, y=b2+10)
        new_email.place(x=30, y=b2+50)
        submit_email.place(x=240, y=b2+50)
        error_label_email.place(x=0, y=b2+80)
        submit_email.configure(command=lambda: confirmation(
            translation["Change_email_info"], 
            lambda: change_email_action(new_email.get())
        ))
        new_email.bind("<KeyRelease>", on_email_change)

        # wylaczanie/wlaczanie 2fa
        two_fa_status = user_data.get("two_fa", False)
        initial_two_fa_status = two_fa_status

        def toggle_2fa_action(two_fa_status):
            result = toggle_2fa(user_data["username"], two_fa_status)
            if result["success"]:
                info_label_change(f"2FA has been {'enabled' if two_fa_status else 'disabled'}.")

        def on_switch_change():
            if change_2fa.get():
                change_2fa.configure(text=translation["On"])
            else:
                change_2fa.configure(text=translation["Off"])

            if change_2fa.get() == initial_two_fa_status:
                submit_2fa.configure(state="disabled")
            else:
                submit_2fa.configure(state="normal")

        b3 = positions[2]
        change_2fa_label = ctk.CTkLabel(settings.tab("tab2"),width=200, height=30, text=translation["Change_2fa"],anchor="w")
        change_2fa = ctk.CTkSwitch(settings.tab("tab2"), text = translation["Off"],command=on_switch_change)
        submit_2fa = ctk.CTkButton(settings.tab("tab2"),state="disabled",width=50, height=30,text=translation["Submit"])

        if two_fa_status:
            change_2fa.select()
            change_2fa.configure(text=translation["On"])
        else:
            change_2fa.deselect()
            change_2fa.configure(text=translation["Off"])

        change_2fa_label.place(x=10, y=b3+10)
        change_2fa.place(x=120,y=b3+50)
        submit_2fa.place(x=220,y=b3+80)
        submit_2fa.configure(command=lambda: confirmation(
            translation["Confirm_2fa"].format(translation["Enable"] if change_2fa.get() else translation["Disable"]), 
            lambda: toggle_2fa_action(change_2fa.get())
        ))

        def password_confirmation(message, action):
            def accept():
                input_password = password_entry.get()
                
                user = db.get_user_by_username(user_data["username"])
                stored_hash = user.get("password")
                
                if bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8')):  
                    action()
                    confirm_frame.place_forget()
                    window.grab_set()
                    close_settings()

                else:
                    error_label.configure(text=translation["Invalid_password"])
                    password_entry.delete(0, ctk.END)
            
            def cancel_confirm():
                confirm_frame.place_forget()
                window.grab_set()
            
            confirm_frame = ctk.CTkFrame(window, border_width=2, width=250, height=180)
            confirm_label = ctk.CTkLabel(confirm_frame, width=230, wraplength=230, text=message)
            password_entry = ctk.CTkEntry(confirm_frame, show="*", width=200, height=30, placeholder_text=translation["Enter_password"])
            error_label = ctk.CTkLabel(confirm_frame, width=230, height=30, text="", text_color="red")
            confirm_button = ctk.CTkButton(confirm_frame, width=80, text=translation["Submit"], command=accept)
            cancel_button = ctk.CTkButton(confirm_frame, width=80, text=translation["Cancel"], command=cancel_confirm)
            
            confirm_label.place(relx=0.5, rely=0.2, anchor="center")
            password_entry.place(relx=0.5, rely=0.5, anchor="center")
            error_label.place(relx=0.5, rely=0.90, anchor="center")
            confirm_button.place(relx=0.3, rely=0.70, anchor="center")
            cancel_button.place(relx=0.7, rely=0.70, anchor="center")
            confirm_frame.place(relx=0.5, rely=0.5, anchor="center")
            confirm_frame.grab_set()
        
        # usuwanie wszystkich systemów
        b4 = positions[3]
        def delete_all_systems_action():
            nonlocal filtered_list
            result = delete_all_user_systems(user_data["username"])
            if result["success"]:
                info_label_change(translation["All_systems_deleted"])
                filtered_list=get_user_systems(user)
            else:
                error_label_delete_all.configure(text=translation["All_systems_deleting_error"])
                return
            
            window.after(100,refresh_systems)
        error_label_delete_all = ctk.CTkLabel(settings.tab("tab2"),width=160, height=30, text=translation["Delete_all_label"],anchor="w")
        delete_all_button = ctk.CTkButton(settings.tab("tab2"),text=translation["Delete_all"],width=50, height=30)
        
        error_label_delete_all.place(x=10,y=b4+20)
        delete_all_button.place(x=180, y=b4+20)
        delete_all_button.configure(command=lambda: password_confirmation(
            translation["Confirm_delete_all_systems"],
            lambda: delete_all_systems_action()
        ))
        def goodbye_message():
            def accept():
                goodbye_frame.place_forget()
                window.grab_set()
            goodbye_frame = ctk.CTkFrame(window,border_width=2, width=200, height=100)
            goodbye_label = ctk.CTkLabel(goodbye_frame, width=196,wraplength=196, text=translation['Goodbye_message'])
            goodbye_button = ctk.CTkButton(goodbye_frame, text="Ok",command=accept)
            goodbye_label.place(relx=0.5, rely=0.3, anchor="center")
            goodbye_button.place(relx=0.5, rely=0.7, anchor="center")
            goodbye_frame.place(relx=0.5, rely=0.5, anchor="center")
            goodbye_frame.grab_set()

        #usuwanie konta 
        def delete_account_action():
            result = delete_user(user_data["username"])
            if result["success"]:
                window.after(500, go_back_to_login)
                window.after(600,goodbye_message)
                send_email(translation["Account_deleted_subject"],current_email,translation["Account_deleted_email"].format(user=username_in))
            else:
                error_label_delete_account.configure(text=result["message"])

        b5 = positions[4]
        error_label_delete_account = ctk.CTkLabel(settings.tab("tab2"),width=160, height=30, text=translation["Delete_account_label"],anchor="w")
        delete_account = ctk.CTkButton(settings.tab("tab2"),text=translation["Delete_account"],width=50, height=30)
        error_label_delete_account.place(x=10,y=b5+20)
        delete_account.place(x=180, y=b5+20)
        delete_account.configure(command=lambda: password_confirmation(
            translation["Confirm_delete_account"],
            lambda: delete_account_action()
        ))
        settings._segmented_button._buttons_dict["tab1"].configure(state=ctk.NORMAL, text=translation["App_settings"])
        settings._segmented_button._buttons_dict["tab2"].configure(state=ctk.NORMAL, text=translation["Account_settings"])

#########################################################
# funkcja do cyszczenia pola wyszukiwania
#########################################################
    def clear_search():
        if search_input.get() != "":
            search_input.delete(0, 'end')
            search_input.configure(placeholder_text=translation["Search"])
            on_search_input_change(None)

#########################################################
# definicja pola bocznego, pola informacyjnego, informacji o stronach, ramki systemow 
#########################################################
    sidebar = ctk.CTkFrame(window, width=200, height=672, corner_radius=0)
    sidebar.place(x=0, y=0)
    info_frame = ctk.CTkFrame(window, width=1000, height=30, corner_radius=0)
    info_frame.place(x=0, y=670)
    pages_label = ctk.CTkLabel(window,width=150, text="", anchor="e")
    pages_label.place(x=735, y=635)

    time_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="right")
    info_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="left")
    info_label.place(x=20, y=0)
    time_label.place(x=860, y=0)

    content_frame = ctk.CTkFrame(window, width=700, height=600)
    content_frame.place(x=250, y=30)
    no_systems_label = ctk.CTkLabel(content_frame, width = 700, height = 50, text = translation["No_system_found"])

    hello_label = ctk.CTkLabel(sidebar, width=200, height=80, text=f"{translation["Hello"]} \n{user}", font=("default", 24))
    search_input = ctk.CTkEntry(sidebar, width=150, height=30, placeholder_text=translation["Search"])
    clear_button = ctk.CTkButton(sidebar, width=150, height=30, text=translation["Clear"],command=clear_search)
    logout = ctk.CTkButton(sidebar, width=150,text=translation["Logout"], command=logout)
    add_system_button = ctk.CTkButton(sidebar, width=150, text=translation["Add_system"], command=add_system)
    sort_label = ctk.CTkLabel(sidebar, width=150, anchor="w", height=30, text=translation["Sort"])
    settings_button = ctk.CTkButton(sidebar, width=150, height=30, text=translation["Settings"],command=settings)
    generator_button = ctk.CTkButton(sidebar, width=150, height=30, text=translation["Password_generator"], command=password_generator)
    strongness_checker_button = ctk.CTkButton(sidebar, width=150, height=30, text=translation["Strongness_checker"],command=strongness_checker)

    sidebar.place(x=0, y=0)
    hello_label.place(x=0, y=35)
    search_input.place(x=25, y=150) 
    clear_button.place(x=25, y=190) 
    add_system_button.place(x=25, y=255) 
    generator_button.place(x=25, y=320) 
    strongness_checker_button.place(x=25, y=370)
    sort_label.place(x=25, y=450)
    settings_button.place(x=25, y=565)
    logout.place(x=25, y=615)

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
        systems_list = get_user_systems(user)
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
        if selected_option == translation["Name(A-Z)"]:
            filtered_list.sort(key=lambda x: x['system_name'].casefold())
        elif selected_option == translation["Name(Z-A)"]:
            filtered_list.sort(key=lambda x: x['system_name'].casefold(), reverse=True)
        elif selected_option == translation["Oldest_first"]:
            filtered_list.sort(key=lambda x: x.get('creation_date', datetime.min))
        elif selected_option == translation["Newest_first"]:
            filtered_list.sort(key=lambda x: x.get('creation_date', datetime.min), reverse=True)
        refresh_systems()

    sort_options = [
        translation["Name(A-Z)"],
        translation["Name(Z-A)"],
        translation["Newest_first"],
        translation["Oldest_first"]
    ]
    sort_combobox = ctk.CTkComboBox(sidebar, width=150, height=30, values=sort_options,command=sort_systems)
    sort_combobox.set(translation["Oldest_first"])
    sort_combobox.place(x=25, y=480)
    sort_combobox.bind("<<ComboboxSelected>>", lambda: sort_systems())
    sort_combobox.configure(state="readonly")

#########################################################
# funkcja do odswierzania okna po jakichkolwiek zmianach(wyszukiwanie, dodawanie, usuwanie itp)
#########################################################
    def refresh_systems():
            def update_systems():
                nonlocal total_items, max_pages, current_page, item_frames

                # Operacje czasochłonne w wątku
                total_items = len(filtered_list)
                max_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1
                current_page = min(current_page, max_pages - 1)

                # Zleć usuwanie starych elementów do głównego wątku
                window.after(0, clear_item_frames)

                # Zleć tworzenie nowych elementów do głównego wątku
                window.after(0, create_item_frames)

                # Zleć finalizowanie aktualizacji do głównego wątku
                window.after(0, finalize_update)

            def clear_item_frames():
                # Usuwanie starych ramek z GUI w głównym wątku
                for item_frame in item_frames:
                    item_frame.destroy()
                item_frames.clear()

            def create_item_frames():
                # Tworzenie nowych ramek w głównym wątku
                for i in range(total_items):
                    item_frame = create_item_frame(content_frame, i, filtered_list)
                    item_frames.append(item_frame)

            def finalize_update():
                # Zakończenie aktualizacji interfejsu w głównym wątku
                unblock_buttons()
                show_page(current_page)
                print_current_page_info(current_page, max_pages)

                # Obsługa etykiety "brak systemów"
                if total_items == 0:
                    no_systems_label.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    no_systems_label.place_forget()

            # Utworzenie wątku
            thread = threading.Thread(target=update_systems)
            thread.start()

#########################################################
# tworzenie kafelków z danymi witryn
#########################################################
    def create_item_frame(parent, index, display_list):
        def copy_password():
            nonlocal active_frame
            if active_frame is None:
                content = haslo.get()
                window.clipboard_clear()
                window.clipboard_append(content)
                info_label_change(translation["Copied"])
                window.update()

        def toggle_password():
            nonlocal active_frame
            if active_frame is None:
                if haslo.cget("show") == "*":
                    haslo.configure(show="")
                    show_pw.configure(text=translation["Hide_password"])
                else:
                    haslo.configure(show="*")
                    show_pw.configure(text=translation["Show_password"])

        def edit_system():
            nonlocal active_frame
            if active_frame is None:
                nonlocal filtered_list
                edit_frame = side_frame("edit_frame")
                if not edit_frame:
                    return

                system_data = display_list[index]
                system_name_value = system_data["system_name"]
                login_value = system_data["login"]
                password_value = system_data["password"]
                note_value = system_data["note"]

                def cancel_edit():
                    nonlocal active_frame, active_frame_type
                    active_frame = None
                    active_frame_type = None
                    edit_frame.place_forget()

                def save_system():
                    nonlocal filtered_list
                    new_system_name = system_entry.get("1.0", "end-1c").strip()
                    new_login = login_entry.get("1.0", "end-1c").strip()
                    new_password = password_entry.get("1.0", "end-1c").strip()
                    new_note = note_entry.get("1.0", "end-1c").strip()

                    if not new_system_name or not new_login or not new_password:
                        error_label.configure(text=translation["Requirements"])
                        return
                    
                    existing_system = db.check_existing_system(user, new_system_name, login)

                    if existing_system:
                        error_label.configure(text=translation["Existing_system"])
                        return

                    update_result = db.update_user_system(
                        user, 
                        original_system_name=system_name_value, 
                        new_system_name=new_system_name,
                        new_login=new_login, 
                        new_password=new_password, 
                        new_note=new_note)

                    if update_result["success"]:
                        systems_list = get_user_systems(user)
                        filtered_list = systems_list
                        edit_frame.place_forget()
                        nonlocal active_frame, active_frame_type
                        active_frame = None
                        active_frame_type = None
                        search_systems()
                        info_label_change(translation["Edited"])
                    else:
                        error_label.configure(text=translation["Editing_error"])
                
                frame = ctk.CTkFrame(edit_frame, width=360, height=650)
                frame.place(x=24, y=10)
                system_label = ctk.CTkLabel(frame, text=translation["System_name"])
                system_label.place(x=20, y=20)
                system_entry = ctk.CTkTextbox(frame, width=200, height=30)
                system_entry.insert("0.0", system_name_value)
                system_entry.place(x=150, y=20)

                login_label = ctk.CTkLabel(frame, text=translation["Login"])
                login_label.place(x=20, y=60)
                login_entry = ctk.CTkTextbox(frame, width=200, height=30)
                login_entry.insert("0.0", login_value)
                login_entry.place(x=150, y=60)

                password_label = ctk.CTkLabel(frame, text=translation["Password"])
                password_label.place(x=20, y=100)
                password_entry = ctk.CTkTextbox(frame, width=200, height=30)
                password_entry.insert("0.0", password_value)
                password_entry.place(x=150, y=100)

                note_label = ctk.CTkLabel(frame, text=translation["Note"])
                note_label.place(x=20, y=140)
                note_entry = ctk.CTkTextbox(frame, width=200, height=100)
                note_entry.insert("0.0", note_value)
                note_entry.place(x=150, y=140)

                error_label = ctk.CTkLabel(frame, text="", text_color="red")
                error_label.place(x=150, y=250)

                save_button = ctk.CTkButton(frame, width=75, text=translation["Submit"], command=save_system)
                save_button.place(x=150, y=300)

                cancel_button = ctk.CTkButton(frame, width=75, text=translation["Cancel"], command=cancel_edit)
                cancel_button.place(x=250, y=300)

        def delete_system(index):
            nonlocal active_frame
            if active_frame is None:
                system_data = display_list[index]

                confirm_frame = ctk.CTkFrame(window, width=200, height=100, border_width=2)
                confirm_frame.place(relx=0.5, rely=0.5, anchor='center')
                confirm_frame.grab_set()

                confirm_label = ctk.CTkLabel(confirm_frame, wraplength=196, width=196, text=translation["Delete_question"], anchor="center")
                confirm_label.place(x=2, y=15)
                
                def confirm_deletion():
                    nonlocal filtered_list
                    result = db.delete_user_system(user, system_data["system_name"])
                    if result.get("success"):
                        systems_list = get_user_systems(user)
                        filtered_list = systems_list
                        refresh_systems()
                        info_label_change(translation["System_deleted"])
                    else:
                        info_label_change(translation["Deleting_error"])
                        
                    confirm_frame.destroy()
                    window.grab_set()

                def cancel_deletion():
                    confirm_frame.destroy()
                    window.grab_set()

                yes_button = ctk.CTkButton(confirm_frame, width=50, height=30, text=translation["Yes"], command=confirm_deletion)
                no_button = ctk.CTkButton(confirm_frame, width=50, height=30, text=translation["No"], command=cancel_deletion)

                yes_button.place(x=25, y=60)
                no_button.place(x=125, y=60)

        system_data = display_list[index]
        frame = ctk.CTkFrame(parent, width=670, height=185, border_width=2)

        system_label = ctk.CTkLabel(frame, text=translation["System_name"], width=40, height=20, anchor="w")
        system = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        system.insert("0.0", system_data["system_name"])

        login_label = ctk.CTkLabel(frame, text=translation["Login"], width=100, height=20, anchor="w")
        login = ctk.CTkTextbox(frame, wrap="none", width=230, height=30)
        login.insert("0.0", system_data["login"])

        haslo_label = ctk.CTkLabel(frame, text=translation["Password"], width=100, height=20, anchor="w")
        haslo = ctk.CTkEntry(frame, width=230, height=30, show="*", border_width=0, fg_color=ctk.ThemeManager.theme["CTkTextbox"]["fg_color"],text_color=ctk.ThemeManager.theme["CTkTextbox"]["text_color"])
        haslo.custom_name = "haslo"
        haslo.insert(0, system_data["password"])
        
        note_label = ctk.CTkLabel(frame, text=translation["Content_frame_note"], width=100, height=15, anchor="w")
        note = ctk.CTkTextbox(frame, width=260, height=140)
        note.custom_name = "note"

        if not system_data["note"]:
            note.insert("0.0", translation["No_note"])
            note.configure(text_color="#808080")
        else:
            note.insert("0.0", system_data["note"])

        copy = ctk.CTkButton(frame, text=translation["Copy"], width=100, command=copy_password)
        delete = ctk.CTkButton(frame, text=translation["Delete"], width=100, command=lambda: delete_system(index))
        edit = ctk.CTkButton(frame, text=translation["Edit"], width=100, command=edit_system)
        show_pw = ctk.CTkButton(frame, width=100, text=translation["Show_password"], command=toggle_password)

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
            pages_label.configure(text=f"{translation["Current_page"]}: {current_page + 1}/{max_pages} ({translation["Items"]}: {total_items})",anchor="e")

    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i, filtered_list)
        item_frames.append(item_frame)

#########################################################
# funkcja do zmiany strony na nastepna
#########################################################
    def next_page():
        nonlocal current_page            
        nonlocal active_frame
        if active_frame is None:
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
        nonlocal active_frame
        if active_frame is None:
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
    window.bind_all("<Button-1>", mouse_action)
    window.bind_all("<Any-KeyPress>", reset_timer)
    window.bind_all("<Button>", reset_timer)

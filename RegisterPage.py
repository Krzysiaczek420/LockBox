import re
import customtkinter as ctk
from CTkToolTip import *
import tkinter as tk
from PIL import Image, ImageTk
import PinWindow as pin
import Baza

def open_register_window(login_window):
    register_window = ctk.CTk()
    register_window.geometry("700x500")
    register_window.title("LockBox-Registration")
    register_window.resizable(False, False)

    def check_passwords():
        global same_passwords
        same_passwords = False
        password = password_input.get()
        confirm_password = confirm_password_input.get()
        if password == confirm_password and (confirm_password != "" and password != ""):
            same_passwords = True
        else:
            clear_textboxes()
            register_window.focus_set()
            error_label.configure(text="Passwords are not the same")

    def check_if_empty(event=None):
        if (username_input.get() == "" or password_input.get() == "" or
            confirm_password_input.get() == "" or answer_input.get() == "" or
            security_question_combobox.get() in ("Select Question", "")):
            register_button.configure(state="disabled")
        else:
            register_button.configure(state="normal")

    def check_username_length():
        username = username_input.get()
        if ' ' in username:
            clear_textboxes()
            error_label.configure(text="Username cannot contain spaces")
            return False
        elif len(username) >= 5:
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text="Username must be at least 5 characters long")
            return False

    def check_password_validity():
        password = password_input.get()
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        if re.match(pattern, password):
            error_label.configure(text="")
            return True
        else:
            clear_textboxes()
            error_label.configure(text="Password must contain at least 12 characters including at least one uppercase letter,\n one lowercase letter, one digit, and one special character", justify="center", compound="center")
            return False

    def cancel_focus(event=None):
        if event:
            widget = register_window.winfo_containing(event.x_root, event.y_root)
            if widget == register_window:
                register_window.focus_set()
                if security_question_combobox.get() == "":
                    security_question_combobox.set("Select Question")
        else:
            register_window.focus_set()
            if security_question_combobox.get() == "":
                security_question_combobox.set("Select Question")

    def show_password_button():
        if password_input.cget("show") == "*" or confirm_password_input.cget("show") == "*":
            password_input.configure(show="")
            confirm_password_input.configure(show="")
        else:
            password_input.configure(show="*")
            confirm_password_input.configure(show="*")

    def on_other_selected(choice):
        if security_question_combobox.get() == "Other...":
            security_question_combobox.configure(state="normal")
            security_question_combobox.set("")
        else:
            security_question_combobox.configure(state="readonly")
        check_if_empty()

    def check_combobox_empty():
        if security_question_combobox.get() == "Other...":
            register_button.configure(state="disabled")
        else:
            check_if_empty()

    def clear_textboxes():
        username_input.delete(0, tk.END)
        username_input.configure(placeholder_text="Username")
        password_input.delete(0, tk.END)
        password_input.configure(placeholder_text="Password")
        confirm_password_input.delete(0, tk.END)
        confirm_password_input.configure(placeholder_text="Confirm password")
        security_question_combobox.set("Select Question")
        answer_input.delete(0, tk.END)
        answer_input.configure(placeholder_text="Security Question Answer")
        error_label.configure(text="")
        register_button.configure(state="disabled")
        cancel_focus()

    def register_action():
        if check_username_length() and check_password_validity():
            check_passwords()
            if same_passwords:
                pin_value = pin.generate_random_pin()
                result = Baza.add_user(
                    username=username_input.get(),
                    password=password_input.get(),
                    security_question=security_question_combobox.get(),
                    answer=answer_input.get(),
                    pin_code=pin_value
                )
                if result["success"]:
                    pin.pin_window(register_window, login_window,pin_value)
                else:
                    error_label.configure(text=result["message"])

    def on_closing():
        if register_window:
            try:
                register_window.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
            except tk.TclError:
                pass

    register_window.protocol("WM_DELETE_WINDOW", on_closing)
    register_window.bind("<Button-1>", cancel_focus)

    username_input = ctk.CTkEntry(register_window, width=150, height=30, placeholder_text="Username")
    show_password_register = ctk.CTkCheckBox(register_window, text="show password", width=150, height=30, command=show_password_button)
    password_input = ctk.CTkEntry(register_window, width=150, height=30, placeholder_text="Password", show="*")
    confirm_password_input = ctk.CTkEntry(register_window, width=150, height=30, placeholder_text="Confirm Password", show="*")

    security_question_values = [
        "What is your mother's maiden name?",
        "What is the name of your",
        "Where were you born?",
        "What is the name of your first pet?",
        "What was your first car?",
        "Other..."]

    security_question_combobox = ctk.CTkComboBox(register_window, state="readonly", width=150, height=30, values=security_question_values, command=on_other_selected)
    security_question_combobox.set("Select Question")
    security_question_combobox.bind("<<ComboboxSelected>>", on_other_selected)

    answer_input = ctk.CTkEntry(register_window, width=150, height=30, placeholder_text="Security Question Answer")
    register_button = ctk.CTkButton(register_window, state="disabled", text="Register", command=register_action)
    error_label = ctk.CTkLabel(register_window, text="",compound="center", width=700, height=50, fg_color="transparent", text_color="red")

    username_input.bind("<KeyRelease>", check_if_empty)
    password_input.bind("<KeyRelease>", check_if_empty)
    confirm_password_input.bind("<KeyRelease>", check_if_empty)
    answer_input.bind("<KeyRelease>", check_if_empty)

    register_label = ctk.CTkLabel(register_window, text="Registration", width=140, height=20)

    username_input.place(x=275, y=150)
    password_input.place(x=275, y=200)
    confirm_password_input.place(x=275, y=250)
    security_question_combobox.place(x=195, y=300)
    answer_input.place(x=365, y=300)
    show_password_register.place(x=275, y=350)
    register_button.place(x=275, y=400)
    error_label.place(x=0, y=430)

    register_window.mainloop()

import math
import time
import customtkinter as ctk
import datetime
import threading
from Animacja import animate_frame, animate_page_change

def MainWindow():
    main_window = ctk.CTk()
    main_window.geometry("1000x700")
    main_window.title("LockBox")
    main_window.resizable(False, False)
    user = "Krzysztof"

    def update_time(label):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label.configure(text=current_time)
        label.after(1000, update_time, label)

    sidebar = ctk.CTkFrame(main_window, width=200, height=670, corner_radius=0)
    info_frame = ctk.CTkFrame(main_window, width=1000, height=30, corner_radius=0)

    hello_label = ctk.CTkLabel(sidebar, width=200, height=80, text=("witaj \n" + user), font=("default", 24))     
    time_label = ctk.CTkLabel(info_frame, width=120, height=30, text="", justify="right")
    info_label = ctk.CTkLabel(info_frame, width=120, height=30, text="aaaaaaaaaaaaaa", justify="left")
    pages_label = ctk.CTkLabel(main_window, text="")
    
    content_frame = ctk.CTkFrame(main_window, width=700, height=600)
    content_frame.place(x=250, y=30)

    sidebar.place(x=0, y=0)
    info_frame.place(x=0, y=670)
    hello_label.place(x=0, y=25)
    time_label.place(x=860, y=0)
    info_label.place(x=20, y=0)
    pages_label.place(x=760, y=640)

    update_time(time_label)

    def create_item_frame(parent, index):
        frame = ctk.CTkFrame(parent, width=610, height=185, border_width=2, border_color="black")
        system_label = ctk.CTkLabel(frame, text=f"system", width=40,height = 20,anchor="w")
        system = ctk.CTkTextbox(frame,wrap="none", width=180, height=30)
        login_label = ctk.CTkLabel(frame, text=f"login", width=100,height = 20,anchor="w")
        haslo_label = ctk.CTkLabel(frame, text=f"haslo", width=100,height = 20,anchor="w")
        note_label = ctk.CTkLabel(frame, text=f"note", width=100,height=15,anchor="w")
        login = ctk.CTkTextbox(frame,wrap="none", width=180,height=30)
        haslo = ctk.CTkTextbox(frame,wrap="none", width=180,height=30)
        #note = ctk.CTkTextbox(frame, width=130,height=100)
        copy = ctk.CTkButton(frame, text="copy password", width=100)
        delete = ctk.CTkButton(frame, text="delete", width=100)
        edit = ctk.CTkButton(frame, text="edit", width=100)
        #show_pw = ctk.CTkCheckBox(frame, text="show password", width=90, height=30,checkbox_height=20, checkbox_width=20)
        show_pw = ctk.CTkButton(frame, text="", width=100)
        # layout 3
        note = ctk.CTkTextbox(frame, width=260,height=140)
        system_label.place(x=30,y=5)
        system.place(x=20,y=25)
        login_label.place(x=30, y=60)
        login.place(x=20,y=80)
        haslo_label.place(x=30,y=115)
        haslo.place(x=20,y=135)
        note_label.place(x=225, y=6)
        note.place(x= 215,y=25)
        copy.place(x=490,y=20)
        edit.place(x=490, y=60)
        delete.place(x=490, y=100)
        show_pw.place(x=490, y=140)

        return frame

    items_per_page = 3
    current_page = 0
    total_items = 7
    item_frames = []
    max_pages = math.ceil(total_items / items_per_page)
    def print_current_page_info(current_page, max_pages):
        pages_label.configure(text=f"Current page: {current_page + 1}/{max_pages}")

    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i)
        item_frames.append(item_frame)

    def show_page(page):
        for i, item_frame in enumerate(item_frames):
            if page * items_per_page <= i < (page + 1) * items_per_page:
                item_frame.place(x=45, y=((i % items_per_page) * 200) + 10, in_=content_frame)
            else:
                item_frame.place_forget()

    def next_page():
        nonlocal current_page
        if (current_page + 1) * items_per_page < total_items:
            block_button()
            current_page = animate_page_change(current_page, current_page + 1, 'next', item_frames, items_per_page, total_items, show_page, content_frame, main_window)
            main_window.after(100, unblock_buttons)  # Adjust delay as needed based on animation duration
            print_current_page_info(current_page, max_pages)

    def prev_page():
        nonlocal current_page
        if current_page > 0:
            block_button()
            current_page = animate_page_change(current_page, current_page - 1, 'prev', item_frames, items_per_page, total_items, show_page, content_frame, main_window)
            main_window.after(100, unblock_buttons)  # Adjust delay as needed based on animation duration
            print_current_page_info(current_page, max_pages)

    def block_button():
        prev_button.configure(state='disabled')
        next_button.configure(state='disabled')

    def unblock_buttons():
        if current_page == 0:
            prev_button.configure(state='disabled')
            next_button.configure(state='normal')
        elif (current_page + 1) * items_per_page >= total_items:
            prev_button.configure(state='normal')
            next_button.configure(state='disabled')
        else:
            prev_button.configure(state='normal')
            next_button.configure(state='normal')

    prev_button = ctk.CTkButton(main_window, text="<", width=20, height=20, command=prev_page)
    next_button = ctk.CTkButton(main_window, text=">", width=20, height=20, command=next_page)
    
    prev_button.place(x=895, y=640)
    next_button.place(x=925, y=640)

    show_page(current_page)

    def show_first_page():
        for i in range(items_per_page):
            if i < total_items:
                frame = item_frames[i]
                frame.place(x=45, y=i * 200 + 10, in_=content_frame)
        for i in range(items_per_page):
            if items_per_page + i < total_items:
                frame = item_frames[items_per_page + i]
                frame.place(x=670, y=i * 200 + 10, in_=content_frame)

    main_window.after(100, show_first_page)
    unblock_buttons()
    print_current_page_info(current_page, max_pages)
    main_window.mainloop()

MainWindow()

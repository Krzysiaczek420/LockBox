import math
import time
import customtkinter as ctk
import datetime
import threading

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

    sidebar = ctk.CTkFrame(main_window, 
        width=200, 
        height=670, 
        corner_radius=0)
    
    info_frame = ctk.CTkFrame(main_window, 
        width=1000,
        height=30, 
        corner_radius=0)

    hello_label = ctk.CTkLabel(sidebar,
        width=200,
        height=80,
        text=("witaj \n"+ user),
        font=("default",24))     
    
    time_label = ctk.CTkLabel(info_frame,
        width=120,
        height=30,
        text="",
        justify="right")
    info_label = ctk.CTkLabel(info_frame,
        width=120,
        height=30,
        text="aaaaaaaaaaaaaa",
        justify="left")
    pages_label = ctk.CTkLabel(main_window, 
        text = "")
    
    
    content_frame = ctk.CTkFrame(main_window, width=700, height=500)
    content_frame.place(x=220, y=120)  # Adjusted x-position to make space for visible parts of elements
    
    sidebar.place(x=0, y=0)
    info_frame.place(x=0, y=670)
    hello_label.place(x=0, y=25)
    time_label.place(x=860, y=0)
    info_label.place(x=20, y=0)
    pages_label.place(x=730, y=625)

    update_time(time_label)  # Uruchom aktualizację czasu

    def create_item_frame(parent, index):
        frame = ctk.CTkFrame(parent, width=610, height=150, border_width=2, border_color="black")
        
        label = ctk.CTkLabel(frame, text=f"Element {index}", width=100)
        label2 = ctk.CTkLabel(frame, text=f"Element {index}", width=100)
        label3 = ctk.CTkLabel(frame, text=f"Element {index}", width=100)
        textbox1 = ctk.CTkEntry(frame, width=140)
        textbox2 = ctk.CTkEntry(frame, width=140)
        textbox3 = ctk.CTkEntry(frame, width=140)
        button1 = ctk.CTkButton(frame, text="Button 1")
        button2 = ctk.CTkButton(frame, text="Button 2")
        button3 = ctk.CTkButton(frame, text="Button 3")
        button4 = ctk.CTkButton(frame, text="Button 4")
        
        # # Ustawienie pozycji elementów w ramce
        # label.place(x=10, y=10)
        # textbox1.place(x=120, y=10)
        # textbox2.place(x=270, y=10)
        # textbox3.place(x=420, y=10)
        # button1.place(x=120, y=50)
        # button2.place(x=270, y=50)
        # button3.place(x=420, y=50)
        # button4.place(x=570, y=50)
        
        return frame

    items_per_page = 3
    current_page = 0
    total_items = 15
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
                item_frame.place(x=45, y=((i % items_per_page) * 165) + 10, in_=content_frame)
            else:
                item_frame.place_forget()

    def animate_frame(x_start, x_end, y, frame, duration=0.15):
        steps = 20  # Stała liczba kroków
        delta_x = (x_end - x_start) / steps
        delay = duration / steps
        for step in range(steps):
            new_x = x_start + delta_x * step
            frame.place(x=new_x, y=y)
            main_window.update()
            time.sleep(delay)
        frame.place(x=x_end, y=y)

    def animate_page_change(next_page, direction):
        nonlocal current_page
        if direction == 'next' and (next_page * items_per_page < total_items):
            # Przesuń elementy z poprzedniej strony w lewo
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(45, -580, ((i % items_per_page) * 165) + 10, frame)).start()
            # Przesuń fragmenty elementów z następnej strony w prawo
            if (next_page + 1) * items_per_page < total_items:
                for i in range(items_per_page):
                    if (next_page + 1) * items_per_page + i < total_items:
                        frame = item_frames[(next_page + 1) * items_per_page + i]
                        threading.Thread(target=animate_frame, args=(1250, 670, ((i % items_per_page) * 165) + 10, frame)).start()
            current_page = next_page
            show_page(current_page)
            # Wyświetl elementy z nowej strony
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    frame.place(x=660, y=((i % items_per_page) * 165) + 10, in_=content_frame)
                    threading.Thread(target=animate_frame, args=(1250, 45, ((i % items_per_page) * 165) + 10, frame)).start()
        elif direction == 'prev' and (current_page > 0):
            # Przesuń elementy z następnej strony w prawo
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(45, 670, ((i % items_per_page) * 165) + 10, frame)).start()
            current_page = next_page  # Poprawienie przypisania
            show_page(current_page)
            # Wyświetl elementy z nowej strony po lewej stronie
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    frame.place(x=45, y=((i % items_per_page) * 165) + 10, in_=content_frame)
                    threading.Thread(target=animate_frame, args=(-590, 45, ((i % items_per_page) * 165) + 10, frame)).start()
            # Przesuń fragmenty elementów z poprzedniej strony w lewo
            if current_page > 0:
                for i in range(items_per_page):
                    if (current_page - 1) * items_per_page + i < total_items:
                        frame = item_frames[(current_page - 1) * items_per_page + i]
                        threading.Thread(target=animate_frame, args=(-1110, -580, ((i % items_per_page) * 165) + 10, frame)).start()

    def next_page():
        if (current_page + 1) * items_per_page < total_items:
            animate_page_change(current_page + 1, 'next')
            block_buttons()
            print_current_page_info(current_page, max_pages)
    def prev_page():
        if current_page > 0:
            animate_page_change(current_page - 1, 'prev')
            block_buttons()
            print_current_page_info(current_page, max_pages)
    def block_buttons():
        if current_page == 0:
            prev_button.configure(state='disabled')
            next_button.configure(state='normal')
        elif (current_page + 1) * items_per_page >= total_items:
            prev_button.configure(state='normal')
            next_button.configure(state='disabled')
        else:
            prev_button.configure(state='normal')
            next_button.configure(state='normal')

    prev_button = ctk.CTkButton(main_window, text="<", width=20,height=20, command=prev_page)
    next_button = ctk.CTkButton(main_window, text=">",width=20,height=20, command=next_page)
    
    prev_button.place(x=865, y=625)
    next_button.place(x=895, y=625)

    show_page(current_page)

    def show_first_page():
        for i in range(items_per_page):
            if i < total_items:
                frame = item_frames[i]
                frame.place(x=45, y=i * 165 + 10, in_=content_frame)  # Ustawienie ramki na odpowiedniej pozycji wewnątrz content_frame
        for i in range(items_per_page):
            if items_per_page + i < total_items:
                frame = item_frames[items_per_page + i]
                frame.place(x=670, y=i * 165 + 10, in_=content_frame)

    main_window.after(100, show_first_page) # Uruchom animację po 100 ms od uruchomienia głównego okna
    block_buttons()
    print_current_page_info(current_page, max_pages)
    main_window.mainloop()

MainWindow()

import time
import customtkinter as ctk
import datetime
import threading

def MainWindow():
    main_window = ctk.CTk()
    main_window.geometry("1000x600")
    main_window.title("LockBox")
    main_window.resizable(False, False)
    user = "Krzysztof"

    def update_time(label):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label.configure(text=current_time)
        label.after(1000, update_time, label)

    sidebar = ctk.CTkFrame(main_window, 
        width=200, 
        height=570, 
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
    
    content_frame = ctk.CTkFrame(main_window, width=650, height=500)
    content_frame.place(x=250, y=30)  # Adjusted x-position to make space for visible parts of elements
    
    sidebar.place(x=0, y=0)
    info_frame.place(x=0, y=570)
    hello_label.place(x=0, y=25)
    time_label.place(x=860, y=0)
    info_label.place(x=20, y=0)

    update_time(time_label)  # Uruchom aktualizację czasu

    def create_item_frame(parent, index):
        frame = ctk.CTkFrame(parent, width=610, height=100, border_width=2, border_color="black")
        
        label = ctk.CTkLabel(frame, text=f"Element {index}", width=100)
        textbox1 = ctk.CTkEntry(frame, width=140)
        textbox2 = ctk.CTkEntry(frame, width=140)
        textbox3 = ctk.CTkEntry(frame, width=140)
        button1 = ctk.CTkButton(frame, text="Button 1")
        button2 = ctk.CTkButton(frame, text="Button 2")
        
        # Ustawienie pozycji elementów w ramce
        label.grid(row=0, column=0, padx=10, pady=10)
        textbox1.grid(row=0, column=1, padx=10, pady=10)
        textbox2.grid(row=0, column=2, padx=10, pady=10)
        textbox3.grid(row=0, column=3, padx=10, pady=10)
        button1.grid(row=1, column=1, columnspan=2, pady=10)
        button2.grid(row=1, column=3, columnspan=2, pady=10)
        
        return frame

    items_per_page = 4
    current_page = 0
    total_items = 17
    item_frames = []

    for i in range(total_items):
        item_frame = create_item_frame(content_frame, i)
        item_frames.append(item_frame)

    def show_page(page):
        for i, item_frame in enumerate(item_frames):
            if page * items_per_page <= i < (page + 1) * items_per_page:
                item_frame.place(x=20, y=((i % items_per_page) * 110) + 20)
            elif (page * items_per_page - items_per_page) <= i < page * items_per_page:
                item_frame.place(x=-590, y=((i % items_per_page) * 110) + 20)
            elif ((page + 1) * items_per_page) <= i < ((page + 2) * items_per_page):
                item_frame.place(x=630, y=((i % items_per_page) * 110) + 20)
            else:
                item_frame.place_forget()

    def animate_frame(x_start, x_end, y, frame, duration=0.25):
        steps = 25
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
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(20, -590, ((i % items_per_page) * 110) + 20, frame)).start()
            current_page = next_page
            show_page(current_page)
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(630, 20, ((i % items_per_page) * 110) + 20, frame)).start()
        elif direction == 'prev' and (current_page > 0):
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(20, 630, ((i % items_per_page) * 110) + 20, frame)).start()
            current_page = next_page
            show_page(current_page)
            for i in range(items_per_page):
                if current_page * items_per_page + i < total_items:
                    frame = item_frames[current_page * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(-590, 20, ((i % items_per_page) * 110) + 20, frame)).start()

    def next_page():
        if (current_page + 1) * items_per_page < total_items:
            animate_page_change(current_page + 1, 'next')

    def prev_page():
        if current_page > 0:
            animate_page_change(current_page - 1, 'prev')

    prev_button = ctk.CTkButton(main_window, text="<", command=prev_page)
    next_button = ctk.CTkButton(main_window, text=">", command=next_page)
    
    prev_button.place(x=150, y=540)
    next_button = ctk.CTkButton(main_window, text=">", command=next_page)
    
    prev_button.place(x=150, y=540)
    next_button.place(x=860, y=540)

    show_page(current_page)

    main_window.mainloop()

MainWindow()

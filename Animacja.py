import time
import threading

def animate_frame(x_start, x_end, y, frame, duration=0.05, main_window=None):
    steps = 20  # Stała liczba kroków
    delta_x = (x_end - x_start) / steps
    delay = duration / steps
    for step in range(steps):
        new_x = x_start + delta_x * step
        frame.place(x=new_x, y=y)
        if main_window:
            main_window.update()
        time.sleep(delay)
    frame.place(x=x_end, y=y)
height = 200
def animate_page_change(current_page, next_page, direction, item_frames, items_per_page, total_items, show_page, content_frame, main_window):
    global height
    if direction == 'next' and (next_page * items_per_page < total_items):
        for i in range(items_per_page):
            if current_page * items_per_page + i < total_items:
                frame = item_frames[current_page * items_per_page + i]
                threading.Thread(target=animate_frame, args=(45, -580, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()
        if (next_page + 1) * items_per_page < total_items:
            for i in range(items_per_page):
                if (next_page + 1) * items_per_page + i < total_items:
                    frame = item_frames[(next_page + 1) * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(1250, 670, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()
        current_page = next_page
        show_page(current_page)
        for i in range(items_per_page):
            if current_page * items_per_page + i < total_items:
                frame = item_frames[current_page * items_per_page + i]
                frame.place(x=660, y=((i % items_per_page) * 200) + 10, in_=content_frame)
                threading.Thread(target=animate_frame, args=(1250, 45, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()
    elif direction == 'prev' and (current_page > 0):
        for i in range(items_per_page):
            if current_page * items_per_page + i < total_items:
                frame = item_frames[current_page * items_per_page + i]
                threading.Thread(target=animate_frame, args=(45, 670, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()
        current_page = next_page
        show_page(current_page)
        for i in range(items_per_page):
            if current_page * items_per_page + i < total_items:
                frame = item_frames[current_page * items_per_page + i]
                frame.place(x=45, y=((i % items_per_page) * 200) + 10, in_=content_frame)
                threading.Thread(target=animate_frame, args=(-590, 45, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()
        if current_page > 0:
            for i in range(items_per_page):
                if (current_page - 1) * items_per_page + i < total_items:
                    frame = item_frames[(current_page - 1) * items_per_page + i]
                    threading.Thread(target=animate_frame, args=(-1110, -580, ((i % items_per_page) * height) + 10, frame, 0.05, main_window)).start()

    return current_page


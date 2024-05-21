import customtkinter as ctk
import tkinter as tk
import Baza

def MainWindow(login_window,username_in):
# def MainWindow():
    main_window = ctk.CTk()
    main_window.geometry("1100x600")
    main_window.title("LockBox")
    main_window.resizable(False, False)
    # user = "Krzysztof"
    user = str(username_in)

    def on_closing():
        if main_window:
            try:
                main_window.destroy()
                if login_window and login_window.winfo_exists():
                    login_window.deiconify()
            except tk.TclError:
                pass

    sidebar = ctk.CTkFrame(main_window, 
        width=200, 
        height=600, 
        corner_radius=0)
    
    info_frame = ctk.CTkFrame(main_window, 
        width=900,
        height=30, 
        corner_radius=0)

    hello_label = ctk.CTkLabel(sidebar,
        width= 200,
        height= 80,
        text=("witaj \n"+ user),
        font=("default",24))     
    
    sidebar.place(x=0, y=0)
    info_frame.place(x=200, y=570)
    hello_label.place(x=0, y=25)

    main_window.protocol("WM_DELETE_WINDOW", on_closing)

    main_window.mainloop()

#MainWindow()

from socket import *
import time
import threading
from customtkinter import*


SERVER_HOST = "0.tcp.eu.ngrok.io"
SERVER_PORT = 10274

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('800x600')
        self.title("Tkinter Chat")

        self.frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width=0)
        self.frame.place(x=0, y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame, text="Ваше ім'я")
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack()
        self.label_theme = CTkOptionMenu(self.frame, values=['Темна', 'Світла'], 
                                         command=self.change_theme)
        self.label_theme.pack(side='bottom', pady=20)
        self.theme = None
        self.btn = CTkButton(self, text='▶', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.menu_show_speed = 20

        self.chat_text = CTkTextbox(self, state='disable')
        self.chat_text.place(x=0, y=30)

        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
        self.message_input.place(x=0, y=550)
        self.send_button = CTkButton(self, text='▶', width=40, height=30)
        self.send_button.place(x=400, y=550)

        self.adaptive_ui()

        self.sock = None
        self.connected = False
        threading.Thread(target=self.connected, daemon=True).start()

    def connect(self):
        while not self.connected:
            try:
                self.sock = socket(AF_INET, SOCK_STREAM)
                self.sock.connect((SERVER_HOST, SERVER_PORT))
                name = self.entry.get().strip() or "без імені"
                self.sock.send(name.encode())
                self.add_message(f"Підключено користувача {name}")
                threading.Thread(target=self.receive_message, daemon=True).start()
                break
            except:
                self.add_message(f"Помилка підключення. Повторна спроба через 2 секунди...")
                time.sleep(2)

    def send_message(self):
        if not self.connected:
            self.add_message("Ви не підключені до сервера.")
            return
        msg = self.message_input.get().strip()
        if not msg:
            return
        try:
            self.sock.send(msg.enode())
            self.add_message("Я: " + msg)
        except:
            self.add_message("помилка відправки повідомлення.")
            self.connected = False

        self.message_input.delete(0, END)
    
    def receive_message(self):
        while self.connected:
            try:
                data = self.sock.recv(1024).decode().strip()
                if not data:
                    self.add_message("З'єднання закрито сервером.")
                    break
                self.add_message(data)
            except:
                self.add_message("Втрачене з'єднання з сервером.")
                break
        self.connected = False

    def add_message(self, msg):
        self.chat_text.configure(state="normal")
        self.chat_text.insert(END, msg + "\n")
        self.chat_text.see(END)
        self.chat_text.configure(state="disable")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()
    
    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='◀')
        if self.is_show_menu:
            self.after(20, self.show_menu)
    
    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= self.menu_show_speed
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text='▶')
        if not self.is_show_menu:
            self.after(20, self.close_menu)

    def change_theme(self, value):
        if value == 'Темна':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')

    def adaptive_ui(self):
        self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(),
                                 height=self.winfo_height()-self.message_input.winfo_height()-30)
        self.chat_text.place(x=self.frame.winfo_width() - 1)

        self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_button.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(), 
                                 y=self.winfo_height()-self.send_button.winfo_height())
        
        self.send_button.place(x=self.winfo_width()-self.send_button.winfo_width(),
                               y=self.winfo_height()-self.send_button.winfo_height())
        self.after(20, self.adaptive_ui)
        

if __name__ == "__main__":

    win = MainWindow()
    win.mainloop()

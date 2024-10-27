import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import pymysql


class ChatClient:
    def __init__(self, host, port, friend_username=None, userid=None):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            self.show_error("无法连接至服务器", str(e))
            return

        self.friend_username = friend_username
        self.userid = userid
        self.root = tk.Tk()
        self.root.title(f"与 {friend_username} 聊天")
        self.root.geometry("500x600")  # 设置窗口大小
        self.root.configure(bg="#f0f0f0")  # 设置背景色

        # 使用ttk.Frame创建一个容器
        self.frame = ttk.Frame(self.root)
        self.frame.pack(pady=10)

        self.text_area = tk.Text(self.frame, state='disabled', wrap='word', bg="#ffffff", fg="#7AE7EC",
                                 font=("Arial", 12), bd=1, relief="solid")
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry_message = ttk.Entry(self.frame, font=("Arial", 12))
        self.entry_message.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.button_send = ttk.Button(self.frame, text="发送", command=self.send_message)
        self.button_send.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.root.mainloop()

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def send_message(self):
        message = self.entry_message.get()
        if len(message.encode('utf-8')) > 512:  # 输入内容长度校验
            self.show_error("输入内容过长", "请确保输入内容不超过512字节。")
            return
        if message:
            conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT u.username FROM users u " "WHERE u.user_id = %s ", (self.userid,))
            result = cursor.fetchone()
            if result:
                username = result[0]
                self.client_socket.sendall(f"{username}: {message}".encode())
                self.display_message(f"你: {message}", "right")
                self.entry_message.delete(0, tk.END)

            cursor.close()
            conn.close()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message, "left")
                else:
                    break
            except:
                break

    def display_message(self, message, side):
        self.text_area.config(state='normal')
        if side == "right":
            self.text_area.insert(tk.END, f"{message}\n", "right")
        else:
            self.text_area.insert(tk.END, f"{message}\n", "left")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

        self.text_area.tag_configure("right", justify='right')
        self.text_area.tag_configure("left", justify='left')

    def on_closing(self):
        self.client_socket.close()
        self.root.destroy()


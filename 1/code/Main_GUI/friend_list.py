import tkinter as tk
from tkinter import messagebox, Menu
import pymysql
import Client


class FriendListApp:
    def __init__(self, master, user_id, host, port):
        self.master = master
        self.user_id = user_id
        self.host = host
        self.port = port
        self.master.title("朋友列表")
        self.master.geometry("300x600")
        self.friend_list = []

        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=10)
        self.friend_listbox = tk.Listbox(self.frame, width=50, height=20)
        self.friend_listbox.pack(side=tk.LEFT)
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.friend_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.friend_listbox.yview)

        self.friend_listbox.bind("<Double-1>", self.open_chat)
        self.friend_listbox.bind("<Button-3>", self.show_context_menu)

        self.entry_add_friend = tk.Entry(self.master)
        self.entry_add_friend.pack(pady=5)
        self.button_add_friend = tk.Button(self.master, text="添加好友", command=self.add_friend)
        self.button_add_friend.pack(pady=5)

        self.load_friend_list()
        self.load_pending_requests()

        # Start automatic refreshing
        self.refresh_friend_list()

        self.context_menu = Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="删除好友", command=self.delete_friend)

    def refresh_friend_list(self):
        self.load_friend_list()
        self.load_pending_requests()
        self.master.after(10000, self.refresh_friend_list)

    def show_context_menu(self, event):  # 右键时出现选择框
        self.context_menu.post(event.x_root, event.y_root)

    def delete_friend(self):
        selected_friend = self.friend_listbox.get(self.friend_listbox.curselection())
        if selected_friend and "请求来自:" not in selected_friend:
            friend_username = selected_friend
            conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (friend_username,))
            friend_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM friendship WHERE user_id = %s AND friend_id = %s", (self.user_id, friend_id))
            cursor.execute("DELETE FROM friendship WHERE user_id = %s AND friend_id = %s", (friend_id, self.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("信息", f"{friend_username} 已从好友列表中删除")

    def load_friend_list(self):
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT u.username FROM friendship f JOIN users u ON f.friend_id = u.user_id "
            "WHERE f.user_id = %s AND f.status = 'accepted'", (self.user_id,))
        friends = cursor.fetchall()
        self.friend_listbox.delete(0, tk.END)
        for friend in friends:
            self.friend_listbox.insert(tk.END, friend[0])
        conn.close()

    def load_pending_requests(self):
        """从数据库加载待处理的好友申请"""
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT u.username FROM friendship f JOIN users u ON f.user_id = u.user_id "
            "WHERE f.friend_id = %s AND f.status = 'pending'", (self.user_id,))
        requests = cursor.fetchall()
        for request in requests:
            self.friend_listbox.insert(tk.END, f"请求来自: {request[0]}")
        conn.close()

    def add_friend(self):
        friend_username = self.entry_add_friend.get()
        if not friend_username:
            messagebox.showerror("错误", "请输入好友用户名")  # 非空校验
            return
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (friend_username,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("错误", "用户不存在")
            conn.close()
            return
        friend_id = result[0]
        try:
            cursor.execute("INSERT INTO friendship (user_id, friend_id, status) VALUES (%s, %s, 'pending')",
                           (self.user_id, friend_id))
            conn.commit()
            messagebox.showinfo("信息", "好友申请已发送")
        except pymysql.IntegrityError:
            messagebox.showerror("错误", "已经是好友或请求已发送")
        finally:
            conn.close()

    def open_chat(self, event):
        selected_friend = self.friend_listbox.get(self.friend_listbox.curselection())
        if "请求来自:" in selected_friend:
            self.handle_friend_request(selected_friend)
        else:
            # 调用聊天模块
            Client.ChatClient(self.host, self.port, selected_friend, self.user_id)

    def handle_friend_request(self, request):
        friend_username = request.split(": ")[1]
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (friend_username,))
        friend_id = cursor.fetchone()[0]
        action = messagebox.askyesno("好友请求", f"是否接受来自 {friend_username} 的好友请求?")
        if action:  # 接受
            cursor.execute("UPDATE friendship SET status = 'accepted' WHERE user_id = %s AND friend_id = %s",
                           (friend_id, self.user_id))
            cursor.execute("INSERT INTO friendship (user_id, friend_id, status) VALUES (%s, %s, 'accepted')",
                           (self.user_id, friend_id))  # 双向更新好友列表
            messagebox.showinfo("信息", f"你已与 {friend_username} 成为好友")
        else:  # 拒绝
            cursor.execute("DELETE FROM friendship WHERE user_id = %s AND friend_id = %s",
                           (friend_id, self.user_id))
            messagebox.showinfo("信息", f"已拒绝来自 {friend_username} 的好友请求")
        conn.commit()
        conn.close()

        self.load_friend_list()
        self.load_pending_requests()


def show_friend_list(user_id, host, port):
    root = tk.Tk()
    app = FriendListApp(root, user_id, host, port)
    root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())  # 设置关闭窗口的行为
    root.mainloop()
    return app  # 返回实例

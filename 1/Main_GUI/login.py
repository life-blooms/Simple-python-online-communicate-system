import tkinter as tk
from tkinter import messagebox
import pymysql
import hashlib
import os
import signup
import friend_list

friend_list_app = None  # 用于跟踪好友列表窗口实例

def login():
    global friend_list_app  # 引用全局变量
    user_id = entry_user_id.get()
    password = entry_password.get()  # 用户输入用户名和密码
    if user_id == "" or password == "":
        messagebox.showerror("错误", "请输入用户ID和密码")  # 非空校验
        return
    try:
        user_id = str(user_id)
        password_hash = hashlib.sha256(password.encode()).hexdigest()  # 计算密码哈希值

        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (user_id, password_hash))
        result = cursor.fetchone()  # 密码校验

        if result:
            user_id = result[0]
            cursor.execute("INSERT INTO logs (user_id, action) VALUES (%s, 'login')", (user_id,))  # 日志记录登录信息
            conn.commit()
            messagebox.showinfo("信息", f"登录成功！用户ID：{user_id}")
            friend_list_app = friend_list.show_friend_list(user_id, host='127.0.0.1', port=5555)
        else:
            messagebox.showerror("错误", "用户名或密码错误")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误：{e}")
    finally:
        if conn:
            conn.close()

# 注册按钮
def register():
    login_window.destroy()
    signup.signupWindow()

# 退出按钮
def exit_app():
    global friend_list_app
    try:
        conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
        cursor = conn.cursor()
        user_name = entry_user_id.get()  # 获取当前登录的用户ID
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user_name,))
        user_id = cursor.fetchone()
        if user_id is None:
            messagebox.showerror("错误", "未找到用户ID，无法记录退出日志")
            return
        user_id = user_id[0]  # 从fetchone结果中获取实际的user_id
        cursor.execute("INSERT INTO logs (user_id, action) VALUES (%s, 'logout')", (user_id,))  # 记录用户的登出日志
        conn.commit()
        if friend_list_app is not None:
            friend_list_app.master.destroy()  # 关闭好友列表窗口
        messagebox.showinfo("信息", "退出成功！")
        os._exit(0)  # 结束任务
    except Exception as e:
        messagebox.showerror("错误", f"退出时发生错误：{e}")
    finally:
        if conn:
            conn.close()


# 创建登录窗口
def logwindow():
    global login_window
    global entry_user_id, entry_password

    login_window = tk.Tk()
    login_window.title("在线聊天系统 - 用户登录")
    login_window.geometry("350x260")
    login_window.configure(bg='#f0f0f0')

    label_user_id = tk.Label(login_window, text="用户ID:", bg='#f0f0f0')
    label_user_id.pack(pady=5)
    entry_user_id = tk.Entry(login_window)
    entry_user_id.pack(pady=5)

    label_password = tk.Label(login_window, text="密码:", bg='#f0f0f0')
    label_password.pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    button_login = tk.Button(login_window, text="登录", command=login, bg='#4CAF50', fg='white')
    button_login.pack(pady=5)

    button_register = tk.Button(login_window, text="注册", command=register, bg='#2196F3', fg='white')
    button_register.pack(pady=5)

    button_exit = tk.Button(login_window, text="退出", command=exit_app, bg='#F44336', fg='white')
    button_exit.pack(pady=5)

    login_window.mainloop()

logwindow()

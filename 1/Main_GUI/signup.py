#signup.py
import tkinter as tk
from tkinter import messagebox
import pymysql  # 使用pymysql库连接MySQL
import hashlib  # 用于密码哈希

def signupWindow():
    def register():
        username = entry_username.get()
        password = entry_password.get()
        confirm_password = entry_confirm_password.get()
        email = entry_email.get()
        if not username or not password or not confirm_password or not email:   # 校验用户名和密码是否填写
            messagebox.showerror("错误", "所有必填项必须填写")
            return
        if len(username) < 3:
            messagebox.showerror("错误", "用户名长度必须大于2个字符")
            return
        if password != confirm_password:  # 校验两次密码是否一致
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        if len(password) < 6:   # 密码复杂性校验
            messagebox.showerror("错误", "密码长度必须大于6个字符")
            return
        password_hash = hashlib.sha256(password.encode()).hexdigest()   # 对密码进行哈希处理
        conn = None
        try:
            conn = pymysql.connect(host='localhost', user='root', password='123456', database='chat')
            cursor = conn.cursor()  # 连接到数据库并插入用户信息
            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                           (username, password_hash, email))
            conn.commit()
            messagebox.showinfo("成功", f"注册成功！用户名：{username}")
        except pymysql.IntegrityError:
            messagebox.showerror("错误", "用户名或邮箱已存在，请填写其他信息")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误：{e}")
        finally:
            if conn:
                conn.close()

        signup_window.destroy()
        import login
        login.logwindow()  # 重新打开登录窗口

    # 创建主窗口
    signup_window = tk.Tk()  # 使用Toplevel以避免干扰主循环
    signup_window.title("在线聊天系统 - 用户注册")
    signup_window.geometry("400x400")

    # 创建并放置标签和输入框
    label_username = tk.Label(signup_window, text="用户名 (必填):")
    label_username.pack(pady=5)
    entry_username = tk.Entry(signup_window)
    entry_username.pack(pady=5)

    label_password = tk.Label(signup_window, text="密码 (必填):")
    label_password.pack(pady=5)
    entry_password = tk.Entry(signup_window, show="*")
    entry_password.pack(pady=5)

    label_confirm_password = tk.Label(signup_window, text="确认密码 (必填):")
    label_confirm_password.pack(pady=5)
    entry_confirm_password = tk.Entry(signup_window, show="*")
    entry_confirm_password.pack(pady=5)

    label_email = tk.Label(signup_window, text="邮箱 (必填):")
    label_email.pack(pady=5)
    entry_email = tk.Entry(signup_window)
    entry_email.pack(pady=5)

    # 创建并放置注册按钮
    button_register = tk.Button(signup_window, text="注册", command=register)
    button_register.pack(pady=20)

    # 运行主循环
    signup_window.mainloop()


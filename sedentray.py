
import tkinter as tk
from tkinter import ttk,messagebox
import sqlbase

class SedentaryTab:
    """久坐提醒标签页"""
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.set_minutes = 30
        self.remaining_seconds = 0
        self.running = False
        self.after_job = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.frame)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="设置久坐时间（分钟）:", font=("Arial", 11)).pack(pady=(10, 5))

        self.entry = tk.Entry(main_frame, font=("Arial", 11), width=10)
        self.entry.insert(0, "30")
        self.entry.pack()

        self.start_button = tk.Button(main_frame, text="开始", command=self.start_stop,
                                      width=12, height=2, font=("Arial", 11, "bold"),
                                      bg="white", fg="black", relief="raised", bd=2)
        self.start_button.pack(pady=15)

        self.timer_label = tk.Label(main_frame, text="00:00:00", font=("Arial", 24, "bold"), fg="#E67E22")
        self.timer_label.pack(pady=10)

    def format_time(self, seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def start_stop(self):
        if not self.running:
            try:
                mins = int(self.entry.get())
                if mins <= 0:
                    messagebox.showerror("错误", "时间必须大于0")
                    return
                self.set_minutes = mins
                self.remaining_seconds = mins * 60
                self.timer_label.config(text=self.format_time(self.remaining_seconds))
                self.running = True
                self.start_button.config(text="停止")
                self.update_timer()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的整数")
        else:
            self.running = False
            self.start_button.config(text="开始")
            if self.after_job:
                self.frame.after_cancel(self.after_job)
                self.after_job = None

    def update_timer(self):
        if self.running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.timer_label.config(text=self.format_time(self.remaining_seconds))
            self.after_job = self.frame.after(1000, self.update_timer)
        elif self.remaining_seconds <= 0:
            self.running = False
            self.start_button.config(text="开始")
            if self.after_job:
                self.frame.after_cancel(self.after_job)
                self.after_job = None

            sqlbase.insert_sedentary(self.set_minutes)

            messagebox.showinfo("久坐提醒", "坐太久了，起来活动一下！")
            # 自动重新开始
            self.remaining_seconds = self.set_minutes * 60
            self.running = True
            self.start_button.config(text="停止")
            self.update_timer()
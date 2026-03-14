import tkinter as tk
from tkinter import ttk,messagebox
from database import sqlbase
import time

class WaterTrackerTab:
    """喝水追踪标签页"""
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 数据变量
        self.cup_capacity = 0.0
        self.total_water = 0.0
        self.remaining_cups = 0.0
        self.remaining_ml = 0.0
        self.total_cups = 0.0

        # 计时器相关
        self.has_drunk = False
        self.last_drink_time = None
        self.timer_job = None

        self.setup_ui()
        self.load_today_state() 

    def setup_ui(self):
        # ---------- 主框架：垂直分为上下两部分 ----------
        main_frame = tk.Frame(self.frame)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # ========== 上部区域：左右两栏 ==========
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        # 左侧输入区域
        left_frame = tk.Frame(top_frame)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        tk.Label(left_frame, text="今日饮水量 (ml):", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.water_entry = tk.Entry(left_frame, font=("Arial", 11), width=15)
        self.water_entry.pack(anchor=tk.W, pady=(0, 15))

        tk.Label(left_frame, text="杯子容量 (ml):", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.cup_entry = tk.Entry(left_frame, font=("Arial", 11), width=15)
        self.cup_entry.pack(anchor=tk.W)

        # 右侧显示区域
        right_frame = tk.Frame(top_frame)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))

        tk.Label(right_frame, text="剩余杯数:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.cups_label = tk.Label(right_frame, text="", font=("Arial", 28, "bold"), fg="#2E86C1")
        self.cups_label.pack(anchor=tk.W, pady=(0, 15))

        tk.Label(right_frame, text="剩余毫升数:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.ml_label = tk.Label(right_frame, text="", font=("Arial", 16), fg="#28B463")
        self.ml_label.pack(anchor=tk.W)

        # ========== 底部区域：计时器 + 按钮组 ==========
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        # 计时器标签
        self.timer_label = tk.Label(bottom_frame, text="", font=("Arial", 14), fg="#28B463")
        self.timer_label.pack(side=tk.TOP, pady=(0, 5))

        # 按钮容器
        button_container = tk.Frame(bottom_frame)
        button_container.pack(fill=tk.X)

        # 左侧按钮组
        self.action_button = tk.Button(button_container, text="确 定", command=self.on_action_button_click,
                                       width=12, height=2, font=("Arial", 11, "bold"),
                                       bg="white", fg="black", relief="raised", bd=2)
        self.action_button.pack(side=tk.LEFT)

        # 右侧按钮
        self.drink_button = tk.Button(button_container, text="已喝一杯水", command=self.drink_one,
                                      width=12, height=2, font=("Arial", 11, "bold"),
                                      state=tk.DISABLED, bg="white", fg="black", relief="raised", bd=2)
        self.drink_button.pack(side=tk.RIGHT)

    def update_timer(self):
        if self.has_drunk and self.last_drink_time is not None:
            elapsed = int(time.time() - self.last_drink_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"距离上次喝水已经：{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.timer_job = self.frame.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="")
            if self.timer_job:
                self.frame.after_cancel(self.timer_job)
                self.timer_job = None

    def on_action_button_click(self):
        if self.action_button["text"] == "确 定":
            self.calculate_and_lock()
        else:
            self.unlock_and_reset()

    def calculate_and_lock(self):
        try:
            total_water = float(self.water_entry.get())
            cup_cap = float(self.cup_entry.get())
            if cup_cap <= 0:
                messagebox.showerror("错误", "杯子容量必须大于0")
                return
            if total_water < 0:
                messagebox.showerror("错误", "饮水量不能为负数")
                return

            # 删除今天所有记录（如果有）
            sqlbase.delete_today_records()
             # 插入目标记录
            sqlbase.insert_goal(cup_cap, total_water)

            self.cup_capacity = cup_cap
            self.total_water = total_water
            self.total_cups = total_water / cup_cap
            self.remaining_cups = self.total_cups
            self.remaining_ml = total_water

            self.cups_label.config(text=f"{self.remaining_cups:.1f}/{self.total_cups:.1f}")
            self.ml_label.config(text=f"{self.remaining_ml:.1f} ml")

            self.water_entry.config(state='readonly')
            self.cup_entry.config(state='readonly')

            self.action_button.config(text="修 改")
            self.drink_button.config(state=tk.NORMAL)

            self.has_drunk = False
            self.last_drink_time = None
            self.timer_label.config(text="距离上次喝水已经：00:00:00")
            if self.timer_job:
                self.frame.after_cancel(self.timer_job)
                self.timer_job = None

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def unlock_and_reset(self):

        # 删除今天所有记录
        sqlbase.delete_today_records()

        self.water_entry.config(state='normal')
        self.cup_entry.config(state='normal')

        self.cup_capacity = 0.0
        self.total_water = 0.0
        self.remaining_cups = 0.0
        self.remaining_ml = 0.0

        self.cups_label.config(text="")
        self.ml_label.config(text="")

        self.action_button.config(text="确 定")
        self.drink_button.config(state=tk.DISABLED)

        self.has_drunk = False
        self.last_drink_time = None
        if self.timer_job:
            self.frame.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_label.config(text="")

    def drink_one(self):
        if self.remaining_cups > 0:
            self.remaining_cups -= 1
            self.remaining_ml -= self.cup_capacity
            self.cups_label.config(text=f"{self.remaining_cups:.1f}/{self.total_cups:.1f}")
            self.ml_label.config(text=f"{self.remaining_ml:.1f} ml")

            sqlbase.insert_drink(self.cup_capacity, 1.0, self.total_water)

            if not self.has_drunk:
                self.has_drunk = True
                self.last_drink_time = time.time()
                self.update_timer()
            else:
                self.last_drink_time = time.time()

            if self.remaining_cups <= 0:
                self.drink_button.config(state=tk.DISABLED)
                messagebox.showinfo("完成", "🎉 恭喜你完成今日饮水目标！")
        else:
            messagebox.showinfo("提示", "已经没有剩余杯数了")

    def load_today_state(self):
     """从数据库加载今日目标，恢复界面状态"""
     goal, cup_cap, drunk_cups = sqlbase.get_today_goal_and_progress()
     if goal is not None:
        # 有今日目标
        self.total_water = goal
        self.cup_capacity = cup_cap
        self.total_cups = goal / cup_cap
        self.remaining_cups = self.total_cups - drunk_cups
        self.remaining_ml = self.remaining_cups * cup_cap

        # 填充输入框并锁定
        self.water_entry.config(state='normal')
        self.water_entry.delete(0, tk.END)
        self.water_entry.insert(0, str(goal))
        self.water_entry.config(state='readonly')

        self.cup_entry.config(state='normal')
        self.cup_entry.delete(0, tk.END)
        self.cup_entry.insert(0, str(cup_cap))
        self.cup_entry.config(state='readonly')

        self.action_button.config(text="修 改")
        self.drink_button.config(state=tk.NORMAL if self.remaining_cups > 0 else tk.DISABLED)

        self.cups_label.config(text=f"{self.remaining_cups:.1f}/{self.total_cups:.1f}")
        self.ml_label.config(text=f"{self.remaining_ml:.1f} ml")

        # 计时器从0开始（不恢复上次喝水时间）
        self.has_drunk = False
        self.last_drink_time = None
        self.timer_label.config(text="距离上次喝水已经：00:00:00")
        if self.timer_job:
            self.frame.after_cancel(self.timer_job)
            self.timer_job = None
        # 如果没有今日目标，不做任何事（界面保持空白）
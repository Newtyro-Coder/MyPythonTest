import tkinter as tk
from tkinter import ttk
from database import sqlbase

class HistoryTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
         # 刷新按钮
        btn_refresh = tk.Button(self.frame, text="刷新数据", command=self.refresh_data)
        btn_refresh.pack(pady=5)

        # 喝水记录表格
        tk.Label(self.frame, text="最近30天喝水记录", font=("Arial", 12)).pack(pady=5)
        self.drink_tree = ttk.Treeview(self.frame, columns=("date", "cups", "ml"), show="headings")
        self.drink_tree.heading("date", text="日期")
        self.drink_tree.heading("cups", text="总杯数")
        self.drink_tree.heading("ml", text="总毫升数")
        self.drink_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 久坐记录表格
        tk.Label(self.frame, text="最近30天久坐记录", font=("Arial", 12)).pack(pady=5)
        self.sed_tree = ttk.Treeview(self.frame, columns=("date", "times", "minutes"), show="headings")
        self.sed_tree.heading("date", text="日期")
        self.sed_tree.heading("times", text="次数")
        self.sed_tree.heading("minutes", text="总分钟")
        self.sed_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.refresh_data()
    
    def refresh_data(self):
        # 清空旧数据
        for row in self.drink_tree.get_children():
            self.drink_tree.delete(row)
        for row in self.sed_tree.get_children():
            self.sed_tree.delete(row)
        
        # 插入喝水记录
        drink_rows = sqlbase.get_recent_drinks(30)
        for day, cups, ml in drink_rows:
            if cups is not None:
                self.drink_tree.insert("", "end", values=(day, f"{cups:.1f}", f"{ml:.1f}"))
        
        # 插入久坐记录
        sed_rows = sqlbase.get_recent_sedentary(30)
        for day, times, minutes in sed_rows:
            if times is not None:
                self.sed_tree.insert("", "end", values=(day, times, minutes))
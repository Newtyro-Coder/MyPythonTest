import tkinter as tk
from tkinter import ttk
from database import sqlbase
import matplotlib
matplotlib.use('TkAgg')  # 设置后端为TkAgg，保证在tkinter中嵌入
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = [
    'WenQuanYi Zen Hei',      # Linux 常用
    'SimHei',                  # Windows 黑体
    'Microsoft YaHei',         # Windows 微软雅黑
    'PingFang SC',             # macOS 苹方
    'Heiti SC',                # macOS 黑体
    'Arial Unicode MS',        # 通用
    'DejaVu Sans'              # 后备
]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class HistoryTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # 刷新按钮
        btn_refresh = tk.Button(self.frame, text="刷新数据", command=self.refresh_data)
        btn_refresh.pack(pady=5)

        # 创建 matplotlib 图形和画布
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 初始化绘制空图
        self.refresh_data()
    
    def refresh_data(self):
        """刷新图表数据"""
        # 获取最近30天喝水记录
        drink_rows = sqlbase.get_recent_drinks(30)  # 返回 [(日期, 总杯数, 总毫升数), ...]
        
        # 提取日期和毫升数（或杯数，这里选择毫升数）
        dates = []
        ml_values = []
        for day, cups, ml in drink_rows:
            if ml is not None:
                dates.append(day)
                ml_values.append(ml)
        
        # 清空旧图形
        self.ax.clear()
        
        if dates and ml_values:
            # 绘制折线图
            self.ax.plot(dates, ml_values, marker='o', linestyle='-', color='#2E86C1', linewidth=2)
            self.ax.set_xlabel('日期')
            self.ax.set_ylabel('喝水量 (ml)')
            self.ax.set_title('最近30天喝水趋势')
            self.ax.grid(True, linestyle='--', alpha=0.7)
            # 自动旋转日期标签避免重叠
            self.fig.autofmt_xdate()
        else:
            # 无数据时显示提示
            self.ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', transform=self.ax.transAxes)
            self.ax.set_title('最近30天喝水趋势')
        
        # 刷新画布
        self.canvas.draw()
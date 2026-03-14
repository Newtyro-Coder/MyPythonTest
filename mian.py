import tkinter as tk
from tkinter import ttk

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.watertracker import WaterTrackerTab
from core.sedentray import SedentaryTab
from core.healthhistory import HistoryTab
from database import sqlbase 

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包后的环境"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApp:
    def __init__(self, root):

        sqlbase.init_db()

        self.root = root
        self.root.title("健康助手 1.0")
        self.root.resizable(False, False)

        # 创建 Notebook（标签页控件）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建两个标签页
        self.water_tab = WaterTrackerTab(self.notebook)
        self.sedentary_tab = SedentaryTab(self.notebook)
        self.history_tab = HistoryTab(self.notebook)

        self.notebook.add(self.water_tab.frame, text="喝水追踪")
        self.notebook.add(self.sedentary_tab.frame, text="久坐提醒")
        self.notebook.add(self.history_tab.frame, text="历史记录")

    def refresh_history(self):
        """刷新历史标签页的数据"""
        if hasattr(self, 'history_tab'):
            self.history_tab.refresh_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
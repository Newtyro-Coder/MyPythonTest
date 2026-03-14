import sqlite3
import os
import time
from datetime import datetime


# 数据库文件路径（放在用户主目录或应用目录下）
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "health_assistant.db")

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """初始化数据库表（如果不存在）"""
    conn = get_connection()
    c = conn.cursor()
    
    # 喝水记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS drink_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cup_capacity REAL NOT NULL,     -- 当时杯子容量(ml)
            cup_count REAL DEFAULT 1,       -- 本次喝了几杯（默认1）
            total_goal REAL,                 -- 当日总目标(ml)，可选
            note TEXT                         -- 备注，留作扩展
        )
    ''')
    
    # 久坐记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS sedentary_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            duration_minutes INTEGER NOT NULL,  -- 设置的久坐时间(分钟)
            note TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_drink(cup_capacity, cup_count=1.0, total_goal=None, note=""):
    conn = get_connection()
    c = conn.cursor()
    local_time = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO drink_history (timestamp, cup_capacity, cup_count, total_goal, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (local_time, cup_capacity, cup_count, total_goal, note))
    conn.commit()
    conn.close()

def insert_sedentary(duration_minutes, note=""):
    """插入一条久坐记录（每次提醒触发时）"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO sedentary_history (duration_minutes, note)
        VALUES (?, ?)
    ''', (duration_minutes, note))
    conn.commit()
    conn.close()

def get_recent_drinks(days=30):
    """获取最近days天的喝水记录（按天分组统计）"""
    conn = get_connection()
    c = conn.cursor()
    # 按日期分组，统计总杯数和总毫升数
    c.execute('''
        SELECT date(timestamp) as day, 
               SUM(cup_count) as total_cups,
               SUM(cup_count * cup_capacity) as total_ml
        FROM drink_history
        WHERE timestamp >= datetime('now', ?)
        GROUP BY day
        ORDER BY day DESC
    ''', (f'-{days} days',))
    rows = c.fetchall()
    conn.close()
    return rows

def get_recent_sedentary(days=30):
    """获取最近days天的久坐记录"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT date(timestamp) as day,
               COUNT(*) as times,
               SUM(duration_minutes) as total_minutes
        FROM sedentary_history
        WHERE timestamp >= datetime('now', ?)
        GROUP BY day
        ORDER BY day DESC
    ''', (f'-{days} days',))
    rows = c.fetchall()
    conn.close()
    return rows

def get_today_goal_and_progress():
    """获取今天的目标设定和进度，返回 (goal_ml, cup_capacity, drunk_cups) 或 (None, None, None) 如果没有目标"""
    conn = get_connection()
    c = conn.cursor()
    local_date = time.strftime('%Y-%m-%d')
    # 获取今天第一条记录（按时间升序），假设它是目标设定记录（cup_count=0）
    c.execute('''
        SELECT total_goal, cup_capacity FROM drink_history
        WHERE substr(timestamp, 1, 10) = ?
        ORDER BY timestamp ASC LIMIT 1
    ''', (local_date,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None, None, None
    goal_ml, cup_cap = row
    if goal_ml is None or cup_cap is None:
        conn.close()
        return None, None, None
    # 计算今天已喝总杯数（不包括 cup_count=0 的目标记录）
    c.execute('''
        SELECT SUM(cup_count) FROM drink_history
        WHERE substr(timestamp, 1, 10) = ? AND cup_count > 0
    ''', (local_date,))
    sum_row = c.fetchone()
    drunk_cups = sum_row[0] if sum_row[0] else 0.0
    conn.close()
    return goal_ml, cup_cap, drunk_cups

def delete_today_records():
    """删除今天的所有记录"""
    conn = get_connection()
    c = conn.cursor()
    local_date = time.strftime('%Y-%m-%d')
    c.execute('''
        DELETE FROM drink_history
        WHERE substr(timestamp, 1, 10) = ?
    ''', (local_date,))
    conn.commit()
    conn.close()

def insert_goal(cup_capacity, total_goal):
    """插入一条目标设定记录（cup_count=0）"""
    conn = get_connection()
    c = conn.cursor()
    local_time = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO drink_history (timestamp, cup_capacity, cup_count, total_goal)
        VALUES (?, ?, ?, ?)
    ''', (local_time, cup_capacity, 0, total_goal))
    conn.commit()
    conn.close()
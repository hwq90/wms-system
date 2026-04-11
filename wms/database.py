"""
仓库管理系统 - 数据库模块
负责SQLite数据库连接和表结构定义
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = 'wms.db'


def init_database():
    """初始化数据库，创建所有表"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 物料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material_code TEXT UNIQUE NOT NULL,
                material_name TEXT NOT NULL,
                category TEXT,
                unit TEXT,
                spec TEXT,
                safety_stock REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 批次表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_no TEXT UNIQUE NOT NULL,
                material_id INTEGER NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                warehouse_location TEXT,
                production_date DATE,
                expiry_date DATE,
                supplier TEXT,
                status TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 入库记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_in (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                operator TEXT,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 出库记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_out (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                operator TEXT,
                remark TEXT,
                fifo_order INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 退料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS returns_to_warehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                return_reason TEXT,
                original_out_id INTEGER,
                operator TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 补料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replenishment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                replenish_reason TEXT,
                operator TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 客户退货表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                material_id INTEGER NOT NULL,
                batch_id INTEGER,
                quantity REAL NOT NULL,
                return_type TEXT DEFAULT 'return',
                return_reason TEXT,
                original_order_no TEXT,
                operator TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        # 盘点表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocktaking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stocktaking_no TEXT UNIQUE NOT NULL,
                stocktaking_date DATE NOT NULL,
                operator TEXT,
                status TEXT DEFAULT 'pending',
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 盘点明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocktaking_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stocktaking_id INTEGER NOT NULL,
                batch_id INTEGER NOT NULL,
                material_id INTEGER NOT NULL,
                system_qty REAL NOT NULL,
                actual_qty REAL NOT NULL,
                diff_qty REAL NOT NULL,
                diff_reason TEXT,
                FOREIGN KEY (stocktaking_id) REFERENCES stocktaking(id),
                FOREIGN KEY (batch_id) REFERENCES batches(id),
                FOREIGN KEY (material_id) REFERENCES materials(id)
            )
        ''')
        
        conn.commit()
        print("数据库初始化完成")


@contextmanager
def get_db():
    """获取数据库连接的上下文管理器"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def dict_factory(cursor, row):
    """将查询结果转换为字典"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


if __name__ == '__main__':
    init_database()

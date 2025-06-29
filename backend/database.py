import sqlite3
from datetime import datetime

DATABASE_NAME = 'canteen.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # 创建供应商表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT NOT NULL,
        phone TEXT NOT NULL,
        full_name TEXT,
        supply_items TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建每月供应商表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monthly_suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
        UNIQUE(year, month, supplier_id)
    )
    ''')
    
    # 删除旧的入库记录表
    cursor.execute('DROP TABLE IF EXISTS stock_ins')
    
    # 创建新的入库记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_ins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        supplier TEXT,
        price REAL DEFAULT 0,
        subtotal REAL DEFAULT 0,
        is_daily BOOLEAN DEFAULT 0,
        note TEXT,
        in_time TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建出库记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_outs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        purpose TEXT,
        operator TEXT,
        out_time TEXT DEFAULT CURRENT_TIMESTAMP,
        remarks TEXT
    )
    ''')
    
    # 创建月度报表模板表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        template_data TEXT NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(year, month)
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成")
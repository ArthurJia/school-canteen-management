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
        supply_items TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
        UNIQUE(year, month, supplier_id)
    )
    ''')
    
    # 检查并添加supply_items列（如果不存在）
    try:
        cursor.execute("ALTER TABLE monthly_suppliers ADD COLUMN supply_items TEXT")
    except sqlite3.OperationalError:
        # 列已存在，忽略错误
        pass
    
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
    
    # 删除旧的出库记录表
    cursor.execute('DROP TABLE IF EXISTS stock_outs')
    
    # 创建新的出库记录表（与入库记录表结构相同）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_outs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,                    -- 食材名称
        category TEXT,                         -- 分类
        quantity REAL NOT NULL,                -- 数量
        unit TEXT NOT NULL,                    -- 单位
        supplier TEXT,                         -- 供应商
        price REAL DEFAULT 0,                  -- 单价
        subtotal REAL DEFAULT 0,               -- 小计
        is_daily BOOLEAN DEFAULT 0,            -- 是否为当天类食材
        note TEXT,                             -- 备注
        out_time TEXT DEFAULT CURRENT_TIMESTAMP -- 出库时间
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
    
    # 创建月底库存表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monthly_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建储存类食材明细表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS storage_ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        unit TEXT NOT NULL,
        unit_price REAL NOT NULL,
        specification TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建报表设计器模板表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS designer_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        sheet_data TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成")
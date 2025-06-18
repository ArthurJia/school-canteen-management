import sqlite3

def update_suppliers_table():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    
    # 检查 suppliers 表是否存在 address 列
    cursor.execute("PRAGMA table_info(suppliers)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if 'address' in column_names and 'shortName' not in column_names:
        print("正在更新 suppliers 表结构...")
        
        # 创建新的临时表
        cursor.execute('''
        CREATE TABLE suppliers_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            phone TEXT NOT NULL,
            shortName TEXT,
            supply_items TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 将数据从旧表复制到新表，将 address 列的值复制到 shortName 列
        cursor.execute('''
        INSERT INTO suppliers_new (id, name, contact, phone, shortName, supply_items, created_at)
        SELECT id, name, contact, phone, address, supply_items, created_at FROM suppliers
        ''')
        
        # 删除旧表
        cursor.execute('DROP TABLE suppliers')
        
        # 将新表重命名为原来的表名
        cursor.execute('ALTER TABLE suppliers_new RENAME TO suppliers')
        
        conn.commit()
        print("suppliers 表结构更新完成")
    else:
        print("suppliers 表结构已经是最新的，不需要更新")
    
    conn.close()

if __name__ == '__main__':
    update_suppliers_table()
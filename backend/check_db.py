import sqlite3

def check_database():
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("\nTables in database:")
    for table in tables:
        print(f"\n- {table[0]}")
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 获取表中的记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  Records count: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
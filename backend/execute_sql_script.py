import sqlite3

# 连接到数据库
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# 读取 SQL 脚本，使用 UTF-8 编码
with open('rename_column.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

# 执行 SQL 脚本
try:
    cursor.executescript(sql_script)
    conn.commit()
    print("SQL 脚本执行成功！")
    
    # 验证修改
    cursor.execute("PRAGMA table_info(suppliers)")
    columns = cursor.fetchall()
    
    print("\nSuppliers 表结构:")
    for column in columns:
        print(f"列名: {column[1]}, 类型: {column[2]}")
    
except Exception as e:
    conn.rollback()
    print(f"执行 SQL 脚本时出错: {e}")

# 关闭连接
conn.close()
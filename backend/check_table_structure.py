import sqlite3

# 连接到数据库
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# 查询 suppliers 表的结构
cursor.execute("PRAGMA table_info(suppliers)")
columns = cursor.fetchall()

print("Suppliers 表结构:")
for column in columns:
    print(f"列名: {column[1]}, 类型: {column[2]}")

# 关闭连接
conn.close()
import sqlite3

# 连接到数据库
conn = sqlite3.connect('canteen.db')
cursor = conn.cursor()

# 查询所有不同的类别
cursor.execute('SELECT DISTINCT category FROM stock_ins WHERE category IS NOT NULL AND category != ""')
categories = cursor.fetchall()

print('Categories in database:')
for cat in categories:
    print(f'- {cat[0]}')

# 查询一些示例数据
cursor.execute('SELECT name, category, subtotal FROM stock_ins LIMIT 10')
records = cursor.fetchall()

print('\nSample records:')
for record in records:
    print(f'Name: {record[0]}, Category: {record[1]}, Subtotal: {record[2]}')

# 关闭连接
conn.close()
import sqlite3
import json
import requests
from datetime import datetime

def add_test_data():
    # 连接数据库
    conn = sqlite3.connect('canteen.db')
    cursor = conn.cursor()
    
    # 添加测试供应商
    cursor.execute('''
    INSERT INTO suppliers (name, contact, phone, address, supply_items, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('测试供应商1', '张三', '13800138000', '北京市海淀区', '蔬菜', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    supplier_id = cursor.lastrowid
    print(f"添加供应商成功，ID: {supplier_id}")
    
    # 添加测试每月供应商
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    cursor.execute('''
    INSERT INTO monthly_suppliers (supplier_id, year, month, created_at)
    VALUES (?, ?, ?, ?)
    ''', (supplier_id, current_year, current_month, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    print(f"添加每月供应商成功，年: {current_year}, 月: {current_month}")
    
    # 添加另一个测试供应商和每月记录（上个月）
    cursor.execute('''
    INSERT INTO suppliers (name, contact, phone, address, supply_items, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('测试供应商2', '李四', '13900139000', '上海市浦东新区', '肉类', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    supplier_id2 = cursor.lastrowid
    print(f"添加供应商成功，ID: {supplier_id2}")
    
    # 计算上个月
    last_month = current_month - 1
    last_year = current_year
    if last_month == 0:
        last_month = 12
        last_year -= 1
    
    cursor.execute('''
    INSERT INTO monthly_suppliers (supplier_id, year, month, created_at)
    VALUES (?, ?, ?, ?)
    ''', (supplier_id2, last_year, last_month, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    print(f"添加每月供应商成功，年: {last_year}, 月: {last_month}")
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()

def test_api():
    try:
        # 测试获取所有每月供应商API
        response = requests.get('http://localhost:5000/api/monthly-suppliers/all')
        if response.status_code == 200:
            data = response.json()
            print("\n获取所有每月供应商成功:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"获取所有每月供应商失败，状态码: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"测试API时出错: {str(e)}")

if __name__ == "__main__":
    add_test_data()
    test_api()
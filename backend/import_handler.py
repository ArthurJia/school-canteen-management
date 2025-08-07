import sqlite3
from database import get_db_connection
import json
from datetime import datetime

def import_stock_data(data, mode='append'):
    """
    将库存查询数据导入到SQLite数据库
    
    参数:
    - data: 要导入的数据列表，每个元素是一个字典，包含库存记录的字段
    - mode: 导入模式，'append'(新增数据)或'overwrite'(覆盖数据)
    
    返回:
    - 包含导入结果的字典
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 如果是覆盖模式，先获取现有记录数量，然后清空表
        existing_count = 0
        if mode == 'overwrite':
            cursor.execute('SELECT COUNT(*) FROM stock_ins')
            existing_count = cursor.fetchone()[0]
            cursor.execute('DELETE FROM stock_ins')
        
        # 批量插入数据
        success_count = 0
        failed_count = 0
        
        for item in data:
            try:
                # 计算小计金额
                quantity = float(item.get('quantity', 0))
                price = float(item.get('price', 0))
                subtotal = quantity * price
                
                # 处理入库日期，如果提供则使用，否则使用当前日期
                in_time = item.get('in_time') or datetime.now().strftime('%Y-%m-%d')
                
                cursor.execute('''
                INSERT INTO stock_ins (name, category, quantity, unit, supplier, price, subtotal, is_daily, note, in_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('name', ''),
                    item.get('category', ''),
                    quantity,
                    item.get('unit', 'kg'),
                    item.get('supplier', ''),
                    price,
                    subtotal,
                    1 if item.get('is_daily', False) else 0,
                    item.get('note', ''),
                    in_time
                ))
                success_count += 1
            except Exception as e:
                print(f"Error importing stock item: {str(e)}, item: {item}")
                failed_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'成功导入 {success_count} 条数据' + (f'，失败 {failed_count} 条' if failed_count > 0 else ''),
            'imported': success_count,
            'failed': failed_count,
            'overwritten': existing_count if mode == 'overwrite' else 0
        }
        
    except Exception as e:
        print(f"Error in import_stock_data: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
        raise

def import_inventory_data(data, mode='append'):
    """
    将月底库存数据导入到SQLite数据库
    
    参数:
    - data: 要导入的数据列表，每个元素是一个字典，包含月底库存记录的字段
    - mode: 导入模式，'append'(新增数据)或'overwrite'(覆盖数据)
    
    返回:
    - 包含导入结果的字典
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否存在monthly_inventory表，如果不存在则创建
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL DEFAULT 0,
            quantity REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 如果是覆盖模式，先获取现有记录数量，然后清空表
        existing_count = 0
        if mode == 'overwrite':
            cursor.execute('SELECT COUNT(*) FROM monthly_inventory')
            existing_count = cursor.fetchone()[0]
            cursor.execute('DELETE FROM monthly_inventory')
        
        # 批量插入数据
        success_count = 0
        failed_count = 0
        
        for item in data:
            try:
                cursor.execute('''
                INSERT INTO monthly_inventory (date, name, category, unit_price, quantity)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    item.get('date', datetime.now().strftime('%Y-%m')),
                    item.get('name', ''),
                    item.get('category', ''),
                    float(item.get('unitPrice', 0)),
                    float(item.get('quantity', 0))
                ))
                success_count += 1
            except Exception as e:
                print(f"Error importing inventory item: {str(e)}, item: {item}")
                failed_count += 1
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'成功导入 {success_count} 条数据' + (f'，失败 {failed_count} 条' if failed_count > 0 else ''),
            'imported': success_count,
            'failed': failed_count,
            'overwritten': existing_count if mode == 'overwrite' else 0
        }
        
    except Exception as e:
        print(f"Error in import_inventory_data: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
        raise
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将stock_ins表中的数据复制到stock_outs表中
"""

import sqlite3
from database import get_db_connection

def migrate_stock_data():
    """将stock_ins表中的数据复制到stock_outs表中"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先清空stock_outs表
        cursor.execute('DELETE FROM stock_outs')
        print("已清空stock_outs表")
        
        # 从stock_ins表中获取所有数据
        cursor.execute('''
        SELECT name, category, quantity, unit, supplier, price, subtotal, is_daily, note, in_time
        FROM stock_ins
        ORDER BY in_time
        ''')
        
        stock_ins_data = cursor.fetchall()
        print(f"从stock_ins表中获取到 {len(stock_ins_data)} 条记录")
        
        # 将数据插入到stock_outs表中
        for record in stock_ins_data:
            cursor.execute('''
            INSERT INTO stock_outs (name, category, quantity, unit, supplier, price, subtotal, is_daily, note, out_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', record)
        
        conn.commit()
        print(f"成功将 {len(stock_ins_data)} 条记录复制到stock_outs表中")
        
        # 验证数据
        cursor.execute('SELECT COUNT(*) FROM stock_outs')
        count = cursor.fetchone()[0]
        print(f"stock_outs表中现有 {count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"数据迁移失败: {str(e)}")
        raise

if __name__ == '__main__':
    migrate_stock_data()
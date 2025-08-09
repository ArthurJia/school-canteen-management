#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将outbound_categories表迁移到storage_ingredients表
"""

import sqlite3
from database import get_db_connection

def migrate_outbound_to_storage():
    """将outbound_categories表的数据迁移到storage_ingredients表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查outbound_categories表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='outbound_categories'
        """)
        
        if cursor.fetchone():
            print("发现outbound_categories表，开始迁移数据...")
            
            # 获取outbound_categories表中的所有数据
            cursor.execute("""
                SELECT name, unit, unit_price, specification, created_at, updated_at
                FROM outbound_categories
                ORDER BY id
            """)
            
            old_data = cursor.fetchall()
            print(f"从outbound_categories表中获取到 {len(old_data)} 条记录")
            
            # 创建storage_ingredients表（如果不存在）
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
            
            # 清空storage_ingredients表（如果有数据）
            cursor.execute('DELETE FROM storage_ingredients')
            print("已清空storage_ingredients表")
            
            # 将数据插入到storage_ingredients表中
            for record in old_data:
                cursor.execute('''
                    INSERT INTO storage_ingredients (name, unit, unit_price, specification, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', record)
            
            conn.commit()
            print(f"成功将 {len(old_data)} 条记录迁移到storage_ingredients表中")
            
            # 验证数据
            cursor.execute('SELECT COUNT(*) FROM storage_ingredients')
            count = cursor.fetchone()[0]
            print(f"storage_ingredients表中现有 {count} 条记录")
            
            # 删除旧表
            cursor.execute('DROP TABLE outbound_categories')
            print("已删除outbound_categories表")
            
        else:
            print("未发现outbound_categories表，创建storage_ingredients表...")
            # 创建storage_ingredients表
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
            conn.commit()
            print("storage_ingredients表创建完成")
        
        conn.close()
        print("数据迁移完成！")
        
    except Exception as e:
        print(f"数据迁移失败: {str(e)}")
        raise

if __name__ == '__main__':
    migrate_outbound_to_storage()
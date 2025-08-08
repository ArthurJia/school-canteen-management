#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查迁移后的数据库内容
"""

import sqlite3
from database import get_db_connection

def check_all_tables():
    """检查所有表的数据"""
    print("=== 检查SQLite数据库中的所有数据 ===\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查月底库存数据
        print("1. 月底库存数据 (monthly_inventory):")
        cursor.execute('SELECT * FROM monthly_inventory ORDER BY date DESC, name ASC')
        inventory_records = cursor.fetchall()
        
        if inventory_records:
            print(f"   共 {len(inventory_records)} 条记录:")
            for record in inventory_records:
                print(f"   - {record[1]} | {record[2]} ({record[3]}) | {record[4]}元/{record[6]} | 数量:{record[5]} | 创建时间:{record[7]}")
        else:
            print("   暂无数据")
        
        print()
        
        # 检查出库分类数据
        print("2. 出库分类数据 (outbound_categories):")
        cursor.execute('SELECT * FROM outbound_categories ORDER BY name ASC')
        category_records = cursor.fetchall()
        
        if category_records:
            print(f"   共 {len(category_records)} 条记录:")
            for record in category_records:
                print(f"   - {record[1]} | {record[3]}元/{record[2]} | 规格:{record[4]} | 创建时间:{record[5]}")
        else:
            print("   暂无数据")
        
        print()
        
        # 检查报表设计器模板数据
        print("3. 报表设计器模板数据 (designer_templates):")
        cursor.execute('SELECT id, name, description, created_at FROM designer_templates ORDER BY created_at DESC')
        template_records = cursor.fetchall()
        
        if template_records:
            print(f"   共 {len(template_records)} 个模板:")
            for record in template_records:
                print(f"   - {record[1]} | {record[2]} | 创建时间:{record[3]}")
        else:
            print("   暂无数据")
        
        print()
        
        # 检查其他已有的表
        print("4. 其他数据表统计:")
        
        # 库存查询数据
        cursor.execute('SELECT COUNT(*) FROM stock_ins')
        stock_ins_count = cursor.fetchone()[0]
        print(f"   - 库存查询记录 (stock_ins): {stock_ins_count} 条")
        
        # 供应商数据
        cursor.execute('SELECT COUNT(*) FROM suppliers')
        suppliers_count = cursor.fetchone()[0]
        print(f"   - 供应商记录 (suppliers): {suppliers_count} 条")
        
        # 每月供应商数据
        cursor.execute('SELECT COUNT(*) FROM monthly_suppliers')
        monthly_suppliers_count = cursor.fetchone()[0]
        print(f"   - 每月供应商记录 (monthly_suppliers): {monthly_suppliers_count} 条")
        
        # 出库记录
        cursor.execute('SELECT COUNT(*) FROM stock_outs')
        stock_outs_count = cursor.fetchone()[0]
        print(f"   - 出库记录 (stock_outs): {stock_outs_count} 条")
        
        # 月度报表模板
        cursor.execute('SELECT COUNT(*) FROM report_templates')
        report_templates_count = cursor.fetchone()[0]
        print(f"   - 月度报表模板 (report_templates): {report_templates_count} 条")
        
        print()
        
        # 显示数据库文件信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"5. 数据库表总数: {len(tables)}")
        print("   表名列表:", [table[0] for table in tables])
        
    except Exception as e:
        print(f"检查数据失败: {e}")
    finally:
        conn.close()

def check_specific_table(table_name):
    """检查特定表的数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'SELECT * FROM {table_name}')
        records = cursor.fetchall()
        
        print(f"=== {table_name} 表数据 ===")
        if records:
            # 获取列名
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"列名: {column_names}")
            print(f"记录数: {len(records)}")
            print("数据:")
            for i, record in enumerate(records, 1):
                print(f"  {i}. {record}")
        else:
            print("暂无数据")
            
    except Exception as e:
        print(f"检查表 {table_name} 失败: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        check_specific_table(table_name)
    else:
        check_all_tables()
        
        print("\n=== 使用说明 ===")
        print("1. 查看所有数据: python check_migrated_data.py")
        print("2. 查看特定表: python check_migrated_data.py <table_name>")
        print("   可用的表名: monthly_inventory, outbound_categories, designer_templates")
        print("   其他表名: stock_ins, suppliers, monthly_suppliers, stock_outs, report_templates")
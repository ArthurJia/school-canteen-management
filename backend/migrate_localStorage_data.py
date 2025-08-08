#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：将localStorage数据导入到SQLite数据库
"""

import sqlite3
import json
from datetime import datetime
from database import get_db_connection, init_db

def migrate_monthly_inventory_data():
    """迁移月底库存数据"""
    print("开始迁移月底库存数据...")
    
    # 示例localStorage数据结构（您需要提供实际的数据）
    # 这里提供一些示例数据，您可以替换为实际的localStorage数据
    sample_monthly_inventory = [
        {
            "date": "2025-06",
            "name": "大米",
            "category": "大米",
            "unitPrice": 5.5,
            "quantity": 100,
            "unit": "千克"
        },
        {
            "date": "2025-06",
            "name": "大豆油",
            "category": "食用油类",
            "unitPrice": 12.8,
            "quantity": 20,
            "unit": "升"
        },
        {
            "date": "2025-06",
            "name": "生抽",
            "category": "调味品类",
            "unitPrice": 8.5,
            "quantity": 5,
            "unit": "升"
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in sample_monthly_inventory:
            cursor.execute('''
            INSERT OR REPLACE INTO monthly_inventory (date, name, category, unit_price, quantity, unit)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['date'],
                item['name'],
                item['category'],
                float(item['unitPrice']),
                float(item['quantity']),
                item['unit']
            ))
        
        conn.commit()
        print(f"成功迁移 {len(sample_monthly_inventory)} 条月底库存记录")
        
    except Exception as e:
        print(f"迁移月底库存数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_outbound_categories_data():
    """迁移出库分类数据"""
    print("开始迁移出库分类数据...")
    
    # 示例localStorage数据结构
    sample_outbound_categories = [
        {
            "name": "大米",
            "unit": "千克",
            "unitPrice": 5.5,
            "specification": "优质大米"
        },
        {
            "name": "大豆油",
            "unit": "升",
            "unitPrice": 12.8,
            "specification": "一级大豆油"
        },
        {
            "name": "生抽",
            "unit": "升",
            "unitPrice": 8.5,
            "specification": "酿造生抽"
        },
        {
            "name": "老抽",
            "unit": "升",
            "unitPrice": 9.2,
            "specification": "酿造老抽"
        },
        {
            "name": "盐",
            "unit": "千克",
            "unitPrice": 3.0,
            "specification": "食用盐"
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for category in sample_outbound_categories:
            cursor.execute('''
            INSERT OR REPLACE INTO outbound_categories (name, unit, unit_price, specification)
            VALUES (?, ?, ?, ?)
            ''', (
                category['name'],
                category['unit'],
                float(category['unitPrice']),
                category.get('specification', '')
            ))
        
        conn.commit()
        print(f"成功迁移 {len(sample_outbound_categories)} 条出库分类记录")
        
    except Exception as e:
        print(f"迁移出库分类数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_designer_templates_data():
    """迁移报表设计器模板数据"""
    print("开始迁移报表设计器模板数据...")
    
    # 示例localStorage数据结构
    sample_designer_templates = [
        {
            "name": "月度支出报表模板",
            "description": "用于统计月度各类支出的报表模板",
            "sheetData": json.dumps([{
                "name": "月度报表",
                "color": "",
                "index": 0,
                "status": 1,
                "order": 0,
                "hide": 0,
                "row": 50,
                "column": 50,
                "defaultRowHeight": 19,
                "defaultColWidth": 73,
                "celldata": [],
                "config": {},
                "scrollLeft": 0,
                "scrollTop": 0,
                "luckysheet_select_save": [],
                "calcChain": [],
                "isPivotTable": False,
                "pivotTable": {},
                "filter_select": {},
                "filter": None,
                "luckysheet_alternateformat_save": [],
                "luckysheet_alternateformat_save_modelCustom": [],
                "luckysheet_conditionformat_save": {},
                "frozen": {},
                "chart": [],
                "zoomRatio": 1,
                "image": [],
                "showGridLines": 1,
                "dataVerification": {}
            }])
        },
        {
            "name": "季度出库统计模板",
            "description": "用于统计季度出库情况的报表模板",
            "sheetData": json.dumps([{
                "name": "季度统计",
                "color": "",
                "index": 0,
                "status": 1,
                "order": 0,
                "hide": 0,
                "row": 30,
                "column": 20,
                "defaultRowHeight": 19,
                "defaultColWidth": 73,
                "celldata": [],
                "config": {},
                "scrollLeft": 0,
                "scrollTop": 0,
                "luckysheet_select_save": [],
                "calcChain": [],
                "isPivotTable": False,
                "pivotTable": {},
                "filter_select": {},
                "filter": None,
                "luckysheet_alternateformat_save": [],
                "luckysheet_alternateformat_save_modelCustom": [],
                "luckysheet_conditionformat_save": {},
                "frozen": {},
                "chart": [],
                "zoomRatio": 1,
                "image": [],
                "showGridLines": 1,
                "dataVerification": {}
            }])
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for template in sample_designer_templates:
            cursor.execute('''
            INSERT INTO designer_templates (name, description, sheet_data)
            VALUES (?, ?, ?)
            ''', (
                template['name'],
                template['description'],
                template['sheetData']
            ))
        
        conn.commit()
        print(f"成功迁移 {len(sample_designer_templates)} 个报表设计器模板")
        
    except Exception as e:
        print(f"迁移报表设计器模板数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def import_from_json_file(file_path, data_type):
    """从JSON文件导入数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data_type == 'monthly_inventory':
            import_monthly_inventory_from_data(data)
        elif data_type == 'outbound_categories':
            import_outbound_categories_from_data(data)
        elif data_type == 'designer_templates':
            import_designer_templates_from_data(data)
        else:
            print(f"未知的数据类型: {data_type}")
            
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在")
    except json.JSONDecodeError:
        print(f"文件 {file_path} 不是有效的JSON格式")
    except Exception as e:
        print(f"导入文件 {file_path} 失败: {e}")

def import_monthly_inventory_from_data(data):
    """从数据导入月底库存"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in data:
            cursor.execute('''
            INSERT OR REPLACE INTO monthly_inventory (date, name, category, unit_price, quantity, unit)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                item['date'],
                item['name'],
                item['category'],
                float(item['unitPrice']),
                float(item['quantity']),
                item['unit']
            ))
        
        conn.commit()
        print(f"成功导入 {len(data)} 条月底库存记录")
        
    except Exception as e:
        print(f"导入月底库存数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def import_outbound_categories_from_data(data):
    """从数据导入出库分类"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for category in data:
            cursor.execute('''
            INSERT OR REPLACE INTO outbound_categories (name, unit, unit_price, specification)
            VALUES (?, ?, ?, ?)
            ''', (
                category['name'],
                category['unit'],
                float(category['unitPrice']),
                category.get('specification', '')
            ))
        
        conn.commit()
        print(f"成功导入 {len(data)} 条出库分类记录")
        
    except Exception as e:
        print(f"导入出库分类数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def import_designer_templates_from_data(data):
    """从数据导入报表设计器模板"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for template in data:
            # 如果sheetData是对象，转换为JSON字符串
            sheet_data = template['sheetData']
            if isinstance(sheet_data, (dict, list)):
                sheet_data = json.dumps(sheet_data)
            
            cursor.execute('''
            INSERT INTO designer_templates (name, description, sheet_data)
            VALUES (?, ?, ?)
            ''', (
                template['name'],
                template.get('description', ''),
                sheet_data
            ))
        
        conn.commit()
        print(f"成功导入 {len(data)} 个报表设计器模板")
        
    except Exception as e:
        print(f"导入报表设计器模板数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def verify_migration():
    """验证迁移结果"""
    print("\n验证迁移结果...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查月底库存数据
        cursor.execute('SELECT COUNT(*) FROM monthly_inventory')
        inventory_count = cursor.fetchone()[0]
        print(f"月底库存记录数: {inventory_count}")
        
        # 检查出库分类数据
        cursor.execute('SELECT COUNT(*) FROM outbound_categories')
        categories_count = cursor.fetchone()[0]
        print(f"出库分类记录数: {categories_count}")
        
        # 检查报表设计器模板数据
        cursor.execute('SELECT COUNT(*) FROM designer_templates')
        templates_count = cursor.fetchone()[0]
        print(f"报表设计器模板数: {templates_count}")
        
        # 显示一些示例数据
        print("\n月底库存示例数据:")
        cursor.execute('SELECT date, name, category, unit_price, quantity, unit FROM monthly_inventory LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]} ({row[2]}) - {row[3]}元/{row[5]} - 数量:{row[4]}")
        
        print("\n出库分类示例数据:")
        cursor.execute('SELECT name, unit, unit_price, specification FROM outbound_categories LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[2]}元/{row[1]} - {row[3]}")
        
        print("\n报表设计器模板示例数据:")
        cursor.execute('SELECT name, description FROM designer_templates LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]}")
            
    except Exception as e:
        print(f"验证迁移结果失败: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("=== localStorage数据迁移到SQLite数据库 ===\n")
    
    # 初始化数据库
    print("初始化数据库...")
    init_db()
    
    # 迁移示例数据
    migrate_monthly_inventory_data()
    migrate_outbound_categories_data()
    migrate_designer_templates_data()
    
    # 验证迁移结果
    verify_migration()
    
    print("\n=== 数据迁移完成 ===")
    print("\n如果您有实际的localStorage数据，请按以下步骤操作：")
    print("1. 将localStorage数据导出为JSON文件")
    print("2. 使用以下命令导入数据：")
    print("   python migrate_localStorage_data.py --import monthly_inventory.json monthly_inventory")
    print("   python migrate_localStorage_data.py --import outbound_categories.json outbound_categories")
    print("   python migrate_localStorage_data.py --import designer_templates.json designer_templates")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--import':
        if len(sys.argv) != 4:
            print("用法: python migrate_localStorage_data.py --import <json_file> <data_type>")
            print("data_type可以是: monthly_inventory, outbound_categories, designer_templates")
            sys.exit(1)
        
        json_file = sys.argv[2]
        data_type = sys.argv[3]
        
        print(f"从文件 {json_file} 导入 {data_type} 数据...")
        init_db()
        import_from_json_file(json_file, data_type)
        verify_migration()
    else:
        main()
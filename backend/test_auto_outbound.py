#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当天类食材自动出库功能
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_daily_ingredient_auto_outbound():
    """测试当天类食材入库时自动出库"""
    print("测试当天类食材自动出库功能...")
    
    # 先获取当前出库记录数量
    response = requests.get(f'{BASE_URL}/api/stock-outs')
    initial_count = len(response.json().get('data', []))
    print(f"初始出库记录数量: {initial_count}")
    
    # 创建当天类食材入库记录
    data = {
        'name': '新鲜蔬菜',
        'category': 'vegetable',  # 当天类食材
        'quantity': 15.0,
        'unit': 'kg',
        'supplier': 'hetianyu',
        'price': 3.5,
        'note': '测试当天类食材自动出库',
        'stockInDate': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        # 创建入库记录
        response = requests.post(f'{BASE_URL}/api/stock-ins', json=data)
        print(f"入库请求状态码: {response.status_code}")
        print(f"入库响应: {response.json()}")
        
        if response.status_code == 201:
            print("✅ 入库记录创建成功")
            
            # 检查是否自动创建了出库记录
            response = requests.get(f'{BASE_URL}/api/stock-outs')
            if response.status_code == 200:
                current_count = len(response.json().get('data', []))
                print(f"当前出库记录数量: {current_count}")
                
                if current_count > initial_count:
                    print("✅ 当天类食材自动出库功能正常工作")
                    
                    # 显示最新的出库记录
                    latest_record = response.json()['data'][0]  # 按时间倒序，第一个是最新的
                    print(f"最新出库记录: {latest_record['name']} - {latest_record['quantity']}{latest_record['unit']}")
                    return True
                else:
                    print("❌ 当天类食材没有自动出库")
                    return False
            else:
                print("❌ 无法获取出库记录")
                return False
        else:
            print("❌ 入库记录创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_storage_ingredient_no_auto_outbound():
    """测试储存类食材入库时不自动出库"""
    print("\n测试储存类食材不自动出库功能...")
    
    # 先获取当前出库记录数量
    response = requests.get(f'{BASE_URL}/api/stock-outs')
    initial_count = len(response.json().get('data', []))
    print(f"初始出库记录数量: {initial_count}")
    
    # 创建储存类食材入库记录
    data = {
        'name': '优质大米',
        'category': 'rice',  # 储存类食材
        'quantity': 50.0,
        'unit': 'kg',
        'supplier': 'tiangu',
        'price': 4.0,
        'note': '测试储存类食材不自动出库',
        'stockInDate': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        # 创建入库记录
        response = requests.post(f'{BASE_URL}/api/stock-ins', json=data)
        print(f"入库请求状态码: {response.status_code}")
        print(f"入库响应: {response.json()}")
        
        if response.status_code == 201:
            print("✅ 入库记录创建成功")
            
            # 检查出库记录数量是否保持不变
            response = requests.get(f'{BASE_URL}/api/stock-outs')
            if response.status_code == 200:
                current_count = len(response.json().get('data', []))
                print(f"当前出库记录数量: {current_count}")
                
                if current_count == initial_count:
                    print("✅ 储存类食材正确地没有自动出库")
                    return True
                else:
                    print("❌ 储存类食材意外地自动出库了")
                    return False
            else:
                print("❌ 无法获取出库记录")
                return False
        else:
            print("❌ 入库记录创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试自动出库功能...")
    print("=" * 50)
    
    # 测试各个功能
    tests = [
        test_daily_ingredient_auto_outbound,
        test_storage_ingredient_no_auto_outbound
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 自动出库功能工作正常！")
    else:
        print("⚠️  自动出库功能存在问题，请检查实现")

if __name__ == '__main__':
    main()
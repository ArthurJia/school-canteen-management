#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试出库管理API接口
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_create_stock_out():
    """测试创建出库记录"""
    print("测试创建出库记录...")
    
    data = {
        'name': '测试食材',
        'category': 'vegetable',
        'quantity': 10.5,
        'unit': 'kg',
        'supplier': 'maidelong',
        'price': 5.0,
        'note': '测试出库记录',
        'stockOutDate': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/stock-outs', json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        if response.status_code == 201:
            print("✅ 创建出库记录成功")
            return True
        else:
            print("❌ 创建出库记录失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_get_stock_outs():
    """测试获取出库记录列表"""
    print("\n测试获取出库记录列表...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/stock-outs')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data.get('data', []))} 条出库记录")
            print("✅ 获取出库记录列表成功")
            return True
        else:
            print("❌ 获取出库记录列表失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_get_today_out_category_totals():
    """测试获取今日出库分类总计"""
    print("\n测试获取今日出库分类总计...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/stock-outs/category-totals/today')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"今日出库分类总计: {data}")
            print("✅ 获取今日出库分类总计成功")
            return True
        else:
            print("❌ 获取今日出库分类总计失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_get_month_out_category_totals():
    """测试获取本月出库分类总计"""
    print("\n测试获取本月出库分类总计...")
    
    try:
        response = requests.get(f'{BASE_URL}/api/stock-outs/category-totals/month')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"本月出库分类总计: {data}")
            print("✅ 获取本月出库分类总计成功")
            return True
        else:
            print("❌ 获取本月出库分类总计失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试出库管理API接口...")
    print("=" * 50)
    
    # 测试各个接口
    tests = [
        test_create_stock_out,
        test_get_stock_outs,
        test_get_today_out_category_totals,
        test_get_month_out_category_totals
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
    else:
        print("⚠️  部分测试失败，请检查API实现")

if __name__ == '__main__':
    main()
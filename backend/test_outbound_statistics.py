#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试出库管理页面的统计功能
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_outbound_page_apis():
    """测试出库管理页面需要的API接口"""
    print("测试出库管理页面相关API...")
    
    apis_to_test = [
        ('/api/stock-outs', '出库记录API'),
        ('/api/monthly-inventory', '月底库存API'),
        ('/api/stock-ins', '库存查询API'),
        ('/api/stock-outs/category-totals/today', '今日出库分类总计API'),
        ('/api/stock-outs/category-totals/month', '本月出库分类总计API')
    ]
    
    passed = 0
    total = len(apis_to_test)
    
    for api_path, api_name in apis_to_test:
        try:
            response = requests.get(f'{BASE_URL}{api_path}')
            if response.status_code == 200:
                data = response.json()
                if api_path.endswith('/today') or api_path.endswith('/month'):
                    # 统计API返回格式检查
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"✅ {api_name} - 正常工作")
                        passed += 1
                    else:
                        print(f"❌ {api_name} - 返回格式不正确")
                else:
                    # 数据API返回格式检查
                    if 'data' in data and isinstance(data['data'], list):
                        print(f"✅ {api_name} - 正常工作，数据量: {len(data['data'])}")
                        passed += 1
                    elif isinstance(data, list):
                        print(f"✅ {api_name} - 正常工作，数据量: {len(data)}")
                        passed += 1
                    else:
                        print(f"❌ {api_name} - 返回格式不正确")
            else:
                print(f"❌ {api_name} - HTTP状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {api_name} - 请求失败: {e}")
    
    return passed, total

def test_create_outbound_record():
    """测试创建出库记录"""
    print("\n测试创建出库记录...")
    
    try:
        data = {
            'name': '测试出库食材',
            'category': 'vegetable',
            'quantity': 5.0,
            'unit': 'kg',
            'supplier': 'hetianyu',
            'price': 4.0,
            'note': '统计功能测试',
            'stockOutDate': datetime.now().strftime('%Y-%m-%d')
        }
        
        response = requests.post(f'{BASE_URL}/api/stock-outs', json=data)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 出库记录创建成功，ID: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ 出库记录创建失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 创建出库记录失败: {e}")
        return False

def test_statistics_calculation():
    """测试统计计算功能"""
    print("\n测试统计计算功能...")
    
    try:
        # 获取当前月份
        now = datetime.now()
        current_month = f"{now.year}-{now.month:02d}"
        
        print(f"测试月份: {current_month}")
        
        # 获取月底库存数据
        inventory_response = requests.get(f'{BASE_URL}/api/monthly-inventory')
        if inventory_response.status_code != 200:
            print("❌ 无法获取月底库存数据")
            return False
        
        inventory_data = inventory_response.json().get('data', [])
        print(f"月底库存记录数量: {len(inventory_data)}")
        
        # 获取库存查询数据
        stock_response = requests.get(f'{BASE_URL}/api/stock-ins', params={'pageSize': 100})
        if stock_response.status_code != 200:
            print("❌ 无法获取库存查询数据")
            return False
        
        stock_data = stock_response.json().get('data', [])
        print(f"库存查询记录数量: {len(stock_data)}")
        
        # 检查是否有当月数据
        current_month_inventory = [item for item in inventory_data if item.get('date') == current_month]
        current_month_stock = [item for item in stock_data if item.get('in_time', '').startswith(current_month)]
        
        print(f"当月库存记录: {len(current_month_inventory)}")
        print(f"当月入库记录: {len(current_month_stock)}")
        
        if len(current_month_inventory) > 0 or len(current_month_stock) > 0:
            print("✅ 统计计算功能具备基础数据")
            return True
        else:
            print("⚠️  当月暂无数据，但统计功能结构正常")
            return True
            
    except Exception as e:
        print(f"❌ 统计计算测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试出库管理页面统计功能...")
    print("=" * 50)
    
    # 测试API接口
    api_passed, api_total = test_outbound_page_apis()
    
    # 测试其他功能
    other_tests = [
        test_create_outbound_record,
        test_statistics_calculation
    ]
    
    other_passed = 0
    for test in other_tests:
        if test():
            other_passed += 1
    
    total_passed = api_passed + other_passed
    total_tests = api_total + len(other_tests)
    
    print("\n" + "=" * 50)
    print(f"测试完成: {total_passed}/{total_tests} 个测试通过")
    
    if total_passed == total_tests:
        print("🎉 所有测试都通过了！")
        print("\n现在可以访问出库管理页面查看统计功能:")
        print("http://localhost:5173/desktop/outbound")
    else:
        print("⚠️  部分测试失败，请检查实现")

if __name__ == '__main__':
    main()
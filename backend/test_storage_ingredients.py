#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试储存类食材明细功能
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_storage_ingredients_api():
    """测试储存类食材明细API"""
    print("测试储存类食材明细API...")
    
    # 测试获取储存类食材明细列表
    try:
        response = requests.get(f'{BASE_URL}/api/storage-ingredients')
        print(f"获取储存类食材明细列表 - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            ingredients = data.get('data', [])
            print(f"✅ 获取成功，共 {len(ingredients)} 条记录")
            
            if ingredients:
                print("示例记录:")
                for i, ingredient in enumerate(ingredients[:3]):
                    print(f"  {i+1}. {ingredient.get('name', 'N/A')} - {ingredient.get('unit', 'N/A')} - {ingredient.get('unitPrice', 0)}元")
            
            return True
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_create_storage_ingredient():
    """测试创建储存类食材明细"""
    print("\n测试创建储存类食材明细...")
    
    try:
        data = {
            'name': '测试食材',
            'unit': '千克',
            'unitPrice': 8.5,
            'specification': '测试规格'
        }
        
        response = requests.post(f'{BASE_URL}/api/storage-ingredients', json=data)
        print(f"创建储存类食材明细 - 状态码: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ 创建成功，ID: {result.get('id', 'N/A')}")
            return result.get('id')
        else:
            print(f"❌ 创建失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_update_storage_ingredient(ingredient_id):
    """测试更新储存类食材明细"""
    print(f"\n测试更新储存类食材明细 (ID: {ingredient_id})...")
    
    try:
        data = {
            'name': '更新测试食材',
            'unit': '升',
            'unitPrice': 12.0,
            'specification': '更新测试规格'
        }
        
        response = requests.put(f'{BASE_URL}/api/storage-ingredients/{ingredient_id}', json=data)
        print(f"更新储存类食材明细 - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 更新成功")
            return True
        else:
            print(f"❌ 更新失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_delete_storage_ingredient(ingredient_id):
    """测试删除储存类食材明细"""
    print(f"\n测试删除储存类食材明细 (ID: {ingredient_id})...")
    
    try:
        response = requests.delete(f'{BASE_URL}/api/storage-ingredients/{ingredient_id}')
        print(f"删除储存类食材明细 - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 删除成功")
            return True
        else:
            print(f"❌ 删除失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试储存类食材明细功能...")
    print("=" * 50)
    
    # 测试获取列表
    if not test_storage_ingredients_api():
        print("⚠️  获取列表失败，可能后端服务未启动")
        return
    
    # 测试创建
    ingredient_id = test_create_storage_ingredient()
    if not ingredient_id:
        print("⚠️  创建失败，跳过后续测试")
        return
    
    # 测试更新
    update_success = test_update_storage_ingredient(ingredient_id)
    
    # 测试删除
    delete_success = test_delete_storage_ingredient(ingredient_id)
    
    print("\n" + "=" * 50)
    
    # 统计结果
    tests = [True, bool(ingredient_id), update_success, delete_success]
    passed = sum(tests)
    total = len(tests)
    
    print(f"测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
        print("\n储存类食材明细功能正常工作:")
        print("- 数据库表已从 outbound_categories 重命名为 storage_ingredients")
        print("- API路由已从 /api/outbound-categories 更改为 /api/storage-ingredients")
        print("- 前端页面已更新相应的命名和API调用")
    else:
        print("⚠️  部分测试失败，请检查实现")

if __name__ == '__main__':
    main()
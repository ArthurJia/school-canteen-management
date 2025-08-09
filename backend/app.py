from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from database import get_db_connection
from import_handler import import_stock_data, import_inventory_data

app = Flask(__name__)
# 增强CORS配置
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

@app.route('/api/stock-ins', methods=['POST'])
def create_stock_in():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['name', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 计算小计金额
        quantity = float(data['quantity'])
        price = float(data.get('price', 0))
        subtotal = quantity * price

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 处理入库日期，如果提供则使用，否则使用当前日期
        in_time = data.get('stockInDate') or datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
        INSERT INTO stock_ins (name, category, quantity, unit, supplier, price, subtotal, is_daily, note, in_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('category', ''),
            quantity,
            data['unit'],
            data.get('supplier', ''),
            price,
            subtotal,
            1 if data.get('is_daily', False) else 0,
            data.get('note', ''),  # 前端使用note字段
            in_time
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        
        # 如果是当天类食材，自动创建出库记录
        is_daily = data.get('is_daily', False)
        if is_daily:
            try:
                cursor.execute('''
                INSERT INTO stock_outs (name, category, quantity, unit, supplier, price, subtotal, is_daily, note, out_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['name'],
                    data.get('category', ''),
                    quantity,
                    data['unit'],
                    data.get('supplier', ''),
                    price,
                    subtotal,
                    1,  # 当天类食材
                    data.get('note', ''),
                    in_time  # 使用相同的时间
                ))
                conn.commit()
                print(f"当天类食材 {data['name']} 已自动出库")
            except Exception as e:
                print(f"自动出库失败: {str(e)}")
                # 不影响入库操作，只记录错误
        
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating stock in: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-ins', methods=['GET'])
def get_stock_ins():
    try:
        # 获取查询参数
        start_time = request.args.get('startTime')
        end_time = request.args.get('endTime')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        query = 'SELECT * FROM stock_ins'
        count_query = 'SELECT COUNT(*) FROM stock_ins'
        params = []
        where_clauses = []
        
        if start_time or end_time:
            if start_time:
                where_clauses.append('date(in_time) >= date(?)')
                params.append(start_time)
            if end_time:
                where_clauses.append('date(in_time) <= date(?)')
                params.append(end_time)
        
        if search:
            where_clauses.append('(name LIKE ? OR category LIKE ? OR supplier LIKE ?)')
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
            count_query += ' WHERE ' + ' AND '.join(where_clauses)
        
        query += ' ORDER BY in_time DESC LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        # 执行查询获取数据
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 执行查询获取总数
        cursor.execute(count_query, params[:len(params)-2] if where_clauses else [])
        total = cursor.fetchone()[0]
        
        # 将记录转换为字典列表，并查询对应的出库时间
        stock_ins = []
        for record in records:
            stock_in = {
                'id': record[0],
                'name': record[1],
                'category': record[2],
                'quantity': float(record[3]),  # 确保数字类型正确
                'unit': record[4],
                'supplier': record[5],
                'price': float(record[6]),     # 确保数字类型正确
                'subtotal': float(record[7]),  # 确保数字类型正确
                'is_daily': bool(record[8]),
                'note': record[9],
                'in_time': record[10],
                'out_time': None  # 默认为None
            }
            
            # 查询对应的出库时间（基于相同的食材名称、分类、供应商和日期）
            cursor.execute('''
                SELECT out_time FROM stock_outs 
                WHERE name = ? AND category = ? AND supplier = ? 
                AND date(out_time) = date(?) 
                AND quantity = ? AND price = ?
                ORDER BY out_time DESC 
                LIMIT 1
            ''', (record[1], record[2], record[5], record[10], record[3], record[6]))
            
            out_record = cursor.fetchone()
            if out_record:
                stock_in['out_time'] = out_record[0]
            
            stock_ins.append(stock_in)
        
        conn.close()
        
        return jsonify({
            'data': stock_ins,
            'total': total,
            'page': page,
            'pageSize': page_size
        })
        
    except Exception as e:
        print(f"Error fetching stock-ins: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-ins/<int:stock_in_id>', methods=['PUT'])
def update_stock_in(stock_in_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['name', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 计算小计金额
        quantity = float(data['quantity'])
        price = float(data.get('price', 0))
        subtotal = quantity * price

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新库存记录
        cursor.execute('''
        UPDATE stock_ins 
        SET name = ?, 
            category = ?, 
            quantity = ?, 
            unit = ?, 
            supplier = ?, 
            price = ?, 
            subtotal = ?, 
            is_daily = ?, 
            note = ?, 
            in_time = ?
        WHERE id = ?
        ''', (
            data['name'],
            data.get('category', ''),
            quantity,
            data['unit'],
            data.get('supplier', ''),
            price,
            subtotal,
            1 if data.get('is_daily', False) else 0,
            data.get('note', ''),
            data.get('in_time', ''),
            stock_in_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Stock record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating stock record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-ins/<int:stock_in_id>', methods=['DELETE'])
def delete_stock_in(stock_in_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除指定的库存记录
        cursor.execute('DELETE FROM stock_ins WHERE id = ?', (stock_in_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Stock record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting stock record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-ins/all', methods=['DELETE'])
def delete_all_stock_ins():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除所有库存记录
        cursor.execute('DELETE FROM stock_ins')
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'成功删除 {deleted_count} 条库存记录',
            'deletedCount': deleted_count
        }), 200
        
    except Exception as e:
        print(f"Error deleting all stock records: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs', methods=['POST'])
def create_stock_out():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['name', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 计算小计金额
        quantity = float(data['quantity'])
        price = float(data.get('price', 0))
        subtotal = quantity * price

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 处理出库日期，如果提供则使用，否则使用当前日期
        out_time = data.get('stockOutDate') or datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
        INSERT INTO stock_outs (name, category, quantity, unit, supplier, price, subtotal, is_daily, note, out_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('category', ''),
            quantity,
            data['unit'],
            data.get('supplier', ''),
            price,
            subtotal,
            1 if data.get('is_daily', False) else 0,
            data.get('note', ''),  # 前端使用note字段
            out_time
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating stock out: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs', methods=['GET'])
def get_stock_outs():
    try:
        # 获取查询参数
        start_time = request.args.get('startTime')
        end_time = request.args.get('endTime')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询条件
        query = 'SELECT * FROM stock_outs'
        count_query = 'SELECT COUNT(*) FROM stock_outs'
        params = []
        where_clauses = []
        
        if start_time or end_time:
            if start_time:
                where_clauses.append('date(out_time) >= date(?)')
                params.append(start_time)
            if end_time:
                where_clauses.append('date(out_time) <= date(?)')
                params.append(end_time)
        
        if search:
            where_clauses.append('(name LIKE ? OR category LIKE ? OR supplier LIKE ?)')
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
            count_query += ' WHERE ' + ' AND '.join(where_clauses)
        
        query += ' ORDER BY out_time DESC LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        # 执行查询获取数据
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 执行查询获取总数
        cursor.execute(count_query, params[:len(params)-2] if where_clauses else [])
        total = cursor.fetchone()[0]
        
        # 将记录转换为字典列表
        stock_outs = []
        for record in records:
            stock_out = {
                'id': record[0],
                'name': record[1],
                'category': record[2],
                'quantity': float(record[3]),  # 确保数字类型正确
                'unit': record[4],
                'supplier': record[5],
                'price': float(record[6]),     # 确保数字类型正确
                'subtotal': float(record[7]),  # 确保数字类型正确
                'is_daily': bool(record[8]),
                'note': record[9],
                'out_time': record[10]
            }
            stock_outs.append(stock_out)
        
        conn.close()
        
        return jsonify({
            'data': stock_outs,
            'total': total,
            'page': page,
            'pageSize': page_size
        })
        
    except Exception as e:
        print(f"Error fetching stock-outs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs/<int:stock_out_id>', methods=['PUT'])
def update_stock_out(stock_out_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['name', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # 计算小计金额
        quantity = float(data['quantity'])
        price = float(data.get('price', 0))
        subtotal = quantity * price

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 更新出库记录
        cursor.execute('''
        UPDATE stock_outs 
        SET name = ?, 
            category = ?, 
            quantity = ?, 
            unit = ?, 
            supplier = ?, 
            price = ?, 
            subtotal = ?, 
            is_daily = ?, 
            note = ?, 
            out_time = ?
        WHERE id = ?
        ''', (
            data['name'],
            data.get('category', ''),
            quantity,
            data['unit'],
            data.get('supplier', ''),
            price,
            subtotal,
            1 if data.get('is_daily', False) else 0,
            data.get('note', ''),
            data.get('out_time', ''),
            stock_out_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Stock out record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating stock out record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs/<int:stock_out_id>', methods=['DELETE'])
def delete_stock_out(stock_out_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除指定的出库记录
        cursor.execute('DELETE FROM stock_outs WHERE id = ?', (stock_out_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Stock out record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting stock out record: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs/all', methods=['DELETE'])
def delete_all_stock_outs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除所有出库记录
        cursor.execute('DELETE FROM stock_outs')
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'成功删除 {deleted_count} 条出库记录',
            'deletedCount': deleted_count
        }), 200
        
    except Exception as e:
        print(f"Error deleting all stock out records: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs/category-totals/today', methods=['GET'])
def get_today_out_category_totals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取今日各分类的出库总计
        cursor.execute('''
            SELECT 
                category,
                ROUND(SUM(subtotal), 2) as total
            FROM stock_outs 
            WHERE date(out_time) = date('now', 'localtime')
            GROUP BY category
            ORDER BY total DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        totals = [{'category': record[0] or '未分类', 'total': float(record[1])} for record in records]
        
        return jsonify({'data': totals})
        
    except Exception as e:
        print(f"Error fetching today's out category totals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-outs/category-totals/month', methods=['GET'])
def get_month_out_category_totals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取本月各分类的出库总计
        cursor.execute('''
            SELECT 
                category,
                ROUND(SUM(subtotal), 2) as total
            FROM stock_outs 
            WHERE strftime('%Y-%m', out_time) = strftime('%Y-%m', 'now', 'localtime')
            GROUP BY category
            ORDER BY total DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        totals = [{'category': record[0] or '未分类', 'total': float(record[1])} for record in records]
        
        return jsonify({'data': totals})
        
    except Exception as e:
        print(f"Error fetching month's out category totals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-totals/today', methods=['GET'])
def get_today_category_totals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取今日各分类的总计
        cursor.execute('''
            SELECT 
                category,
                ROUND(SUM(subtotal), 2) as total
            FROM stock_ins 
            WHERE date(in_time) = date('now', 'localtime')
            GROUP BY category
            ORDER BY total DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        totals = [{'category': record[0] or '未分类', 'total': float(record[1])} for record in records]
        
        return jsonify({'data': totals})
        
    except Exception as e:
        print(f"Error fetching today's category totals: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/category-totals/month', methods=['GET'])
def get_month_category_totals():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取本月各分类的总计
        cursor.execute('''
            SELECT 
                category,
                ROUND(SUM(subtotal), 2) as total
            FROM stock_ins 
            WHERE strftime('%Y-%m', in_time) = strftime('%Y-%m', 'now', 'localtime')
            GROUP BY category
            ORDER BY total DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        totals = [{'category': record[0] or '未分类', 'total': float(record[1])} for record in records]
        
        return jsonify({'data': totals})
        
    except Exception as e:
        print(f"Error fetching month's category totals: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 供应商管理API
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取查询参数
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 构建查询条件
        query = 'SELECT * FROM suppliers'
        count_query = 'SELECT COUNT(*) FROM suppliers'
        params = []
        
        if search:
            query += ' WHERE name LIKE ? OR contact LIKE ? OR phone LIKE ? OR supply_items LIKE ?'
            count_query += ' WHERE name LIKE ? OR contact LIKE ? OR phone LIKE ? OR supply_items LIKE ?'
            search_param = f'%{search}%'
            params = [search_param, search_param, search_param, search_param]
        
        # 添加排序和分页
        query += ' ORDER BY name ASC LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        
        # 执行查询
        cursor.execute(query, params)
        records = cursor.fetchall()
        
        # 获取总记录数
        cursor.execute(count_query, params[:4] if search else [])
        total = cursor.fetchone()[0]
        
        # 将记录转换为字典列表
        suppliers = []
        for record in records:
            # 将逗号分隔的供应项目字符串转换为数组
            supply_items = record[5].split(',') if record[5] else []
            
            supplier = {
                'id': record[0],
                'name': record[1],
                'contact': record[2],
                'phone': record[3],
                'fullName': record[4],
                'supplyItems': supply_items,  # 转换为数组并使用驼峰命名法
                'created_at': record[6]
            }
            suppliers.append(supplier)
        
        conn.close()
        
        return jsonify({
            'data': suppliers,
            'total': total,
            'page': page,
            'pageSize': page_size
        })
        
    except Exception as e:
        print(f"Error fetching suppliers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers', methods=['POST'])
def create_supplier():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 适应前端的驼峰命名法
        supply_items = data.get('supplyItems') or data.get('supply_items')
            
        # 必填字段验证
        if not data.get('name'):
            return jsonify({'error': 'Missing required field: name'}), 400
        if not data.get('contact'):
            return jsonify({'error': 'Missing required field: contact'}), 400
        if not data.get('phone'):
            return jsonify({'error': 'Missing required field: phone'}), 400
        if not supply_items:
            return jsonify({'error': 'Missing required field: supplyItems'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 将供应项目数组转换为逗号分隔的字符串
        supply_items_str = ','.join(supply_items) if isinstance(supply_items, list) else supply_items
        
        cursor.execute('''
        INSERT INTO suppliers (name, contact, phone, full_name, supply_items)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['contact'],
            data['phone'],
            data.get('fullName', ''),
            supply_items_str
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 适应前端的驼峰命名法
        supply_items = data.get('supplyItems') or data.get('supply_items')
            
        # 必填字段验证
        if not data.get('name'):
            return jsonify({'error': 'Missing required field: name'}), 400
        if not data.get('contact'):
            return jsonify({'error': 'Missing required field: contact'}), 400
        if not data.get('phone'):
            return jsonify({'error': 'Missing required field: phone'}), 400
        if not supply_items:
            return jsonify({'error': 'Missing required field: supplyItems'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 将供应项目数组转换为逗号分隔的字符串
        supply_items_str = ','.join(supply_items) if isinstance(supply_items, list) else supply_items
        
        cursor.execute('''
        UPDATE suppliers
        SET name = ?, contact = ?, phone = ?, full_name = ?, supply_items = ?
        WHERE id = ?
        ''', (
            data['name'],
            data['contact'],
            data['phone'],
            data.get('fullName', ''),
            supply_items_str,
            supplier_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Supplier not found'}), 404
            
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询指定ID的供应商
        cursor.execute('SELECT * FROM suppliers WHERE id = ?', (supplier_id,))
        record = cursor.fetchone()
        
        if not record:
            conn.close()
            return jsonify({'error': 'Supplier not found'}), 404
            
        # 将逗号分隔的供应项目字符串转换为数组
        supply_items = record[5].split(',') if record[5] else []
        
        supplier = {
            'id': record[0],
            'name': record[1],
            'contact': record[2],
            'phone': record[3],
            'fullName': record[4],
            'supplyItems': supply_items,  # 转换为数组并使用驼峰命名法
            'created_at': record[6]
        }
        
        conn.close()
        
        return jsonify(supplier), 200
        
    except Exception as e:
        print(f"Error fetching supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先删除关联的每月供应商记录
        cursor.execute('DELETE FROM monthly_suppliers WHERE supplier_id = ?', (supplier_id,))
        
        # 然后删除供应商
        cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Supplier not found'}), 404
            
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 每月供应商API
@app.route('/api/monthly-suppliers/all', methods=['GET'])
def get_all_monthly_suppliers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有每月供应商记录，包括供应商信息和年月信息
        cursor.execute('''
        SELECT s.id, s.name, s.contact, s.phone, s.full_name, s.supply_items, s.created_at, ms.year, ms.month, ms.supply_items
        FROM suppliers s
        JOIN monthly_suppliers ms ON s.id = ms.supplier_id
        ORDER BY ms.year DESC, ms.month DESC, s.name ASC
        ''')
        
        records = cursor.fetchall()
        
        # 将记录转换为字典列表
        monthly_suppliers = []
        for record in records:
            # 处理每月供应商的供应品类（优先使用每月供应商表中的数据）
            monthly_supply_items = record[9]  # ms.supply_items
            if monthly_supply_items:
                try:
                    supply_items = json.loads(monthly_supply_items)
                except (json.JSONDecodeError, TypeError):
                    supply_items = []
            else:
                # 如果每月供应商表中没有供应品类，使用供应商表中的数据
                supply_items = record[5].split(',') if record[5] else []
            
            supplier = {
                'id': record[0],
                'name': record[1],
                'contact': record[2],
                'phone': record[3],
                'fullName': record[4],
                'supplyItems': supply_items,  # 转换为数组并使用驼峰命名法
                'created_at': record[6],
                'year': record[7],
                'month': record[8]
            }
            monthly_suppliers.append(supplier)
        
        conn.close()
        
        return jsonify({
            'data': monthly_suppliers
        })
        
    except Exception as e:
        print(f"Error fetching all monthly suppliers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-suppliers', methods=['GET'])
def get_monthly_suppliers():
    try:
        # 获取查询参数
        year = request.args.get('year')
        month = request.args.get('month')
        
        if not year or not month:
            # 如果未提供年月，使用当前年月
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取指定年月的每月供应商
        cursor.execute('''
        SELECT s.*, ms.supply_items FROM suppliers s
        JOIN monthly_suppliers ms ON s.id = ms.supplier_id
        WHERE ms.year = ? AND ms.month = ?
        ORDER BY s.name ASC
        ''', (year, month))
        
        records = cursor.fetchall()
        
        # 将记录转换为字典列表
        monthly_suppliers = []
        for record in records:
            # 处理每月供应商的供应品类（优先使用每月供应商表中的数据）
            monthly_supply_items = record[7]  # ms.supply_items
            if monthly_supply_items:
                try:
                    supply_items = json.loads(monthly_supply_items)
                except (json.JSONDecodeError, TypeError):
                    supply_items = []
            else:
                # 如果每月供应商表中没有供应品类，使用供应商表中的数据
                supply_items = record[5].split(',') if record[5] else []
            
            supplier = {
                'id': record[0],
                'name': record[1],
                'contact': record[2],
                'phone': record[3],
                'fullName': record[4],
                'supplyItems': supply_items,  # 转换为数组并使用驼峰命名法
                'created_at': record[6]
            }
            monthly_suppliers.append(supplier)
        
        conn.close()
        
        return jsonify({
            'data': monthly_suppliers,
            'year': int(year),
            'month': int(month)
        })
        
    except Exception as e:
        print(f"Error fetching monthly suppliers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-suppliers', methods=['POST'])
def set_monthly_supplier():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['supplier_id', 'year', 'month']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查供应商是否存在
        cursor.execute('SELECT id FROM suppliers WHERE id = ?', (data['supplier_id'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Supplier not found'}), 404
        
        # 处理供应品类数据
        supply_items = data.get('supply_items', [])
        supply_items_json = json.dumps(supply_items) if supply_items else None
        
        # 尝试插入每月供应商记录
        try:
            cursor.execute('''
            INSERT INTO monthly_suppliers (supplier_id, year, month, supply_items)
            VALUES (?, ?, ?, ?)
            ''', (
                data['supplier_id'],
                data['year'],
                data['month'],
                supply_items_json
            ))
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            
            return jsonify({'success': True, 'id': last_id}), 201
            
        except sqlite3.IntegrityError:
            # 如果记录已存在（违反唯一约束），更新供应品类
            cursor.execute('''
            UPDATE monthly_suppliers 
            SET supply_items = ? 
            WHERE supplier_id = ? AND year = ? AND month = ?
            ''', (supply_items_json, data['supplier_id'], data['year'], data['month']))
            
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Supplier supply items updated for this month'}), 200
        
    except Exception as e:
        print(f"Error setting monthly supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_monthly_supplier(supplier_id):
    try:
        # 获取查询参数
        year = request.args.get('year')
        month = request.args.get('month')
        
        if not year or not month:
            return jsonify({'error': 'Year and month parameters are required'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 删除指定的每月供应商记录
        cursor.execute('''
        DELETE FROM monthly_suppliers 
        WHERE supplier_id = ? AND year = ? AND month = ?
        ''', (supplier_id, year, month))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Monthly supplier record not found'}), 404
            
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting monthly supplier: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 月度报表API
@app.route('/api/monthly-report/data', methods=['GET'])
def get_monthly_report_data():
    try:
        # 获取查询参数
        year = request.args.get('year')
        month = request.args.get('month')
        
        if not year or not month:
            # 如果未提供年月，使用当前年月
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        else:
            year = int(year)
            month = int(month)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取指定月份的入库记录
        cursor.execute('''
        SELECT 
            name,
            category,
            SUM(quantity) as total_quantity,
            unit,
            AVG(price) as avg_price,
            SUM(subtotal) as total_subtotal,
            COUNT(*) as count
        FROM stock_ins 
        WHERE strftime('%Y', in_time) = ? AND strftime('%m', in_time) = ?
        GROUP BY name, category, unit
        ORDER BY category, name
        ''', (str(year), f"{month:02d}"))
        
        records = cursor.fetchall()
        
        # 获取月度总计
        cursor.execute('''
        SELECT 
            SUM(subtotal) as monthly_total
        FROM stock_ins 
        WHERE strftime('%Y', in_time) = ? AND strftime('%m', in_time) = ?
        ''', (str(year), f"{month:02d}"))
        
        monthly_total_record = cursor.fetchone()
        monthly_total = float(monthly_total_record[0]) if monthly_total_record[0] else 0
        
        # 获取按类别分组的总计
        cursor.execute('''
        SELECT 
            category,
            SUM(subtotal) as category_total
        FROM stock_ins 
        WHERE strftime('%Y', in_time) = ? AND strftime('%m', in_time) = ?
        GROUP BY category
        ORDER BY category_total DESC
        ''', (str(year), f"{month:02d}"))
        
        category_totals_records = cursor.fetchall()
        
        # 获取每日总计
        cursor.execute('''
        SELECT 
            strftime('%d', in_time) as day,
            SUM(subtotal) as daily_total
        FROM stock_ins 
        WHERE strftime('%Y', in_time) = ? AND strftime('%m', in_time) = ?
        GROUP BY strftime('%Y-%m-%d', in_time)
        ORDER BY day
        ''', (str(year), f"{month:02d}"))
        
        daily_totals_records = cursor.fetchall()
        
        conn.close()
        
        # 将记录转换为字典列表
        items = []
        for record in records:
            item = {
                'name': record[0],
                'category': record[1] or '未分类',
                'totalQuantity': float(record[2]),
                'unit': record[3],
                'avgPrice': float(record[4]),
                'totalSubtotal': float(record[5]),
                'count': record[6]
            }
            items.append(item)
        
        # 将类别总计转换为字典列表
        category_totals = []
        for record in category_totals_records:
            category_total = {
                'category': record[0] or '未分类',
                'total': float(record[1])
            }
            category_totals.append(category_total)
        
        # 将每日总计转换为字典列表
        daily_totals = []
        for record in daily_totals_records:
            daily_total = {
                'day': record[0],
                'total': float(record[1])
            }
            daily_totals.append(daily_total)
        
        # 创建完整的月份天数数组
        days_in_month = [str(i).zfill(2) for i in range(1, 32)]
        if month in [4, 6, 9, 11]:
            days_in_month = days_in_month[:30]
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days_in_month = days_in_month[:29]  # 闰年
            else:
                days_in_month = days_in_month[:28]  # 平年
        
        # 填充没有数据的日期
        daily_totals_dict = {record['day']: record['total'] for record in daily_totals}
        complete_daily_totals = []
        for day in days_in_month:
            complete_daily_totals.append({
                'day': day,
                'total': daily_totals_dict.get(day, 0)
            })
        
        return jsonify({
            'items': items,
            'monthlyTotal': monthly_total,
            'categoryTotals': category_totals,
            'dailyTotals': complete_daily_totals,
            'year': year,
            'month': month
        })
        
    except Exception as e:
        print(f"Error fetching monthly report data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-report/template', methods=['POST'])
def save_report_template():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # 必填字段验证
        required_fields = ['name', 'templateData', 'year', 'month']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在该年月的模板
        cursor.execute('''
        SELECT id FROM report_templates
        WHERE year = ? AND month = ?
        ''', (data['year'], data['month']))
        
        existing_template = cursor.fetchone()
        
        if existing_template:
            # 更新现有模板
            cursor.execute('''
            UPDATE report_templates
            SET name = ?, template_data = ?, updated_at = CURRENT_TIMESTAMP
            WHERE year = ? AND month = ?
            ''', (
                data['name'],
                data['templateData'],
                data['year'],
                data['month']
            ))
            template_id = existing_template[0]
        else:
            # 创建新模板
            cursor.execute('''
            INSERT INTO report_templates (name, template_data, year, month)
            VALUES (?, ?, ?, ?)
            ''', (
                data['name'],
                data['templateData'],
                data['year'],
                data['month']
            ))
            template_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': template_id,
            'message': '报表模板保存成功'
        }), 200
        
    except Exception as e:
        print(f"Error saving report template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-report/template', methods=['GET'])
def get_report_template():
    try:
        # 获取查询参数
        year = request.args.get('year')
        month = request.args.get('month')
        
        if not year or not month:
            # 如果未提供年月，使用当前年月
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取指定年月的模板
        cursor.execute('''
        SELECT id, name, template_data, year, month, created_at, updated_at
        FROM report_templates
        WHERE year = ? AND month = ?
        ''', (year, month))
        
        record = cursor.fetchone()
        conn.close()
        
        if not record:
            return jsonify({
                'exists': False,
                'message': '未找到模板'
            }), 404
        
        template = {
            'id': record[0],
            'name': record[1],
            'templateData': record[2],
            'year': record[3],
            'month': record[4],
            'createdAt': record[5],
            'updatedAt': record[6],
            'exists': True
        }
        
        return jsonify(template), 200
        
    except Exception as e:
        print(f"Error fetching report template: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 数据导入API
@app.route('/api/stock-ins/batch', methods=['POST'])
def batch_import_stock_ins():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '没有提供数据'}), 400
            
        import_data = data.get('data', [])
        import_mode = data.get('mode', 'append')  # 默认为新增模式
        
        if not import_data or not isinstance(import_data, list):
            return jsonify({'error': '数据格式不正确，应为数组'}), 400
            
        # 调用导入处理函数
        result = import_stock_data(import_data, import_mode)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"批量导入库存数据失败: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/inventory-import', methods=['POST'])
def import_monthly_inventory():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '没有提供数据'}), 400
            
        import_data = data.get('data', [])
        import_mode = data.get('mode', 'append')  # 默认为新增模式
        
        if not import_data or not isinstance(import_data, list):
            return jsonify({'error': '数据格式不正确，应为数组'}), 400
            
        # 调用导入处理函数
        result = import_inventory_data(import_data, import_mode)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"批量导入月底库存数据失败: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

# 批量导入月底库存数据API
@app.route('/api/monthly-inventory/batch', methods=['POST'])
def batch_import_monthly_inventory():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        inventory_data = data.get('data', [])
        import_mode = data.get('mode', 'append')  # 'append' 或 'overwrite'
        
        if not inventory_data:
            return jsonify({'error': 'No inventory data provided'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        success_count = 0
        failed_count = 0
        errors = []
        
        try:
            # 如果是覆盖模式，先删除所有现有数据
            if import_mode == 'overwrite':
                cursor.execute('DELETE FROM monthly_inventory')
                print(f"覆盖模式：已清空现有数据")
            
            # 批量插入新数据
            for item in inventory_data:
                try:
                    # 验证必填字段
                    required_fields = ['date', 'name', 'category', 'unitPrice', 'quantity']
                    for field in required_fields:
                        if field not in item:
                            raise ValueError(f'Missing required field: {field}')
                    
                    cursor.execute('''
                    INSERT INTO monthly_inventory (date, name, category, unit_price, quantity, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item['date'],
                        item['name'],
                        item['category'],
                        float(item['unitPrice']),
                        float(item['quantity']),
                        item.get('unit', '千克')
                    ))
                    success_count += 1
                    
                except Exception as item_error:
                    failed_count += 1
                    error_msg = f"{item.get('name', 'Unknown')}: {str(item_error)}"
                    errors.append(error_msg)
                    print(f"导入单条记录失败: {error_msg}")
            
            conn.commit()
            
            # 返回导入结果
            result = {
                'success': failed_count == 0,
                'successCount': success_count,
                'failedCount': failed_count,
                'errors': errors,
                'message': f'成功导入 {success_count} 条记录' + (f'，失败 {failed_count} 条' if failed_count > 0 else '')
            }
            
            print(f"批量导入完成: 成功 {success_count} 条，失败 {failed_count} 条")
            return jsonify(result), 200
            
        except Exception as e:
            conn.rollback()
            print(f"批量导入事务失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'批量导入失败: {str(e)}',
                'successCount': 0,
                'failedCount': len(inventory_data)
            }), 500
            
        finally:
            conn.close()
        
    except Exception as e:
        print(f"批量导入月底库存数据失败: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

# 月底库存API
@app.route('/api/monthly-inventory', methods=['GET'])
def get_monthly_inventory():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, date, name, category, unit_price, quantity, unit, created_at
        FROM monthly_inventory
        ORDER BY date DESC, name ASC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        inventory_list = []
        for record in records:
            inventory = {
                'id': record[0],
                'date': record[1],
                'name': record[2],
                'category': record[3],
                'unitPrice': float(record[4]),
                'quantity': float(record[5]),
                'unit': record[6],
                'created_at': record[7]
            }
            inventory_list.append(inventory)
        
        return jsonify({'data': inventory_list})
        
    except Exception as e:
        print(f"Error fetching monthly inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-inventory', methods=['POST'])
def create_monthly_inventory():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['date', 'name', 'category', 'unitPrice', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO monthly_inventory (date, name, category, unit_price, quantity, unit)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['date'],
            data['name'],
            data['category'],
            float(data['unitPrice']),
            float(data['quantity']),
            data['unit']
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating monthly inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-inventory/<int:inventory_id>', methods=['PUT'])
def update_monthly_inventory(inventory_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE monthly_inventory 
        SET date = ?, name = ?, category = ?, unit_price = ?, quantity = ?, unit = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            data['date'],
            data['name'],
            data['category'],
            float(data['unitPrice']),
            float(data['quantity']),
            data['unit'],
            inventory_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Inventory record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating monthly inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly-inventory/<int:inventory_id>', methods=['DELETE'])
def delete_monthly_inventory(inventory_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM monthly_inventory WHERE id = ?', (inventory_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Inventory record not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting monthly inventory: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 储存类食材明细API
@app.route('/api/storage-ingredients', methods=['GET'])
def get_storage_ingredients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, unit, unit_price, specification, created_at
        FROM storage_ingredients
        ORDER BY name ASC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        ingredients = []
        for record in records:
            ingredient = {
                'id': record[0],
                'name': record[1],
                'unit': record[2],
                'unitPrice': float(record[3]),
                'specification': record[4] or '',
                'created_at': record[5]
            }
            ingredients.append(ingredient)
        
        return jsonify({'data': ingredients})
        
    except Exception as e:
        print(f"Error fetching storage ingredients: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/storage-ingredients', methods=['POST'])
def create_storage_ingredient():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'unit', 'unitPrice']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO storage_ingredients (name, unit, unit_price, specification)
        VALUES (?, ?, ?, ?)
        ''', (
            data['name'],
            data['unit'],
            float(data['unitPrice']),
            data.get('specification', '')
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating storage ingredient: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/storage-ingredients/<int:ingredient_id>', methods=['PUT'])
def update_storage_ingredient(ingredient_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE storage_ingredients 
        SET name = ?, unit = ?, unit_price = ?, specification = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            data['name'],
            data['unit'],
            float(data['unitPrice']),
            data.get('specification', ''),
            ingredient_id
        ))
        
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Storage ingredient not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error updating storage ingredient: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/storage-ingredients/<int:ingredient_id>', methods=['DELETE'])
def delete_storage_ingredient(ingredient_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM storage_ingredients WHERE id = ?', (ingredient_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Storage ingredient not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting storage ingredient: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 报表设计器模板API
@app.route('/api/designer-templates', methods=['GET'])
def get_designer_templates():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, name, description, sheet_data, created_at
        FROM designer_templates
        ORDER BY created_at DESC
        ''')
        
        records = cursor.fetchall()
        conn.close()
        
        templates = []
        for record in records:
            template = {
                'id': record[0],
                'name': record[1],
                'description': record[2] or '',
                'sheetData': record[3],
                'createdAt': record[4]
            }
            templates.append(template)
        
        return jsonify({'data': templates})
        
    except Exception as e:
        print(f"Error fetching designer templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/designer-templates', methods=['POST'])
def create_designer_template():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'sheetData']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO designer_templates (name, description, sheet_data)
        VALUES (?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['sheetData']
        ))
        
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'id': last_id}), 201
        
    except Exception as e:
        print(f"Error creating designer template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/designer-templates/<int:template_id>', methods=['DELETE'])
def delete_designer_template(template_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM designer_templates WHERE id = ?', (template_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Template not found'}), 404
            
        conn.close()
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Error deleting designer template: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

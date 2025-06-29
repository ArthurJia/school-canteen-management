from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
from database import get_db_connection

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
        
        # 将记录转换为字典列表
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
                'in_time': record[10]
            }
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

@app.route('/api/stock-outs', methods=['POST'])
def create_stock_out():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO stock_outs (item_name, quantity, unit, purpose, operator, remarks)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['item_name'],
        data['quantity'],
        data['unit'],
        data.get('purpose', ''),
        data.get('operator', ''),
        data.get('remarks', '')
    ))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 201

@app.route('/api/stock-outs', methods=['GET'])
def get_stock_outs():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM stock_outs ORDER BY out_time DESC')
    records = cursor.fetchall()
    
    conn.close()
    
    stock_outs = []
    for record in records:
        stock_outs.append({
            'id': record[0],
            'item_name': record[1],
            'quantity': record[2],
            'unit': record[3],
            'purpose': record[4],
            'operator': record[5],
            'out_time': record[6],
            'remarks': record[7]
        })
    
    return jsonify(stock_outs)

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
        SELECT s.id, s.name, s.contact, s.phone, s.full_name, s.supply_items, s.created_at, ms.year, ms.month
        FROM suppliers s
        JOIN monthly_suppliers ms ON s.id = ms.supplier_id
        ORDER BY ms.year DESC, ms.month DESC, s.name ASC
        ''')
        
        records = cursor.fetchall()
        
        # 将记录转换为字典列表
        monthly_suppliers = []
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
        SELECT s.* FROM suppliers s
        JOIN monthly_suppliers ms ON s.id = ms.supplier_id
        WHERE ms.year = ? AND ms.month = ?
        ORDER BY s.name ASC
        ''', (year, month))
        
        records = cursor.fetchall()
        
        # 将记录转换为字典列表
        monthly_suppliers = []
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
        
        # 尝试插入每月供应商记录
        try:
            cursor.execute('''
            INSERT INTO monthly_suppliers (supplier_id, year, month)
            VALUES (?, ?, ?)
            ''', (
                data['supplier_id'],
                data['year'],
                data['month']
            ))
            
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            
            return jsonify({'success': True, 'id': last_id}), 201
            
        except sqlite3.IntegrityError:
            # 如果记录已存在（违反唯一约束），返回成功
            conn.close()
            return jsonify({'success': True, 'message': 'Supplier already set for this month'}), 200
        
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)
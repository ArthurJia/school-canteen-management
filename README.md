# 中华路小学食堂管理系统

## 项目概述

这是一个基于Vue 3 + Flask的食堂管理系统，主要用于管理食材入库、库存查询、供应商管理、月度报表等功能。系统采用前后端分离架构，支持桌面端和移动端访问。

## 技术栈

- **前端**: Vue 3, Element Plus, Vite, JavaScript
- **后端**: Flask, Python
- **数据库**: SQLite
- **其他**: Axios, ECharts, XLSX, Luckysheet

## 桌面端页面说明

### 1. 入库管理页面 (`/desktop/inbound`)
**文件位置**: `frontend/src/views/desktop/InboundManagement.vue`

**功能描述**: 
- 食材入库录入
- 今日入库记录查看
- 今日/本月分类价格统计

**使用的API接口**:
- `POST /api/stock-ins` - 创建入库记录
- `GET /api/stock-ins` - 获取入库记录列表
- `GET /api/category-totals/today` - 获取今日分类总计
- `GET /api/category-totals/month` - 获取本月分类总计
- `GET /api/monthly-suppliers/all` - 获取历史每月供应商记录

**对应数据库表**: 
- `stock_ins` - 入库记录表
- `monthly_suppliers` - 每月供应商表
- `suppliers` - 供应商表

### 2. 库存查询页面 (`/desktop/stock`)
**文件位置**: `frontend/src/views/desktop/StockQuery.vue`

**功能描述**:
- 库存记录查询和筛选
- 库存记录编辑和删除
- 数据导出Excel功能

**使用的API接口**:
- `GET /api/stock-ins` - 获取库存记录（支持分页、搜索、日期筛选）
- `PUT /api/stock-ins/{id}` - 更新库存记录
- `DELETE /api/stock-ins/{id}` - 删除库存记录

**对应数据库表**:
- `stock_ins` - 入库记录表

### 3. 供应商管理页面 (`/desktop/supplier`)
**文件位置**: `frontend/src/views/desktop/SupplierManagement.vue`

**功能描述**:
- 供应商信息管理（增删改查）
- 每月供应商设置和管理
- 历史每月供应商记录查看
- 供应商数据导出Excel

**使用的API接口**:
- `GET /api/suppliers` - 获取供应商列表
- `POST /api/suppliers` - 创建供应商
- `PUT /api/suppliers/{id}` - 更新供应商信息
- `DELETE /api/suppliers/{id}` - 删除供应商
- `GET /api/suppliers/{id}` - 获取供应商详情
- `GET /api/monthly-suppliers` - 获取指定月份的每月供应商
- `GET /api/monthly-suppliers/all` - 获取所有历史每月供应商记录
- `POST /api/monthly-suppliers` - 添加每月供应商
- `DELETE /api/monthly-suppliers/{id}` - 删除每月供应商

**对应数据库表**:
- `suppliers` - 供应商表
- `monthly_suppliers` - 每月供应商表

### 4. 月底盘点明细页面 (`/desktop/monthly-inventory`)
**文件位置**: `frontend/src/views/desktop/MonthlyInventory.vue`

**功能描述**:
- 月底库存数据管理
- 储存类食材分类管理
- 使用量统计（大米、食用油、调味品）

**使用的API接口**:
- `GET /api/monthly-inventory` - 获取月底库存记录
- `POST /api/monthly-inventory` - 创建月底库存记录
- `PUT /api/monthly-inventory/{id}` - 更新月底库存记录
- `DELETE /api/monthly-inventory/{id}` - 删除月底库存记录
- `GET /api/outbound-categories` - 获取出库分类
- `POST /api/outbound-categories` - 创建出库分类
- `PUT /api/outbound-categories/{id}` - 更新出库分类
- `DELETE /api/outbound-categories/{id}` - 删除出库分类

**对应数据库表**:
- `monthly_inventory` - 月底库存表
- `outbound_categories` - 出库分类表

### 5. 月度报表页面 (`/desktop/report`)
**文件位置**: `frontend/src/views/desktop/MonthlyReport.vue`

**功能描述**:
- 月度支出统计
- 类别支出占比图表
- 每日支出统计图表
- 明细数据查看

**使用的API接口**:
- `GET /api/monthly-report/data` - 获取月度报表数据
- `GET /api/monthly-report/template` - 获取报表模板
- `POST /api/monthly-report/template` - 保存报表模板

**对应数据库表**:
- `stock_ins` - 入库记录表（用于统计）
- `report_templates` - 报表模板表

### 6. 报表设计及导出页面 (`/desktop/report-designer`)
**文件位置**: `frontend/src/views/desktop/ReportDesigner.vue`

**功能描述**:
- 使用Luckysheet进行报表设计
- 报表模板保存和加载
- 报表导出功能

**使用的API接口**:
- `GET /api/designer-templates` - 获取设计器模板列表
- `POST /api/designer-templates` - 创建设计器模板
- `DELETE /api/designer-templates/{id}` - 删除设计器模板

**对应数据库表**:
- `designer_templates` - 设计器模板表

### 7. 数据导入页面 (`/desktop/data-import`)
**文件位置**: `frontend/src/views/desktop/DataImport.vue`

**功能描述**:
- 库存查询数据批量导入
- 月底库存数据批量导入
- Excel/CSV文件解析和处理
- 导入模板下载

**使用的API接口**:
- `POST /api/stock-ins/batch` - 批量导入库存数据
- `POST /api/monthly-inventory/batch` - 批量导入月底库存数据

**对应数据库表**:
- `stock_ins` - 入库记录表
- `monthly_inventory` - 月底库存表

## 数据库结构

### 1. stock_ins (入库记录表)
```sql
CREATE TABLE stock_ins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 食材名称
    category TEXT,                         -- 分类
    quantity REAL NOT NULL,                -- 数量
    unit TEXT NOT NULL,                    -- 单位
    supplier TEXT,                         -- 供应商
    price REAL DEFAULT 0,                  -- 单价
    subtotal REAL DEFAULT 0,               -- 小计
    is_daily BOOLEAN DEFAULT 0,            -- 是否为当天类食材
    note TEXT,                             -- 备注
    in_time TEXT DEFAULT CURRENT_TIMESTAMP -- 入库时间
)
```

### 2. suppliers (供应商表)
```sql
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 供应商名称
    contact TEXT NOT NULL,                 -- 联系人
    phone TEXT NOT NULL,                   -- 联系电话
    full_name TEXT,                        -- 供应商全称
    supply_items TEXT NOT NULL,            -- 供应品类（逗号分隔）
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### 3. monthly_suppliers (每月供应商表)
```sql
CREATE TABLE monthly_suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,         -- 供应商ID
    year INTEGER NOT NULL,                 -- 年份
    month INTEGER NOT NULL,                -- 月份
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
    UNIQUE(year, month, supplier_id)
)
```

### 4. stock_outs (出库记录表)
```sql
CREATE TABLE stock_outs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,               -- 物品名称
    quantity REAL NOT NULL,                -- 数量
    unit TEXT NOT NULL,                    -- 单位
    purpose TEXT,                          -- 用途
    operator TEXT,                         -- 操作员
    out_time TEXT DEFAULT CURRENT_TIMESTAMP, -- 出库时间
    remarks TEXT                           -- 备注
)
```

### 5. monthly_inventory (月底库存表)
```sql
CREATE TABLE monthly_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- 时间（年月）
    name TEXT NOT NULL,                    -- 名称
    category TEXT NOT NULL,                -- 分类
    unit_price REAL NOT NULL,              -- 单价
    quantity REAL NOT NULL,                -- 库存数量
    unit TEXT NOT NULL,                    -- 单位
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### 6. outbound_categories (出库分类表)
```sql
CREATE TABLE outbound_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,             -- 分类名称
    unit TEXT NOT NULL,                    -- 单位
    unit_price REAL NOT NULL,              -- 单价
    specification TEXT,                    -- 规格
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### 7. report_templates (报表模板表)
```sql
CREATE TABLE report_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 模板名称
    template_data TEXT NOT NULL,           -- 模板数据
    year INTEGER NOT NULL,                 -- 年份
    month INTEGER NOT NULL,                -- 月份
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month)
)
```

### 8. designer_templates (设计器模板表)
```sql
CREATE TABLE designer_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 模板名称
    description TEXT,                      -- 描述
    sheet_data TEXT NOT NULL,              -- 表格数据
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## API接口汇总

### 入库管理相关
- `POST /api/stock-ins` - 创建入库记录
- `GET /api/stock-ins` - 获取入库记录列表（支持分页、搜索、日期筛选）
- `PUT /api/stock-ins/{id}` - 更新入库记录
- `DELETE /api/stock-ins/{id}` - 删除入库记录
- `DELETE /api/stock-ins/all` - 删除所有入库记录
- `POST /api/stock-ins/batch` - 批量导入入库记录

### 出库管理相关
- `POST /api/stock-outs` - 创建出库记录
- `GET /api/stock-outs` - 获取出库记录列表

### 统计相关
- `GET /api/category-totals/today` - 获取今日分类总计
- `GET /api/category-totals/month` - 获取本月分类总计

### 供应商管理相关
- `GET /api/suppliers` - 获取供应商列表
- `POST /api/suppliers` - 创建供应商
- `PUT /api/suppliers/{id}` - 更新供应商信息
- `DELETE /api/suppliers/{id}` - 删除供应商
- `GET /api/suppliers/{id}` - 获取供应商详情

### 每月供应商相关
- `GET /api/monthly-suppliers` - 获取指定月份的每月供应商
- `GET /api/monthly-suppliers/all` - 获取所有历史每月供应商记录
- `POST /api/monthly-suppliers` - 添加每月供应商
- `DELETE /api/monthly-suppliers/{id}` - 删除每月供应商

### 月底库存相关
- `GET /api/monthly-inventory` - 获取月底库存记录
- `POST /api/monthly-inventory` - 创建月底库存记录
- `PUT /api/monthly-inventory/{id}` - 更新月底库存记录
- `DELETE /api/monthly-inventory/{id}` - 删除月底库存记录
- `POST /api/monthly-inventory/batch` - 批量导入月底库存记录

### 出库分类相关
- `GET /api/outbound-categories` - 获取出库分类
- `POST /api/outbound-categories` - 创建出库分类
- `PUT /api/outbound-categories/{id}` - 更新出库分类
- `DELETE /api/outbound-categories/{id}` - 删除出库分类

### 月度报表相关
- `GET /api/monthly-report/data` - 获取月度报表数据
- `GET /api/monthly-report/template` - 获取报表模板
- `POST /api/monthly-report/template` - 保存报表模板

### 设计器模板相关
- `GET /api/designer-templates` - 获取设计器模板列表
- `POST /api/designer-templates` - 创建设计器模板
- `DELETE /api/designer-templates/{id}` - 删除设计器模板

## 项目启动

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 数据库初始化
```bash
cd backend
python database.py
```

## 注意事项

1. 系统使用SQLite作为数据库，数据库文件为 `backend/canteen.db`
2. 前端默认API地址为 `http://localhost:5000`
3. 系统支持Excel和CSV文件的导入导出功能
4. 分类代码和供应商代码在系统中使用英文标识，显示时转换为中文
5. 系统具有完整的错误处理和用户提示机制
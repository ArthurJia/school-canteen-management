-- 创建一个临时表，使用新的列名 full_name 代替 address
CREATE TABLE suppliers_new (
    id INTEGER PRIMARY KEY,
    name TEXT,
    contact TEXT,
    phone TEXT,
    full_name TEXT,
    supply_items TEXT,
    created_at TEXT
);

-- 将数据从旧表复制到新表，将 address 列的数据复制到 full_name 列
INSERT INTO suppliers_new (id, name, contact, phone, full_name, supply_items, created_at)
SELECT id, name, contact, phone, address, supply_items, created_at FROM suppliers;

-- 删除旧表
DROP TABLE suppliers;

-- 将新表重命名为旧表的名称
ALTER TABLE suppliers_new RENAME TO suppliers;

-- 验证修改
PRAGMA table_info(suppliers);
-- 初始化数据库脚本

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备表
CREATE TABLE IF NOT EXISTS equipment (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    specification TEXT,
    manufacturer VARCHAR(100),
    purchase_date DATE,
    supplier VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'running',
    lifecycle_status VARCHAR(20) DEFAULT 'active',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建日志基础表
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    log_type VARCHAR(30) NOT NULL,
    operator_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    attachments JSONB,
    approved_at TIMESTAMP,
    approver_id INTEGER REFERENCES users(id),
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建设备安装日志
CREATE TABLE IF NOT EXISTS installation_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    installation_date DATE NOT NULL,
    installer VARCHAR(100),
    location VARCHAR(100),
    acceptance_status VARCHAR(20)
);

-- 创建设备维修日志
CREATE TABLE IF NOT EXISTS repair_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    repair_date DATE NOT NULL,
    fault_description TEXT,
    solution TEXT,
    cost DECIMAL(10,2),
    repair_time INTEGER
);

-- 创建设备报废日志
CREATE TABLE IF NOT EXISTS scrap_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    scrap_date DATE NOT NULL,
    scrap_reason TEXT,
    residual_value DECIMAL(10,2)
);

-- 创建日常巡检日志
CREATE TABLE IF NOT EXISTS inspection_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    inspection_date DATE NOT NULL,
    inspector VARCHAR(100),
    inspection_items JSONB,
    result VARCHAR(20)
);

-- 创建保养记录
CREATE TABLE IF NOT EXISTS maintenance_records (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    maintenance_date DATE NOT NULL,
    maintenance_items JSONB,
    next_maintenance_date DATE
);

-- 创建故障报修日志
CREATE TABLE IF NOT EXISTS fault_reports (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    fault_date DATE NOT NULL,
    fault_level VARCHAR(20),
    reporter VARCHAR(100),
    fault_description TEXT,
    handle_status VARCHAR(20)
);

-- 创建配件更换日志
CREATE TABLE IF NOT EXISTS parts_replacement_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    replacement_date DATE NOT NULL,
    parts_name VARCHAR(100),
    parts_code VARCHAR(50),
    quantity INTEGER,
    cost DECIMAL(10,2)
);

-- 创建校准记录
CREATE TABLE IF NOT EXISTS calibration_logs (
    id INTEGER PRIMARY KEY REFERENCES logs(id),
    calibration_date DATE NOT NULL,
    calibration_org VARCHAR(100),
    calibration_result VARCHAR(20),
    next_calibration_date DATE
);

-- 创建审批配置
CREATE TABLE IF NOT EXISTS approval_configs (
    id SERIAL PRIMARY KEY,
    log_type VARCHAR(30) NOT NULL,
    require_approval BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建系统配置
CREATE TABLE IF NOT EXISTS system_configs (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(50) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建操作日志
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建通知表
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(30),
    is_read BOOLEAN DEFAULT false,
    equipment_id INTEGER REFERENCES equipment(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_logs_equipment_id ON logs(equipment_id);
CREATE INDEX IF NOT EXISTS idx_logs_status ON logs(status);
CREATE INDEX IF NOT EXISTS idx_logs_log_type ON logs(log_type);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status);

-- 插入默认管理员账号（密码: admin123，使用前请修改）
INSERT INTO users (username, password_hash, role)
SELECT 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8xm5/Y5KUi', 'admin'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- 插入默认审批配置
INSERT INTO approval_configs (log_type, require_approval)
VALUES
    ('installation', true),
    ('repair', true),
    ('scrap', true),
    ('inspection', false),
    ('maintenance', true),
    ('fault', false),
    ('parts', true),
    ('calibration', true)
ON CONFLICT DO NOTHING;

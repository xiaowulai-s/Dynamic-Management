-- ============================================================
-- 数据库迁移脚本 - 纯 SQL 版本
-- 对应 Alembic 迁移: a3f7c2e1d9b6
-- 描述: add customer_name, indexes, relationships and numeric types
-- 日期: 2026-07-18
-- ============================================================
-- 使用方法:
--   docker exec -i equipment-postgres psql -U postgres -d equipment_db < migration.sql
-- 或:
--   psql -U postgres -d equipment_db -f migration.sql
-- ============================================================

BEGIN;

-- ========== 1. equipment 表：新增 customer_name 字段 ==========
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS customer_name VARCHAR(200);
COMMENT ON COLUMN equipment.customer_name IS '客户名称';
CREATE INDEX IF NOT EXISTS ix_equipment_customer_name ON equipment (customer_name);

-- ========== 2. equipment 表：为 lifecycle_status 添加索引 ==========
CREATE INDEX IF NOT EXISTS ix_equipment_lifecycle_status ON equipment (lifecycle_status);

-- ========== 3. maintenance_records 表：为 next_maintenance_date 添加索引 ==========
CREATE INDEX IF NOT EXISTS ix_maintenance_records_next_maintenance_date
    ON maintenance_records (next_maintenance_date);

-- ========== 4. calibration_logs 表：为 next_calibration_date 添加索引 ==========
CREATE INDEX IF NOT EXISTS ix_calibration_logs_next_calibration_date
    ON calibration_logs (next_calibration_date);

-- ========== 5. feedbacks 表：为 user_id 添加索引 ==========
CREATE INDEX IF NOT EXISTS ix_feedbacks_user_id ON feedbacks (user_id);

-- ========== 6. 将 cost 字段从 Integer 改为 Numeric(10, 2) ==========
ALTER TABLE repair_logs ALTER COLUMN cost TYPE NUMERIC(10, 2);
ALTER TABLE parts_replacement_logs ALTER COLUMN cost TYPE NUMERIC(10, 2);

-- ========== 7. 将 scrap_logs.residual_value 从 Integer 改为 Numeric(10, 2) ==========
ALTER TABLE scrap_logs ALTER COLUMN residual_value TYPE NUMERIC(10, 2);

-- ========== 8. 创建 Alembic 版本记录表（如果不存在） ==========
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- 记录迁移版本
INSERT INTO alembic_version (version_num) VALUES ('a3f7c2e1d9b6')
ON CONFLICT (version_num) DO NOTHING;

-- 清除旧版本（如果有）
DELETE FROM alembic_version WHERE version_num != 'a3f7c2e1d9b6';

COMMIT;

-- ========== 验证查询 ==========
-- 检查 customer_name 字段
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'equipment' AND column_name = 'customer_name';

-- 检查索引
SELECT indexname FROM pg_indexes
WHERE tablename IN ('equipment', 'maintenance_records', 'calibration_logs', 'feedbacks')
AND indexname LIKE 'ix_%';

-- 检查字段类型
SELECT table_name, column_name, data_type, numeric_precision, numeric_scale
FROM information_schema.columns
WHERE table_name IN ('repair_logs', 'parts_replacement_logs', 'scrap_logs')
AND column_name IN ('cost', 'residual_value');

-- 检查迁移版本
SELECT * FROM alembic_version;

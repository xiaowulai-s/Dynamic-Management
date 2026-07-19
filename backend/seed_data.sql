-- ============================================================
-- 设备信息动态管理系统 - 种子数据脚本
-- 创建日期: 2026-07-18
-- 说明: 包含 approval_configs 系统配置 + 业务演示数据
-- 使用方法:
--   docker exec -i equipment-postgres psql -U postgres -d equipment_db < seed_data.sql
-- ============================================================

BEGIN;

-- ========== 0. 清空旧业务数据（保留 users 表）==========
TRUNCATE TABLE feedbacks RESTART IDENTITY CASCADE;
TRUNCATE TABLE audit_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE notifications RESTART IDENTITY CASCADE;
TRUNCATE TABLE scrap_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE calibration_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE parts_replacement_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE fault_reports RESTART IDENTITY CASCADE;
TRUNCATE TABLE maintenance_records RESTART IDENTITY CASCADE;
TRUNCATE TABLE inspection_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE repair_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE installation_logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE logs RESTART IDENTITY CASCADE;
TRUNCATE TABLE equipment RESTART IDENTITY CASCADE;
TRUNCATE TABLE customers RESTART IDENTITY CASCADE;
TRUNCATE TABLE approval_configs RESTART IDENTITY CASCADE;
TRUNCATE TABLE system_configs RESTART IDENTITY CASCADE;

-- ========== 1. 审批配置（init.sql 中缺失的）==========
INSERT INTO approval_configs (log_type, require_approval) VALUES
    ('installation', true),
    ('repair', true),
    ('scrap', true),
    ('inspection', false),
    ('maintenance', true),
    ('fault', false),
    ('parts', true),
    ('calibration', true)
ON CONFLICT DO NOTHING;

-- ========== 2. 系统配置 ==========
INSERT INTO system_configs (config_key, config_value, description) VALUES
    ('system_name', '"设备信息动态管理系统"', '系统名称'),
    ('system_version', '"1.0.0"', '系统版本'),
    ('notification_enabled', 'true', '是否启用通知'),
    ('maintenance_reminder_days', '7', '保养提醒提前天数')
ON CONFLICT (config_key) DO NOTHING;

-- ========== 3. 客户数据（5个）==========
INSERT INTO customers (name, contact, phone, email, address, remark) VALUES
    ('上海精密制造有限公司', '张经理', '13800138001', 'zhang@shprecision.com', '上海市浦东新区张江高科技园区', 'VIP客户，年采购额500万'),
    ('北京华科技有限公司', '李工', '13900139002', 'li@huake.com', '北京市海淀区中关村科技园', '长期合作伙伴'),
    ('深圳创新电子厂', '王总', '13700137003', 'wang@cxel.com', '深圳市南山区科技园南区', '新客户，首次合作'),
    ('广州医疗器械集团', '刘主任', '13600136004', 'liu@gzmed.com', '广州市天河区珠江新城', '医疗行业客户，资质齐全'),
    ('成都航天装备公司', '陈总工', '13500135005', 'chen@cdspace.com', '成都市高新区西部园区', '航天军工客户，保密等级高');

-- ========== 4. 设备数据（10台）==========
INSERT INTO equipment (code, name, model, specification, manufacturer, purchase_date, supplier, location, customer_name, status, lifecycle_status, created_by) VALUES
    ('EQ-2024-001', '数控车床 CK6140', 'CK6140', '最大加工直径400mm，长度1000mm', '沈阳机床集团', '2024-03-15', '沈阳机床销售公司', '一号车间A区', '上海精密制造有限公司', 'running', 'active', 1),
    ('EQ-2024-002', '立式加工中心 VM-850', 'VM-850', '工作台1000x500mm，主轴转速8000rpm', '大连机床集团', '2024-04-20', '大连机床华北代理', '一号车间B区', '上海精密制造有限公司', 'running', 'active', 1),
    ('EQ-2024-003', '激光切割机 LG-3015', 'LG-3015', '切割范围3000x1500mm，功率2000W', '大族激光', '2024-05-10', '大族激光直供', '二号车间A区', '北京华科技有限公司', 'running', 'active', 1),
    ('EQ-2024-004', '注塑机 IT-200', 'IT-200', '锁模力200吨，注射量500g', '海天国际', '2024-06-01', '海天华东代理', '二号车间B区', '深圳创新电子厂', 'repairing', 'maintenance', 1),
    ('EQ-2024-005', '超声波清洗机 UC-100', 'UC-100', '容量100L，频率40kHz', '深圳洁盟', '2024-06-15', '洁盟旗舰店', '三号车间A区', '深圳创新电子厂', 'running', 'active', 1),
    ('EQ-2024-006', '工业机器人 IRB-1200', 'IRB-1200', '负载5kg，臂展700mm', 'ABB机器人', '2024-07-01', 'ABB中国', '自动化产线1', '广州医疗器械集团', 'running', 'active', 1),
    ('EQ-2024-007', '真空干燥箱 VD-500', 'VD-500', '内胆500L，温度范围RT+10~250℃', '上海一恒', '2024-07-15', '一恒官方店', '三号车间B区', '广州医疗器械集团', 'stopped', 'active', 1),
    ('EQ-2024-008', 'CMM 三坐标测量机', 'CRYSTA-544', '测量范围500x400x400mm', '三丰精密', '2024-08-01', '三丰华北代理', '质检中心', '成都航天装备公司', 'running', 'active', 1),
    ('EQ-2024-009', '数控铣床 XKA-715', 'XKA-715', '工作台1250x500mm，主轴锥孔ISO40', '北京机电院', '2024-08-15', '机电院直供', '一号车间C区', '成都航天装备公司', 'running', 'active', 1),
    ('EQ-2023-010', '旧式车床 C6132', 'C6132', '最大加工直径320mm，长度750mm', '济南一机', '2023-09-10', '二手设备市场', '一号车间D区', '上海精密制造有限公司', 'scrapped', 'scrapped', 1);

-- ========== 5. 安装日志（3条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (1, 'installation', 1, 'approved', '设备到货后由厂家工程师进行安装调试，已通过验收。', '2024-03-20 10:00:00+08'),
    (2, 'installation', 1, 'approved', '加工中心安装完成，完成几何精度测试。', '2024-04-25 14:30:00+08'),
    (6, 'installation', 1, 'approved', 'ABB机器人安装调试完成，轨迹示教已完成。', '2024-07-05 09:15:00+08');

INSERT INTO installation_logs (id, installation_date, installer, location, acceptance_status) VALUES
    (1, '2024-03-20', '李工（厂家）', '一号车间A区', 'passed'),
    (2, '2024-04-25', '王工（厂家）', '一号车间B区', 'passed'),
    (3, '2024-07-05', 'ABB工程师团队', '自动化产线1', 'passed');

-- ========== 6. 维修日志（3条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (4, 'repair', 1, 'approved', '注塑机锁模力异常，更换液压油及密封圈。', '2024-09-10 08:00:00+08'),
    (3, 'repair', 1, 'approved', '激光切割机光路偏移，重新校准光路系统。', '2024-10-05 13:00:00+08'),
    (7, 'repair', 1, 'pending', '真空干燥箱加热异常，待检修。', '2024-10-15 09:00:00+08');

INSERT INTO repair_logs (id, repair_date, fault_description, solution, cost, repair_time) VALUES
    (4, '2024-09-10', '锁模力不稳定，压力波动大', '更换液压油、密封圈，重新调校压力参数', 3500.00, 8),
    (5, '2024-10-05', '切割精度下降，光路偏移', '重新校准光路系统，更换反射镜', 2200.00, 6),
    (6, '2024-10-15', '加热到150℃后温度无法继续上升', '待检修，初步判断加热管故障', NULL, NULL);

-- ========== 7. 巡检日志（2条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (1, 'inspection', 1, 'approved', '日常巡检，各部件运行正常。', '2024-10-01 09:00:00+08'),
    (2, 'inspection', 1, 'approved', '周巡检，主轴润滑良好，导轨无异响。', '2024-10-08 10:00:00+08');

INSERT INTO inspection_logs (id, inspection_date, inspector, inspection_items, result) VALUES
    (7, '2024-10-01', '赵班长', '{"主轴": "正常", "导轨": "正常", "液压系统": "正常", "电气": "正常"}', 'passed'),
    (8, '2024-10-08', '钱工', '{"主轴": "正常", "刀库": "正常", "润滑": "正常", "冷却": "正常"}', 'passed');

-- ========== 8. 保养记录（2条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (1, 'maintenance', 1, 'approved', '季度保养，更换冷却液和液压油。', '2024-09-15 14:00:00+08'),
    (3, 'maintenance', 1, 'approved', '月度保养，清洁镜片，检查气路。', '2024-09-20 10:00:00+08');

INSERT INTO maintenance_records (id, maintenance_date, maintenance_items, next_maintenance_date) VALUES
    (9, '2024-09-15', '{"items": ["更换冷却液", "更换液压油", "清洁过滤网"]}', '2024-12-15'),
    (10, '2024-09-20', '{"items": ["清洁镜片", "检查气路密封", "校准焦距"]}', '2024-10-20');

-- ========== 9. 故障报修（2条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (5, 'fault', 1, 'approved', '超声波清洗机异常停机。', '2024-10-12 11:00:00+08'),
    (8, 'fault', 1, 'approved', '三坐标Z轴移动有异响。', '2024-10-14 15:00:00+08');

INSERT INTO fault_reports (id, fault_date, fault_level, reporter, fault_description, handle_status) VALUES
    (11, '2024-10-12', 'medium', '操作员小张', '清洗过程中突然停机，面板显示E-03错误', 'resolved'),
    (12, '2024-10-14', 'low', '质检员小李', 'Z轴移动时有异常摩擦声', 'processing');

-- ========== 10. 配件更换（2条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (4, 'parts', 1, 'approved', '更换注塑机密封圈和液压油滤芯。', '2024-09-10 11:00:00+08'),
    (1, 'parts', 1, 'approved', '更换车床刀具和刀架定位销。', '2024-09-16 09:30:00+08');

INSERT INTO parts_replacement_logs (id, replacement_date, parts_name, parts_code, quantity, cost) VALUES
    (13, '2024-09-10', '密封圈套装', 'SEAL-SET-001', 1, 800.00),
    (14, '2024-09-16', '车床刀具', 'TOOL-001', 5, 1200.00);

-- ========== 11. 校准记录（2条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (8, 'calibration', 1, 'approved', '三坐标测量机年度校准。', '2024-09-01 10:00:00+08'),
    (3, 'calibration', 1, 'approved', '激光切割机定位精度校准。', '2024-09-05 14:00:00+08');

INSERT INTO calibration_logs (id, calibration_date, calibration_org, calibration_result, next_calibration_date) VALUES
    (15, '2024-09-01', '上海市计量测试技术研究院', 'qualified', '2025-09-01'),
    (16, '2024-09-05', '大族激光售后校准中心', 'qualified', '2025-03-05');

-- ========== 12. 报废日志（1条）==========
INSERT INTO logs (equipment_id, log_type, operator_id, status, description, created_at) VALUES
    (10, 'scrap', 1, 'approved', '旧式车床使用年限过长，已报废处理。', '2024-08-20 16:00:00+08');

INSERT INTO scrap_logs (id, scrap_date, scrap_reason, residual_value) VALUES
    (17, '2024-08-20', '设备使用超过10年，精度严重下降，无法满足加工要求，经评估无维修价值', 3500.00);

-- ========== 13. 通知（5条）==========
INSERT INTO notifications (user_id, title, content, type, is_read, equipment_id, created_at) VALUES
    (1, '保养提醒', '设备 EQ-2024-001 即将到达下次保养日期，请及时安排保养。', 'maintenance', false, 1, '2024-12-01 09:00:00+08'),
    (1, '校准到期', '设备 EQ-2024-008 三坐标测量机校准证书即将到期，请及时复校。', 'calibration', false, 8, '2024-11-15 10:00:00+08'),
    (1, '故障待处理', '设备 EQ-2024-007 真空干燥箱故障报修待处理。', 'fault', false, 7, '2024-10-15 09:30:00+08'),
    (1, '审批通知', '维修日志已通过审批，请查看详情。', 'approval', true, 4, '2024-09-11 14:00:00+08'),
    (1, '系统通知', '欢迎使用设备信息动态管理系统，初始密码请及时修改。', 'system', true, NULL, '2024-07-18 00:00:00+08');

-- ========== 14. 审计日志（5条）==========
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, ip_address, created_at) VALUES
    (1, 'login', 'auth', NULL, '{"user": "admin", "action": "用户登录"}', '127.0.0.1', '2024-07-18 00:46:00+08'),
    (1, 'create', 'equipment', 1, '{"code": "EQ-2024-001", "name": "数控车床 CK6140"}', '127.0.0.1', '2024-03-20 10:00:00+08'),
    (1, 'update', 'equipment', 4, '{"field": "status", "old": "running", "new": "repairing"}', '127.0.0.1', '2024-09-10 08:00:00+08'),
    (1, 'create', 'log', 17, '{"log_type": "scrap", "equipment": "EQ-2023-010"}', '127.0.0.1', '2024-08-20 16:00:00+08'),
    (1, 'export', 'equipment', NULL, '{"format": "csv", "count": 10}', '127.0.0.1', '2024-10-01 11:00:00+08');

-- ========== 15. 用户反馈（3条）==========
INSERT INTO feedbacks (user_id, title, content, reply, replied_by, replied_at, is_read, status, created_at) VALUES
    (2, '建议增加设备二维码扫码功能', '希望能为每台设备生成二维码，扫码即可查看设备信息和历史日志，方便现场操作。', '感谢您的建议，该功能已纳入下个版本开发计划，预计v1.2版本上线。', 1, '2024-10-05 15:00:00+08', true, 'replied', '2024-10-01 09:00:00+08'),
    (2, '仪表盘数据加载较慢', '设备数量增加后，仪表盘加载时间明显变长，约3-4秒，建议优化。', NULL, NULL, NULL, false, 'open', '2024-10-10 14:00:00+08'),
    (2, '密码修改功能使用问题', '修改密码后无法立即重新登录，需要等几分钟，是正常现象吗？', '这是Token缓存导致的正常现象，旧Token失效后即可使用新密码登录，通常1分钟内。', 1, '2024-10-12 11:00:00+08', false, 'replied', '2024-10-12 10:30:00+08');

COMMIT;

-- ========== 验证查询 ==========
SELECT '=== 数据统计 ===' AS info;
SELECT 'users' AS tbl, count(*) AS cnt FROM users
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'equipment', count(*) FROM equipment
UNION ALL SELECT 'logs', count(*) FROM logs
UNION ALL SELECT 'installation_logs', count(*) FROM installation_logs
UNION ALL SELECT 'repair_logs', count(*) FROM repair_logs
UNION ALL SELECT 'inspection_logs', count(*) FROM inspection_logs
UNION ALL SELECT 'maintenance_records', count(*) FROM maintenance_records
UNION ALL SELECT 'fault_reports', count(*) FROM fault_reports
UNION ALL SELECT 'parts_replacement_logs', count(*) FROM parts_replacement_logs
UNION ALL SELECT 'calibration_logs', count(*) FROM calibration_logs
UNION ALL SELECT 'scrap_logs', count(*) FROM scrap_logs
UNION ALL SELECT 'notifications', count(*) FROM notifications
UNION ALL SELECT 'audit_logs', count(*) FROM audit_logs
UNION ALL SELECT 'feedbacks', count(*) FROM feedbacks
UNION ALL SELECT 'approval_configs', count(*) FROM approval_configs
UNION ALL SELECT 'system_configs', count(*) FROM system_configs
ORDER BY tbl;

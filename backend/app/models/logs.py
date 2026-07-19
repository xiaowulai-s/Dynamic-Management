from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Log(Base):
    """日志基础模型（单表继承）"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True, comment="设备ID")
    log_type = Column(String(30), nullable=False, index=True, comment="日志类型")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="操作人ID（删除用户时置空）")
    status = Column(String(20), nullable=False, default="pending", index=True, comment="状态：pending/approved/rejected")
    description = Column(Text, comment="描述")
    attachments = Column(JSON, comment="附件列表（文件路径）")
    approved_at = Column(DateTime(timezone=True), comment="审批时间")
    approver_id = Column(Integer, ForeignKey("users.id"), comment="审批人ID")
    rejection_reason = Column(Text, comment="驳回原因")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="创建时间")

    # 关系（P3: 启用 relationship 以支持 joinedload 优化 N+1 查询）
    equipment = relationship("Equipment", back_populates="logs")
    operator = relationship("User", foreign_keys=[operator_id])
    approver = relationship("User", foreign_keys=[approver_id])

    def __repr__(self):
        return f"<Log(id={self.id}, log_type='{self.log_type}', status='{self.status}')>"


class InstallationLog(Base):
    """设备安装日志"""
    __tablename__ = "installation_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    installation_date = Column(DateTime(timezone=True), nullable=False, comment="安装日期")
    installer = Column(String(100), comment="安装人员")
    location = Column(String(100), comment="安装位置")
    acceptance_status = Column(String(20), comment="验收状态")


class RepairLog(Base):
    """设备维修日志"""
    __tablename__ = "repair_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    repair_date = Column(DateTime(timezone=True), nullable=False, comment="维修日期")
    fault_description = Column(Text, comment="故障描述")
    solution = Column(Text, comment="解决方案")
    cost = Column(Numeric(10, 2), comment="维修费用（元）")  # Q7: 统一为 Numeric(10,2)
    repair_time = Column(Integer, comment="维修时长（小时）")


class ScrapLog(Base):
    """设备报废日志"""
    __tablename__ = "scrap_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    scrap_date = Column(DateTime(timezone=True), nullable=False, comment="报废日期")
    scrap_reason = Column(Text, comment="报废原因")
    residual_value = Column(Numeric(10, 2), comment="残值（元）")  # Q7: 统一为 Numeric(10,2)


class InspectionLog(Base):
    """日常巡检日志"""
    __tablename__ = "inspection_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    inspection_date = Column(DateTime(timezone=True), nullable=False, comment="巡检日期")
    inspector = Column(String(100), comment="巡检人员")
    inspection_items = Column(JSON, comment="巡检项目列表")
    result = Column(String(20), comment="结果：normal/abnormal")


class MaintenanceRecord(Base):
    """保养记录"""
    __tablename__ = "maintenance_records"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    maintenance_date = Column(DateTime(timezone=True), nullable=False, comment="保养日期")
    maintenance_items = Column(JSON, comment="保养项目列表")
    next_maintenance_date = Column(DateTime(timezone=True), index=True, comment="下次保养日期")  # P13: 添加索引


class FaultReport(Base):
    """故障报修日志"""
    __tablename__ = "fault_reports"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    fault_date = Column(DateTime(timezone=True), nullable=False, comment="故障时间")
    fault_level = Column(String(20), comment="故障等级：minor/major/critical")
    reporter = Column(String(100), comment="报修人")
    fault_description = Column(Text, comment="故障描述")
    handle_status = Column(String(20), comment="处理状态：pending/handling/resolved")


class PartsReplacementLog(Base):
    """配件更换日志"""
    __tablename__ = "parts_replacement_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    replacement_date = Column(DateTime(timezone=True), nullable=False, comment="更换日期")
    parts_name = Column(String(100), comment="配件名称")
    parts_code = Column(String(50), comment="配件编号")
    quantity = Column(Integer, comment="数量")
    cost = Column(Numeric(10, 2), comment="费用（元）")  # Q7: 统一为 Numeric(10,2)


class CalibrationLog(Base):
    """校准记录"""
    __tablename__ = "calibration_logs"

    id = Column(Integer, ForeignKey("logs.id"), primary_key=True, comment="日志ID")
    calibration_date = Column(DateTime(timezone=True), nullable=False, comment="校准日期")
    calibration_org = Column(String(100), comment="校准机构")
    calibration_result = Column(String(20), comment="校准结果：qualified/unqualified")
    next_calibration_date = Column(DateTime(timezone=True), index=True, comment="下次校准日期")  # P14: 添加索引

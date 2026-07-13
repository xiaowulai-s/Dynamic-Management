from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from app.database import Base


class ApprovalConfig(Base):
    """审批配置模型"""
    __tablename__ = "approval_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_type = Column(String(30), nullable=False, unique=True, comment="日志类型")
    require_approval = Column(Boolean, default=True, comment="是否需要审批")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<ApprovalConfig(id={self.id}, log_type='{self.log_type}', require_approval={self.require_approval})>"


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False, index=True, comment="配置键")
    config_value = Column(JSON, nullable=False, comment="配置值")
    description = Column(Text, comment="配置说明")
    updated_by = Column(Integer, ForeignKey("users.id"), comment="更新人ID")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<SystemConfig(id={self.id}, key='{self.config_key}')>"


class AuditLog(Base):
    """操作审计日志"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), comment="操作用户ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    resource_type = Column(String(50), comment="资源类型")
    resource_id = Column(Integer, comment="资源ID")
    details = Column(JSON, comment="详细信息")
    ip_address = Column(String(45), comment="IP地址")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="操作时间")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"

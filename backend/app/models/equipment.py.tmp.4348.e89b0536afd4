from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Equipment(Base):
    """设备模型"""
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="设备编号")
    name = Column(String(100), nullable=False, comment="设备名称")
    model = Column(String(100), comment="型号")
    specification = Column(Text, comment="规格")
    manufacturer = Column(String(100), comment="生产厂家")
    purchase_date = Column(Date, comment="购置日期")
    supplier = Column(String(100), comment="供应商")
    location = Column(String(100), comment="安装位置")
    status = Column(String(20), nullable=False, default="running", comment="状态：running/stopped/repairing/scrapped")
    lifecycle_status = Column(String(20), nullable=False, default="active", comment="生命周期状态：active/maintenance/scrapped")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    notifications = relationship("Notification", back_populates="equipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Equipment(id={self.id}, code='{self.code}', name='{self.name}')>"

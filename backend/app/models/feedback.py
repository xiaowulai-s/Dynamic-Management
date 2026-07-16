from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Feedback(Base):
    """用户反馈模型"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="提交用户")
    title = Column(String(200), nullable=False, comment="反馈标题")
    content = Column(Text, nullable=False, comment="反馈内容")
    reply = Column(Text, nullable=True, comment="管理员回复")
    replied_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="回复人ID")
    replied_at = Column(DateTime(timezone=True), nullable=True, comment="回复时间")
    is_read = Column(Boolean, default=False, comment="用户是否已读回复")
    status = Column(String(20), default="open", comment="状态：open/replied/closed")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    user = relationship("User", foreign_keys=[user_id], backref="feedbacks")
    replier = relationship("User", foreign_keys=[replied_by])

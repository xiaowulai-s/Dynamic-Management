from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.approval import AuditLog
from app.models.user import User
from app.utils.auth import get_current_user, require_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class AuditLogResponse(BaseModel):
    """审计日志响应（Q6: 使用模型真实字段）"""
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource_type: str = None,
    resource_id: int = None,
    details: str = None,
    ip_address: str = None
):
    """快捷写入审计日志（Q6: 使用真实字段名）"""
    import json
    al = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.loads(details) if details and details.startswith('{') else details,
        ip_address=ip_address
    )
    db.add(al)
    db.commit()


@router.get("/", response_model=list[AuditLogResponse])
def list_audit(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """查询审计日志（S13: 非管理员返回 403；支持分页和过滤）"""
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    items = q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    # 批量查询用户名避免 N+1
    user_ids = {a.user_id for a in items if a.user_id}
    user_map = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {u.id: u.username for u in users}

    return [
        AuditLogResponse(
            id=a.id, user_id=a.user_id,
            username=user_map.get(a.user_id),
            action=a.action,
            resource_type=a.resource_type,
            resource_id=a.resource_id,
            details=str(a.details) if a.details else None,
            created_at=a.created_at.isoformat()
        )
        for a in items
    ]

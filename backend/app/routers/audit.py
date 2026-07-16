from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.approval import AuditLog
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()

class AuditLogResponse(BaseModel):
    id: int; username: str; action: str; target: Optional[str]=None
    target_id: Optional[int]=None; details: Optional[str]=None
    created_at: str
    class Config: from_attributes=True

def log_action(db: Session, user_id: int, username: str, action: str, target: str = None, target_id: int = None, details: str = None):
    """快捷写入审计日志"""
    al = AuditLog(user_id=user_id, username=username, action=action, target=target, target_id=target_id, details=details)
    db.add(al)
    db.commit()

@router.get("/", response_model=list[AuditLogResponse])
def list_audit(limit: int=Query(100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "super_admin"):
        return []
    items = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [AuditLogResponse(id=a.id, username=a.username, action=a.action, target=a.target,
            target_id=a.target_id, details=a.details, created_at=a.created_at.isoformat()) for a in items]

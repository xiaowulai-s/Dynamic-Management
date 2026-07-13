from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment
from app.models.notification import Notification
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field


router = APIRouter()


# Pydantic 模型
class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    type: Optional[str] = None
    is_read: bool
    equipment_id: Optional[int] = None
    created_at: datetime
    equipment: Optional[dict] = None

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    content: str
    type: Optional[str] = None
    equipment_id: Optional[int] = None


class MarkReadResponse(BaseModel):
    message: str
    count: int


@router.get("/", response_model=List[NotificationResponse], summary="获取通知列表")
async def get_notifications(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(50, ge=1, le=100, description="返回记录数"),
    is_read: Optional[bool] = Query(None, description="是否已读筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的通知列表"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()

    # 组装响应数据
    result = []
    for notification in notifications:
        equipment_data = None
        if notification.equipment:
            equipment_data = {
                "id": notification.equipment.id,
                "name": notification.equipment.name,
                "code": notification.equipment.code,
                "model": notification.equipment.model,
                "location": notification.equipment.location
            }

        result.append(NotificationResponse(
            id=notification.id,
            title=notification.title,
            content=notification.content,
            type=notification.type,
            is_read=notification.is_read,
            equipment_id=notification.equipment_id,
            created_at=notification.created_at,
            equipment=equipment_data
        ))

    return result


@router.get("/unread-count", summary="获取未读通知数量")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户未读通知数量"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False  # noqa: E712
    ).count()
    return {"count": count}


@router.post("/{notification_id}/read", response_model=MarkReadResponse, summary="标记通知为已读")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记单个通知为已读"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )

    notification.is_read = True
    db.commit()

    return MarkReadResponse(message="已标记为已读", count=1)


@router.post("/read-all", response_model=MarkReadResponse, summary="全部标记为已读")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """将所有通知标记为已读"""
    result = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False  # noqa: E712
    ).update({"is_read": True})

    db.commit()

    return MarkReadResponse(message="已全部标记为已读", count=result)


@router.delete("/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除通知"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )

    db.delete(notification)
    db.commit()

    return {"message": "删除成功"}


# 内部函数：创建通知（供其他模块调用）
async def create_notification(
    user_id: int,
    title: str,
    content: str,
    db: Session,
    type: Optional[str] = None,
    equipment_id: Optional[int] = None
):
    """创建通知（内部函数 - 异步版本）"""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=type,
        equipment_id=equipment_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


# 内部函数：创建通知（同步版本 - 供 Celery 任务使用）
def create_notification_sync(
    user_id: int,
    title: str,
    content: str,
    db: Session,
    type: Optional[str] = None,
    equipment_id: Optional[int] = None
):
    """创建通知（同步版本 - 供 Celery 任务调用）"""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=type,
        equipment_id=equipment_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

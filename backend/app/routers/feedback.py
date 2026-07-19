from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.database import get_db
from app.models.feedback import Feedback
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter()


class FeedbackCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)  # Q21: 添加 min_length
    content: str = Field(..., min_length=1, max_length=2000)  # Q21: 添加 min_length


class FeedbackReply(BaseModel):
    reply: str = Field(..., max_length=2000)


class FeedbackResponse(BaseModel):
    id: int
    title: str
    content: str
    reply: Optional[str] = None
    replied_by_name: Optional[str] = None
    replied_at: Optional[str] = None
    is_read: bool
    status: str
    created_at: str
    user_name: str = ""

    class Config:
        from_attributes = True


@router.post("/", response_model=FeedbackResponse, summary="提交反馈")
async def create_feedback(
    data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fb = Feedback(user_id=current_user.id, title=data.title, content=data.content)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackResponse(id=fb.id, title=fb.title, content=fb.content,
                           reply=fb.reply, replied_by_name=None, replied_at=None,
                           is_read=fb.is_read, status=fb.status,
                           created_at=fb.created_at.isoformat(), user_name=current_user.username)


@router.get("/", response_model=List[FeedbackResponse], summary="获取反馈列表")
async def list_feedbacks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取反馈列表（P1: 批量查询用户名，消除 N+1）"""
    if current_user.role in ("admin", "super_admin"):
        items = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    else:
        items = db.query(Feedback).filter(Feedback.user_id == current_user.id).order_by(Feedback.created_at.desc()).all()

    # 批量查询用户名，避免循环内 N+1 查询
    user_ids = {fb.user_id for fb in items if fb.user_id}
    user_ids.update({fb.replied_by for fb in items if fb.replied_by})
    user_map = {}
    if user_ids:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_map = {u.id: u.username for u in users}

    result = []
    for fb in items:
        result.append(FeedbackResponse(
            id=fb.id, title=fb.title, content=fb.content,
            reply=fb.reply,
            replied_by_name=user_map.get(fb.replied_by) if fb.replied_by else None,
            replied_at=fb.replied_at.isoformat() if fb.replied_at else None,
            is_read=fb.is_read, status=fb.status,
            created_at=fb.created_at.isoformat(),
            user_name=user_map.get(fb.user_id, "未知")
        ))
    return result


@router.put("/{feedback_id}/reply", response_model=FeedbackResponse, summary="回复反馈")
async def reply_feedback(
    feedback_id: int,
    data: FeedbackReply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="权限不足")

    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="反馈不存在")

    fb.reply = data.reply
    fb.replied_by = current_user.id
    fb.replied_at = datetime.now(timezone.utc)
    fb.status = "replied"
    fb.is_read = False
    db.commit()
    db.refresh(fb)

    user = db.query(User).filter(User.id == fb.user_id).first()
    replier = db.query(User).filter(User.id == fb.replied_by).first()
    return FeedbackResponse(
        id=fb.id, title=fb.title, content=fb.content,
        reply=fb.reply, replied_by_name=replier.username if replier else None,
        replied_at=fb.replied_at.isoformat(), is_read=fb.is_read, status=fb.status,
        created_at=fb.created_at.isoformat(), user_name=user.username if user else "未知"
    )


@router.put("/{feedback_id}/read", summary="标记已读")
async def mark_read(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记反馈已读（S14: 不存在时返回 404）"""
    fb = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.user_id == current_user.id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="反馈不存在")
    fb.is_read = True
    db.commit()
    return {"message": "ok"}

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
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=2000)


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
    if current_user.role in ("admin", "super_admin"):
        items = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    else:
        items = db.query(Feedback).filter(Feedback.user_id == current_user.id).order_by(Feedback.created_at.desc()).all()

    result = []
    for fb in items:
        user = db.query(User).filter(User.id == fb.user_id).first()
        replier = db.query(User).filter(User.id == fb.replied_by).first() if fb.replied_by else None
        result.append(FeedbackResponse(
            id=fb.id, title=fb.title, content=fb.content,
            reply=fb.reply, replied_by_name=replier.username if replier else None,
            replied_at=fb.replied_at.isoformat() if fb.replied_at else None,
            is_read=fb.is_read, status=fb.status,
            created_at=fb.created_at.isoformat(), user_name=user.username if user else "未知"
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
    fb = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.user_id == current_user.id).first()
    if fb:
        fb.is_read = True
        db.commit()
    return {"message": "ok"}

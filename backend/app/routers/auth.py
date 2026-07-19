from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.config import settings
from app.utils.auth import create_access_token, get_current_user
from pydantic import BaseModel, Field
from typing import Optional
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# 统一密码哈希上下文（Q17/Q18: 模块级复用，统一 passlib）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


# Pydantic模型
class UserRegister(BaseModel):
    """用户注册模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    confirm_password: str = Field(..., description="确认密码")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    role: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str
    user: UserResponse


class PasswordChange(BaseModel):
    """修改密码模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


@router.post("/register", response_model=UserResponse, summary="用户注册")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    - 用户名必须唯一
    - 密码长度至少6位
    - 默认角色为普通用户
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 验证密码是否一致
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )

    # 创建新用户（统一使用 passlib）
    new_user = User(
        username=user_data.username,
        password_hash=pwd_context.hash(user_data.password),
        role="user",  # 默认角色
        is_active=True  # 直接激活（或者需要管理员审批）
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at.isoformat()
    )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录并获取访问令牌
    - 使用OAuth2标准表单格式
    - 返回JWT令牌
    """
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码（统一使用 passlib）
    if not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    logger.info("用户登录成功: %s", user.username)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    # 验证旧密码（统一使用 passlib）
    if not pwd_context.verify(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 更新密码
    current_user.password_hash = pwd_context.hash(password_data.new_password)
    db.commit()

    return {"message": "密码修改成功"}


@router.get("/users", response_model=list[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员可用）
    - super_admin: 可看到所有用户
    - admin: 仅能看到 admin 和 user，看不到 super_admin
    """
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    query = db.query(User)
    # 管理员看不到超级管理员，也看不到测试账号
    if current_user.role == "admin":
        query = query.filter(User.role != "super_admin").filter(User.is_test == False)

    users = query.offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat()
        )
        for user in users
    ]


# ============ 用户管理接口（Q26: 三级角色权限细分） ============

class UserCreate(BaseModel):
    """管理员创建用户模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: str = Field("user", description="角色：super_admin/admin/user")
    is_active: bool = Field(True, description="是否激活")


class UserUpdate(BaseModel):
    """更新用户模型"""
    role: Optional[str] = Field(None, description="角色：super_admin/admin/user")
    is_active: Optional[bool] = Field(None, description="是否激活")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码（可选）")


@router.post("/users", response_model=UserResponse, summary="创建用户（管理员）")
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建用户
    - super_admin/admin 可用
    - admin 不能创建 super_admin
    - 用户名必须唯一
    """
    # 权限校验
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # admin 不能创建 super_admin
    if user_data.role == "super_admin" and current_user.role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权创建超级管理员")

    # 角色合法性
    if user_data.role not in ("super_admin", "admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")

    # 用户名唯一
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    new_user = User(
        username=user_data.username,
        password_hash=pwd_context.hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("用户 %s 创建了新用户: %s (%s)", current_user.username, new_user.username, new_user.role)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        is_active=new_user.is_active,
        created_at=new_user.created_at.isoformat()
    )


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户（管理员）")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户角色/状态/密码
    - super_admin: 可更新所有人
    - admin: 不能更新 super_admin；不能将用户提升为 super_admin
    """
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # admin 不能操作 super_admin
    if current_user.role == "admin" and target.role == "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权修改超级管理员")

    # admin 不能将用户提升为 super_admin
    if current_user.role == "admin" and user_data.role == "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权设置超级管理员角色")

    # 角色合法性
    if user_data.role is not None and user_data.role not in ("super_admin", "admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效的角色")

    if user_data.role is not None:
        target.role = user_data.role
    if user_data.is_active is not None:
        target.is_active = user_data.is_active
    if user_data.password is not None:
        target.password_hash = pwd_context.hash(user_data.password)

    db.commit()
    db.refresh(target)

    logger.info("用户 %s 更新了用户: %s", current_user.username, target.username)

    return UserResponse(
        id=target.id,
        username=target.username,
        role=target.role,
        is_active=target.is_active,
        created_at=target.created_at.isoformat()
    )


@router.delete("/users/{user_id}", summary="删除用户（管理员）")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户
    - super_admin: 可删除所有人（但不能删自己）
    - admin: 只能删除 admin/user，不能删除 super_admin，也不能删自己
    - 删除前置空所有外键引用，保留历史数据（设备/日志/反馈的创建人/操作人显示为"未知"）
    """
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    # 不能删除自己
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录用户")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # admin 不能删除 super_admin
    if current_user.role == "admin" and target.role == "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除超级管理员")

    # 置空所有外键引用，避免破坏历史数据
    from app.models.equipment import Equipment
    from app.models.logs import Log
    from app.models.feedback import Feedback
    from app.models.approval import ApprovalConfig, SystemConfig, AuditLog

    # nullable=False 已迁移为 nullable=True 的字段：直接置空
    db.query(Equipment).filter(Equipment.created_by == user_id).update({Equipment.created_by: None})
    db.query(Log).filter(Log.operator_id == user_id).update({Log.operator_id: None})
    db.query(Feedback).filter(Feedback.user_id == user_id).update({Feedback.user_id: None})

    # 原本就 nullable=True 的字段：置空
    db.query(Log).filter(Log.approver_id == user_id).update({Log.approver_id: None})
    db.query(Feedback).filter(Feedback.replied_by == user_id).update({Feedback.replied_by: None})
    db.query(ApprovalConfig).filter(ApprovalConfig.created_by == user_id).update({ApprovalConfig.created_by: None})
    db.query(SystemConfig).filter(SystemConfig.updated_by == user_id).update({SystemConfig.updated_by: None})
    db.query(AuditLog).filter(AuditLog.user_id == user_id).update({AuditLog.user_id: None})

    # 通知表有 cascade delete-orphan，会随用户一起删除，无需手动处理

    db.delete(target)
    db.commit()

    logger.info("用户 %s 删除了用户: %s", current_user.username, target.username)

    return {"message": "用户删除成功"}

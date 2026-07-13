from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.approval import ApprovalConfig, SystemConfig
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


# 审批配置模型
class ApprovalConfigResponse(BaseModel):
    id: int
    log_type: str
    require_approval: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalConfigUpdate(BaseModel):
    log_type: str
    require_approval: bool


# 系统配置模型
class SystemConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: Any
    description: str | None
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemConfigUpdate(BaseModel):
    config_key: str
    config_value: Any
    description: str | None = None


@router.get("/approval-configs", response_model=list[ApprovalConfigResponse], summary="获取审批配置")
async def get_approval_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有日志类型的审批配置"""
    configs = db.query(ApprovalConfig).all()
    return configs


@router.put("/approval-configs/{config_id}", response_model=ApprovalConfigResponse, summary="更新审批配置")
async def update_approval_config(
    config_id: int,
    config_data: ApprovalConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新审批配置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可修改审批配置"
        )

    config = db.query(ApprovalConfig).filter(ApprovalConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )

    config.require_approval = config_data.require_approval
    db.commit()
    db.refresh(config)

    return config


@router.post("/approval-configs", response_model=ApprovalConfigResponse, summary="创建审批配置")
async def create_approval_config(
    config_data: ApprovalConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建审批配置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可创建审批配置"
        )

    # 检查是否已存在
    existing = db.query(ApprovalConfig).filter(
        ApprovalConfig.log_type == config_data.log_type
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该日志类型的配置已存在"
        )

    new_config = ApprovalConfig(
        log_type=config_data.log_type,
        require_approval=config_data.require_approval,
        created_by=current_user.id
    )

    db.add(new_config)
    db.commit()
    db.refresh(new_config)

    return new_config


@router.get("/system-configs", response_model=list[SystemConfigResponse], summary="获取系统配置")
async def get_system_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有系统配置"""
    configs = db.query(SystemConfig).all()
    return configs


@router.get("/system-configs/{config_key}", response_model=SystemConfigResponse, summary="获取单个系统配置")
async def get_system_config(
    config_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个系统配置"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    return config


@router.put("/system-configs/{config_key}", response_model=SystemConfigResponse, summary="更新系统配置")
async def update_system_config(
    config_key: str,
    config_data: SystemConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新系统配置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可修改系统配置"
        )

    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        # 创建新配置
        config = SystemConfig(
            config_key=config_key,
            config_value=config_data.config_value,
            description=config_data.description,
            updated_by=current_user.id
        )
        db.add(config)
    else:
        config.config_value = config_data.config_value
        if config_data.description is not None:
            config.description = config_data.description
        config.updated_by = current_user.id

    db.commit()
    db.refresh(config)

    return config


@router.post("/system-configs", response_model=SystemConfigResponse, summary="创建系统配置")
async def create_system_config(
    config_data: SystemConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建系统配置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可创建系统配置"
        )

    # 检查是否已存在
    existing = db.query(SystemConfig).filter(
        SystemConfig.config_key == config_data.config_key
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该配置已存在"
        )

    new_config = SystemConfig(
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        description=config_data.description,
        updated_by=current_user.id
    )

    db.add(new_config)
    db.commit()
    db.refresh(new_config)

    return new_config


@router.get("/init-configs", summary="初始化默认配置")
async def init_default_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """初始化默认系统配置（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可初始化配置"
        )

    import json

    # 默认配置
    default_configs = [
        {
            "config_key": "maintenance_cycle",
            "config_value": {
                "default": 30,  # 默认30天
                "equipment_types": {
                    "CNC": 15,
                    "注塑机": 30,
                    "冲床": 45,
                    "包装机": 30
                }
            },
            "description": "保养周期配置（天）"
        },
        {
            "config_key": "equipment_life",
            "config_value": {
                "default": 10,  # 默认10年
                "equipment_types": {
                    "CNC": 8,
                    "注塑机": 10,
                    "冲床": 15,
                    "包装机": 8
                }
            },
            "description": "设备设计寿命（年）"
        },
        {
            "config_key": "calibration_cycle",
            "config_value": {
                "default": 180,  # 默认180天
                "equipment_types": {
                    "测量设备": 90,
                    "测试设备": 180
                }
            },
            "description": "校准周期配置（天）"
        },
        {
            "config_key": "fault_levels",
            "config_value": {
                "minor": {"label": "一般", "response_time": 24},  # 24小时内响应
                "major": {"label": "严重", "response_time": 4},   # 4小时内响应
                "critical": {"label": "紧急", "response_time": 1}  # 1小时内响应
            },
            "description": "故障等级配置"
        }
    ]

    created_count = 0
    for config_data in default_configs:
        existing = db.query(SystemConfig).filter(
            SystemConfig.config_key == config_data["config_key"]
        ).first()

        if not existing:
            new_config = SystemConfig(
                config_key=config_data["config_key"],
                config_value=config_data["config_value"],
                description=config_data["description"],
                updated_by=current_user.id
            )
            db.add(new_config)
            created_count += 1

    db.commit()

    return {
        "message": "配置初始化完成",
        "created_count": created_count
    }

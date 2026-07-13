from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.equipment import Equipment
from app.models.user import User
from app.utils.auth import get_current_user, require_role
from pydantic import BaseModel, Field
from datetime import datetime, date

router = APIRouter()


# Pydantic模型
class EquipmentBase(BaseModel):
    """设备基础模型"""
    code: str = Field(..., description="设备编号")
    name: str = Field(..., description="设备名称")
    model: Optional[str] = Field(None, description="型号")
    specification: Optional[str] = Field(None, description="规格")
    manufacturer: Optional[str] = Field(None, description="生产厂家")
    purchase_date: Optional[date] = Field(None, description="购置日期")
    supplier: Optional[str] = Field(None, description="供应商")
    location: Optional[str] = Field(None, description="安装位置")
    status: str = Field("running", description="状态：running/stopped/repairing/scrapped")
    lifecycle_status: str = Field("active", description="生命周期状态：active/maintenance/scrapped")


class EquipmentCreate(EquipmentBase):
    """创建设备模型"""
    pass


class EquipmentUpdate(BaseModel):
    """更新设备模型"""
    name: Optional[str] = None
    model: Optional[str] = None
    specification: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    supplier: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    lifecycle_status: Optional[str] = None


class EquipmentResponse(EquipmentBase):
    """设备响应模型"""
    id: int
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EquipmentDetail(EquipmentResponse):
    """设备详情模型（包含统计信息）"""
    total_logs: int = 0
    pending_logs: int = 0
    last_maintenance_date: Optional[str] = None
    next_maintenance_date: Optional[str] = None
    total_repair_cost: int = 0

    class Config:
        from_attributes = True


@router.post("/", response_model=EquipmentResponse, summary="创建设备")
async def create_equipment(
    equipment_data: EquipmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新设备
    - 设备编号必须唯一
    - 创建人自动设置为当前用户
    """
    # 检查设备编号是否已存在
    existing_equipment = db.query(Equipment).filter(Equipment.code == equipment_data.code).first()
    if existing_equipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备编号 {equipment_data.code} 已存在"
        )

    # 创建新设备
    new_equipment = Equipment(
        **equipment_data.model_dump(),
        created_by=current_user.id
    )

    db.add(new_equipment)
    db.commit()
    db.refresh(new_equipment)

    return EquipmentResponse(
        id=new_equipment.id,
        code=new_equipment.code,
        name=new_equipment.name,
        model=new_equipment.model,
        specification=new_equipment.specification,
        manufacturer=new_equipment.manufacturer,
        purchase_date=new_equipment.purchase_date.isoformat() if new_equipment.purchase_date else None,
        supplier=new_equipment.supplier,
        location=new_equipment.location,
        status=new_equipment.status,
        lifecycle_status=new_equipment.lifecycle_status,
        created_by=new_equipment.created_by,
        created_at=new_equipment.created_at.isoformat(),
        updated_at=new_equipment.updated_at.isoformat()
    )


@router.get("/", response_model=List[EquipmentResponse], summary="获取设备列表")
async def get_equipments(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（名称/编号/型号）"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取设备列表
    - 支持分页
    - 支持按状态筛选
    - 支持关键词搜索
    """
    query = db.query(Equipment)

    # 状态筛选
    if status:
        query = query.filter(Equipment.status == status)

    # 关键词搜索
    if keyword:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Equipment.name.ilike(f"%{keyword}%"),
                Equipment.code.ilike(f"%{keyword}%"),
                Equipment.model.ilike(f"%{keyword}%")
            )
        )

    # 分页
    equipments = query.offset(skip).limit(limit).all()

    return [
        EquipmentResponse(
            id=eq.id,
            code=eq.code,
            name=eq.name,
            model=eq.model,
            specification=eq.specification,
            manufacturer=eq.manufacturer,
            purchase_date=eq.purchase_date.isoformat() if eq.purchase_date else None,
            supplier=eq.supplier,
            location=eq.location,
            status=eq.status,
            lifecycle_status=eq.lifecycle_status,
            created_by=eq.created_by,
            created_at=eq.created_at.isoformat(),
            updated_at=eq.updated_at.isoformat()
        )
        for eq in equipments
    ]


@router.get("/{equipment_id}", response_model=EquipmentDetail, summary="获取设备详情")
async def get_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取设备详情
    - 包含统计信息
    """
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 统计日志数量
    from app.models.logs import Log, MaintenanceRecord
    total_logs = db.query(Log).filter(Log.equipment_id == equipment_id).count()
    pending_logs = db.query(Log).filter(
        Log.equipment_id == equipment_id,
        Log.status == "pending"
    ).count()

    # 最后保养日期
    last_maintenance = db.query(MaintenanceRecord).join(Log).filter(
        Log.equipment_id == equipment_id,
        Log.status == "approved"
    ).order_by(MaintenanceRecord.maintenance_date.desc()).first()

    # 总维修费用
    from app.models.logs import RepairLog
    total_repair_cost = db.query(RepairLog).join(Log).filter(
        Log.equipment_id == equipment_id,
        Log.status == "approved",
        RepairLog.cost.isnot(None)
    ).all()

    total_cost = sum(r.cost for r in total_repair_cost if r.cost)

    return EquipmentDetail(
        id=equipment.id,
        code=equipment.code,
        name=equipment.name,
        model=equipment.model,
        specification=equipment.specification,
        manufacturer=equipment.manufacturer,
        purchase_date=equipment.purchase_date.isoformat() if equipment.purchase_date else None,
        supplier=equipment.supplier,
        location=equipment.location,
        status=equipment.status,
        lifecycle_status=equipment.lifecycle_status,
        created_by=equipment.created_by,
        created_at=equipment.created_at.isoformat(),
        updated_at=equipment.updated_at.isoformat(),
        total_logs=total_logs,
        pending_logs=pending_logs,
        last_maintenance_date=last_maintenance.maintenance_date.isoformat() if last_maintenance else None,
        next_maintenance_date=last_maintenance.next_maintenance_date.isoformat() if last_maintenance and last_maintenance.next_maintenance_date else None,
        total_repair_cost=total_cost
    )


@router.put("/{equipment_id}", response_model=EquipmentResponse, summary="更新设备")
async def update_equipment(
    equipment_id: int,
    equipment_data: EquipmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新设备信息
    - 仅管理员可更新
    - 只更新提供的字段
    """
    # 检查权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可修改设备信息"
        )

    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 更新设备信息
    update_data = equipment_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(equipment, key, value)

    db.commit()
    db.refresh(equipment)

    return EquipmentResponse(
        id=equipment.id,
        code=equipment.code,
        name=equipment.name,
        model=equipment.model,
        specification=equipment.specification,
        manufacturer=equipment.manufacturer,
        purchase_date=equipment.purchase_date.isoformat() if equipment.purchase_date else None,
        supplier=equipment.supplier,
        location=equipment.location,
        status=equipment.status,
        lifecycle_status=equipment.lifecycle_status,
        created_by=equipment.created_by,
        created_at=equipment.created_at.isoformat(),
        updated_at=equipment.updated_at.isoformat()
    )


@router.delete("/{equipment_id}", summary="删除设备")
async def delete_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除设备
    - 仅管理员可删除
    - 检查是否有关联日志
    """
    # 检查权限
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可删除设备"
        )

    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 检查是否有关联日志
    from app.models.logs import Log
    log_count = db.query(Log).filter(Log.equipment_id == equipment_id).count()
    if log_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备有 {log_count} 条关联日志，无法删除"
        )

    db.delete(equipment)
    db.commit()

    return {"message": "设备删除成功"}

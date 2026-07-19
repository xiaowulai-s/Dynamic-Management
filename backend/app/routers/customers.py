from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.customer import Customer
from app.models.equipment import Equipment
from app.models.user import User
from app.utils.auth import get_current_user, require_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    created_at: str
    equipment_count: int = 0

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CustomerResponse])
def list_customers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取客户列表（S9: 添加认证；P2: 使用聚合查询消除 N+1）"""
    # 一次性聚合查询设备数量
    count_map = dict(
        db.query(Equipment.customer_name, func.count(Equipment.id))
        .group_by(Equipment.customer_name)
        .all()
    )
    items = db.query(Customer).order_by(Customer.name).all()
    return [
        CustomerResponse(
            id=c.id, name=c.name, contact=c.contact, phone=c.phone,
            email=c.email, address=c.address, remark=c.remark,
            created_at=c.created_at.isoformat(),
            equipment_count=count_map.get(c.name, 0)
        )
        for c in items
    ]


@router.post("/", response_model=CustomerResponse)
def create_customer(
    data: CustomerCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if db.query(Customer).filter(Customer.name == data.name).first():
        raise HTTPException(status_code=400, detail="客户名称已存在")
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return CustomerResponse(
        id=c.id, name=c.name, contact=c.contact, phone=c.phone,
        email=c.email, address=c.address, remark=c.remark,
        created_at=c.created_at.isoformat()
    )


@router.put("/{cid}", response_model=CustomerResponse)
def update_customer(
    cid: int,
    data: CustomerCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="不存在")
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    cnt = db.query(func.count(Equipment.id)).filter(Equipment.customer_name == c.name).scalar() or 0
    return CustomerResponse(
        id=c.id, name=c.name, contact=c.contact, phone=c.phone,
        email=c.email, address=c.address, remark=c.remark,
        created_at=c.created_at.isoformat(), equipment_count=cnt
    )


@router.delete("/{cid}")
def delete_customer(
    cid: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c:
        raise HTTPException(status_code=404, detail="不存在")
    # 检查是否有关联设备
    equip_count = db.query(func.count(Equipment.id)).filter(Equipment.customer_name == c.name).scalar() or 0
    if equip_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"该客户下有 {equip_count} 台设备，无法删除。请先转移或删除这些设备。"
        )
    db.delete(c)
    db.commit()
    return {"message": "已删除"}

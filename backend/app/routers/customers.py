from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.utils.auth import get_current_user

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
    class Config: from_attributes = True

@router.get("/", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    items = db.query(Customer).order_by(Customer.name).all()
    from app.models.equipment import Equipment
    result = []
    for c in items:
        count = db.query(Equipment).filter(Equipment.customer_name == c.name).count()
        result.append(CustomerResponse(id=c.id, name=c.name, contact=c.contact, phone=c.phone,
            email=c.email, address=c.address, remark=c.remark,
            created_at=c.created_at.isoformat(), equipment_count=count))
    return result

@router.post("/", response_model=CustomerResponse)
def create_customer(data: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="权限不足")
    if db.query(Customer).filter(Customer.name == data.name).first():
        raise HTTPException(status_code=400, detail="客户名称已存在")
    c = Customer(**data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return CustomerResponse(id=c.id, name=c.name, contact=c.contact, phone=c.phone,
        email=c.email, address=c.address, remark=c.remark, created_at=c.created_at.isoformat())

@router.put("/{cid}", response_model=CustomerResponse)
def update_customer(cid: int, data: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="权限不足")
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c: raise HTTPException(status_code=404, detail="不存在")
    for k, v in data.model_dump().items():
        setattr(c, k, v)
    db.commit(); db.refresh(c)
    from app.models.equipment import Equipment
    cnt = db.query(Equipment).filter(Equipment.customer_name == c.name).count()
    return CustomerResponse(id=c.id, name=c.name, contact=c.contact, phone=c.phone,
        email=c.email, address=c.address, remark=c.remark, created_at=c.created_at.isoformat(), equipment_count=cnt)

@router.delete("/{cid}")
def delete_customer(cid: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="权限不足")
    c = db.query(Customer).filter(Customer.id == cid).first()
    if not c: raise HTTPException(status_code=404, detail="不存在")
    db.delete(c); db.commit()
    return {"message": "已删除"}

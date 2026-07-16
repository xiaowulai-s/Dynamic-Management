from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.models.equipment import Equipment
from app.models.user import User as UserModel
from app.models.logs import Log as LogModel
from app.models.customer import Customer
import json, io, datetime

router = APIRouter()

@router.get("/export-all", summary="导出全量数据")
def export_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=403, detail="权限不足")
    data = {
        "exported_at": datetime.datetime.now().isoformat(),
        "equipment": [],
        "logs": [],
        "customers": [],
        "users": []
    }
    for e in db.query(Equipment).all():
        data["equipment"].append({c.name: str(getattr(e, c.name)) for c in e.__table__.columns})
    for l in db.query(LogModel).all():
        data["logs"].append({c.name: str(getattr(l, c.name)) for c in l.__table__.columns})
    for c in db.query(Customer).all():
        data["customers"].append({col.name: str(getattr(c, col.name)) for col in c.__table__.columns})
    for u in db.query(UserModel).all():
        data["users"].append({"id": u.id, "username": u.username, "nickname": u.nickname, "role": u.role, "is_active": u.is_active, "created_at": str(u.created_at)})
    buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode())
    return StreamingResponse(buf, media_type="application/json", headers={"Content-Disposition": "attachment; filename=backup.json"})

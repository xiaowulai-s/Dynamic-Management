"""CSV 导入导出路由"""
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment
from app.models.logs import Log
from app.utils.auth import get_current_user

router = APIRouter(prefix="/csv", tags=["CSV导入导出"])


def make_csv_response(filename: str, headers: list, rows: list[list]) -> StreamingResponse:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ========== 设备 CSV ==========
@router.get("/equipment/export")
def export_equipment_csv(current_user=Depends(get_current_user), db=Depends(get_db)):
    equipment = db.query(Equipment).all()
    rows = [[eq.code, eq.name, eq.model or "", eq.manufacturer or "", eq.location or "",
             eq.customer_name or "", eq.status or "", eq.lifecycle_status or "",
             str(eq.purchase_date) if eq.purchase_date else "",
             str(eq.warranty_start_date) if eq.warranty_start_date else "",
             str(eq.warranty_duration_months) if eq.warranty_duration_months else ""]
            for eq in equipment]
    return make_csv_response("设备数据.csv",
        ["编号","名称","型号","厂家","位置","客户","状态","生命周期","购置日期","质保起始","质保月数"], rows)


@router.post("/equipment/import")
async def import_equipment_csv(file: UploadFile = File(...), current_user=Depends(get_current_user), db=Depends(get_db)):
    if current_user.role not in ('admin', 'super_admin'):
        raise HTTPException(403, "权限不足")
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
    count = 0
    for row in reader:
        eq = Equipment(
            code=row.get("编号",""), name=row.get("名称",""), model=row.get("型号"),
            manufacturer=row.get("厂家"), location=row.get("位置"),
            customer_name=row.get("客户"), status=row.get("状态","running"),
            lifecycle_status=row.get("生命周期","active"), created_by=current_user.id
        )
        db.add(eq); count += 1
    db.commit()
    return {"imported": count}


# ========== 日志 CSV ==========
@router.get("/logs/export")
def export_logs_csv(current_user=Depends(get_current_user), db=Depends(get_db)):
    logs = db.query(Log).all()
    rows = [[str(l.id), l.equipment_code or "", l.equipment_name or "",
             l.log_type or "", l.operator_name or "", l.status or "",
             l.description or "", str(l.created_at) if l.created_at else ""]
            for l in logs]
    return make_csv_response("日志数据.csv",
        ["ID","设备编号","设备名称","日志类型","操作人","状态","描述","创建时间"], rows)


# ========== 用户 CSV ==========
@router.get("/users/export")
def export_users_csv(current_user=Depends(get_current_user), db=Depends(get_db)):
    if current_user.role not in ('admin', 'super_admin'):
        raise HTTPException(403, "权限不足")
    users = db.query(User).all()
    rows = [[str(u.id), u.username, u.role or "", str(u.is_active), str(u.created_at)]
            for u in users]
    return make_csv_response("用户数据.csv",
        ["ID","用户名","角色","是否启用","创建时间"], rows)


# ========== 客户 CSV ==========
@router.get("/customers/export")
def export_customers_csv(current_user=Depends(get_current_user), db=Depends(get_db)):
    from sqlalchemy import distinct
    customers = db.query(distinct(Equipment.customer_name)).filter(
        Equipment.customer_name.isnot(None), Equipment.customer_name != ''
    ).all()
    rows = [[c[0]] for c in customers]
    return make_csv_response("客户列表.csv", ["客户名称"], rows)

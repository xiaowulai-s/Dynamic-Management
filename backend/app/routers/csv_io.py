"""CSV 导入导出路由"""
import csv
import io
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment
from app.models.logs import Log
from app.models.customer import Customer
from app.utils.auth import get_current_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/csv", tags=["CSV导入导出"])

# CSV 文件大小上限 10MB（B12）
MAX_CSV_SIZE = 10 * 1024 * 1024
# 导入行数上限（B8）
MAX_IMPORT_ROWS = 5000


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
def export_equipment_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出设备 CSV（S10: 已有认证，字段以实际模型为准）"""
    equipment = db.query(Equipment).all()
    rows = [[eq.code, eq.name, eq.model or "", eq.manufacturer or "", eq.location or "",
             getattr(eq, "customer_name", "") or "", eq.status or "", eq.lifecycle_status or "",
             str(eq.purchase_date) if eq.purchase_date else ""]
            for eq in equipment]
    return make_csv_response("设备数据.csv",
        ["编号", "名称", "型号", "厂家", "位置", "客户", "状态", "生命周期", "购置日期"], rows)


@router.post("/equipment/import")
async def import_equipment_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """导入设备 CSV（B8: 增加数据校验、大小限制、错误处理）"""
    content = await file.read()
    if len(content) > MAX_CSV_SIZE:
        raise HTTPException(400, f"文件过大，最大支持 {MAX_CSV_SIZE // 1024 // 1024}MB")

    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            text = content.decode('gbk')
        except UnicodeDecodeError:
            raise HTTPException(400, "文件编码不支持，请使用 UTF-8 或 GBK")

    reader = csv.DictReader(io.StringIO(text))
    # 校验必填列
    if not reader.fieldnames or "编号" not in reader.fieldnames or "名称" not in reader.fieldnames:
        raise HTTPException(400, "CSV 缺少必填列：编号、名称")

    valid_statuses = {"running", "stopped", "repairing", "scrapped"}
    valid_lifecycle = {"active", "maintenance", "scrapped"}
    imported = 0
    errors = []

    for i, row in enumerate(reader, start=2):  # 第2行开始（第1行是表头）
        if imported >= MAX_IMPORT_ROWS:
            errors.append(f"已达导入上限 {MAX_IMPORT_ROWS} 行，后续行已跳过")
            break

        code = (row.get("编号") or "").strip()
        name = (row.get("名称") or "").strip()
        if not code:
            errors.append(f"第{i}行：编号不能为空")
            continue
        if not name:
            errors.append(f"第{i}行：名称不能为空")
            continue

        status = (row.get("状态") or "running").strip()
        if status not in valid_statuses:
            errors.append(f"第{i}行：状态值'{status}'无效，已设为默认值")
            status = "running"

        lifecycle = (row.get("生命周期") or "active").strip()
        if lifecycle not in valid_lifecycle:
            lifecycle = "active"

        # 唯一性校验
        if db.query(Equipment).filter(Equipment.code == code).first():
            errors.append(f"第{i}行：编号'{code}'已存在，跳过")
            continue

        eq = Equipment(
            code=code, name=name, model=row.get("型号"),
            manufacturer=row.get("厂家"), location=row.get("位置"),
            customer_name=row.get("客户"), status=status,
            lifecycle_status=lifecycle, created_by=current_user.id
        )
        db.add(eq)
        imported += 1

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("CSV 导入提交失败")
        raise HTTPException(400, f"导入失败，已回滚：{str(e)}")

    return {"imported": imported, "errors": errors[:50] if errors else None}


# ========== 日志 CSV ==========
@router.get("/logs/export")
def export_logs_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """导出日志 CSV（S11: 添加管理员权限校验；Q4: 使用 join 获取关联字段）"""
    from app.models.equipment import Equipment
    from app.models.user import User as UserModel

    rows_data = (
        db.query(
            Log.id, Equipment.code, Equipment.name, Log.log_type,
            UserModel.username, Log.status, Log.description, Log.created_at
        )
        .join(Equipment, Log.equipment_id == Equipment.id)
        .join(UserModel, Log.operator_id == UserModel.id)
        .all()
    )
    rows = [[str(r[0]), r[1] or "", r[2] or "", r[3] or "", r[4] or "",
             r[5] or "", r[6] or "", str(r[7]) if r[7] else ""]
            for r in rows_data]
    return make_csv_response("日志数据.csv",
        ["ID", "设备编号", "设备名称", "日志类型", "操作人", "状态", "描述", "创建时间"], rows)


# ========== 用户 CSV ==========
@router.get("/users/export")
def export_users_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """导出用户 CSV（S12: 已有管理员校验）"""
    users = db.query(User).all()
    rows = [[str(u.id), u.username, u.role or "", str(u.is_active), str(u.created_at)]
            for u in users]
    return make_csv_response("用户数据.csv",
        ["ID", "用户名", "角色", "是否启用", "创建时间"], rows)


# ========== 客户 CSV ==========
@router.get("/customers/export")
def export_customers_csv(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """导出客户 CSV（S12: 添加管理员校验；改用 Customer 表）"""
    customers = db.query(Customer).order_by(Customer.name).all()
    rows = [[c.name, c.contact or "", c.phone or "", c.email or "", c.address or ""]
            for c in customers]
    return make_csv_response("客户列表.csv",
        ["客户名称", "联系人", "电话", "邮箱", "地址"], rows)

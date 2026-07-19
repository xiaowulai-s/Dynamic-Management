import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime

from app.database import get_db
from app.models.logs import (
    Log, InstallationLog, RepairLog, ScrapLog,
    InspectionLog, MaintenanceRecord, FaultReport,
    PartsReplacementLog, CalibrationLog
)
from app.models.equipment import Equipment
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel, Field
from enum import Enum

router = APIRouter()


# 枚举类型
class LogType(str, Enum):
    installation = "installation"
    repair = "repair"
    scrap = "scrap"
    inspection = "inspection"
    maintenance = "maintenance"
    fault = "fault"
    parts = "parts"
    calibration = "calibration"


class LogStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


# Pydantic 模型
class LogBase(BaseModel):
    equipment_id: int = Field(..., description="设备ID")
    description: Optional[str] = Field(None, description="描述")


class LogResponse(LogBase):
    id: int
    log_type: str
    operator_name: str
    equipment_name: str
    status: str
    approved_at: Optional[str] = None
    approver_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    attachments: Optional[List[str]] = []
    created_at: str

    class Config:
        from_attributes = True


class InstallationLogCreate(LogBase):
    log_type: str = "installation"
    installation_date: datetime = Field(..., description="安装日期")
    installer: Optional[str] = None
    location: Optional[str] = None
    acceptance_status: Optional[str] = None


class RepairLogCreate(LogBase):
    log_type: str = "repair"
    repair_date: datetime = Field(..., description="维修日期")
    fault_description: str = Field(..., description="故障描述")
    solution: Optional[str] = None
    cost: Optional[int] = None
    repair_time: Optional[int] = None


class ScrapLogCreate(LogBase):
    log_type: str = "scrap"
    scrap_date: datetime = Field(..., description="报废日期")
    scrap_reason: str = Field(..., description="报废原因")
    residual_value: Optional[int] = None


class InspectionLogCreate(LogBase):
    log_type: str = "inspection"
    inspection_date: datetime = Field(..., description="巡检日期")
    inspector: Optional[str] = None
    inspection_items: Optional[list] = None
    result: Optional[str] = "normal"


class MaintenanceRecordCreate(LogBase):
    log_type: str = "maintenance"
    maintenance_date: datetime = Field(..., description="保养日期")
    maintenance_items: Optional[list] = None
    next_maintenance_date: Optional[datetime] = None


class FaultReportCreate(LogBase):
    log_type: str = "fault"
    fault_date: datetime = Field(..., description="故障时间")
    fault_level: Optional[str] = "minor"
    reporter: Optional[str] = None
    fault_description: str = Field(..., description="故障描述")
    handle_status: Optional[str] = "pending"


class PartsReplacementLogCreate(LogBase):
    log_type: str = "parts"
    replacement_date: datetime = Field(..., description="更换日期")
    parts_name: str = Field(..., description="配件名称")
    parts_code: Optional[str] = None
    quantity: int = Field(..., description="数量")
    cost: Optional[int] = None


class CalibrationLogCreate(LogBase):
    log_type: str = "calibration"
    calibration_date: datetime = Field(..., description="校准日期")
    calibration_org: Optional[str] = None
    calibration_result: Optional[str] = "qualified"
    next_calibration_date: Optional[datetime] = None


class LogDetailResponse(LogResponse):
    """日志详情响应"""
    detail_data: dict = {}  # 具体日志类型的详细信息

    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    """审批操作模型"""
    approved: bool = Field(..., description="是否批准")
    rejection_reason: Optional[str] = Field(None, description="驳回原因")


@router.post("/", response_model=LogResponse, summary="创建日志")
async def create_log(
    log_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新日志
    - 根据 log_type 创建不同类型的日志
    - 检查是否需要审批
    """
    log_type = log_data.get("log_type")
    equipment_id = log_data.get("equipment_id")

    if not log_type or not equipment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要字段：log_type, equipment_id"
        )

    # 验证设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 检查是否需要审批
    from app.models.approval import ApprovalConfig
    approval_config = db.query(ApprovalConfig).filter(
        ApprovalConfig.log_type == log_type
    ).first()

    require_approval = approval_config.require_approval if approval_config else True
    status_value = "pending" if require_approval else "approved"

    # 创建基础日志
    new_log = Log(
        equipment_id=equipment_id,
        log_type=log_type,
        operator_id=current_user.id,
        status=status_value,
        description=log_data.get("description"),
        attachments=log_data.get("attachments", []),
        approved_at=datetime.utcnow() if not require_approval else None,
        approver_id=current_user.id if not require_approval else None
    )

    db.add(new_log)
    db.flush()  # 获取 new_log.id

    # 根据类型创建具体日志
    try:
        if log_type == "installation":
            db.add(InstallationLog(
                id=new_log.id,
                installation_date=log_data["installation_date"],
                installer=log_data.get("installer"),
                location=log_data.get("location"),
                acceptance_status=log_data.get("acceptance_status")
            ))

        elif log_type == "repair":
            db.add(RepairLog(
                id=new_log.id,
                repair_date=log_data["repair_date"],
                fault_description=log_data["fault_description"],
                solution=log_data.get("solution"),
                cost=log_data.get("cost"),
                repair_time=log_data.get("repair_time")
            ))

        elif log_type == "scrap":
            db.add(ScrapLog(
                id=new_log.id,
                scrap_date=log_data["scrap_date"],
                scrap_reason=log_data["scrap_reason"],
                residual_value=log_data.get("residual_value")
            ))

        elif log_type == "inspection":
            db.add(InspectionLog(
                id=new_log.id,
                inspection_date=log_data["inspection_date"],
                inspector=log_data.get("inspector"),
                inspection_items=log_data.get("inspection_items", []),
                result=log_data.get("result", "normal")
            ))

        elif log_type == "maintenance":
            db.add(MaintenanceRecord(
                id=new_log.id,
                maintenance_date=log_data["maintenance_date"],
                maintenance_items=log_data.get("maintenance_items", []),
                next_maintenance_date=log_data.get("next_maintenance_date")
            ))

        elif log_type == "fault":
            db.add(FaultReport(
                id=new_log.id,
                fault_date=log_data["fault_date"],
                fault_level=log_data.get("fault_level", "minor"),
                reporter=log_data.get("reporter"),
                fault_description=log_data["fault_description"],
                handle_status=log_data.get("handle_status", "pending")
            ))

        elif log_type == "parts":
            db.add(PartsReplacementLog(
                id=new_log.id,
                replacement_date=log_data["replacement_date"],
                parts_name=log_data["parts_name"],
                parts_code=log_data.get("parts_code"),
                quantity=log_data["quantity"],
                cost=log_data.get("cost")
            ))

        elif log_type == "calibration":
            db.add(CalibrationLog(
                id=new_log.id,
                calibration_date=log_data["calibration_date"],
                calibration_org=log_data.get("calibration_org"),
                calibration_result=log_data.get("calibration_result", "qualified"),
                next_calibration_date=log_data.get("next_calibration_date")
            ))

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的日志类型: {log_type}"
            )

        db.commit()
        db.refresh(new_log)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建日志失败: {str(e)}"
        )

    # 构建响应
    approver = db.query(User).filter(User.id == new_log.approver_id).first() if new_log.approver_id else None
    return LogResponse(
        id=new_log.id,
        equipment_id=new_log.equipment_id,
        log_type=new_log.log_type,
        description=new_log.description,
        equipment_name=equipment.name,
        operator_name=current_user.username,
        status=new_log.status,
        attachments=new_log.attachments or [],
        created_at=new_log.created_at.isoformat(),
        approved_at=new_log.approved_at.isoformat() if new_log.approved_at else None,
        approver_name=approver.username if approver else None
    )


@router.get("/", response_model=List[LogResponse], summary="获取日志列表")
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    equipment_id: Optional[int] = Query(None, description="按设备筛选"),
    log_type: Optional[str] = Query(None, description="按类型筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日志列表"""
    from app.models.logs import Log as LogModel

    query = db.query(LogModel)

    # 筛选条件
    if equipment_id:
        query = query.filter(LogModel.equipment_id == equipment_id)

    if log_type:
        query = query.filter(LogModel.log_type == log_type)

    if status:
        query = query.filter(LogModel.status == status)

    if keyword:
        from sqlalchemy import or_
        query = query.join(Equipment).filter(
            or_(
                Equipment.name.ilike(f"%{keyword}%"),
                Equipment.code.ilike(f"%{keyword}%"),
                LogModel.description.ilike(f"%{keyword}%")
            )
        )

    # 按创建时间倒序
    logs = query.order_by(LogModel.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for log in logs:
        equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()
        operator = db.query(User).filter(User.id == log.operator_id).first()
        approver = db.query(User).filter(User.id == log.approver_id).first() if log.approver_id else None

        result.append(LogResponse(
            id=log.id,
            equipment_id=log.equipment_id,
            log_type=log.log_type,
            description=log.description,
            equipment_name=equipment.name if equipment else "未知",
            operator_name=operator.username if operator else "未知",
            status=log.status,
            attachments=log.attachments or [],
            created_at=log.created_at.isoformat(),
            approved_at=log.approved_at.isoformat() if log.approved_at else None,
            approver_name=approver.username if approver else None
        ))

    return result


@router.get("/{log_id}", response_model=LogDetailResponse, summary="获取日志详情")
async def get_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日志详情"""
    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )

    equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()
    operator = db.query(User).filter(User.id == log.operator_id).first()
    approver = db.query(User).filter(User.id == log.approver_id).first() if log.approver_id else None

    # 获取具体日志详情
    detail_data = {}
    if log.log_type == "installation":
        detail = db.query(InstallationLog).filter(InstallationLog.id == log.id).first()
        if detail:
            detail_data = {
                "installation_date": detail.installation_date.isoformat() if detail.installation_date else None,
                "installer": detail.installer,
                "location": detail.location,
                "acceptance_status": detail.acceptance_status
            }
    elif log.log_type == "repair":
        detail = db.query(RepairLog).filter(RepairLog.id == log.id).first()
        if detail:
            detail_data = {
                "repair_date": detail.repair_date.isoformat() if detail.repair_date else None,
                "fault_description": detail.fault_description,
                "solution": detail.solution,
                "cost": detail.cost,
                "repair_time": detail.repair_time
            }
    elif log.log_type == "scrap":
        detail = db.query(ScrapLog).filter(ScrapLog.id == log.id).first()
        if detail:
            detail_data = {
                "scrap_date": detail.scrap_date.isoformat() if detail.scrap_date else None,
                "scrap_reason": detail.scrap_reason,
                "residual_value": detail.residual_value
            }
    elif log.log_type == "inspection":
        detail = db.query(InspectionLog).filter(InspectionLog.id == log.id).first()
        if detail:
            detail_data = {
                "inspection_date": detail.inspection_date.isoformat() if detail.inspection_date else None,
                "inspector": detail.inspector,
                "inspection_items": detail.inspection_items,
                "result": detail.result
            }
    elif log.log_type == "maintenance":
        detail = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == log.id).first()
        if detail:
            detail_data = {
                "maintenance_date": detail.maintenance_date.isoformat() if detail.maintenance_date else None,
                "maintenance_items": detail.maintenance_items,
                "next_maintenance_date": detail.next_maintenance_date.isoformat() if detail.next_maintenance_date else None
            }
    elif log.log_type == "fault":
        detail = db.query(FaultReport).filter(FaultReport.id == log.id).first()
        if detail:
            detail_data = {
                "fault_date": detail.fault_date.isoformat() if detail.fault_date else None,
                "fault_level": detail.fault_level,
                "reporter": detail.reporter,
                "fault_description": detail.fault_description,
                "handle_status": detail.handle_status
            }
    elif log.log_type == "parts":
        detail = db.query(PartsReplacementLog).filter(PartsReplacementLog.id == log.id).first()
        if detail:
            detail_data = {
                "replacement_date": detail.replacement_date.isoformat() if detail.replacement_date else None,
                "parts_name": detail.parts_name,
                "parts_code": detail.parts_code,
                "quantity": detail.quantity,
                "cost": detail.cost
            }
    elif log.log_type == "calibration":
        detail = db.query(CalibrationLog).filter(CalibrationLog.id == log.id).first()
        if detail:
            detail_data = {
                "calibration_date": detail.calibration_date.isoformat() if detail.calibration_date else None,
                "calibration_org": detail.calibration_org,
                "calibration_result": detail.calibration_result,
                "next_calibration_date": detail.next_calibration_date.isoformat() if detail.next_calibration_date else None
            }

    return LogDetailResponse(
        id=log.id,
        equipment_id=log.equipment_id,
        log_type=log.log_type,
        description=log.description,
        equipment_name=equipment.name if equipment else "未知",
        operator_name=operator.username if operator else "未知",
        status=log.status,
        attachments=log.attachments or [],
        created_at=log.created_at.isoformat(),
        approved_at=log.approved_at.isoformat() if log.approved_at else None,
        approver_name=approver.username if approver else None,
        rejection_reason=log.rejection_reason,
        detail_data=detail_data
    )


@router.put("/{log_id}", summary="更新日志")
async def update_log(
    log_id: int,
    log_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新日志
    - 只能更新description字段
    - 普通用户：仅能更新自己创建的、待审批或已驳回状态的日志
    - 管理员/超级管理员：可更新任意待审批或已驳回状态的日志
    """
    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )

    # 权限校验（Q26: 三级角色细分）
    is_admin_role = current_user.role in ("admin", "super_admin")
    if not is_admin_role:
        # 普通用户：仅能更新自己创建的日志
        if log.operator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限更新他人日志"
            )

    # 状态校验：待审批或已驳回状态的日志可更新（已通过的不可改）
    if log.status not in ("pending", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能更新待审批或已驳回状态的日志"
        )

    # 只允许更新description
    if "description" in log_data:
        log.description = log_data["description"]

    db.commit()
    db.refresh(log)

    return {
        "message": "日志更新成功",
        "log_id": log.id,
        "description": log.description
    }


@router.post("/{log_id}/approve", summary="审批日志")
async def approve_log(
    log_id: int,
    action: ApprovalAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审批日志（通过或驳回）"""
    # 检查权限
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可审批日志"
        )

    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )

    if log.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该日志已审批"
        )

    # 更新日志状态
    if action.approved:
        log.status = "approved"
        log.approved_at = datetime.utcnow()
        log.approver_id = current_user.id
    else:
        log.status = "rejected"
        log.rejection_reason = action.rejection_reason or "审批不通过"

    db.commit()
    db.refresh(log)

    return {
        "message": "审批成功",
        "log_id": log.id,
        "status": log.status
    }


@router.delete("/{log_id}", summary="删除日志")
async def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除日志（Q26: 仅管理员/超级管理员可删除）"""
    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )

    # 权限校验：仅管理员/超级管理员可删除日志，普通用户无权删除
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除日志，仅管理员可删除"
        )

    # 级联删除具体日志
    db.query(InstallationLog).filter(InstallationLog.id == log_id).delete()
    db.query(RepairLog).filter(RepairLog.id == log_id).delete()
    db.query(ScrapLog).filter(ScrapLog.id == log_id).delete()
    db.query(InspectionLog).filter(InspectionLog.id == log_id).delete()
    db.query(MaintenanceRecord).filter(MaintenanceRecord.id == log_id).delete()
    db.query(FaultReport).filter(FaultReport.id == log_id).delete()
    db.query(PartsReplacementLog).filter(PartsReplacementLog.id == log_id).delete()
    db.query(CalibrationLog).filter(CalibrationLog.id == log_id).delete()

    # 删除基础日志
    db.delete(log)
    db.commit()

    return {"message": "日志删除成功"}


@router.get("/types/list", summary="获取日志类型列表")
async def get_log_types():
    """获取所有日志类型"""
    return {
        "types": [
            {"value": "installation", "label": "设备安装"},
            {"value": "repair", "label": "设备维修"},
            {"value": "scrap", "label": "设备报废"},
            {"value": "inspection", "label": "日常巡检"},
            {"value": "maintenance", "label": "保养记录"},
            {"value": "fault", "label": "故障报修"},
            {"value": "parts", "label": "配件更换"},
            {"value": "calibration", "label": "校准记录"}
        ]
    }

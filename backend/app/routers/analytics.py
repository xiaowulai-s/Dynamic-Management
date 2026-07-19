from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.database import get_db
from app.models.logs import Log, RepairLog, MaintenanceRecord
from app.models.equipment import Equipment
from app.models.user import User
from app.utils.auth import get_current_user
from pydantic import BaseModel
import pandas as pd

router = APIRouter()


def parse_date_safe(date_str: str, field_name: str = "日期") -> datetime:
    """安全解析日期字符串"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的{field_name}格式：{date_str}，请使用 YYYY-MM-DD 格式"
        )


class AnalyticsResponse(BaseModel):
    """分析数据响应"""
    labels: List[str]
    data: List[int]
    total: int


class FaultRateResponse(BaseModel):
    """故障率统计响应"""
    labels: List[str]
    data: List[float]  # 百分比
    total_faults: int
    total_equipments: int


class MaintenanceCostResponse(BaseModel):
    """维修成本统计响应"""
    labels: List[str]
    data: List[float]
    total_cost: float
    average_cost: float


class EquipmentStatusResponse(BaseModel):
    """设备状态响应"""
    labels: List[str]
    data: List[int]
    total: int


@router.get("/fault-rate", response_model=FaultRateResponse, summary="设备故障率统计")
async def get_fault_rate(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    group_by: str = Query("month", description="分组方式：day/week/month"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设备故障率统计"""
    start = parse_date_safe(start_date, "开始日期")
    end = parse_date_safe(end_date, "结束日期") + timedelta(days=1)

    # 查询故障日志
    fault_logs = db.query(Log).filter(
        Log.log_type == "fault",
        Log.status == "approved",
        Log.created_at >= start,
        Log.created_at < end
    ).all()

    # 查询所有设备
    total_equipments = db.query(Equipment).count()

    # 按时间段分组
    fault_df = pd.DataFrame([{
        'date': log.created_at,
        'count': 1
    } for log in fault_logs])

    if len(fault_df) == 0:
        return FaultRateResponse(
            labels=[],
            data=[],
            total_faults=0,
            total_equipments=total_equipments
        )

    fault_df['date'] = pd.to_datetime(fault_df['date'])

    if group_by == "day":
        grouped = fault_df.groupby(fault_df['date'].dt.date)['count'].sum()
        labels = [d.strftime("%Y-%m-%d") for d in grouped.index]
    elif group_by == "week":
        fault_df['week'] = fault_df['date'].dt.to_period('W')
        grouped = fault_df.groupby('week')['count'].sum()
        labels = [str(w) for w in grouped.index]
    else:  # month
        grouped = fault_df.groupby(fault_df['date'].dt.to_period('M'))['count'].sum()
        labels = [str(m) for m in grouped.index]

    # 计算故障率（故障次数/设备总数）
    data = [(count / total_equipments * 100) if total_equipments > 0 else 0 for count in grouped.values]

    return FaultRateResponse(
        labels=labels,
        data=data,
        total_faults=len(fault_logs),
        total_equipments=total_equipments
    )


@router.get("/maintenance-cost", response_model=MaintenanceCostResponse, summary="维修成本统计")
async def get_maintenance_cost(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    group_by: str = Query("month", description="分组方式：day/week/month"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """维修成本统计"""
    start = parse_date_safe(start_date, "开始日期")
    end = parse_date_safe(end_date, "结束日期") + timedelta(days=1)

    # 查询维修日志
    repair_logs = db.query(RepairLog).join(Log).filter(
        Log.log_type == "repair",
        Log.status == "approved",
        Log.created_at >= start,
        Log.created_at < end,
        RepairLog.cost.isnot(None)
    ).all()

    if len(repair_logs) == 0:
        return MaintenanceCostResponse(
            labels=[],
            data=[],
            total_cost=0,
            average_cost=0
        )

    # 构建DataFrame
    repair_data = []
    for repair in repair_logs:
        log = db.query(Log).filter(Log.id == repair.id).first()
        repair_data.append({
            'date': log.created_at,
            'cost': repair.cost or 0
        })

    df = pd.DataFrame(repair_data)
    df['date'] = pd.to_datetime(df['date'])

    if group_by == "day":
        grouped = df.groupby(df['date'].dt.date)['cost'].sum()
        labels = [d.strftime("%Y-%m-%d") for d in grouped.index]
    elif group_by == "week":
        df['week'] = df['date'].dt.to_period('W')
        grouped = df.groupby('week')['cost'].sum()
        labels = [str(w) for w in grouped.index]
    else:  # month
        grouped = df.groupby(df['date'].dt.to_period('M'))['cost'].sum()
        labels = [str(m) for m in grouped.index]

    total_cost = sum(grouped.values)
    average_cost = total_cost / len(grouped) if len(grouped) > 0 else 0

    return MaintenanceCostResponse(
        labels=labels,
        data=grouped.values.tolist(),
        total_cost=round(total_cost, 2),
        average_cost=round(average_cost, 2)
    )


@router.get("/maintenance-schedule", summary="保养计划统计")
async def get_maintenance_schedule(
    days: int = Query(30, description="未来多少天"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保养计划统计（未来N天）"""
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days)

    # 查询即将到期的保养记录
    upcoming_maintenance = db.query(MaintenanceRecord).join(Log).filter(
        Log.status == "approved",
        MaintenanceRecord.next_maintenance_date >= now,
        MaintenanceRecord.next_maintenance_date <= end_date
    ).order_by(MaintenanceRecord.next_maintenance_date.asc()).all()

    result = []
    for maintenance in upcoming_maintenance:
        log = db.query(Log).filter(Log.id == maintenance.id).first()
        equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()

        result.append({
            "id": maintenance.id,
            "equipment_name": equipment.name if equipment else "未知",
            "equipment_code": equipment.code if equipment else "未知",
            "maintenance_date": log.created_at.isoformat(),
            "next_maintenance_date": maintenance.next_maintenance_date.isoformat() if maintenance.next_maintenance_date else None,
            "days_remaining": (maintenance.next_maintenance_date - now).days if maintenance.next_maintenance_date else None,
            "maintenance_items": maintenance.maintenance_items or []
        })

    return {
        "upcoming": result,
        "total": len(result)
    }


@router.get("/equipment-status", response_model=EquipmentStatusResponse, summary="设备状态统计")
async def get_equipment_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设备状态分布统计"""
    status_counts = db.query(
        Equipment.status,
        func.count(Equipment.id)
    ).group_by(Equipment.status).all()

    status_labels = {
        "running": "运行中",
        "stopped": "停机",
        "repairing": "维修中",
        "scrapped": "已报废"
    }

    labels = [status_labels.get(s[0], s[0]) for s in status_counts]
    data = [s[1] for s in status_counts]

    total = sum(data)

    return EquipmentStatusResponse(
        labels=labels,
        data=data,
        total=total
    )


@router.get("/log-type-stats", summary="日志类型统计")
async def get_log_type_stats(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """日志类型统计"""
    query = db.query(Log)

    # 日期筛选
    if start_date:
        start = parse_date_safe(start_date, "开始日期")
        query = query.filter(Log.created_at >= start)

    if end_date:
        end = parse_date_safe(end_date, "结束日期") + timedelta(days=1)
        query = query.filter(Log.created_at < end)

    # 按类型分组统计
    type_counts = query.with_entities(
        Log.log_type,
        func.count(Log.id).label('count')
    ).group_by(Log.log_type).all()

    type_labels = {
        "installation": "设备安装",
        "repair": "设备维修",
        "scrap": "设备报废",
        "inspection": "日常巡检",
        "maintenance": "保养记录",
        "fault": "故障报修",
        "parts": "配件更换",
        "calibration": "校准记录"
    }

    labels = [type_labels.get(t[0], t[0]) for t in type_counts]
    data = [t[1] for t in type_counts]

    return {
        "labels": labels,
        "data": data,
        "total": sum(data)
    }


@router.get("/repair-ranking", summary="设备维修频率排名")
async def get_repair_ranking(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设备维修频率排名"""
    # 统计每个设备的维修次数
    repair_counts = db.query(
        Log.equipment_id,
        func.count(Log.id).label('repair_count')
    ).filter(
        Log.log_type == "repair",
        Log.status == "approved"
    ).group_by(Log.equipment_id).order_by(
        func.count(Log.id).desc()
    ).limit(limit).all()

    result = []
    for equipment_id, repair_count in repair_counts:
        equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
        if equipment:
            # 查询总维修费用
            total_cost = db.query(func.sum(RepairLog.cost)).join(Log).filter(
                Log.equipment_id == equipment_id,
                Log.status == "approved",
                RepairLog.cost.isnot(None)
            ).scalar() or 0

            result.append({
                "equipment_id": equipment_id,
                "equipment_code": equipment.code,
                "equipment_name": equipment.name,
                "repair_count": repair_count,
                "total_cost": round(total_cost, 2)
            })

    return {
        "ranking": result,
        "total": len(result)
    }


@router.get("/cost-analysis", summary="维修成本分析")
async def get_cost_analysis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """维修成本分析（总费用、平均费用、最高单次费用）"""
    query = db.query(RepairLog).join(Log).filter(
        Log.log_type == "repair",
        Log.status == "approved",
        RepairLog.cost.isnot(None)
    )

    if start_date:
        start = parse_date_safe(start_date, "开始日期")
        query = query.filter(Log.created_at >= start)

    if end_date:
        end = parse_date_safe(end_date, "结束日期") + timedelta(days=1)
        query = query.filter(Log.created_at < end)

    repairs = query.all()

    if not repairs:
        return {
            "total_cost": 0,
            "average_cost": 0,
            "max_cost": 0,
            "min_cost": 0,
            "repair_count": 0
        }

    costs = [r.cost for r in repairs if r.cost]

    return {
        "total_cost": round(sum(costs), 2),
        "average_cost": round(sum(costs) / len(costs), 2) if costs else 0,
        "max_cost": round(max(costs), 2) if costs else 0,
        "min_cost": round(min(costs), 2) if costs else 0,
        "repair_count": len(repairs)
    }


@router.get("/parts-usage", summary="配件消耗统计")
async def get_parts_usage(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """配件消耗统计"""
    from app.models.logs import PartsReplacementLog

    query = db.query(PartsReplacementLog).join(Log).filter(
        Log.status == "approved"
    )

    if start_date:
        start = parse_date_safe(start_date, "开始日期")
        query = query.filter(Log.created_at >= start)

    if end_date:
        end = parse_date_safe(end_date, "结束日期") + timedelta(days=1)
        query = query.filter(Log.created_at < end)

    parts_logs = query.all()

    # 按配件名称分组统计
    parts_dict = {}
    for log in parts_logs:
        if log.parts_name not in parts_dict:
            parts_dict[log.parts_name] = {
                "parts_name": log.parts_name,
                "total_quantity": 0,
                "total_cost": 0,
                "usage_count": 0
            }

        parts_dict[log.parts_name]["total_quantity"] += log.quantity or 0
        parts_dict[log.parts_name]["total_cost"] += log.cost or 0
        parts_dict[log.parts_name]["usage_count"] += 1

    # 按使用量排序
    result = sorted(parts_dict.values(), key=lambda x: x["total_quantity"], reverse=True)

    return {
        "parts_usage": result,
        "total_parts_types": len(result)
    }

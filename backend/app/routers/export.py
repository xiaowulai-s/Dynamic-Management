from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta, timezone
import os
import uuid

from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment
from app.models.logs import Log, RepairLog, MaintenanceRecord, PartsReplacementLog
from app.utils.auth import get_current_user
from app.utils.export_utils import export_to_excel, export_to_pdf
from app.config import settings
from pydantic import BaseModel


router = APIRouter()


class ExportRequest(BaseModel):
    """导出请求基础模型"""
    format: str = "excel"  # excel/pdf


class FaultRateExportRequest(ExportRequest):
    """故障率统计导出请求"""
    start_date: str
    end_date: str
    group_by: Optional[str] = "month"


class MaintenanceCostExportRequest(ExportRequest):
    """维修成本统计导出请求"""
    start_date: str
    end_date: str
    group_by: Optional[str] = "month"


class MaintenanceScheduleExportRequest(ExportRequest):
    """保养计划导出请求"""
    days: int = 30


class PartsUsageExportRequest(ExportRequest):
    """配件消耗统计导出请求"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class RepairRankingExportRequest(ExportRequest):
    """维修频率排名导出请求"""
    limit: int = 10


class CostAnalysisExportRequest(ExportRequest):
    """成本分析导出请求"""
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/fault-rate", summary="导出故障率统计")
async def export_fault_rate(
    request: FaultRateExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出故障率统计报表"""
    try:
        # 查询数据
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # 按设备统计故障次数
        fault_data = db.query(
            Equipment.code,
            Equipment.name,
            func.count(Log.id).label('fault_count')
        ).join(Log).filter(
            Log.log_type == 'fault',
            Log.status == 'approved',
            Log.created_at >= start_date,
            Log.created_at <= end_date
        ).group_by(Equipment.id).order_by(func.count(Log.id).desc()).all()

        # 转换为DataFrame格式
        data = []
        for idx, row in enumerate(fault_data, 1):
            data.append({
                '排名': idx,
                '设备编号': row.code,
                '设备名称': row.name,
                '故障次数': row.fault_count
            })

        # 生成文件
        filename = f"故障率统计_{request.start_date}_to_{request.end_date}"
        file_path = export_to_excel(data, filename, "故障率统计") if request.format == "excel" else export_to_pdf(data, filename, "故障率统计报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/maintenance-cost", summary="导出维修成本分析")
async def export_maintenance_cost(
    request: MaintenanceCostExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出维修成本分析报表"""
    try:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        # 按月份统计维修成本
        cost_data = db.query(
            extract('year', Log.created_at).label('year'),
            extract('month', Log.created_at).label('month'),
            func.sum(RepairLog.cost).label('total_cost'),
            func.count(Log.id).label('repair_count')
        ).join(RepairLog).filter(
            Log.log_type == 'repair',
            Log.status == 'approved',
            Log.created_at >= start_date,
            Log.created_at <= end_date
        ).group_by('year', 'month').order_by('year', 'month').all()

        data = []
        for row in cost_data:
            data.append({
                '年份': int(row.year),
                '月份': int(row.month),
                '维修次数': row.repair_count,
                '维修成本(元)': float(row.total_cost or 0)
            })

        filename = f"维修成本分析_{request.start_date}_to_{request.end_date}"
        file_path = export_to_excel(data, filename, "维修成本分析") if request.format == "excel" else export_to_pdf(data, filename, "维修成本分析报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/maintenance-schedule", summary="导出保养计划")
async def export_maintenance_schedule(
    request: MaintenanceScheduleExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出保养计划报表"""
    try:
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=request.days)

        # 查询即将到期的保养计划
        schedule_data = db.query(
            Equipment.code,
            Equipment.name,
            Equipment.location,
            MaintenanceRecord.maintenance_date,
            MaintenanceRecord.next_maintenance_date,
            MaintenanceRecord.maintenance_items
        ).join(Log).filter(
            Log.log_type == 'maintenance',
            Log.status == 'approved',
            MaintenanceRecord.next_maintenance_date >= now,
            MaintenanceRecord.next_maintenance_date <= end_date
        ).order_by(MaintenanceRecord.next_maintenance_date.asc()).all()

        data = []
        for row in schedule_data:
            days_remaining = (row.next_maintenance_date - now).days
            items = row.maintenance_items if isinstance(row.maintenance_items, list) else []
            data.append({
                '设备编号': row.code,
                '设备名称': row.name,
                '安装位置': row.location,
                '上次保养日期': row.maintenance_date.strftime('%Y-%m-%d') if row.maintenance_date else '',
                '下次保养日期': row.next_maintenance_date.strftime('%Y-%m-%d'),
                '剩余天数': days_remaining,
                '保养项目': ', '.join(items) if items else '常规保养'
            })

        filename = f"保养计划_未来{request.days}天"
        file_path = export_to_excel(data, filename, "保养计划") if request.format == "excel" else export_to_pdf(data, filename, "保养计划报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/parts-usage", summary="导出配件消耗统计")
async def export_parts_usage(
    request: PartsUsageExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出配件消耗统计报表"""
    try:
        query = db.query(
            PartsReplacementLog.parts_name,
            PartsReplacementLog.parts_code,
            func.sum(PartsReplacementLog.quantity).label('total_quantity'),
            func.sum(PartsReplacementLog.cost).label('total_cost'),
            func.count(Log.id).label('usage_count')
        ).join(Log).filter(
            Log.log_type == 'parts',
            Log.status == 'approved'
        )

        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(Log.created_at >= start_date)

        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(Log.created_at <= end_date)

        parts_data = query.group_by(
            PartsReplacementLog.parts_name,
            PartsReplacementLog.parts_code
        ).order_by(func.sum(PartsReplacementLog.quantity).desc()).all()

        data = []
        for idx, row in enumerate(parts_data, 1):
            data.append({
                '排名': idx,
                '配件名称': row.parts_name,
                '配件编码': row.parts_code,
                '使用次数': row.usage_count,
                '总消耗数量': row.total_quantity,
                '总成本(元)': float(row.total_cost or 0)
            })

        date_range = ""
        if request.start_date and request.end_date:
            date_range = f"_{request.start_date}_to_{request.end_date}"
        elif request.start_date:
            date_range = f"_{request.start_date}_至今"
        else:
            date_range = f"_全部"

        filename = f"配件消耗统计{date_range}"
        file_path = export_to_excel(data, filename, "配件消耗统计") if request.format == "excel" else export_to_pdf(data, filename, "配件消耗统计报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/repair-ranking", summary="导出维修频率排名")
async def export_repair_ranking(
    request: RepairRankingExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出维修频率排名报表"""
    try:
        # 查询维修次数排名
        ranking_data = db.query(
            Equipment.code,
            Equipment.name,
            Equipment.model,
            Equipment.location,
            func.count(Log.id).label('repair_count'),
            func.sum(RepairLog.cost).label('total_cost'),
            func.avg(RepairLog.repair_time).label('avg_repair_time')
        ).join(RepairLog).join(Log).filter(
            Log.log_type == 'repair',
            Log.status == 'approved'
        ).group_by(Equipment.id).order_by(func.count(Log.id).desc()).limit(request.limit).all()

        data = []
        for idx, row in enumerate(ranking_data, 1):
            data.append({
                '排名': idx,
                '设备编号': row.code,
                '设备名称': row.name,
                '型号': row.model or '-',
                '安装位置': row.location or '-',
                '维修次数': row.repair_count,
                '总维修成本(元)': float(row.total_cost or 0),
                '平均维修时间(小时)': round(float(row.avg_repair_time or 0), 1)
            })

        filename = f"维修频率排名_Top{request.limit}"
        file_path = export_to_excel(data, filename, "维修频率排名") if request.format == "excel" else export_to_pdf(data, filename, "维修频率排名报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/cost-analysis", summary="导出成本分析")
async def export_cost_analysis(
    request: CostAnalysisExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出成本分析报表"""
    try:
        query = db.query(
            Equipment.code,
            Equipment.name,
            func.count(Log.id).label('repair_count'),
            func.sum(RepairLog.cost).label('repair_cost'),
            func.sum(PartsReplacementLog.cost).label('parts_cost')
        ).outerjoin(RepairLog).outerjoin(PartsReplacementLog).filter(
            Log.log_type.in_(['repair', 'parts']),
            Log.status == 'approved'
        )

        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(Log.created_at >= start_date)

        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(Log.created_at <= end_date)

        cost_data = query.group_by(Equipment.id).order_by(
            (func.sum(RepairLog.cost) + func.sum(PartsReplacementLog.cost)).desc()
        ).all()

        data = []
        for idx, row in enumerate(cost_data, 1):
            total_cost = float((row.repair_cost or 0) + (row.parts_cost or 0))
            data.append({
                '排名': idx,
                '设备编号': row.code,
                '设备名称': row.name,
                '维修次数': row.repair_count,
                '维修成本(元)': float(row.repair_cost or 0),
                '配件成本(元)': float(row.parts_cost or 0),
                '总成本(元)': total_cost
            })

        date_range = ""
        if request.start_date and request.end_date:
            date_range = f"_{request.start_date}_to_{request.end_date}"
        elif request.start_date:
            date_range = f"_{request.start_date}_至今"
        else:
            date_range = "_全部"

        filename = f"成本分析{date_range}"
        file_path = export_to_excel(data, filename, "成本分析") if request.format == "excel" else export_to_pdf(data, filename, "成本分析报表")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}"
        )

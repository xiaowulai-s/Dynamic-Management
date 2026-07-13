from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.logs import MaintenanceRecord, CalibrationLog, Log
from app.models.equipment import Equipment
from app.models.approval import SystemConfig
from app.models.notification import Notification
from app.routers.notifications import create_notification_sync
from app.config import settings
import json


@shared_task(name="reminder_tasks.check_maintenance_reminder")
def check_maintenance_reminder():
    """
    检查需要保养提醒的设备
    每天凌晨2点执行
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # 获取保养周期配置
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "maintenance_cycle"
        ).first()

        if not config:
            return {"message": "未找到保养周期配置"}

        maintenance_cycle_config = config.config_value
        default_cycle = maintenance_cycle_config.get("default", 30)

        # 查询即将到期的保养记录
        upcoming_maintenance = db.query(MaintenanceRecord).join(Log).filter(
            Log.status == "approved",
            MaintenanceRecord.next_maintenance_date >= now,
            MaintenanceRecord.next_maintenance_date <= now + timedelta(days=7)  # 未来7天内
        ).all()

        reminders = []
        for maintenance in upcoming_maintenance:
            log = db.query(Log).filter(Log.id == maintenance.id).first()
            equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()

            if equipment:
                days_remaining = (maintenance.next_maintenance_date - now).days

                reminders.append({
                    "equipment_id": equipment.id,
                    "equipment_code": equipment.code,
                    "equipment_name": equipment.name,
                    "next_maintenance_date": maintenance.next_maintenance_date.isoformat(),
                    "days_remaining": days_remaining,
                    "maintenance_items": maintenance.maintenance_items or []
                })

                # 发送通知（同步调用）
                try:
                    create_notification_sync(
                        user_id=log.operator_id,
                        title=f"设备保养提醒：{equipment.name}",
                        content=f"设备 {equipment.name}（编号：{equipment.code}）将在 {days_remaining} 天后需要保养。\n下次保养日期：{maintenance.next_maintenance_date.strftime('%Y-%m-%d')}\n保养项目：{', '.join(maintenance.maintenance_items) if maintenance.maintenance_items else '常规保养'}",
                        db=db,
                        type="maintenance",
                        equipment_id=equipment.id
                    )
                except Exception as e:
                    print(f"发送保养提醒通知失败: {str(e)}")

        return {
            "check_time": now.isoformat(),
            "reminders": reminders,
            "total": len(reminders)
        }

    finally:
        db.close()


@shared_task(name="reminder_tasks.check_equipment_life")
def check_equipment_life():
    """
    检查设备寿命到期预警
    每天凌晨3点执行
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # 获取设备寿命配置
        config = db.query(SystemConfig).filter(
            SystemConfig.config_key == "equipment_life"
        ).first()

        if not config:
            return {"message": "未找到设备寿命配置"}

        life_config = config.config_value
        default_life = life_config.get("default", 10)

        # 查询所有运行中的设备
        equipments = db.query(Equipment).filter(
            Equipment.status == "running",
            Equipment.lifecycle_status == "active"
        ).all()

        warnings = []
        for equipment in equipments:
            # 计算设备使用年限
            if equipment.created_at:
                used_years = (now - equipment.created_at).days / 365.25

                # 计算寿命百分比
                life_percentage = (used_years / default_life) * 100

                # 如果超过80%寿命，发送预警
                if life_percentage >= 80:
                    warning_level = "yellow"  # 黄色预警
                    if life_percentage >= 90:
                        warning_level = "red"  # 红色预警

                    warnings.append({
                        "equipment_id": equipment.id,
                        "equipment_code": equipment.code,
                        "equipment_name": equipment.name,
                        "used_years": round(used_years, 1),
                        "design_life": default_life,
                        "life_percentage": round(life_percentage, 1),
                        "warning_level": warning_level
                    })

                    # 发送预警通知
                    warning_text = {
                        "yellow": "黄色预警",
                        "red": "红色预警"
                    }.get(warning_level, "预警")

                    # 发送预警通知（同步调用）
                    try:
                        create_notification_sync(
                            user_id=equipment.created_by,
                            title=f"设备寿命{warning_text}：{equipment.name}",
                            content=f"设备 {equipment.name}（编号：{equipment.code}）\n已使用年限：{round(used_years, 1)} 年\n设计寿命：{default_life} 年\n寿命使用率：{round(life_percentage, 1)}%\n当前状态：{warning_text}\n建议尽快安排设备检查和更换计划。",
                            db=db,
                            type="lifecycle",
                            equipment_id=equipment.id
                        )
                    except Exception as e:
                        print(f"发送寿命预警通知失败: {str(e)}")

        return {
            "check_time": now.isoformat(),
            "warnings": warnings,
            "total": len(warnings)
        }

    finally:
        db.close()


@shared_task(name="reminder_tasks.check_calibration_reminder")
def check_calibration_reminder():
    """
    检查校准到期提醒
    每天凌晨4点执行
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # 查询即将到期的校准记录
        upcoming_calibrations = db.query(CalibrationLog).join(Log).filter(
            Log.status == "approved",
            CalibrationLog.next_calibration_date >= now,
            CalibrationLog.next_calibration_date <= now + timedelta(days=30)  # 未来30天内
        ).order_by(CalibrationLog.next_calibration_date.asc()).all()

        reminders = []
        for calibration in upcoming_calibrations:
            log = db.query(Log).filter(Log.id == calibration.id).first()
            equipment = db.query(Equipment).filter(Equipment.id == log.equipment_id).first()

            if equipment:
                days_remaining = (calibration.next_calibration_date - now).days

                reminders.append({
                    "equipment_id": equipment.id,
                    "equipment_code": equipment.code,
                    "equipment_name": equipment.name,
                    "next_calibration_date": calibration.next_calibration_date.isoformat(),
                    "days_remaining": days_remaining,
                    "calibration_org": calibration.calibration_org
                })

                # 发送通知（同步调用）
                try:
                    create_notification_sync(
                        user_id=log.operator_id,
                        title=f"校准到期提醒：{equipment.name}",
                        content=f"设备 {equipment.name}（编号：{equipment.code}）将在 {days_remaining} 天后需要校准。\n下次校准日期：{calibration.next_calibration_date.strftime('%Y-%m-%d')}\n校准机构：{calibration.calibration_org or '待定'}",
                        db=db,
                        type="calibration",
                        equipment_id=equipment.id
                    )
                except Exception as e:
                    print(f"发送校准提醒通知失败: {str(e)}")

        return {
            "check_time": now.isoformat(),
            "reminders": reminders,
            "total": len(reminders)
        }

    finally:
        db.close()


@shared_task(name="reminder_tasks.cleanup_temp_files")
def cleanup_temp_files():
    """
    清理临时文件
    每天凌晨1点执行
    """
    import os
    import glob

    try:
        temp_dir = settings.UPLOAD_DIR + "/temp"
        if not os.path.exists(temp_dir):
            return {"message": "临时目录不存在"}

        # 查找7天前的临时文件
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0

        for file_path in glob.glob(os.path.join(temp_dir, "*")):
            file_stat = os.stat(file_path)
            file_mtime = datetime.fromtimestamp(file_stat.st_mtime)

            if file_mtime < cutoff_date:
                os.remove(file_path)
                deleted_count += 1

        return {
            "cleanup_time": datetime.utcnow().isoformat(),
            "deleted_count": deleted_count
        }

    except Exception as e:
        return {
            "error": str(e)
        }

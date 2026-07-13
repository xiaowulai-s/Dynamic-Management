from celery import Celery
from celery.schedules import crontab
from app.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.ocr_tasks", "app.tasks.reminder_tasks"]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=29 * 60,  # 软超时
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天凌晨2点检查保养提醒
    "check-maintenance-reminder": {
        "task": "app.tasks.reminder_tasks.check_maintenance_reminder",
        "schedule": crontab(hour=2, minute=0),
    },
    # 每天凌晨3点检查设备寿命预警
    "check-equipment-life": {
        "task": "app.tasks.reminder_tasks.check_equipment_life",
        "schedule": crontab(hour=3, minute=0),
    },
    # 每天凌晨4点检查校准到期提醒
    "check-calibration-reminder": {
        "task": "app.tasks.reminder_tasks.check_calibration_reminder",
        "schedule": crontab(hour=4, minute=0),
    },
    # 每天凌晨1点清理临时文件
    "cleanup-temp-files": {
        "task": "app.tasks.reminder_tasks.cleanup_temp_files",
        "schedule": crontab(hour=1, minute=0),
    },
}

if __name__ == "__main__":
    celery_app.start()

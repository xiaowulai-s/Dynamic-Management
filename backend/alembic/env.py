"""Alembic 迁移环境配置。

从 app.database 导入 Base，从 app.config 导入 settings，
并将 sqlalchemy.url 动态设置为 settings.DATABASE_URL。
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 项目配置与基类
from app.config import settings
from app.database import Base

# 显式导入所有模型，确保它们注册到 Base.metadata 以支持 autogenerate
# noqa: F401  -- 仅为注册 metadata
from app.models import (  # noqa: F401
    User,
    Equipment,
    Log,
    InstallationLog,
    RepairLog,
    ScrapLog,
    InspectionLog,
    MaintenanceRecord,
    FaultReport,
    PartsReplacementLog,
    CalibrationLog,
    ApprovalConfig,
    SystemConfig,
    AuditLog,
)
from app.models.customer import Customer  # noqa: F401
from app.models.feedback import Feedback  # noqa: F401
from app.models.notification import Notification  # noqa: F401

# Alembic 配置对象
config = context.config

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 动态设置 sqlalchemy.url（覆盖 alembic.ini 中的空值）
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 目标 metadata，用于 autogenerate 比较
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以 'offline' 模式运行迁移。

    仅生成 SQL 脚本而不实际连接数据库。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以 'online' 模式运行迁移。

    创建数据库连接并执行迁移。
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

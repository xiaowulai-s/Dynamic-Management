"""add customer_name, indexes, relationships and numeric types

Revision ID: a3f7c2e1d9b6
Revises:
Create Date: 2026-07-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3f7c2e1d9b6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. equipment 表：新增 customer_name 字段（VARCHAR(200)，带索引） ---
    op.add_column(
        "equipment",
        sa.Column(
            "customer_name",
            sa.String(length=200),
            nullable=True,
            comment="客户名称",
        ),
    )
    op.create_index(
        "ix_equipment_customer_name", "equipment", ["customer_name"], unique=False
    )

    # --- 2. equipment 表：为 lifecycle_status 字段添加索引 ---
    op.create_index(
        "ix_equipment_lifecycle_status",
        "equipment",
        ["lifecycle_status"],
        unique=False,
    )

    # --- 3. maintenance_records 表：为 next_maintenance_date 字段添加索引 ---
    op.create_index(
        "ix_maintenance_records_next_maintenance_date",
        "maintenance_records",
        ["next_maintenance_date"],
        unique=False,
    )

    # --- 4. calibration_logs 表：为 next_calibration_date 字段添加索引 ---
    op.create_index(
        "ix_calibration_logs_next_calibration_date",
        "calibration_logs",
        ["next_calibration_date"],
        unique=False,
    )

    # --- 5. feedbacks 表：为 user_id 字段添加索引 ---
    op.create_index(
        "ix_feedbacks_user_id", "feedbacks", ["user_id"], unique=False
    )

    # --- 6. 将 cost 字段从 Integer 改为 Numeric(10, 2) ---
    # repair_logs.cost
    op.alter_column(
        "repair_logs",
        "cost",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=True,
        existing_comment="维修费用（元）",
    )
    # parts_replacement_logs.cost
    op.alter_column(
        "parts_replacement_logs",
        "cost",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=True,
        existing_comment="费用（元）",
    )

    # --- 7. 将 scrap_logs.residual_value 字段从 Integer 改为 Numeric(10, 2) ---
    op.alter_column(
        "scrap_logs",
        "residual_value",
        existing_type=sa.Integer(),
        type_=sa.Numeric(precision=10, scale=2),
        existing_nullable=True,
        existing_comment="残值（元）",
    )


def downgrade() -> None:
    # --- 反向：将 Numeric(10, 2) 改回 Integer ---
    # scrap_logs.residual_value
    op.alter_column(
        "scrap_logs",
        "residual_value",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Integer(),
        existing_nullable=True,
        existing_comment="残值（元）",
    )

    # cost 字段改回 Integer
    # parts_replacement_logs.cost
    op.alter_column(
        "parts_replacement_logs",
        "cost",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Integer(),
        existing_nullable=True,
        existing_comment="费用（元）",
    )
    # repair_logs.cost
    op.alter_column(
        "repair_logs",
        "cost",
        existing_type=sa.Numeric(precision=10, scale=2),
        type_=sa.Integer(),
        existing_nullable=True,
        existing_comment="维修费用（元）",
    )

    # --- 删除索引 ---
    op.drop_index("ix_feedbacks_user_id", table_name="feedbacks")
    op.drop_index(
        "ix_calibration_logs_next_calibration_date", table_name="calibration_logs"
    )
    op.drop_index(
        "ix_maintenance_records_next_maintenance_date",
        table_name="maintenance_records",
    )
    op.drop_index("ix_equipment_lifecycle_status", table_name="equipment")
    op.drop_index("ix_equipment_customer_name", table_name="equipment")

    # --- 删除 customer_name 字段 ---
    op.drop_column("equipment", "customer_name")

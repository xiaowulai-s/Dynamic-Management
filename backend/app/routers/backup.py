from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.equipment import Equipment
from app.models.logs import Log as LogModel
from app.models.customer import Customer
from app.utils.auth import require_admin
import json, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/export-all", summary="导出全量数据")
def export_all(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """全量数据备份导出（P9: 流式输出；Q5: 移除不存在的 nickname 字段）"""

    def generate():
        yield '{"exported_at":"' + datetime.now(timezone.utc).isoformat() + '","data":{'

        # 设备（分批）
        yield '"equipment":['
        first = True
        for e in db.query(Equipment).yield_per(100):
            if not first:
                yield ','
            yield json.dumps({c.name: str(getattr(e, c.name)) for c in e.__table__.columns}, ensure_ascii=False)
            first = False
        yield '],'

        # 日志（分批）
        yield '"logs":['
        first = True
        for l in db.query(LogModel).yield_per(100):
            if not first:
                yield ','
            yield json.dumps({c.name: str(getattr(l, c.name)) for c in l.__table__.columns}, ensure_ascii=False)
            first = False
        yield '],'

        # 客户（分批）
        yield '"customers":['
        first = True
        for c in db.query(Customer).yield_per(100):
            if not first:
                yield ','
            yield json.dumps({col.name: str(getattr(c, col.name)) for col in c.__table__.columns}, ensure_ascii=False)
            first = False
        yield '],'

        # 用户（不含密码哈希）
        yield '"users":['
        first = True
        for u in db.query(User).yield_per(100):
            if not first:
                yield ','
            yield json.dumps({
                "id": u.id, "username": u.username, "role": u.role,
                "is_active": u.is_active, "created_at": str(u.created_at)
            }, ensure_ascii=False)
            first = False
        yield ']}'

        yield '}'

    return StreamingResponse(
        generate(),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=backup.json"}
    )

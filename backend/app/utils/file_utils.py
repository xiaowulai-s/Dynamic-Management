import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from app.config import settings


def validate_upload_path(file_path: Path) -> bool:
    """验证文件路径是否在允许的目录内（防止路径穿越攻击）"""
    try:
        upload_dir = Path(settings.UPLOAD_DIR).resolve()
        requested_path = file_path.resolve()
        # 确保解析后的路径在上传目录内
        return str(requested_path).startswith(str(upload_dir))
    except Exception:
        return False


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4().hex}{ext}"


def save_uploaded_file(file_content: bytes, original_filename: str, sub_dir: str = "") -> str:
    """保存上传的文件"""
    # 创建子目录
    upload_dir = Path(settings.UPLOAD_DIR)
    if sub_dir:
        upload_dir = upload_dir / sub_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    unique_filename = generate_unique_filename(original_filename)
    file_path = upload_dir / unique_filename

    # 验证路径安全性（防止路径穿越）
    if not validate_upload_path(file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件路径"
        )

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 返回相对路径
    relative_path = str(file_path.relative_to(Path(settings.UPLOAD_DIR)))
    return relative_path


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        full_path = Path(settings.UPLOAD_DIR) / file_path
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def get_file_path(file_path: str) -> Path:
    """获取文件的完整路径"""
    return Path(settings.UPLOAD_DIR) / file_path


def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    try:
        full_path = Path(settings.UPLOAD_DIR) / file_path
        return full_path.stat().st_size
    except:
        return 0


def validate_file_extension(filename: str) -> bool:
    """验证文件扩展名"""
    ext = Path(filename).suffix.lower()
    return ext in settings.ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """验证文件大小"""
    return file_size <= settings.MAX_UPLOAD_SIZE

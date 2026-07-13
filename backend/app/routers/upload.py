from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
import asyncio

from app.database import get_db
from app.models.user import User
from app.models.logs import Log
from app.utils.auth import get_current_user
from app.utils.file_utils import save_uploaded_file, delete_file, validate_file_extension, validate_file_size
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    file_path: str
    file_name: str
    file_size: int
    message: str


class OcrRequest(BaseModel):
    """OCR识别请求"""
    file_path: str
    file_name: str


class OcrResponse(BaseModel):
    """OCR识别响应"""
    task_id: str
    status: str


class OcrStatusResponse(BaseModel):
    """OCR识别状态响应"""
    task_id: str
    status: str  # processing/completed/failed
    progress: Optional[int] = 0
    data: Optional[dict] = None
    message: Optional[str] = None


@router.post("/single", response_model=FileUploadResponse, summary="上传单个文件")
async def upload_single_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传单个文件"""
    try:
        # 验证文件类型
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式。支持的格式：{', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # 读取文件内容
        contents = await file.read()

        # 验证文件大小
        if not validate_file_size(len(contents)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超出限制（最大 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB）"
            )

        # 保存文件
        file_path = save_uploaded_file(contents, file.filename, sub_dir="logs")

        return FileUploadResponse(
            success=True,
            file_path=file_path,
            file_name=file.filename,
            file_size=len(contents),
            message="文件上传成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败：{str(e)}"
        )


@router.post("/batch", response_model=List[FileUploadResponse], summary="批量上传文件")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """批量上传文件（最多20个）"""
    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多上传20个文件"
        )

    results = []
    for file in files:
        try:
            # 验证文件类型
            if not validate_file_extension(file.filename):
                results.append(FileUploadResponse(
                    success=False,
                    file_path="",
                    file_name=file.filename or "",
                    file_size=0,
                    message=f"不支持的文件格式：{file.filename}"
                ))
                continue

            # 读取文件内容
            contents = await file.read()

            # 验证文件大小
            if not validate_file_size(len(contents)):
                results.append(FileUploadResponse(
                    success=False,
                    file_path="",
                    file_name=file.filename or "",
                    file_size=len(contents),
                    message=f"文件大小超出限制：{file.filename}"
                ))
                continue

            # 保存文件
            file_path = save_uploaded_file(contents, file.filename, sub_dir="logs")

            results.append(FileUploadResponse(
                success=True,
                file_path=file_path,
                file_name=file.filename or "",
                file_size=len(contents),
                message="上传成功"
            ))

        except Exception as e:
            results.append(FileUploadResponse(
                success=False,
                file_path="",
                file_name=file.filename or "",
                file_size=0,
                message=f"上传失败：{str(e)}"
            ))

    return results


@router.get("/download/{file_path:path}", summary="下载文件")
async def download_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """下载文件"""
    try:
        full_path = os.path.join(settings.UPLOAD_DIR, file_path)

        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )

        filename = os.path.basename(file_path)
        return FileResponse(
            path=full_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败：{str(e)}"
        )


@router.delete("/{file_path:path}", summary="删除文件")
async def delete_uploaded_file(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """删除上传的文件"""
    try:
        success = delete_file(file_path)
        if success:
            return {"message": "文件删除成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败：{str(e)}"
        )


# OCR任务存储（生产环境应该使用Redis）
ocr_tasks: dict = {}


@router.post("/ocr", response_model=OcrResponse, summary="触发OCR识别")
async def trigger_ocr(
    request: OcrRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """触发OCR识别任务"""
    task_id = str(uuid.uuid4())

    # 初始化任务状态
    ocr_tasks[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0,
        "data": None,
        "message": "正在识别..."
    }

    # 异步执行OCR识别（模拟）
    asyncio.create_task(process_ocr_task(task_id, request.file_path, request.file_name, db))

    return OcrResponse(task_id=task_id, status="processing")


@router.get("/ocr-status/{task_id}", response_model=OcrStatusResponse, summary="查询OCR识别状态")
async def get_ocr_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """查询OCR识别任务状态"""
    if task_id not in ocr_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )

    task = ocr_tasks[task_id]
    return OcrStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        data=task["data"],
        message=task["message"]
    )


async def process_ocr_task(task_id: str, file_path: str, file_name: str, db: Session):
    """
    处理OCR识别任务（模拟实现）
    实际项目中应该集成PaddleOCR或其他OCR引擎
    """
    try:
        # 模拟OCR识别过程
        await asyncio.sleep(2)  # 模拟处理时间
        ocr_tasks[task_id]["progress"] = 30

        await asyncio.sleep(2)
        ocr_tasks[task_id]["progress"] = 60

        await asyncio.sleep(2)
        ocr_tasks[task_id]["progress"] = 90

        # TODO: 实际集成OCR引擎
        # 这里返回模拟的识别结果
        # 实际应该根据文件内容调用OCR服务
        ocr_result = simulate_ocr_result(file_path, file_name, db)

        ocr_tasks[task_id]["status"] = "completed"
        ocr_tasks[task_id]["progress"] = 100
        ocr_tasks[task_id]["data"] = ocr_result

    except Exception as e:
        ocr_tasks[task_id]["status"] = "failed"
        ocr_tasks[task_id]["message"] = str(e)


def simulate_ocr_result(file_path: str, file_name: str, db: Session) -> dict:
    """
    模拟OCR识别结果
    实际项目中应该调用真实的OCR引擎
    """
    # 从文件名推断信息（模拟识别）
    file_ext = file_name.split('.')[-1].lower()

    # 模拟识别结果
    result = {
        "equipment_code": "",
        "equipment_name": "",
        "log_type": "maintenance",
        "confidence": 0.75,
        "raw_text": "模拟OCR识别结果"
    }

    # 尝试从文件名提取信息
    if "安装" in file_name or "installation" in file_name.lower():
        result["log_type"] = "installation"
        result["confidence"] = 0.8
    elif "维修" in file_name or "repair" in file_name.lower():
        result["log_type"] = "repair"
        result["confidence"] = 0.8
    elif "报废" in file_name or "scrap" in file_name.lower():
        result["log_type"] = "scrap"
        result["confidence"] = 0.8
    elif "巡检" in file_name or "inspection" in file_name.lower():
        result["log_type"] = "inspection"
        result["confidence"] = 0.8
    elif "保养" in file_name or "maintenance" in file_name.lower():
        result["log_type"] = "maintenance"
        result["confidence"] = 0.85
    elif "故障" in file_name or "fault" in file_name.lower():
        result["log_type"] = "fault"
        result["confidence"] = 0.8
    elif "配件" in file_name or "parts" in file_name.lower():
        result["log_type"] = "parts"
        result["confidence"] = 0.8
    elif "校准" in file_name or "calibration" in file_name.lower():
        result["log_type"] = "calibration"
        result["confidence"] = 0.8

    return result

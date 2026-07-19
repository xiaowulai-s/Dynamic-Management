from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

_DEFAULT_SECRET_PLACEHOLDER = "your-secret-key-change-this-in-production"


class Settings(BaseSettings):
    """应用配置类"""

    # 应用配置
    APP_NAME: str = "设备信息动态管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # S6: 默认关闭，仅显式环境变量开启

    # 数据库配置（S5: 不再提供带明文密码的默认值，强制从环境变量读取）
    DATABASE_URL: str = ""

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT配置（S4: 默认占位符，启动时校验）
    SECRET_KEY: str = _DEFAULT_SECRET_PLACEHOLDER
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".jpg", ".jpeg", ".png"]

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # OCR配置
    OCR_LANGUAGE: str = "ch"  # ch:中文, en:英文

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    class Config:
        env_file = ".env"
        extra = "ignore"  # 允许 .env 中有未定义的字段
        case_sensitive = True

    @validator('ALLOWED_EXTENSIONS', pre=True)
    @classmethod
    def parse_allowed_extensions(cls, v):
        """支持逗号分隔的字符串或JSON数组格式"""
        if isinstance(v, str):
            # 如果是逗号分隔的字符串，转换为列表
            if ',' in v:
                return [ext.strip() for ext in v.split(',')]
            # 如果是JSON数组字符串
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    @validator('CORS_ORIGINS', pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        """支持逗号分隔的字符串或JSON数组格式"""
        if isinstance(v, str):
            # 如果是逗号分隔的字符串，转换为列表
            if ',' in v:
                return [origin.strip() for origin in v.split(',')]
            # 如果是JSON数组字符串
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    def get_cors_origins(self) -> List[str]:
        """获取CORS origins，支持从环境变量JSON字符串解析"""
        import os
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            try:
                return json.loads(cors_origins_env)
            except json.JSONDecodeError:  # Q12: 明确异常类型
                logger.warning("CORS_ORIGINS 环境变量 JSON 解析失败，使用默认值")
                return self.CORS_ORIGINS
        return self.CORS_ORIGINS

    def validate_security(self) -> None:
        """启动时校验关键安全配置（S4/S5）"""
        if self.SECRET_KEY == _DEFAULT_SECRET_PLACEHOLDER:
            raise RuntimeError(
                "SECRET_KEY 仍为默认占位符，请通过环境变量或 .env 文件设置一个安全的随机密钥。"
                "可使用 python -c \"import secrets; print(secrets.token_hex(32))\" 生成。"
            )
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL 未配置，请通过环境变量或 .env 文件设置数据库连接字符串。")


# 全局配置实例
settings = Settings()
# 启动时校验安全配置
settings.validate_security()

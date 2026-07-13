# 设备信息动态管理系统

基于FastAPI + Vue 3的工业机械设备全生命周期管理系统

## 🎯 项目状态

**当前版本**: v1.0-beta  
**更新日期**: 2026-07-13  
**系统状态**: ✅ 核心功能已完成，已修复14/33个bug（42.4%）

### 最新进展

- ✅ **已完成**: 9个P0崩溃级Bug修复（2026-07-13）
- ✅ **已完成**: 5个P1高风险Bug修复（2026-07-13）
- ✅ **已完成**: UI/UX全面重构（2026-07-13）
- ✅ **已完成**: 深色模式支持
- ✅ **已完成**: 新增3个缺失路由（个人资料、日志详情、通知中心）
- ⏳ **待完成**: 11个P2中风险Bug（预计9.5小时）
- ⏳ **待完成**: 8个P3低风险Bug（预计8.5小时）

详细修复记录请查看 [BUGFIX_LOG.md](BUGFIX_LOG.md)  
完整开发进度请查看 [DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md)

## 功能特性

### 核心功能
- **设备管理**：设备档案管理、分类、状态跟踪
- **全链路日志**：安装、维修、报废、巡检、保养、报修、配件更换、校准8类日志
- **灵活审批**：管理员可配置哪些日志类型需要审批
- **文件OCR识别**：支持Word/PDF/图片批量上传和智能识别
- **统计分析**：故障率、维修成本、保养计划等多维度报表
- **智能预警**：定期保养提醒、设备寿命到期预警、校准到期提醒
- **多人协作**：20人同时在线，实时数据同步
- **移动端支持**：响应式设计，支持PC和手机访问

### 技术栈
- **后端**：FastAPI + SQLAlchemy + PostgreSQL + Celery + Redis
- **前端**：Vue 3 + TypeScript + Element Plus + ECharts
- **OCR**：PaddleOCR（中文识别）
- **部署**：Docker Compose一键部署

## 快速开始

### 环境要求
- Docker & Docker Compose
- Python 3.10+（本地开发）
- Node.js 18+（本地开发）

### 使用Docker部署（推荐）

1. 进入项目目录
```bash
cd equipment-management
```

2. 复制环境配置文件
```bash
cp backend/.env.example backend/.env
```

3. 编辑 `backend/.env` 文件，修改数据库密码等配置

4. 启动所有服务
```bash
docker-compose up -d
```

5. 查看服务状态
```bash
docker-compose ps
```

6. 访问系统
- 前端：http://localhost:5173（开发模式）或 http://localhost（生产模式）
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 本地开发

#### 后端开发

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

5. 启动PostgreSQL和Redis（可使用Docker）
```bash
docker-compose up -d postgres redis
```

6. 启动后端服务
```bash
uvicorn app.main:app --reload
```

#### 前端开发

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 访问 http://localhost:5173

## 项目结构

```
equipment-management/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   ├── models/         # SQLAlchemy数据模型
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务逻辑
│   │   ├── tasks/          # Celery异步任务
│   │   └── utils/          # 工具函数
│   ├── requirements.txt    # Python依赖
│   ├── Dockerfile
│   └── .env.example       # 环境变量示例
├── frontend/               # Vue 3前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # Pinia状态管理
│   │   ├── api/            # API接口
│   │   ├── router/         # Vue Router路由
│   │   └── utils/          # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml      # Docker Compose配置
└── README.md
```

## 使用指南

### 1. 系统初始化
1. 管理员登录系统
2. 添加设备信息
3. 配置审批规则（哪些日志类型需要审批）
4. 配置保养周期和寿命参数

### 2. 日常使用
1. 普通用户登录
2. 提交设备日志（填写表单或上传文件OCR识别）
3. 等待管理员审批（如需要）
4. 查看设备历史记录和统计报表

### 3. 管理员操作
1. 审批用户提交的日志
2. 管理系统配置
3. 查看全系统统计报表
4. 导出数据报表

## 开发文档

详细开发文档请参见 `docs/` 目录：
- [部署文档](docs/deployment.md)
- [用户操作手册](docs/user-manual.md)
- [API文档](http://localhost:8000/docs)

## 常见问题

### 1. OCR识别准确率低
- 确保上传的文档清晰、无模糊
- 表格识别优先使用PDF格式
- 手写内容识别率较低，建议打印后扫描

### 2. 数据库连接失败
- 检查PostgreSQL服务是否启动
- 确认 `.env` 文件中的数据库配置正确
- 检查防火墙设置

### 3. 文件上传失败
- 检查上传目录权限
- 确认文件大小不超过10MB
- 检查文件格式是否支持（.pdf, .docx, .jpg, .jpeg, .png）

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目维护者：[侯嘻嘻]
- 邮箱：[2557783035@qq.com]

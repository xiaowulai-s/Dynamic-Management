# 本地部署方案 - 完整指南

## 📋 方案说明

由于 Docker 镜像下载缓慢，我们改用本地部署方案。您的系统已经安装了：
- ✅ Node.js v24.9.0（D:/NODEJS/node）
- ✅ Python 3.x（Windows Store 版本）

需要安装：
- ⚠️ PostgreSQL 15（数据库）
- ⚠️ Redis（缓存和消息队列）

## 🎯 两种方案

### 方案 A：自动安装 PostgreSQL 和 Redis（推荐）

使用 Chocolatey 包管理器一键安装：

#### 1. 安装 Chocolatey

打开 PowerShell（管理员）：
```powershell
# 设置执行策略
Set-ExecutionPolicy Bypass -Scope Process -Force

# 安装 Chocolatey
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 2. 使用 Chocolatey 安装 PostgreSQL 和 Redis

```powershell
# 安装 PostgreSQL
choco install postgresql15 -y

# 安装 Redis
choco install redis-64 -y
```

**完成！** Chocolatey 会自动配置环境变量和服务。

---

### 方案 B：手动下载安装

如果不想使用 Chocolatey，可以手动下载：

#### PostgreSQL 15

1. 访问 https://www.postgresql.org/download/windows/
2. 下载 PostgreSQL 15.x Windows installer
3. 运行安装程序
4. 记住安装时设置的密码

#### Redis for Windows

1. 访问 https://github.com/tporadowski/redis/releases
2. 下载 Redis-x64-3.0.504.msi
3. 运行安装程序

---

## 🚀 快速启动步骤

### 1. 验证安装

```powershell
# 检查 PostgreSQL
psql --version

# 检查 Redis
redis-cli ping
# 应该显示 "PONG"
```

### 2. 创建数据库

```powershell
# 打开 PowerShell，执行：
psql -U postgres -c "CREATE DATABASE equipment_db;"
```

### 3. 初始化数据库

```powershell
# 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 执行初始化脚本
psql -U postgres -d equipment_db -f backend/init.sql
```

### 4. 配置后端环境

```powershell
# 进入后端目录
cd backend

# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，修改以下配置：
# DATABASE_URL=postgresql://postgres:您的密码@localhost:5432/equipment_db
# HOST=0.0.0.0
# PORT=8000
```

### 5. 安装 Python 依赖

```powershell
# 进入后端目录
cd "d:\Demo\Dynamic-Management\backend"

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖（使用国内镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**注意**：安装 PaddleOCR 可能需要较长时间（约 5-10 分钟）

### 6. 安装前端依赖

```powershell
# 进入前端目录
cd "d:\Demo\Dynamic-Management\frontend"

# 安装依赖
npm install
```

### 7. 启动服务

需要启动 **5 个服务**（打开 5 个终端窗口）：

#### 终端 1: PostgreSQL
```powershell
# 通常自动运行，无需操作
# 如果没有启动：
pg_ctl start
```

#### 终端 2: Redis
```powershell
redis-server
```

#### 终端 3: 后端 API
```powershell
cd "d:\Demo\Dynamic-Management\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 终端 4: Celery Worker
```powershell
cd "d:\Demo\ynamic-Management\backend"
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info
```

#### 终端 5: 前端服务
```powershell
cd "d:\Demo\Dynamic-Management\frontend"
npm run dev -- --host
```

### 8. 访问系统

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 🎯 方案二：混合部署（最快）

### 说明

- 使用 Docker 运行 PostgreSQL 和 Redis（这两个镜像很小）
- 本地运行 Backend 和 Frontend（避免下载 Python 镜像）

### 步骤

#### 1. 只下载必要的镜像

```powershell
cd "d:\Demo\Dynamic-Management"

# 只下载 PostgreSQL 和 Redis（约 115 MB，很快）
docker-compose up postgres redis -d
```

#### 2. 本地启动 Backend 和 Frontend

参考上面"方案一"的步骤 5-7

---

## ⚡ 推荐方案：使用我创建的脚本

我已经为您创建了自动化脚本：

### 1. 本地部署脚本

```powershell
# 运行本地部署脚本
.\deploy-local.ps1
```

这个脚本会自动：
- ✅ 检查环境
- ✅ 安装依赖
- ✅ 初始化数据库
- ✅ 配置环境变量

### 2. 一键启动脚本

```powershell
# 启动所有服务（需要先手动启动 PostgreSQL 和 Redis）
.\start-system.ps1
```

### 3. 诊断脚本

```powershell
# 检查系统状态
.\diagnose.ps1
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Docker 部署** | 一键启动、环境隔离 | 镜像大、下载慢 | ⭐⭐⭐ |
| **本地部署（自动安装）** | 速度快、资源占用少 | 需要安装软件 | ⭐⭐⭐⭐⭐ **推荐** |
| **本地部署（手动安装）** | 完全可控 | 步骤繁琐 | ⭐⭐⭐⭐ |
| **混合部署** | 结合两者优点 | 稍微复杂 | ⭐⭐⭐⭐ |

---

## ❓ 如何选择？

### 选择本地部署，如果：
- ✅ 不想等待 Docker 下载
- ✅ 电脑配置较低
- ✅ 需要频繁修改代码
- ✅ 熟悉本地开发环境

### 选择 Docker，如果：
- ✅ 想快速启动（首次除外）
- ✅ 需要和生产环境一致
- ✅ 不想安装多个软件
- ✅ 网络速度足够快

---

## 🎯 我的建议

**立即开始本地部署！**

理由：
1. **更快**: 10-15 分钟 vs 15-20 分钟（Docker 下载时间不确定）
2. **更稳定**: 不依赖网络下载大文件
3. **更灵活**: 方便调试和开发

### 下一步行动

1. **安装 PostgreSQL 和 Redis**（使用 Chocolatey）
2. **运行自动化脚本**: `.\deploy-local.ps1`
3. **启动系统**: `.\start-system.ps1`

---

**您想选择哪个方案？**

- **方案 A**: 本地部署（我帮您自动化安装）
- **方案 B**: 继续等待 Docker
- **方案 C**: 混合部署
- **方案 D**: 了解更多细节

请告诉我您的选择！🚀

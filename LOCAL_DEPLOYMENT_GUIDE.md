# 本地部署完整指南

本指南将帮助您在本地 Windows 电脑上部署设备信息动态管理系统，并配置局域网内其他用户访问。

---

## 📋 目录

1. [环境准备](#环境准备)
2. [安装依赖软件](#安装依赖软件)
3. [配置项目](#配置项目)
4. [启动数据库](#启动数据库)
5. [启动后端服务](#启动后端服务)
6. [启动前端服务](#启动前端服务)
7. [配置局域网访问](#配置局域网访问)
8. [验证部署](#验证部署)
9. [常见问题](#常见问题)

---

## 环境准备

### 系统要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10/11 | Windows 11 |
| CPU | 双核 | 四核及以上 |
| 内存 | 4GB | 8GB 及以上 |
| 磁盘空间 | 10GB | 20GB 及以上 |
| 网络 | 局域网 | 局域网 + 互联网（下载依赖） |

---

## 安装依赖软件

### 方案选择

**方案 A: Docker 部署（推荐）**
- ✅ 一键启动，自动配置
- ✅ 环境隔离，不污染系统
- ✅ 易于管理和升级
- ⚠️ 需要安装 Docker Desktop（约 500MB）

**方案 B: 本地部署**
- ✅ 不需要 Docker
- ⚠️ 需要手动安装 PostgreSQL、Redis
- ⚠️ 环境配置较复杂

### 方案 A: Docker 部署（推荐）

#### 1. 安装 Docker Desktop

1. 访问 Docker 官网下载页面：
   ```
   https://www.docker.com/products/docker-desktop/
   ```

2. 下载 Docker Desktop for Windows（约 500MB）

3. 运行安装程序，按提示安装

4. 安装完成后**重启电脑**

5. 启动 Docker Desktop（开始菜单 → Docker Desktop）

6. 验证安装：
   ```powershell
   # 打开 PowerShell 或命令提示符
   docker --version
   docker-compose --version
   ```

#### 2. 启动系统

```powershell
# 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 启动所有服务
docker-compose up -d --build

# 查看服务状态（应显示所有服务为 "Up"）
docker-compose ps

# 查看日志（可选）
docker-compose logs -f
```

**首次启动时间**: 约 10-15 分钟（下载镜像约 2-3GB）

#### 3. 跳过 Docker，直接使用方案 B

---

### 方案 B: 本地部署（不使用 Docker）

#### 1. 安装 PostgreSQL 15

**下载地址**: https://www.postgresql.org/download/windows/

**安装步骤**:

1. 下载 PostgreSQL 15 Windows 安装程序
2. 运行安装程序
3. 选择安装目录（默认即可）
4. 设置超级用户密码（**请记住此密码**）
5. 保持默认端口 `5432`
6. 完成安装

**验证安装**:
```powershell
# 打开命令提示符
psql --version
# 应显示 psql (PostgreSQL) 15.x
```

**创建数据库**:

方法一：使用 pgAdmin（图形界面）
1. 打开 pgAdmin
2. 连接到 PostgreSQL 服务器
3. 创建数据库 `equipment_db`

方法二：使用命令行
```powershell
# 打开命令提示符
psql -U postgres

# 在 psql 中执行
CREATE DATABASE equipment_db;
\q
```

#### 2. 安装 Redis

**下载地址**: https://github.com/tporadowski/redis/releases

**安装步骤**:

1. 下载 Redis for Windows（选择 Redis-x64-3.0.504.msi 或最新版本）
2. 运行安装程序
3. 保持默认端口 `6379`
4. 完成安装

**启动 Redis**:
```powershell
# Redis 安装为 Windows 服务，会自动启动
# 或手动启动
redis-server
```

**验证安装**:
```powershell
# 打开新的命令提示符窗口
redis-cli ping
# 应显示 "PONG"
```

#### 3. 安装 Python 3.11

**下载地址**: https://www.python.org/downloads/windows/

**安装步骤**:

1. 下载 Python 3.11 Windows installer（64-bit）
2. 运行安装程序
3. ⚠️ **重要**: 勾选 "Add Python to PATH"
4. 选择 "Customize installation"
5. 确保所有可选功能都选中
6. 完成安装

**验证安装**:
```powershell
# 打开新的 PowerShell
python --version
# 应显示 Python 3.11.x

pip --version
```

**安装 Python 依赖**:
```powershell
# 进入后端目录
cd "d:\Demo\Dynamic-Management\backend"

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. 安装 Node.js 18

**下载地址**: https://nodejs.org/

**安装步骤**:

1. 下载 Node.js 18 LTS Windows installer（64-bit）
2. 运行安装程序
3. 保持默认选项
4. 完成安装

**验证安装**:
```powershell
# 打开新的 PowerShell
node --version
# 应显示 v18.x.x

npm --version
```

**安装前端依赖**:
```powershell
# 进入前端目录
cd "d:\Demo\Dynamic-Management\frontend"

# 安装依赖
npm install
```

---

## 配置项目

### 1. 配置后端环境变量

在 `backend` 目录下创建 `.env` 文件：

```powershell
# 进入后端目录
cd "d:\Demo\Dynamic-Management\backend"

# 复制环境变量模板
copy .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:您的密码@localhost:5432/equipment_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=您的密码
POSTGRES_DB=equipment_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置（请修改为随机字符串）
SECRET_KEY=your-secret-key-change-this-in-production-abc123xyz789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME=设备信息动态管理系统
APP_VERSION=1.0.0
DEBUG=True

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.docx,.jpg,.jpeg,.png

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OCR配置
OCR_LANGUAGE=ch

# 服务器配置（重点！局域网访问必须设置为 0.0.0.0）
HOST=0.0.0.0
PORT=8000
```

**重要提示**:
- ⚠️ 将 `您的密码` 替换为实际安装 PostgreSQL 时设置的密码
- ⚠️ `HOST=0.0.0.0` 是必须的，表示监听所有网络接口，否则局域网无法访问

### 2. 初始化数据库

**方法一：使用 init.sql（推荐）**

```powershell
# 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 使用 psql 执行初始化脚本
psql -U postgres -d equipment_db -f init.sql

# 如果提示密码，输入 PostgreSQL 的密码
```

**方法二：手动创建**

```powershell
# 打开 psql
psql -U postgres

# 执行 SQL 脚本
\i init.sql
```

**验证数据库**:
```sql
-- 在 psql 中执行
\dt
-- 应显示 15 张表

SELECT * FROM users;
-- 应显示 admin 用户
```

---

## 启动服务

### 方案 A: Docker 部署（推荐）

如果使用 Docker 部署，只需执行：

```powershell
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps
```

**所有服务会自动启动**：
- PostgreSQL（数据库）
- Redis（缓存）
- Backend（后端 API）
- Celery Worker（异步任务）
- Celery Beat（定时任务）
- Frontend（前端开发服务器）

### 方案 B: 本地部署

需要手动启动多个服务，建议使用**方案 A（Docker）**更简单。

#### 方法一：使用一键启动脚本（推荐）

我为你创建了一个一键启动脚本，请查看下一节。

#### 方法二：手动启动

**终端 1：启动 PostgreSQL**
```powershell
# PostgreSQL 通常作为服务运行，无需手动启动
# 如果没有启动，可以执行：
pg_ctl start
```

**终端 2：启动 Redis**
```powershell
redis-server
```

**终端 3：启动后端服务**
```powershell
cd "d:\Demo\Dynamic-Management\backend"

# 如果使用虚拟环境，先激活
venv\Scripts\activate

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**终端 4：启动 Celery Worker（异步任务）**
```powershell
cd "d:\Demo\Dynamic-Management\backend"

# 激活虚拟环境
venv\Scripts\activate

# 启动 Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info
```

**终端 5：启动 Celery Beat（定时任务）**
```powershell
cd "d:\Demo\Dynamic-Management\backend"

# 激活虚拟环境
venv\Scripts\activate

# 启动 Celery Beat
celery -A app.tasks.celery_app beat --loglevel=info
```

**终端 6：启动前端服务**
```powershell
cd "d:\Demo\Dynamic-Management\frontend"

# 启动开发服务器
npm run dev -- --host
```

**您需要打开 6 个终端窗口，建议使用方案 A（Docker）！**

---

## 一键部署脚本

我已经为您创建了自动化部署脚本，请查看以下文件：
- `deploy-docker.ps1` - Docker 部署脚本
- `deploy-local.ps1` - 本地部署脚本
- `start-system.ps1` - 系统启动脚本
- `stop-system.ps1` - 系统停止脚本

---

## 配置局域网访问

### 1. 获取本机 IP 地址

```powershell
# 查看本机 IP
ipconfig

# 在 "无线局域网适配器 WLAN" 或 "以太网适配器" 下查看
# IPv4 地址 例如：192.168.1.100
```

**假设本机 IP 为**: `192.168.1.100`

### 2. 配置防火墙

**Windows Defender 防火墙配置**:

1. 打开 Windows 安全中心 → 防火墙和网络保护 → 高级设置

2. 点击左侧 "入站规则" → 右侧 "新建规则"

3. 选择 "端口" → 下一步

4. 选择 "TCP"，添加端口：
   - `8000`（后端 API）
   - `5173`（前端开发服务器）

5. 选择 "允许连接" → 下一步

6. 全部勾选 → 下一步

7. 输入规则名称（如 "设备管理系统-后端"、"设备管理系统-前端"）→ 完成

**PowerShell 一键配置防火墙**（需要管理员权限）:
```powershell
# 开放 8000 端口（后端）
New-NetFirewallRule -DisplayName "设备管理系统-后端" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# 开放 5173 端口（前端）
New-NetFirewallRule -DisplayName "设备管理系统-前端" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow

# 开放 5432 端口（PostgreSQL，可选，如果需要局域网其他电脑访问数据库）
# New-NetFirewallRule -DisplayName "设备管理系统-数据库" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow
```

### 3. 配置后端允许跨域

后端已经配置了 CORS，允许所有来源访问。如果要限制，修改 `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://192.168.1.100:5173"],  # 添加局域网 IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. 修改前端 API 地址

前端环境变量在 `docker-compose.yml` 中配置为 `http://localhost:8000`。

**Docker 部署**：不需要修改，已经配置正确。

**本地部署**：修改 `frontend\.env` 文件：
```env
VITE_API_URL=http://192.168.1.100:8000
```

如果文件不存在，创建它。

---

## 验证部署

### 1. 本地访问验证

**本机访问**:
- 打开浏览器访问: http://localhost:5173
- 或 http://127.0.0.1:5173

**预期结果**:
- ✅ 显示登录页面
- ✅ 使用 admin/admin123 登录
- ✅ 成功进入仪表盘

### 2. 局域网访问验证

**其他设备访问**:
- 确保其他设备和本机在**同一局域网**
- 打开浏览器访问: http://192.168.1.100:5173
- （将 `192.168.1.100` 替换为您的实际 IP）

**预期结果**:
- ✅ 其他设备可以打开登录页面
- ✅ 可以正常登录和使用

### 3. API 访问验证

**访问 API 文档**:
- 本机: http://localhost:8000/docs
- 局域网: http://192.168.1.100:8000/docs

### 4. 完整功能测试

参考 [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) 进行完整功能测试。

---

## 常见问题

### 问题 1: 端口被占用

**现象**:
```
Error: listen EADDRINUSE: address already in use :::5173
```

**解决方案**:
```powershell
# 查看占用端口的进程
netstat -ano | findstr :5173

# 结束进程（替换 <PID> 为实际进程 ID）
taskkill /PID <PID> /F

# 或者修改端口
# 前端：修改 docker-compose.yml 或前端配置
# 后端：修改 .env 文件中的 PORT
```

### 问题 2: 数据库连接失败

**现象**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:
1. 检查 PostgreSQL 是否启动
   ```powershell
   # Docker 部署
   docker-compose ps postgres

   # 本地部署
   Get-Service postgresql*
   ```

2. 检查数据库配置
   - 用户名是否正确
   - 密码是否正确
   - 数据库名称是否正确
   - 端口是否为 5432

3. 检查 PostgreSQL 是否允许本地连接
   - 查看 `pg_hba.conf` 文件
   - 确保有以下配置：
     ```
     host    all             all             127.0.0.1/32            md5
     host    all             all             ::1/128                 md5
     ```

### 问题 3: 局域网无法访问

**排查步骤**:

1. **检查本机防火墙**
   ```powershell
   # 检查防火墙规则
   Get-NetFirewallRule -DisplayName "设备管理系统*"
   ```

2. **检查本机 IP 是否正确**
   ```powershell
   ipconfig
   ```

3. **检查是否在同一个局域网**
   - 确保其他设备和本机连接到同一个 WiFi 或路由器

4. **检查是否启用了网络发现**
   - 控制面板 → 网络和共享中心 → 高级共享设置
   - 启用网络发现

5. **测试网络连通性**
   ```powershell
   # 在其他设备上使用 ping 测试
   ping 192.168.1.100

   # 测试端口是否开放
   Test-NetConnection -ComputerName 192.168.1.100 -Port 5173
   ```

### 问题 4: 前端页面空白

**现象**: 浏览器打开后显示空白页面

**解决方案**:
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签页的错误信息
3. 常见原因：
   - API 地址配置错误
   - CORS 跨域问题
   - 后端服务未启动

### 问题 5: Redis 连接失败

**现象**:
```
ConnectionError: Error 111 connecting to localhost:6379
```

**解决方案**:
1. 检查 Redis 是否启动
   ```powershell
   # Docker 部署
   docker-compose ps redis

   # 本地部署
   redis-cli ping
   # 应显示 "PONG"
   ```

2. 启动 Redis
   ```powershell
   # Windows 服务方式
   net start Redis

   # 或直接运行
   redis-server
   ```

---

## 进阶配置

### 1. 配置开机自启动

#### Docker 部署
Docker Desktop 设置为开机启动，`docker-compose.yml` 中已配置 `restart: unless-stopped`。

#### 本地部署
将服务配置为 Windows 服务，建议使用 NSSM（Non-Sucking Service Manager）：
- 下载地址: https://nssm.cc/download
- 使用 NSSM 将 Python、Redis 等服务安装为 Windows 服务

### 2. 配置域名访问

**在路由器上配置端口转发**:
1. 登录路由器管理界面（通常是 192.168.1.1）
2. 找到 "端口转发" 或 "虚拟服务器" 设置
3. 添加转发规则：
   - 外部端口: 80（或 8080）
   - 内部 IP: 192.168.1.100（本机 IP）
   - 内部端口: 5173
4. 保存配置

**配置 DDNS（动态域名）**:
- 使用花生壳、DDNS 等服务
- 将动态 IP 映射到域名
- 实现外网访问

### 3. 配置 HTTPS

**使用 Let's Encrypt 免费证书**:
```powershell
# 安装 Certbot
choco install certbot

# 申请证书
certbot certonly --standalone -d your-domain.com

# 证书将保存在 C:\Certbot\live\your-domain.com\
```

**配置 Nginx**（参考 TENCENT_CLOUD_DEPLOYMENT.md）

---

## 备份与恢复

### 数据库备份

```powershell
# Docker 部署
docker exec equipment-postgres pg_dump -U postgres equipment_db > backup.sql

# 本地部署
pg_dump -U postgres equipment_db > backup.sql
```

### 数据库恢复

```powershell
# Docker 部署
docker exec -i equipment-postgres psql -U postgres equipment_db < backup.sql

# 本地部署
psql -U postgres equipment_db < backup.sql
```

---

## 升级系统

```powershell
# 1. 备份数据库
pg_dump -U postgres equipment_db > backup.sql

# 2. 拉取最新代码
cd "d:\Demo\Dynamic-Management"
git pull origin main

# 3. 重新启动
docker-compose down
docker-compose up -d --build
```

---

## 获取帮助

- 📖 [完整文档索引](DOCUMENTATION_INDEX.md)
- 📋 [测试清单](TESTING_CHECKLIST.md)
- 🔧 [架构验证报告](ARCHITECTURE_VERIFICATION.md)
- 💬 [GitHub Issues](https://github.com/xiaowulai-s/Dynamic-Management/issues)

---

**祝部署顺利！🎉**

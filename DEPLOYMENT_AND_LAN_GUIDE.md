# 部署与局域网访问完整指南

本指南提供完整的本地部署和局域网访问配置说明。

---

## 📋 部署方案对比

| 方案 | 难度 | 时间 | 推荐度 |
|------|------|------|--------|
| **Docker 部署** | ⭐ 简单 | 10-15 分钟 | ⭐⭐⭐⭐⭐ 强烈推荐 |
| **本地部署** | ⭐⭐⭐ 复杂 | 30-60 分钟 | ⭐⭐⭐ 需要高级用户 |

**推荐使用 Docker 部署！** 一键启动，自动配置，无需手动安装 PostgreSQL、Redis 等依赖。

---

## 🚀 方案一：Docker 部署（推荐）

### 前置条件

1. **安装 Docker Desktop**
   - 下载：https://www.docker.com/products/docker-desktop/
   - 约 500MB，安装后需重启电脑
   - 启动 Docker Desktop（从开始菜单）

### 一键部署

```powershell
# 1. 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 2. 一键启动（首次约 10-15 分钟）
.\start-system.ps1

# 3. 等待完成后，访问
http://localhost:5173
```

**就是这么简单！** 🎉

---

## 🌐 局域网访问配置

### 方法一：自动配置（推荐）

```powershell
# 1. 配置防火墙
.\setup-firewall.ps1

# 2. 查看本机 IP
.\show-network-info.ps1

# 3. 测试局域网访问
.\test-lan-access.ps1
```

### 方法二：手动配置

#### 步骤 1: 获取本机 IP

```powershell
# 查看 IP 地址
ipconfig

# 找到 "IPv4 地址"，例如: 192.168.1.100
```

#### 步骤 2: 配置防火墙

**PowerShell（管理员）**:
```powershell
# 开放前端端口 5173
New-NetFirewallRule -DisplayName "设备管理系统-前端" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow

# 开放后端端口 8000
New-NetFirewallRule -DisplayName "设备管理系统-后端" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

**或使用图形界面**:
1. Windows 安全中心 → 防火墙和网络保护 → 高级设置
2. 入站规则 → 新建规则
3. 选择 "端口" → 下一步
4. TCP → 本地端口输入 `5173,8000`
5. 允许连接 → 下一步
6. 全部勾选 → 下一步
7. 输入名称 → 完成

#### 步骤 3: 确保后端监听所有接口

检查 `backend\.env` 文件：
```env
HOST=0.0.0.0  # ✅ 必须为 0.0.0.0，表示监听所有接口
PORT=8000
```

**为什么重要？**
- `HOST=0.0.0.0` → 监听所有网络接口，局域网可访问
- `HOST=127.0.0.1` → 仅本地回环，局域网无法访问 ❌

#### 步骤 4: 验证局域网访问

在其他设备（手机、平板、其他电脑）上打开浏览器访问：
```
http://192.168.1.100:5173
```

（将 `192.168.1.100` 替换为您的实际 IP）

---

## 🔧 方案二：本地部署（不使用 Docker）

### 适合人群

- 高级用户
- Docker 安装困难
- 需要深度定制

### 前置条件

需要手动安装以下软件：

| 软件 | 版本要求 | 下载地址 |
|------|---------|---------|
| Python | 3.11+ | https://www.python.org/downloads/windows/ |
| Node.js | 18+ | https://nodejs.org/ |
| PostgreSQL | 15+ | https://www.postgresql.org/download/windows/ |
| Redis | 最新版 | https://github.com/tporadowski/redis/releases |

### 部署步骤

#### 1. 安装依赖软件

按照下表安装并验证：

**Python**:
```powershell
python --version  # 应显示 Python 3.11.x
pip --version
```

**Node.js**:
```powershell
node --version  # 应显示 v18.x.x
npm --version
```

**PostgreSQL**:
```powershell
psql --version  # 应显示 psql 15.x
```

**Redis**:
```powershell
redis-cli ping  # 应显示 PONG
```

#### 2. 安装 Python 依赖

```powershell
cd "d:\Demo\Dynamic-Management\backend"

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 安装 Node.js 依赖

```powershell
cd "d:\Demo\Dynamic-Management\frontend"
npm install
```

#### 4. 配置环境变量

在 `backend\.env` 文件中配置：
```env
DATABASE_URL=postgresql://postgres:您的密码@localhost:5432/equipment_db
REDIS_URL=redis://localhost:6379/0
HOST=0.0.0.0  # ✅ 必须为 0.0.0.0
PORT=8000
```

#### 5. 初始化数据库

```powershell
# 创建数据库
psql -U postgres -c "CREATE DATABASE equipment_db;"

# 执行初始化脚本
psql -U postgres -d equipment_db -f init.sql
```

#### 6. 启动服务（需打开 6 个终端）

**终端 1: PostgreSQL**
```powershell
# 通常自动运行，无需操作
```

**终端 2: Redis**
```powershell
redis-server
```

**终端 3: 后端服务**
```powershell
cd "d:\Demo\Dynamic-Management\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**终端 4: Celery Worker**
```powershell
cd "d:\Demo\Dynamic-Management\backend"
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info
```

**终端 5: Celery Beat**
```powershell
cd "d:\Demo\Dynamic-Management\backend"
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info
```

**终端 6: 前端服务**
```powershell
cd "d:\Demo\Dynamic-Management\frontend"
npm run dev -- --host
```

**或者使用一键启动脚本**:
```powershell
.\deploy-local.ps1
.\start-system-local.ps1
```

---

## 📚 创建的文档和脚本

### 📄 文档

| 文件 | 说明 |
|------|------|
| **LOCAL_DEPLOYMENT_GUIDE.md** | 完整的本地部署指南 |
| **QUICK_START_NEW.md** | 快速开始指南（5分钟部署） |

### 🔧 脚本

| 脚本 | 功能 |
|------|------|
| **start-system.ps1** | 启动系统（Docker 模式） |
| **stop-system.ps1** | 停止系统（Docker 模式） |
| **deploy-docker.ps1** | 一键部署（Docker 模式） |
| **deploy-local.ps1** | 一键部署（本地模式） |
| **setup-firewall.ps1** | 配置防火墙规则 |
| **system-status.ps1** | 查看系统状态 |
| **diagnose.ps1** | 系统诊断 |
| **test-lan-access.ps1** | 测试局域网访问 |
| **show-network-info.ps1** | 显示网络信息 |

---

## 🎯 推荐操作流程

### 第一次部署

```powershell
# 1. 安装 Docker Desktop（如果还没安装）
# 下载地址: https://www.docker.com/products/docker-desktop/

# 2. 启动 Docker Desktop
# 从开始菜单启动 Docker Desktop

# 3. 一键启动系统
.\start-system.ps1

# 4. 配置防火墙
.\setup-firewall.ps1

# 5. 查看网络信息
.\show-network-info.ps1

# 6. 访问系统
# 浏览器打开: http://localhost:5173
```

### 后续启动

```powershell
# 启动
.\start-system.ps1

# 停止
.\stop-system.ps1
```

### 局域网访问测试

```powershell
# 查看本机 IP
.\show-network-info.ps1

# 测试局域网访问
.\test-lan-access.ps1

# 如有问题，自动修复
.\test-lan-access.ps1 -Fix
```

---

## ❓ 常见问题

### 1. Docker 启动慢

**原因**: 首次启动需下载约 2-3GB 的镜像

**解决**: 耐心等待，查看下载进度：
```powershell
docker-compose logs -f
```

### 2. 局域网无法访问

**排查步骤**:

```powershell
# 1. 完整诊断
.\diagnose.ps1

# 2. 测试局域网访问
.\test-lan-access.ps1

# 3. 配置防火墙
.\setup-firewall.ps1

# 4. 检查网络信息
.\show-network-info.ps1
```

**常见原因**:
- ❌ 防火墙未开放端口
- ❌ 后端未监听 0.0.0.0（检查 `HOST` 配置）
- ❌ 设备和本机不在同一局域网
- ❌ 路由器启用了 AP 隔离

### 3. 端口被占用

```powershell
# 查看占用端口的进程
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# 结束进程（替换 <PID>）
taskkill /PID <PID> /F
```

### 4. 数据库连接失败

```powershell
# 检查 PostgreSQL 状态
docker-compose ps postgres  # Docker 模式
# 或
Get-Service postgresql*  # 本地模式

# 检查连接
.\diagnose.ps1
```

---

## 📞 获取帮助

1. **查看完整文档**: [LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md)
2. **运行诊断工具**: `.\diagnose.ps1`
3. **查看文档索引**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
4. **GitHub Issues**: https://github.com/xiaowulai-s/Dynamic-Management/issues

---

**版本**: v1.0
**更新日期**: 2026-07-17
**文档维护**: Claude Code

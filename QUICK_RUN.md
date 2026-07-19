# 快速运行指南

## 环境要求

### 必需软件
- **Docker Desktop** - [下载地址](https://www.docker.com/products/docker-desktop)
- **Git** - [下载地址](https://git-scm.com/download/win)

### 推荐配置
- CPU: 4核心及以上
- 内存: 8GB 及以上
- 磁盘: 20GB 可用空间

---

## 一键部署（推荐）

### Windows PowerShell

```powershell
# 1. 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 2. 启动所有服务
docker-compose up -d --build

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志（可选）
docker-compose logs -f
```

### 首次运行时间
- 下载镜像: 5-10 分钟（取决于网络）
- 数据库初始化: 1-2 分钟
- 首次启动: 约 10-15 分钟

---

## 访问系统

### 应用地址
- **开发模式前端**: http://localhost:5173
- **生产模式前端**: http://localhost:80
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **API 文档(ReDoc)**: http://localhost:8000/redoc

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| **超级管理员** | root | root123 |
| **管理员** | admin | admin123 |

⚠️ **首次登录后请立即修改密码！**

---

## 服务管理

### 常用命令

```powershell
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 停止服务并删除数据（慎用）
docker-compose down -v

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [服务名]

# 进入容器
docker exec -it equipment-backend bash

# 备份数据库
docker exec equipment-postgres pg_dump -U postgres equipment_db > backup.sql
```

### 服务说明

| 服务名 | 容器名 | 端口 | 说明 |
|--------|--------|------|------|
| PostgreSQL | equipment-postgres | 5432 | 数据库 |
| Redis | equipment-redis | 6379 | 缓存和消息队列 |
| Backend | equipment-backend | 8000 | 后端 API |
| Celery Worker | equipment-celery-worker | - | 异步任务 |
| Celery Beat | equipment-celery-beat | - | 定时任务 |
| Frontend | equipment-frontend | 5173 | 开发服务器 |
| Nginx | equipment-nginx | 80 | 生产服务器 |

---

## 常见问题

### 1. 端口被占用

如果 80 或 5173 端口被占用：

```powershell
# 查看占用端口的进程
netstat -ano | findstr :80
netstat -ano | findstr :5173

# 结束进程（替换 <PID> 为实际进程ID）
taskkill /PID <PID> /F
```

或者修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:80"  # 将主机的 8080 映射到容器的 80
```

### 2. Docker 启动慢

首次启动需要下载镜像（约 2-3GB），请耐心等待。

```powershell
# 查看下载进度
docker-compose logs -f
```

### 3. 数据库连接失败

确保 PostgreSQL 容器已启动并健康：

```powershell
# 查看容器状态
docker-compose ps

# 查看 PostgreSQL 日志
docker-compose logs postgres
```

### 4. 前端页面空白

检查前端服务是否启动成功：

```powershell
# 查看前端日志
docker-compose logs frontend

# 重启前端服务
docker-compose restart frontend
```

### 5. API 请求失败

检查后端服务是否正常运行：

```powershell
# 访问 API 文档测试
http://localhost:8000/docs

# 查看后端日志
docker-compose logs backend
```

---

## 开发模式

### 前端开发（热重载）

前端已配置热重载，修改代码会自动刷新。

### 后端开发（热重载）

后端使用 `--reload` 参数，修改 Python 代码会自动重启。

---

## 数据备份

### 备份数据库

```powershell
# 备份到 SQL 文件
docker exec equipment-postgres pg_dump -U postgres equipment_db > backup.sql

# 恢复数据库
docker exec -i equipment-postgres psql -U postgres equipment_db < backup.sql
```

### 备份上传文件

```powershell
# 备份上传目录
cp -r ./uploads ./uploads_backup
```

---

## 更新系统

```powershell
# 1. 拉取最新代码
git pull origin main

# 2. 重启服务
docker-compose down
docker-compose up -d --build

# 3. 查看日志
docker-compose logs -f
```

---

## 停止服务

```powershell
# 停止所有服务（保留数据）
docker-compose down

# 停止并删除所有数据（慎用）
docker-compose down -v
```

---

## 获取帮助

- 📖 详细文档: [README.md](README.md)
- 📋 部署文档: [TENCENT_CLOUD_DEPLOYMENT.md](TENCENT_CLOUD_DEPLOYMENT.md)
- 📝 更新日志: [CHANGELOG.md](CHANGELOG.md)
- 🐛 问题反馈: [GitHub Issues](https://github.com/xiaowulai-s/Dynamic-Management/issues)

---

**祝使用愉快！🎉**

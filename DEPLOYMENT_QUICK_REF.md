# 🎯 部署指南 - 快速参考

本文件提供本地部署和局域网访问的快速参考。

---

## ⚡ 5分钟快速部署（Docker）

```powershell
# 1. 进入项目
cd "d:\Demo\Dynamic-Management"

# 2. 启动系统
.\start-system.ps1

# 3. 访问
http://localhost:5173
```

**账号**: admin / admin123

---

## 🌐 局域网访问配置

### 一键配置
```powershell
# 配置防火墙
.\setup-firewall.ps1

# 测试访问
.\test-lan-access.ps1
```

### 手动配置

1. **获取 IP**:
   ```powershell
   ipconfig
   # 找到 IPv4 地址，如 192.168.1.100
   ```

2. **配置防火墙**（管理员 PowerShell）:
   ```powershell
   New-NetFirewallRule -DisplayName "设备管理系统-前端" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
   New-NetFirewallRule -DisplayName "设备管理系统-后端" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
   ```

3. **验证后端配置**:
   ```env
   # 检查 backend\.env 文件
   HOST=0.0.0.0  # 必须为 0.0.0.0
   PORT=8000
   ```

4. **局域网访问**:
   ```
   http://192.168.1.100:5173
   ```

---

## 🛠️ 常用命令

| 命令 | 说明 |
|------|------|
| `.\start-system.ps1` | 启动系统 |
| `.\stop-system.ps1` | 停止系统 |
| `.\system-status.ps1` | 查看状态 |
| `.\diagnose.ps1` | 诊断问题 |
| `.\setup-firewall.ps1` | 配置防火墙 |
| `.\show-network-info.ps1` | 显示网络信息 |
| `.\test-lan-access.ps1` | 测试局域网访问 |
| `docker-compose logs -f` | 查看日志 |
| `docker-compose ps` | 查看服务状态 |

---

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| **[DEPLOYMENT_AND_LAN_GUIDE.md](DEPLOYMENT_AND_LAN_GUIDE.md)** | 完整部署指南 ⭐ **推荐阅读** |
| **[LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md)** | 详细本地部署指南 |
| **[QUICK_START_NEW.md](QUICK_START_NEW.md)** | 快速开始指南 |
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | 文档索引 |

---

## ❓ 遇到问题？

### 1. 诊断问题
```powershell
.\diagnose.ps1
```

### 2. 查看日志
```powershell
# Docker 模式
docker-compose logs -f

# 查看特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 常见问题

**问题 1: 启动失败**
- 检查 Docker Desktop 是否运行
- 检查端口是否被占用
- 运行 `.\diagnose.ps1`

**问题 2: 局域网无法访问**
- 确认设备和本机在同一局域网
- 运行 `.\setup-firewall.ps1` 配置防火墙
- 运行 `.\test-lan-access.ps1` 诊断

**问题 3: 数据库连接失败**
- 检查 PostgreSQL 服务状态
- 检查 `backend\.env` 中的数据库配置

---

## 📋 系统要求

### Docker 模式
- Windows 10/11
- Docker Desktop（约 500MB）
- 4GB+ 内存
- 10GB+ 磁盘空间

### 本地模式
- Windows 10/11
- Python 3.11
- Node.js 18
- PostgreSQL 15
- Redis
- 8GB+ 内存

---

## 🔐 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | root | root123 |
| 管理员 | admin | admin123 |

⚠️ **首次登录后请立即修改密码！**

---

**最后更新**: 2026-07-17
**维护者**: Claude Code

# 🚀 快速开始

本指南帮助您在 5 分钟内启动设备信息动态管理系统。

---

## ⚡ 最快部署（Docker 模式）

### 前提条件
- Windows 10/11
- Docker Desktop（[下载](https://www.docker.com/products/docker-desktop/)）

### 一键启动

```powershell
# 1. 进入项目目录
cd "d:\Demo\Dynamic-Management"

# 2. 启动系统
.\start-system.ps1

# 3. 等待约 30 秒后，打开浏览器访问
http://localhost:5173
```

**完成！** 🎉

---

## 📝 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 超级管理员 | root | root123 |
| 管理员 | admin | admin123 |

---

## 🌐 局域网访问

其他设备在同一个局域网内可以通过以下地址访问：
```
http://您的IP:5173
```

**查看本机 IP**:
```powershell
.\show-network-info.ps1
```

**配置防火墙**（如果无法访问）:
```powershell
.\setup-firewall.ps1
```

---

## 📚 更多文档

| 文档 | 说明 |
|------|------|
| **[LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md)** | 完整的本地部署指南（包含 Docker 和本地部署两种方案） |
| **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** | 功能测试清单（40+ 个测试场景） |
| **[ARCHITECTURE_VERIFICATION.md](ARCHITECTURE_VERIFICATION.md)** | 架构验证报告 |
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | 文档索引 |

---

## 🛠️ 常用命令

### Docker 模式

```powershell
# 启动系统
.\start-system.ps1

# 停止系统
.\stop-system.ps1

# 查看状态
.\system-status.ps1

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

### 诊断问题

```powershell
# 完整诊断
.\diagnose.ps1

# 测试局域网访问
.\test-lan-access.ps1

# 查看网络信息
.\show-network-info.ps1
```

---

## ❓ 遇到问题？

1. **查看诊断信息**
   ```powershell
   .\diagnose.ps1
   ```

2. **查看完整部署指南**
   - [LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md)

3. **查看常见问题**
   - [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**祝使用愉快！** 🎉

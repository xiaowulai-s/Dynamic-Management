# Docker 镜像源配置状态

## ✅ 已完成

1. 已在 `settings-store.json` 中添加镜像源配置
2. 创建了配置脚本：`setup-docker-mirror.ps1`

## ⚠️ 需要您手动操作

### 步骤 1: 启动 Docker Desktop

1. 从**开始菜单**启动 **Docker Desktop**
2. 等待 Docker Desktop 完全启动（右下角鲸鱼图标变绿，约 30-60 秒）

### 步骤 2: 配置镜像源（通过界面）

1. 打开 Docker Desktop 后，点击右上角 **⚙️ Settings**
2. 左侧选择 **Docker Engine**
3. 您会看到 JSON 配置编辑器

**请将以下内容复制到 Docker Engine 配置中：**

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

4. 点击右下角 **Apply & Restart**
5. Docker Desktop 会自动重启

### 步骤 3: 验证配置

Docker Desktop 重启完成后，打开 PowerShell 运行：

```powershell
# 测试拉取镜像
docker pull hello-world

# 如果成功，会看到下载进度
```

## 📝 为什么需要手动配置？

Docker Desktop 的配置存储在多个位置，Windows 上的配置文件包括：

- `settings-store.json` - Docker Desktop 应用设置
- `daemon.json` - Docker Engine 配置（可能在 ProgramData 或用户目录）

由于 Docker 进程未运行，无法确定确切的配置位置，**通过 Docker Desktop 界面配置是最可靠的方法**。

## 🔄 配置完成后

一旦配置成功并重启，运行以下命令启动系统：

```powershell
cd "d:\Demo\Dynamic-Management"
docker-compose up -d
```

**预计时间**：首次启动约 10-15 分钟（下载约 2-3GB 镜像）

---

**更新日期**: 2026-07-17 19:55

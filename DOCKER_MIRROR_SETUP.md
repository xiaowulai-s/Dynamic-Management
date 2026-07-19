# Docker 镜像源配置 - 详细步骤

## 问题说明

Docker 无法连接到 Docker Hub，需要配置国内镜像源。

## 配置方法（推荐：Docker Desktop 界面）

### 步骤 1: 打开 Docker Desktop

1. 从开始菜单启动 Docker Desktop
2. 等待 Docker Desktop 完全启动（右下角鲸鱼图标变绿）

### 步骤 2: 打开设置

1. 点击 Docker Desktop 窗口右上角的 **⚙️ Settings**（设置图标）

### 步骤 3: 配置 Docker Engine

1. 在左侧菜单选择 **Docker Engine**
2. 您会看到一个 JSON 配置编辑器

### 步骤 4: 添加镜像源配置

在 JSON 配置中添加 `registry-mirrors` 字段。**请完整替换现有配置为以下内容：**

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

**完整配置示例：**
```json
{
  "AutoStart": false,
  "DisplayedOnboarding": true,
  "EnableDockerAI": true,
  "InferenceCanUseGPUVariant": true,
  "LastContainerdSnapshotterEnable": 1784287551,
  "LicenseTermsVersion": 2,
  "SettingsVersion": 45,
  "UseContainerdSnapshotter": true,
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```

### 步骤 5: 应用配置

1. 点击右下角的 **Apply & Restart** 按钮
2. Docker Desktop 会自动重启
3. 等待约 30 秒让 Docker 完全启动

### 步骤 6: 验证配置

打开 PowerShell，运行：

```powershell
# 测试拉取镜像
docker pull hello-world

# 测试 Docker Compose
cd "d:\Demo\Dynamic-Management"
docker-compose up -d
```

---

## 替代方法：使用阿里云镜像（更快）

如果您有阿里云账号，可以获得专属加速地址：

1. 访问 https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
2. 登录阿里云账号
3. 复制您的专属镜像加速地址（类似：`https://xxxxxx.mirror.aliyuncs.com`）
4. 在 Docker Engine 配置中使用：

```json
{
  "registry-mirrors": ["https://xxxxxx.mirror.aliyuncs.com"]
}
```

---

## 常见镜像源

### 推荐镜像源（国内可用）

| 镜像源 | 地址 | 推荐度 |
|--------|------|--------|
| DaoCloud | https://docker.m.daocloud.io | ⭐⭐⭐⭐⭐ |
| 1ms.run | https://docker.1ms.run | ⭐⭐⭐⭐⭐ |
| 中科大 | https://docker.mirrors.ustc.edu.cn | ⭐⭐⭐⭐ |
| 网易 | https://hub-mirror.c.163.com | ⭐⭐⭐⭐ |
| 阿里云 | https://cr.console.aliyun.com 获取专属地址 | ⭐⭐⭐⭐⭐ |

### 已失效的镜像源（不要使用）

- ❌ https://docker.mirrors.ustc.edu.cn（有时不稳定）
- ❌ https://hub.docker.com（官方，国内无法直接访问）

---

## 故障排查

### 问题 1: Docker Desktop 找不到 Docker Engine 配置

**解决**: Docker Desktop 版本可能不支持，尝试升级到最新版本。

### 问题 2: 配置后仍然无法拉取镜像

**检查**:
1. Docker Desktop 是否已重启
2. 网络连接是否正常
3. 尝试切换到其他镜像源

### 问题 3: 镜像源全部失效

**解决**: 使用阿里云专属镜像（最稳定）

---

## 配置完成后

一旦配置成功，您就可以：

```powershell
# 启动系统
cd "d:\Demo\Dynamic-Management"
docker-compose up -d

# 查看服务状态
docker-compose ps

# 访问系统
# 浏览器打开: http://localhost:5173
```

**预计时间**: 首次启动约 10-15 分钟（下载约 2-3GB 镜像）

---

**需要帮助？** 配置完成后如果仍有问题，请运行诊断脚本：

```powershell
.\diagnose.ps1
```

# 群晖 NAS 部署指南

将设备信息动态管理系统部署到群晖 Synology NAS（x86_64 架构）的完整操作指南。

**适用环境**：
- 群晖 Synology NAS（DSM 7.0+）
- x86_64 架构（Intel/AMD CPU，如 DS920+/DS923+/DS1522+/DS723+/DS423+ 等）
- 具备 SSH 访问能力

**不适用**：ARM 架构 NAS（如 DS220/DS218/DS120/DS223j 等 J/R/ARM 系列），部分镜像可能无 ARM 版本。

---

## 一、部署前准备

### 1.1 确认 NAS 架构

登录 DSM → 控制面板 → 信息中心 → 确认"处理器"为 Intel 系列（x86_64）。

或在 SSH 中执行：
```bash
uname -m
# 输出 x86_64 则符合要求
```

### 1.2 确认 DSM 版本

- **DSM 7.2+**：使用 Container Manager（推荐，原生支持 docker-compose 项目）
- **DSM 7.0-7.1**：使用 Docker 套件（需通过 SSH 运行 docker compose 命令）
- **DSM 6.x**：建议先升级，或仅用 Docker 套件 + SSH

### 1.3 安装 Container Manager / Docker

- DSM 7.2+：套件中心 → 搜索"Container Manager" → 安装
- DSM 7.0-7.1：套件中心 → 搜索"Docker" → 安装

### 1.4 开启 SSH

1. 控制面板 → 终端机和 SNMP → 启用 SSH 功能 → 端口 22
2. 记住 NAS 的 IP 地址和 admin 账户密码

### 1.5 准备迁移包

在**当前 Windows 服务器**上运行 `迁移-导出.ps1` 生成迁移包，并将整个 `迁移包` 文件夹通过以下方式上传到 NAS：

- **方式 A（推荐）**：用 File Station 上传到 `/volume1/docker/` 目录
- **方式 B**：通过 SMB 共享文件夹映射到 Windows 网络驱动器后拷贝
- **方式 C**：用 SCP 命令（需先打包）：
  ```powershell
  # 在 Windows 上执行
  Compress-Archive -Path '迁移包\*' -DestinationPath 'equipment-migrate.zip'
  scp equipment-migrate.zip admin@NAS_IP:/volume1/docker/
  ```

---

## 二、部署步骤（SSH 方式，通用）

以下步骤在 SSH 终端中执行。用 PuTTY 或 Windows Terminal 连接 NAS：
```bash
ssh admin@NAS_IP
```

### 2.1 创建项目目录

```bash
sudo mkdir -p /volume1/docker/equipment
sudo chown $USER:users /volume1/docker/equipment
cd /volume1/docker/equipment
```

### 2.2 解压迁移包内容

如果上传的是 zip：
```bash
sudo apt install unzip  # 若无 unzip（群晖自带 7z，也可用 7z x）
unzip /volume1/docker/equipment-migrate.zip -d /volume1/docker/equipment/
```

或用 File Station 解压后移动文件，确保目录结构如下：
```
/volume1/docker/equipment/
├── data/
│   ├── equipment_db.dump
│   └── uploads.zip
├── backend/
├── frontend/
│   └── dist/
├── docker-compose.yml
├── nginx.prod.conf
└── ...
```

### 2.3 修改 docker-compose.yml 适配群晖

群晖的卷映射建议用绝对路径，编辑 `docker-compose.yml`：

```bash
vi docker-compose.yml
```

**需修改的内容**：

1. **postgres 数据卷**（从命名卷改为绑定路径）：
   ```yaml
   postgres:
     volumes:
       - /volume1/docker/equipment/postgres_data:/var/lib/postgresql/data
   ```
   替换原有的 `postgres_data:/var/lib/postgresql/data` 和顶层 volumes 定义。

2. **redis 数据卷**：
   ```yaml
   redis:
     volumes:
       - /volume1/docker/equipment/redis_data:/data
   ```

3. **uploads 目录**：
   ```yaml
   backend:
     volumes:
       - /volume1/docker/equipment/uploads:/app/uploads
   ```

4. **前端 dist**（nginx 挂载）：
   ```yaml
   nginx:
     volumes:
       - /volume1/docker/equipment/frontend/dist:/usr/share/nginx/html:ro
       - /volume1/docker/equipment/nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro
   ```

5. **端口冲突检查**（群晖默认占用 5000/5001/6379 等）：
   ```yaml
   # 检查端口占用
   sudo netstat -tulpn | grep -E ':(9000|8000|15432|6379)'
   ```
   若 6379 被群晖占用，redis 端口改为 `16379:6379`。

### 2.4 启动服务

```bash
cd /volume1/docker/equipment
sudo docker compose up -d --build
```

> **注意**：群晖上构建后端镜像（python:3.11-slim）可能较慢（10-20 分钟），取决于 CPU 性能。若迁移包含已构建的前端 dist，前端无需构建。

### 2.5 等待 PostgreSQL 就绪

```bash
# 循环检查直到就绪
until sudo docker exec equipment-postgres pg_isready -U postgres; do
  echo "等待 PostgreSQL..."
  sleep 2
done
echo "PostgreSQL 已就绪"
```

### 2.6 导入数据库

```bash
# 清空并重建数据库
sudo docker exec equipment-postgres psql -U postgres -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='equipment_db' AND pid <> pg_backend_pid();"
sudo docker exec equipment-postgres psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS equipment_db;"
sudo docker exec equipment-postgres psql -U postgres -d postgres -c "CREATE DATABASE equipment_db OWNER postgres;"

# 导入备份
sudo docker cp data/equipment_db.dump equipment-postgres:/tmp/dump.pgc
sudo docker exec equipment-postgres pg_restore -U postgres -d equipment_db --no-owner --no-privileges /tmp/dump.pgc
sudo docker exec equipment-postgres rm /tmp/dump.pgc

# 验证
sudo docker exec equipment-postgres psql -U postgres -d equipment_db -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"
```

### 2.7 还原上传文件

```bash
if [ -f data/uploads.zip ]; then
  mkdir -p uploads
  unzip data/uploads.zip -d uploads/
  echo "上传文件已还原"
fi
```

### 2.8 bcrypt 版本自检（关键）

```bash
BCRYPT_VER=$(sudo docker exec equipment-backend pip show bcrypt 2>/dev/null | grep Version)
echo "当前 bcrypt: $BCRYPT_VER"

if echo "$BCRYPT_VER" | grep -q "5.0"; then
  echo "检测到 bcrypt 5.0，降级到 4.0.1..."
  sudo docker exec equipment-backend pip install "bcrypt==4.0.1" -q
  sudo docker restart equipment-backend
  echo "bcrypt 已修复"
fi
```

### 2.9 验证部署

```bash
# 检查所有容器
sudo docker compose ps

# 测试后端
curl http://127.0.0.1:8000/api/settings/site-title

# 测试前端
curl -I http://127.0.0.1:9000/
```

### 2.10 获取访问地址

```bash
# 查看 NAS IP
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

访问地址：`http://NAS_IP:9000`

---

## 三、DSM 7.2+ Container Manager 图形化部署

DSM 7.2+ 支持通过 Container Manager 的"项目"功能直接导入 docker-compose.yml，无需 SSH。

### 3.1 创建项目

1. 打开 Container Manager → 项目 → 新增
2. 项目名称：`equipment`
3. 路径：`/volume1/docker/equipment`
4. 来源：选择"使用已有的 docker-compose.yml"
5. 选择 `/volume1/docker/equipment/docker-compose.yml`
6. 点击"下一步" → 确认 → 创建

### 3.2 构建与启动

Container Manager 会自动拉取镜像并启动。首次启动可能需要 10-30 分钟（取决于网络和 CPU）。

### 3.3 导入数据

数据导入（pg_restore）仍需通过 SSH 执行，Container Manager 不提供此功能。参考第 2.6 节。

---

## 四、开机自启配置

### 4.1 Container Manager 项目（DSM 7.2+）

项目设置 → 勾选"NAS 启动时自动启动"。

### 4.2 Docker 套件（DSM 7.0-7.1）

1. Docker 套件 → 容器 → 选中各容器 → 编辑 → 勾选"自动启动"
2. 或在 docker-compose.yml 中添加 `restart: always`：
   ```yaml
   services:
     postgres:
       restart: always
     redis:
       restart: always
     backend:
       restart: always
     nginx:
       restart: always
   ```

---

## 五、群晖专用运维脚本

### 5.1 创建启动脚本

```bash
sudo tee /volume1/docker/equipment/start.sh > /dev/null << 'EOF'
#!/bin/bash
cd /volume1/docker/equipment
echo "=== 启动设备管理系统 ==="
sudo docker compose up -d
sleep 5

# bcrypt 自检
BCRYPT_VER=$(sudo docker exec equipment-backend pip show bcrypt 2>/dev/null | grep Version)
if echo "$BCRYPT_VER" | grep -q "5.0"; then
  echo "[警告] 检测到 bcrypt 5.0，降级到 4.0.1..."
  sudo docker exec equipment-backend pip install "bcrypt==4.0.1" -q
  sudo docker restart equipment-backend
  echo "bcrypt 已修复"
fi

echo "=== 系统已启动 ==="
echo "访问地址: http://$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):9000"
EOF

sudo chmod +x /volume1/docker/equipment/start.sh
```

### 5.2 创建停止脚本

```bash
sudo tee /volume1/docker/equipment/stop.sh > /dev/null << 'EOF'
#!/bin/bash
cd /volume1/docker/equipment
echo "=== 停止设备管理系统 ==="
sudo docker compose down
echo "=== 系统已停止 ==="
EOF

sudo chmod +x /volume1/docker/equipment/stop.sh
```

### 5.3 创建备份脚本

```bash
sudo tee /volume1/docker/equipment/backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/volume1/docker/equipment-backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR/data"

echo "=== 备份设备管理系统 ==="

# 导出数据库
sudo docker exec equipment-postgres pg_dump -U postgres -d equipment_db -Fc -f /tmp/dump.pgc
sudo docker cp equipment-postgres:/tmp/dump.pgc "$BACKUP_DIR/data/equipment_db.dump"
sudo docker exec equipment-postgres rm /tmp/dump.pgc

# 备份 uploads
if [ -d /volume1/docker/equipment/uploads ]; then
  cd /volume1/docker/equipment
  tar -czf "$BACKUP_DIR/data/uploads.tar.gz" uploads/
fi

# 备份配置
cp /volume1/docker/equipment/docker-compose.yml "$BACKUP_DIR/"
cp /volume1/docker/equipment/nginx.prod.conf "$BACKUP_DIR/"

# 清理 7 天前的备份
find /volume1/docker/equipment-backups -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null

echo "=== 备份完成: $BACKUP_DIR ==="
echo "备份大小: $(du -sh $BACKUP_DIR | cut -f1)"
EOF

sudo chmod +x /volume1/docker/equipment/backup.sh
```

### 5.4 设置定时备份

1. DSM 控制面板 → 任务计划 → 新增 → 计划任务 → 用户定义的脚本
2. 常规：任务名称 `equipment-backup`，用户 `root`
3. 执行计划：每周日 03:00
4. 执行命令：`/volume1/docker/equipment/backup.sh`

---

## 六、数据持久化与备份策略

### 6.1 持久化目录结构

```
/volume1/docker/equipment/
├── postgres_data/          # 数据库数据（持久化）
├── redis_data/             # Redis 数据（持久化）
├── uploads/                # 上传文件（持久化）
├── frontend/dist/          # 前端构建产物
├── backend/                # 后端代码
├── docker-compose.yml      # 编排配置
├── nginx.prod.conf         # Nginx 配置
├── start.sh                # 启动脚本
├── stop.sh                 # 停止脚本
└── backup.sh               # 备份脚本

/volume1/docker/equipment-backups/
├── 20260719_030000/
│   ├── data/
│   │   ├── equipment_db.dump
│   │   └── uploads.tar.gz
│   ├── docker-compose.yml
│   └── nginx.prod.conf
└── ...
```

### 6.2 群晖快照备份（推荐）

若 NAS 存储池为 Btrfs 文件系统：
1. 存储空间 → 快照 → 为 `/volume1` 启用快照
2. 设置每日快照，保留 7 天
3. 系统故障时可秒级回滚

### 6.3 Hyper Backup 异地备份

1. Hyper Backup → 新增 → 数据备份任务
2. 来源：共享文件夹 → 选择 `docker/equipment-backups`
3. 目标：本地文件夹 / 外接 USB / 云端
4. 计划：每周备份

---

## 七、网络与访问配置

### 7.1 局域网访问

直接用 `http://NAS_IP:9000` 访问。查看 NAS IP：
```bash
ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1
```

### 7.2 域名访问（可选）

1. 路由器/DNS 服务器设置：`equipment.local → NAS_IP`
2. 访问 `http://equipment.local:9000`

### 7.3 HTTPS 配置（可选）

群晖自带反向代理，可配置 HTTPS：

1. 控制面板 → 登录门户 → 高级 → 反向代理 → 新增
2. 来源：HTTPS，端口 9443，启用群晖默认证书
3. 目标：HTTP，NAS_IP:9000
4. 访问 `https://NAS_IP:9443`

### 7.4 外网访问（需谨慎）

如需外网访问，建议：
- 使用群晖 VPN Server（OpenVPN/WireGuard）建立 VPN 后访问，而非直接暴露端口
- 或用 Cloudflare Tunnel 做零信任访问
- **切勿直接将 9000 端口映射到公网**（系统有未实现的登录锁定，存在暴力破解风险）

---

## 八、常见问题

### Q1：docker compose 命令不存在

群晖的 Container Manager/Docker 套件提供的 docker 命令版本可能较旧。

```bash
# 检查版本
docker compose version    # DSM 7.2+ 支持
docker-compose version    # 旧版需用 docker-compose（带连字符）
```

若只有 `docker-compose`，将本文档中的 `docker compose` 全部替换为 `docker-compose`。

### Q2：构建后端镜像失败（网络问题）

群晖在国内拉取 Docker Hub 镜像可能慢。配置镜像加速：

1. Container Manager → 注册表 → 新增
2. 添加加速地址：
   - `https://docker.mirrors.ustc.edu.cn`
   - `https://hub-mirror.c.163.com`
3. 或在 SSH 中编辑 `/etc/docker/daemon.json`：
   ```json
   {
     "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
   }
   ```
   重启 Docker：`sudo systemctl restart docker`

### Q3：postgres 端口冲突

群晖可能预装 PostgreSQL 或其他服务占用 5432。本项目已改用 15432，通常不会冲突。若仍冲突：

```bash
# 查看占用
sudo netstat -tulpn | grep 15432

# 若冲突，改为其他端口（如 25432）
# 编辑 docker-compose.yml 中 postgres 的 ports
```

### Q4：redis 端口冲突

群晖某些套件（如 Surveillance Station）可能占用 6379。

```bash
sudo netstat -tulpn | grep 6379
```

若被占用，编辑 docker-compose.yml，redis 端口改为 `16379:6379`。

### Q5：权限问题（Permission denied）

群晖对 `/volume1/docker/` 目录有权限控制。若容器无法读写：

```bash
sudo chown -R $USER:users /volume1/docker/equipment/
sudo chmod -R 755 /volume1/docker/equipment/
```

或对 postgres_data 目录单独赋权：
```bash
sudo chown -R 999:999 /volume1/docker/equipment/postgres_data/
# 999 是 postgres 容器内的用户 ID
```

### Q6：bcrypt 导致登录 500

群晖构建镜像时若装了 bcrypt 5.0，会触发 passlib 兼容性问题。执行自检脚本：

```bash
BCRYPT_VER=$(sudo docker exec equipment-backend pip show bcrypt 2>/dev/null | grep Version)
if echo "$BCRYPT_VER" | grep -q "5.0"; then
  sudo docker exec equipment-backend pip install "bcrypt==4.0.1" -q
  sudo docker restart equipment-backend
fi
```

或直接运行 `start.sh`（已含自检逻辑）。

### Q7：容器无法访问外网

某些群晖网络配置会导致容器无法联网（影响 pip install）。

1. 控制面板 → 网络 → 网络接口 → 编辑 → 高级 → 确认"启用 IPv4 转发"
2. 或在 docker-compose.yml 中为 backend 指定 DNS：
   ```yaml
   backend:
     dns:
       - 8.8.8.8
       - 114.114.114.114
   ```

### Q8：NAS 重启后容器未自动启动

确认容器配置了 `restart: always`：
```bash
sudo docker inspect equipment-backend | grep RestartPolicy
```

或在 Container Manager → 容器 → 编辑 → 勾选"自动启动"。

### Q9：磁盘空间不足

数据库和上传文件会持续增长。定期检查：
```bash
df -h /volume1
du -sh /volume1/docker/equipment/
du -sh /volume1/docker/equipment-backups/
```

建议预留至少 5GB 空间。若不足，清理旧备份：
```bash
# 清理 7 天前的备份
find /volume1/docker/equipment-backups -type d -mtime +7 -exec rm -rf {} \;
```

---

## 九、性能考量

### 9.1 硬件建议

| 用户规模 | 最低配置 | 推荐配置 |
|----------|----------|----------|
| 1-10 人 | 2 核 CPU / 4GB RAM | 4 核 CPU / 8GB RAM |
| 10-50 人 | 4 核 CPU / 8GB RAM | 4 核 CPU / 16GB RAM |
| 50+ 人 | 不建议 NAS 部署 | 改用专用服务器 |

### 9.2 资源监控

```bash
# 实时监控容器资源
sudo docker stats

# 查看内存占用
free -h

# 查看磁盘 IO
iostat -x 1
```

### 9.3 性能优化

- **数据库**：若日志量大，考虑为 postgres 增加内存配置：
  ```yaml
  postgres:
    environment:
      - shared_buffers=512MB
      - effective_cache_size=2GB
  ```
- **前端**：nginx 已配置静态资源缓存（30 天），无需额外优化
- **后端**：FastAPI 默认单进程，若并发高可增加 workers：
  ```yaml
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```

---

## 十、从 NAS 回迁到其他服务器

如需从 NAS 迁移回 Windows 或其他 Linux 服务器：

```bash
# 在 NAS 上执行
cd /volume1/docker/equipment

# 导出数据库
sudo docker exec equipment-postgres pg_dump -U postgres -d equipment_db -Fc -f /tmp/dump.pgc
sudo docker cp equipment-postgres:/tmp/dump.pgc ./data/equipment_db.dump
sudo docker exec equipment-postgres rm /tmp/dump.pgc

# 打包上传文件
tar -czf ./data/uploads.tar.gz uploads/

# 打包整个项目
cd /volume1/docker
tar -czf /tmp/equipment-migrate.tar.gz equipment/ --exclude='postgres_data' --exclude='redis_data'
```

将 `/tmp/equipment-migrate.tar.gz` 传输到目标服务器，按目标系统的部署指南操作。

---

## 十一、安全注意事项

1. **修改默认密码**：部署后立即用 root 登录，在个人资料页修改 root123 默认密码
2. **限制 SSH 访问**：DSM 控制面板 → 终端机和 SNMP → SSH → 仅允许特定 IP
3. **启用防火墙**：DSM 控制面板 → 安全性 → 防火墙 → 仅开放必要端口（9000、22、5000/5001）
4. **定期更新 DSM**：群晖定期发布安全补丁
5. **外网访问谨慎**：系统未实现登录锁定（v1.1.2 状态），外网暴露有暴力破解风险，建议通过 VPN 访问
6. **备份加密**：Hyper Backup 支持备份加密，建议启用

---

## 十二、部署检查清单

部署完成后逐项验证：

### 基础功能
- [ ] 访问 `http://NAS_IP:9000` 显示登录页
- [ ] 登录页标题显示"设备信息动态管理系统"
- [ ] root/root123 可登录
- [ ] 侧边栏角色显示"超级管理员"

### 数据完整性
- [ ] 仪表盘统计数据正常
- [ ] 设备管理列表有数据
- [ ] 日志管理列表有数据
- [ ] 用户管理列表有 7 个用户

### 持久化
- [ ] 重启 NAS 后容器自动启动
- [ ] 重启后数据仍在（未丢失）
- [ ] 上传文件可正常访问

### 备份
- [ ] 手动运行 backup.sh 成功
- [ ] 备份文件可正常还原
- [ ] 定时备份任务已配置

### 性能
- [ ] 页面加载 < 3 秒
- [ ] 登录响应 < 2 秒
- [ ] 容器内存占用合理（< 1GB）

---

## 附录：一键部署脚本

将以下内容保存为 `/volume1/docker/equipment/deploy.sh`，执行 `sudo bash deploy.sh` 即可完成全流程部署：

```bash
#!/bin/bash
set -e

APP_DIR="/volume1/docker/equipment"
cd "$APP_DIR"

echo "============================================"
echo "  设备信息动态管理系统 - 群晖一键部署"
echo "============================================"

echo "[1/7] 启动 Docker 服务..."
sudo docker compose up -d --build

echo "[2/7] 等待 PostgreSQL 就绪..."
until sudo docker exec equipment-postgres pg_isready -U postgres 2>/dev/null; do
  echo "  等待中..."
  sleep 2
done

echo "[3/7] 导入数据库..."
sudo docker exec equipment-postgres psql -U postgres -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='equipment_db' AND pid <> pg_backend_pid();" 2>/dev/null || true
sudo docker exec equipment-postgres psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS equipment_db;" 2>/dev/null
sudo docker exec equipment-postgres psql -U postgres -d postgres -c "CREATE DATABASE equipment_db OWNER postgres;" 2>/dev/null
sudo docker cp data/equipment_db.dump equipment-postgres:/tmp/dump.pgc
sudo docker exec equipment-postgres pg_restore -U postgres -d equipment_db --no-owner --no-privileges /tmp/dump.pgc 2>/dev/null || true
sudo docker exec equipment-postgres rm /tmp/dump.pgc

echo "[4/7] 还原上传文件..."
if [ -f data/uploads.zip ]; then
  mkdir -p uploads
  unzip -o data/uploads.zip -d uploads/ > /dev/null
fi

echo "[5/7] bcrypt 版本自检..."
BCRYPT_VER=$(sudo docker exec equipment-backend pip show bcrypt 2>/dev/null | grep Version)
if echo "$BCRYPT_VER" | grep -q "5.0"; then
  echo "  降级 bcrypt 到 4.0.1..."
  sudo docker exec equipment-backend pip install "bcrypt==4.0.1" -q
  sudo docker restart equipment-backend
fi

echo "[6/7] 重启服务..."
sudo docker compose restart
sleep 5

echo "[7/7] 部署完成！"
echo ""
echo "访问地址: http://$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1):9000"
echo "默认账号: root / root123"
echo ""
echo "运维脚本:"
echo "  启动: sudo bash $APP_DIR/start.sh"
echo "  停止: sudo bash $APP_DIR/stop.sh"
echo "  备份: sudo bash $APP_DIR/backup.sh"
```

---

**文档版本**：v1.0
**生成日期**：2026-07-19
**适用系统版本**：设备信息动态管理系统 v1.1.2

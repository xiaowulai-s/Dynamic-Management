# 腾讯云服务器部署指南

本指南将帮助您在腾讯云服务器上部署设备信息动态管理系统。

## 📋 目录

1. [前期准备](#前期准备)
2. [服务器环境配置](#服务器环境配置)
3. [安装依赖](#安装依赖)
4. [部署项目](#部署项目)
5. [配置Nginx反向代理](#配置nginx反向代理)
6. [配置Systemd服务](#配置systemd服务)
7. [配置HTTPS（可选）](#配置https可选)
8. [验证部署](#验证部署)

---

## 前期准备

### 1. 购买腾讯云服务器

**推荐配置**:
- **CPU**: 2核+
- **内存**: 4GB+
- **系统盘**: 50GB SSD
- **带宽**: 5Mbps+
- **系统**: CentOS 7.9 / Ubuntu 22.04 LTS

**购买时注意**:
- 选择与您物理位置最近的区域（降低延迟）
- 建议开启DDoS防护（基础防护免费）

### 2. 配置安全组

登录腾讯云控制台 → 云服务器 → 安全组 → 配置规则：

**入站规则**:
| 协议 | 端口 | 来源 | 说明 |
|------|------|------|------|
| SSH | 22 | 您的IP | 远程管理（建议限制为您的IP） |
| HTTP | 80 | 0.0.0.0/0 | Web访问 |
| HTTPS | 443 | 0.0.0.0/0 | HTTPS访问（可选） |
| 后端API | 8000 | 仅服务器内部 | 不开放公网 |

### 3. 域名备案（可选但推荐）

如果使用域名访问：
1. 购买域名（腾讯云DNSPod）
2. 实名认证
3. ICP备案（中国大陆服务器必须备案）
4. 解析域名到服务器IP

---

## 服务器环境配置

### 方法一：使用腾讯云自动化脚本（推荐）

腾讯云提供了一键初始化脚本，可在购买服务器时选择"镜像市场" → "基础镜像" → "云服务器初始化脚本"。

### 方法二：手动配置

#### 1. 连接服务器

```bash
# Windows用户使用PuTTY或PowerShell
ssh root@您的服务器IP

# 首次登录需修改密码
passwd root
```

#### 2. 更新系统

**CentOS**:
```bash
yum update -y
yum install -y wget curl vim git
```

**Ubuntu**:
```bash
apt update && apt upgrade -y
apt install -y wget curl vim git ufw
```

---

## 安装依赖

### 1. 安装 Python 3.10+

```bash
# CentOS 7
yum install -y python310 python310-pip

# Ubuntu 22.04（自带Python 3.10）
apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version  # 应显示 Python 3.10.x
pip3 --version
```

### 2. 安装 Node.js 18+

```bash
# 使用 nvm 安装（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
nvm alias default 18

# 验证
node --version  # 应显示 v18.x.x
npm --version
```

### 3. 安装 PostgreSQL 15

```bash
# CentOS
yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
yum install -y postgresql15-server postgresql15
/usr/pgsql-15/bin/postgresql-15-setup initdb
systemctl enable --now postgresql-15

# Ubuntu
apt install -y postgresql postgresql-contrib

# 验证
systemctl status postgresql
```

**配置数据库**:
```bash
# 切换到 postgres 用户
su - postgres

# 进入 psql
psql

# 创建数据库和用户
CREATE DATABASE equipment_db;
CREATE USER equipment_user WITH PASSWORD '您的强密码';
GRANT ALL PRIVILEGES ON DATABASE equipment_db TO equipment_user;

# 退出
\q
exit
```

### 4. 安装 Redis

```bash
# CentOS
yum install -y redis
systemctl enable --now redis

# Ubuntu
apt install -y redis-server
systemctl enable --now redis

# 验证
redis-cli ping  # 应返回 PONG
```

### 5. 安装 Nginx

```bash
# CentOS
yum install -y epel-release
yum install -y nginx
systemctl enable --now nginx

# Ubuntu
apt install -y nginx
systemctl enable --now nginx

# 验证
systemctl status nginx
nginx -v  # 应显示 nginx/1.24.x
```

---

## 部署项目

### 1. 克隆代码

```bash
# 创建项目目录
mkdir -p /opt/equipment-management
cd /opt/equipment-management

# 克隆代码
git clone https://github.com/xiaowulai-s/Dynamic-Management.git .

# 如果是私有仓库，使用 SSH 或 Token
# git clone git@github.com:xiaowulai-s/Dynamic-Management.git
```

### 2. 配置环境变量

```bash
cd /opt/equipment-management/backend

# 复制环境配置模板
cp .env.example .env

# 编辑配置
vim .env
```

**修改以下配置**:
```env
# 数据库配置（使用刚才创建的数据库）
DATABASE_URL=postgresql://equipment_user:您的密码@localhost:5432/equipment_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT密钥（必须修改！）
SECRET_KEY=your-very-long-and-random-secret-key-change-this-in-production

# 上传文件目录
UPLOAD_DIR=/opt/equipment-management/backend/uploads

# 环境（生产环境设为 production）
ENV=production
```

**生成安全密钥**:
```bash
# Python生成随机密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用OpenSSL
openssl rand -base64 32
```

### 3. 安装Python依赖

```bash
cd /opt/equipment-management/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（使用国内镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 构建前端

```bash
cd /opt/equipment-management/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建完成后会在 `frontend/dist/` 生成静态文件。

### 5. 初始化数据库

```bash
cd /opt/equipment-management/backend

# 激活虚拟环境
source venv/bin/activate

# 创建数据库表
python3 -c "
from app.database import engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ 数据库表创建完成')
"

# 初始化默认数据（管理员账号、系统配置等）
python3 -c "
from app.database import SessionLocal
from app.models.user import User
from app.models.approval import ApprovalConfig, SystemConfig
from app.utils.auth import get_password_hash

db = SessionLocal()

# 创建管理员账号（如果不存在）
admin = db.query(User).filter(User.username == 'admin').first()
if not admin:
    admin = User(
        username='admin',
        password_hash=get_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    db.add(admin)
    print('✅ 管理员账号创建成功（admin/admin123）')

# 创建审批配置
log_types = ['installation', 'repair', 'scrap', 'inspection', 'maintenance', 'fault', 'parts', 'calibration']
for log_type in log_types:
    config = db.query(ApprovalConfig).filter(ApprovalConfig.log_type == log_type).first()
    if not config:
        config = ApprovalConfig(log_type=log_type, require_approval=True)
        db.add(config)
print(f'✅ 创建 {len(log_types)} 个日志类型的审批配置')

db.commit()
db.close()
print('✅ 初始化完成！')
"
```

---

## 配置Nginx反向代理

### 1. 创建Nginx配置文件

```bash
vim /etc/nginx/conf.d/equipment-management.conf
```

**CentOS配置**:
```nginx
server {
    listen 80;
    server_name 您的域名或服务器IP;  # 例如: example.com 或 123.45.67.89

    # 前端静态文件
    location / {
        root /opt/equipment-management/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 文件上传大小限制
        client_max_body_size 20M;

        # 超时设置（OCR识别可能需要较长时间）
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }

    # WebSocket支持（如果需要实时通信）
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Ubuntu配置**:
```bash
# 删除默认配置
rm /etc/nginx/sites-enabled/default

# 创建配置
vim /etc/nginx/sites-available/equipment-management
```

粘贴上述配置后：
```bash
# 创建软链接
ln -s /etc/nginx/sites-available/equipment-management /etc/nginx/sites-enabled/

# 测试配置
nginx -t
# 应显示：test is successful
```

### 2. 启动Nginx

```bash
systemctl enable --now nginx

# 如果修改了配置，重新加载
systemctl reload nginx
```

### 3. 配置防火墙

```bash
# CentOS 7（使用 firewalld）
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload

# Ubuntu（使用 ufw）
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

---

## 配置Systemd服务

创建后端服务守护进程，确保崩溃后自动重启。

### 1. 创建后端服务文件

```bash
vim /etc/systemd/system/equipment-backend.service
```

**内容**:
```ini
[Unit]
Description=Equipment Management Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/equipment-management/backend
Environment="PATH=/opt/equipment-management/backend/venv/bin"
ExecStart=/opt/equipment-management/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=equipment-backend

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### 2. 创建Celery Worker服务文件

```bash
vim /etc/systemd/system/equipment-celery.service
```

**内容**:
```ini
[Unit]
Description=Equipment Management Celery Worker
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/equipment-management/backend
Environment="PATH=/opt/equipment-management/backend/venv/bin"
ExecStart=/opt/equipment-management/backend/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=equipment-celery

[Install]
WantedBy=multi-user.target
```

### 3. 创建Celery Beat服务文件

```bash
vim /etc/systemd/system/equipment-celery-beat.service
```

**内容**:
```ini
[Unit]
Description=Equipment Management Celery Beat
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/equipment-management/backend
Environment="PATH=/opt/equipment-management/backend/venv/bin"
ExecStart=/opt/equipment-management/backend/venv/bin/celery -A app.tasks.celery_app beat --loglevel=info
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=equipment-celery-beat

[Install]
WantedBy=multi-user.target
```

### 4. 启动服务

```bash
# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动后端服务
systemctl enable --now equipment-backend

# 启用并启动Celery Worker
systemctl enable --now equipment-celery

# 启用并启动Celery Beat（定时任务）
systemctl enable --now equipment-celery-beat

# 查看服务状态
systemctl status equipment-backend
systemctl status equipment-celery
systemctl status equipment-celery-beat
```

### 5. 查看日志

```bash
# 后端日志
journalctl -u equipment-backend -f

# Celery日志
journalctl -u equipment-celery -f

# Celery Beat日志
journalctl -u equipment-celery-beat -f
```

---

## 配置HTTPS（可选但推荐）

使用Let's Encrypt免费SSL证书。

### 1. 安装Certbot

```bash
# CentOS
yum install -y certbot python3-certbot-nginx

# Ubuntu
apt install -y certbot python3-certbot-nginx
```

### 2. 申请证书

```bash
# 如果使用域名
certbot --nginx -d example.com -d www.example.com

# 按照提示输入邮箱、同意条款
# Certbot会自动配置Nginx
```

### 3. 自动续期

Certbot会自动配置定时任务续期，无需手动操作。

---

## 验证部署

### 1. 访问系统

打开浏览器访问：
- **HTTP**: http://您的服务器IP
- **HTTPS**: https://您的域名（如果配置了SSL）

### 2. 测试登录

使用默认管理员账号登录：
- **用户名**: `admin`
- **密码**: `admin123`

**⚠️ 首次登录后请立即修改密码！**

### 3. 检查各项功能

- [ ] 用户登录/登出
- [ ] 设备管理（添加/编辑/删除设备）
- [ ] 日志管理（提交日志）
- [ ] 统计分析（查看报表）
- [ ] 系统设置（审批配置、系统配置）
- [ ] 文件上传（测试上传功能）

### 4. 检查服务状态

```bash
# 检查所有服务
systemctl status nginx equipment-backend equipment-celery equipment-celery-beat postgresql redis

# 查看资源使用
top
htop  # 如果未安装：yum install -y htop / apt install -y htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

---

## 备份策略

### 1. 自动备份脚本

创建备份脚本 `/opt/equipment-management/backup.sh`:

```bash
#!/bin/bash

# 配置
BACKUP_DIR="/opt/backups/equipment-management"
DB_NAME="equipment_db"
DB_USER="equipment_user"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 备份上传的文件
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" /opt/equipment-management/backend/uploads

# 删除30天前的备份
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

echo "✅ 备份完成：$BACKUP_DIR"
```

添加执行权限并测试：
```bash
chmod +x /opt/equipment-management/backup.sh
/opt/equipment-management/backup.sh
```

### 2. 配置定时备份

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * /opt/equipment-management/backup.sh >> /var/log/backup.log 2>&1
```

---

## 性能优化

### 1. 启用Gzip压缩

编辑 `/etc/nginx/nginx.conf`，在 `http` 块中添加：

```nginx
gzip on;
gzip_min_length 1k;
gzip_comp_level 5;
gzip_types text/plain application/json application/javascript text/css;
```

重启Nginx：
```bash
systemctl reload nginx
```

### 2. 配置CDN（可选）

如果有域名，可配置腾讯云CDN加速：
1. 开通腾讯云CDN
2. 添加加速域名
3. 配置CNAME解析
4. 配置HTTPS

### 3. 数据库优化

```bash
# 编辑PostgreSQL配置
vim /var/lib/pgsql/15/data/postgresql.conf

# 推荐配置
shared_buffers = 256MB
work_mem = 16MB
maintenance_work_mem = 128MB
effective_cache_size = 1GB
```

重启PostgreSQL：
```bash
systemctl restart postgresql-15  # CentOS
systemctl restart postgresql     # Ubuntu
```

---

## 安全加固

### 1. 修改SSH端口

```bash
vim /etc/ssh/sshd_config

# 修改以下行
Port 2222  # 改为非常用端口
PermitRootLogin no  # 禁止root直接登录
PasswordAuthentication no  # 禁用密码登录（使用密钥登录）

# 重启SSH
systemctl restart sshd
```

### 2. 配置Fail2ban防暴力破解

```bash
# CentOS
yum install -y epel-release
yum install -y fail2ban

# Ubuntu
apt install -y fail2ban

# 启动
systemctl enable --now fail2ban
```

### 3. 定期更新系统

```bash
# 配置自动安全更新
# CentOS
yum install -y yum-cron
systemctl enable --now yum-cron

# Ubuntu
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

## 常见问题

### Q1: 服务启动失败

**检查日志**:
```bash
# 查看后端日志
journalctl -u equipment-backend -n 100

# 查看Nginx日志
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

**常见原因**:
- 数据库连接失败：检查PostgreSQL是否运行
- Redis连接失败：检查Redis是否运行
- 端口被占用：使用 `netstat -tlnp | grep 8000` 检查

### Q2: 上传文件失败

**检查目录权限**:
```bash
chmod 755 /opt/equipment-management/backend/uploads
chown -R root:root /opt/equipment-management/backend/uploads
```

### Q3: 502 Bad Gateway

**原因**: Nginx无法连接到后端

**解决**:
```bash
# 检查后端是否运行
systemctl status equipment-backend

# 检查端口监听
netstat -tlnp | grep 8000

# 重启后端
systemctl restart equipment-backend
```

### Q4: OCR识别失败

**原因**: PaddleOCR依赖库缺失

**解决**:
```bash
cd /opt/equipment-management/backend
source venv/bin/activate

# 重新安装OCR依赖
pip install paddleocr paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 监控与维护

### 1. 配置日志轮转

创建 `/etc/logrotate.d/equipment-management`:
```
/var/log/equipment/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 root root
    postrotate
        systemctl reload equipment-backend > /dev/null 2>&1 || true
    endscript
}
```

### 2. 监控告警

推荐使用腾讯云自带监控：
- 云监控（Cloud Monitor）
- 配置CPU、内存、磁盘告警
- 配置服务可用性监控

### 3. 定期维护

**每周**:
```bash
# 清理日志
find /var/log -name "*.log.*" -mtime +7 -delete

# 清理临时文件
find /tmp -type f -mtime +7 -delete
```

**每月**:
```bash
# 更新系统
yum update -y  # CentOS
apt upgrade -y  # Ubuntu

# 重启服务
systemctl restart equipment-backend equipment-celery equipment-celery-beat
```

---

## 技术支持

- 项目文档：https://github.com/xiaowulai-s/Dynamic-Management
- 问题反馈：https://github.com/xiaowulai-s/Dynamic-Management/issues
- 邮箱：2557783035@qq.com

---

## 下一步

部署完成后：

1. ✅ **立即修改管理员密码**
2. ✅ **配置域名解析**（如果有域名）
3. ✅ **配置HTTPS**（使用Certbot）
4. ✅ **设置自动备份**
5. ✅ **配置监控告警**
6. ✅ **邀请用户开始使用**

祝部署顺利！🎉

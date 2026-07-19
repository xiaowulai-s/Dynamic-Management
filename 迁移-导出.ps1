# 迁移导出工具 - 设备信息动态管理系统
# 在【当前服务器】运行，导出数据供新服务器使用
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  迁移导出工具 - 设备信息动态管理系统" -ForegroundColor Cyan
Write-Host "  在当前服务器运行，导出数据供新服务器使用" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Docker 未运行，请先启动 Docker Desktop" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查 postgres 容器
$containers = docker ps --format "{{.Names}}" 2>&1
if ($containers -notcontains 'equipment-postgres') {
    Write-Host "[错误] equipment-postgres 容器未运行，请先启动系统" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

$exportDir = "迁移包"
$ts = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "[1/5] 创建导出目录..." -ForegroundColor Yellow
if (Test-Path $exportDir) { Remove-Item -Recurse -Force $exportDir }
New-Item -ItemType Directory -Path $exportDir | Out-Null
New-Item -ItemType Directory -Path "$exportDir\data" | Out-Null
Write-Host "      目录已创建: $exportDir"
Write-Host ""

Write-Host "[2/5] 导出数据库数据 (pg_dump)..." -ForegroundColor Yellow
docker exec equipment-postgres pg_dump -U postgres -d equipment_db -Fc -f /tmp/dump.pgc
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 数据库导出失败" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
docker cp equipment-postgres:/tmp/dump.pgc "$exportDir\data\equipment_db.dump"
docker exec equipment-postgres rm /tmp/dump.pgc
$dumpSize = [math]::Round((Get-Item "$exportDir\data\equipment_db.dump").Length / 1MB, 2)
Write-Host "      数据库已导出: data\equipment_db.dump ($dumpSize MB)"
Write-Host ""

Write-Host "[3/5] 打包上传文件 (uploads)..." -ForegroundColor Yellow
if (Test-Path "uploads") {
    $uploadFiles = Get-ChildItem "uploads" -Recurse -File | Where-Object { $_.Name -ne '.gitkeep' }
    if ($uploadFiles.Count -gt 0) {
        Write-Host "      正在打包 uploads 目录..."
        Compress-Archive -Path "uploads\*" -DestinationPath "$exportDir\data\uploads.zip" -Force
        if (Test-Path "$exportDir\data\uploads.zip") {
            $zipSize = [math]::Round((Get-Item "$exportDir\data\uploads.zip").Length / 1MB, 2)
            Write-Host "      上传文件已打包: data\uploads.zip ($zipSize MB)"
        } else {
            Write-Host "      [提示] uploads 打包失败，跳过" -ForegroundColor DarkYellow
        }
    } else {
        Write-Host "      [提示] uploads 目录为空，跳过" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "      [提示] uploads 目录不存在，跳过" -ForegroundColor DarkYellow
}
Write-Host ""

Write-Host "[4/5] 复制部署必需文件..." -ForegroundColor Yellow
Copy-Item "docker-compose.yml" $exportDir
Copy-Item "nginx.prod.conf" $exportDir
Copy-Item "启动系统.bat" $exportDir -ErrorAction SilentlyContinue
Copy-Item "更新前端.bat" $exportDir -ErrorAction SilentlyContinue
Copy-Item "停止服务.bat" $exportDir -ErrorAction SilentlyContinue
# 迁移导入脚本（新服务器部署用）
Copy-Item "迁移-导入.ps1" $exportDir -ErrorAction SilentlyContinue
# 后端代码
Copy-Item "backend" "$exportDir\backend" -Recurse -Force
# 前端源码（新机器需要重新构建）
Copy-Item "frontend\src" "$exportDir\frontend\src" -Recurse -Force
Copy-Item "frontend\index.html" "$exportDir\frontend\" -Force
Copy-Item "frontend\package.json" "$exportDir\frontend\" -Force
Copy-Item "frontend\package-lock.json" "$exportDir\frontend\" -Force -ErrorAction SilentlyContinue
Copy-Item "frontend\tsconfig.json" "$exportDir\frontend\" -Force
Copy-Item "frontend\vite.config.ts" "$exportDir\frontend\" -Force
# 已构建的前端产物（可选，省去新机器装 Node.js）
if (Test-Path "frontend\dist") {
    Write-Host "      复制前端构建产物 dist..."
    Copy-Item "frontend\dist" "$exportDir\frontend\dist" -Recurse -Force
}
Write-Host "      代码与配置已复制"
Write-Host ""

Write-Host "[5/5] 生成迁移说明..." -ForegroundColor Yellow
$readme = @"
# 设备信息动态管理系统 - 迁移包

## 导出时间
$ts

## 包含内容
- data\equipment_db.dump  数据库备份（PostgreSQL 自定义格式）
- data\uploads.zip        上传文件压缩包
- docker-compose.yml      服务编排配置
- nginx.prod.conf         Nginx 配置
- backend\                后端代码（含 Dockerfile）
- frontend\               前端源码 + 已构建产物 dist
- 迁移-导入.ps1           新服务器部署脚本
- 启动系统.bat            启动脚本
- 更新前端.bat            前端构建脚本
- 停止服务.bat            停止脚本

## 在新服务器上的部署步骤
1. 安装 Docker Desktop for Windows 并启动（托盘图标变绿）
2. 将整个"迁移包"文件夹拷贝到新服务器（建议 D:\Dynamic-Management，路径不含中文空格）
3. 在迁移包根目录右键"迁移-导入.ps1" → 用 PowerShell 运行
4. 等待部署完成（首次约 5-15 分钟，需拉取 Docker 镜像）
5. 浏览器访问 http://新服务器IP:9000 （首次用 Ctrl+F5 强制刷新）

## 默认账号
- root / root123        （超级管理员）
- admin_test / 123456   （管理员）
- user_test / 123456    （普通用户）

## 部署后验证清单
- [ ] 登录页标题显示"设备信息动态管理系统"
- [ ] root 登录后侧边栏角色显示"超级管理员"
- [ ] 仪表盘统计数据与原服务器一致
- [ ] 设备/日志/用户列表数量一致
- [ ] 新建日志可提交，审批流程正常

## 常见问题
- 镜像拉取慢：配置 Docker 镜像加速器（阿里云/腾讯云）
- 页面空白：Ctrl+F5 强制刷新，或检查 nginx 容器是否运行
- 401 反复刷新：清除浏览器 localStorage 后重新登录
- 修改端口：编辑 docker-compose.yml 的 nginx.ports 配置

## 备注
- 前端 dist 已包含在包内，新服务器无需安装 Node.js 即可访问
- 如需修改前端，安装 Node.js 18+ 后运行"更新前端.bat"重新构建
- 完整迁移指南见项目 docs\迁移部署指南.md
"@
$readme | Out-File -FilePath "$exportDir\迁移说明.md" -Encoding UTF8
Write-Host "      说明文档已生成: 迁移说明.md"
Write-Host ""

$totalSize = [math]::Round((Get-ChildItem -Recurse $exportDir | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  导出完成！" -ForegroundColor Green
Write-Host ""
Write-Host "  迁移包位置: $((Get-Location).Path)\$exportDir" -ForegroundColor White
Write-Host "  迁移包总大小: $totalSize MB" -ForegroundColor White
Write-Host ""
Write-Host "  下一步:" -ForegroundColor Yellow
Write-Host "  1. 将整个 '$exportDir' 文件夹拷贝到新服务器" -ForegroundColor White
Write-Host "  2. 在新服务器上运行 迁移-导入.ps1" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Read-Host "按回车键退出"

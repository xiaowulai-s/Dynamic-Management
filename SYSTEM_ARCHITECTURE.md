# 📐 系统架构文档

## 设备信息动态管理系统

**版本**: v1.1.1
**更新日期**: 2026-07-18

---

## 📋 目录

1. [系统概述](#系统概述)
2. [技术架构](#技术架构)
3. [后端架构](#后端架构)
4. [前端架构](#前端架构)
5. [系统架构图](#系统架构图)
6. [数据流](#数据流)
7. [核心业务流程](#核心业务流程)
8. [数据库设计](#数据库设计)
9. [API 设计](#api-设计)
10. [部署架构](#部署架构)

---

## 系统概述

### 项目简介

**设备信息动态管理系统** 是一个基于 FastAPI + Vue 3 的工业机械设备全生命周期管理系统，用于管理设备从安装、运行、维修到报废的全过程。

### 核心功能

- ✅ **账号与权限**: 双预设账号、三级角色权限、登录安全
- ✅ **设备管理**: 设备档案、状态跟踪、生命周期管理
- ✅ **日志管理**: 8 种日志类型、审批流程、时间线展示
- ✅ **统计分析**: 故障率趋势、成本分析、可视化报表
- ✅ **系统管理**: 用户管理、审批配置、审计日志、数据备份

### 业务价值

- 📊 **提高设备利用率**: 实时跟踪设备状态，减少停机时间
- 💰 **降低维护成本**: 预防性维护，减少突发故障
- 📈 **数据驱动决策**: 统计分析支持管理决策
- 🔒 **安全可控**: 权限管理，操作审计

---

## 技术架构

### 整体架构模式

```
┌─────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                  │
│  Vue 3 + TypeScript + Element Plus + Pinia          │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/REST API
                      ↓
┌─────────────────────────────────────────────────────┐
│                    网关层 (Gateway)                  │
│              Nginx (反向代理 + 静态文件)              │
└─────────────────────┬───────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────┐
│                    应用层 (Backend)                   │
│  FastAPI + Python 3.11 + SQLAlchemy ORM             │
└──────────┬──────────────┬──────────────┬────────────┘
           │              │              │
           ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │    Redis     │ │   Celery     │
│   (数据库)   │ │  (缓存/队列)  │ │  (异步任务)   │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 技术栈总览

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端框架** | Vue 3 | 3.3.9 | 渐进式 JavaScript 框架 |
| **前端语言** | TypeScript | 5.2.0 | 类型安全 |
| **UI 组件库** | Element Plus | 2.4.4 | 企业级 UI 组件 |
| **状态管理** | Pinia | 2.1.7 | 轻量级状态管理 |
| **路由** | Vue Router | 4.2.5 | 前端路由 |
| **HTTP 客户端** | Axios | 1.6.2 | HTTP 请求 |
| **图表库** | ECharts | 5.4.3 | 数据可视化 |
| **构建工具** | Vite | 5.0.4 | 前端构建 |
| **后端框架** | FastAPI | 0.104.1 | 现代 Python Web 框架 |
| **后端语言** | Python | 3.11 | 编程语言 |
| **ORM** | SQLAlchemy | 2.0.23 | 数据库 ORM |
| **数据库** | PostgreSQL | 15 | 关系型数据库 |
| **缓存** | Redis | 7 | 缓存和消息队列 |
| **任务队列** | Celery | 5.3.4 | 异步任务处理 |
| **认证** | JWT + bcrypt | - | 身份认证 |
| **API 文档** | Swagger UI | - | 自动生成 API 文档 |
| **部署** | Docker | 29.6.1 | 容器化部署 |
| **编排** | Docker Compose | v5.3.0 | 多容器管理 |
| **反向代理** | Nginx | Alpine | 静态文件服务 |

---

## 后端架构

### 后端架构图

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Application                    │
│                   (app/main.py)                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   认证模块    │  │   设备模块    │  │   日志模块    │  │
│  │  (auth.py)   │  │(equipment.py)│  │  (logs.py)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  统计分析模块  │  │  系统设置模块  │  │  其他模块    │  │
│  │(analytics.py)│  │(settings.py) │  │(upload, etc) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
           ↓                    ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Pydantic 模型    │  │  SQLAlchemy ORM   │  │  工具函数          │
│  (数据验证)       │  │  (数据库操作)      │  │  (auth, export)   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### 后端目录结构

```
backend/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # 数据模型
│   │   ├── user.py            # 用户模型
│   │   ├── equipment.py       # 设备模型
│   │   ├── logs.py            # 日志模型（8种类型）
│   │   ├── approval.py        # 审批配置模型
│   │   ├── customer.py        # 客户模型
│   │   ├── feedback.py        # 反馈模型
│   │   ├── notification.py    # 通知模型
│   │   └── audit.py           # 审计日志模型
│   ├── routers/                # API 路由
│   │   ├── auth.py            # 认证接口（登录/注册）
│   │   ├── equipment.py       # 设备管理接口
│   │   ├── logs.py            # 日志管理接口（8种类型）
│   │   ├── upload.py          # 文件上传接口
│   │   ├── analytics.py       # 统计分析接口
│   │   ├── settings.py        # 系统设置接口
│   │   ├── customers.py       # 客户管理接口
│   │   ├── feedback.py        # 用户反馈接口
│   │   ├── audit.py           # 审计日志接口
│   │   ├── backup.py          # 数据备份接口
│   │   ├── notifications.py   # 通知管理接口
│   │   ├── csv_io.py          # CSV 导入导出
│   │   └── export.py          # 报表导出
│   ├── tasks/                  # Celery 异步任务
│   │   ├── celery_app.py      # Celery 配置
│   │   ├── ocr_tasks.py       # OCR 识别任务
│   │   └── reminder_tasks.py  # 定时提醒任务
│   └── utils/                  # 工具函数
│       ├── auth.py            # JWT 认证和权限
│       ├── file_utils.py      # 文件处理工具
│       └── export_utils.py    # 导出工具
├── requirements.txt            # Python 依赖
├── Dockerfile                  # Docker 镜像配置
├── init.sql                    # 数据库初始化脚本
└── .env.example                # 环境变量模板
```

### 后端核心模块

#### 1. 认证模块 (`auth.py`)

**功能**:
- 用户注册
- 用户登录（JWT Token）
- 密码修改
- Token 刷新
- 用户信息查询

**API 端点**:
```
POST   /api/auth/register          # 注册
POST   /api/auth/login             # 登录
POST   /api/auth/change-password   # 修改密码
GET    /api/auth/me                # 当前用户信息
POST   /api/auth/test-login         # 测试登录
```

**安全特性**:
- ✅ 密码 bcrypt 哈希存储
- ✅ JWT Token 认证（30 分钟过期）
- ✅ 角色权限验证（admin/user）
- ✅ 登录失败锁定机制（5 次失败后锁定）

#### 2. 设备管理模块 (`equipment.py`)

**功能**:
- 设备 CRUD 操作
- 设备编号唯一性验证
- 设备状态管理（4 种状态）
- 设备搜索和筛选
- 设备详情统计

**设备状态**:
- `running` - 运行中
- `stopped` - 停机
- `repairing` - 维修中
- `scrapped` - 报废

**生命周期状态**:
- `active` - 在用
- `maintenance` - 保养中
- `scrapped` - 已报废

**API 端点**:
```
GET    /api/equipment              # 设备列表
POST   /api/equipment              # 创建设备
GET    /api/equipment/{id}         # 设备详情
PUT    /api/equipment/{id}         # 更新设备
DELETE /api/equipment/{id}         # 删除设备
GET    /api/equipment/{id}/logs    # 设备日志
GET    /api/equipment/stats        # 设备统计
```

#### 3. 日志管理模块 (`logs.py`)

**8 种日志类型**:

| 日志类型 | 枚举值 | 特有字段 |
|---------|--------|---------|
| 设备安装 | `installation` | 安装日期、安装人员、位置、验收状态 |
| 设备维修 | `repair` | 维修日期、故障描述、解决方案、费用、时长 |
| 设备报废 | `scrap` | 报废日期、报废原因、残值 |
| 日常巡检 | `inspection` | 巡检日期、巡检人员、巡检项目、结果 |
| 保养记录 | `maintenance` | 保养日期、保养项目、下次保养日期 |
| 故障报修 | `fault` | 故障时间、故障等级、报修人、处理状态 |
| 配件更换 | `parts` | 更换日期、配件名称、配件编号、数量、费用 |
| 校准记录 | `calibration` | 校准日期、校准机构、校准结果、下次校准日期 |

**审批流程**:
- `pending` - 待审批
- `approved` - 已通过
- `rejected` - 已驳回

**API 端点**:
```
GET    /api/logs                        # 日志列表
POST   /api/logs                        # 创建日志
GET    /api/logs/{id}                   # 日志详情
PUT    /api/logs/{id}/approve           # 审批通过
PUT    /api/logs/{id}/reject            # 驳回日志
GET    /api/logs/types                  # 日志类型
GET    /api/logs/timeline/{equipment_id} # 设备日志时间线
```

#### 4. 统计分析模块 (`analytics.py`)

**统计功能**:
- 设备状态分布
- 日志类型统计
- 故障率趋势（日/周/月）
- 维修成本分析
- 维修频率排名
- 保养计划提醒
- 配件消耗统计

**API 端点**:
```
GET /api/analytics/dashboard        # 仪表盘统计
GET /api/analytics/equipment-status  # 设备状态分布
GET /api/analytics/log-statistics   # 日志统计
GET /api/analytics/fault-rate       # 故障率趋势
GET /api/analytics/cost-analysis    # 成本分析
GET /api/analytics/repair-frequency  # 维修频率
GET /api/analytics/maintenance-plan  # 保养计划
GET /api/analytics/parts-consumption # 配件消耗
```

### 后端中间件

#### 1. CORS 中间件

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. 请求日志中间件

记录每个请求的处理时间，添加到响应头 `X-Process-Time`

#### 3. 全局异常处理

统一处理异常，返回友好的错误信息

### 后端安全特性

- ✅ **密码安全**: bcrypt 哈希，不可逆
- ✅ **JWT Token**: 无状态认证，30 分钟过期
- ✅ **权限控制**: 基于角色的访问控制（RBAC）
- ✅ **SQL 注入防护**: ORM 自动转义
- ✅ **XSS 防护**: 前端自动转义
- ✅ **登录锁定**: 5 次失败后渐进式锁定

---

## 前端架构

### 前端架构图

```
┌─────────────────────────────────────────────────────────┐
│                    App.vue (根组件)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│                  Layout.vue (主布局)                     │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────┐│
│  │  侧边栏导航    │  │   内容区域          │  │  顶部栏      ││
│  │ (菜单项)     │  │  (路由视图)         │  │ (用户信息)   ││
│  └─────────────┘  └──────────────────┘  └─────────────┘│
└─────────────────────┬───────────────────────────────────┘
                      │ Router View
                      ↓
        ┌───────────────────────────────┐
        │   Views (页面组件)              │
        ├───────────────────────────────┤
        │  Login.vue      Dashboard.vue │
        │  Equipment.vue  Logs.vue      │
        │  Analytics.vue  Settings.vue  │
        └───────────────────────────────┘
                      │
                      ↓
        ┌───────────────────────────────┐
        │   Composables (组合式函数)       │
        ├───────────────────────────────┤
        │  useTheme.ts   useAuth.ts      │
        └───────────────────────────────┘
                      │
                      ↓
        ┌───────────────────────────────┐
        │   Stores (状态管理)              │
        ├───────────────────────────────┤
        │  user.ts   equipment.ts        │
        └───────────────────────────────┘
                      │
                      ↓
        ┌───────────────────────────────┐
        │   API (数据请求)                 │
        ├───────────────────────────────┤
        │  auth.ts   equipment.ts        │
        │  logs.ts   analytics.ts        │
        └───────────────────────────────┘
                      │
                      ↓
        ┌───────────────────────────────┐
        │   Axios (HTTP 客户端)            │
        └───────────────────────────────┘
```

### 前端目录结构

```
frontend/
├── src/
│   ├── main.ts                # 应用入口
│   ├── App.vue                # 根组件
│   ├── api/                   # API 接口
│   │   ├── request.ts         # Axios 封装
│   │   ├── auth.ts            # 认证接口
│   │   ├── equipment.ts       # 设备接口
│   │   ├── logs.ts            # 日志接口
│   │   └── index.ts           # 接口统一导出
│   ├── components/            # 公共组件
│   │   ├── NotificationList.vue
│   │   ├── NotificationsPopover.vue
│   │   └── ThemeToggle.vue
│   ├── composables/           # 组合式函数
│   │   └── useTheme.ts
│   ├── router/                # 路由配置
│   │   └── index.ts
│   ├── stores/                # Pinia 状态管理
│   │   └── user.ts
│   ├── styles/                # 全局样式
│   │   ├── index.css
│   │   ├── design-tokens.css
│   │   ├── components/
│   │   └── pages.css
│   ├── types/                 # TypeScript 类型
│   │   └── index.ts
│   ├── utils/                 # 工具函数
│   │   └── echarts-theme.ts
│   └── views/                 # 页面组件（17个）
│       ├── Login.vue          # 登录页
│       ├── Register.vue       # 注册页
│       ├── Layout.vue         # 主布局
│       ├── Dashboard.vue      # 仪表盘
│       ├── Equipment.vue      # 设备管理
│       ├── Logs.vue           # 日志管理
│       ├── LogDetail.vue      # 日志详情
│       ├── EquipmentLogs.vue  # 设备日志
│       ├── Analytics.vue      # 统计分析
│       ├── Settings.vue       # 系统设置
│       ├── Upload.vue         # 批量上传
│       ├── UserManage.vue     # 用户管理
│       ├── Profile.vue        # 个人资料
│       ├── Customers.vue      # 客户管理
│       ├── Feedback.vue       # 用户反馈
│       ├── AuditLog.vue       # 审计日志
│       ├── Notifications.vue  # 通知中心
│       └── NotFound.vue       # 404 页面
├── package.json               # 依赖配置
├── vite.config.ts             # Vite 配置
├── tsconfig.json              # TypeScript 配置
└── index.html                 # HTML 入口
```

### 前端核心模块

#### 1. 路由模块 (`router/index.ts`)

**路由配置**:
```typescript
{
  path: '/',
  component: Layout,
  children: [
    { path: 'dashboard', name: 'Dashboard', component: Dashboard },
    { path: 'equipment', name: 'Equipment', component: Equipment },
    { path: 'logs', name: 'Logs', component: Logs },
    { path: 'analytics', name: 'Analytics', component: Analytics },
    { path: 'settings', name: 'Settings', component: Settings },
    { path: 'upload', name: 'Upload', component: Upload },
    { path: 'profile', name: 'Profile', component: Profile },
    { path: 'logs/:id', name: 'LogDetail', component: LogDetail },
    { path: 'notifications', name: 'Notifications', component: Notifications },
  ]
}
```

**路由守卫**:
- 检查认证状态
- 未认证自动跳转到登录页
- 动态设置页面标题

#### 2. 状态管理 (`stores/user.ts`)

**用户状态**:
```typescript
interface UserState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  permissions: string[]
}
```

**核心方法**:
- `login()` - 用户登录
- `logout()` - 用户登出
- `init()` - 初始化认证状态
- `checkPermission()` - 权限检查

#### 3. API 请求封装 (`api/request.ts`)

**特性**:
- ✅ 请求拦截器：自动添加 Token
- ✅ 响应拦截器：统一错误处理
- ✅ Token 过期自动跳转登录
- ✅ 请求/响应日志

```typescript
// 请求配置
const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use((config) => {
  const token = userStore.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      userStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 前端页面清单

| 页面 | 路径 | 功能 | 访问权限 |
|------|------|------|---------|
| 登录页 | `/login` | 用户登录 | 所有人 |
| 注册页 | `/register` | 用户注册（已禁用） | 超级管理员 |
| 仪表盘 | `/dashboard` | 统计卡片、图表、待审批列表 | 所有用户 |
| 设备管理 | `/equipment` | 设备 CRUD、搜索筛选 | 所有用户 |
| 日志管理 | `/logs` | 日志列表、创建、审批 | 所有用户 |
| 日志详情 | `/logs/:id` | 日志详情、审批弹窗 | 所有用户 |
| 设备日志 | `/equipment/:id/logs` | 设备日志时间线 | 所有用户 |
| 统计分析 | `/analytics` | 多维度报表、图表 | 所有用户 |
| 系统设置 | `/settings` | 审批配置、系统参数 | 管理员 |
| 批量上传 | `/upload` | 批量文件上传 | 所有用户 |
| 用户管理 | `/user-manage` | 用户 CRUD、角色管理 | 超级管理员 |
| 个人资料 | `/profile` | 个人信息、修改密码 | 所有用户 |
| 客户管理 | `/customers` | 客户 CRUD、设备统计 | 管理员 |
| 用户反馈 | `/feedback` | 反馈提交、回复管理 | 所有用户 |
| 审计日志 | `/audit-log` | 操作审计记录 | 管理员 |
| 通知中心 | `/notifications` | 通知列表、标记已读 | 所有用户 |
| 404 页面 | `/*` | 页面未找到 | 所有人 |

### 前端 UI 特性

- ✅ **响应式设计**: 支持 PC、平板、手机
- ✅ **深色模式**: 已实现但默认隐藏
- ✅ **加载状态**: 统一的 loading 动画
- ✅ **错误提示**: 统一的错误处理
- ✅ **表单验证**: 实时验证 + 提交验证
- ✅ **分页功能**: 所有列表支持分页
- ✅ **搜索筛选**: 多条件搜索和筛选
- ✅ **图表可视化**: ECharts 图表
- ✅ **状态标签**: 彩色标签区分状态

---

## 系统架构图

### 完整系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层 (Client Layer)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   PC 浏览器    │  │  平板浏览器   │  │  手机浏览器   │         │
│  │  Chrome/Edge │  │  Safari      │  │  Mobile      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/HTTPS
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend Layer)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Vue 3 + TypeScript + Element Plus            │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │
│  │  │  登录页      │  │  仪表盘      │  │  设备管理    │        │  │
│  │  └────────────┘  └────────────┘  └────────────┘        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │  │
│  │  │  日志管理    │  │  统计分析    │  │  系统设置    │        │  │
│  │  └────────────┘  └────────────┘  └────────────┘        │  │
│  │                                                          │  │
│  │  状态管理: Pinia   路由: Vue Router   图表: ECharts     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ REST API (JSON)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      网关层 (Gateway Layer)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      Nginx (反向代理)                      │  │
│  │  - 静态文件服务    - 反向代理    - 负载均衡（可选）         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      应用层 (Application Layer)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           FastAPI (Python 3.11 + ASGI 服务器)             │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ 认证模块     设备模块     日志模块     统计分析      │  │  │
│  │  │   ↓           ↓           ↓           ↓            │  │  │
│  │  │ JWT验证     SQLAlchemy   审批流程     ECharts数据    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  中间件: CORS | 认证 | 日志 | 异常处理                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────┬──────────────────────┬──────────────────┬───────────┘
           │                      │                  │
           ↓                      ↓                  ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │     Redis        │  │    Celery        │
│    (数据库)       │  │   (缓存/队列)     │  │   (异步任务)      │
│                  │  │                  │  │                  │
│  - users         │  │  - 会话缓存       │  │  - OCR 识别      │
│  - equipment     │  │  - 验证码         │  │  - 定时提醒       │
│  - logs          │  │  - 消息队列       │  │  - 数据导出       │
│  - ... (15张表)  │  │                  │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 数据流

### 1. 用户登录流程

```
┌──────────┐     1. 输入账号密码      ┌──────────┐
│  用户     │ ──────────────────────→ │  前端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 2. POST /api/auth/login
                                               ↓
┌──────────┐     3. 验证账号密码       ┌──────────┐
│  用户     │ ←────────────────────── │  后端     │
└──────────┘     4. 返回 JWT Token     └──────────┘
                                               │
                                               │ 5. 存储 Token
                                               ↓
┌──────────┐     6. 跳转到仪表盘        ┌──────────┐
│  用户     │ ←────────────────────── │  前端     │
└──────────┘                           └──────────┘
```

### 2. 创建设备流程

```
┌──────────┐     1. 填写设备表单       ┌──────────┐
│  用户     │ ──────────────────────→ │  前端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 2. POST /api/equipment (Bearer Token)
                                               ↓
┌──────────┐     3. 验证 Token         ┌──────────┐
│  用户     │     4. 验证数据           │  后端     │
└──────────┘     5. 保存到数据库        └──────────┘
                                               │
                                               │ 6. 返回设备信息
                                               ↓
┌──────────┐     7. 更新设备列表        ┌──────────┐
│  用户     │ ←────────────────────── │  前端     │
└──────────┘                           └──────────┘
```

### 3. 提交日志+审批流程

```
┌──────────┐     1. 选择日志类型        ┌──────────┐
│  用户     │ ──────────────────────→ │  前端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 2. POST /api/logs
                                               ↓
┌──────────┐     3. 验证设备存在        ┌──────────┐
│  用户     │     4. 检查是否需要审批    │  后端     │
└──────────┘     5. 保存日志            └──────────┘
                                               │
                                               │ 6. 返回日志信息
                                               ↓
┌──────────┐     7. 显示日志状态        ┌──────────┐
│  用户     │ ←────────────────────── │  前端     │
└──────────┘   (待审批/已通过)          └──────────┘
                                               │
                                               │ 8. (如果需要审批)
                                               ↓
┌──────────┐     9. 管理员审批          ┌──────────┐
│  管理员   │ ──────────────────────→ │  后端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 10. 更新日志状态
                                               ↓
┌──────────┐     11. 通知提交人         ┌──────────┐
│  用户     │ ←────────────────────── │  前端     │
└──────────┘   (审批通过/驳回)          └──────────┘
```

### 4. 统计数据查询流程

```
┌──────────┐     1. 请求仪表盘          ┌──────────┐
│  用户     │ ──────────────────────→ │  前端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 2. GET /api/analytics/dashboard
                                               ↓
┌──────────┐     3. 查询设备总数        ┌──────────┐
│  PostgreSQL│ ←────────────────────── │  后端     │
│          │     4. 查询日志统计        └──────────┘
│          │     5. 查询故障率
│          │     6. 聚合统计数据
└──────────┘
                                               │
                                               │ 7. 返回统计数据
                                               ↓
┌──────────┐     8. 渲染图表            ┌──────────┐
│  用户     │ ←────────────────────── │  前端     │
└──────────┘   (ECharts 图表)          └──────────┘
```

### 5. 文件上传流程

```
┌──────────┐     1. 选择文件            ┌──────────┐
│  用户     │ ──────────────────────→ │  前端     │
└──────────┘                          └──────────┘
                                               │
                                               │ 2. POST /api/upload (multipart/form-data)
                                               ↓
┌──────────┐     3. 验证文件格式        ┌──────────┐
│  后端     │     4. 保存到本地          └──────────┘
└──────────┘     5. 返回文件路径
                       │
                       │ 6. 保存文件路径到数据库
                       ↓
              ┌──────────┐     7. 返回成功    ┌──────────┐
              │ PostgreSQL│ ←──────────────────│  后端     │
              └──────────┘                     └──────────┘
```

### 6. 数据流总结

```
┌─────────────────────────────────────────────────────────┐
│                      数据流向总图                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  用户操作 → 前端表单 → API 请求 → 后端验证 → 数据库操作  │
│     ↑                                              ↓      │
│     └──────────── 响应数据 ← 返回结果 ←─────────────┘      │
│                                                           │
│  异步任务:                                                   │
│  用户提交 → 创建任务 → Celery 队列 → Worker 执行 → 存储结果  │
│     ↑                                                      │
│     └──────────── 查询任务状态 ← 前端轮询 ←────────────┘      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 核心业务流程

### 1. 设备全生命周期流程

```
设备创建 → 安装 → 运行 → 巡检 → 维修 → 保养 → 报废
   ↓         ↓      ↓      ↓      ↓      ↓      ↓
 管理员创建  安装日志  运行中  巡检日志  维修日志  保养记录  报废日志
```

### 2. 日志审批流程

```
创建日志 → 检查审批配置 → 需要审批? → 是 → 状态=待审批
                                      ↓
                                  管理员审批 → 通过/驳回
                                      ↓
                                  更新日志状态 → 通知提交人
```

### 3. 用户权限流程

```
登录 → 验证身份 → 获取角色 → 权限检查 → 显示对应菜单/功能
```

---

## 数据库设计

### 数据表清单（15张）

| 表名 | 说明 | 主要字段 | 关联 |
|------|------|---------|------|
| users | 用户表 | id, username, password_hash, role, is_active | - |
| equipment | 设备表 | id, code, name, model, status, lifecycle_status | users |
| logs | 日志基础表 | id, equipment_id, log_type, status, operator_id | equipment, users |
| installation_logs | 安装日志 | id, installation_date, installer, location | logs |
| repair_logs | 维修日志 | id, repair_date, fault_description, cost, repair_time | logs |
| scrap_logs | 报废日志 | id, scrap_date, scrap_reason, residual_value | logs |
| inspection_logs | 巡检日志 | id, inspection_date, inspector, result | logs |
| maintenance_records | 保养记录 | id, maintenance_date, maintenance_items, next_maintenance_date | logs |
| fault_reports | 故障报修 | id, fault_date, fault_level, reporter, handle_status | logs |
| parts_replacement_logs | 配件更换日志 | id, parts_name, quantity, cost | logs |
| calibration_logs | 校准记录 | id, calibration_date, calibration_org, calibration_result | logs |
| approval_configs | 审批配置 | id, log_type, require_approval | - |
| system_configs | 系统配置 | id, config_key, config_value | - |
| audit_logs | 审计日志 | id, user_id, action, resource_type, details | users |
| notifications | 通知表 | id, user_id, title, content, is_read | users, equipment |

### 数据库关系图

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  users   │────────→│  logs    │────────→│equipment│
└──────────┘         └──────────┘         └──────────┘
     │                     │                     │
     │                     │                     │
     ↓                     ↓                     ↓
┌──────────┐         ┌──────────┐         ┌──────────┐
│audit_logs│         │8种日志表  │         │logs      │
└──────────┘         │(继承logs)│         │(关联)    │
                     └──────────┘         └──────────┘

┌──────────┐         ┌──────────┐
│approval_ │         │system_   │
│configs   │         │configs   │
└──────────┘         └──────────┘
```

---

## API 设计

### RESTful API 规范

**基础 URL**: `/api`

**认证方式**: Bearer Token (JWT)

**请求格式**: JSON

**响应格式**: JSON

### API 端点汇总

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| **认证** | `/api/auth/register` | POST | 用户注册 |
| | `/api/auth/login` | POST | 用户登录 |
| | `/api/auth/change-password` | POST | 修改密码 |
| | `/api/auth/me` | GET | 当前用户信息 |
| **设备** | `/api/equipment` | GET | 设备列表 |
| | `/api/equipment` | POST | 创建设备 |
| | `/api/equipment/{id}` | GET | 设备详情 |
| | `/api/equipment/{id}` | PUT | 更新设备 |
| | `/api/equipment/{id}` | DELETE | 删除设备 |
| | `/api/equipment/{id}/logs` | GET | 设备日志 |
| **日志** | `/api/logs` | GET | 日志列表 |
| | `/api/logs` | POST | 创建日志 |
| | `/api/logs/{id}` | GET | 日志详情 |
| | `/api/logs/{id}/approve` | PUT | 审批通过 |
| | `/api/logs/{id}/reject` | PUT | 驳回日志 |
| **统计分析** | `/api/analytics/dashboard` | GET | 仪表盘统计 |
| | `/api/analytics/fault-rate` | GET | 故障率趋势 |
| | `/api/analytics/cost-analysis` | GET | 成本分析 |
| **系统设置** | `/api/settings/approval` | GET/PUT | 审批配置 |
| | `/api/settings/system` | GET/PUT | 系统配置 |
| **上传** | `/api/upload` | POST | 文件上传 |
| **导出** | `/api/export/excel` | POST | Excel 导出 |
| | `/api/export/pdf` | POST | PDF 导出 |

### 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

### 错误响应格式

```json
{
  "code": 400,
  "detail": "错误信息",
  "message": "请求参数错误"
}
```

---

## 部署架构

### Docker 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host (Windows)                  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Docker Compose (编排工具)                    │ │
│  └────────────┬────────────────┬────────────┬─────────┘ │
│               │                │            │           │
│  ┌────────────▼───┐  ┌────────▼───┐  ┌───▼─────────┐ │
│  │  postgres      │  │  redis     │  │  nginx      │ │
│  │  (数据库)       │  │  (缓存)     │  │  (反向代理)  │ │
│  │  Port: 5432    │  │ Port: 6379 │  │  Port: 80   │ │
│  └────────────────┘  └────────────┘  └─────────────┘ │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  backend (FastAPI)   Port: 8000                     │ │
│  │  frontend (Node.js)  Port: 5173                     │ │
│  │  celery-worker      (异步任务)                      │ │
│  │  celery-beat        (定时任务)                      │ │
│  └────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 服务依赖关系

```
postgres (healthy) ──→ backend (depends_on)
redis (healthy)   ──→ backend (depends_on)
backend (running) ──→ celery-worker (depends_on)
backend (running) ──→ celery-beat (depends_on)
backend (running) ──→ nginx (depends_on)
```

### 数据持久化

```yaml
volumes:
  postgres_data:     # PostgreSQL 数据
  redis_data:        # Redis 数据
  ./uploads:/app/uploads  # 上传文件
```

### 网络配置

```yaml
networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 性能优化

### 前端优化

- ✅ **代码分割**: 路由懒加载
- ✅ **资源压缩**: Vite 自动压缩
- ✅ **缓存策略**: HTTP 缓存
- ✅ **CDN 加速**: Nginx 静态文件

### 后端优化

- ✅ **数据库索引**: 关键字段已建索引
- ✅ **连接池**: SQLAlchemy 连接池
- ✅ **缓存**: Redis 缓存热点数据
- ✅ **异步任务**: Celery 处理耗时操作

### 数据库优化

- ✅ **索引优化**: 15+ 个索引
- ✅ **查询优化**: ORM 优化查询
- ✅ **连接池**: 最大 20 个连接

---

## 安全设计

### 认证安全

- ✅ JWT Token（30 分钟过期）
- ✅ Refresh Token 机制
- ✅ bcrypt 密码哈希（cost factor=12）
- ✅ 登录失败锁定（5 次失败后锁定）

### 权限控制

- ✅ 基于角色的访问控制（RBAC）
- ✅ 三级角色：超级管理员 > 管理员 > 用户
- ✅ 细粒度权限检查

### 数据安全

- ✅ SQL 注入防护（ORM）
- ✅ XSS 防护（前端转义）
- ✅ CSRF 防护（Token）
- ✅ 敏感数据加密存储

### 网络安全

- ✅ CORS 配置
- ✅ HTTPS（生产环境）
- ✅ 防火墙配置

---

## 监控与日志

### 日志记录

- **请求日志**: 记录所有 HTTP 请求
- **错误日志**: 记录所有异常
- **审计日志**: 记录用户关键操作
- **Celery 日志**: 异步任务执行日志

### 健康检查

```bash
# 应用健康检查
GET /health

# 响应
{
  "status": "healthy",
  "app_name": "设备信息动态管理系统",
  "version": "1.0.0"
}
```

---

## 总结

### 系统特点

1. **现代化技术栈**: Vue 3 + FastAPI + PostgreSQL
2. **完整的功能**: 覆盖设备管理全流程
3. **良好的架构**: 前后端分离、模块化设计
4. **易于维护**: 代码清晰、文档齐全
5. **容器化部署**: Docker + Docker Compose

### 适用场景

- 工业设备管理
- 机械设备维护
- 设备生命周期跟踪
- 维修成本分析
- 保养计划管理

### 扩展性

- ✅ 模块化设计，易于添加新功能
- ✅ RESTful API，易于集成
- ✅ Docker 部署，易于扩展

---

**文档版本**: v1.0
**最后更新**: 2026-07-18
**维护者**: Claude Code

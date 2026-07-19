# 文档索引

本文档提供项目所有文档的导航和说明。

---

## 📚 官方文档

### 入门文档
1. **[README.md](README.md)** - 项目说明
   - 功能特性
   - 技术栈
   - 快速开始
   - 默认账号

2. **[QUICK_RUN.md](QUICK_RUN.md)** - 快速运行指南 ⭐ **推荐首先阅读**
   - 环境要求
   - 一键部署步骤
   - 访问地址
   - 常见问题

3. **[QUICK_START.md](QUICK_START.md)** - 快速开始指南

### 部署文档
4. **[LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)** - 本地部署详细指南
5. **[DOCKER_INSTALL.md](DOCKER_INSTALL.md)** - Docker 安装指南
6. **[TENCENT_CLOUD_DEPLOYMENT.md](TENCENT_CLOUD_DEPLOYMENT.md)** - 腾讯云部署指南
7. **[docs/迁移部署指南.md](docs/迁移部署指南.md)** - 系统迁移到其他服务器（含全量数据迁移）

### 开发文档
8. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目完成总结
9. **[DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md)** - 开发进度追踪
10. **[CHANGELOG.md](CHANGELOG.md)** - 版本更新日志
11. **[BUGFIX_LOG.md](BUGFIX_LOG.md)** - Bug 修复记录
12. **[DESIGN_SYSTEM_QUICK_REFERENCE.md](DESIGN_SYSTEM_QUICK_REFERENCE.md)** - 设计系统参考

---

## 🧪 测试与验证文档

12. **[ARCHITECTURE_VERIFICATION.md](ARCHITECTURE_VERIFICATION.md)** - 架构验证报告
    - 完整的后端架构分析
    - 完整的前端架构分析
    - 数据库设计验证
    - 功能清单（50+ API 端点、17 个页面）

13. **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** - 功能测试清单 ⭐ **测试必读**
    - 认证功能测试（5 个场景）
    - 设备管理测试（7 个场景）
    - 日志管理测试（8 个场景）
    - 统计分析测试（7 个场景）
    - 系统设置测试（3 个场景）
    - 用户管理测试（3 个场景）
    - 新增功能测试（5 个场景）
    - 文件上传测试（2 个场景）
    - 响应式测试（3 个场景）
    - 性能测试（2 个场景）

14. **[VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)** - 验证总结报告
    - 验证结论
    - 项目规模统计
    - 技术架构评分
    - 代码质量分析
    - 综合评鉴

15. **[docs/README功能对比报告.md](docs/README功能对比报告.md)** - README 描述与实际功能差异对比
    - 文档描述了但未实现的功能（6 项）
    - 系统拥有但文档未提及的功能（8 项）
    - 描述准确的功能清单
    - 差异处理建议

16. **[docs/迁移包验证报告.md](docs/迁移包验证报告.md)** - 迁移包完整性验证报告
    - 数据库 18 张表数据一致性验证
    - 后端代码完整性（13 路由 + 7 模型）
    - 前端代码完整性（18 页面 + 支撑文件）
    - 部署配置关键规则验证

17. **[docs/开发过程记忆文档.md](docs/开发过程记忆文档.md)** - 项目完整开发历程存档 ⭐ **开发历史必读**
    - v1.0.0 → v1.1.2 完整时间线叙事
    - 8 大技术突破过程详细复盘（含 bcrypt/GitHub SNI/Hyper-V 端口等）
    - 功能实现状态表（已实现/部分实现/未实现）
    - 关键决策记录与思考过程
    - 经验教训总结

18. **[docs/群晖NAS部署指南.md](docs/群晖NAS部署指南.md)** - 群晖 Synology NAS 部署指南（x86_64 架构）
    - 迁移包上传与目录结构适配
    - docker-compose.yml 群晖卷映射修改
    - SSH 部署全流程 + DSM 7.2+ 图形化部署
    - 开机自启、定时备份、HTTPS 反向代理配置
    - 群晖专用运维脚本（start.sh/stop.sh/backup.sh）
    - 一键部署脚本 deploy.sh

---

## 📖 快速导航

### 新用户
1. 先阅读 **[README.md](README.md)** 了解项目概况
2. 查看 **[QUICK_RUN.md](QUICK_RUN.md)** 快速部署
3. 参考 **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** 测试功能

### 开发者
1. 阅读 **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** 了解项目结构
2. 查看 **[ARCHITECTURE_VERIFICATION.md](ARCHITECTURE_VERIFICATION.md)** 深入理解架构
3. 参考 **[DEVELOPMENT_PROGRESS.md](DEVELOPMENT_PROGRESS.md)** 开发历史

### 运维人员
1. 查看 **[QUICK_RUN.md](QUICK_RUN.md)** 部署指南
2. 参考 **[TENCENT_CLOUD_DEPLOYMENT.md](TENCENT_CLOUD_DEPLOYMENT.md)** 云部署
3. 阅读 **[DOCKER_INSTALL.md](DOCKER_INSTALL.md)** Docker 安装

### 测试人员
1. 参考 **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** 完整测试清单
2. 查看 **[VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)** 验证报告

---

## 📊 文档统计

| 分类 | 数量 | 总页数（估算） |
|------|------|---------------|
| 官方文档 | 12 | 160+ |
| 测试验证 | 7 | 320+ |
| 总计 | 18 | 480+ |

---

## 🔍 文档搜索

### 按主题查找

#### 部署相关
- Docker 部署 → QUICK_RUN.md
- 本地部署 → LOCAL_DEPLOYMENT.md
- 云部署 → TENCENT_CLOUD_DEPLOYMENT.md
- Docker 安装 → DOCKER_INSTALL.md
- 系统迁移 → docs/迁移部署指南.md

#### 功能相关
- 设备管理 → ARCHITECTURE_VERIFICATION.md
- 日志管理 → ARCHITECTURE_VERIFICATION.md
- 用户认证 → ARCHITECTURE_VERIFICATION.md
- 统计分析 → ARCHITECTURE_VERIFICATION.md
- 功能差异 → docs/README功能对比报告.md

#### 开发相关
- 项目结构 → PROJECT_SUMMARY.md
- 开发进度 → DEVELOPMENT_PROGRESS.md
- Bug 修复 → BUGFIX_LOG.md
- 版本历史 → CHANGELOG.md

#### 测试相关
- 测试清单 → TESTING_CHECKLIST.md
- 架构验证 → ARCHITECTURE_VERIFICATION.md
- 验证总结 → VERIFICATION_SUMMARY.md
- 迁移包验证 → docs/迁移包验证报告.md

---

## 📝 文档版本

**最后更新**: 2026-07-19
**文档版本**: v1.1
**维护者**: Claude Code

---

**提示**: 建议新用户从 **[QUICK_RUN.md](QUICK_RUN.md)** 开始阅读！

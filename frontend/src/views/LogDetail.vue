<template>
  <div class="log-detail-page" v-loading="loading">
    <div v-if="logDetail" class="detail-wrap">
      <!-- ============ 1. 顶部操作栏 ============ -->
      <div class="detail-head">
        <div class="head-left">
          <button class="icon-btn" title="返回" @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <div class="head-title">
            <div class="title-row">
              <h1 class="detail-title">
                {{ logDetail.equipment?.name }} {{ getLogTypeLabel(logDetail.log_type) }}
              </h1>
              <span class="badge badge-lg badge-warning">{{ getLogTypeLabel(logDetail.log_type) }}</span>
              <span
                class="badge badge-lg"
                :class="logDetail.status === 'approved' ? 'badge-success' : logDetail.status === 'rejected' ? 'badge-error' : logDetail.status === 'pending' ? 'badge-warning' : 'badge-neutral'"
              >
                {{ getStatusLabel(logDetail.status) }}
              </span>
              <span
                v-if="logDetail.log_type === 'fault' && logDetail.detail && logDetail.detail.fault_level === 'critical'"
                class="badge badge-lg badge-error"
              >
                紧急优先
              </span>
              <span class="log-no numeric">LOG-{{ logDetail.id }}</span>
            </div>
            <div class="subtitle">
              提交人 {{ logDetail.operator?.username || '-' }} · {{ formatDateTime(logDetail.created_at) }} · {{ logDetail.equipment?.code || '-' }}
            </div>
          </div>
        </div>
        <div class="head-right">
          <el-button class="head-btn">
            <el-icon><Edit /></el-icon>
            <span>编辑</span>
          </el-button>
          <el-button class="head-btn">
            <el-icon><Printer /></el-icon>
            <span>打印</span>
          </el-button>
          <button class="icon-btn" title="更多">
            <el-icon><MoreFilled /></el-icon>
          </button>
          <span class="head-divider"></span>
          <el-button type="primary" @click="$router.push('/logs')">
            <el-icon><Plus /></el-icon>
            <span>新建日志</span>
          </el-button>
        </div>
      </div>

      <!-- ============ 2. 状态进度条卡片 ============ -->
      <div class="card-minimal progress-card">
        <div class="card-head">
          <div class="section-title">
            <span class="card-title-bar"></span>
            <span class="section-label">审批进度</span>
            <span class="section-meta">共 4 个节点</span>
          </div>
          <div class="head-status">
            <span class="status-label">当前状态</span>
            <span
              class="badge"
              :class="logDetail.status === 'approved' ? 'badge-success' : logDetail.status === 'rejected' ? 'badge-error' : logDetail.status === 'pending' ? 'badge-warning' : 'badge-neutral'"
            >
              {{ getStatusLabel(logDetail.status) }}
            </span>
          </div>
        </div>
        <div class="progress-grid">
          <!-- 节点1 提交 -->
          <div class="progress-node">
            <div class="node-top">
              <span class="node-dot done"></span>
              <span class="node-label">提交</span>
              <span class="badge badge-success">已完成</span>
            </div>
            <div class="progress-bar done"></div>
            <div class="node-meta">{{ logDetail.operator?.username || '-' }} · {{ formatDateTime(logDetail.created_at) }}</div>
          </div>

          <!-- 节点2 初审 -->
          <div class="progress-node">
            <div class="node-top">
              <span
                class="node-dot"
                :class="logDetail.status === 'approved' ? 'done' : logDetail.status === 'pending' ? 'current' : logDetail.status === 'rejected' ? 'error' : 'pending'"
              ></span>
              <span class="node-label">初审</span>
              <span
                class="badge"
                :class="logDetail.status === 'approved' ? 'badge-success' : logDetail.status === 'pending' ? 'badge-info' : logDetail.status === 'rejected' ? 'badge-error' : 'badge-neutral'"
              >
                {{ logDetail.status === 'approved' ? '已完成' : logDetail.status === 'pending' ? '进行中' : logDetail.status === 'rejected' ? '已驳回' : '待处理' }}
              </span>
            </div>
            <div
              class="progress-bar"
              :class="logDetail.status === 'approved' ? 'done' : logDetail.status === 'pending' ? 'current' : logDetail.status === 'rejected' ? 'error' : 'pending'"
            ></div>
            <div class="node-meta">
              {{ logDetail.status === 'approved' ? (logDetail.approver?.username || '审批人') + ' · ' + formatDateTime(logDetail.approved_at) : '待初审' }}
            </div>
          </div>

          <!-- 节点3 复核 -->
          <div class="progress-node">
            <div class="node-top">
              <span class="node-dot" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></span>
              <span class="node-label">复核</span>
              <span class="badge" :class="logDetail.status === 'approved' ? 'badge-success' : 'badge-neutral'">
                {{ logDetail.status === 'approved' ? '已完成' : '待处理' }}
              </span>
            </div>
            <div class="progress-bar" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></div>
            <div class="node-meta">{{ logDetail.status === 'approved' ? '复核通过' : '等待复核' }}</div>
          </div>

          <!-- 节点4 终审 -->
          <div class="progress-node">
            <div class="node-top">
              <span class="node-dot" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></span>
              <span class="node-label">终审</span>
              <span class="badge" :class="logDetail.status === 'approved' ? 'badge-success' : 'badge-neutral'">
                {{ logDetail.status === 'approved' ? '已完成' : '待处理' }}
              </span>
            </div>
            <div class="progress-bar" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></div>
            <div class="node-meta">{{ logDetail.status === 'approved' ? '终审通过' : '等待终审' }}</div>
          </div>
        </div>
      </div>

      <!-- ============ 3. 主信息区 ============ -->
      <div class="main-grid">
        <!-- 左栏 -->
        <div class="main-left">
          <!-- 日志基本信息 -->
          <div class="card-minimal">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">日志基本信息</span>
            </div>
            <div class="field-grid">
              <div class="field-item">
                <div class="field-label">日志编号</div>
                <div class="field-value numeric">LOG-{{ logDetail.id }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">日志类型</div>
                <div class="field-value">
                  <span class="badge badge-warning">{{ getLogTypeLabel(logDetail.log_type) }}</span>
                </div>
              </div>
              <div class="field-item full">
                <div class="field-label">日志标题</div>
                <div class="field-value">{{ logDetail.equipment?.name || '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">日志描述</div>
                <div class="field-value desc-value">{{ logDetail.description || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 设备信息 -->
          <div class="card-minimal">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">设备信息</span>
            </div>
            <div class="field-grid">
              <div class="field-item">
                <div class="field-label">设备名称</div>
                <div class="field-value">{{ logDetail.equipment?.name || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">设备编号</div>
                <div class="field-value numeric">{{ logDetail.equipment?.code || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">创建时间</div>
                <div class="field-value numeric">{{ formatDateTime(logDetail.created_at) }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">审批时间</div>
                <div class="field-value numeric">
                  {{ logDetail.approved_at ? formatDateTime(logDetail.approved_at) : '-' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 详细信息 -->
          <div class="card-minimal" v-if="logDetail.detail">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">详细信息</span>
            </div>

            <!-- 安装日志 -->
            <div class="field-grid" v-if="logDetail.log_type === 'installation'">
              <div class="field-item">
                <div class="field-label">安装日期</div>
                <div class="field-value">{{ logDetail.detail.installation_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">安装人员</div>
                <div class="field-value">{{ logDetail.detail.installer || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">安装位置</div>
                <div class="field-value">{{ logDetail.detail.location || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">验收状态</div>
                <div class="field-value">{{ logDetail.detail.acceptance_status || '-' }}</div>
              </div>
            </div>

            <!-- 维修日志 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'repair'">
              <div class="field-item">
                <div class="field-label">维修日期</div>
                <div class="field-value">{{ logDetail.detail.repair_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">维修费用</div>
                <div class="field-value numeric">¥{{ logDetail.detail.cost ?? '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">维修时长(小时)</div>
                <div class="field-value numeric">{{ logDetail.detail.repair_time ?? '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">故障描述</div>
                <div class="field-value desc-value">{{ logDetail.detail.fault_description || '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">解决方案</div>
                <div class="field-value desc-value">{{ logDetail.detail.solution || '-' }}</div>
              </div>
            </div>

            <!-- 报废日志 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'scrap'">
              <div class="field-item">
                <div class="field-label">报废日期</div>
                <div class="field-value">{{ logDetail.detail.scrap_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">残值</div>
                <div class="field-value numeric">¥{{ logDetail.detail.residual_value ?? '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">报废原因</div>
                <div class="field-value desc-value">{{ logDetail.detail.scrap_reason || '-' }}</div>
              </div>
            </div>

            <!-- 巡检日志 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'inspection'">
              <div class="field-item">
                <div class="field-label">巡检日期</div>
                <div class="field-value">{{ logDetail.detail.inspection_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">巡检人员</div>
                <div class="field-value">{{ logDetail.detail.inspector || '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">巡检结果</div>
                <div class="field-value">
                  <span
                    class="badge"
                    :class="logDetail.detail.result === 'normal' ? 'badge-success' : 'badge-error'"
                  >
                    {{ logDetail.detail.result === 'normal' ? '正常' : '异常' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 保养记录 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'maintenance'">
              <div class="field-item">
                <div class="field-label">保养日期</div>
                <div class="field-value">{{ logDetail.detail.maintenance_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">下次保养日期</div>
                <div class="field-value">{{ logDetail.detail.next_maintenance_date || '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">保养项目</div>
                <div class="field-value">
                  <div class="tag-inline-list">
                    <span
                      class="badge badge-info"
                      v-for="item in logDetail.detail.maintenance_items"
                      :key="item"
                    >
                      {{ item }}
                    </span>
                    <span v-if="!logDetail.detail.maintenance_items || logDetail.detail.maintenance_items.length === 0">-</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 故障报修 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'fault'">
              <div class="field-item">
                <div class="field-label">故障日期</div>
                <div class="field-value">{{ logDetail.detail.fault_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">故障等级</div>
                <div class="field-value">
                  <span class="badge" :class="logDetail.detail.fault_level === 'critical' ? 'badge-error' : logDetail.detail.fault_level === 'major' ? 'badge-warning' : 'badge-info'">
                    {{ getFaultLevelLabel(logDetail.detail.fault_level) }}
                  </span>
                </div>
              </div>
              <div class="field-item">
                <div class="field-label">报告人</div>
                <div class="field-value">{{ logDetail.detail.reporter || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">处理状态</div>
                <div class="field-value">{{ logDetail.detail.handle_status || '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">故障描述</div>
                <div class="field-value desc-value">{{ logDetail.detail.fault_description || '-' }}</div>
              </div>
            </div>

            <!-- 配件更换 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'parts'">
              <div class="field-item">
                <div class="field-label">更换日期</div>
                <div class="field-value">{{ logDetail.detail.replacement_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">配件编号</div>
                <div class="field-value numeric">{{ logDetail.detail.parts_code || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">配件名称</div>
                <div class="field-value">{{ logDetail.detail.parts_name || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">数量</div>
                <div class="field-value numeric">{{ logDetail.detail.quantity ?? '-' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">费用</div>
                <div class="field-value numeric">¥{{ logDetail.detail.cost ?? '-' }}</div>
              </div>
            </div>

            <!-- 校准记录 -->
            <div class="field-grid" v-else-if="logDetail.log_type === 'calibration'">
              <div class="field-item">
                <div class="field-label">校准日期</div>
                <div class="field-value">{{ logDetail.detail.calibration_date || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">校准机构</div>
                <div class="field-value">{{ logDetail.detail.calibration_org || '-' }}</div>
              </div>
              <div class="field-item">
                <div class="field-label">校准结果</div>
                <div class="field-value">
                  <span
                    class="badge"
                    :class="logDetail.detail.calibration_result === 'qualified' ? 'badge-success' : 'badge-error'"
                  >
                    {{ logDetail.detail.calibration_result === 'qualified' ? '合格' : '不合格' }}
                  </span>
                </div>
              </div>
              <div class="field-item">
                <div class="field-label">下次校准日期</div>
                <div class="field-value">{{ logDetail.detail.next_calibration_date || '-' }}</div>
              </div>
            </div>
          </div>

          <!-- 关联附件 -->
          <div class="card-minimal" v-if="logDetail.attachments && logDetail.attachments.length > 0">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">关联附件</span>
              <span class="section-meta">{{ logDetail.attachments.length }} 个文件</span>
            </div>
            <div class="attachments-grid">
              <div
                class="attachment-item"
                v-for="(file, index) in logDetail.attachments"
                :key="index"
                @click="handleDownload(file)"
              >
                <div class="attachment-icon-wrap">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="attachment-info">
                  <div class="attachment-name">附件 {{ index + 1 }}</div>
                  <div class="attachment-hint">点击下载</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 审批流程时间线 -->
          <div class="card-minimal">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">审批流程时间线</span>
            </div>
            <ol class="timeline">
              <li class="timeline-item">
                <span class="timeline-dot done"></span>
                <div class="timeline-content">
                  <div class="timeline-head">
                    <span class="timeline-title">提交日志</span>
                    <span class="timeline-time numeric">{{ formatDateTime(logDetail.created_at) }}</span>
                  </div>
                  <div class="timeline-user">{{ logDetail.operator?.username || '-' }}</div>
                  <div class="timeline-desc">提交 {{ getLogTypeLabel(logDetail.log_type) }} 日志，等待审批</div>
                </div>
              </li>
              <li class="timeline-item">
                <span
                  class="timeline-dot"
                  :class="logDetail.status === 'approved' ? 'done' : logDetail.status === 'pending' ? 'current' : logDetail.status === 'rejected' ? 'error' : 'pending'"
                ></span>
                <div class="timeline-content">
                  <div class="timeline-head">
                    <span class="timeline-title">初审</span>
                    <span class="timeline-time numeric" v-if="logDetail.approved_at">{{ formatDateTime(logDetail.approved_at) }}</span>
                  </div>
                  <div class="timeline-user">
                    {{ logDetail.approver?.username || (logDetail.status === 'pending' ? '待分配' : '-') }}
                  </div>
                  <div class="timeline-desc">
                    {{ logDetail.status === 'approved' ? '初审通过，进入复核环节' : logDetail.status === 'pending' ? '等待管理员初审' : '初审驳回，流程终止' }}
                  </div>
                </div>
              </li>
              <li class="timeline-item">
                <span class="timeline-dot" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></span>
                <div class="timeline-content">
                  <div class="timeline-head">
                    <span class="timeline-title">复核</span>
                    <span class="timeline-time numeric" v-if="logDetail.status === 'approved'">{{ formatDateTime(logDetail.approved_at) }}</span>
                  </div>
                  <div class="timeline-user">
                    {{ logDetail.status === 'approved' ? (logDetail.approver?.username || '-') : '待分配' }}
                  </div>
                  <div class="timeline-desc">{{ logDetail.status === 'approved' ? '复核通过' : '等待复核' }}</div>
                </div>
              </li>
              <li class="timeline-item last">
                <span class="timeline-dot" :class="logDetail.status === 'approved' ? 'done' : 'pending'"></span>
                <div class="timeline-content">
                  <div class="timeline-head">
                    <span class="timeline-title">终审</span>
                    <span class="timeline-time numeric" v-if="logDetail.status === 'approved'">{{ formatDateTime(logDetail.approved_at) }}</span>
                  </div>
                  <div class="timeline-user">
                    {{ logDetail.status === 'approved' ? (logDetail.approver?.username || '-') : '待分配' }}
                  </div>
                  <div class="timeline-desc">{{ logDetail.status === 'approved' ? '终审通过，流程结束' : '等待终审' }}</div>
                </div>
              </li>
            </ol>
          </div>

          <!-- 驳回原因 -->
          <div class="card-minimal reject-card" v-if="logDetail.status === 'rejected'">
            <div class="section-title">
              <span class="card-title-bar error"></span>
              <span class="section-label">驳回原因</span>
              <span class="badge badge-error">仅驳回时填写</span>
            </div>
            <div class="reject-content">
              {{ logDetail.rejection_reason || '未填写驳回原因' }}
            </div>
          </div>
        </div>

        <!-- 右栏 元数据侧栏 -->
        <div class="main-right">
          <!-- 审批操作 -->
          <div class="side-card" v-if="logDetail?.status === 'pending'">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">审批操作</span>
              <span class="badge badge-neutral">管理员</span>
            </div>
            <div class="action-grid">
              <button class="action-btn approve" @click="handleApprove">
                <el-icon><Check /></el-icon>
                <span>通过</span>
              </button>
              <button class="action-btn reject" @click="handleReject">
                <el-icon><Close /></el-icon>
                <span>驳回</span>
              </button>
              <button class="action-btn transfer">
                <el-icon><Share /></el-icon>
                <span>转交</span>
              </button>
            </div>
            <div class="action-tip">通过后将进入复核环节，驳回需填写原因</div>
          </div>

          <!-- 日志元信息 -->
          <div class="side-card">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">日志元信息</span>
            </div>
            <dl class="meta-list">
              <div class="meta-row">
                <dt>提交人</dt>
                <dd>{{ logDetail.operator?.username || '-' }}</dd>
              </div>
              <div class="meta-row">
                <dt>提交时间</dt>
                <dd class="numeric">{{ formatDateTime(logDetail.created_at) }}</dd>
              </div>
              <div class="meta-row">
                <dt>日志类型</dt>
                <dd><span class="badge badge-info">{{ getLogTypeLabel(logDetail.log_type) }}</span></dd>
              </div>
              <div class="meta-row">
                <dt>状态</dt>
                <dd>
                  <span
                    class="badge"
                    :class="logDetail.status === 'approved' ? 'badge-success' : logDetail.status === 'rejected' ? 'badge-error' : logDetail.status === 'pending' ? 'badge-warning' : 'badge-neutral'"
                  >
                    {{ getStatusLabel(logDetail.status) }}
                  </span>
                </dd>
              </div>
              <div class="meta-row">
                <dt>审批人</dt>
                <dd>{{ logDetail.approver?.username || '-' }}</dd>
              </div>
              <div class="meta-row">
                <dt>审批时间</dt>
                <dd class="numeric">{{ logDetail.approved_at ? formatDateTime(logDetail.approved_at) : '-' }}</dd>
              </div>
            </dl>
          </div>

          <!-- 标签 -->
          <div class="side-card">
            <div class="section-title">
              <span class="card-title-bar"></span>
              <span class="section-label">标签</span>
            </div>
            <div class="tag-list">
              <template v-if="logDetail.log_type === 'repair'">
                <span class="badge badge-neutral">压力异常</span>
                <span class="badge badge-neutral">阀芯磨损</span>
                <span class="badge badge-neutral">紧急维修</span>
              </template>
              <template v-else-if="logDetail.log_type === 'fault'">
                <span class="badge badge-neutral">停机风险</span>
                <span class="badge badge-neutral">紧急处理</span>
                <span class="badge badge-neutral">现场排查</span>
              </template>
              <template v-else-if="logDetail.log_type === 'maintenance'">
                <span class="badge badge-neutral">常规保养</span>
                <span class="badge badge-neutral">润滑更换</span>
              </template>
              <template v-else-if="logDetail.log_type === 'inspection'">
                <span class="badge badge-neutral">日常巡检</span>
                <span class="badge badge-neutral">状态记录</span>
              </template>
              <template v-else-if="logDetail.log_type === 'installation'">
                <span class="badge badge-neutral">新装验收</span>
                <span class="badge badge-neutral">调试完成</span>
              </template>
              <template v-else-if="logDetail.log_type === 'scrap'">
                <span class="badge badge-neutral">资产处置</span>
                <span class="badge badge-neutral">残值回收</span>
              </template>
              <template v-else-if="logDetail.log_type === 'parts'">
                <span class="badge badge-neutral">配件更换</span>
                <span class="badge badge-neutral">库存核销</span>
              </template>
              <template v-else-if="logDetail.log_type === 'calibration'">
                <span class="badge badge-neutral">计量校准</span>
                <span class="badge badge-neutral">精度核验</span>
              </template>
              <template v-else>
                <span class="badge badge-neutral">{{ getLogTypeLabel(logDetail.log_type) }}</span>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-empty description="日志不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Edit,
  Printer,
  MoreFilled,
  Plus,
  Check,
  Close,
  Document,
  Share
} from '@element-plus/icons-vue'
import { getLogDetail, approveLog } from '@/api'

const route = useRoute()
const loading = ref(false)
const logDetail = ref<any>(null)

const getLogTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    installation: '设备安装',
    repair: '设备维修',
    scrap: '设备报废',
    inspection: '日常巡检',
    maintenance: '保养记录',
    fault: '故障报修',
    parts: '配件更换',
    calibration: '校准记录'
  }
  return labels[type] || type
}

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已驳回'
  }
  return labels[status] || status
}

const getStatusType = (status: string): string => {
  const types: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getFaultLevelLabel = (level: string): string => {
  const labels: Record<string, string> = {
    minor: '轻微',
    major: '严重',
    critical: '紧急'
  }
  return labels[level] || level
}

const getFaultLevelType = (level: string): string => {
  const types: Record<string, string> = {
    minor: 'info',
    major: 'warning',
    critical: 'danger'
  }
  return types[level] || 'info'
}

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadLogDetail = async () => {
  try {
    loading.value = true
    const id = route.params.id
    const res = await getLogDetail(Number(id))
    logDetail.value = res.data
  } catch (error) {
    ElMessage.error('加载日志详情失败')
  } finally {
    loading.value = false
  }
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('确认通过此日志？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await approveLog(logDetail.value.id, true)
    ElMessage.success('审批通过')
    loadLogDetail()
  } catch (error) {
    // 用户取消
  }
}

const handleReject = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'textarea'
    })
    await approveLog(logDetail.value.id, false, value)
    ElMessage.success('已驳回')
    loadLogDetail()
  } catch (error) {
    // 用户取消
  }
}

const handleDownload = (filePath: string) => {
  window.open(filePath, '_blank')
}

onMounted(() => {
  loadLogDetail()
})
</script>

<style scoped>
/* ============================================================
   LogDetail · 方案A 现代简约风
   ============================================================ */

.log-detail-page {
  width: 100%;
}

.detail-wrap {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* ---------- 通用卡片 ---------- */
.card-minimal {
  background: var(--surface-overlay);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: none;
  padding: 20px 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.section-label {
  font-size: 15px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: 1;
}

.section-meta {
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: var(--font-weight-normal);
}

.card-title-bar {
  display: inline-block;
  width: 3px;
  height: 14px;
  background: var(--color-primary-600);
  border-radius: 2px;
  flex-shrink: 0;
}

.card-title-bar.error {
  background: var(--color-danger-500);
}

/* ---------- numeric ---------- */
.numeric {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* ---------- badge ---------- */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: var(--font-weight-medium);
  line-height: 1.5;
  white-space: nowrap;
  border: none;
}

.badge-lg {
  padding: 4px 12px;
  font-size: 13px;
}

.badge-warning {
  background: color-mix(in srgb, var(--color-warning-500) 12%, transparent);
  color: var(--color-warning-600);
}

.badge-success {
  background: color-mix(in srgb, var(--color-success-500) 12%, transparent);
  color: var(--color-success-600);
}

.badge-error {
  background: color-mix(in srgb, var(--color-danger-500) 12%, transparent);
  color: var(--color-danger-600);
}

.badge-info {
  background: color-mix(in srgb, var(--color-primary-600) 12%, transparent);
  color: var(--color-primary-600);
}

.badge-neutral {
  background: var(--surface-elevated);
  color: var(--text-tertiary);
}

/* ============================================================
   1. 顶部操作栏
   ============================================================ */
.detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.head-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
  flex: 1;
}

.head-title {
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-title {
  font-size: var(--text-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  letter-spacing: -0.01em;
  line-height: 1.3;
  margin: 0;
}

.log-no {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-left: 4px;
}

.subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.head-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.head-btn .el-icon + span {
  margin-left: 4px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
  font-size: 16px;
}

.icon-btn:hover {
  background: var(--surface-elevated);
  color: var(--text-primary);
}

.head-divider {
  width: 1px;
  height: 24px;
  background: var(--border-default);
  margin: 0 4px;
}

/* ============================================================
   2. 进度条卡片
   ============================================================ */
.progress-card .card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.head-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.progress-node {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.node-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--color-neutral-300);
}

.node-dot.done {
  background: var(--color-success-500);
}

.node-dot.current {
  background: var(--color-primary-600);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary-600) 18%, transparent);
}

.node-dot.error {
  background: var(--color-danger-500);
}

.node-dot.pending {
  background: var(--color-neutral-300);
}

.node-label {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.progress-bar {
  height: 6px;
  border-radius: 3px;
  background: var(--surface-elevated);
}

.progress-bar.done {
  background: var(--color-success-500);
}

.progress-bar.current {
  background: var(--color-primary-600);
}

.progress-bar.error {
  background: var(--color-danger-500);
}

.progress-bar.pending {
  background: var(--surface-elevated);
}

.node-meta {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

/* ============================================================
   3. 主信息区
   ============================================================ */
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  align-items: start;
}

.main-left {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

/* ---------- field-grid ---------- */
.field-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px 24px;
}

.field-item {
  min-width: 0;
}

.field-item.full {
  grid-column: 1 / -1;
}

.field-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
}

.field-value {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
  word-break: break-word;
}

.desc-value {
  color: var(--text-secondary);
}

.tag-inline-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* ---------- 附件 ---------- */
.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  background: var(--surface-overlay);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.attachment-item:hover {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
}

.attachment-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--color-primary-600) 10%, transparent);
  color: var(--color-primary-600);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.attachment-info {
  min-width: 0;
}

.attachment-name {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.attachment-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* ---------- 时间线 ---------- */
.timeline {
  list-style: none;
  margin: 0;
  padding: 0;
  border-left: 1px solid var(--border-default);
  padding-left: 24px;
}

.timeline-item {
  position: relative;
  padding-bottom: 24px;
}

.timeline-item.last {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -31px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--color-neutral-300);
  border: 2px solid var(--surface-overlay);
  box-sizing: content-box;
}

.timeline-dot.done {
  background: var(--color-primary-600);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary-600) 16%, transparent);
}

.timeline-dot.current {
  background: var(--color-primary-600);
  animation: tl-pulse 1.6s ease-in-out infinite;
}

.timeline-dot.error {
  background: var(--color-danger-500);
}

.timeline-dot.pending {
  background: var(--color-neutral-300);
}

@keyframes tl-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 color-mix(in srgb, var(--color-primary-600) 35%, transparent);
  }
  50% {
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-primary-600) 0%, transparent);
  }
}

.timeline-content {
  min-width: 0;
}

.timeline-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.timeline-title {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.timeline-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.timeline-user {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: var(--font-weight-medium);
}

.timeline-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
  line-height: 1.6;
}

/* ---------- 驳回原因 ---------- */
.reject-card {
  border-color: color-mix(in srgb, var(--color-danger-500) 30%, var(--border-default));
}

.reject-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  padding: 12px 14px;
  background: color-mix(in srgb, var(--color-danger-500) 6%, transparent);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-danger-500);
}

/* ============================================================
   右栏 元数据侧栏
   ============================================================ */
.main-right {
  background: var(--surface-elevated);
  border: 1px solid var(--border-default);
  padding: 20px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
}

.side-card {
  padding: 16px 0;
  border-bottom: 1px solid var(--border-default);
}

.side-card:first-child {
  padding-top: 0;
}

.side-card:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* 审批操作 */
.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 10px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 8px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--surface-overlay);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-default);
}

.action-btn .el-icon {
  font-size: 18px;
}

.action-btn:hover {
  border-color: var(--color-primary-400);
  color: var(--color-primary-600);
}

.action-btn.approve {
  background: var(--color-success-500);
  border-color: var(--color-success-500);
  color: #fff;
}

.action-btn.approve:hover {
  background: var(--color-success-600);
  border-color: var(--color-success-600);
  color: #fff;
}

.action-btn.reject {
  background: var(--color-danger-500);
  border-color: var(--color-danger-500);
  color: #fff;
}

.action-btn.reject:hover {
  background: var(--color-danger-600);
  border-color: var(--color-danger-600);
  color: #fff;
}

.action-tip {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.6;
}

/* 元信息列表 */
.meta-list {
  margin: 0;
}

.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-default);
}

.meta-row:last-child {
  border-bottom: none;
}

.meta-row dt {
  font-size: 13px;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.meta-row dd {
  font-size: 13px;
  color: var(--text-primary);
  text-align: right;
  word-break: break-word;
}

/* 标签 */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* ============================================================
   空状态
   ============================================================ */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
}

.empty-state :deep(.el-empty__image) {
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--surface-elevated);
  color: var(--text-tertiary);
}

.empty-state :deep(.el-empty__description) {
  color: var(--text-tertiary);
  font-size: 14px;
  margin-top: 16px;
}

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .detail-head {
    flex-direction: column;
    align-items: stretch;
  }

  .head-right {
    flex-wrap: wrap;
  }

  .progress-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .field-grid {
    grid-template-columns: 1fr;
  }

  .card-minimal {
    padding: 16px;
  }

  .main-right {
    padding: 16px;
  }
}
</style>

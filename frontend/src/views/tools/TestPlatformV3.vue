<template>
  <div class="test-platform-v3">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/tools')" :icon="Back" size="small">返回工具页</el-button>
      <h2 class="tool-title">🛠️ 测试平台 V3.0</h2>
      <el-tag type="warning" size="small">规划中</el-tag>
    </div>

    <!-- 平台介绍Banner -->
    <div class="platform-banner">
      <div class="banner-content">
        <div class="banner-text">
          <h3 class="banner-title">用例管理平台 × 测试引擎</h3>
          <p class="banner-desc">
            V3.0 接入专业用例管理平台（如 metersphere、TestCenter），通过标准化接口统一管控测试引擎，
            实现<strong>用例管理</strong> + <strong>引擎执行</strong> + <strong>结果回传</strong>的完整闭环。
          </p>
        </div>
        <div class="banner-diagram">
          <div class="diagram-node platform">
            <span>用例管理平台</span>
            <small>metersphere 等</small>
          </div>
          <div class="diagram-arrow">⟶</div>
          <div class="diagram-node engine">
            <span>测试引擎</span>
            <small>REST/WebSocket API</small>
          </div>
          <div class="diagram-arrow">⟶</div>
          <div class="diagram-node result">
            <span>执行结果</span>
            <small>实时推送</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能Tab -->
    <el-tabs v-model="activeTab" class="main-tabs">

      <!-- 1. 平台接入配置 -->
      <el-tab-pane label="🔗 平台接入" name="platform">
        <div class="pane-content">
          <div class="section-intro">
            <h4>已接入的用例管理平台</h4>
            <p>配置 metersphere / TestCenter 等平台的对接信息，引擎即可接收平台下发的测试任务。</p>
          </div>

          <el-table :data="platforms" stripe size="small">
            <el-table-column type="index" width="50" label="#" />
            <el-table-column prop="name" label="平台名称" min-width="140" />
            <el-table-column prop="type" label="平台类型" width="120">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="平台地址" min-width="180" show-overflow-tooltip />
            <el-table-column prop="engineId" label="绑定引擎" width="100" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'connected' ? 'success' : 'info'" size="small">
                  {{ row.status === 'connected' ? '已连接' : '未连接' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="testConnection(row)">测试连接</el-button>
                <el-button size="small" link @click="editPlatform(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deletePlatform(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="add-platform">
            <el-button type="primary" :icon="Plus" @click="showAddPlatform = true">添加平台接入</el-button>
          </div>

          <!-- 接入说明 -->
          <div class="connect-guide">
            <h4>📖 快速接入指南</h4>
            <div class="guide-steps">
              <div class="guide-step">
                <div class="step-num">1</div>
                <div class="step-content">
                  <div class="step-title">在 metersphere 创建测试项目</div>
                  <div class="step-desc">登录 metersphere，进入「项目管理」→「创建项目」，填写项目名称和描述。</div>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-num">2</div>
                <div class="step-content">
                  <div class="step-title">配置引擎接入</div>
                  <div class="step-desc">在 metersphere「系统管理」→「工作空间」→「测试资源池」中添加本引擎节点。</div>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-num">3</div>
                <div class="step-content">
                  <div class="step-title">填写平台地址并保存</div>
                  <div class="step-desc">在上方「添加平台接入」中填写 metersphere 的 URL 和 API Token，即可开始对接。</div>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-num">4</div>
                <div class="step-content">
                  <div class="step-title">验证连接</div>
                  <div class="step-desc">点击「测试连接」，若显示「连接成功」则表示引擎已成功接入 metersphere。</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 2. 引擎节点管理 -->
      <el-tab-pane label="⚙️ 引擎节点" name="engine">
        <div class="pane-content">
          <div class="section-intro">
            <h4>测试引擎节点</h4>
            <p>管理本系统部署的测试引擎节点，每个节点可执行不同类型的测试任务（接口/UI/性能）。</p>
          </div>

          <div class="engine-cards">
            <div v-for="node in engineNodes" :key="node.id" class="engine-card">
              <div class="engine-card-header">
                <div class="engine-icon">{{ node.icon }}</div>
                <div class="engine-info">
                  <div class="engine-name">{{ node.name }}</div>
                  <div class="engine-version">v{{ node.version }}</div>
                </div>
                <el-tag :type="node.status === 'online' ? 'success' : 'danger'" size="small">
                  {{ node.status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </div>
              <div class="engine-stats">
                <div class="stat-item">
                  <div class="stat-val">{{ node.tasks }}</div>
                  <div class="stat-lbl">累计任务</div>
                </div>
                <div class="stat-item">
                  <div class="stat-val" :style="{ color: node.passRate >= 90 ? '#67c23a' : '#e6a23c' }">{{ node.passRate }}%</div>
                  <div class="stat-lbl">通过率</div>
                </div>
                <div class="stat-item">
                  <div class="stat-val">{{ node.cpu }}%</div>
                  <div class="stat-lbl">CPU</div>
                </div>
                <div class="stat-item">
                  <div class="stat-val">{{ node.mem }}%</div>
                  <div class="stat-lbl">内存</div>
                </div>
              </div>
              <div class="engine-tags">
                <el-tag v-for="cap in node.capabilities" :key="cap" size="small" type="info">{{ cap }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 3. 任务调度 -->
      <el-tab-pane label="📋 任务调度" name="schedule">
        <div class="pane-content">
          <div class="schedule-toolbar">
            <el-select v-model="scheduleStatus" placeholder="全部状态" clearable style="width: 130px">
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="已失败" value="failed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-button type="primary" :icon="Plus" @click="showAddSchedule = true">新建定时任务</el-button>
          </div>

          <el-table :data="schedules" stripe size="small">
            <el-table-column type="index" width="50" label="#" />
            <el-table-column prop="name" label="任务名称" min-width="160" />
            <el-table-column prop="trigger" label="触发方式" width="130">
              <template #default="{ row }">
                <el-tag size="small" :type="row.trigger === 'cron' ? 'warning' : 'info'">
                  {{ row.trigger === 'cron' ? 'Cron 定时' : '手动触发' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cron" label="Cron 表达式" width="140">
              <template #default="{ row }">
                <code class="cron-code">{{ row.cron || '-' }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="platform" label="来源平台" width="120" />
            <el-table-column prop="lastRun" label="上次执行" width="160" />
            <el-table-column prop="nextRun" label="下次执行" width="160" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="runNow(row)">立即执行</el-button>
                <el-button size="small" link @click="editSchedule(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteSchedule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 4. 通知配置 -->
      <el-tab-pane label="🔔 通知配置" name="notify">
        <div class="pane-content">
          <div class="section-intro">
            <h4>测试结果通知渠道</h4>
            <p>配置钉钉、飞书、企业微信等通知渠道，测试完成后自动推送执行结果。</p>
          </div>

          <div class="notify-channels">
            <div v-for="ch in notifyChannels" :key="ch.id" class="notify-card" :class="{ active: ch.enabled }">
              <div class="notify-header">
                <span class="notify-icon">{{ ch.icon }}</span>
                <div class="notify-info">
                  <div class="notify-name">{{ ch.name }}</div>
                  <div class="notify-status">{{ ch.enabled ? '已启用' : '未启用' }}</div>
                </div>
                <el-switch v-model="ch.enabled" @change="toggleNotify(ch)" />
              </div>
              <div v-if="ch.enabled" class="notify-config">
                <el-input v-model="ch.webhook" placeholder="Webhook 地址" size="small">
                  <template #prepend>URL</template>
                </el-input>
                <div class="notify-options">
                  <el-checkbox v-model="ch.notifyOnPass">通过时通知</el-checkbox>
                  <el-checkbox v-model="ch.notifyOnFail">失败时通知</el-checkbox>
                  <el-checkbox v-model="ch.notifyOnComplete">执行完成通知</el-checkbox>
                </div>
                <el-button type="primary" size="small" @click="testNotify(ch)">发送测试通知</el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

    </el-tabs>

    <!-- 添加平台弹窗 -->
    <el-dialog v-model="showAddPlatform" title="添加用例管理平台" width="560px">
      <el-form :model="newPlatform" label-width="110px">
        <el-form-item label="平台名称">
          <el-input v-model="newPlatform.name" placeholder="例如：metersphere 测试环境" />
        </el-form-item>
        <el-form-item label="平台类型">
          <el-select v-model="newPlatform.type" placeholder="选择平台类型">
            <el-option label="metersphere" value="metersphere" />
            <el-option label="TestCenter" value="testcenter" />
            <el-option label="MeterSphere Cloud" value="metersphere-cloud" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="平台地址">
          <el-input v-model="newPlatform.url" placeholder="http://metersphere.example.com" />
        </el-form-item>
        <el-form-item label="API Token">
          <el-input v-model="newPlatform.token" type="password" show-password placeholder="平台 API Token" />
        </el-form-item>
        <el-form-item label="绑定引擎">
          <el-select v-model="newPlatform.engineId" placeholder="选择要绑定的引擎节点">
            <el-option v-for="n in engineNodes" :key="n.id" :label="n.name" :value="n.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="newPlatform.remark" type="textarea" :rows="2" placeholder="可选备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPlatform = false">取消</el-button>
        <el-button type="primary" @click="addPlatform">保存</el-button>
      </template>
    </el-dialog>

    <!-- 新建定时任务弹窗 -->
    <el-dialog v-model="showAddSchedule" title="新建定时任务" width="560px">
      <el-form :model="newSchedule" label-width="110px">
        <el-form-item label="任务名称">
          <el-input v-model="newSchedule.name" placeholder="例如：每日接口回归测试" />
        </el-form-item>
        <el-form-item label="来源平台">
          <el-select v-model="newSchedule.platform" placeholder="选择平台">
            <el-option v-for="p in platforms" :key="p.id" :label="p.name" :value="p.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发方式">
          <el-radio-group v-model="newSchedule.trigger">
            <el-radio value="cron">Cron 定时</el-radio>
            <el-radio value="manual">手动触发</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="newSchedule.trigger === 'cron'" label="Cron 表达式">
          <el-input v-model="newSchedule.cron" placeholder="0 0 9 * * ?" />
          <div class="form-tip">格式：秒 分 时 日 月 周（例：每天9点执行）</div>
        </el-form-item>
        <el-form-item label="通知渠道">
          <el-select v-model="newSchedule.notifyChannels" multiple placeholder="选择通知渠道">
            <el-option v-for="ch in notifyChannels.filter(c => c.enabled)" :key="ch.id" :label="ch.name" :value="ch.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddSchedule = false">取消</el-button>
        <el-button type="primary" @click="addSchedule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Back, Plus } from '@element-plus/icons-vue'

const activeTab = ref('platform')
const showAddPlatform = ref(false)
const showAddSchedule = ref(false)
const scheduleStatus = ref('')

const platforms = ref([
  { id: 1, name: 'metersphere 生产', type: 'metersphere', url: 'http://metersphere.example.com', engineId: 'engine-1', status: 'connected' },
  { id: 2, name: 'TestCenter UAT', type: 'testcenter', url: 'http://tc.example.com', engineId: 'engine-1', status: 'disconnected' },
])

const engineNodes = ref([
  {
    id: 'engine-1',
    name: '主引擎节点',
    icon: '🖥️',
    version: '1.0.0',
    status: 'online',
    tasks: 2847,
    passRate: 93,
    cpu: 23,
    mem: 41,
    capabilities: ['接口测试', 'UI自动化', '性能测试']
  },
  {
    id: 'engine-2',
    name: '性能专用节点',
    icon: '⚡',
    version: '1.0.0',
    status: 'online',
    tasks: 156,
    passRate: 88,
    cpu: 67,
    mem: 72,
    capabilities: ['性能测试', '压测场景']
  }
])

const schedules = ref([
  { id: 1, name: '每日接口回归', trigger: 'cron', cron: '0 0 9 * * ?', platform: 'metersphere 生产', lastRun: '2026-05-17 09:00', nextRun: '2026-05-18 09:00', status: 'completed' },
  { id: 2, name: '每周全面测试', trigger: 'cron', cron: '0 30 18 * * ?', platform: 'metersphere 生产', lastRun: '2026-05-16 18:30', nextRun: '2026-05-23 18:30', status: 'completed' },
  { id: 3, name: '发布前冒烟测试', trigger: 'manual', cron: '', platform: 'TestCenter UAT', lastRun: '-', nextRun: '-', status: 'idle' },
])

const notifyChannels = ref([
  { id: 'wecom', name: '企业微信', icon: '💬', enabled: true, webhook: '', notifyOnPass: false, notifyOnFail: true, notifyOnComplete: true },
  { id: 'dingtalk', name: '钉钉', icon: '🔔', enabled: false, webhook: '', notifyOnPass: false, notifyOnFail: true, notifyOnComplete: false },
  { id: 'feishu', name: '飞书', icon: '📱', enabled: false, webhook: '', notifyOnPass: false, notifyOnFail: true, notifyOnComplete: false },
])

const newPlatform = reactive({
  name: '',
  type: '',
  url: '',
  token: '',
  engineId: '',
  remark: ''
})

const newSchedule = reactive({
  name: '',
  platform: '',
  trigger: 'cron',
  cron: '',
  notifyChannels: []
})

const statusTagType = (status) => {
  const map = { running: 'warning', completed: 'success', failed: 'danger', idle: 'info', cancelled: 'info' }
  return map[status] || 'info'
}

const statusText = (status) => {
  const map = { running: '执行中', completed: '已完成', failed: '已失败', idle: '空闲', cancelled: '已取消' }
  return map[status] || status
}

const testConnection = (row) => {
  ElMessage.info(`正在测试连接：${row.name}`)
  setTimeout(() => ElMessage.success(`连接成功！引擎与 ${row.name} 通信正常`), 800)
}

const editPlatform = (row) => {
  ElMessage.info('编辑功能开发中')
}

const deletePlatform = (row) => {
  const idx = platforms.value.findIndex(p => p.id === row.id)
  if (idx !== -1) platforms.value.splice(idx, 1)
  ElMessage.success('平台已删除')
}

const addPlatform = () => {
  if (!newPlatform.name || !newPlatform.url) {
    ElMessage.warning('请填写平台名称和地址')
    return
  }
  const id = platforms.value.length + 1
  platforms.value.push({ id, ...newPlatform, status: 'disconnected' })
  showAddPlatform.value = false
  Object.assign(newPlatform, { name: '', type: '', url: '', token: '', engineId: '', remark: '' })
  ElMessage.success('平台添加成功')
}

const runNow = (row) => {
  row.status = 'running'
  ElMessage.success(`任务「${row.name}」已开始执行`)
  setTimeout(() => {
    row.status = 'completed'
    row.lastRun = new Date().toLocaleString('zh-CN', { hour12: false })
    ElMessage.success('任务执行完成')
  }, 2000)
}

const editSchedule = () => {
  ElMessage.info('编辑功能开发中')
}

const deleteSchedule = (row) => {
  const idx = schedules.value.findIndex(s => s.id === row.id)
  if (idx !== -1) schedules.value.splice(idx, 1)
  ElMessage.success('定时任务已删除')
}

const addSchedule = () => {
  if (!newSchedule.name) {
    ElMessage.warning('请填写任务名称')
    return
  }
  const id = schedules.value.length + 1
  schedules.value.push({ id, ...newSchedule, lastRun: '-', nextRun: '-', status: 'idle' })
  showAddSchedule.value = false
  Object.assign(newSchedule, { name: '', platform: '', trigger: 'cron', cron: '', notifyChannels: [] })
  ElMessage.success('定时任务创建成功')
}

const toggleNotify = (ch) => {
  ElMessage.success(`${ch.name}已${ch.enabled ? '启用' : '禁用'}`)
}

const testNotify = (ch) => {
  if (!ch.webhook) {
    ElMessage.warning('请先填写 Webhook 地址')
    return
  }
  ElMessage.success('测试通知已发送，请查收')
}
</script>

<style scoped>
.test-platform-v3 {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.tool-title {
  font-size: 20px;
  color: #333;
  margin: 0;
  flex: 1;
}

/* Banner */
.platform-banner {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 16px;
  color: white;
}

.banner-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.banner-title {
  font-size: 18px;
  margin: 0 0 8px 0;
  font-weight: 700;
}

.banner-desc {
  margin: 0;
  font-size: 14px;
  color: #b8c5d6;
  line-height: 1.7;
}

.banner-diagram {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.diagram-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 12px 20px;
  min-width: 120px;
}

.diagram-node span {
  font-size: 14px;
  font-weight: 600;
}

.diagram-node small {
  font-size: 11px;
  color: #b8c5d6;
}

.diagram-arrow {
  font-size: 20px;
  color: #4da6ff;
  font-weight: bold;
}

.main-tabs {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.pane-content {
  min-height: 400px;
}

/* 通用 */
.section-intro {
  margin-bottom: 16px;
}

.section-intro h4 {
  margin: 0 0 6px 0;
  font-size: 15px;
  color: #333;
}

.section-intro p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.add-platform {
  margin-top: 16px;
}

/* 平台接入 */
.connect-guide {
  margin-top: 24px;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px;
}

.connect-guide h4 {
  margin: 0 0 16px 0;
  font-size: 15px;
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.guide-step {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

/* 引擎卡片 */
.engine-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.engine-card {
  background: #f9fafb;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 18px;
}

.engine-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.engine-icon {
  font-size: 32px;
}

.engine-info {
  flex: 1;
}

.engine-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.engine-version {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.engine-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
}

.stat-val {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.stat-lbl {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.engine-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

/* 定时任务 */
.schedule-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 10px;
  flex-wrap: wrap;
}

.cron-code {
  font-family: 'Consolas', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  color: #667eea;
}

/* 通知渠道 */
.notify-channels {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.notify-card {
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px;
  transition: all 0.3s;
}

.notify-card.active {
  border-color: #667eea;
  background: #f8f7ff;
}

.notify-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.notify-icon {
  font-size: 28px;
}

.notify-info {
  flex: 1;
}

.notify-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.notify-status {
  font-size: 12px;
  color: #909399;
}

.notify-config {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notify-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

@media screen and (max-width: 768px) {
  .test-platform-v3 {
    padding: 10px;
  }

  .platform-banner {
    padding: 16px;
  }

  .banner-diagram {
    flex-direction: column;
    gap: 8px;
  }

  .diagram-arrow {
    transform: rotate(90deg);
  }

  .engine-cards {
    grid-template-columns: 1fr;
  }

  .notify-channels {
    grid-template-columns: 1fr;
  }
}
</style>

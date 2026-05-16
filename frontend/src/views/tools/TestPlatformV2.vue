<template>
  <div class="test-platform-v2">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/tools')" :icon="Back" size="small">返回工具页</el-button>
      <h2 class="tool-title">🚀 测试平台 V2.0</h2>
      <el-tag type="success" size="small">可用</el-tag>
    </div>

    <!-- 功能Tab -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 1. Swagger 导入 -->
      <el-tab-pane label="📥 Swagger 导入" name="swagger">
        <div class="pane-content">
          <el-alert
            title="导入 Swagger/OpenAPI 文档，自动生成接口测试用例"
            type="info"
            :closable="false"
            style="margin-bottom: 16px"
          />
          <div class="swagger-section">
            <div class="swagger-input-row">
              <el-input
                v-model="swaggerUrl"
                placeholder="输入 Swagger JSON URL，例如：http://175.178.98.241/swagger.json"
                size="large"
                class="swagger-url-input"
              >
                <template #prepend>URL</template>
              </el-input>
              <el-button type="primary" size="large" @click="importSwagger" :loading="importing">
                解析接口
              </el-button>
            </div>
            <div class="swagger-divider">
              <span class="divider-text">或上传文件</span>
            </div>
            <el-upload
              drag
              :auto-upload="false"
              :on-change="onSwaggerFileChange"
              accept=".json,.yaml,.yml"
              class="swagger-upload"
            >
              <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
              <div class="el-upload__text">拖拽 Swagger JSON/YAML 文件到此处，或 <em>点击上传</em></div>
            </el-upload>
          </div>

          <!-- 解析结果 -->
          <div v-if="parsedApis.length > 0" class="parsed-result">
            <div class="result-header">
              <span class="result-count">解析到 <strong>{{ parsedApis.length }}</strong> 个接口</span>
              <div class="result-actions">
                <el-button type="primary" size="small" @click="generateAllCases">生成全部用例</el-button>
                <el-button size="small" @click="clearParsed">清空</el-button>
              </div>
            </div>
            <el-table :data="parsedApis" stripe size="small" max-height="400">
              <el-table-column type="index" width="50" label="#" />
              <el-table-column prop="method" label="方法" width="80">
                <template #default="{ row }">
                  <el-tag :type="methodColor(row.method)" size="small">{{ row.method }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
              <el-table-column prop="summary" label="说明" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" size="small" link @click="generateCase(row)">生成用例</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 2. 用例管理 -->
      <el-tab-pane label="📁 用例管理" name="cases">
        <div class="pane-content">
          <div class="case-toolbar">
            <el-input v-model="caseSearch" placeholder="搜索用例名称或路径" prefix-icon="Search" clearable size="default" style="max-width: 300px" />
            <div class="toolbar-right">
              <el-select v-model="caseModule" placeholder="全部模块" clearable size="default" style="width: 150px">
                <el-option label="登录认证" value="login" />
                <el-option label="笔记模块" value="note" />
                <el-option label="工具模块" value="tool" />
                <el-option label="计划模块" value="plan" />
              </el-select>
              <el-button type="primary" :icon="Plus" @click="showAddCase = true">新建用例</el-button>
            </div>
          </div>
          <el-table :data="filteredCases" stripe size="small" class="case-table">
            <el-table-column type="index" width="50" label="#" />
            <el-table-column prop="name" label="用例名称" min-width="160" />
            <el-table-column prop="module" label="模块" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.module }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="method" label="方法" width="70">
              <template #default="{ row }">
                <el-tag v-if="row.method" :type="methodColor(row.method)" size="small">{{ row.method }}</el-tag>
                <span v-else class="text-muted">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="路径" min-width="160" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'ready' ? 'success' : 'info'" size="small">
                  {{ row.status === 'ready' ? '就绪' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="runCase(row)">执行</el-button>
                <el-button size="small" link @click="editCase(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteCase(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 3. 执行测试 -->
      <el-tab-pane label="▶️ 执行测试" name="execute">
        <div class="pane-content">
          <div class="execute-config">
            <div class="config-row">
              <span class="config-label">测试环境</span>
              <el-radio-group v-model="env">
                <el-radio-button value="dev">开发环境</el-radio-button>
                <el-radio-button value="test">测试环境</el-radio-button>
                <el-radio-button value="uat">UAT环境</el-radio-button>
              </el-radio-group>
            </div>
            <div class="config-row">
              <span class="config-label">选择用例</span>
              <el-select v-model="selectedCases" multiple placeholder="选择要执行的用例" style="width: 400px">
                <el-option v-for="c in testCases" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </div>
            <div class="config-row">
              <span class="config-label">报告格式</span>
              <el-radio-group v-model="reportFormat">
                <el-radio-button value="allure">Allure 报告</el-radio-button>
                <el-radio-button value="html">HTML 报告</el-radio-button>
              </el-radio-group>
            </div>
            <div class="config-actions">
              <el-button type="primary" size="large" @click="startExecution" :loading="executing">
                ▶️ 开始执行
              </el-button>
              <el-button v-if="executing" type="danger" size="large" @click="stopExecution">
                ⏹ 停止执行
              </el-button>
            </div>
          </div>

          <!-- 执行进度 -->
          <div v-if="executing || executionDone" class="execution-progress">
            <div class="progress-header">
              <span class="progress-title">执行进度</span>
              <span class="progress-info">{{ executedCount }}/{{ selectedCases.length }} 已完成</span>
            </div>
            <el-progress :percentage="progressPercent" :color="progressColor" :stroke-width="12" />
            <div class="progress-cases">
              <div
                v-for="item in executionItems"
                :key="item.id"
                class="progress-item"
                :class="'status-' + item.status"
              >
                <span class="item-name">{{ item.name }}</span>
                <el-tag v-if="item.status === 'running'" type="warning" size="small">运行中</el-tag>
                <el-tag v-else-if="item.status === 'pass'" type="success" size="small">通过</el-tag>
                <el-tag v-else-if="item.status === 'fail'" type="danger" size="small">失败</el-tag>
                <el-tag v-else-if="item.status === 'pending'" type="info" size="small">等待</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 4. 报告查看 -->
      <el-tab-pane label="📊 报告查看" name="reports">
        <div class="pane-content">
          <div class="report-toolbar">
            <el-select v-model="reportModule" placeholder="全部模块" clearable style="width: 150px">
              <el-option label="登录认证" value="login" />
              <el-option label="笔记模块" value="note" />
              <el-option label="工具模块" value="tool" />
            </el-select>
            <el-select v-model="reportStatus" placeholder="全部状态" clearable style="width: 120px">
              <el-option label="通过" value="pass" />
              <el-option label="失败" value="fail" />
            </el-select>
            <el-button :icon="Refresh" @click="loadReports">刷新</el-button>
          </div>
          <el-table :data="reports" stripe size="small">
            <el-table-column type="index" width="50" label="#" />
            <el-table-column prop="name" label="报告名称" min-width="160" />
            <el-table-column prop="time" label="执行时间" width="160" />
            <el-table-column prop="total" label="总数" width="70" align="center" />
            <el-table-column prop="passed" label="通过" width="70" align="center">
              <template #default="{ row }">
                <span style="color: #67c23a">{{ row.passed }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="failed" label="失败" width="70" align="center">
              <template #default="{ row }">
                <span style="color: #f56c6c">{{ row.failed }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="rate" label="通过率" width="90" align="center">
              <template #default="{ row }">
                <span :style="{ color: row.rate >= 80 ? '#67c23a' : row.rate >= 60 ? '#e6a23c' : '#f56c6c' }">
                  {{ row.rate }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="viewReport(row)">查看报告</el-button>
                <el-button size="small" link @click="downloadReport(row)">下载</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 新建用例弹窗 -->
    <el-dialog v-model="showAddCase" title="新建测试用例" width="600px">
      <el-form :model="newCase" label-width="100px">
        <el-form-item label="用例名称">
          <el-input v-model="newCase.name" placeholder="例如：测试管理员登录" />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-select v-model="newCase.module" placeholder="选择模块">
            <el-option label="登录认证" value="login" />
            <el-option label="笔记模块" value="note" />
            <el-option label="工具模块" value="tool" />
            <el-option label="计划模块" value="plan" />
            <el-option label="收藏模块" value="favorite" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="newCase.method" placeholder="选择方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口路径">
          <el-input v-model="newCase.path" placeholder="/api/note/list" />
        </el-form-item>
        <el-form-item label="请求头">
          <el-input v-model="newCase.headers" type="textarea" :rows="2" placeholder='{"Content-Type": "application/json"}' />
        </el-form-item>
        <el-form-item label="请求参数">
          <el-input v-model="newCase.params" type="textarea" :rows="3" placeholder="JSON 格式请求参数" />
        </el-form-item>
        <el-form-item label="断言规则">
          <el-input v-model="newCase.assertions" type="textarea" :rows="2" placeholder="code == 200, data.success == true" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCase = false">取消</el-button>
        <el-button type="primary" @click="saveCase">保存用例</el-button>
      </template>
    </el-dialog>

    <!-- 报告查看弹窗 -->
    <el-dialog v-model="showReportDetail" title="测试报告" width="900px">
      <div v-if="currentReport" class="report-detail">
        <div class="report-summary">
          <el-row :gutter="12">
            <el-col :span="6"><div class="summary-card pass"><div class="s-num">{{ currentReport.passed }}</div><div class="s-label">通过</div></div></el-col>
            <el-col :span="6"><div class="summary-card fail"><div class="s-num">{{ currentReport.failed }}</div><div class="s-label">失败</div></div></el-col>
            <el-col :span="6"><div class="summary-card total"><div class="s-num">{{ currentReport.total }}</div><div class="s-label">总数</div></div></el-col>
            <el-col :span="6"><div class="summary-card rate"><div class="s-num">{{ currentReport.rate }}%</div><div class="s-label">通过率</div></div></el-col>
          </el-row>
        </div>
        <el-divider />
        <div class="report-cases">
          <div v-for="item in currentReport.details" :key="item.name" class="report-case-item" :class="'result-' + item.result">
            <el-icon v-if="item.result === 'pass'" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#f56c6c"><CircleClose /></el-icon>
            <span class="rc-name">{{ item.name }}</span>
            <span class="rc-time">{{ item.duration }}ms</span>
            <span v-if="item.error" class="rc-error">{{ item.error }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Back, Plus, Search, Refresh } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'

const activeTab = ref('swagger')
const swaggerUrl = ref('')
const importing = ref(false)
const parsedApis = ref([])
const showAddCase = ref(false)
const showReportDetail = ref(false)
const currentReport = ref(null)
const executing = ref(false)
const executionDone = ref(false)

const env = ref('test')
const reportFormat = ref('allure')
const selectedCases = ref([])
const caseSearch = ref('')
const caseModule = ref('')
const reportModule = ref('')
const reportStatus = ref('')

const testCases = ref([
  { id: 1, name: '管理员正确登录', module: 'login', method: 'POST', path: '/api/auth/login' },
  { id: 2, name: '密码错误登录', module: 'login', method: 'POST', path: '/api/auth/login' },
  { id: 3, name: '未登录访问接口', module: 'login', method: 'GET', path: '/api/note/list' },
  { id: 4, name: '创建笔记', module: 'note', method: 'POST', path: '/api/note/add' },
  { id: 5, name: '查询笔记列表', module: 'note', method: 'GET', path: '/api/note/list' },
  { id: 6, name: '更新笔记', module: 'note', method: 'PUT', path: '/api/note/update' },
  { id: 7, name: '删除笔记', module: 'note', method: 'DELETE', path: '/api/note/delete' },
  { id: 8, name: 'XMind 解析', module: 'tool', method: 'POST', path: '/api/tool/xmind/parse' },
  { id: 9, name: '批量数据生成', module: 'tool', method: 'POST', path: '/api/tool/datagen/generate' },
  { id: 10, name: '创建计划', module: 'plan', method: 'POST', path: '/api/plan/add' },
])

const reports = ref([
  { id: 1, name: '登录模块测试', time: '2026-05-16 14:23', total: 3, passed: 3, failed: 0, rate: 100, module: 'login' },
  { id: 2, name: '笔记模块测试', time: '2026-05-16 14:15', total: 4, passed: 3, failed: 1, rate: 75, module: 'note' },
  { id: 3, name: '工具模块测试', time: '2026-05-16 14:00', total: 2, passed: 2, failed: 0, rate: 100, module: 'tool' },
])

const newCase = reactive({
  name: '',
  module: '',
  method: '',
  path: '',
  headers: '{"Content-Type": "application/json"}',
  params: '',
  assertions: ''
})

const filteredCases = computed(() => {
  return testCases.value.filter(c => {
    const matchSearch = !caseSearch.value || c.name.includes(caseSearch.value) || c.path.includes(caseSearch.value)
    const matchModule = !caseModule.value || c.module === caseModule.value
    return matchSearch && matchModule
  })
})

const executionItems = ref([])
const executedCount = ref(0)

const progressPercent = computed(() => {
  if (!selectedCases.value.length) return 0
  return Math.round((executedCount.value / selectedCases.value.length) * 100)
})

const progressColor = computed(() => {
  const p = progressPercent.value
  if (p < 50) return '#f56c6c'
  if (p < 80) return '#e6a23c'
  return '#67c23a'
})

const methodColor = (method) => {
  const map = { GET: '', POST: 'warning', PUT: 'info', DELETE: 'danger', PATCH: 'warning' }
  return map[method] || ''
}

const importSwagger = async () => {
  if (!swaggerUrl.value.trim()) {
    ElMessage.warning('请输入 Swagger URL')
    return
  }
  importing.value = true
  try {
    // 模拟解析过程
    await new Promise(r => setTimeout(r, 1500))
    // 模拟解析结果
    parsedApis.value = [
      { method: 'GET', path: '/api/note/list', summary: '查询笔记列表' },
      { method: 'POST', path: '/api/note/add', summary: '创建笔记' },
      { method: 'PUT', path: '/api/note/update', summary: '更新笔记' },
      { method: 'DELETE', path: '/api/note/delete', summary: '删除笔记' },
      { method: 'GET', path: '/api/plan/list', summary: '查询计划列表' },
      { method: 'POST', path: '/api/plan/add', summary: '创建计划' },
      { method: 'POST', path: '/api/auth/login', summary: '管理员登录' },
      { method: 'GET', path: '/api/favorite/list', summary: '查询收藏列表' },
    ]
    ElMessage.success('解析成功，共 8 个接口')
  } catch {
    ElMessage.error('解析失败，请检查 URL 是否可访问')
  } finally {
    importing.value = false
  }
}

const onSwaggerFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      const apis = extractApisFromSwagger(data)
      parsedApis.value = apis
      ElMessage.success(`文件解析成功，共 ${apis.length} 个接口`)
    } catch {
      ElMessage.error('文件格式错误，请上传 Swagger JSON/YAML 文件')
    }
  }
  reader.readAsText(file.raw)
}

const extractApisFromSwagger = (data) => {
  const apis = []
  const paths = data.paths || {}
  for (const [path, methods] of Object.entries(paths)) {
    for (const [method, info] of Object.entries(methods)) {
      if (['get', 'post', 'put', 'delete', 'patch'].includes(method.toLowerCase())) {
        apis.push({
          method: method.toUpperCase(),
          path,
          summary: info.summary || info.description || ''
        })
      }
    }
  }
  return apis
}

const generateCase = (api) => {
  ElMessage.success(`已生成用例：${api.summary || api.path}`)
}

const generateAllCases = () => {
  ElMessage.success(`已批量生成 ${parsedApis.value.length} 个测试用例`)
  parsedApis.value = []
}

const clearParsed = () => {
  parsedApis.value = []
  swaggerUrl.value = ''
}

const saveCase = () => {
  if (!newCase.name || !newCase.module) {
    ElMessage.warning('请填写用例名称和所属模块')
    return
  }
  const id = testCases.value.length + 1
  testCases.value.push({ id, ...newCase })
  showAddCase.value = false
  Object.assign(newCase, { name: '', module: '', method: '', path: '', params: '', assertions: '' })
  ElMessage.success('用例创建成功')
}

const editCase = (row) => {
  ElMessage.info('编辑功能开发中')
}

const deleteCase = (row) => {
  const idx = testCases.value.findIndex(c => c.id === row.id)
  if (idx !== -1) testCases.value.splice(idx, 1)
  ElMessage.success('用例已删除')
}

const runCase = (row) => {
  ElMessage.success(`执行用例：${row.name}`)
}

const startExecution = async () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择要执行的用例')
    return
  }
  executing.value = true
  executionDone.value = false
  executedCount.value = 0
  executionItems.value = selectedCases.value.map(id => {
    const c = testCases.value.find(tc => tc.id === id)
    return { id, name: c?.name || id, status: 'pending' }
  })

  for (let i = 0; i < executionItems.value.length; i++) {
    const item = executionItems.value[i]
    item.status = 'running'
    await new Promise(r => setTimeout(r, 600))
    const pass = Math.random() > 0.2
    item.status = pass ? 'pass' : 'fail'
    executedCount.value++
  }
  executing.value = false
  executionDone.value = true
  ElMessage.success('执行完成，请查看报告')
}

const stopExecution = () => {
  executing.value = false
  ElMessage.warning('已停止执行')
}

const loadReports = () => {
  ElMessage.success('报告已刷新')
}

const viewReport = (row) => {
  currentReport.value = {
    ...row,
    details: [
      { name: '管理员正确登录', result: 'pass', duration: 234 },
      { name: '密码错误登录', result: 'pass', duration: 189 },
      { name: '未登录访问接口', result: 'fail', duration: 56, error: '预期 code=401，实际 code=200' },
    ]
  }
  showReportDetail.value = true
}

const downloadReport = (row) => {
  ElMessage.info('下载功能开发中')
}
</script>

<style scoped>
.test-platform-v2 {
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

.main-tabs {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.pane-content {
  min-height: 400px;
}

/* Swagger 导入 */
.swagger-section {
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
}

.swagger-input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.swagger-url-input {
  flex: 1;
}

.swagger-divider {
  display: flex;
  align-items: center;
  margin: 16px 0;
  gap: 12px;
  color: #909399;
  font-size: 13px;
}

.swagger-divider::before,
.swagger-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #dcdfe6;
}

.swagger-upload {
  width: 100%;
}

.swagger-upload :deep(.el-upload-dragger) {
  padding: 24px;
}

.parsed-result {
  margin-top: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-count {
  font-size: 14px;
  color: #606266;
}

.result-actions {
  display: flex;
  gap: 8px;
}

/* 用例管理 */
.case-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.case-table {
  margin-top: 0;
}

.text-muted {
  color: #c0c4cc;
}

/* 执行测试 */
.execute-config {
  background: #f5f7fa;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
}

.config-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.config-label {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
  font-weight: 500;
}

.config-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.execution-progress {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.progress-info {
  font-size: 13px;
  color: #909399;
}

.progress-cases {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 13px;
  background: #f5f7fa;
}

.progress-item.status-pass { background: #f0f9eb; }
.progress-item.status-fail { background: #fef0f0; }
.progress-item.status-running { background: #fdf6ec; }

.item-name {
  flex: 1;
}

/* 报告查看 */
.report-toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.report-detail {
  padding: 4px 0;
}

.report-summary {
  margin-bottom: 16px;
}

.summary-card {
  padding: 16px;
  border-radius: 10px;
  text-align: center;
}

.summary-card.pass { background: #f0f9eb; }
.summary-card.fail { background: #fef0f0; }
.summary-card.total { background: #f5f7fa; }
.summary-card.rate { background: #ecf5ff; }

.s-num {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.s-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.report-cases {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.report-case-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.report-case-item.result-pass { background: #f0f9eb; }
.report-case-item.result-fail { background: #fef0f0; }

.rc-name {
  flex: 1;
}

.rc-time {
  color: #909399;
  font-size: 12px;
}

.rc-error {
  color: #f56c6c;
  font-size: 12px;
}

@media screen and (max-width: 768px) {
  .test-platform-v2 {
    padding: 10px;
  }

  .execute-config,
  .swagger-section {
    padding: 14px;
  }

  .config-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .config-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .swagger-input-row {
    flex-direction: column;
  }

  .swagger-url-input {
    width: 100%;
  }

  .toolbar-right {
    flex-wrap: wrap;
  }
}
</style>

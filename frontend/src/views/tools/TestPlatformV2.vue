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
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Back, Plus, Search, Refresh } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'
import axios from 'axios'

// ========== API 基础路径（通过 Nginx 直连 Python 引擎） ==========
const API = '/api/tool/test-engine'
const WS_BASE = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/test-engine`

// ========== 状态 ==========
const activeTab = ref('swagger')
const swaggerUrl = ref('')
const importing = ref(false)
const parsedApis = ref([])
const showAddCase = ref(false)
const showReportDetail = ref(false)
const currentReport = ref(null)
const executing = ref(false)
const executionDone = ref(false)
const currentTaskId = ref('')

const env = ref('test')
const reportFormat = ref('allure')
const selectedCases = ref([])
const caseSearch = ref('')
const caseModule = ref('')
const reportModule = ref('')
const reportStatus = ref('')

const testCases = ref([])
const reports = ref([])
const loadingCases = ref(false)
const loadingReports = ref(false)

const newCase = reactive({
  name: '',
  module: '',
  method: '',
  path: '',
  headers: '{"Content-Type": "application/json"}',
  params: '',
  assertions: ''
})

// ========== 初始化 ==========
onMounted(() => {
  loadCases()
  loadReports()
})

// ========== 用例管理（真实 API） ==========
const loadCases = async () => {
  loadingCases.value = true
  try {
    const resp = await axios.get(`${API}/cases`, {
      params: { module: caseModule.value || undefined, search: caseSearch.value || undefined }
    })
    testCases.value = resp.data.cases || []
  } catch (e) {
    console.error('加载用例失败', e)
    // 静默失败，保留旧数据
  } finally {
    loadingCases.value = false
  }
}

const filteredCases = computed(() => {
  return testCases.value.filter(c => {
    const matchSearch = !caseSearch.value || c.name.includes(caseSearch.value) || (c.path || '').includes(caseSearch.value)
    const matchModule = !caseModule.value || c.module === caseModule.value
    return matchSearch && matchModule
  })
})

const saveCase = async () => {
  if (!newCase.name || !newCase.module) {
    ElMessage.warning('请填写用例名称和所属模块')
    return
  }
  try {
    const resp = await axios.post(`${API}/cases`, {
      name: newCase.name,
      module: newCase.module,
      method: newCase.method || 'GET',
      path: newCase.path,
      headers: newCase.headers,
      params: newCase.params,
      assertions: newCase.assertions,
    })
    ElMessage.success('用例创建成功')
    showAddCase.value = false
    Object.assign(newCase, { name: '', module: '', method: '', path: '', params: '', assertions: '' })
    await loadCases()
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
  }
}

const editCase = (row) => {
  Object.assign(newCase, {
    name: row.name || '',
    module: row.module || '',
    method: row.method || 'GET',
    path: row.path || '',
    headers: row.headers || '{"Content-Type": "application/json"}',
    params: row.params || '',
    assertions: row.assertions || ''
  })
  showAddCase.value = true
}

const deleteCase = async (row) => {
  try {
    await axios.delete(`${API}/cases/${row.id}`)
    testCases.value = testCases.value.filter(c => c.id !== row.id)
    ElMessage.success('用例已删除')
  } catch (e) {
    ElMessage.error('删除失败: ' + (e.response?.data?.detail || e.message))
  }
}

const runCase = async (row) => {
  try {
    const resp = await axios.post(`${API}/execute`, {
      module: row.module || 'api',
      case_ids: [String(row.id)],
      priority: 'P1',
    })
    const taskId = resp.data.task_id
    ElMessage.success(`任务已提交: ${taskId}`)
    activeTab.value = 'execute'
    openWebSocket(taskId)
  } catch (e) {
    ElMessage.error('执行失败: ' + (e.response?.data?.detail || e.message))
  }
}

// ========== Swagger 导入 ==========
const importSwagger = async () => {
  if (!swaggerUrl.value.trim()) {
    ElMessage.warning('请输入 Swagger URL')
    return
  }
  importing.value = true
  try {
    const resp = await axios.post(`${API}/swagger/parse-url`, { url: swaggerUrl.value.trim() })
    parsedApis.value = resp.data.apis || []
    ElMessage.success(resp.data.message || `解析成功，共 ${parsedApis.value.length} 个接口`)
  } catch (e) {
    ElMessage.error('解析失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    importing.value = false
  }
}

const onSwaggerFileChange = async (file) => {
  const formData = new FormData()
  formData.append('file', file.raw)
  try {
    const resp = await axios.post(`${API}/swagger/parse-file`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    parsedApis.value = resp.data.apis || []
    ElMessage.success(resp.data.message || `文件解析成功，共 ${parsedApis.value.length} 个接口`)
  } catch (e) {
    // 回退：客户端 JSON 解析
    try {
      const text = await file.raw.text()
      const data = JSON.parse(text)
      parsedApis.value = extractApisFromSwagger(data)
      ElMessage.success(`客户端解析成功，共 ${parsedApis.value.length} 个接口`)
    } catch {
      ElMessage.error('文件解析失败: ' + (e.response?.data?.detail || '格式不支持'))
    }
  }
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

const generateCase = async (api) => {
  try {
    const resp = await axios.post(`${API}/swagger/generate-cases`, { apis: [api] })
    ElMessage.success(resp.data.message || '用例已生成')
    await loadCases()
  } catch (e) {
    ElMessage.error('生成失败: ' + (e.response?.data?.detail || e.message))
  }
}

const generateAllCases = async () => {
  try {
    const resp = await axios.post(`${API}/swagger/generate-cases`, { apis: parsedApis.value })
    ElMessage.success(resp.data.message || `已批量生成用例`)
    parsedApis.value = []
    await loadCases()
  } catch (e) {
    ElMessage.error('批量生成失败: ' + (e.response?.data?.detail || e.message))
  }
}

const clearParsed = () => {
  parsedApis.value = []
  swaggerUrl.value = ''
}

// ========== 执行测试（真实 API + WebSocket） ==========
const executionItems = ref([])
const executedCount = ref(0)
let ws = null

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
    return { id, name: c?.name || String(id), status: 'pending' }
  })

  try {
    // 确定模块（取选中用例最多的 module）
    const modules = {}
    selectedCases.value.forEach(id => {
      const c = testCases.value.find(tc => tc.id === id)
      if (c) modules[c.module] = (modules[c.module] || 0) + 1
    })
    const mainModule = Object.entries(modules).sort((a, b) => b[1] - a[1])[0]?.[0] || 'api'

    const resp = await axios.post(`${API}/execute`, {
      module: mainModule,
      case_ids: selectedCases.value.map(String),
      env: env.value,
      priority: 'P1',
    })
    const taskId = resp.data.task_id
    currentTaskId.value = taskId
    ElMessage.success(`任务已提交: ${taskId}`)

    // 启动 WebSocket 监听实时进度
    openWebSocket(taskId)
  } catch (e) {
    executing.value = false
    ElMessage.error('执行失败: ' + (e.response?.data?.detail || e.message))
  }
}

const openWebSocket = (taskId) => {
  if (ws) { ws.close(); ws = null }

  const url = `${WS_BASE}/${taskId}`
  ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('[WS] connected', taskId)
  }

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      if (msg.type === 'log') {
        // 从日志行解析 pytest 结果
        const line = msg.line || ''
        const testMatch = line.match(/^(test_\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)/)
        if (testMatch) {
          const testName = testMatch[1]
          const testStatus = testMatch[2].toLowerCase()
          const item = executionItems.value.find(it =>
            it.name.includes(testName) || testName.includes(it.name.replace(/\s/g, '_'))
          )
          if (item) {
            item.status = testStatus === 'passed' ? 'pass' : testStatus === 'failed' ? 'fail' : testStatus
            if (item.status !== 'pending' && item.status !== 'running') {
              executedCount.value++
            }
          }
        }
        // 执行完成
        if (line.includes('passed') && (line.includes('failed') || line.includes('==='))) {
          executing.value = false
          executionDone.value = true
          ws.close()
          ws = null
        }
      } else if (msg.type === 'status' || msg.data) {
        const data = msg.data || msg
        if (data.status === 'pass' || data.status === 'fail' || data.status === 'stopped') {
          executing.value = false
          executionDone.value = true
          if (data.result) {
            executedCount.value = data.result.total || executedCount.value
          }
          ws.close()
          ws = null
          // 刷新报告列表
          loadReports()
        }
      }
    } catch {}
  }

  ws.onerror = () => {
    console.error('[WS] error')
  }

  ws.onclose = () => {
    console.log('[WS] closed')
  }
}

const stopExecution = async () => {
  if (!currentTaskId.value) return
  try {
    await axios.post(`${API}/stop/${currentTaskId.value}`)
    ElMessage.warning('已停止执行')
    executing.value = false
    if (ws) { ws.close(); ws = null }
  } catch (e) {
    ElMessage.error('停止失败: ' + (e.response?.data?.detail || e.message))
  }
}

// ========== 报告查看 ==========
const loadReports = async () => {
  loadingReports.value = true
  try {
    const resp = await axios.get(`${API}/reports`)
    reports.value = resp.data.reports || []
  } catch (e) {
    console.error('加载报告失败', e)
  } finally {
    loadingReports.value = false
  }
}

const viewReport = async (row) => {
  try {
    const resp = await axios.get(`${API}/report/${row.id}`)
    const data = resp.data
    currentReport.value = {
      id: data.id,
      name: data.name,
      total: data.result?.total || 0,
      passed: data.result?.passed || 0,
      failed: data.result?.failed || 0,
      rate: data.result?.pass_rate || 0,
      time: new Date(data.created_at * 1000).toLocaleString(),
      status: data.status,
      details: (data.logs || []).filter(l => l.includes('PASSED') || l.includes('FAILED')).map(l => {
        const m = l.match(/^(test_\S+)\s+(PASSED|FAILED)/) || []
        return { name: m[1] || l.substring(0, 60), result: (m[2] || 'pass').toLowerCase(), duration: 0 }
      })
    }
  } catch (e) {
    // 回退：构建基本报告信息
    currentReport.value = {
      ...row,
      details: []
    }
  }
  showReportDetail.value = true
}

const downloadReport = (row) => {
  const url = `${API}/report/${row.id}/download`
  window.open(url, '_blank')
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

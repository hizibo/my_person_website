<template>
  <div class="xmind-tool">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/tools')" :icon="Back" size="small">返回</el-button>
      <h2 class="tool-title">🧪 XMind 转测试用例</h2>
    </div>

    <!-- 使用说明 -->
    <div class="guide-section">
      <el-collapse>
        <el-collapse-item title="📖 使用说明" name="guide">
          <div class="guide-content">
            <p><strong>1. 准备 XMind 文件</strong></p>
            <p>在 XMind 中按以下层级结构组织思维导图：</p>
            <pre class="guide-tree">项目名称（根节点）
├── 模块A
│   ├── 预置条件1
│   │   ├── 测试步骤1
│   │   │   ├── 预期结果1
│   │   │   └── 预期结果2
│   │   └── 测试步骤2
│   │       └── 预期结果3
│   └── 预置条件2
│       └── 测试步骤3
│           └── 预期结果4
└── 模块B
    └── 预置条件3
        └── 测试步骤4
            └── 预期结果5</pre>
            <p><strong>2. 层级说明</strong></p>
            <ul>
              <li><strong>第1层</strong>（根节点）→ 项目名称，<em>不生成用例</em></li>
              <li><strong>第2层</strong> → <el-tag size="small">所属模块</el-tag></li>
              <li><strong>第3层</strong> → <el-tag size="small" type="warning">预置条件</el-tag></li>
              <li><strong>第4层</strong> → <el-tag size="small" type="info">测试步骤</el-tag></li>
              <li><strong>第5层及以下</strong> → <el-tag size="small" type="success">预期结果</el-tag></li>
            </ul>
            <p><strong>3. 用例名生成规则</strong></p>
            <p>用例名称 = <strong>预置条件</strong> _ <strong>测试步骤</strong> _ <strong>预期结果</strong>（下划线连接）</p>
            <p><strong>4. 优先级规则</strong></p>
            <ul>
              <li>4层深度（项目→模块→预置条件→步骤）→ <el-tag type="danger" size="small">P0</el-tag></li>
              <li>5层深度（再加1层预期结果）→ <el-tag type="warning" size="small">P1</el-tag></li>
              <li>6层及以上 → <el-tag type="info" size="small">P2</el-tag></li>
            </ul>
            <p><strong>5. 转换结果说明</strong></p>
            <ul>
              <li><strong>识别数</strong>：识别到"预置条件"层级的节点数量（表示有多少条有基本的模块-预置条件结构）</li>
              <li><strong>转换成功数</strong>：实际生成测试用例的数量（需要至少4层：模块→预置条件→步骤→预期结果）</li>
              <li>层数不足的分支会被自动跳过，不影响其他正常用例</li>
            </ul>
            <p><strong>⚠️ 注意事项</strong></p>
            <ul>
              <li>仅支持 <code>.xmind</code> 格式文件（XMind 8 及以上版本）</li>
              <li>每个分支必须至少包含"模块→预置条件→测试步骤→预期结果"4层才会生成用例</li>
              <li>缺少步骤或预期结果的分支会被跳过，转换结果中会显示跳过数量</li>
              <li>叶子节点即预期结果层，同一步骤下可添加多个预期结果</li>
            </ul>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".xmind"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽 XMind 文件到此处，或 <em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .xmind 格式文件</div>
        </template>
      </el-upload>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar" v-if="fileData">
      <el-button type="primary" @click="parseXmind" :loading="loading" :icon="Upload" size="small">
        转换为测试用例
      </el-button>
      <el-button @click="previewResult" :icon="View" size="small">预览结果</el-button>
    </div>

    <!-- 转换统计 -->
    <div class="stats-section" v-if="parseDone">
      <el-alert
        :title="`识别到 ${recognizedCount} 条，转换成功 ${convertedCount} 条${recognizedCount - convertedCount > 0 ? `（跳过 ' + (recognizedCount - convertedCount) + ' 条，结构不满足）` : ''}`"
        :type="convertedCount > 0 ? 'success' : 'warning'"
        :closable="false"
        show-icon
      />
    </div>

    <!-- 结果预览 -->
    <div class="result-section" v-if="testCases.length > 0">
      <div class="result-header">
        <h3 class="result-title">📊 转换结果预览</h3>
        <span class="case-count">共 {{ testCases.length }} 条用例</span>
      </div>

      <div class="table-wrapper">
        <el-table :data="testCases" stripe border style="width: 100%" size="small">
          <el-table-column prop="module" label="所属模块" width="120" />
          <el-table-column prop="feature" label="预置条件" width="150" show-overflow-tooltip />
          <el-table-column prop="caseName" label="用例名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="priority" label="优先级" width="70">
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="steps" label="测试步骤" min-width="120" show-overflow-tooltip />
          <el-table-column prop="expected" label="预期结果" min-width="120" show-overflow-tooltip />
        </el-table>
      </div>

      <!-- 导出按钮 -->
      <div class="export-bar">
        <el-button type="success" @click="exportExcel" :icon="Download" size="small">导出 Excel</el-button>
        <el-button type="warning" @click="exportXmind" :icon="Document" size="small">导出文档</el-button>
      </div>
    </div>

    <!-- 树形结构预览 -->
    <div class="tree-section" v-if="mindmapData">
      <h3 class="tree-title">🌲 思维导图结构预览</h3>
      <div class="tree-wrapper">
        <el-tree :data="treeData" :props="treeProps" default-expand-all />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { UploadFilled, Upload, View, Download, Document, Back } from '@element-plus/icons-vue'

const fileData = ref(null)
const loading = ref(false)
const testCases = ref([])
const mindmapData = ref(null)
const treeData = ref([])
const parseDone = ref(false)
const recognizedCount = ref(0)
const convertedCount = ref(0)

const treeProps = {
  children: 'children',
  label: 'label'
}

const handleFileChange = (file) => {
  fileData.value = file
}

const parseXmind = async () => {
  if (!fileData.value) {
    ElMessage.warning('请先上传 XMind 文件')
    return
  }

  loading.value = true
  parseDone.value = false
  try {
    const formData = new FormData()
    formData.append('file', fileData.value.raw)

    const res = await axios.post('/api/tool/xmind/parse-xmind', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    // Python 直接返回，不包裹在 Result 中
    const data = res.data
    testCases.value = data.cases || []
    recognizedCount.value = data.recognizedCount || 0
    convertedCount.value = data.convertedCount || 0
    parseDone.value = true
    mindmapData.value = data.mindmap
    buildTreeData(mindmapData.value)

    if (convertedCount.value > 0) {
      ElMessage.success(`转换完成：识别 ${recognizedCount.value} 条，成功转换 ${convertedCount.value} 条`)
    } else {
      ElMessage.warning(`识别 ${recognizedCount.value} 条，但无合法用例（请检查层级是否满足：模块→预置条件→步骤→预期结果）`)
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('请求失败，请检查后端服务是否启动')
  } finally {
    loading.value = false
  }
}

const previewResult = () => {
  if (testCases.value.length === 0) {
    ElMessage.info('请先进行转换')
  }
}

const getPriorityType = (priority) => {
  const map = { 'P0': 'danger', 'P1': 'warning', 'P2': 'info', 'P3': '' }
  return map[priority] || ''
}

const exportExcel = () => {
  if (testCases.value.length === 0) {
    ElMessage.warning('没有可导出的数据')
    return
  }
  const ws = XLSX.utils.json_to_sheet(testCases.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '测试用例')
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  saveAs(new Blob([wbout], { type: 'application/octet-stream' }), '测试用例.xlsx')
  ElMessage.success('Excel 导出成功')
}

const exportXmind = () => {
  ElMessage.info('XMind 文档导出功能开发中')
}

const buildTreeData = (data) => {
  if (!data) return []
  const result = []
  const traverse = (node, parent) => {
    const children = node.topics || []
    children.forEach(child => {
      const item = { label: child.title || '未命名' }
      if (child.topics && child.topics.length > 0) {
        item.children = []
        traverse(child, item)
      }
      parent.push(item)
    })
  }
  if (data.workbook && data.workbook.sheets) {
    data.workbook.sheets.forEach(sheet => {
      const root = { label: sheet.title, children: [] }
      traverse(sheet.rootTopic || {}, root.children)
      result.push(root)
    })
  }
  treeData.value = result
}
</script>

<style scoped>
.xmind-tool {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.tool-title {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.upload-section {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stats-section {
  margin-bottom: 16px;
}

.result-section {
  background: white;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.result-title {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.case-count {
  color: #666;
  font-size: 13px;
}

.table-wrapper {
  overflow-x: auto;
}

.export-bar {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tree-section {
  background: white;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.tree-title {
  font-size: 16px;
  color: #333;
  margin: 0 0 14px 0;
}

.tree-wrapper {
  overflow-x: auto;
}

/* ========== 使用说明样式 ========== */
.guide-section {
  margin-bottom: 20px;
}

.guide-content {
  font-size: 14px;
  color: #555;
  line-height: 1.8;
}

.guide-content p {
  margin: 8px 0 4px;
}

.guide-content ul {
  padding-left: 20px;
  margin: 4px 0 8px;
}

.guide-content li {
  margin: 3px 0;
}

.guide-content code {
  background: #f5f5f5;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 13px;
  color: #e74c3c;
}

.guide-tree {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 8px 0;
  font-family: 'Courier New', Consolas, monospace;
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .xmind-tool {
    padding: 10px;
  }

  .guide-tree {
    font-size: 11px;
    padding: 8px 10px;
  }
}
</style>

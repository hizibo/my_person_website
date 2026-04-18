<template>
  <div class="xmind-tool">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/')" :icon="Back">返回</el-button>
      <h2>🧪 XMind 转测试用例</h2>
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
      <el-button type="primary" @click="parseXmind" :loading="loading" :icon="Upload">
        转换为测试用例
      </el-button>
      <el-button @click="previewResult" :icon="View">预览结果</el-button>
    </div>

    <!-- 结果预览 -->
    <div class="result-section" v-if="testCases.length > 0">
      <div class="result-header">
        <h3>📊 转换结果预览</h3>
        <span class="case-count">共 {{ testCases.length }} 条用例</span>
      </div>

      <el-table :data="testCases" stripe border max-height="400" style="width: 100%">
        <el-table-column prop="module" label="所属模块" width="150" />
        <el-table-column prop="feature" label="功能点" width="150" />
        <el-table-column prop="caseName" label="用例名称" min-width="200" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="precondition" label="前置条件" min-width="150" show-overflow-tooltip />
        <el-table-column prop="steps" label="测试步骤" min-width="200" show-overflow-tooltip />
        <el-table-column prop="expected" label="预期结果" min-width="150" show-overflow-tooltip />
      </el-table>

      <!-- 导出按钮 -->
      <div class="export-bar">
        <el-button type="success" @click="exportExcel" :icon="Download">导出为 Excel</el-button>
        <el-button type="warning" @click="exportXmind" :icon="Document">导出为测试用例文档</el-button>
      </div>
    </div>

    <!-- 树形结构预览 -->
    <div class="tree-section" v-if="mindmapData">
      <h3>🌲 思维导图结构预览</h3>
      <el-tree :data="treeData" :props="treeProps" default-expand-all />
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
  try {
    const formData = new FormData()
    formData.append('file', fileData.value.raw)

    const res = await axios.post('/api/tool/xmind/parse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data.code === 200) {
      testCases.value = res.data.data.cases
      mindmapData.value = res.data.data.mindmap
      ElMessage.success(`转换成功，共 ${testCases.value.length} 条测试用例`)
    } else {
      ElMessage.error(res.data.message || '转换失败')
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

const treeData = ref([])

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
  padding: 20px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.tool-header h2 {
  font-size: 24px;
  color: #333;
}

.upload-section {
  margin-bottom: 30px;
}

.action-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.result-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.result-header h3 {
  font-size: 18px;
  color: #333;
}

.case-count {
  color: #666;
  font-size: 14px;
}

.export-bar {
  margin-top: 20px;
  display: flex;
  gap: 15px;
}

.tree-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.tree-section h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}
</style>

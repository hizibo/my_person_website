<template>
  <div class="website-container">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索网站名称、地址或描述"
        clearable
        @input="onSearch"
        style="width: 300px; margin-right: 16px"
      >
        <template #prefix>
          <el-icon><search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><plus /></el-icon>添加网站
      </el-button>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" v-loading="loading" stripe border style="margin-top: 20px" @row-dblclick="viewWebsite">
      <el-table-column prop="name" label="网站名称" width="180" />
      <el-table-column prop="url" label="网站地址" width="250">
        <template #default="{ row }">
          <div class="url-cell">
            <span class="url-text">{{ row.url }}</span>
            <el-button
              type="text"
              size="small"
              class="copy-btn"
              @click="copyToClipboard(row.url, '网站地址')"
            >
              <el-icon><document-copy /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="account" label="账号" width="150">
        <template #default="{ row }">
          <div v-if="row.account" class="account-cell">
            <span>{{ row.account }}</span>
            <el-button
              type="text"
              size="small"
              class="copy-btn"
              @click="copyToClipboard(row.account, '账号')"
            >
              <el-icon><document-copy /></el-icon>
            </el-button>
          </div>
          <span v-else class="empty-text">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="password" label="密码" width="180">
        <template #default="{ row }">
          <div v-if="row.password" class="password-cell">
            <span>{{ showPassword[row.id] ? row.password : '••••••••' }}</span>
            <div class="password-actions">
              <el-button
                type="text"
                size="small"
                @click="togglePassword(row.id)"
              >
                <el-icon>{{ showPassword[row.id] ? 'Hide' : 'View' }}</el-icon>
              </el-button>
              <el-button
                type="text"
                size="small"
                class="copy-btn"
                @click="copyToClipboard(row.password, '密码')"
              >
                <el-icon><document-copy /></el-icon>
              </el-button>
            </div>
          </div>
          <span v-else class="empty-text">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="showEditDialog(row)">
            编辑
          </el-button>
          <el-button type="danger" link @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="网站名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入网站名称" />
        </el-form-item>
        <el-form-item label="网站地址" prop="url">
          <el-input v-model="formData.url" placeholder="请输入网站地址 (http:// 或 https://)" />
        </el-form-item>
        <el-form-item label="账号" prop="account">
          <el-input v-model="formData.account" placeholder="可选，请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            placeholder="可选，请输入密码"
            :type="showPasswordInForm ? 'text' : 'password'"
          >
            <template #append>
              <el-button
                type="text"
                @click="showPasswordInForm = !showPasswordInForm"
              >
                <el-icon>{{ showPasswordInForm ? 'Hide' : 'View' }}</el-icon>
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :autosize="{ minRows: 3 }"
            placeholder="可选，请输入网站描述"
            maxlength="512"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看网站对话框 -->
    <el-dialog v-model="viewDialogVisible" title="查看网站" width="500" append-to-body class="view-dialog">
      <div class="view-content" v-if="viewForm">
        <div class="view-field">
          <label>网站名称</label>
          <div class="view-value">{{ viewForm.name }}</div>
        </div>
        <div class="view-field">
          <label>网站地址</label>
          <div class="view-value"><a :href="viewForm.url" target="_blank" style="color: #409eff;">{{ viewForm.url }}</a></div>
        </div>
        <div class="view-field">
          <label>账号</label>
          <div class="view-value">{{ viewForm.account || '无' }}</div>
        </div>
        <div class="view-field">
          <label>密码</label>
          <div class="view-value">{{ viewForm.password || '无' }}</div>
        </div>
        <div class="view-field">
          <label>描述</label>
          <div class="view-value article-format">{{ viewForm.description || '无' }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false" size="small">关闭</el-button>
        <el-button type="primary" @click="goEditFromView" :icon="Edit" size="small">修改</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="400px"
    >
      <span>确定要删除该网站记录吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleting">
            删除
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Plus, DocumentCopy, Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 表格数据
const tableData = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const showPassword = ref({}) // 记录每个行密码是否显示

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const formData = reactive({
  id: null,
  name: '',
  url: '',
  account: '',
  password: '',
  description: ''
})
const showPasswordInForm = ref(false)
const submitting = ref(false)

// 删除相关
const deleteDialogVisible = ref(false)
const deletingId = ref(null)
const deleting = ref(false)

// 查看网站
const viewDialogVisible = ref(false)
const viewForm = ref(null)

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入网站名称', trigger: 'blur' },
    { max: 255, message: '网站名称不能超过255个字符', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入网站地址', trigger: 'blur' },
    { max: 1024, message: '网站地址不能超过1024个字符', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+$/,
      message: '请输入正确的网址 (http:// 或 https://)',
      trigger: 'blur'
    }
  ],
  account: [
    { max: 255, message: '账号不能超过255个字符', trigger: 'blur' }
  ],
  password: [
    { max: 255, message: '密码不能超过255个字符', trigger: 'blur' }
  ],
  description: [
    { max: 512, message: '描述不能超过512个字符', trigger: 'blur' }
  ]
}

// 查看网站详情
const viewWebsite = (row) => {
  viewForm.value = { ...row }
  viewDialogVisible.value = true
}

const goEditFromView = () => {
  const row = viewForm.value
  viewDialogVisible.value = false
  showEditDialog(row)
}

// 加载数据
const loadData = async (keyword = '') => {
  loading.value = true
  try {
    let url = '/api/website-bookmark/list'
    if (keyword.trim()) {
      url = `/api/website-bookmark/search?keyword=${encodeURIComponent(keyword.trim())}`
    }
    const response = await axios.get(url)
    if (response.data.code === 200) {
      tableData.value = response.data.data || []
    } else {
      ElMessage.error(response.data.msg || '加载失败')
    }
  } catch (error) {
    ElMessage.error('请求失败：' + (error.message || '网络错误'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 搜索
const onSearch = () => {
  loadData(searchKeyword.value)
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加网站'
  resetForm()
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑网站'
  resetForm()
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    url: row.url,
    account: row.account || '',
    password: row.password || '',
    description: row.description || ''
  })
  dialogVisible.value = true
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(formData, {
    id: null,
    name: '',
    url: '',
    account: '',
    password: '',
    description: ''
  })
  showPasswordInForm.value = false
}

// 对话框关闭处理
const handleDialogClose = (done) => {
  if (formData.name || formData.url || formData.account || formData.password || formData.description) {
    ElMessageBox.confirm('表单内容未保存，确定关闭吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      done()
    }).catch(() => {})
  } else {
    done()
  }
}

// 提交表单（添加或更新）
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const url = formData.id ? '/api/website-bookmark/update' : '/api/website-bookmark/add'
      const method = formData.id ? 'put' : 'post'
      const response = await axios[method](url, formData)
      if (response.data.code === 200) {
        ElMessage.success(formData.id ? '更新成功' : '添加成功')
        dialogVisible.value = false
        loadData(searchKeyword.value)
      } else {
        ElMessage.error(response.data.msg || '操作失败')
      }
    } catch (error) {
      ElMessage.error('请求失败：' + (error.message || '网络错误'))
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 处理删除
const handleDelete = (id) => {
  deletingId.value = id
  deleteDialogVisible.value = true
}

// 确认删除
const confirmDelete = async () => {
  deleting.value = true
  try {
    const response = await axios.delete(`/api/website-bookmark/delete/${deletingId.value}`)
    if (response.data.code === 200) {
      ElMessage.success('删除成功')
      deleteDialogVisible.value = false
      loadData(searchKeyword.value)
    } else {
      ElMessage.error(response.data.msg || '删除失败')
    }
  } catch (error) {
    ElMessage.error('请求失败：' + (error.message || '网络错误'))
    console.error(error)
  } finally {
    deleting.value = false
    deletingId.value = null
  }
}

// 复制到剪贴板
const copyToClipboard = async (text, fieldName) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(`${fieldName} 已复制到剪贴板`)
  } catch (error) {
    // 降级方案
    try {
      const textarea = document.createElement('textarea')
      textarea.value = text
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      ElMessage.success(`${fieldName} 已复制到剪贴板`)
    } catch (fallbackError) {
      ElMessage.error('复制失败，请手动复制')
    }
  }
}

// 切换密码显示
const togglePassword = (id) => {
  showPassword.value[id] = !showPassword.value[id]
  // 如果需要在Vue响应式中强制更新
  showPassword.value = { ...showPassword.value }
}

// 页面加载时获取数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.website-container {
  padding: 20px;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.url-cell, .account-cell, .password-cell {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.url-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.copy-btn {
  margin-left: 8px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.copy-btn:hover {
  opacity: 1;
}

.password-actions {
  display: flex;
  align-items: center;
  margin-left: 8px;
}

.empty-text {
  color: #999;
  font-style: italic;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table__body-wrapper .el-table__row) {
  cursor: pointer;
}

/* ========== 查看对话框样式 ========== */
.view-content {
  padding: 8px 0;
}

.view-field {
  margin-bottom: 20px;
}

.view-field label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
  font-weight: 500;
}

.view-value {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
}

.view-value.article-format {
  background: #fafafa;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  min-height: 80px;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
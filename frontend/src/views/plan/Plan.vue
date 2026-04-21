<template>
  <div class="plan-page">
    <div class="page-header">
      <h1 class="page-title">我的计划</h1>
      <el-tooltip placement="right" effect="light">
        <template #content>
          <div class="info-tooltip-content">
            <p><strong>功能说明：</strong></p>
            <p>• 添加计划：输入标题和描述后点击添加按钮</p>
            <p>• 查看计划：双击列表行查看详情</p>
            <p>• 编辑计划：点击编辑按钮修改计划内容</p>
            <p>• 进度管理：点击修改按钮调整计划进度</p>
            <p>• 搜索功能：输入关键词后点击搜索按钮</p>
          </div>
        </template>
        <el-icon class="info-icon" :size="18"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>

    <!-- 添加计划 / 搜索 -->
    <div class="add-form">
      <el-input v-model="newPlan.title" placeholder="计划标题 / 搜索关键词" class="input-title" clearable />
      <el-input v-model="newPlan.description" placeholder="计划描述" class="input-desc" clearable />
      <el-input-number v-model="newPlan.sort" :min="1" :step="1" placeholder="排序" style="width: 120px" />
      <el-button type="primary" @click="addPlan" :icon="Plus" :loading="adding">添加</el-button>
      <el-button @click="searchPlans" :icon="Search" :loading="searching">搜索</el-button>
    </div>

    <!-- 计划列表 -->
    <div class="plan-list">
      <div class="table-wrapper">
        <el-table :data="plans" style="width: 100%" border v-loading="loading" size="small" @row-dblclick="viewPlan">
          <el-table-column prop="sort" label="排序" width="80">
            <template #default="{ row }">
              {{ row.sort }}
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="120" />
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
          <el-table-column label="进度" width="200">
            <template #default="{ row }">
              <div class="progress-cell">
                <el-progress :percentage="row.progress" :stroke-width="8" :show-text="false" class="progress-bar" />
                <span class="progress-text">{{ row.progress }}%</span>
                <el-button size="small" @click="editProgress(row)" :icon="Edit" class="progress-btn">改</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.updateTime) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="editPlan(row)" :icon="Edit">编辑</el-button>
              <el-button size="small" type="danger" @click="deletePlan(row.id)" :icon="Delete">删</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 查看计划对话框 -->
    <el-dialog v-model="viewDialogVisible" title="查看计划" width="700" append-to-body class="view-dialog">
      <div class="view-content" v-if="viewForm">
        <div class="view-field">
          <label>标题</label>
          <div class="view-value">{{ viewForm.title }}</div>
        </div>
        <div class="view-field">
          <label>描述</label>
          <div class="view-value article-format" v-html="formatDescription(viewForm.description)"></div>
        </div>
        <div class="view-field">
          <label>进度</label>
          <div class="view-value">
            <el-progress :percentage="viewForm.progress" :stroke-width="10" />
          </div>
        </div>
        <div class="view-field">
          <label>排序</label>
          <div class="view-value">{{ viewForm.sort }}</div>
        </div>
        <div class="view-field">
          <label>更新时间</label>
          <div class="view-value">{{ formatDate(viewForm.updateTime) }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false" size="small">关闭</el-button>
        <el-button type="primary" @click="goEditFromView" :icon="Edit" size="small">修改</el-button>
      </template>
    </el-dialog>

    <!-- 编辑计划对话框 -->
    <el-dialog v-model="editDialogVisible" :title="editingCategory ? '编辑分类' : '编辑计划'" width="500" append-to-body>
      <el-form :model="editForm" label-width="70px" size="small">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="6" style="width: 100%" />
        </el-form-item>
        <el-form-item label="进度">
          <el-slider v-model="editForm.progress" show-input :step="5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="editForm.sort" :min="1" :step="1" placeholder="排序号" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="editing" size="small">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改进度对话框 -->
    <el-dialog v-model="progressDialogVisible" title="修改进度" width="350" append-to-body>
      <el-form :model="progressForm" label-width="60px" size="small">
        <el-form-item label="进度">
          <el-slider v-model="progressForm.progress" show-input :step="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="progressDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveProgress" :loading="updatingProgress" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete, Search, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const API_BASE = '/api/plan'

const plans = ref([])
const loading = ref(false)
const adding = ref(false)
const editing = ref(false)
const updatingProgress = ref(false)
const searching = ref(false)
const editingCategory = ref(false)

const newPlan = reactive({ title: '', description: '', sort: null })

const viewDialogVisible = ref(false)
const viewForm = ref(null)

const editDialogVisible = ref(false)
const editForm = reactive({ id: null, title: '', description: '', progress: 0, sort: 0 })

const progressDialogVisible = ref(false)
const progressForm = reactive({ id: null, progress: 0 })

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatDescription = (desc) => {
  if (!desc) return '<span style="color:#999">暂无描述</span>'
  return desc.replace(/\n/g, '<br>')
}

const fetchPlans = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/list`)
    if (response.data && response.data.code === 200) { plans.value = response.data.data }
    else { ElMessage.error('获取计划列表失败') }
  } catch (error) {
    console.error('获取计划列表失败:', error); ElMessage.error('获取计划列表失败')
  } finally {
    loading.value = false
  }
}

const searchPlans = async () => {
  const keyword = newPlan.title.trim()
  if (!keyword) { await fetchPlans(); return }
  searching.value = true
  try {
    const response = await axios.get(`${API_BASE}/search`, { params: { keyword } })
    if (response.data && response.data.code === 200) { plans.value = response.data.data }
    else { ElMessage.error('搜索失败') }
  } catch (error) {
    console.error('搜索计划失败:', error)
    const allPlans = await axios.get(`${API_BASE}/list`)
    if (allPlans.data && allPlans.data.code === 200) {
      const kw = keyword.toLowerCase()
      plans.value = allPlans.data.data.filter(plan =>
        plan.title.toLowerCase().includes(kw) || plan.description.toLowerCase().includes(kw)
      )
    }
  } finally {
    searching.value = false
  }
}

const addPlan = async () => {
  if (!newPlan.title.trim()) { ElMessage.warning('请输入标题'); return }
  if (newPlan.sort != null && newPlan.sort < 1) { ElMessage.warning('排序值必须大于 0'); return }
  adding.value = true
  try {
    const response = await axios.post(`${API_BASE}/add`, { title: newPlan.title, description: newPlan.description, progress: 0, status: 'active', sort: newPlan.sort || 0 })
    if (response.data && response.data.code === 200) {
      ElMessage.success('添加成功'); newPlan.title = ''; newPlan.description = ''; newPlan.sort = null; await fetchPlans()
    } else { ElMessage.error(response.data.message || '添加失败') }
  } catch (error) { console.error('添加计划失败:', error); ElMessage.error('添加计划失败') }
  finally { adding.value = false }
}

const viewPlan = (row) => {
  viewForm.value = { ...row }
  viewDialogVisible.value = true
}

const goEditFromView = () => {
  const row = viewForm.value
  viewDialogVisible.value = false
  editForm.id = row.id; editForm.title = row.title; editForm.description = row.description; editForm.progress = row.progress; editForm.sort = row.sort || 0
  editDialogVisible.value = true
}

const editPlan = (row) => { editForm.id = row.id; editForm.title = row.title; editForm.description = row.description; editForm.progress = row.progress; editForm.sort = row.sort || 0; editDialogVisible.value = true }

const saveEdit = async () => {
  if (editForm.sort != null && editForm.sort < 1) { ElMessage.warning('排序值必须大于 0'); return }
  editing.value = true
  try {
    const response = await axios.put(`${API_BASE}/update`, editForm)
    if (response.data && response.data.code === 200) { ElMessage.success('更新成功'); editDialogVisible.value = false; await fetchPlans() }
    else { ElMessage.error(response.data.message || '更新失败') }
  } catch (error) { console.error('更新计划失败:', error); ElMessage.error('更新计划失败') }
  finally { editing.value = false }
}

const editProgress = (row) => { progressForm.id = row.id; progressForm.progress = row.progress; progressDialogVisible.value = true }

const saveProgress = async () => {
  updatingProgress.value = true
  try {
    const response = await axios.put(`${API_BASE}/update`, { id: progressForm.id, progress: progressForm.progress })
    if (response.data && response.data.code === 200) { ElMessage.success('进度已更新'); progressDialogVisible.value = false; await fetchPlans() }
    else { ElMessage.error(response.data.msg || '更新失败') }
  } catch (error) { console.error('更新进度失败:', error); ElMessage.error('更新进度失败') }
  finally { updatingProgress.value = false }
}

const deletePlan = (id) => {
  ElMessageBox.confirm('确定删除该计划吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    .then(async () => {
      try {
        const response = await axios.delete(`${API_BASE}/delete/${id}`)
        if (response.data && response.data.code === 200) { ElMessage.success('删除成功'); await fetchPlans() }
        else { ElMessage.error(response.data.msg || '删除失败') }
      } catch (error) { console.error('删除计划失败:', error); ElMessage.error('删除计划失败') }
    }).catch(() => {})
}

onMounted(() => { fetchPlans() })
</script>

<style scoped>
.plan-page {
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.info-icon {
  color: #909399;
  cursor: pointer;
  transition: color 0.3s;
}

.info-icon:hover {
  color: #409eff;
}

.info-tooltip-content {
  max-width: 280px;
  line-height: 1.8;
}

.info-tooltip-content p {
  margin: 4px 0;
}

.add-form {
  margin: 16px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.input-title {
  width: 180px !important;
}

.input-desc {
  flex: 1;
  min-width: 150px;
}

.plan-list {
  margin-top: 16px;
}

.table-wrapper {
  overflow-x: auto;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-bar {
  flex: 1;
  min-width: 60px;
}

.progress-text {
  font-size: 12px;
  min-width: 32px;
  text-align: right;
}

.progress-btn {
  flex-shrink: 0;
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

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .plan-page {
    padding: 10px;
  }

  .page-title {
    font-size: 16px;
  }

  .add-form {
    flex-direction: column;
    align-items: stretch;
  }

  .input-title {
    width: 100% !important;
  }

  .add-form .el-button {
    width: 100%;
  }

  .view-dialog :deep(.el-dialog) {
    width: 95% !important;
  }
}

/* ========== 响应式：小手机 ========== */
@media screen and (max-width: 480px) {
  .plan-list .el-table {
    font-size: 12px;
  }
}
</style>

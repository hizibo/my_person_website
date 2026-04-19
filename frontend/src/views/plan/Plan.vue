<template>
  <div class="plan-page">
    <h1>我的计划</h1>
    <p>这里管理我的待办事项，跟踪工作进度。</p>

    <!-- 添加计划表单 -->
    <div class="add-form">
      <el-input v-model="newPlan.title" placeholder="计划标题" style="width: 200px; margin-right: 10px;" />
      <el-input v-model="newPlan.description" placeholder="计划描述" style="width: 300px; margin-right: 10px;" />
      <el-button type="primary" @click="addPlan" :icon="Plus" :loading="adding">添加</el-button>
    </div>

    <!-- 计划列表 -->
    <div class="plan-list">
      <el-table :data="plans" style="width: 100%" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" width="180" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-progress :percentage="row.progress" :stroke-width="10" :show-text="false" style="flex: 1;" />
              <span style="min-width: 40px;">{{ row.progress }}%</span>
              <el-button size="small" @click="editProgress(row)" :icon="Edit">修改</el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="editPlan(row)" :icon="Edit">编辑</el-button>
            <el-button size="small" type="danger" @click="deletePlan(row.id)" :icon="Delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑计划对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑计划" width="500">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="进度">
          <el-slider v-model="editForm.progress" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="editing">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改进度对话框 -->
    <el-dialog v-model="progressDialogVisible" title="修改进度" width="400">
      <el-form :model="progressForm" label-width="80px">
        <el-form-item label="进度">
          <el-slider v-model="progressForm.progress" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="progressDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProgress" :loading="updatingProgress">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const API_BASE = '/api/plan'

const plans = ref([])
const loading = ref(false)
const adding = ref(false)
const editing = ref(false)
const updatingProgress = ref(false)

// 新增计划表单
const newPlan = reactive({
  title: '',
  description: ''
})

// 编辑对话框
const editDialogVisible = ref(false)
const editForm = reactive({
  id: null,
  title: '',
  description: '',
  progress: 0
})

// 进度对话框
const progressDialogVisible = ref(false)
const progressForm = reactive({
  id: null,
  progress: 0
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 获取计划列表
const fetchPlans = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/list`)
    if (response.data && response.data.code === 200) {
      plans.value = response.data.data
    } else {
      ElMessage.error('获取计划列表失败')
    }
  } catch (error) {
    console.error('获取计划列表失败:', error)
    ElMessage.error('获取计划列表失败')
  } finally {
    loading.value = false
  }
}

// 添加计划
const addPlan = async () => {
  if (!newPlan.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  adding.value = true
  try {
    const planData = {
      title: newPlan.title,
      description: newPlan.description,
      progress: 0,
      status: 'active'
    }
    const response = await axios.post(`${API_BASE}/add`, planData)
    if (response.data && response.data.code === 200) {
      ElMessage.success('添加成功')
      newPlan.title = ''
      newPlan.description = ''
      await fetchPlans()
    } else {
      ElMessage.error(response.data.msg || '添加失败')
    }
  } catch (error) {
    console.error('添加计划失败:', error)
    ElMessage.error('添加计划失败')
  } finally {
    adding.value = false
  }
}

// 编辑计划
const editPlan = (row) => {
  editForm.id = row.id
  editForm.title = row.title
  editForm.description = row.description
  editForm.progress = row.progress
  editDialogVisible.value = true
}

// 保存编辑
const saveEdit = async () => {
  editing.value = true
  try {
    const response = await axios.put(`${API_BASE}/update`, editForm)
    if (response.data && response.data.code === 200) {
      ElMessage.success('更新成功')
      editDialogVisible.value = false
      await fetchPlans()
    } else {
      ElMessage.error(response.data.msg || '更新失败')
    }
  } catch (error) {
    console.error('更新计划失败:', error)
    ElMessage.error('更新计划失败')
  } finally {
    editing.value = false
  }
}

// 修改进度
const editProgress = (row) => {
  progressForm.id = row.id
  progressForm.progress = row.progress
  progressDialogVisible.value = true
}

// 保存进度
const saveProgress = async () => {
  updatingProgress.value = true
  try {
    const planData = {
      id: progressForm.id,
      progress: progressForm.progress
    }
    const response = await axios.put(`${API_BASE}/update`, planData)
    if (response.data && response.data.code === 200) {
      ElMessage.success('进度已更新')
      progressDialogVisible.value = false
      await fetchPlans()
    } else {
      ElMessage.error(response.data.msg || '更新失败')
    }
  } catch (error) {
    console.error('更新进度失败:', error)
    ElMessage.error('更新进度失败')
  } finally {
    updatingProgress.value = false
  }
}

// 删除计划
const deletePlan = (id) => {
  ElMessageBox.confirm('确定删除该计划吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const response = await axios.delete(`${API_BASE}/delete/${id}`)
      if (response.data && response.data.code === 200) {
        ElMessage.success('删除成功')
        await fetchPlans()
      } else {
        ElMessage.error(response.data.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除计划失败:', error)
      ElMessage.error('删除计划失败')
    }
  }).catch(() => {
    // 取消
  })
}

// 初始化
onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.plan-page {
  padding: 20px;
}

.add-form {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.plan-list {
  margin-top: 30px;
}
</style>
<template>
  <div class="permission-page">
    <div class="page-header">
      <h2>🔑 权限管理</h2>
      <el-button type="primary" @click="openAddDialog">
        <el-icon><Plus /></el-icon> 新增用户
      </el-button>
    </div>

    <!-- 用户列表 -->
    <el-table :data="users" stripe border style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="用户名" width="150">
        <template #default="{ row }">
          <span>{{ row.username }}</span>
          <el-tag v-if="row.username === 'admin'" type="warning" size="small" style="margin-left: 8px">超级管理员</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="菜单权限" min-width="250">
        <template #default="{ row }">
          <template v-if="row.username === 'admin'">
            <el-tag type="success" size="small">全部权限</el-tag>
          </template>
          <template v-else>
            <el-tag
              v-for="perm in parsePermissions(row.permissions)"
              :key="perm"
              size="small"
              style="margin: 2px 4px 2px 0"
            >
              {{ getMenuLabel(perm) }}
            </el-tag>
            <el-tag v-if="!parsePermissions(row.permissions).length" type="info" size="small">无权限</el-tag>
          </template>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <template v-if="row.username !== 'admin'">
            <el-button type="primary" size="small" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
          </template>
          <span v-else class="disabled-action">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="480px"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form :model="form" label-width="90px">
        <el-form-item label="用户名">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item :label="isEdit ? '新密码' : '密码'">
          <el-input
            v-model="form.password"
            type="password"
            :placeholder="isEdit ? '不修改请留空' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="菜单权限">
          <el-select
            v-model="form.permissions"
            multiple
            placeholder="请选择菜单权限"
            style="width: 100%"
          >
            <el-option
              v-for="menu in menuOptions"
              :key="menu.value"
              :label="menu.label"
              :value="menu.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 菜单权限选项（前端配置，工具页不纳入权限管理）
const menuOptions = [
  { value: 'plan', label: '📋 计划' },
  { value: 'notes', label: '📝 笔记' },
  { value: 'website', label: '🌐 网站' },
  { value: 'permission', label: '🔑 权限管理' }
]

const getMenuLabel = (value) => {
  const opt = menuOptions.find(m => m.value === value)
  return opt ? opt.label : value
}

const parsePermissions = (permissions) => {
  if (!permissions) return []
  return permissions.split(',').filter(p => p.trim())
}

const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitLoading = ref(false)
const editingId = ref(null)

const form = ref({
  username: '',
  password: '',
  permissions: []
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/user/list')
    if (res.data.code === 200) {
      users.value = res.data.data
    } else {
      ElMessage.error(res.data.message || '获取用户列表失败')
    }
  } catch (e) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  form.value = { username: '', password: '', permissions: [] }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    username: row.username,
    password: '',
    permissions: parsePermissions(row.permissions)
  }
  dialogVisible.value = true
}

const resetForm = () => {
  form.value = { username: '', password: '', permissions: [] }
}

const handleSubmit = async () => {
  if (!isEdit.value) {
    // 新增模式校验
    if (!form.value.username.trim()) {
      ElMessage.warning('请输入用户名')
      return
    }
    if (!form.value.password.trim()) {
      ElMessage.warning('请输入密码')
      return
    }
  }

  submitLoading.value = true
  try {
    const permStr = form.value.permissions.join(',')
    if (isEdit.value) {
      const payload = {
        id: editingId.value,
        permissions: permStr
      }
      if (form.value.password.trim()) {
        payload.password = form.value.password
      }
      const res = await axios.put('/api/user/update', payload)
      if (res.data.code === 200) {
        ElMessage.success('更新成功')
        dialogVisible.value = false
        fetchUsers()
      } else {
        ElMessage.error(res.data.message || '更新失败')
      }
    } else {
      const res = await axios.post('/api/user/add', {
        username: form.value.username.trim(),
        password: form.value.password,
        permissions: permStr
      })
      if (res.data.code === 200) {
        ElMessage.success('创建成功')
        dialogVisible.value = false
        fetchUsers()
      } else {
        ElMessage.error(res.data.message || '创建失败')
      }
    }
  } catch (e) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定删除用户 "${row.username}" 吗？此操作不可恢复。`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await axios.delete(`/api/user/delete/${row.id}`)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      fetchUsers()
    } else {
      ElMessage.error(res.data.message || '删除失败')
    }
  } catch (e) {
    // 取消删除
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.permission-page {
  padding: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-header h2 {
  font-size: 20px;
  color: #2c3e50;
  margin: 0;
}

.disabled-action {
  color: #ccc;
}

/* ========== 响应式 ========== */
@media screen and (max-width: 768px) {
  .permission-page {
    padding: 12px;
  }

  .page-header h2 {
    font-size: 17px;
  }

  :deep(.el-table) {
    font-size: 13px;
  }
}
</style>

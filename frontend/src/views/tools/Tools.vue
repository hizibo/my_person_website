<template>
  <div class="tools-page">
    <!-- 登录入口 -->
    <div class="login-bar" v-if="!isLoggedIn">
      <span class="login-tip">🔒 更多功能请先登录</span>
      <el-button type="primary" size="small" @click="showLogin = true">登录</el-button>
    </div>
    <div class="login-bar logged-in" v-else>
      <span class="login-tip">✅ 已登录：{{ username }}</span>
      <el-button size="small" @click="handleLogout">退出登录</el-button>
    </div>

    <!-- 工具分类 -->
    <div class="container">
      <div v-if="tools.length === 0 && !loading" class="empty-wrapper">
        <el-empty description="暂无工具，请联系管理员添加" />
      </div>

      <div v-for="(group, category) in groupedTools" :key="category" class="category">
        <h2 class="category-title">{{ category }}</h2>
        <div class="tool-grid">
          <div
            v-for="tool in group"
            :key="tool.id"
            class="tool-card"
            @click="goTool(tool)"
          >
            <div class="tool-icon">{{ tool.icon }}</div>
            <div class="tool-info">
              <h3 class="tool-name">{{ tool.name }}</h3>
              <p class="tool-desc">{{ tool.description }}</p>
            </div>
            <el-tag v-if="tool.status === 'online'" type="success" size="small">可用</el-tag>
            <el-tag v-else type="info" size="small">开发中</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 登录弹窗 -->
    <el-dialog v-model="showLogin" title="管理员登录" width="380px" :close-on-click-modal="false">
      <el-form :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLogin = false">取消</el-button>
        <el-button type="primary" :loading="loginLoading" @click="handleLogin">登录</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const tools = ref([])
const loading = ref(true)

// 登录状态
const isLoggedIn = ref(!!localStorage.getItem('auth_token'))
const username = ref(localStorage.getItem('auth_username') || '')
const showLogin = ref(false)
const loginLoading = ref(false)
const loginForm = ref({ username: '', password: '' })

const localTools = [
  {
    id: 'xmind2case',
    name: 'XMind 转测试用例',
    icon: '🧪',
    category: '测试工具',
    description: '将 XMind 思维导图一键转换为标准测试用例，支持 Excel/CSV 导出',
    route: '/tools/xmind',
    status: 'online'
  },
  {
    id: 'batch-datagen',
    name: '批量数据生成',
    icon: '🗄️',
    category: '测试工具',
    description: '生成 MySQL/Oracle 批量测试数据 SQL 脚本，支持 Faker 随机与多表关联',
    route: '/tools/datagen',
    status: 'online'
  },
  {
    id: 'json-format',
    name: 'JSON 格式化',
    icon: '📋',
    category: '开发工具',
    description: 'JSON 数据格式化、压缩、校验',
    route: '/tools/json',
    status: 'online'
  }
]

onMounted(async () => {
  try {
    const res = await axios.get('/api/tool/list')
    if (res.data.code === 200) {
      tools.value = res.data.data
    } else {
      tools.value = localTools
    }
  } catch (e) {
    console.log('后端未启动，使用本地数据')
    tools.value = localTools
  } finally {
    loading.value = false
  }
})

const groupedTools = computed(() => {
  const groups = {}
  tools.value.forEach(tool => {
    const cat = tool.category || '其他'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(tool)
  })
  return groups
})

const goTool = (tool) => {
  if (tool.status === 'online') {
    router.push(tool.route)
  }
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loginLoading.value = true
  try {
    const res = await axios.post('/api/auth/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    if (res.data.code === 200) {
      const { token, username: name } = res.data.data
      localStorage.setItem('auth_token', token)
      localStorage.setItem('auth_username', name)
      isLoggedIn.value = true
      username.value = name
      showLogin.value = false
      loginForm.value = { username: '', password: '' }
      window.dispatchEvent(new CustomEvent('auth-change', { detail: { action: 'login' } }))
      ElMessage.success('登录成功')
      // 登录后跳转到计划页
      router.push('/plan')
    } else {
      ElMessage.error(res.data.message || '登录失败')
    }
  } catch (e) {
    ElMessage.error('登录失败，请检查网络连接')
  } finally {
    loginLoading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_username')
  isLoggedIn.value = false
  username.value = ''
  window.dispatchEvent(new CustomEvent('auth-change', { detail: { action: 'logout' } }))
  ElMessage.success('已退出登录')
  router.push('/tools')
}
</script>

<style scoped>
.tools-page {
  height: 100%;
}

.login-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 0 0 12px 12px;
  margin-bottom: 4px;
}

.login-bar.logged-in {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.login-tip {
  font-size: 14px;
  font-weight: 500;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

.empty-wrapper {
  padding: 60px 0;
}

.category {
  margin-bottom: 32px;
}

.category-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #667eea;
}

.tool-grid {
  display: grid;
  /* PC: 3列; 平板: 2列; 手机: 1列 */
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.tool-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 100px;
}

.tool-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border-color: #667eea;
}

.tool-icon {
  font-size: 36px;
  line-height: 1;
}

.tool-name {
  font-size: 16px;
  color: #333;
  font-weight: 600;
  margin: 0;
}

.tool-desc {
  font-size: 13px;
  color: #999;
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

/* ========== 响应式：平板 ========== */
@media screen and (max-width: 1024px) {
  .tool-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .container {
    padding: 12px;
  }
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .tool-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .container {
    padding: 10px;
  }

  .category-title {
    font-size: 16px;
  }

  .tool-card {
    padding: 16px;
    flex-direction: row;
    align-items: flex-start;
    gap: 12px;
  }

  .tool-icon {
    font-size: 28px;
    flex-shrink: 0;
  }

  .tool-info {
    flex: 1;
    min-width: 0;
  }

  .tool-name {
    font-size: 15px;
  }

  .login-bar {
    padding: 10px 16px;
  }

  .login-tip {
    font-size: 13px;
  }
}
</style>

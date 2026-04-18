<template>
  <div class="home">
    <!-- 顶部导航 -->
    <div class="header">
      <div class="header-content">
        <h1 class="logo">🧰 我的工具箱</h1>
        <div class="tool-count">{{ tools.length }} 个工具</div>
      </div>
    </div>

    <!-- 工具分类 -->
    <div class="container">
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

      <!-- 空状态 -->
      <el-empty v-if="tools.length === 0" description="暂无工具，请联系管理员添加" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const tools = ref([])

// 初始工具数据（本地数据，等后端接口开发后替换）
const localTools = [
  {
    id: 'xmind2case',
    name: 'XMind 转测试用例',
    icon: '🧪',
    category: '测试工具',
    description: '将 XMind 思维导图一键转换为标准测试用例，支持 Excel 导出',
    route: '/tools/xmind',
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
      // 后端未启动时使用本地数据
      tools.value = localTools
    }
  } catch (e) {
    console.log('后端未启动，使用本地数据')
    tools.value = localTools
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
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 28px;
  font-weight: 600;
}

.tool-count {
  font-size: 14px;
  opacity: 0.9;
}

.container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.category {
  margin-bottom: 40px;
}

.category-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  padding-left: 12px;
  border-left: 4px solid #667eea;
}

.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.tool-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.tool-icon {
  font-size: 40px;
}

.tool-name {
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.tool-desc {
  font-size: 14px;
  color: #999;
  line-height: 1.6;
}
</style>

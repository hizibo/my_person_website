<template>
  <div class="tools-page">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const tools = ref([])
const loading = ref(true)

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
</script>

<style scoped>
.tools-page {
  height: 100%;
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
}
</style>

<template>
  <div class="json-tool">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/tools')" :icon="Back" size="small">返回</el-button>
      <h2 class="tool-title">📋 JSON 格式化工具</h2>
    </div>

    <!-- 功能按钮区 -->
    <div class="action-bar">
      <el-button type="primary" @click="formatJson" :icon="MagicStick" :loading="processing">格式化</el-button>
      <el-button @click="minifyJson" :icon="Mini">压缩</el-button>
      <el-button @click="validateJson" :icon="CircleCheck" :type="validState === 'valid' ? 'success' : validState === 'invalid' ? 'danger' : ''">校验</el-button>
      <el-button @click="clearAll" :icon="Delete">清空</el-button>
      <el-divider direction="vertical" />
      <el-button @click="copyResult" :icon="DocumentCopy" :disabled="!outputText">复制结果</el-button>
      <el-button @click="sampleJson" :icon="Tickets">示例</el-button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-tip">
      <el-icon :size="16"><WarningFilled /></el-icon>
      <span>{{ errorMsg }}</span>
    </div>

    <!-- 编辑器区 -->
    <div class="editor-wrapper">
      <!-- 左侧：输入 -->
      <div class="editor-panel">
        <div class="panel-header">
          <span class="panel-title">输入 JSON</span>
          <span class="char-count">{{ inputText.length }} 字符</span>
        </div>
        <div class="code-area">
          <textarea
            ref="inputRef"
            v-model="inputText"
            class="code-input"
            placeholder="粘贴或输入 JSON 内容..."
            spellcheck="false"
            @input="onInputChange"
            @keydown.tab.prevent="handleTab"
          ></textarea>
          <!-- 行号 -->
          <div class="line-numbers" v-if="lineNumbers.length > 0">
            <div v-for="n in lineNumbers" :key="n" class="line-num">{{ n }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧：输出 -->
      <div class="editor-panel output-panel">
        <div class="panel-header">
          <span class="panel-title">输出结果</span>
          <span class="char-count">{{ outputText.length }} 字符</span>
        </div>
        <div class="code-area">
          <pre v-if="outputText" class="code-output"><code v-html="highlightedOutput"></code></pre>
          <div v-else class="output-placeholder">
            <span>格式化后的 JSON 将显示在这里</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div v-if="stats" class="stats-bar">
      <el-tag type="info">键值对：{{ stats.keyCount }}</el-tag>
      <el-tag type="info">层数：{{ stats.depth }}</el-tag>
      <el-tag type="info">字符串：{{ stats.stringCount }}</el-tag>
      <el-tag type="info">数字：{{ stats.numberCount }}</el-tag>
      <el-tag type="info">布尔值：{{ stats.boolCount }}</el-tag>
      <el-tag type="info">null：{{ stats.nullCount }}</el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Back, MagicStick, Delete, DocumentCopy, Tickets, CircleCheck, WarningFilled } from '@element-plus/icons-vue'

const inputRef = ref(null)
const inputText = ref('')
const outputText = ref('')
const errorMsg = ref('')
const processing = ref(false)
const validState = ref('')

// 计算行号
const lineNumbers = computed(() => {
  if (!inputText.value) return []
  return Array.from({ length: inputText.value.split('\n').length }, (_, i) => i + 1)
})

// 解析 JSON 获取统计
const getStats = (obj) => {
  let keyCount = 0, stringCount = 0, numberCount = 0, boolCount = 0, nullCount = 0, depth = 0

  const traverse = (val, currentDepth) => {
    depth = Math.max(depth, currentDepth)
    if (Array.isArray(val)) {
      val.forEach(item => traverse(item, currentDepth + 1))
    } else if (val !== null && typeof val === 'object') {
      Object.keys(val).forEach(key => {
        keyCount++
        traverse(val[key], currentDepth + 1)
      })
    } else {
      if (typeof val === 'string') stringCount++
      else if (typeof val === 'number') numberCount++
      else if (typeof val === 'boolean') boolCount++
      else if (val === null) nullCount++
    }
  }
  traverse(obj, 0)
  return { keyCount, stringCount, numberCount, boolCount, nullCount, depth }
}

const stats = computed(() => {
  if (!outputText.value) return null
  try {
    return getStats(JSON.parse(outputText.value))
  } catch {
    return null
  }
})

// 语法高亮
const highlightedOutput = computed(() => {
  if (!outputText.value) return ''
  try {
    const json = JSON.parse(outputText.value)
    const str = JSON.stringify(json, null, 2)
    return str.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
      let cls = 'json-number'
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'json-key'
          match = match.slice(0, -1) + '<span class="json-colon">:</span>'
        } else {
          cls = 'json-string'
        }
      } else if (/true|false/.test(match)) {
        cls = 'json-bool'
      } else if (/null/.test(match)) {
        cls = 'json-null'
      }
      return `<span class="${cls}">${match}</span>`
    })
  } catch {
    return outputText.value.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
})

// 格式化
const formatJson = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请先输入 JSON 内容')
    return
  }
  try {
    const parsed = JSON.parse(inputText.value)
    outputText.value = JSON.stringify(parsed, null, 2)
    errorMsg.value = ''
    validState.value = 'valid'
  } catch (e) {
    const err = e.message
    let hint = err
    if (err.includes('Unexpected token')) {
      hint = `语法错误：${err}（检查引号、逗号、括号是否匹配）`
    }
    errorMsg.value = hint
    validState.value = 'invalid'
    outputText.value = ''
  }
}

// 压缩
const minifyJson = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请先输入 JSON 内容')
    return
  }
  try {
    const parsed = JSON.parse(inputText.value)
    outputText.value = JSON.stringify(parsed)
    errorMsg.value = ''
    validState.value = 'valid'
  } catch (e) {
    errorMsg.value = e.message
    validState.value = 'invalid'
    outputText.value = ''
  }
}

// 校验
const validateJson = () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请先输入 JSON 内容')
    return
  }
  try {
    JSON.parse(inputText.value)
    errorMsg.value = ''
    validState.value = 'valid'
    ElMessage.success('✅ JSON 格式正确')
  } catch (e) {
    errorMsg.value = e.message
    validState.value = 'invalid'
    ElMessage.error(`❌ JSON 格式错误：${e.message}`)
  }
}

// 清空
const clearAll = () => {
  inputText.value = ''
  outputText.value = ''
  errorMsg.value = ''
  validState.value = ''
}

// 复制
const copyResult = async () => {
  if (!outputText.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  try {
    await navigator.clipboard.writeText(outputText.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 示例
const sampleJson = () => {
  inputText.value = JSON.stringify({
    name: "张三",
    age: 28,
    email: "zhangsan@example.com",
    skills: ["Java", "Python", "Vue"],
    address: {
      city: "北京",
      district: "朝阳区"
    },
    active: true,
    salary: null
  }, null, 2)
  formatJson()
}

// 输入变化自动格式化（可选）
const onInputChange = () => {
  // 留空，用户手动触发格式化
}

// Tab 键支持
const handleTab = (e) => {
  const el = inputRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  inputText.value = inputText.value.substring(0, start) + '  ' + inputText.value.substring(end)
  setTimeout(() => {
    el.selectionStart = el.selectionEnd = start + 2
  }, 0)
}
</script>

<style scoped>
.json-tool {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex-shrink: 0;
}

.tool-title {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.action-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.error-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 6px;
  padding: 8px 12px;
  color: #f56c6c;
  font-size: 13px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.editor-wrapper {
  display: flex;
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.editor-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 10px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
}

.char-count {
  font-size: 11px;
  color: #909399;
}

.code-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
}

.code-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  padding: 14px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #333;
  background: #fff;
  overflow-y: auto;
  tab-size: 2;
  white-space: pre;
}

.code-input::placeholder {
  color: #c0c4cc;
}

.line-numbers {
  padding: 14px 8px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  text-align: right;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #b4b6bc;
  user-select: none;
  overflow-y: hidden;
  min-width: 36px;
}

.line-num {
  height: calc(13px * 1.7);
}

.code-output {
  flex: 1;
  margin: 0;
  padding: 14px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #333;
  background: #fff;
  overflow-y: auto;
  white-space: pre;
  word-break: break-all;
}

.output-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  font-size: 13px;
}

/* JSON 语法高亮 */
.code-output :deep(.json-key) { color: #881391; font-weight: 600; }
.code-output :deep(.json-string) { color: #0a7b06; }
.code-output :deep(.json-number) { color: #1565c0; }
.code-output :deep(.json-bool) { color: #c26804; font-weight: 600; }
.code-output :deep(.json-null) { color: #808080; font-style: italic; }
.code-output :deep(.json-colon) { color: inherit; }

/* 统计栏 */
.stats-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
  flex-shrink: 0;
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .json-tool {
    padding: 10px;
    height: auto;
    overflow: auto;
  }

  .editor-wrapper {
    flex-direction: column;
    overflow: visible;
  }

  .editor-panel {
    min-height: 300px;
    overflow: visible;
  }

  .code-area {
    overflow: visible;
  }

  .code-input,
  .code-output {
    overflow-y: scroll;
    min-height: 280px;
  }

  .line-numbers {
    overflow-y: scroll;
  }

  .action-bar {
    gap: 4px;
  }

  .stats-bar {
    margin-top: 8px;
  }
}

/* ========== 响应式：小手机 ========== */
@media screen and (max-width: 480px) {
  .editor-panel {
    min-height: 240px;
  }

  .code-input,
  .code-output {
    min-height: 220px;
    font-size: 12px;
  }
}
</style>

<template>
  <div class="notes-page">
    <div class="page-header">
      <h1 class="page-title">我的笔记</h1>
      <el-tooltip placement="right" effect="light">
        <template #content>
          <div class="info-tooltip-content">
            <p><strong>功能说明：</strong></p>
            <p>• 分类管理：左侧树形结构管理笔记分类</p>
            <p>• 展开/收起：点击分类头部按钮切换全部展开/收起</p>
            <p>• 新建笔记：选择分类后点击新建按钮</p>
            <p>• 查看笔记：双击笔记行查看详情</p>
            <p>• 编辑笔记：单击编辑按钮</p>
            <p>• 搜索功能：支持搜索标题、内容、标签</p>
            <p>• Markdown 编辑：支持左侧编辑、右侧实时预览</p>
          </div>
        </template>
        <el-icon class="info-icon" :size="18"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>

    <!-- 移动端分类切换按钮 -->
    <div class="mobile-category-toggle">
      <el-button @click="showMobileCategory = !showMobileCategory" size="small">
        {{ showMobileCategory ? '收起分类' : '展开分类' }}
      </el-button>
    </div>

    <el-row :gutter="0" class="notes-row">
      <!-- 左侧分类树 -->
      <div class="category-col" :class="{ 'collapsed': categoryCollapsed }">
        <div class="collapse-btn" @click="categoryCollapsed = !categoryCollapsed" :title="categoryCollapsed ? '展开分类' : '收起分类'">
          <el-icon :size="14"><ArrowLeft v-if="!categoryCollapsed" /><ArrowRight v-else /></el-icon>
        </div>
        <div class="category-panel" :class="{ 'mobile-show': showMobileCategory }" :style="{ width: categoryCollapsed ? '0px' : '260px', minWidth: categoryCollapsed ? '0px' : '220px', maxWidth: categoryCollapsed ? '0px' : '320px' }">
          <div class="category-header">
            <span class="category-header-title">分类管理</span>
            <div class="category-header-actions">
              <el-button size="small" @click="toggleExpandAll" :icon="allExpanded ? Fold : Expand" :title="allExpanded ? '全部收起' : '全部展开'" />
              <el-button type="primary" size="small" @click="handleAddCategory" :icon="Plus">新增</el-button>
            </div>
          </div>
          <!-- 分类搜索框 -->
          <div class="category-search">
            <el-input v-model="categorySearchKeyword" placeholder="搜索分类..." clearable size="small" @input="filterCategoryTree">
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
          <!-- 全部笔记选项 -->
          <div class="all-notes-btn" :class="{ active: !selectedCategoryId }" @click="loadAllNotes">
            <el-icon><List /></el-icon>
            <span>全部笔记</span>
          </div>
          <div class="category-tree-wrapper">
            <el-tree ref="categoryTreeRef" :data="filteredCategoryTree" :props="{ label: 'name', children: 'children' }" node-key="id" highlight-current :expand-on-click-node="false" :default-expanded-keys="defaultExpandedKeys" @node-click="handleCategoryClick">
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <span class="node-label">
                    <el-icon v-if="data.children && data.children.length" @click.stop="toggleNodeExpand(node)" style="cursor: pointer; margin-right: 4px;">
                      <ArrowRight v-if="!node.expanded" />
                      <ArrowDown v-else />
                    </el-icon>
                    <span class="category-name">{{ node.label }}</span>
                    <span v-if="data.noteCount > 0" class="note-count-badge">{{ data.noteCount }}</span>
                  </span>
                  <span class="node-actions">
                    <el-button link type="primary" size="small" @click.stop="addChildCategory(data)" :icon="Plus"></el-button>
                    <el-button link type="primary" size="small" @click.stop="editCategory(data)" :icon="Edit"></el-button>
                    <el-button link type="danger" size="small" @click.stop="deleteCategory(data)" :icon="Delete"></el-button>
                  </span>
                </span>
              </template>
            </el-tree>
          </div>
        </div>
      </div>

      <!-- 右侧笔记列表/编辑器 -->
      <div class="notes-col" :style="{ flex: 1, minWidth: 0 }">
        <div class="notes-panel">
          <!-- 笔记列表 -->
          <div v-if="!showEditor" class="notes-list">
            <div class="notes-header">
              <span class="notes-header-title">{{ selectedCategoryName }} ({{ notes.length }})</span>
              <div class="header-actions">
                <el-input v-model="searchKeyword" placeholder="搜索..." style="width: 150px; margin-right: 8px;" clearable @keyup.enter="searchNotes" @clear="searchNotes">
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="searchNotes" :icon="Search" size="small" class="action-btn">搜索</el-button>
                <el-button type="primary" @click="createNewNote" :icon="Plus" size="small" class="action-btn">新建</el-button>
              </div>
            </div>
            <div class="table-wrapper">
              <!-- 统一卡片列表（PC + H5） -->
              <div class="notes-card-list" v-loading="notesLoading">
                <div v-for="note in notes" :key="note.id" class="note-card" @dblclick="viewNote(note)">
                  <div class="note-card-main">
                    <div class="note-card-title-row">
                      <span class="note-card-title" @click="viewNote(note)">{{ note.title }}</span>
                      <span class="note-card-date">{{ formatDate(note.createTime) }}</span>
                    </div>
                    <div class="note-card-summary" v-if="note.summary">{{ note.summary }}</div>
                    <div class="note-card-summary note-card-empty" v-else>暂无摘要</div>
                  </div>
                  <div class="note-card-actions">
                    <el-button size="small" text type="primary" @click="editNote(note)" :icon="Edit" />
                    <el-button size="small" text type="danger" @click="deleteNote(note.id)" :icon="Delete" />
                  </div>
                </div>
                <el-empty v-if="!notesLoading && notes.length === 0" description="暂无笔记" />
              </div>
            </div>
          </div>

          <!-- Markdown 编辑器 -->
          <div v-else class="note-editor">
            <div class="editor-header">
              <div class="editor-header-left">
                <span class="editor-title">{{ editingNoteId ? '编辑笔记' : '新建笔记' }}</span>
                <el-button size="small" text @click="metaCollapsed = !metaCollapsed" class="toggle-meta-btn">
                  <el-icon><component :is="metaCollapsed ? 'ArrowDown' : 'ArrowUp'" /></el-icon>
                  {{ metaCollapsed ? '展开' : '收起' }}
                </el-button>
              </div>
              <div class="editor-actions">
                <el-button size="small" @click="cancelEdit">取消</el-button>
                <el-button type="primary" size="small" @click="saveNote" :loading="savingNote">保存</el-button>
              </div>
            </div>
            <!-- 标题始终可见 -->
            <el-form :model="noteForm" label-width="70px" size="small" class="editor-title-form">
              <el-form-item label="标题" required>
                <el-input v-model="noteForm.title" placeholder="请输入笔记标题" />
              </el-form-item>
            </el-form>
            <!-- 元信息折叠区：分类、标签、摘要 -->
            <el-collapse-transition>
              <div v-show="!metaCollapsed" class="meta-section">
                <el-form :model="noteForm" label-width="70px" size="small">
                  <el-form-item label="分类">
                    <el-select v-model="noteForm.categoryId" placeholder="选择分类" style="width: 100%;">
                      <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="标签">
                    <el-input v-model="noteForm.tags" placeholder="多个标签用逗号分隔" />
                  </el-form-item>
                  <el-form-item label="摘要">
                    <el-input v-model="noteForm.summary" type="textarea" :autosize="{ minRows: 2 }" placeholder="请输入摘要" />
                  </el-form-item>
                </el-form>
              </div>
            </el-collapse-transition>
            <!-- 内容区 - 自动撑满剩余高度 -->
            <div class="editor-content-area">
              <!-- Markdown 编辑 + 预览区 -->
              <!-- 隐藏的图片上传 input -->
              <input
                ref="imageUploadRef"
                type="file"
                accept="image/*"
                style="display: none;"
                @change="handleImageUpload"
              />
              <div class="md-editor-wrapper" @drop="handleDrop" @dragover="handleDragOver">
                <!-- 工具栏 -->
                <div class="md-toolbar">
                  <span class="md-toolbar-label">撰写</span>
                  <div class="md-toolbar-buttons">
                    <el-tooltip content="标题" placement="bottom"><el-button size="small" @click="insertMd('heading')" :icon="Finished" /></el-tooltip>
                    <el-tooltip content="加粗" placement="bottom"><el-button size="small" @click="insertMd('bold')" :icon="WarnTriangleFilled" /></el-tooltip>
                    <el-tooltip content="斜体" placement="bottom"><el-button size="small" @click="insertMd('italic')" :icon="CircleCloseFilled" /></el-tooltip>
                    <el-tooltip content="删除线" placement="bottom"><el-button size="small" @click="insertMd('strike')">~~</el-button></el-tooltip>
                    <el-divider direction="vertical" />
                    <el-tooltip content="行内代码" placement="bottom"><el-button size="small" @click="insertMd('code')">`</el-button></el-tooltip>
                    <el-tooltip content="代码块" placement="bottom"><el-button size="small" @click="insertMd('codeblock')" :icon="Menu" /></el-tooltip>
                    <el-tooltip content="引用" placement="bottom"><el-button size="small" @click="insertMd('quote')" :icon="ChatLineSquare" /></el-tooltip>
                    <el-tooltip content="无序列表" placement="bottom"><el-button size="small" @click="insertMd('ul')" :icon="List" /></el-tooltip>
                    <el-tooltip content="有序列表" placement="bottom"><el-button size="small" @click="insertMd('ol')" :icon="List" /></el-tooltip>
                    <el-divider direction="vertical" />
                    <el-tooltip content="链接" placement="bottom"><el-button size="small" @click="insertMd('link')" :icon="Link" /></el-tooltip>
                    <el-tooltip content="图片" placement="bottom"><el-button size="small" @click="insertMd('image')" :icon="Picture" :loading="imageUploading" /></el-tooltip>
                    <el-tooltip content="分割线" placement="bottom"><el-button size="small" @click="insertMd('hr')" :icon="Minus" /></el-tooltip>
                    <el-tooltip content="表格" placement="bottom"><el-button size="small" @click="insertMd('table')" :icon="Grid" /></el-tooltip>
                  </div>
                  <el-divider class="toolbar-divider" direction="vertical" />
                  <span class="md-toolbar-label preview-label">预览</span>
                </div>
                <!-- 编辑+预览区域 -->
                <div class="md-main">
                  <textarea
                    ref="mdTextareaRef"
                    v-model="noteForm.content"
                    class="md-textarea"
                    placeholder="请输入 Markdown 内容，支持 GFM 语法...（支持拖拽/粘贴图片上传）"
                    @keydown.tab.prevent="handleTabKey"
                    @paste="handlePaste"
                  ></textarea>
                  <div class="md-preview markdown-body" v-html="renderedContent"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-row>

    <!-- 查看笔记对话框 -->
    <el-dialog v-model="viewDialogVisible" fullscreen append-to-body class="view-dialog">
      <template #header>
        <div class="view-dialog-header">
          <h2 class="view-dialog-title">{{ viewForm ? viewForm.title : '' }}</h2>
          <div class="view-dialog-actions">
            <div class="view-meta">
              <el-tag v-if="viewForm" size="small" type="info">{{ viewForm.categoryName }}</el-tag>
              <el-tag v-if="viewForm && viewForm.tags" size="small" type="info" style="margin-left: 6px;">{{ viewForm.tags }}</el-tag>
              <span class="view-date">{{ viewForm ? formatDate(viewForm.createTime) : '' }}</span>
            </div>
            <el-button type="primary" @click="goEditFromView" :icon="Edit" size="small">修改</el-button>
            <el-button type="success" @click="exportNotePdf" :icon="Download" size="small" style="margin-left: 6px;">导出PDF</el-button>
          </div>
        </div>
      </template>
      <div class="view-content" v-if="viewForm">
        <div class="view-summary" v-if="viewForm.summary">
          <p>{{ viewForm.summary }}</p>
        </div>
        <div class="view-body markdown-body" v-html="renderedViewContent"></div>
      </div>
    </el-dialog>

    <!-- 分类对话框 -->
    <el-dialog v-model="addCategoryDialogVisible" :title="editingCategory ? '编辑分类' : '新增分类'" width="400" append-to-body @close="resetCategoryForm">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="categoryForm.parentId" placeholder="根分类" clearable style="width: 100%;">
            <el-option label="根分类" :value="0" />
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="categoryForm.sort" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCategoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory" :loading="savingCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import {
  Plus, Edit, Delete, Search, InfoFilled, Expand, Fold,
  ArrowDown, ArrowRight, ArrowLeft, ArrowUp, Finished, WarnTriangleFilled,
  CircleCloseFilled, Menu, ChatLineSquare, List as ListIcon, Link,
  Picture, Minus, Grid, UploadFilled, Download
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import axios from 'axios'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

const API_BASE = '/api/note'
const CATEGORY_API = '/api/note/category'

// H5端检测（保留用于响应式样式调整）
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// ========== Bug 2 & 3 修复：marked v18 正确配置 ==========
// marked v18+ 使用 Extensions 机制，不再支持 setOptions.highlight
// 配置 marked：启用 GFM、换行、代码高亮
marked.setOptions({
  breaks: true,
  gfm: true
})

// 自定义渲染器：实现代码高亮和图片支持
const renderer = new marked.Renderer()

// marked v18 签名变更：code(token) / image(token)，参数改为对象
renderer.code = function(token) {
  let highlighted
  const lang = token.lang || ''
  const code = token.text || ''

  if (lang && hljs.getLanguage(lang)) {
    try {
      highlighted = hljs.highlight(code, { language: lang }).value
    } catch (e) {
      highlighted = hljs.highlightAuto(code).value
    }
  } else {
    highlighted = hljs.highlightAuto(code).value
  }

  return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
}

renderer.image = function(token) {
  const href = token.href || ''
  const title = token.title || ''
  const text = token.text || ''
  const titleAttr = title ? ` title="${title}"` : ''
  return `<img src="${href}" alt="${text}"${titleAttr} style="max-width: 100%; border-radius: 6px;" />`
}

// 应用自定义渲染器 + 同步模式（marked v18 parse 默认异步，需显式关闭）
marked.use({ renderer, async: false })

// 判断内容是否为纯 HTML（兼容旧富文本数据）
// 注意：代码块中包含 HTML 标签的 Markdown 不是 HTML 内容！
// 先去除代码块和行内代码，再检测是否含有 HTML 标签
const isHtmlContent = (content) => {
  if (!content || typeof content !== 'string') return false
  // 去除代码块 (```...```) 和行内代码 (`...`)
  const stripped = content
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`]*`/g, '')
  // 检查剩余内容是否包含 HTML 标签（排除 Markdown 语法残留）
  return /<\/(?!\/)([a-zA-Z][a-zA-Z0-9]*)\s*>/.test(stripped) &&
         !/^\s*[-*+>\[|#`]/m.test(content)
}

const renderMarkdown = (content) => {
  if (!content) return ''
  if (isHtmlContent(content)) {
    // 旧数据，直接返回 HTML
    return content
  }
  try {
    return marked.parse(content)
  } catch (e) {
    console.error('Markdown 解析错误:', e)
    return content
  }
}

// 移动端分类面板
const showMobileCategory = ref(false)
const categoryCollapsed = ref(false)

// 分类树
const categoryTree = ref([])
const filteredCategoryTree = ref([])
const categoryTreeRef = ref()
const selectedCategoryId = ref(null)
const allExpanded = ref(true)
const defaultExpandedKeys = ref([])

// 分类搜索
const categorySearchKeyword = ref('')
const filterCategoryTree = () => {
  if (!categorySearchKeyword.value.trim()) {
    filteredCategoryTree.value = categoryTree.value
    return
  }
  const keyword = categorySearchKeyword.value.toLowerCase()
  const filterNode = (nodes) => {
    const result = []
    for (const node of nodes) {
      const match = node.name.toLowerCase().includes(keyword)
      const children = node.children ? filterNode(node.children) : []
      if (match || children.length > 0) {
        result.push({ ...node, children })
      }
    }
    return result
  }
  filteredCategoryTree.value = filterNode(categoryTree.value)
}

// 加载全部笔记
const loadAllNotes = async () => {
  selectedCategoryId.value = null
  notesLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/list`)
    if (response.data && response.data.code === 200) { notes.value = response.data.data }
    else { ElMessage.error('获取笔记列表失败') }
  } catch (error) {
    console.error('获取笔记列表失败:', error); ElMessage.error('获取笔记列表失败')
  } finally {
    notesLoading.value = false
  }
}

const selectedCategoryName = computed(() => {
  if (!selectedCategoryId.value) return '全部'
  const find = flatCategories.value.find(cat => cat.id === selectedCategoryId.value)
  return find ? find.name : '未知'
})

// 分类对话框
const addCategoryDialogVisible = ref(false)
const editingCategory = ref(null)
const savingCategory = ref(false)
const categoryForm = reactive({ name: '', parentId: 0, sort: 0 })

// 笔记列表
const notes = ref([])
const notesLoading = ref(false)
const searchKeyword = ref('')

// Markdown 编辑器
const showEditor = ref(false)
const editingNoteId = ref(null)
const mdTextareaRef = ref(null)
const noteForm = reactive({
  title: '',
  categoryId: null,
  content: '',
  summary: '',
  tags: ''
})
const metaCollapsed = ref(false)
const savingNote = ref(false)

// 查看笔记
const viewDialogVisible = ref(false)
const viewForm = ref(null)

// 实时渲染内容
const renderedContent = computed(() => renderMarkdown(noteForm.content))
const renderedViewContent = computed(() => viewForm.value ? renderMarkdown(viewForm.value.content) : '')

// 扁平化分类
const flatCategories = computed(() => {
  const flatten = (nodes, result = []) => {
    nodes.forEach(node => {
      result.push({ id: node.id, name: node.name })
      if (node.children && node.children.length > 0) flatten(node.children, result)
    })
    return result
  }
  return flatten(categoryTree.value)
})

const getAllNodeKeys = () => {
  const keys = []
  const collect = (nodes) => {
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        keys.push(node.id)
        collect(node.children)
      }
    })
  }
  collect(categoryTree.value)
  return keys
}

const toggleExpandAll = () => {
  const tree = categoryTreeRef.value
  if (!tree) return
  if (allExpanded.value) {
    tree.store._getAllNodes().forEach(node => { node.expanded = false })
    allExpanded.value = false
  } else {
    tree.store._getAllNodes().forEach(node => { node.expanded = true })
    allExpanded.value = true
  }
}

const toggleNodeExpand = (node) => { node.expanded = !node.expanded }

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// ========== Markdown 工具栏插入 ==========
const insertMd = (type) => {
  const textarea = mdTextareaRef.value
  if (!textarea) return
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = noteForm.content || ''
  const selected = text.substring(start, end)
  let insert = ''
  let cursorOffset = 0

  switch (type) {
    case 'heading':
      insert = `\n## 标题\n`
      cursorOffset = 4
      break
    case 'bold':
      insert = `**${selected || '粗体文字'}**`
      cursorOffset = selected ? insert.length : 2
      break
    case 'italic':
      insert = `*${selected || '斜体文字'}*`
      cursorOffset = selected ? insert.length : 1
      break
    case 'strike':
      insert = `~~${selected || '删除线文字'}~~`
      cursorOffset = selected ? insert.length : 2
      break
    case 'code':
      insert = `\`${selected || 'code'}\``
      cursorOffset = selected ? insert.length : 1
      break
    case 'codeblock':
      insert = `\n\`\`\`javascript\n${selected || '// 代码'}\n\`\`\`\n`
      cursorOffset = selected ? insert.length : 14
      break
    case 'quote':
      insert = `\n> ${selected || '引用内容'}\n`
      cursorOffset = selected ? insert.length : 3
      break
    case 'ul':
      insert = `\n- ${selected || '列表项'}\n`
      cursorOffset = selected ? insert.length : 3
      break
    case 'ol':
      insert = `\n1. ${selected || '列表项'}\n`
      cursorOffset = selected ? insert.length : 4
      break
    case 'link':
      insert = `[${selected || '链接文字'}](url)`
      cursorOffset = insert.length - 1
      break
    case 'image':
      // 触发图片上传
      triggerImageUpload()
      break
    case 'hr':
      insert = `\n---\n`
      cursorOffset = insert.length
      break
    case 'table':
      insert = `\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |\n`
      cursorOffset = insert.length
      break
    default:
      insert = selected
  }

  noteForm.content = text.substring(0, start) + insert + text.substring(end)
  // 回填后聚焦并定位光标
  textarea.focus()
  setTimeout(() => {
    const pos = start + cursorOffset
    textarea.setSelectionRange(pos, pos)
  }, 0)
}

const handleTabKey = (e) => {
  const textarea = mdTextareaRef.value
  if (!textarea) return
  const start = textarea.selectionStart
  const content = noteForm.content || ''
  noteForm.content = content.substring(0, start) + '  ' + content.substring(start)
  setTimeout(() => { textarea.setSelectionRange(start + 2, start + 2) }, 0)
}

// ========== 图片上传功能 ==========
const imageUploadRef = ref(null)
const imageUploading = ref(false)

const triggerImageUpload = () => {
  if (imageUploadRef.value) {
    imageUploadRef.value.click()
  }
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }

  // 验证文件大小（最大 10MB）
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 10MB')
    return
  }

  imageUploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data && response.data.code === 200) {
      const imageUrl = response.data.data.url
      // 在光标位置插入图片 Markdown 语法
      const textarea = mdTextareaRef.value
      if (textarea) {
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const text = noteForm.content || ''
        const imageMd = `![${file.name}](${imageUrl})`
        noteForm.content = text.substring(0, start) + imageMd + text.substring(end)
        
        // 移动光标到插入内容之后
        setTimeout(() => {
          textarea.focus()
          textarea.setSelectionRange(start + imageMd.length, start + imageMd.length)
        }, 0)
      }
      ElMessage.success('图片上传成功')
    } else {
      ElMessage.error(response.data.msg || '上传失败')
    }
  } catch (error) {
    console.error('图片上传失败:', error)
    ElMessage.error('图片上传失败')
  } finally {
    imageUploading.value = false
    // 清空 input，允许重复上传同一文件
    event.target.value = ''
  }
}

// 拖拽上传支持
const handleDrop = async (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length === 0) return

  const file = files[0]
  if (!file.type.startsWith('image/')) {
    return
  }

  // 复用 handleImageUpload 逻辑
  const fakeEvent = { target: { files: [file], value: '' } }
  await handleImageUpload(fakeEvent)
}

const handleDragOver = (event) => {
  event.preventDefault()
}

// 粘贴上传支持
const handlePaste = async (event) => {
  const items = event.clipboardData.items
  if (!items) return

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.kind === 'file' && item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        const fakeEvent = { target: { files: [file], value: '' } }
        await handleImageUpload(fakeEvent)
      }
      break
    }
  }
}

// ========== Bug 1 修复：分类操作 ==========
const fetchCategories = async () => {
  try {
    const response = await axios.get(`${CATEGORY_API}/list`)
    if (response.data && response.data.code === 200) {
      const categories = response.data.data
      const map = {}
      const tree = []
      categories.forEach(cat => { cat.children = []; map[cat.id] = cat })
      categories.forEach(cat => {
        if (cat.parentId === 0 || !map[cat.parentId]) tree.push(cat)
        else map[cat.parentId].children.push(cat)
      })
      // 递归计算含子分类的总笔记数
      const sumNoteCount = (node) => {
        let total = node.noteCount || 0
        if (node.children) {
          node.children.forEach(child => { total += sumNoteCount(child) })
        }
        node.noteCount = total
        return total
      }
      tree.forEach(node => sumNoteCount(node))
      categoryTree.value = tree
      filteredCategoryTree.value = tree  // 初始化过滤后的树
      defaultExpandedKeys.value = getAllNodeKeys()
      // 默认加载全部笔记，不自动选择第一个分类
      if (!selectedCategoryId.value) {
        loadAllNotes()
      }
    } else {
      ElMessage.error('获取分类失败')
    }
  } catch (error) {
    console.error('获取分类失败:', error)
    ElMessage.error('获取分类失败')
  }
}

const saveCategory = async () => {
  if (!categoryForm.name.trim()) { ElMessage.warning('请输入分类名称'); return }
  savingCategory.value = true
  try {
    // Bug 1 修复：确保 parentId 有默认值
    const submitData = {
      name: categoryForm.name.trim(),
      parentId: categoryForm.parentId === null || categoryForm.parentId === undefined ? 0 : categoryForm.parentId,
      sort: categoryForm.sort || 0
    }
    
    // 如果是编辑，添加 id
    if (editingCategory.value) {
      submitData.id = editingCategory.value
    }
    
    const api = editingCategory.value ? `${CATEGORY_API}/update` : `${CATEGORY_API}/add`
    const response = await axios[editingCategory.value ? 'put' : 'post'](api, submitData)
    if (response.data && response.data.code === 200) {
      ElMessage.success(editingCategory.value ? '更新成功' : '添加成功')
      addCategoryDialogVisible.value = false
      resetCategoryForm()
      await fetchCategories()
    } else {
      ElMessage.error(response.data.message || response.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error('保存分类失败')
  } finally {
    savingCategory.value = false
  }
}

const resetCategoryForm = () => {
  categoryForm.name = ''
  categoryForm.parentId = 0
  categoryForm.sort = 0
  editingCategory.value = null
}

const handleAddCategory = () => {
  resetCategoryForm()
  addCategoryDialogVisible.value = true
}

const addChildCategory = (parentData) => {
  resetCategoryForm()
  categoryForm.parentId = parentData.id
  addCategoryDialogVisible.value = true
}

const editCategory = (data) => {
  editingCategory.value = data.id
  categoryForm.name = data.name
  categoryForm.parentId = data.parentId || 0
  categoryForm.sort = data.sort || 0
  addCategoryDialogVisible.value = true
}

const deleteCategory = async (data) => {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${data.name}" 吗？`, '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    const response = await axios.delete(`${CATEGORY_API}/delete/${data.id}`)
    if (response.data && response.data.code === 200) { 
      ElMessage.success('删除成功'); 
      await fetchCategories() 
    } else { 
      const msg = response.data.msg || response.data.message || '删除失败'
      ElMessage.warning(msg)
    }
  } catch (error) {
    if (error !== 'cancel') { console.error('删除分类失败:', error); ElMessage.error('删除失败') }
  }
}

const handleCategoryClick = (data) => { 
  selectedCategoryId.value = data.id 
  fetchNotesByCategory(data.id) 
}

// 获取笔记（含子分类）
const fetchNotesByCategory = async (categoryId) => {
  notesLoading.value = true
  try {
    // 使用包含子分类的API
    const response = await axios.get(`${API_BASE}/category/${categoryId}/with-children`)
    if (response.data && response.data.code === 200) { notes.value = response.data.data }
    else { ElMessage.error('获取笔记列表失败') }
  } catch (error) {
    console.error('获取笔记列表失败:', error); ElMessage.error('获取笔记列表失败')
  } finally {
    notesLoading.value = false
  }
}

const searchNotes = async () => {
  if (!searchKeyword.value.trim()) { 
    // 无关键词时，根据是否选择分类加载对应笔记
    if (selectedCategoryId.value) {
      fetchNotesByCategory(selectedCategoryId.value)
    } else {
      loadAllNotes()
    }
    return 
  }
  notesLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/search?keyword=${encodeURIComponent(searchKeyword.value)}`)
    if (response.data && response.data.code === 200) { notes.value = response.data.data }
    else { ElMessage.error('搜索失败') }
  } catch (error) {
    console.error('搜索笔记失败:', error); ElMessage.error('搜索失败')
  } finally {
    notesLoading.value = false
  }
}

const createNewNote = () => {
  editingNoteId.value = null
  noteForm.title = ''
  noteForm.categoryId = selectedCategoryId.value
  noteForm.content = ''
  noteForm.summary = ''
  noteForm.tags = ''
  showEditor.value = true
}

const editNote = async (row) => {
  try {
    const response = await axios.get(`${API_BASE}/detail/${row.id}`)
    if (response.data && response.data.code === 200) {
      const note = response.data.data
      editingNoteId.value = note.id
      noteForm.title = note.title
      noteForm.categoryId = note.categoryId
      noteForm.content = note.content || ''
      noteForm.summary = note.summary || ''
      noteForm.tags = note.tags || ''
      showEditor.value = true
    } else { ElMessage.error('获取笔记详情失败') }
  } catch (error) { console.error('获取笔记详情失败:', error); ElMessage.error('获取笔记详情失败') }
}

const viewNote = async (row) => {
  try {
    const response = await axios.get(`${API_BASE}/detail/${row.id}`)
    if (response.data && response.data.code === 200) {
      const note = response.data.data
      const cat = flatCategories.value.find(c => c.id === note.categoryId)
      viewForm.value = { ...note, categoryName: cat ? cat.name : '未知' }
      viewDialogVisible.value = true
    } else { ElMessage.error('获取笔记详情失败') }
  } catch (error) { console.error('获取笔记详情失败:', error); ElMessage.error('获取笔记详情失败') }
}

const goEditFromView = () => {
  const row = { id: viewForm.value.id }
  viewDialogVisible.value = false
  editNote(row)
}

const saveNote = async () => {
  if (!noteForm.title.trim()) { ElMessage.warning('请输入笔记标题'); return }
  if (!noteForm.content.trim()) { ElMessage.warning('请输入笔记内容'); return }
  savingNote.value = true
  try {
    const api = editingNoteId.value ? `${API_BASE}/update` : `${API_BASE}/add`
    const response = await axios[editingNoteId.value ? 'put' : 'post'](api, { ...noteForm, id: editingNoteId.value })
    if (response.data && response.data.code === 200) {
      ElMessage.success(editingNoteId.value ? '更新成功' : '添加成功')
      showEditor.value = false
      await fetchNotesByCategory(selectedCategoryId.value)
    } else { ElMessage.error(response.data.msg || '保存失败') }
  } catch (error) { console.error('保存笔记失败:', error); ElMessage.error('保存失败') }
  finally { savingNote.value = false }
}

const cancelEdit = () => { showEditor.value = false }

const deleteNote = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该笔记吗？', '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    const response = await axios.delete(`${API_BASE}/delete/${id}`)
    if (response.data && response.data.code === 200) { ElMessage.success('删除成功'); await fetchNotesByCategory(selectedCategoryId.value) }
    else { ElMessage.error(response.data.msg || '删除失败') }
  } catch (error) { if (error !== 'cancel') { console.error('删除笔记失败:', error); ElMessage.error('删除失败') } }
}

// ========== PDF 导出功能 ==========
const exportNotePdf = async () => {
  if (!viewForm.value) return
  const loadingInstance = ElLoading.service({ text: '正在生成 PDF...', background: 'rgba(0,0,0,0.5)' })
  try {
    // 创建一个临时 div 用于渲染笔记内容
    const tempDiv = document.createElement('div')
    tempDiv.style.cssText = 'position:fixed;left:-9999px;top:0;width:780px;padding:40px 48px;background:#fff;font-family:"Microsoft YaHei",sans-serif;font-size:14px;line-height:1.8;color:#333;'
    tempDiv.innerHTML = `
      <div style="margin-bottom:12px;">
        <h1 style="font-size:22px;margin:0 0 8px;color:#1a1a1a;">${viewForm.value.title || ''}</h1>
        <div style="font-size:12px;color:#888;">
          <span style="margin-right:12px;">分类：${viewForm.value.categoryName || ''}</span>
          ${viewForm.value.tags ? `<span style="margin-right:12px;">标签：${viewForm.value.tags}</span>` : ''}
          <span>创建时间：${formatDate(viewForm.value.createTime) || ''}</span>
        </div>
        ${viewForm.value.summary ? `<div style="margin-top:16px;padding:12px 16px;background:#f5f7fa;border-left:4px solid #409eff;font-size:13px;color:#555;border-radius:4px;">${viewForm.value.summary}</div>` : ''}
        <div style="height:1px;background:#e8e8e8;margin-top:16px;"></div>
      </div>
      <div class="markdown-body">${renderedViewContent.value || ''}</div>
    `
    document.body.appendChild(tempDiv)
    // 等图片等资源加载完成
    await new Promise(r => setTimeout(r, 800))
    const canvas = await html2canvas(tempDiv, { scale: 2, useCORS: true, allowTaint: false, backgroundColor: '#ffffff' })
    document.body.removeChild(tempDiv)
    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' })
    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()
    const imgW = canvas.width
    const imgH = canvas.height
    const ratio = pageW / imgW
    const scaledH = imgH * ratio
    const margin = 40
    const usableH = pageH - margin * 2
    let currentY = 0
    let page = 0
    while (currentY < scaledH) {
      if (page > 0) pdf.addPage()
      // 计算本页需要截取的高度（canvas 像素）
      const sliceCanvasH = Math.min(usableH / ratio, imgH - currentY / ratio)
      // 创建本页的截取 canvas
      const sliceCanvas = document.createElement('canvas')
      sliceCanvas.width = imgW
      sliceCanvas.height = sliceCanvasH
      const sliceCtx = sliceCanvas.getContext('2d')
      sliceCtx.fillStyle = '#ffffff'
      sliceCtx.fillRect(0, 0, imgW, sliceCanvasH)
      // 从源 canvas 截取对应区域
      sliceCtx.drawImage(canvas, 0, currentY / ratio, imgW, sliceCanvasH, 0, 0, imgW, sliceCanvasH)
      const sliceData = sliceCanvas.toDataURL('image/jpeg', 0.95)
      pdf.addImage(sliceData, 'JPEG', 0, margin, pageW, sliceCanvasH * ratio)
      currentY += sliceCanvasH * ratio
      page++
    }
    const safeTitle = (viewForm.value.title || '笔记').replace(/[/\\:*?"<>|]/g, '_')
    pdf.save(`${safeTitle}.pdf`)
    ElMessage.success('PDF 导出成功')
  } catch (e) {
    console.error('PDF导出失败:', e)
    ElMessage.error('PDF 导出失败：' + (e.message || '未知错误'))
  } finally {
    loadingInstance.close()
  }
}

onMounted(() => { fetchCategories() })
</script>

<style scoped>
.notes-page { padding: 16px; }

.page-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.page-title { font-size: 18px; font-weight: 600; color: #333; }
.info-icon { color: #909399; cursor: pointer; transition: color 0.3s; }
.info-icon:hover { color: #409eff; }
.info-tooltip-content { max-width: 280px; line-height: 1.8; }
.info-tooltip-content p { margin: 4px 0; }

.mobile-category-toggle { display: none; margin-bottom: 12px; }
.notes-row { display: flex; }

/* 分类列 */
.category-col { flex-shrink: 0; display: flex; overflow: visible; position: relative; }
.category-col.collapsed { flex-shrink: 0; }
.category-col.collapsed .category-panel { display: none; }

.collapse-btn {
  flex-shrink: 0; width: 16px; height: 48px; background: #e4e7ed;
  border-radius: 0 4px 4px 0; display: flex; align-items: center;
  justify-content: center; cursor: pointer; z-index: 10;
  transition: background 0.2s; align-self: center; margin-left: -1px;
}
.collapse-btn:hover { background: #c0c4cc; }

.category-panel {
  flex-shrink: 0; transition: width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease;
  overflow: hidden; width: 260px; min-width: 220px; max-width: 320px;
  border: 1px solid #e4e7ed; border-radius: 8px; padding: 12px;
  background: #fff; position: sticky; top: 0; max-height: calc(100vh - 120px);
}
.category-tree-wrapper { overflow-y: auto; max-height: calc(100vh - 180px); }
.category-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
.category-header-title { font-weight: bold; font-size: 14px; }
.category-header-actions { display: flex; align-items: center; gap: 6px; }
.custom-tree-node { flex: 1; display: flex; align-items: center; justify-content: space-between; font-size: 13px; padding-right: 4px; }
.node-label { display: inline-flex; align-items: center; gap: 6px; }
.category-name { line-height: 1; }
.note-count-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; padding: 0 5px;
  font-size: 11px; font-weight: 500; line-height: 1;
  color: #8b949e; background: #f0f2f5; border-radius: 9px;
  user-select: none;
}
.node-actions { opacity: 0; transition: opacity 0.2s; }
.custom-tree-node:hover .node-actions { opacity: 1; }

/* 分类搜索框 */
.category-search {
  padding: 8px 12px;
  border-bottom: 1px solid #ebeef5;
}

/* 全部笔记按钮 */
.all-notes-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
  transition: all 0.2s;
}

.all-notes-btn:hover {
  background: #f5f7fa;
  color: #409eff;
}

.all-notes-btn.active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 500;
}

/* 笔记列 */
.notes-col { flex: 1; min-width: 0; }
.notes-panel { border: 1px solid #e4e7ed; border-radius: 8px; padding: 16px; background: #fff; min-height: 400px; display: flex; flex-direction: column; height: calc(100vh - 120px); overflow: hidden; }
.notes-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.notes-header-title { font-weight: bold; font-size: 14px; }
.header-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; }
.table-wrapper { overflow-x: auto; }
:deep(.el-table__body-wrapper .el-table__row) { cursor: pointer; }

/* 编辑器头部 */
.editor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #ebeef5; padding-bottom: 10px; flex-shrink: 0; }
.editor-header-left { display: flex; align-items: center; gap: 8px; }
.editor-title { font-weight: bold; font-size: 15px; color: #303133; }
.toggle-meta-btn { font-size: 12px; color: #909399 !important; padding: 4px 8px !important; }
.toggle-meta-btn:hover { color: #409eff !important; }
.editor-actions { display: flex; gap: 8px; }
.editor-title-form { flex-shrink: 0; padding: 0; }
.editor-title-form .el-form-item { margin-bottom: 8px; }
.meta-section { padding: 0 0 8px; border-bottom: 1px dashed #ebeef5; margin-bottom: 8px; flex-shrink: 0; }
.meta-section .el-form-item { margin-bottom: 8px; }

/* 笔记编辑器容器 */
.note-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 内容区 - 自动撑满剩余高度 */
.editor-content-area {
  flex: 1;
  min-height: 300px; /* 初始最小高度，确保初始显示 */
  display: flex;
  flex-direction: column;
}
.editor-content-area .md-editor-wrapper {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止内容溢出 */
}
.editor-content-area .md-main {
  flex: 1;
  min-height: 0;
  overflow: hidden; /* 内部通过 textarea/preview 自己滚动 */
}

/* ========== Markdown 编辑器样式 ========== */
.md-editor-wrapper {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.md-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #f8f9fb;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  flex-shrink: 0;
}

.md-toolbar-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  white-space: nowrap;
}

.preview-label {
  margin-left: 4px;
}

.md-toolbar-buttons {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}

.toolbar-divider {
  margin: 0 4px;
  height: 16px;
}

.md-main {
  display: flex;
  flex: 1;
  min-height: 0;
  /* 高度由父容器 editor-content-area 自动撑满 */
}

.md-textarea {
  flex: 1;
  min-width: 0;
  min-height: 200px; /* 初始最小高度 */
  resize: none;
  border: none;
  outline: none;
  padding: 14px 16px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.8;
  color: #24292f;
  background: #fff;
  box-sizing: border-box;
  tab-size: 2;
  overflow-y: auto; /* 内容超出时内部滚动 */
}

.md-textarea::placeholder {
  color: #c0c4cc;
  font-style: italic;
}

.md-preview {
  flex: 1;
  min-width: 0;
  min-height: 200px; /* 初始最小高度 */
  border-left: 1px solid #e4e7ed;
  overflow-y: auto;
  padding: 14px 18px;
  background: #fafafa;
  box-sizing: border-box;
}

/* ========== Markdown 渲染样式（与 GitHub 风格一致） ========== */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  line-height: 1.8;
  color: #24292f;
  word-wrap: break-word;
}

:deep(.markdown-body h1),
:deep(.markdown-body h2),
:deep(.markdown-body h3),
:deep(.markdown-body h4),
:deep(.markdown-body h5),
:deep(.markdown-body h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 8px;
}

:deep(.markdown-body h1) { font-size: 2em; }
:deep(.markdown-body h2) { font-size: 1.5em; }
:deep(.markdown-body h3) { font-size: 1.25em; }
:deep(.markdown-body h4) { font-size: 1em; }

:deep(.markdown-body p) { margin: 0 0 14px; }

:deep(.markdown-body blockquote) {
  margin: 12px 0;
  padding: 4px 16px;
  border-left: 3px solid #d0d7de;
  color: #57606a;
  background: #f6f8fa;
  border-radius: 0 4px 4px 0;
}

:deep(.markdown-body pre) {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 14px 16px;
  overflow-x: auto;
  margin: 12px 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
}

:deep(.markdown-body code) {
  background: #f0f2f5;
  border-radius: 3px;
  padding: 1px 5px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  color: #e74c3c;
}

:deep(.markdown-body pre code) {
  background: transparent;
  border: none;
  padding: 0;
  color: #24292f;
  font-size: 13px;
}

:deep(.markdown-body ul),
:deep(.markdown-body ol) {
  padding-left: 24px;
  margin: 8px 0 12px;
}

:deep(.markdown-body li) { margin: 4px 0; line-height: 1.8; }
:deep(.markdown-body li > ul),
:deep(.markdown-body li > ol) { margin: 4px 0; }

:deep(.markdown-body hr) { border: none; border-top: 1px solid #e1e4e8; margin: 20px 0; }

:deep(.markdown-body a) { color: #0969da; text-decoration: none; }
:deep(.markdown-body a:hover) { text-decoration: underline; }

:deep(.markdown-body img) { max-width: 100%; border-radius: 6px; }

:deep(.markdown-body table) {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
  font-size: 13px;
  overflow-x: auto;
  display: block;
}

:deep(.markdown-body table th),
:deep(.markdown-body table td) {
  border: 1px solid #d0d7de;
  padding: 8px 12px;
  text-align: left;
}

:deep(.markdown-body table th) {
  background: #f6f8fa;
  font-weight: 600;
}

:deep(.markdown-body table tr:nth-child(even)) {
  background: #f6f8fa;
}

/* ========== 查看对话框样式（全屏） ========== */
.view-dialog :deep(.el-dialog__header) { 
  padding: 16px 20px; 
  border-bottom: 1px solid #e4e7ed; 
  margin-right: 0; 
  text-align: center; /* 标题居中 */
}
.view-dialog :deep(.el-dialog__body) { 
  padding: 24px 48px; 
  height: calc(100vh - 80px); 
  overflow-y: auto; 
}
.view-dialog :deep(.el-dialog__close) { font-size: 20px; }
.view-dialog-header { display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 12px; }
.view-dialog-title { font-size: 20px; font-weight: 600; color: #1f2328; margin: 0; }
.view-dialog-actions { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.view-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.view-date { font-size: 13px; color: #8b949e; margin-left: 8px; }
.view-content { 
  max-width: 900px; 
  margin: 0 auto; 
}
.view-summary { background: #f6f8fa; border-radius: 6px; padding: 16px 20px; font-size: 14px; color: #57606a; line-height: 1.6; margin-bottom: 24px; text-align: center; /* 摘要居中 */ }
.view-summary p { margin: 0; }
.view-body { 
  line-height: 1.8; 
  font-size: 15px;
}

/* ========== 响应式：平板 ========== */
@media screen and (max-width: 1024px) {
  .notes-page { padding: 12px; }
  .category-panel { max-height: calc(100vh - 100px); }
  .notes-panel { height: auto; min-height: calc(100vh - 120px); }
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .notes-page { padding: 10px; }
  .page-header { margin-bottom: 12px; }
  .page-title { font-size: 16px; }
  .mobile-category-toggle { display: block; }
  .category-col { width: 100% !important; max-width: 100% !important; min-width: 100% !important; flex: 0 0 100% !important; margin-bottom: 12px; }
  .category-col .collapse-btn { display: none; }
  .category-col .category-panel { width: 100% !important; max-width: 100% !important; min-width: 100% !important; position: static; max-height: none; display: none; }
  .category-panel.mobile-show { display: block; }
  .notes-col { width: 100% !important; max-width: 100% !important; flex: 0 0 100% !important; }
  .notes-panel { padding: 12px; }
  .notes-header { flex-direction: column; align-items: flex-start; }
  .header-actions { width: 100%; }
  .header-actions .el-input { flex: 1; }
  .editor-header { flex-direction: column; align-items: flex-start; }

  /* 手机：编辑器和预览上下排列 */
  .md-main { flex-direction: column; height: auto; }
  .md-textarea { height: 280px; border-bottom: 1px solid #e4e7ed; border-right: none; }
  .md-preview { height: 280px; border-left: none; }
}

@media screen and (max-width: 480px) {
  .md-textarea { height: 220px; }
  .md-preview { height: 220px; }
}

/* ========== 笔记卡片列表样式 ========== */
.notes-card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.note-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  gap: 12px;
}

.note-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.12);
  transform: translateY(-1px);
}

.note-card-main {
  flex: 1;
  min-width: 0;
}

.note-card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.note-card-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.2s;
}

.note-card-title:hover {
  color: #409eff;
}

.note-card-date {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  white-space: nowrap;
}

.note-card-summary {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.note-card-empty {
  font-style: italic;
  color: #c0c4cc;
}

.note-card-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.note-card:hover .note-card-actions {
  opacity: 1;
}

/* 深色主题卡片适配 */
[data-theme="dark"] .note-card {
  background: #16213e;
  border-color: #2a2a4a;
}

[data-theme="dark"] .note-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

[data-theme="dark"] .note-card-title {
  color: #e8e8e8;
}

[data-theme="dark"] .note-card-title:hover {
  color: #409eff;
}

[data-theme="dark"] .note-card-summary {
  color: #8b949e;
}

[data-theme="dark"] .note-card-date {
  color: #6e7681;
}

/* H5端卡片调整 */
@media screen and (max-width: 768px) {
  .note-card {
    padding: 12px 14px;
    border-radius: 8px;
  }
  .note-card-title {
    font-size: 14px;
  }
  .note-card-summary {
    font-size: 12px;
  -webkit-line-clamp: 2;
  }
  .note-card-actions {
    opacity: 1; /* H5端始终显示操作按钮 */
  }
  .note-card-date {
    font-size: 11px;
  }
}
</style>

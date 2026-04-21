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
            <p>• 编辑笔记：单击编辑按钮或双击笔记行</p>
            <p>• 搜索功能：支持搜索标题、内容、标签</p>
            <p>• 富文本编辑：支持多种格式和图片</p>
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
        <!-- 折叠按钮（始终在分类列外部可见） -->
        <div class="collapse-btn" @click="categoryCollapsed = !categoryCollapsed" :title="categoryCollapsed ? '展开分类' : '收起分类'">
          <el-icon :size="14"><ArrowLeft v-if="!categoryCollapsed" /><ArrowRight v-else /></el-icon>
        </div>
        <!-- 折叠内容 -->
        <div class="category-panel" :class="{ 'mobile-show': showMobileCategory }" :style="{ width: categoryCollapsed ? '0px' : '260px', minWidth: categoryCollapsed ? '0px' : '220px', maxWidth: categoryCollapsed ? '0px' : '320px' }">
          <div class="category-header">
            <span class="category-header-title">分类管理</span>
            <div class="category-header-actions">
              <el-button size="small" @click="toggleExpandAll" :icon="allExpanded ? Fold : Expand" :title="allExpanded ? '全部收起' : '全部展开'" />
              <el-button type="primary" size="small" @click="addCategoryDialogVisible = true" :icon="Plus">新增</el-button>
            </div>
          </div>
          <div class="category-tree-wrapper">
            <el-tree ref="categoryTreeRef" :data="categoryTree" :props="{ label: 'name', children: 'children' }" node-key="id" highlight-current :expand-on-click-node="false" :default-expanded-keys="defaultExpandedKeys" @node-click="handleCategoryClick">
              <template #default="{ node, data }">
                <span class="custom-tree-node">
                  <span>
                    <el-icon v-if="data.children && data.children.length" @click.stop="toggleNodeExpand(node)" style="cursor: pointer; margin-right: 4px;">
                      <ArrowRight v-if="!node.expanded" />
                      <ArrowDown v-else />
                    </el-icon>
                    {{ node.label }}
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
              <el-table :data="notes" border style="width: 100%" v-loading="notesLoading" @row-dblclick="handleRowDblClick" size="small">
                <el-table-column prop="id" label="ID" width="60" />
                <el-table-column prop="title" label="标题" min-width="120" />
                <el-table-column prop="summary" label="摘要" min-width="150" show-overflow-tooltip />
                <el-table-column prop="createTime" label="创建时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.createTime) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="140" fixed="right">
                  <template #default="{ row }">
                    <el-button size="small" @click="editNote(row)" :icon="Edit">编辑</el-button>
                    <el-button size="small" type="danger" @click="deleteNote(row.id)" :icon="Delete">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 笔记编辑器 -->
          <div v-else class="note-editor">
            <div class="editor-header">
              <span class="editor-title">{{ editingNoteId ? '编辑笔记' : '新建笔记' }}</span>
              <div class="editor-actions">
                <el-button size="small" @click="cancelEdit">取消</el-button>
                <el-button type="primary" size="small" @click="saveNote" :loading="savingNote">保存</el-button>
              </div>
            </div>
            <div class="editor-form">
              <el-form :model="noteForm" label-width="70px" size="small">
                <el-form-item label="标题" required>
                  <el-input v-model="noteForm.title" placeholder="请输入笔记标题" />
                </el-form-item>
                <el-form-item label="分类">
                  <el-select v-model="noteForm.categoryId" placeholder="选择分类" style="width: 100%;">
                    <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
                  </el-select>
                </el-form-item>
                <el-form-item label="标签">
                  <el-input v-model="noteForm.tags" placeholder="多个标签用逗号分隔" />
                </el-form-item>
                <el-form-item label="摘要">
                  <el-input v-model="noteForm.summary" type="textarea" rows="2" placeholder="请输入摘要" />
                </el-form-item>
                <el-form-item label="内容" required>
                  <QuillEditor v-model:content="noteForm.content" contentType="html" :options="editorOptions" class="quill-editor-mobile" />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </div>
    </el-row>

    <!-- 分类对话框 -->
    <el-dialog v-model="addCategoryDialogVisible" :title="editingCategory ? '编辑分类' : '新增分类'" width="400" append-to-body>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { Plus, Edit, Delete, Search, InfoFilled, Expand, Fold, ArrowDown, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import axios from 'axios'

const API_BASE = '/api/note'
const CATEGORY_API = '/api/note/category'

// 移动端分类面板显示状态
const showMobileCategory = ref(false)

// 桌面端分类左右收起
const categoryCollapsed = ref(false)

// 分类树
const categoryTree = ref([])
const categoryTreeRef = ref()
const selectedCategoryId = ref(null)
const allExpanded = ref(true)
const defaultExpandedKeys = ref([])

const selectedCategoryName = computed(() => {
  if (!selectedCategoryId.value) return '全部'
  const find = flatCategories.value.find(cat => cat.id === selectedCategoryId.value)
  return find ? find.name : '未知'
})

// 分类对话框
const addCategoryDialogVisible = ref(false)
const editingCategory = ref(null)
const savingCategory = ref(false)
const categoryForm = reactive({
  name: '',
  parentId: 0,
  sort: 0
})

// 笔记列表
const notes = ref([])
const notesLoading = ref(false)
const searchKeyword = ref('')

// 笔记编辑器
const showEditor = ref(false)
const editingNoteId = ref(null)
const noteForm = reactive({
  title: '',
  categoryId: null,
  content: '',
  summary: '',
  tags: ''
})
const savingNote = ref(false)

// 编辑器配置
const editorOptions = {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'script': 'sub' }, { 'script': 'super' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      ['clean'],
      ['link', 'image', 'video']
    ]
  },
  placeholder: '请输入笔记内容...'
}

// 扁平化分类列表
const flatCategories = computed(() => {
  const flatten = (nodes, result = []) => {
    nodes.forEach(node => {
      result.push({ id: node.id, name: node.name })
      if (node.children && node.children.length > 0) {
        flatten(node.children, result)
      }
    })
    return result
  }
  return flatten(categoryTree.value)
})

// 获取所有节点 key
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

// 切换全部展开/收起
const toggleExpandAll = () => {
  const tree = categoryTreeRef.value
  if (!tree) return
  if (allExpanded.value) {
    const nodes = tree.store._getAllNodes()
    nodes.forEach(node => { node.expanded = false })
    allExpanded.value = false
  } else {
    const nodes = tree.store._getAllNodes()
    nodes.forEach(node => { node.expanded = true })
    allExpanded.value = true
  }
}

// 切换单个节点
const toggleNodeExpand = (node) => {
  node.expanded = !node.expanded
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 获取分类树
const fetchCategories = async () => {
  try {
    const response = await axios.get(`${CATEGORY_API}/list`)
    if (response.data && response.data.code === 200) {
      const categories = response.data.data
      const map = {}
      const tree = []
      categories.forEach(cat => { cat.children = []; map[cat.id] = cat })
      categories.forEach(cat => {
        if (cat.parentId === 0 || !map[cat.parentId]) { tree.push(cat) }
        else { map[cat.parentId].children.push(cat) }
      })
      categoryTree.value = tree
      defaultExpandedKeys.value = getAllNodeKeys()
      if (tree.length > 0 && !selectedCategoryId.value) {
        selectedCategoryId.value = tree[0].id
        fetchNotesByCategory(tree[0].id)
      }
    } else {
      ElMessage.error('获取分类失败')
    }
  } catch (error) {
    console.error('获取分类失败:', error)
    ElMessage.error('获取分类失败')
  }
}

// 保存分类
const saveCategory = async () => {
  if (!categoryForm.name.trim()) { ElMessage.warning('请输入分类名称'); return }
  savingCategory.value = true
  try {
    const api = editingCategory.value ? `${CATEGORY_API}/update` : `${CATEGORY_API}/add`
    const response = await axios[editingCategory.value ? 'put' : 'post'](api, categoryForm)
    if (response.data && response.data.code === 200) {
      ElMessage.success(editingCategory.value ? '更新成功' : '添加成功')
      addCategoryDialogVisible.value = false
      resetCategoryForm()
      await fetchCategories()
    } else {
      ElMessage.error(response.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('保存分类失败:', error)
    ElMessage.error('保存分类失败')
  } finally {
    savingCategory.value = false
  }
}

const resetCategoryForm = () => {
  categoryForm.name = ''; categoryForm.parentId = 0; categoryForm.sort = 0; editingCategory.value = null
}

const addChildCategory = (parentData) => {
  resetCategoryForm(); categoryForm.parentId = parentData.id; addCategoryDialogVisible.value = true
}

const editCategory = (data) => {
  editingCategory.value = data.id; categoryForm.name = data.name; categoryForm.parentId = data.parentId || 0; categoryForm.sort = data.sort || 0; addCategoryDialogVisible.value = true
}

const deleteCategory = async (data) => {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${data.name}" 吗？`, '提示', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    const response = await axios.delete(`${CATEGORY_API}/delete/${data.id}`)
    if (response.data && response.data.code === 200) { ElMessage.success('删除成功'); await fetchCategories() }
    else { ElMessage.error(response.data.msg || '删除失败') }
  } catch (error) {
    if (error !== 'cancel') { console.error('删除分类失败:', error); ElMessage.error('删除失败') }
  }
}

const handleCategoryClick = (data) => { selectedCategoryId.value = data.id; fetchNotesByCategory(data.id) }

const fetchNotesByCategory = async (categoryId) => {
  notesLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/category/${categoryId}`)
    if (response.data && response.data.code === 200) { notes.value = response.data.data }
    else { ElMessage.error('获取笔记列表失败') }
  } catch (error) {
    console.error('获取笔记列表失败:', error); ElMessage.error('获取笔记列表失败')
  } finally {
    notesLoading.value = false
  }
}

const searchNotes = async () => {
  if (!searchKeyword.value.trim()) { fetchNotesByCategory(selectedCategoryId.value); return }
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
  editingNoteId.value = null; noteForm.title = ''; noteForm.categoryId = selectedCategoryId.value; noteForm.content = ''; noteForm.summary = ''; noteForm.tags = ''; showEditor.value = true
}

const editNote = async (row) => {
  try {
    const response = await axios.get(`${API_BASE}/detail/${row.id}`)
    if (response.data && response.data.code === 200) {
      const note = response.data.data
      editingNoteId.value = note.id; noteForm.title = note.title; noteForm.categoryId = note.categoryId; noteForm.content = note.content || ''; noteForm.summary = note.summary || ''; noteForm.tags = note.tags || ''; showEditor.value = true
    } else { ElMessage.error('获取笔记详情失败') }
  } catch (error) { console.error('获取笔记详情失败:', error); ElMessage.error('获取笔记详情失败') }
}

const handleRowDblClick = (row) => { editNote(row) }

const saveNote = async () => {
  if (!noteForm.title.trim()) { ElMessage.warning('请输入笔记标题'); return }
  if (!noteForm.content.trim()) { ElMessage.warning('请输入笔记内容'); return }
  savingNote.value = true
  try {
    const api = editingNoteId.value ? `${API_BASE}/update` : `${API_BASE}/add`
    const response = await axios[editingNoteId.value ? 'put' : 'post'](api, { ...noteForm, id: editingNoteId.value })
    if (response.data && response.data.code === 200) {
      ElMessage.success(editingNoteId.value ? '更新成功' : '添加成功'); showEditor.value = false; await fetchNotesByCategory(selectedCategoryId.value)
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

onMounted(() => { fetchCategories() })
</script>

<style scoped>
.notes-page {
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

/* 移动端分类切换按钮 */
.mobile-category-toggle {
  display: none;
  margin-bottom: 12px;
}

.notes-row {
  display: flex;
}

/* 分类列 */
.category-col {
  flex-shrink: 0;
  display: flex;
  overflow: visible;
  position: relative;
}

.category-col.collapsed {
  flex-shrink: 0;
}

.category-col.collapsed .category-panel {
  display: none;
}

.collapse-btn {
  flex-shrink: 0;
  width: 16px;
  height: 48px;
  background: #e4e7ed;
  border-radius: 0 4px 4px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: background 0.2s;
  align-self: center;
  margin-left: -1px;
}

.collapse-btn:hover {
  background: #c0c4cc;
}

.category-panel {
  flex-shrink: 0;
  transition: width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease;
  overflow: hidden;
  width: 260px;
  min-width: 220px;
  max-width: 320px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  background: #fff;
  position: sticky;
  top: 0;
  max-height: calc(100vh - 120px);
}

.category-tree-wrapper {
  overflow-y: auto;
  max-height: calc(100vh - 180px);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}

.category-header-title {
  font-weight: bold;
  font-size: 14px;
}

.category-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  padding-right: 4px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.custom-tree-node:hover .node-actions {
  opacity: 1;
}

/* 笔记列 */
.notes-col {
  flex: 1;
  min-width: 0;
}

.notes-panel {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  min-height: 400px;
}

.notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.notes-header-title {
  font-weight: bold;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.table-wrapper {
  overflow-x: auto;
}

/* 编辑器 */
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}

.editor-title {
  font-weight: bold;
  font-size: 14px;
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-form {
  margin-top: 12px;
}

/* Quill 内容区排版优化 */
.ql-editor.ql-blank::before {
  color: #c0c4cc;
  font-style: normal;
}

.ql-editor {
  min-height: 320px;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 15px;
  line-height: 1.8;
  color: #2c2c2c;
  padding: 16px 20px;
}

.ql-editor p {
  margin: 0 0 12px;
}

.ql-editor h1,
.ql-editor h2,
.ql-editor h3,
.ql-editor h4,
.ql-editor h5,
.ql-editor h6 {
  font-weight: 600;
  line-height: 1.4;
  margin: 20px 0 10px;
}

.ql-editor h1 { font-size: 22px; }
.ql-editor h2 { font-size: 19px; }
.ql-editor h3 { font-size: 17px; }

.ql-editor blockquote {
  border-left: 3px solid #d0d7de;
  padding: 4px 16px;
  margin: 12px 0;
  color: #57606a;
  background: #f6f8fa;
  border-radius: 0 4px 4px 0;
}

.ql-editor pre.ql-syntax {
  background: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 14px 16px;
  font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #24292f;
  overflow-x: auto;
  margin: 12px 0;
}

.ql-editor code {
  background: #f0f0f0;
  border-radius: 3px;
  padding: 1px 5px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #e74c3c;
}

.ql-editor ul,
.ql-editor ol {
  padding-left: 24px;
  margin: 8px 0 12px;
}

.ql-editor li {
  margin: 4px 0;
  line-height: 1.8;
}

.ql-editor hr {
  border: none;
  border-top: 1px solid #e1e4e8;
  margin: 16px 0;
}

.ql-editor a {
  color: #0969da;
  text-decoration: none;
}

.ql-editor a:hover {
  text-decoration: underline;
}

/* Quill 工具栏美化 */
.ql-toolbar.ql-snow {
  border: 1px solid #e4e7ed;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
  padding: 8px 10px;
  background: #fafafa;
}

.ql-container.ql-snow {
  border: 1px solid #e4e7ed;
  border-radius: 0 0 6px 6px;
  font-family: inherit;
}

.ql-snow .ql-picker {
  color: #606266;
}

.ql-snow .ql-picker-label {
  padding: 2px 6px;
}

.ql-snow .ql-stroke {
  stroke: #606266;
}

.ql-snow .ql-fill {
  fill: #606266;
}

.ql-snow .ql-picker.ql-expanded .ql-picker-label {
  color: #409eff;
  border-color: #409eff;
}

/* Quill 编辑器高度 */
.quill-editor-mobile {
  height: 400px;
  margin-bottom: 20px;
}

/* ========== 响应式：平板 ========== */
@media screen and (max-width: 1024px) {
  .notes-page {
    padding: 12px;
  }

  .category-panel {
    max-height: calc(100vh - 100px);
  }

  .quill-editor-mobile {
    height: 350px;
  }
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .notes-page {
    padding: 10px;
  }

  .page-header {
    margin-bottom: 12px;
  }

  .page-title {
    font-size: 16px;
  }

  .mobile-category-toggle {
    display: block;
  }

  .category-col {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 12px;
  }

  .category-col .collapse-btn {
    display: none;
  }

  .category-col .category-panel {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    position: static;
    max-height: none;
    display: none;
  }

  .category-panel.mobile-show {
    display: block;
  }

  .notes-col {
    width: 100% !important;
    max-width: 100% !important;
    flex: 0 0 100% !important;
  }

  .notes-panel {
    padding: 12px;
  }

  .notes-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-input {
    flex: 1;
  }

  .editor-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .quill-editor-mobile {
    height: 300px;
  }
}

/* ========== 响应式：小手机 ========== */
@media screen and (max-width: 480px) {
  .quill-editor-mobile {
    height: 250px;
  }
}
</style>

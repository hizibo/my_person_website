<template>
  <div class="notes-page">
    <div class="page-header">
      <h1>我的笔记</h1>
      <el-tooltip placement="right" effect="light">
        <template #content>
          <div class="info-tooltip-content">
            <p><strong>功能说明：</strong></p>
            <p>• 分类管理：左侧树形结构管理笔记分类</p>
            <p>• 新建笔记：选择分类后点击新建按钮</p>
            <p>• 编辑笔记：单击编辑按钮或双击笔记行</p>
            <p>• 搜索功能：支持搜索标题、内容、标签</p>
            <p>• 富文本编辑：支持多种格式和图片</p>
          </div>
        </template>
        <el-icon class="info-icon" :size="18"><InfoFilled /></el-icon>
      </el-tooltip>
    </div>

    <el-row :gutter="20">
      <!-- 左侧分类树 -->
      <el-col :span="6">
        <div class="category-panel">
          <div class="category-header">
            <span>分类管理</span>
            <el-button type="primary" size="small" @click="addCategoryDialogVisible = true" :icon="Plus">
              新增
            </el-button>
          </div>
          <el-tree
            ref="categoryTreeRef"
            :data="categoryTree"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            default-expand-all
            highlight-current
            :expand-on-click-node="false"
            @node-click="handleCategoryClick"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>{{ node.label }}</span>
                <span class="node-actions">
                  <el-button
                    link
                    type="primary"
                    size="small"
                    @click.stop="addChildCategory(data)"
                    :icon="Plus"
                  ></el-button>
                  <el-button
                    link
                    type="primary"
                    size="small"
                    @click.stop="editCategory(data)"
                    :icon="Edit"
                  ></el-button>
                  <el-button
                    link
                    type="danger"
                    size="small"
                    @click.stop="deleteCategory(data)"
                    :icon="Delete"
                  ></el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
      </el-col>

      <!-- 右侧笔记列表/编辑器 -->
      <el-col :span="18">
        <div class="notes-panel">
          <!-- 笔记列表 -->
          <div v-if="!showEditor" class="notes-list">
            <div class="notes-header">
              <span>笔记列表 ({{ selectedCategoryName }})</span>
              <div class="header-actions">
                <el-input
                  v-model="searchKeyword"
                  placeholder="搜索标题、内容或标签"
                  style="width: 250px; margin-right: 10px;"
                  clearable
                  @keyup.enter="searchNotes"
                  @clear="searchNotes"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button type="primary" @click="searchNotes" :icon="Search" style="margin-right: 10px;">搜索</el-button>
                <el-button type="primary" @click="createNewNote" :icon="Plus">新建笔记</el-button>
              </div>
            </div>
            <el-table :data="notes" border style="width: 100%" v-loading="notesLoading" @row-dblclick="handleRowDblClick">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="标题" width="200" />
              <el-table-column prop="summary" label="摘要" />
              <el-table-column prop="createTime" label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.createTime) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="180">
                <template #default="{ row }">
                  <el-button size="small" @click="editNote(row)" :icon="Edit">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteNote(row.id)" :icon="Delete">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 笔记编辑器 -->
          <div v-else class="note-editor">
            <div class="editor-header">
              <span>{{ editingNoteId ? '编辑笔记' : '新建笔记' }}</span>
              <div>
                <el-button @click="cancelEdit">取消</el-button>
                <el-button type="primary" @click="saveNote" :loading="savingNote">保存</el-button>
              </div>
            </div>
            <div class="editor-form">
              <el-form :model="noteForm" label-width="80px">
                <el-form-item label="标题" required>
                  <el-input v-model="noteForm.title" placeholder="请输入笔记标题" />
                </el-form-item>
                <el-form-item label="分类">
                  <el-select v-model="noteForm.categoryId" placeholder="选择分类" style="width: 100%;">
                    <el-option
                      v-for="cat in flatCategories"
                      :key="cat.id"
                      :label="cat.name"
                      :value="cat.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="标签">
                  <el-input v-model="noteForm.tags" placeholder="多个标签用逗号分隔" />
                </el-form-item>
                <el-form-item label="摘要">
                  <el-input v-model="noteForm.summary" type="textarea" rows="2" placeholder="请输入摘要" />
                </el-form-item>
                <el-form-item label="内容" required>
                  <QuillEditor
                    v-model:content="noteForm.content"
                    contentType="html"
                    :options="editorOptions"
                    style="height: 600px; margin-bottom: 20px;"
                  />
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 分类对话框 -->
    <el-dialog v-model="addCategoryDialogVisible" :title="editingCategory ? '编辑分类' : '新增分类'" width="400">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="categoryForm.parentId" placeholder="根分类" clearable style="width: 100%;">
            <el-option label="根分类" :value="0" />
            <el-option
              v-for="cat in flatCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
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
import { Plus, Edit, Delete, Search, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import axios from 'axios'

const API_BASE = '/api/note'
const CATEGORY_API = '/api/note/category'

// 分类树
const categoryTree = ref([])
const categoryTreeRef = ref()
const selectedCategoryId = ref(null)
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
      [{ 'direction': 'rtl' }],
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

// 扁平化分类列表（用于下拉选择）
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
      // 构建树形结构
      const map = {}
      const tree = []
      categories.forEach(cat => {
        cat.children = []
        map[cat.id] = cat
      })
      categories.forEach(cat => {
        if (cat.parentId === 0 || !map[cat.parentId]) {
          tree.push(cat)
        } else {
          map[cat.parentId].children.push(cat)
        }
      })
      categoryTree.value = tree
      // 默认选择第一个分类
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
  if (!categoryForm.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
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

// 重置分类表单
const resetCategoryForm = () => {
  categoryForm.name = ''
  categoryForm.parentId = 0
  categoryForm.sort = 0
  editingCategory.value = null
}

// 添加子分类
const addChildCategory = (parentData) => {
  resetCategoryForm()
  categoryForm.parentId = parentData.id
  addCategoryDialogVisible.value = true
}

// 编辑分类
const editCategory = (data) => {
  editingCategory.value = data.id
  categoryForm.name = data.name
  categoryForm.parentId = data.parentId || 0
  categoryForm.sort = data.sort || 0
  addCategoryDialogVisible.value = true
}

// 删除分类
const deleteCategory = async (data) => {
  try {
    await ElMessageBox.confirm(`确定删除分类 "${data.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const response = await axios.delete(`${CATEGORY_API}/delete/${data.id}`)
    if (response.data && response.data.code === 200) {
      ElMessage.success('删除成功')
      await fetchCategories()
    } else {
      ElMessage.error(response.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除分类失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 分类点击事件
const handleCategoryClick = (data) => {
  selectedCategoryId.value = data.id
  fetchNotesByCategory(data.id)
}

// 获取分类下的笔记
const fetchNotesByCategory = async (categoryId) => {
  notesLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/category/${categoryId}`)
    if (response.data && response.data.code === 200) {
      notes.value = response.data.data
    } else {
      ElMessage.error('获取笔记列表失败')
    }
  } catch (error) {
    console.error('获取笔记列表失败:', error)
    ElMessage.error('获取笔记列表失败')
  } finally {
    notesLoading.value = false
  }
}

// 搜索笔记
const searchNotes = async () => {
  if (!searchKeyword.value.trim()) {
    fetchNotesByCategory(selectedCategoryId.value)
    return
  }
  notesLoading.value = true
  try {
    const response = await axios.get(`${API_BASE}/search?keyword=${encodeURIComponent(searchKeyword.value)}`)
    if (response.data && response.data.code === 200) {
      notes.value = response.data.data
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('搜索笔记失败:', error)
    ElMessage.error('搜索笔记失败')
  } finally {
    notesLoading.value = false
  }
}

// 创建新笔记
const createNewNote = () => {
  editingNoteId.value = null
  noteForm.title = ''
  noteForm.categoryId = selectedCategoryId.value
  noteForm.content = ''
  noteForm.summary = ''
  noteForm.tags = ''
  showEditor.value = true
}

// 编辑笔记
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
    } else {
      ElMessage.error('获取笔记详情失败')
    }
  } catch (error) {
    console.error('获取笔记详情失败:', error)
    ElMessage.error('获取笔记详情失败')
  }
}

// 双击查看笔记
const handleRowDblClick = (row) => {
  editNote(row)
}

// 保存笔记
const saveNote = async () => {
  if (!noteForm.title.trim()) {
    ElMessage.warning('请输入笔记标题')
    return
  }
  if (!noteForm.content.trim()) {
    ElMessage.warning('请输入笔记内容')
    return
  }
  savingNote.value = true
  try {
    const api = editingNoteId.value ? `${API_BASE}/update` : `${API_BASE}/add`
    const response = await axios[editingNoteId.value ? 'put' : 'post'](api, {
      ...noteForm,
      id: editingNoteId.value
    })
    if (response.data && response.data.code === 200) {
      ElMessage.success(editingNoteId.value ? '更新成功' : '添加成功')
      showEditor.value = false
      await fetchNotesByCategory(selectedCategoryId.value)
    } else {
      ElMessage.error(response.data.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存笔记失败:', error)
    ElMessage.error('保存笔记失败')
  } finally {
    savingNote.value = false
  }
}

// 取消编辑
const cancelEdit = () => {
  showEditor.value = false
}

// 删除笔记
const deleteNote = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该笔记吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const response = await axios.delete(`${API_BASE}/delete/${id}`)
    if (response.data && response.data.code === 200) {
      ElMessage.success('删除成功')
      await fetchNotesByCategory(selectedCategoryId.value)
    } else {
      ElMessage.error(response.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除笔记失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 初始化
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.notes-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
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

.category-panel {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #fff;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.custom-tree-node:hover .node-actions {
  opacity: 1;
}

.notes-panel {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  background: #fff;
  min-height: 600px;
}

.notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 10px;
}

.editor-form {
  margin-top: 20px;
}
</style>
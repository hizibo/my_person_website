<template>
  <div class="batch-data-gen">
    <!-- 顶部 -->
    <div class="tool-header">
      <el-button @click="$router.push('/tools')" :icon="Back" size="small">返回</el-button>
      <h2 class="tool-title">🗄️ 批量数据生成</h2>
    </div>

    <!-- 数据库选择 -->
    <div class="db-section">
      <span class="section-label">数据库类型</span>
      <el-radio-group v-model="database" size="small">
        <el-radio-button value="mysql">MySQL</el-radio-button>
        <el-radio-button value="oracle">Oracle</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 表配置 -->
    <div class="tables-section">
      <div class="section-header">
        <span class="section-label">📋 表配置</span>
        <el-button type="primary" size="small" :icon="Plus" @click="addTable">添加表</el-button>
      </div>

      <div v-for="(table, ti) in tables" :key="ti" class="table-card">
        <div class="table-header">
          <el-input v-model="table.name" placeholder="表名" size="small" class="table-name-input" />
          <span class="row-label">行数</span>
          <el-input-number v-model="table.row_count" :min="1" :max="100000" size="small" class="row-count-input" />
          <el-button type="danger" :icon="Delete" size="small" circle @click="removeTable(ti)" />
        </div>

        <!-- 字段列表 -->
        <div class="fields-section">
          <div class="field-row field-row-header">
            <span class="col-name">字段名</span>
            <span class="col-type">数据类型</span>
            <span class="col-mode">填充方式</span>
            <span class="col-config">配置</span>
            <span class="col-action"></span>
          </div>
          <div v-for="(field, fi) in table.fields" :key="fi" class="field-row">
            <el-input v-model="field.name" placeholder="字段名" size="small" class="col-name" />
            <el-select v-model="field.data_type" size="small" class="col-type">
              <el-option label="字符串" value="string" />
              <el-option label="数字" value="number" />
              <el-option label="日期" value="date" />
              <el-option label="日期时间" value="datetime" />
            </el-select>
            <el-select v-model="field.fill_mode" size="small" class="col-mode" @change="onFillModeChange(field)">
              <el-option label="固定值" value="fixed" />
              <el-option label="自增" value="auto_increment" />
              <el-option label="随机" value="random" />
              <el-option label="Faker" value="faker" />
              <el-option label="引用变量" value="variable" />
            </el-select>

            <!-- 配置区域 -->
            <div class="col-config">
              <!-- 固定值 -->
              <el-input v-if="field.fill_mode === 'fixed'" v-model="field.fixed_value" placeholder="固定值" size="small" />

              <!-- 自增 -->
              <div v-if="field.fill_mode === 'auto_increment'" class="inline-config">
                <span>起</span>
                <el-input-number v-model="field.start_value" :min="0" size="small" controls-position="right" />
                <span>步</span>
                <el-input-number v-model="field.step" :min="1" size="small" controls-position="right" />
              </div>

              <!-- 随机 -->
              <el-button v-if="field.fill_mode === 'random'" size="small" @click="openRandomConfig(table, fi)">
                {{ formatRandomRule(field.random_rule) }}
              </el-button>

              <!-- Faker -->
              <el-select v-if="field.fill_mode === 'faker'" v-model="field.faker_type" size="small" placeholder="选择类型">
                <el-option v-for="(label, key) in fakerTypes" :key="key" :label="label" :value="key" />
              </el-select>

              <!-- 引用变量 -->
              <el-select v-if="field.fill_mode === 'variable'" v-model="field.variable_name" size="small" placeholder="选择变量">
                <el-option v-for="v in variables" :key="v.name" :label="v.name" :value="v.name" />
                <el-option v-if="variables.length === 0" disabled label="请先添加变量" value="" />
              </el-select>
            </div>

            <el-button type="danger" :icon="Delete" size="small" circle @click="removeField(table, fi)" class="col-action" />
          </div>
          <el-button size="small" :icon="Plus" @click="addField(table)" class="add-field-btn">添加字段</el-button>
        </div>
      </div>
    </div>

    <!-- 变量定义 -->
    <div class="variables-section">
      <div class="section-header">
        <span class="section-label">🔗 变量定义 <el-tag size="small" type="info">可选，用于多表关联</el-tag></span>
        <el-button type="warning" size="small" :icon="Plus" @click="addVariable">添加变量</el-button>
      </div>

      <div v-for="(v, vi) in variables" :key="vi" class="variable-card">
        <div class="var-header">
          <el-input v-model="v.name" placeholder="变量名" size="small" class="var-name-input" />
          <span class="var-count-label">数量</span>
          <el-input-number v-model="v.count" :min="1" :max="100000" size="small" />
          <el-button type="danger" :icon="Delete" size="small" circle @click="removeVariable(vi)" />
        </div>
        <div class="var-rule">
          <el-button size="small" @click="openVarRandomConfig(vi)">
            规则: {{ formatRandomRule(v.rule) }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" size="default" :icon="Cpu" @click="generateSQL" :loading="generating">
        🚀 生成 SQL 脚本
      </el-button>
      <el-button v-if="generatedSQL" type="success" size="default" :icon="Download" @click="downloadSQL">
        📥 下载脚本
      </el-button>
      <el-button v-if="generatedSQL" size="default" @click="copySQL">📋 复制</el-button>
    </div>

    <!-- SQL 预览 -->
    <div v-if="generatedSQL" class="result-section">
      <div class="result-header">
        <h3>📄 SQL 脚本预览</h3>
        <el-tag type="success" size="small">{{ generateMessage }}</el-tag>
      </div>
      <el-input v-model="generatedSQL" type="textarea" :rows="16" readonly class="sql-preview" />
    </div>

    <!-- 随机规则配置弹窗 -->
    <el-dialog v-model="randomConfigVisible" title="随机规则配置" width="480px" :close-on-click-modal="false">
      <el-form label-width="80px" size="default">
        <el-form-item label="随机类型">
          <el-select v-model="editingRule.type">
            <el-option label="整数" value="int" />
            <el-option label="小数" value="float" />
            <el-option label="字符串" value="string" />
            <el-option label="日期" value="date" />
            <el-option label="日期时间" value="datetime" />
            <el-option label="枚举值" value="enum" />
          </el-select>
        </el-form-item>

        <!-- 整数/小数 -->
        <template v-if="editingRule.type === 'int' || editingRule.type === 'float'">
          <el-form-item label="最小值">
            <el-input-number v-model="editingRule.min_val" :precision="editingRule.type === 'float' ? 2 : 0" />
          </el-form-item>
          <el-form-item label="最大值">
            <el-input-number v-model="editingRule.max_val" :precision="editingRule.type === 'float' ? 2 : 0" />
          </el-form-item>
          <el-form-item v-if="editingRule.type === 'float'" label="小数位数">
            <el-input-number v-model="editingRule.decimal_places" :min="0" :max="10" />
          </el-form-item>
        </template>

        <!-- 字符串 -->
        <template v-if="editingRule.type === 'string'">
          <el-form-item label="长度">
            <el-input-number v-model="editingRule.length" :min="1" :max="200" />
          </el-form-item>
          <el-form-item label="字符集">
            <el-select v-model="editingRule.charset">
              <el-option label="字母+数字" value="mixed" />
              <el-option label="纯数字" value="digits" />
              <el-option label="纯字母" value="letters" />
              <el-option label="中文" value="chinese" />
            </el-select>
          </el-form-item>
          <el-form-item label="前缀">
            <el-input v-model="editingRule.prefix" placeholder="可选" />
          </el-form-item>
          <el-form-item label="后缀">
            <el-input v-model="editingRule.suffix" placeholder="可选" />
          </el-form-item>
        </template>

        <!-- 日期/日期时间 -->
        <template v-if="editingRule.type === 'date' || editingRule.type === 'datetime'">
          <el-form-item label="起始日期">
            <el-date-picker v-model="editingRule.start_date" type="date" value-format="YYYY-MM-DD" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="editingRule.end_date" type="date" value-format="YYYY-MM-DD" />
          </el-form-item>
          <el-form-item v-if="editingRule.type === 'date'" label="日期格式">
            <el-select v-model="editingRule.date_format">
              <el-option label="YYYY-MM-DD" value="%Y-%m-%d" />
              <el-option label="YYYY/MM/DD" value="%Y/%m/%d" />
              <el-option label="DD-MM-YYYY" value="%d-%m-%Y" />
            </el-select>
          </el-form-item>
        </template>

        <!-- 枚举 -->
        <template v-if="editingRule.type === 'enum'">
          <el-form-item label="枚举值">
            <div class="enum-editor">
              <div v-for="(ev, ei) in editingRule.enum_values" :key="ei" class="enum-item">
                <el-input v-model="editingRule.enum_values[ei]" size="small" />
                <el-button type="danger" :icon="Delete" size="small" circle @click="editingRule.enum_values.splice(ei, 1)" />
              </div>
              <el-button size="small" :icon="Plus" @click="editingRule.enum_values.push('')">添加</el-button>
            </div>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="randomConfigVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRandomConfig">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { Back, Plus, Delete, Download, Cpu } from '@element-plus/icons-vue'

const database = ref('mysql')
const tables = reactive([
  {
    name: '',
    row_count: 100,
    fields: [
      { name: 'id', data_type: 'number', fill_mode: 'auto_increment', fixed_value: '', start_value: 1, step: 1, random_rule: null, faker_type: null, variable_name: null }
    ]
  }
])
const variables = reactive([])
const fakerTypes = ref({})
const generating = ref(false)
const generatedSQL = ref('')
const generateMessage = ref('')

// Random config dialog
const randomConfigVisible = ref(false)
const editingRule = reactive({
  type: 'string', min_val: 0, max_val: 100, decimal_places: 2,
  length: 10, charset: 'mixed', prefix: '', suffix: '',
  start_date: '2020-01-01', end_date: '2026-12-31', date_format: '%Y-%m-%d',
  enum_values: ['选项1', '选项2', '选项3']
})
let editingTarget = null // { type: 'field'|'variable', tableIndex, fieldIndex, varIndex }

onMounted(async () => {
  try {
    const res = await axios.get('/api/tool/datagen/faker-types')
    fakerTypes.value = res.data
  } catch (e) {
    console.warn('获取 Faker 类型失败，使用默认值')
    fakerTypes.value = {
      name: '姓名', phone: '手机号', email: '邮箱', city: '城市',
      province: '省份', address: '地址', id_card: '身份证号',
      company: '公司名', job: '职位', username: '用户名'
    }
  }
})

function addTable() {
  tables.push({
    name: '',
    row_count: 100,
    fields: [
      { name: 'id', data_type: 'number', fill_mode: 'auto_increment', fixed_value: '', start_value: 1, step: 1, random_rule: null, faker_type: null, variable_name: null }
    ]
  })
}

function removeTable(index) {
  tables.splice(index, 1)
}

function addField(table) {
  table.fields.push({
    name: '', data_type: 'string', fill_mode: 'random',
    fixed_value: '', start_value: 1, step: 1,
    random_rule: { type: 'string', min_val: 0, max_val: 100, decimal_places: 2, length: 10, charset: 'mixed', prefix: '', suffix: '', start_date: '2020-01-01', end_date: '2026-12-31', date_format: '%Y-%m-%d', enum_values: ['选项1', '选项2', '选项3'] },
    faker_type: null, variable_name: null
  })
}

function removeField(table, index) {
  table.fields.splice(index, 1)
}

function addVariable() {
  variables.push({
    name: '',
    count: 100,
    rule: { type: 'int', min_val: 1, max_val: 1000, decimal_places: 2, length: 10, charset: 'mixed', prefix: '', suffix: '', start_date: '2020-01-01', end_date: '2026-12-31', date_format: '%Y-%m-%d', enum_values: ['选项1', '选项2', '选项3'] }
  })
}

function removeVariable(index) {
  variables.splice(index, 1)
}

function onFillModeChange(field) {
  if (field.fill_mode === 'random' && !field.random_rule) {
    field.random_rule = {
      type: field.data_type === 'number' ? 'int' : (field.data_type === 'date' ? 'date' : 'string'),
      min_val: 0, max_val: 100, decimal_places: 2, length: 10, charset: 'mixed',
      prefix: '', suffix: '', start_date: '2020-01-01', end_date: '2026-12-31',
      date_format: '%Y-%m-%d', enum_values: ['选项1', '选项2', '选项3']
    }
  }
}

function openRandomConfig(table, fieldIndex) {
  const field = table.fields[fieldIndex]
  const src = field.random_rule || {
    type: 'string', min_val: 0, max_val: 100, decimal_places: 2, length: 10,
    charset: 'mixed', prefix: '', suffix: '', start_date: '2020-01-01',
    end_date: '2026-12-31', date_format: '%Y-%m-%d', enum_values: ['选项1', '选项2', '选项3']
  }
  Object.assign(editingRule, JSON.parse(JSON.stringify(src)))
  editingTarget = { type: 'field', tableIndex: tables.indexOf(table), fieldIndex }
  randomConfigVisible.value = true
}

function openVarRandomConfig(varIndex) {
  const v = variables[varIndex]
  Object.assign(editingRule, JSON.parse(JSON.stringify(v.rule)))
  editingTarget = { type: 'variable', varIndex }
  randomConfigVisible.value = true
}

function saveRandomConfig() {
  const ruleCopy = JSON.parse(JSON.stringify(editingRule))
  if (editingTarget.type === 'field') {
    tables[editingTarget.tableIndex].fields[editingTarget.fieldIndex].random_rule = ruleCopy
  } else if (editingTarget.type === 'variable') {
    variables[editingTarget.varIndex].rule = ruleCopy
  }
  randomConfigVisible.value = false
}

function formatRandomRule(rule) {
  if (!rule) return '未配置'
  const typeLabels = { int: '整数', float: '小数', string: '字符串', date: '日期', datetime: '日期时间', enum: '枚举' }
  const base = typeLabels[rule.type] || rule.type
  if (rule.type === 'int' || rule.type === 'float') return `${base} ${rule.min_val ?? 0}~${rule.max_val ?? 100}`
  if (rule.type === 'string') return `${base} 长${rule.length || 10}`
  if (rule.type === 'date' || rule.type === 'datetime') return `${base} ${rule.start_date || '?'}~${rule.end_date || '?'}`
  if (rule.type === 'enum') return `枚举 (${(rule.enum_values || []).length}项)`
  return base
}

async function generateSQL() {
  // Validate
  for (let ti = 0; ti < tables.length; ti++) {
    const t = tables[ti]
    if (!t.name.trim()) { ElMessage.error(`第${ti + 1}张表名不能为空`); return }
    if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(t.name)) { ElMessage.error(`表名 "${t.name}" 不合法，仅支持字母/数字/下划线`); return }
    if (t.fields.length === 0) { ElMessage.error(`表 "${t.name}" 至少需要一个字段`); return }
    for (const f of t.fields) {
      if (!f.name.trim()) { ElMessage.error(`表 "${t.name}" 有字段名为空`); return }
      if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(f.name)) { ElMessage.error(`字段名 "${f.name}" 不合法`); return }
    }
  }

  generating.value = true
  try {
    const payload = {
      database: database.value,
      tables: tables.map(t => ({
        name: t.name,
        row_count: t.row_count,
        fields: t.fields.map(f => {
          const obj = { name: f.name, data_type: f.data_type, fill_mode: f.fill_mode }
          if (f.fill_mode === 'fixed') obj.fixed_value = f.fixed_value
          if (f.fill_mode === 'auto_increment') { obj.start_value = f.start_value; obj.step = f.step }
          if (f.fill_mode === 'random') obj.random_rule = f.random_rule
          if (f.fill_mode === 'faker') obj.faker_type = f.faker_type
          if (f.fill_mode === 'variable') obj.variable_name = f.variable_name
          return obj
        })
      })),
      variables: variables.map(v => ({ name: v.name, rule: v.rule, count: v.count }))
    }

    const res = await axios.post('/api/tool/datagen/generate', payload)
    if (res.data.sql) {
      generatedSQL.value = res.data.sql
      generateMessage.value = res.data.message
      ElMessage.success(res.data.message)
    }
  } catch (e) {
    const msg = e.response?.data?.detail || e.response?.data?.message || '生成失败'
    ElMessage.error(msg)
  } finally {
    generating.value = false
  }
}

function downloadSQL() {
  if (!generatedSQL.value) return
  const blob = new Blob([generatedSQL.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `batch_data_${database.value}_${new Date().toISOString().slice(0, 10)}.sql`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

function copySQL() {
  if (!generatedSQL.value) return
  navigator.clipboard.writeText(generatedSQL.value).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.batch-data-gen {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.tool-title {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.db-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f0f5ff;
  border-radius: 8px;
}

.section-label {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.tables-section,
.variables-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.table-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.table-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.table-name-input {
  width: 180px;
}

.row-label {
  font-size: 13px;
  color: #666;
  margin-left: 8px;
}

.row-count-input {
  width: 130px;
}

.fields-section {
  margin-top: 8px;
}

.field-row-header {
  font-size: 12px;
  color: #909399;
  font-weight: 600;
  padding-bottom: 4px;
  border-bottom: 1px solid #ebeef5;
}

.field-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  flex-wrap: wrap;
}

.col-name { width: 120px; flex-shrink: 0; }
.col-type { width: 110px; flex-shrink: 0; }
.col-mode { width: 110px; flex-shrink: 0; }
.col-config { flex: 1; min-width: 150px; }
.col-action { flex-shrink: 0; }

.inline-config {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.inline-config .el-input-number {
  width: 90px;
}

.add-field-btn {
  margin-top: 8px;
}

.variable-card {
  background: #fffbf0;
  border: 1px solid #f0d9a0;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 10px;
}

.var-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.var-name-input {
  width: 150px;
}

.var-count-label {
  font-size: 13px;
  color: #666;
  margin-left: 4px;
}

.var-rule {
  margin-top: 8px;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.result-section {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.sql-preview :deep(textarea) {
  font-family: 'Courier New', Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
}

.enum-editor {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.enum-item {
  display: flex;
  gap: 6px;
  align-items: center;
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .batch-data-gen {
    padding: 10px;
  }

  .tool-title {
    font-size: 17px;
  }

  .table-card {
    padding: 10px;
  }

  .field-row {
    gap: 4px;
  }

  .col-name { width: 80px; }
  .col-type { width: 90px; }
  .col-mode { width: 90px; }

  .action-bar {
    flex-direction: column;
  }

  .action-bar .el-button {
    width: 100%;
  }
}
</style>

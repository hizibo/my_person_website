<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue'
export default {
  setup() {
    onMounted(() => {
      const saved = localStorage.getItem('theme')
      if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark')
      }
    })
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}


/* ========== 深色主题全局样式 ========== */
[data-theme="dark"] body {
  background-color: #1a1a2e !important;
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-table,
[data-theme="dark"] .el-table__header-wrapper th,
[data-theme="dark"] .el-table__body-wrapper tr,
[data-theme="dark"] .el-table__body-wrapper td {
  background-color: #16213e !important;
  color: #e8e8e8 !important;
  border-color: #2a2a4a !important;
}

[data-theme="dark"] .el-table th.el-table__cell {
  background-color: #0f3460 !important;
  color: #c8d6e5 !important;
}

[data-theme="dark"] .el-table__row:hover > td {
  background-color: #1e3a5f !important;
}

[data-theme="dark"] .el-input__wrapper,
[data-theme="dark"] .el-textarea__inner {
  background-color: #16213e !important;
  box-shadow: inset 0 0 0 1px #2a2a4a !important;
}

[data-theme="dark"] .el-input__inner,
[data-theme="dark"] .el-textarea__inner {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-input__wrapper:hover,
[data-theme="dark"] .el-input__wrapper.is-focus {
  box-shadow: inset 0 0 0 1px #409eff !important;
}

[data-theme="dark"] .el-button--default {
  background-color: #16213e !important;
  border-color: #2a2a4a !important;
  color: #c8d6e5 !important;
}

[data-theme="dark"] .el-button--default:hover {
  background-color: #0f3460 !important;
  border-color: #409eff !important;
  color: white !important;
}

[data-theme="dark"] .el-card {
  background-color: #16213e !important;
  border-color: #2a2a4a !important;
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-card__body {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-dialog {
  background-color: #16213e !important;
}

[data-theme="dark"] .el-dialog__title {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-form-item__label {
  color: #c8d6e5 !important;
}

[data-theme="dark"] .el-tree {
  background-color: transparent !important;
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-tree-node__content:hover {
  background-color: #1e3a5f !important;
}

[data-theme="dark"] .el-message-box {
  background-color: #16213e !important;
  border-color: #2a2a4a !important;
  color: #e8e8e8 !important;
}

[data-theme="dark"] .el-tag {
  border-color: #2a2a4a !important;
}

[data-theme="dark"] .el-pagination {
  color: #c8d6e5 !important;
}

[data-theme="dark"] .el-pagination button,
[data-theme="dark"] .el-pager li {
  background-color: #16213e !important;
  color: #c8d6e5 !important;
}

[data-theme="dark"] .markdown-body {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .markdown-body pre,
[data-theme="dark"] .markdown-body code {
  background-color: #0d1b2a !important;
  color: #c8d6e5 !important;
  border-color: #2a2a4a !important;
}

[data-theme="dark"] .page-header .page-title {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .notes-panel {
  background-color: #16213e !important;
  border-color: #2a2a4a !important;
}

[data-theme="dark"] .notes-header {
  border-bottom-color: #2a2a4a !important;
}

[data-theme="dark"] .notes-header-title {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .category-panel {
  background-color: #16213e !important;
  border-color: #2a2a4a !important;
}

[data-theme="dark"] .category-header-title {
  color: #c8d6e5 !important;
}

[data-theme="dark"] .category-tree-wrapper .el-tree-node__content {
  color: #c8d6e5 !important;
}

[data-theme="dark"] .view-dialog .el-dialog__body {
  color: #e8e8e8 !important;
}

[data-theme="dark"] .view-dialog .view-summary {
  background-color: #0f3460 !important;
  border-left-color: #409eff !important;
  color: #c8d6e5 !important;
}

/* ========== 响应式基础 ========== */
/* 平板/大手机横屏 */
@media screen and (max-width: 1024px) {
  body {
    font-size: 14px;
  }
}

/* 手机 */
@media screen and (max-width: 768px) {
  body {
    font-size: 13px;
  }
}
</style>

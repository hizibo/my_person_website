<template>
  <div class="study-page">
    <div class="page-header">
      <h1 class="page-title">我的学习</h1>
    </div>
    <div class="coming-soon">
      <div class="coming-icon">📚</div>
      <h2 class="coming-title">学习中心</h2>
      <p class="coming-desc">这里将展示学习历程、课程笔记、学习计划等内容</p>
      <el-tag type="info" size="large" effect="plain">🚧 开发中，敬请期待...</el-tag>
    </div>
  </div>
</template>

<script setup>
// 学习页面逻辑
</script>

<style scoped>
.study-page {
  padding: 20px;
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
  color: #303133;
}

.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  text-align: center;
}

.coming-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.coming-title {
  font-size: 22px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px;
}

.coming-desc {
  font-size: 14px;
  color: #909399;
  margin: 0 0 20px;
}
</style>
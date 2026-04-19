<template>
  <div class="personal-website">
    <div class="sidebar">
      <h1 class="logo">个人网站</h1>
      <nav class="nav">
        <router-link to="/study" class="nav-item">我的学习</router-link>
        <router-link to="/notes" class="nav-item">我的笔记</router-link>
        <router-link to="/website" class="nav-item">我的网站</router-link>
        <router-link to="/tools" class="nav-item">我的工具</router-link>
      </nav>
    </div>
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
// 父页面逻辑暂时为空
</script>

<style scoped>
.personal-website {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.logo {
  font-size: 1.5rem;
  margin-bottom: 30px;
  text-align: center;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  color: #ecf0f1;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background-color: #34495e;
}

.nav-item.router-link-active {
  background-color: #3498db;
  color: white;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f9f9f9;
}
</style>
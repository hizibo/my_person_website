<template>
  <div class="personal-website" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- 移动端顶部栏 -->
    <div class="mobile-header" @click="toggleSidebar">
      <span class="hamburger" :class="{ active: sidebarOpen }">
        <span></span>
        <span></span>
        <span></span>
      </span>
      <span class="mobile-title">个人网站</span>
    </div>

    <!-- 遮罩层 -->
    <div class="overlay" v-if="sidebarOpen" @click="sidebarOpen = false"></div>

    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-inner">
        <h1 class="logo">🌟 个人网站</h1>
        <nav class="nav">
          <router-link v-if="isLoggedIn && hasPerm('plan')" to="/plan" class="nav-item" @click="closeSidebarOnMobile">
            <span class="nav-icon">📋</span>
            <span class="nav-text">计划</span>
          </router-link>
          <router-link v-if="isLoggedIn && hasPerm('notes')" to="/notes" class="nav-item" @click="closeSidebarOnMobile">
            <span class="nav-icon">📝</span>
            <span class="nav-text">笔记</span>
          </router-link>
          <router-link v-if="isLoggedIn && hasPerm('website')" to="/website" class="nav-item" @click="closeSidebarOnMobile">
            <span class="nav-icon">🌐</span>
            <span class="nav-text">网站</span>
          </router-link>
          <router-link v-if="isLoggedIn && hasPerm('permission')" to="/permission" class="nav-item" @click="closeSidebarOnMobile">
            <span class="nav-icon">🔑</span>
            <span class="nav-text">权限</span>
          </router-link>
          <router-link to="/tools" class="nav-item" @click="closeSidebarOnMobile">
            <span class="nav-icon">🧰</span>
            <span class="nav-text">工具</span>
          </router-link>
        </nav>
        <!-- 登录状态指示 -->
        <div class="auth-status" v-if="isLoggedIn">
          <span class="auth-user">👤 {{ username }}</span>
          <span class="auth-logout" @click="handleLogout">退出</span>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const sidebarOpen = ref(false)
const route = useRoute()
const router = useRouter()

// 登录状态（响应式，通过事件刷新）
const isLoggedIn = ref(!!localStorage.getItem('auth_token'))
const username = ref(localStorage.getItem('auth_username') || '')
const userPermissions = ref(getUserPermissions())

function getUserPermissions() {
  const perms = localStorage.getItem('auth_permissions') || ''
  return perms ? perms.split(',').filter(p => p.trim()) : []
}

// 判断用户是否有某权限（admin 拥有 all，全部放行）
function hasPerm(key) {
  return userPermissions.value.includes('all') || userPermissions.value.includes(key)
}

const refreshAuthState = () => {
  isLoggedIn.value = !!localStorage.getItem('auth_token')
  username.value = localStorage.getItem('auth_username') || ''
  userPermissions.value = getUserPermissions()
}

onMounted(() => {
  window.addEventListener('auth-change', refreshAuthState)
})
onUnmounted(() => {
  window.removeEventListener('auth-change', refreshAuthState)
})

// 路由变化时关闭侧边栏
watch(() => route.path, () => {
  sidebarOpen.value = false
})

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebarOnMobile = () => {
  // 移动端点击导航后关闭侧边栏
  if (window.innerWidth <= 768) {
    sidebarOpen.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('auth_username')
  localStorage.removeItem('auth_permissions')
  window.dispatchEvent(new CustomEvent('auth-change', { detail: { action: 'logout' } }))
  router.push('/tools')
}
</script>

<style scoped>
.personal-website {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ========== 移动端顶部栏 ========== */
.mobile-header {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  height: 50px;
  background: #2c3e50;
  color: white;
  padding: 0 16px;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.hamburger {
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  padding: 4px;
}

.hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: white;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

.mobile-title {
  font-size: 16px;
  font-weight: 600;
}

/* ========== 遮罩层 ========== */
.overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #1e2a3a 0%, #2c3e50 100%);
  color: white;
  flex-shrink: 0;
  transition: transform 0.3s ease;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-inner {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  font-size: 1.4rem;
  margin-bottom: 30px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  color: #bdc3c7;
  text-decoration: none;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
}

.nav-item:hover {
  background-color: #34495e;
  color: white;
}

.nav-item.router-link-active {
  background-color: #3498db;
  color: white;
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.nav-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ========== 登录状态 ========== */
.auth-status {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #3d566e;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
}

.auth-user {
  color: #bdc3c7;
}

.auth-logout {
  color: #e74c3c;
  cursor: pointer;
  transition: color 0.2s;
}

.auth-logout:hover {
  color: #ff6b6b;
}

/* ========== 主内容区 ========== */
.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #f5f7fa;
  padding-top: 0;
  min-width: 0;
}

/* ========== 响应式：平板 ========== */
@media screen and (max-width: 1024px) {
  .sidebar {
    width: 200px;
  }

  .logo {
    font-size: 1.2rem;
  }

  .nav-item {
    font-size: 14px;
    padding: 10px 12px;
  }
}

/* ========== 响应式：手机 ========== */
@media screen and (max-width: 768px) {
  .personal-website {
    flex-direction: column;
  }

  .mobile-header {
    display: flex;
  }

  .overlay {
    display: block;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 260px;
    z-index: 1000;
    transform: translateX(-100%);
    padding-top: 50px;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-inner {
    height: calc(100vh - 50px);
    padding-top: 16px;
  }

  .main-content {
    padding-top: 50px;
    height: 100vh;
  }
}
</style>

import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'
import axios from 'axios'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, { locale: zhCn })
app.use(router)
app.mount('#app')

// ========== 全局登录状态事件 ==========
// 通过 window 事件通知各组件刷新登录状态
window.dispatchEvent(new CustomEvent('auth-change', { detail: { action: 'init' } }))

// ========== 全局 Axios 拦截器 ==========

// 请求拦截：自动附加 Token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截：401 未认证 → 清除登录状态并跳转到工具页
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_username')
      window.dispatchEvent(new CustomEvent('auth-change', { detail: { action: 'logout' } }))
      window.location.href = '/#/tools'
    }
    return Promise.reject(error)
  }
)

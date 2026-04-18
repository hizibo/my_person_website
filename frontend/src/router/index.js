import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/tools/xmind',
    name: 'XmindTool',
    component: () => import('@/views/tools/XmindTool.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import PersonalWebsite from '@/views/PersonalWebsite.vue'

const routes = [
  {
    path: '/',
    component: PersonalWebsite,
    children: [
      {
        path: '',
        redirect: '/plan' // 默认重定向到"我的计划"
      },
      {
        path: 'plan',
        name: 'Plan',
        component: () => import('@/views/plan/Plan.vue')
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('@/views/notes/Notes.vue')
      },
      {
        path: 'website',
        name: 'Website',
        component: () => import('@/views/website/Website.vue')
      },
      {
        path: 'tools',
        name: 'Tools',
        component: () => import('@/views/tools/Tools.vue')
      },
      {
        path: 'tools/xmind',
        name: 'XmindTool',
        component: () => import('@/views/tools/XmindTool.vue')
      },
      {
        path: 'tools/json',
        name: 'JsonTool',
        component: () => import('@/views/tools/JsonTool.vue')
      },
      {
        path: 'tools/datagen',
        name: 'BatchDataGen',
        component: () => import('@/views/tools/BatchDataGen.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：未登录时只能访问工具页，其他页面重定向到工具页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const isToolsPage = to.path === '/tools' || to.path.startsWith('/tools/')

  if (!token && !isToolsPage) {
    // 未登录访问非工具页 → 重定向到工具页
    next('/tools')
  } else {
    next()
  }
})

export default router

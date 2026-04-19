import { createRouter, createWebHistory } from 'vue-router'
import PersonalWebsite from '@/views/PersonalWebsite.vue'

const routes = [
  {
    path: '/',
    component: PersonalWebsite,
    children: [
      {
        path: '',
        redirect: '/study' // 默认重定向到“我的学习”
      },
      {
        path: 'study',
        name: 'Study',
        component: () => import('@/views/study/Study.vue')
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
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
import { createRouter, createWebHistory } from 'vue-router'
import PersonalWebsite from '@/views/PersonalWebsite.vue'

// 菜单权限配置：路由名 -> 权限标识
const routePermissionMap = {
  'Plan': 'plan',
  'Notes': 'notes',
  'Website': 'website',
  'Permission': 'permission'
}

// 获取当前用户权限列表
function getUserPermissions() {
  const perms = localStorage.getItem('auth_permissions') || ''
  return perms ? perms.split(',').filter(p => p.trim()) : []
}

// 判断用户是否有某个权限（admin 拥有全部权限）
function hasPermission(permKey) {
  const perms = getUserPermissions()
  return perms.includes('all') || perms.includes(permKey)
}

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
      },
      {
        path: 'permission',
        name: 'Permission',
        component: () => import('@/views/permission/Permission.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：登录 + 权限校验
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const isToolsPage = to.path === '/tools' || to.path.startsWith('/tools/')

  // 未登录只能访问工具页
  if (!token && !isToolsPage) {
    next('/tools')
    return
  }

  // 已登录时检查菜单权限
  if (token) {
    const permKey = routePermissionMap[to.name]
    if (permKey && !hasPermission(permKey)) {
      // 无权限 → 跳转到工具页
      next('/tools')
      return
    }
  }

  next()
})

export default router
export { hasPermission, getUserPermissions, routePermissionMap }

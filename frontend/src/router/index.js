import { createRouter, createWebHistory } from 'vue-router'
import { isMobile } from '../utils/device'

// 公共路由
const routes = [
  {
    path: '/',
    redirect: isMobile() ? '/mobile' : '/desktop'
  },
  {
    path: '/desktop',
    component: () => import('@/views/desktop/DesktopLayout.vue'),
    redirect: '/desktop/inbound',
    children: [
      {
        path: 'inbound',
        component: () => import('@/views/desktop/InboundManagement.vue'),
        meta: { title: '入库管理' }
      },
      {
        path: 'outbound',
        component: () => import('@/views/desktop/OutboundManagement.vue'),
        meta: { title: '出库管理' }
      },
      {
        path: 'stock',
        component: () => import('@/views/desktop/StockQuery.vue'),
        meta: { title: '库存查询' }
      },
      {
        path: 'supplier',
        component: () => import('@/views/desktop/SupplierManagement.vue'),
        meta: { title: '供应商管理' }
      },
      {
        path: 'report',
        component: () => import('@/views/desktop/MonthlyReport.vue'),
        meta: { title: '月度报表' }
      }
    ]
  },
  {
    path: '/mobile',
    component: () => import('@/views/mobile/MobileLayout.vue'),
    redirect: '/mobile/inbound',
    children: [
      {
        path: 'inbound',
        component: () => import('@/views/mobile/MobileInbound.vue'),
        meta: { title: '入库' }
      },
      {
        path: 'stock',
        component: () => import('@/views/mobile/MobileStock.vue'),
        meta: { title: '库存' }
      },
      {
        path: 'supplier',
        component: () => import('@/views/mobile/MobileSupplier.vue'),
        meta: { title: '供应商' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 学生食堂管理系统`
  }
  next()
})

export default router
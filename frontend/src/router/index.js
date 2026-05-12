import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/recommendations', name: 'Recommendations', component: () => import('../views/Recommendations.vue') },
  { path: '/rankings', name: 'Rankings', component: () => import('../views/Rankings.vue') },
  { path: '/positions', name: 'Positions', component: () => import('../views/Positions.vue') },
  { path: '/stock/:code', name: 'StockDetail', component: () => import('../views/StockDetail.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/pages/LandingPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPage
    }
    // Задел на будущее:
    // { path: '/dashboard', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') }
  ]
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import LandingPage from '@/pages/LandingPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPage,
      meta: { title: 'Нумерия — Образовательная экономическая игра' }
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('@/pages/AuthPage.vue'),
      meta: { title: 'Авторизация | Нумерия' }
    },
    {
      path: '/game',
      name: 'game',
      component: () => import('@/pages/GamePage.vue'),
      meta: { title: 'Игровое поле | Нумерия', requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  const hasSession = Boolean(localStorage.getItem('access_token') && localStorage.getItem('user_data'))
  if (to.meta.requiresAuth && !hasSession) {
    next({ name: 'auth', query: { mode: 'login' } })
    return
  }
  next()
})

export default router
import { createRouter, createWebHistory } from 'vue-router'
import Interview from '../views/Interview.vue'
import History from '../views/History.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Interview',
      component: Interview
    },
    {
      path: '/history',
      name: 'History',
      component: History
    }
  ]
})

export default router 
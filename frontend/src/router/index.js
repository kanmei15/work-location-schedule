import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import ChangePassword from '../components/ChangePassword.vue'
import WorkLocationSchedule from '../components/WorkLocationSchedule.vue'

import { useAuthStore } from '../stores/auth'

const routes = [
    { path: '/login', component: Login },
    { path: '/change-password', component: ChangePassword },
    {
        path: '/',
        component: WorkLocationSchedule,
        beforeEnter: async (to, from, next) => {
            const auth = useAuthStore()
            await auth.checkAuth()
            if (!auth.isAuthenticated) {
                next('/login')
            } else {
                next()
            }
        }
    }
]

export default createRouter({
    history: createWebHistory(),
    routes,
})

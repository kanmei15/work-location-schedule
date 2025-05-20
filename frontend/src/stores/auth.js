import { defineStore } from 'pinia'
import { login, refreshToken, api } from '../api/auth'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: false,
        user: null,
    }),
    actions: {
        async login(email, password) {
            const result = await login(email, password)
            // ログイン成功後にユーザー情報を取得
            const response = await api.get('/auth/me', { withCredentials: true })
            this.user = response.data
            this.isAuthenticated = true
            return result
        },
        async checkAuth() {
            try {
                const response = await api.get('/auth/me', { withCredentials: true })
                this.user = response.data
                this.isAuthenticated = true
            } catch (error) {
                this.user = null
                this.isAuthenticated = false
            }
        },
        logout() {
            api.post('/auth/logout', {}, { withCredentials: true })
            this.user = null
            this.isAuthenticated = false
        },
    }
})

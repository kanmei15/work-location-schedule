import axios from 'axios'
import { getCookie } from '../utils/cookie'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    withCredentials: true,
})

api.interceptors.request.use((config) => {
    // CSRFトークンをヘッダーに追加
    const csrfToken = getCookie('csrf_token')
    if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
    }

    return config
})

export async function login(email, password) {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const response = await api.post('/api/auth/login', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        withCredentials: true
    })
    return response.data
}

export async function refreshToken() {
    const response = await api.post('/api/auth/refresh', null, {
        withCredentials: true
    })
    return response.data
}

export async function logout() {
    await api.post('/api/auth/logout', null, {
        withCredentials: true
    })
}

export { api }
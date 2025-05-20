import axios from 'axios'
import axiosRetry from 'axios-retry'
import { getCookie } from '../utils/cookie'

//const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const BASE_URL = import.meta.env.VITE_API_BASE_URL

const api = axios.create({
    baseURL: BASE_URL,
    withCredentials: true,
})

axiosRetry(api, {
    retries: 3, // 最大3回リトライ
    retryDelay: (retryCount) => retryCount * 1000, // 1秒、2秒、3秒の間隔でリトライ
    retryCondition: (error) => {
        // 5xxエラー、ネットワークエラー時にリトライ
        return axiosRetry.isNetworkOrIdempotentRequestError(error) || error.response?.status >= 500
    }
})

api.interceptors.request.use((config) => {
    // CSRFトークンをヘッダーに追加
    const csrfToken = getCookie('csrf_token')
    if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
    }

    return config
})

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            // サーバーからのレスポンスがあり、ステータスコードがエラーの場合
            const status = error.response.status
            const data = error.response.data

            // 例: 401 Unauthorized ならログイン画面へ誘導など
            if (status === 401) {
                alert('ログイン期限が切れました。再度ログインしてください。')
                // 例えば、ここでリダイレクト処理を入れてもよい
                // location.href = '/login'
            } else if (status >= 400 && status < 500) {
                alert(data.message || 'リクエストに問題があります。')
            } else if (status >= 500) {
                alert('サーバーエラーが発生しました。時間を置いて再度お試しください。')
            }
        } else if (error.request) {
            // サーバーからレスポンスがない場合
            alert('サーバーからの応答がありません。ネットワーク接続を確認してください。')
        } else {
            // それ以外のエラー（設定ミスなど）
            alert('エラーが発生しました: ' + error.message)
        }
        return Promise.reject(error)
    }
)

export async function login(email, password) {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const response = await api.post('/auth/login', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        withCredentials: true
    })
    return response.data
}

export async function refreshToken() {
    const response = await api.post('/auth/refresh', null, {
        withCredentials: true
    })
    return response.data
}

export async function logout() {
    await api.post('/auth/logout', null, {
        withCredentials: true
    })
}

export { api }
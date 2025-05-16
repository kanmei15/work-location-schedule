import { getCookie } from '../utils/cookie'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function fetchUsers() {
    const res = await fetch(`${BASE_URL}/api/users`, {
        credentials: 'include'
    })
    return res.json()
}

export async function fetchSchedules() {
    const res = await fetch(`${BASE_URL}/api/schedules`, {
        credentials: 'include'
    })
    return res.json()
}

export async function updateSchedule(userId, work_date, location) {
    const csrfToken = getCookie('csrf_token')

    await fetch(`${BASE_URL}/schedules`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify({ user_id: userId, work_date, location }),
        credentials: 'include'
    })
}

// 祝日取得
export async function fetchHolidays(year) {
    const res = await fetch(`https://holidays-jp.github.io/api/v1/${year}/date.json`)
    return await res.json() // 例: { "2025-01-01": "元日", ... }
}

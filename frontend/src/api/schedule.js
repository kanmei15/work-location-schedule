import axios from 'axios'
import { api } from './auth.js'

const THIRDPARTY_URL = import.meta.env.THIRDPARTY_URL || 'https://holidays-jp.github.io'

export async function fetchUsers() {
    const res = await api.get('/api/users')
    return res.data
}

export async function fetchSchedules() {
    const res = await api.get('/api/schedules')
    return res.data
}

export async function updateSchedule(userId, work_date, location) {
    await api.post('/api/schedules', {
        user_id: userId,
        work_date,
        location
    })
}

export async function updateCommutingAllowance(userId, newAllowance) {
    await api.patch(`/api/users/${userId}/commuting_allowance`, { allowance: newAllowance })
}

// 祝日取得
export async function fetchHolidays(year) {
    //const res = await fetch(`${THIRDPARTY_URL}/api/v1/${year}/date.json`)
    const res = await axios.get(`${THIRDPARTY_URL}/api/v1/${year}/date.json`)
    return await res.json() // 例: { "2025-01-01": "元日", ... }
}
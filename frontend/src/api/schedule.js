import axios from 'axios'
import { api } from './auth.js'

const THIRDPARTY_URL = import.meta.env.THIRDPARTY_URL || 'https://holidays-jp.github.io'

export async function fetchUsers() {
    const res = await api.get('/users')
    return res.data
}

export async function fetchSchedules() {
    const res = await api.get('/schedules')
    return res.data
}

export async function updateSchedule(userId, work_date, location) {
    await api.post('/schedules', {
        user_id: userId,
        work_date,
        location
    })
}

export async function updateCommutingAllowance(userId, newAllowance) {
    await api.patch(`/users/${userId}/commuting_allowance`, { allowance: newAllowance })
}

// 祝日取得
export async function fetchHolidays(year) {
    const res = await axios.get(`${THIRDPARTY_URL}/api/v1/${year}/date.json`)
    return await res.data // 例: { "2025-01-01": "元日", ... }
}
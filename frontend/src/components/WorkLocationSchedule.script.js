import { ref, computed } from 'vue'
import { fetchUsers, fetchSchedules, updateSchedule } from '../api/schedule.js'
import { fetchHolidays } from '../api/schedule.js'
import { api } from '../api/auth.js'

export const currentUser = ref(null)
export const users = ref([])
export const schedules = ref([])

// 年リスト（現在の年の前後1年）
const currentYear = new Date().getFullYear()
export const yearOptions = [currentYear - 1, currentYear, currentYear + 1]

export const year = ref(currentYear)
export const month = ref(new Date().getMonth() + 1)

const holidays = ref({})
const locations = ['-', '本', '赤', '分', '東', '在', '休', '客', 'そ', '大', '沖', '博']

export const daysInMonth = computed(() =>
    Array.from({ length: new Date(year.value, month.value, 0).getDate() }, (_, i) => i + 1)
)

export async function loadData() {
    users.value = await fetchUsers()
    const yyyymm = `${year.value}-${String(month.value).padStart(2, '0')}`
    schedules.value = await fetchSchedules(yyyymm)
    holidays.value = await fetchHolidays(year.value)
}

export function getLocation(userId, day) {
    const date = `${year.value}-${String(month.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const record = schedules.value.find(s => s.user_id === userId && s.work_date === date)
    return record?.location
}

// ヘッダのスタイル変更
export function getHeaderStyle(day) {
    const dateStr = `${year.value}-${String(month.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const date = new Date(dateStr)
    const weekday = date.getDay()
    const isSunday = weekday === 0
    const isSaturday = weekday === 6
    const isHoliday = holidays.value[dateStr]

    let color = 'black'
    let backgroundColor = '#ffffff'  // 平日の背景色

    if (isHoliday || isSunday) {
        color = 'red'
        backgroundColor = '#fdd' // 日曜・祝日の背景色
    } else if (isSaturday) {
        color = 'blue'
        backgroundColor = '#ddf' // 土曜の背景色
    }

    return {
        color,
        backgroundColor,
        textAlign: 'center',
        padding: '4px'
    }
}

// 曜日名取得
export function getWeekdayName(day) {
    const date = new Date(year.value, month.value - 1, day)
    const names = ['日', '月', '火', '水', '木', '金', '土']
    return names[date.getDay()]
}

// 通勤切替の判定
export function getCommuteChangeStatus(commuteAllowance, remoteDays, workingDaysInMonth) {
    const ratio = remoteDays / workingDaysInMonth;
    const twoThirds = 2 / 3;

    if (commuteAllowance === '申請' && ratio >= twoThirds) {
        return '要';
    }
    if (commuteAllowance === '停止' && ratio > twoThirds) {
        return '要';
    }
    return '';
}

export function getCellStyle(userId, day) {
    const loc = getLocation(userId, day)
    const colorMap = {
        '本': '#ffffff', '赤': '#c6e0b4', '分': '#c65911', '東': '#ffe699',
        '在': '#00b050', '休': '#ff0000', '客': '#ccccff', 'そ': '#ff00ff', '大': '#bdd7ee',
        '沖': '#7030a0', '博': '#f3e5f5'
    }

    const dateStr = `${year.value}-${String(month.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const dateObj = new Date(dateStr)
    const isSunday = dateObj.getDay() === 0
    const isSaturday = dateObj.getDay() === 6
    const isHoliday = dateStr in holidays.value

    // 背景色の決定
    let bg = colorMap[loc] || 'transparent'
    if (!loc) {
        if (isHoliday || isSunday || isSaturday) {
            bg = '#d9d9d9'
        }
    }

    // 編集不可ユーザー用スタイルを追加
    const isLocked = currentUser.value?.id !== userId
    const style = {
        backgroundColor: bg
    }

    if (isLocked) {
        style.cursor = 'not-allowed'
        style.opacity = 0.6 // 少し薄く表示
    } else {
        style.cursor = 'pointer'
    }

    return style
}

// 在宅日数カウント
export function countZai(userId) {
    // 年と月に基づいて在宅日数をカウント
    const yyyymm = `${year.value}-${String(month.value).padStart(2, '0')}`

    return schedules.value.filter(
        (s) => s.user_id === userId && s.location === '在' && s.work_date.startsWith(yyyymm)
    ).length
}

//
export function calculateWorkingDays(year, month) {
    const totalDays = new Date(year, month, 0).getDate();
    let workingDays = 0;

    for (let day = 1; day <= totalDays; day++) {
        const date = new Date(year, month - 1, day);
        const dateStr = date.toISOString().split('T')[0];
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        const isHoliday = holidays.value[dateStr];

        if (!isWeekend && !isHoliday) {
            workingDays++;
        }
    }

    return workingDays;
}

function isHoliday(date) {
    // API or 祝日リストに応じて実装（例：固定祝日 or API）
    return false;
}

export async function fetchCurrentUser() {
    const res = await api.get('/api/auth/me')
    currentUser.value = res.data
}

export async function toggleLocation(userId, day) {
    if (!currentUser.value || currentUser.value.id !== userId) return  // ← ここでロック！

    const date = `${year.value}-${String(month.value).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const current = getLocation(userId, day)
    const currentIndex = locations.indexOf(current || '-')
    const next = locations[(currentIndex + 1) % locations.length]

    if (next === '-') {
        // 該当のスケジュールを削除
        schedules.value = schedules.value.filter(s => !(s.user_id === userId && s.work_date === date))
        await updateSchedule(userId, date, null)
    } else {
        // 既存があれば更新、なければ追加
        const index = schedules.value.findIndex(s => s.user_id === userId && s.work_date === date)
        if (index >= 0) {
            schedules.value[index].location = next
        } else {
            schedules.value.push({ user_id: userId, work_date: date, location: next })
        }
        await updateSchedule(userId, date, next)
    }
}


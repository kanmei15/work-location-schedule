<template>
    <div>
        <div class="date-selectors">
            <label for="year-select">年月:</label>
            <select id="year-select" name="year" v-model="year">
                <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
            </select>
            <select id="month-select" name="month" v-model="month">
                <option v-for="m in Array(12).fill().map((_, i) => i + 1)" :key="m" :value="m">{{ m }}</option>
            </select>
        </div>

        <table border="1">
            <thead>
                <tr>
                    <th>名前</th>
                    <th>通勤<br />手当</th>
                    <th>在宅<br />日数</th>
                    <th>通勤<br />切替</th>
                    <th v-for="day in daysInMonth" :key="day" :style="getHeaderStyle(day)">
                        {{ day }}<br>
                        {{ getWeekdayName(day) }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in users" :key="user.id">
                    <td>{{ user.name }}</td>
                    <!--<td>{{ user.commuting_allowance }}</td>-->
                    <td @click="user.id === currentUser?.id ? toggleCommutingAllowance(user) : null"
                        :style="{ cursor: user.id === currentUser?.id ? 'pointer' : 'not-allowed' }">
                        {{ user.commuting_allowance || '-' }}
                    </td>
                    <td>{{ countZai(user.id) }}</td>
                    <!-- 通勤切替表示 -->
                    <td>
                        {{
                            getCommuteChangeStatus(
                                user.commuting_allowance,
                                countZai(user.id),
                                calculateWorkingDays(year, month)
                            )
                        }}
                    </td>
                    <!-- 日ごとの勤務場所 -->
                    <td v-for="day in daysInMonth" :key="`${user.id}-${day}`"
                        @click="user.id === currentUser?.id ? toggleLocation(user.id, day) : null"
                        :style="getCellStyle(user.id, day)">
                        {{ getLocation(user.id, day) || '-' }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup>
import {
    currentUser,
    users,
    schedules,
    yearOptions,
    year,
    month,
    daysInMonth,
    getLocation,
    getHeaderStyle,
    getWeekdayName,
    getCommuteChangeStatus,
    getCellStyle,
    countZai,
    calculateWorkingDays,
    fetchCurrentUser,
    toggleLocation,
    toggleCommutingAllowance,
    loadData,
} from './WorkLocationSchedule.script.js'

import { ref, computed, watch, onMounted } from 'vue'

onMounted(() => {
    fetchCurrentUser()
    loadData()
})

watch([year, month], () => {
    loadData()
})
</script>

<style scoped src="./WorkLocationSchedule.style.css"></style>

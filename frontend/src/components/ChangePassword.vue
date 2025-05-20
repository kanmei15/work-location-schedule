<template>
    <div>
        <h2>パスワード変更</h2>
        <form @submit.prevent="handleChangePassword">
            <div>
                <label for="currentPassword">現在のパスワード:</label>
                <input id="currentPassword" type="password" v-model="currentPassword" required />
            </div>
            <div>
                <label for="newPassword">新しいパスワード:</label>
                <input id="newPassword" type="password" v-model="newPassword" required />
            </div>
            <div>
                <label for="confirmPassword">新しいパスワード（確認）:</label>
                <input id="confirmPassword" type="password" v-model="confirmPassword" required />
            </div>
            <button type="submit">変更</button>
        </form>
        <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
        <p v-if="successMessage" style="color: green">{{ successMessage }}</p>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/auth.js'

const router = useRouter()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const successMessage = ref('')

const handleChangePassword = async () => {
    errorMessage.value = ''
    successMessage.value = ''

    if (newPassword.value !== confirmPassword.value) {
        errorMessage.value = '新しいパスワードが一致しません。'
        return
    }

    try {
        await api.post('/auth/change-password', {
            old_password: currentPassword.value,
            new_password: newPassword.value
        })
        successMessage.value = 'パスワードが変更されました。'

        // フォームをリセット
        currentPassword.value = ''
        newPassword.value = ''
        confirmPassword.value = ''

        // パスワード変更後にページ遷移
        router.push('/')

    } catch (error) {
        errorMessage.value = error.response?.data?.detail || 'パスワード変更に失敗しました。'
    }
}
</script>

<style scoped>
form div {
    margin-bottom: 10px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input {
    width: 100%;
    padding: 8px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

button {
    width: 100%;
    padding: 10px;
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
}

button:hover {
    background-color: #1976D2;
}
</style>
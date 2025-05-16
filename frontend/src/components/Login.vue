<template>
    <div>
        <h2>ログイン</h2>
        <form @submit.prevent="handleLogin">
            <div>
                <label for="email">Email:</label>
                <input id="email" name="email" v-model="email" placeholder="Email" type="email" required
                    autocomplete="email" />
            </div>
            <div>
                <label for="password">Password:</label>
                <input id="password" name="password" v-model="password" type="password" placeholder="Password" required
                    autocomplete="current-password" />
            </div>
            <button type="submit">ログイン</button>
        </form>
        <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const errorMessage = ref('')  // エラーメッセージ用の変数
const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
    try {
        const result = await authStore.login(email.value, password.value)

        if (result.is_default_password) {
            router.push('/change-password')
        } else {
            router.push('/')
        }
    } catch (e) {
        errorMessage.value = 'ログインに失敗しました。もう一度お試しください。'  // エラーメッセージ表示
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
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
}

button:hover {
    background-color: #45a049;
}
</style>

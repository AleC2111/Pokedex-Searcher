<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'


const username = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()

async function login() {
  try {
    const { data, statusCode } = await useFetch(`${API_BASE_URL}/token`, {

      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }).post(new URLSearchParams({
      username: username.value,
      password: password.value,
    })).json()

    if (statusCode.value !== 200) {
      throw new Error(data.value?.detail || 'Credenciales incorrectas')
    }

    localStorage.setItem('token', data.value.access_token)
    window.dispatchEvent(new CustomEvent('auth-change'))
    router.push('/')
  } catch (err) {
    errorMsg.value = err.message
  }
}
</script>

<template>
  <div class="auth-container">
    <h2>Iniciar Sesión</h2>
    <div class="text-container form-box">
      <input v-model="username" placeholder="Usuario" type="text" />
      <input v-model="password" placeholder="Contraseña" type="password" />
      <button @click="login">Entrar</button>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <p>
        ¿No tienes cuenta? <router-link to="/register">Regístrate aquí</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
}

.form-box {
  display: flex;
  flex-direction: column;
  width: 300px;
  align-items: center;
}

input {
  margin: 10px;
  padding: 8px;
  width: 90%;
  border-radius: 3px;
}

button {
  background-color: #f76998;
  margin: 10px;
  padding: 8px 16px;
  border-radius: 5px;
  transition: scale 0.2s ease-in;
  cursor: pointer;
}

button:hover {
  scale: 1.1;
}

.error {
  color: red;
  font-size: 0.9rem;
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'


const username = ref('')
const password = ref('')
const errorMsg = ref('')
const router = useRouter()

async function register() {
  try {
    const { data: regData, statusCode: regStatus } = await useFetch(
      `${API_BASE_URL}/register`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )
      .post(
        JSON.stringify({
          username: username.value,
          password: password.value,
        }),
      )
      .json()

    if (regStatus.value !== 200) {
      throw new Error(regData.value?.detail || 'Error en el registro')
    }

    const { data: loginData, statusCode: loginStatus } = await useFetch(
      `${API_BASE_URL}/token`,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      },
    )

      .post(
        new URLSearchParams({
          username: username.value,
          password: password.value,
        }),
      )
      .json()

    if (loginStatus.value === 200) {
      localStorage.setItem('token', loginData.value.access_token)
      window.dispatchEvent(new CustomEvent('auth-change'))
      router.push('/')
    } else {
      router.push('/login')
    }
  } catch (err) {
    errorMsg.value = err.message
  }
}
</script>

<template>
  <div class="auth-container">
    <h2>Registro</h2>
    <div class="text-container form-box">
      <input v-model="username" placeholder="Usuario" type="text" />
      <input v-model="password" placeholder="Contraseña" type="password" />
      <button @click="register">Registrarse</button>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <p>¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión</router-link></p>
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

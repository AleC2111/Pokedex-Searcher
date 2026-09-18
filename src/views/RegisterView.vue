<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'

const username = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const router = useRouter()

async function register() {
  errorMsg.value = ''

  if (!username.value.trim() || !lastName.value.trim() || !email.value.trim() || !password.value || !confirmPassword.value) {
    errorMsg.value = 'Todos los campos son obligatorios.'
    return
  }

  if (password.value.length < 8) {
    errorMsg.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMsg.value = 'Las contraseñas no coinciden.'
    return
  }

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
          last_name: lastName.value,
          email: email.value,
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
    <form @submit.prevent="register" class="text-container form-box">
      <input v-model="username" placeholder="Nombre de usuario" type="text" required />
      <input v-model="lastName" placeholder="Apellido" type="text" required />
      <input v-model="email" placeholder="Correo electrónico" type="email" required />
      <input v-model="password" placeholder="Contraseña (mín. 8 caracteres)" type="password" minlength="8" required />
      <input v-model="confirmPassword" placeholder="Confirmar contraseña" type="password" minlength="8" required />
      <button type="submit">Registrarse</button>
      <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      <p>¿Ya tienes cuenta? <router-link to="/login">Inicia Sesión</router-link></p>
    </form>
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
  width: 320px;
  align-items: center;
}

input {
  margin: 8px 0;
  padding: 10px;
  width: 100%;
  border-radius: 5px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  background-color: #f76998;
  color: white;
  margin: 12px 0;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  transition: transform 0.2s ease-in;
  cursor: pointer;
  width: 100%;
}

button:hover {
  transform: scale(1.03);
}

.error {
  color: #d9534f;
  font-size: 0.9rem;
  margin-top: 5px;
  text-align: center;
}
</style>

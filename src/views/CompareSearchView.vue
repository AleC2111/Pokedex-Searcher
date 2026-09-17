<script setup>
import { ref, watch, nextTick } from 'vue'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'

const BASE_URL = `${API_BASE_URL}/api`


const search1 = ref('')
const search2 = ref('')

const p1 = ref(null)
const p2 = ref(null)

const loading1 = ref(false)
const loading2 = ref(false)
const error1 = ref('')
const error2 = ref('')

let timer1 = null
let timer2 = null

const canvas1 = ref(null)
const canvas2 = ref(null)

function statsGraph(ctx, baseStats) {
  const statNames = ['HP', 'ATK', 'DEF', 'SP. ATK', 'SP. DEF', 'SPD']
  const width = ctx.canvas.width
  const height = ctx.canvas.height

  ctx.clearRect(0, 0, width, height)
  const margin = 5
  const barHeight = height - margin * 2
  const maxValue = 255

  baseStats.forEach((statValue, i) => {
    const barWidth = (statValue / maxValue) * (width - margin * 10)
    const x = width - margin - barWidth
    const y = margin + i * 20 + 10

    if (statValue < 40) ctx.fillStyle = '#c6001a'
    else if (statValue < 60) ctx.fillStyle = '#fd5441'
    else if (statValue < 80) ctx.fillStyle = '#ff752b'
    else if (statValue < 100) ctx.fillStyle = '#fffb2b'
    else if (statValue < 130) ctx.fillStyle = '#64ff2b'
    else if (statValue < 150) ctx.fillStyle = '#02c819'
    else if (statValue < 180) ctx.fillStyle = '#27ff90'
    else ctx.fillStyle = '#27edff'
    ctx.fillRect(x, y, barWidth, barHeight * 0.1)

    ctx.fillStyle = '#010101'
    ctx.font = '10px Arial'
    ctx.fillText(statNames[i] + ': ' + statValue, x - 65, y + 10)
  })
}

async function fetchPokemon(name, slot) {
  if (!name) return

  if (slot === 1) {
    loading1.value = true
    error1.value = ''
    p1.value = null
  } else {
    loading2.value = true
    error2.value = ''
    p2.value = null
  }

  try {
    const { data, statusCode } = await useFetch(`${BASE_URL}/pokemon/${name.toLowerCase()}`)
      .get()
      .json()
    if (statusCode.value !== 200) {
      throw new Error('No encontrado')
    }

    const parsed = {
      id: data.value.id,
      name: data.value.name,
      image: data.value.sprites.front_default,
      types: data.value.types.map((t) => t.type.name).join(', '),
      abilities: data.value.abilities.map((a) => a.ability.name).join(', '),
      stats: data.value.stats.map((s) => s.base_stat),
    }

    if (slot === 1) {
      p1.value = parsed
      await nextTick()
      if (canvas1.value) {
        statsGraph(canvas1.value.getContext('2d'), parsed.stats)
      }
    } else {
      p2.value = parsed
      await nextTick()
      if (canvas2.value) {
        statsGraph(canvas2.value.getContext('2d'), parsed.stats)
      }
    }
  } catch (err) {
    if (slot === 1) error1.value = err.message
    else error2.value = err.message
  } finally {
    if (slot === 1) loading1.value = false
    else loading2.value = false
  }
}

watch(search1, (newValue) => {
  if (!newValue) {
    p1.value = null
    error1.value = ''
    return
  }
  clearTimeout(timer1)
  timer1 = setTimeout(() => {
    fetchPokemon(newValue, 1)
  }, 1000)
})

watch(search2, (newValue) => {
  if (!newValue) {
    p2.value = null
    error2.value = ''
    return
  }
  clearTimeout(timer2)
  timer2 = setTimeout(() => {
    fetchPokemon(newValue, 2)
  }, 1000)
})
</script>

<template>
  <main class="compare-container">
    <h2>Buscador Comparativo</h2>
    <div class="side-by-side">
      <div class="pokemon-slot">
        <div class="search-box text-container">
          <input v-model="search1" placeholder="Nombre o ID..." />
        </div>

        <div v-if="loading1" class="text-container">Cargando...</div>
        <div v-if="error1" class="error text-container">{{ error1 }}</div>

        <div v-if="p1" class="text-container p-card">
          <h3 class="capitalize">{{ p1.name }}</h3>
          <p>ID: {{ p1.id }}</p>
          <img :src="p1.image" alt="sprite" class="sprite" />
          <div class="info-section">
            <p><strong>Tipos:</strong> {{ p1.types }}</p>
            <p><strong>Habilidades:</strong> {{ p1.abilities }}</p>
            <hr />
            <p><strong>Estadísticas:</strong></p>
            <div class="canvas-container">
              <canvas ref="canvas1" width="200" height="150"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="pokemon-slot">
        <div class="search-box text-container">
          <input v-model="search2" placeholder="Nombre o ID..." />
        </div>

        <div v-if="loading2" class="text-container">Cargando...</div>
        <div v-if="error2" class="error text-container">{{ error2 }}</div>

        <div v-if="p2" class="text-container p-card">
          <h3 class="capitalize">{{ p2.name }}</h3>
          <p>ID: {{ p2.id }}</p>
          <img :src="p2.image" alt="sprite" class="sprite" />
          <div class="info-section">
            <p><strong>Tipos:</strong> {{ p2.types }}</p>
            <p><strong>Habilidades:</strong> {{ p2.abilities }}</p>
            <hr />
            <p><strong>Estadísticas:</strong></p>
            <div class="canvas-container">
              <canvas ref="canvas2" width="200" height="150"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.compare-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.side-by-side {
  display: flex;
  flex-direction: row;
  width: 100%;
  justify-content: center;
  gap: 10px;
}

.pokemon-slot {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 50%;
}

.search-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 90%;
  padding: 10px;
}

.search-box input {
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
  border-radius: 3px;
}

.text-container {
  background-color: #feffd7;
  color: black;
  margin: 4px;
  padding: 8px;
  border-radius: 5px;
}

.p-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 90%;
  margin-top: 10px;
}

.sprite {
  width: 120px;
  height: 120px;
}

.capitalize {
  text-transform: capitalize;
  margin: 0;
}

.info-section {
  width: 100%;
  text-align: left;
  font-size: 0.9rem;
}

.canvas-container {
  display: flex;
  justify-content: center;
  width: 100%;
}

.error {
  color: red;
  font-weight: bold;
}

@media screen and (max-width: 480px) {
  .side-by-side {
    gap: 5px;
  }
  .sprite {
    width: 80px;
    height: 80px;
  }
  .info-section {
    font-size: 0.75rem;
  }
  .search-box input {
    font-size: 0.8rem;
  }
}
</style>

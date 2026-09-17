<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'

const favorites = ref([])
const detailedFavorites = ref([])
const loading = ref(true)

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

function setCanvasRef(el, stats) {
  if (el) {
    statsGraph(el.getContext('2d'), stats)
  }
}

async function fetchFavorites() {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const { data, statusCode } = await useFetch(`${API_BASE_URL}/api/favorites`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }).get().json()
    
    if (statusCode.value === 200) {
      favorites.value = data.value
      await loadDetails(data.value)
    }
  } catch (error) {
    console.error('Error fetching favorites:', error)
  } finally {
    loading.value = false
  }
}

async function loadDetails(favs) {
  const promises = favs.map(async (fav) => {
    try {
      const { data, statusCode } = await useFetch(`${API_BASE_URL}/api/pokemon/${fav.pokemon_name}`).get().json()
      if (statusCode.value === 200) {
        return {
          id_fav: fav.id,
          pokemon_name: fav.pokemon_name,
          id: data.value.id,
          name: data.value.name,
          image: data.value.sprites.front_default,
          types: data.value.types.map(t => t.type.name).join(', '),
          abilities: data.value.abilities.map(a => a.ability.name).join(', '),
          stats: data.value.stats.map(s => s.base_stat)
        }
      }
    } catch {
       return null
    }
  })
  
  const results = await Promise.all(promises)
  detailedFavorites.value = results.filter(p => p !== null)
}

async function removeFavorite(pokemon_name) {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const { statusCode } = await useFetch(`${API_BASE_URL}/api/favorites/${pokemon_name}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }).delete().json()
    
    if (statusCode.value === 200) {
      favorites.value = favorites.value.filter(fav => fav.pokemon_name !== pokemon_name)
      detailedFavorites.value = detailedFavorites.value.filter(fav => fav.pokemon_name !== pokemon_name)
    }
  } catch (error) {
    console.error('Error removing favorite:', error)
  }
}


onMounted(() => {
  fetchFavorites()
})
</script>

<template>
  <div class="favorites-container">
    <h2>Mis Favoritos</h2>
    <div v-if="loading" class="text-container">Cargando favoritos...</div>
    <div v-else-if="favorites.length === 0" class="text-container">
      No tienes ningún Pokémon favorito aún.
    </div>
    <div v-else class="grid-container">
      <div v-for="fav in detailedFavorites" :key="fav.pokemon_name" class="favorite-card text-container p-card">
        <h3 class="capitalize">{{ fav.name }}</h3>
        <p>ID: {{ fav.id }}</p>
        <img :src="fav.image" alt="sprite" class="sprite" />
        <div class="info-section">
          <p><strong>Tipos:</strong> {{ fav.types }}</p>
          <p><strong>Habilidades:</strong> {{ fav.abilities }}</p>
          <hr />
          <p><strong>Estadísticas:</strong></p>
          <div class="canvas-container">
            <canvas :ref="(el) => setCanvasRef(el, fav.stats)" width="200" height="150"></canvas>
          </div>
        </div>
        <button @click="removeFavorite(fav.pokemon_name)" class="remove-btn">Eliminar</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  width: 80%;
}
.favorite-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.remove-btn {
  background-color: #f76998;
  margin-top: 10px;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  border: none;
}
.remove-btn:hover {
  scale: 1.1;
}
.p-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding: 15px;
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
</style>

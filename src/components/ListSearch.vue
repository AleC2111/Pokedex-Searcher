<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'

const offset_option = ref('')
const types_option = ref('')
const selectedGen = ref('')
const canvasRef = ref(null)

const availableTypes = [
  'fire',
  'water',
  'grass',
  'electric',
  'ground',
  'rock',
  'poison',
  'ghost',
  'fighting',
  'psychic',
  'steel',
  'normal',
  'flying',
  'dragon',
  'ice',
  'dark',
  'fairy',
  'bug',
]
const maxCount = 1351
let nextPage = ref(false)
let previousPage = ref(false)
let loading = ref(false)
let timer = null
let globalOffset = 0
let globalType = ''

const BASE_URL = `${API_BASE_URL}/api`

const displayedPokemon = ref([])
const hoveredPokemon = ref(null)

function checkTypeExists(typeSearching) {
  return availableTypes.includes(typeSearching)
}

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

function existsPreviousOrNext(offset, limit) {
  previousPage.value = offset - limit >= 0
  nextPage.value = offset + limit <= maxCount
}

async function fetchPokemonDetails(pokemonNames) {
  const promises = pokemonNames.map(async (name) => {
    try {
      const { data, statusCode } = await useFetch(`${BASE_URL}/pokemon/${name}`).get().json()
      if (statusCode.value !== 200) return null
      return data.value
    } catch {
      return null
    }
  })

  const results = await Promise.all(promises)
  return results
    .filter((p) => p !== null)
    .map((p) => ({
      id: p.id,
      name: p.name,
      image: p.sprites.front_default,
      types: p.types.map((t) => t.type.name).join(', '),
      abilities: p.abilities.map((a) => a.ability.name).join(', '),
      stats: p.stats.map((s) => s.base_stat),
    }))
}

async function startSimpleSearch(offset = 0, limit = 20) {
  const { data } = await useFetch(`${BASE_URL}/pokemon?offset=${offset}&limit=${limit}`)
    .get()
    .json()
  existsPreviousOrNext(offset, limit)

  const names = data.value.results.map((r) => r.name)
  displayedPokemon.value = await fetchPokemonDetails(names)
}

async function startTypeSearch(type, offset = 0, limit = 20) {
  const { data } = await useFetch(`${BASE_URL}/type/${type}`).get().json()
  existsPreviousOrNext(offset, limit)

  const sliced = data.value.pokemon.slice(offset, limit + offset)
  const names = sliced.map((r) => r.pokemon.name)
  displayedPokemon.value = await fetchPokemonDetails(names)
}

async function searchParameters(offset = '', typeSearching = '', limit = 20) {
  try {
    loading.value = true
    displayedPokemon.value = []

    if (offset === null || offset === '' || isNaN(offset)) {
      offset = 0
    } else {
      offset = parseInt(offset)
    }

    if (offset < 0 || offset > maxCount) {
      throw new Error('Goes over the maximum or minimum available')
    }
    if (!checkTypeExists(typeSearching) && typeSearching !== '' && typeSearching !== null) {
      throw new Error("Type doesn't exist")
    }
    globalOffset = offset
    globalType = typeSearching

    if (typeSearching === '' || typeSearching === null) {
      await startSimpleSearch(offset, limit)
    } else {
      await startTypeSearch(typeSearching, offset, limit)
    }
  } catch (error) {
    alert('Error: Ha ocurrido un error en la busqueda')
    console.log('Error: ' + error.message)
  } finally {
    loading.value = false
  }
}

function searchNextPage() {
  searchParameters(globalOffset + 20, globalType)
}

function searchPreviousPage() {
  searchParameters(globalOffset - 20, globalType)
}

const generations = {
  1: { offset: 0, limit: 151 },
  2: { offset: 151, limit: 100 },
  3: { offset: 251, limit: 135 },
  4: { offset: 386, limit: 107 },
  5: { offset: 493, limit: 156 },
  6: { offset: 649, limit: 72 },
  7: { offset: 721, limit: 88 },
  8: { offset: 809, limit: 96 },
  9: { offset: 905, limit: 120 },
}

function loadGeneration() {
  if (selectedGen.value && generations[selectedGen.value]) {
    const gen = generations[selectedGen.value]
    offset_option.value = gen.offset
    types_option.value = ''
    searchParameters(gen.offset, '', gen.limit)
  }
}

onMounted(() => {
  searchParameters()
})

watch([offset_option, types_option], (newValues, _) => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    searchParameters(newValues[0], newValues[1])
  }, 1000)
})

async function onHover(pokemon) {
  hoveredPokemon.value = pokemon
  await nextTick()
  if (canvasRef.value) {
    statsGraph(canvasRef.value.getContext('2d'), pokemon.stats)
  }
}

function onLeave() {
  hoveredPokemon.value = null
}
</script>

<template>
  <h2>Busqueda por lista</h2>
  <button v-if="previousPage === true" @click="searchPreviousPage">Anterior</button>
  <button v-if="nextPage === true" @click="searchNextPage">Siguiente</button>
  <div class="text-container" id="general-info">
    <input
      id="offset"
      v-model="offset_option"
      type="number"
      placeholder="Id de inicio de la busqueda"
    />
    <input id="types" v-model="types_option" placeholder="Tipo a buscar" />
    <select
      v-model="selectedGen"
      @change="loadGeneration"
      style="margin: 6px; padding: 5px; border-radius: 3px"
    >
      <option value="">Selecciona Generación</option>
      <option value="1">Generación 1 (1-151)</option>
      <option value="2">Generación 2 (152-251)</option>
      <option value="3">Generación 3 (252-386)</option>
      <option value="4">Generación 4 (387-493)</option>
      <option value="5">Generación 5 (494-649)</option>
      <option value="6">Generación 6 (650-721)</option>
      <option value="7">Generación 7 (722-809)</option>
      <option value="8">Generación 8 (810-905)</option>
      <option value="9">Generación 9 (906-1025)</option>
    </select>
  </div>

  <hr />
  <div class="text-container" v-if="loading">Cargando datos...</div>

  <div class="list-container" v-else>
    <div class="pokemon-list">
      <div
        v-for="(pokemon, _) in displayedPokemon"
        :key="pokemon.id"
        class="list-item"
        @mouseenter="onHover(pokemon)"
        @mouseleave="onLeave"
      >
        <span class="pokemon-id">#{{ pokemon.id }}</span>
        <span class="pokemon-name">{{ pokemon.name }}</span>
        <img :src="pokemon.image" class="small-sprite" alt="sprite" />
        <span class="pokemon-type">{{ pokemon.types }}</span>
      </div>
    </div>

    <div class="hover-panel text-container">
      <div
        v-if="hoveredPokemon"
        style="display: flex; flex-direction: column; align-items: center; width: 100%"
      >
        <h3>{{ hoveredPokemon.name.toUpperCase() }}</h3>
        <img :src="hoveredPokemon.image" style="width: 150px; height: 150px" />
        <p>ID: {{ hoveredPokemon.id }}</p>
        <p>Tipos: {{ hoveredPokemon.types }}</p>
        <p>Habilidades: {{ hoveredPokemon.abilities }}</p>
        <div style="display: flex; justify-content: center; width: 100%; margin-top: 10px">
          <canvas ref="canvasRef" width="200" height="150"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
input {
  margin: 6px;
  border-radius: 3px;
  padding: 5px;
}
button {
  background-color: #f76998;
  margin: 5px;
  border-radius: 5px;
  transition: scale 0.2s ease-in;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}
button:hover {
  scale: 1.1;
}

#general-info {
  align-items: center;
  justify-content: center;
  display: flex;
}

.text-container {
  background-color: #feffd7;
  color: black;
  margin: 4px;
  padding: 8px;
  display: flex;
  border-radius: 5px;
  min-width: 50%;
}

.list-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  position: relative;
}

.pokemon-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-item {
  display: flex;
  align-items: center;
  background-color: #feffd7;
  color: black;
  padding: 10px;
  border-radius: 5px;
  cursor: pointer;
}

.list-item:hover {
  background-color: #f0f0c0;
}

.small-sprite {
  width: 50px;
  height: 50px;
  margin-left: 15px;
}

.pokemon-id {
  font-weight: bold;
  margin-right: 15px;
  width: 40px;
}

.pokemon-name {
  text-transform: capitalize;
  width: 150px;
}

.pokemon-type {
  margin-left: auto;
  font-style: italic;
}

.hover-panel {
  position: sticky;
  top: 20px;
  width: 250px;
  height: auto;
  min-height: 450px;
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-left: 20px;
}

@media screen and (max-width: 480px) {
  .text-container {
    margin: 4px;
    padding: 8px;
    display: inline-block;
    min-width: 75%;
  }
  #general-info {
    align-items: normal;
    justify-content: inherit;
    display: inline-block;
  }
  .hover-panel {
    display: none;
  }
}
</style>

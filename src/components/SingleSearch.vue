<script setup>
import { ref, watch } from 'vue'
import { useFetch } from '@vueuse/core'
import { API_BASE_URL } from '@/config'


const search_bar = ref('')
const name = ref(null)
const pokedex_id = ref(null)
const image = ref(null)
const types = ref(null)
const abilities = ref(null)
const height_weight = ref(null)
const move_list = ref(null)
const shiny_toggle = ref(null)
const stats_graph = ref(null)
const evolution_line = ref(null)

const BASE_URL = `${API_BASE_URL}/api`

let currentData = { default_image: '/default-img.jpg', shiny_image: '/shiny-img.jpg' }
let loading = ref(false)
let timer = null
const is_favorite = ref(false)
const saved = ref(false)
const removed = ref(false)

function parseData(data) {
  let id = data.id
  let pokemonName = data.name
  let stats = data.stats.map((s) => s.base_stat)
  let abilitiesData = data.abilities.map((a) => a.ability.name)
  let typesData = data.types.map((t) => t.type.name)
  let height = data.height / 10
  let weight = data.weight / 10
  let moves = data.moves
  let default_image = data.sprites.front_default
  let shiny_image = data.sprites.front_shiny

  currentData = {
    id,
    name: pokemonName,
    base_stats: stats,
    abilities: abilitiesData,
    types: typesData,
    height,
    weight,
    moves,
    default_image,
    shiny_image,
    favorite: false,
  }
  return currentData
}

function changeAbilitiesUI(abilities) {
  return 'Habilidades: ' + abilities.join(', ')
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
    ctx.fillText(statNames[i] + ': ' + statValue, x - 65, y + 10)
  })
}

async function changeMoveList(moveData, movesContainer) {
  movesContainer.innerHTML = 'Cargando movimientos...'

  const movePromises = moveData.map(async (move) => {
    const { data, statusCode } = await useFetch(`${BASE_URL}/move/${move.move.name}`).get().json()
    if (statusCode.value !== 200) return {}
    return data.value
  })

  const parsedMoves = await Promise.all(movePromises)
  movesContainer.innerHTML = ''

  parsedMoves.forEach((parsedData) => {
    let moveElementName = document.createElement('div')
    moveElementName.textContent = parsedData.name
    movesContainer.appendChild(moveElementName)

    let parsedMove = document.createElement('div')
    parsedMove.textContent =
      'Clase de daño: ' +
      parsedData.damage_class.name +
      ' Poder base: ' +
      parsedData.power +
      ' Precision: ' +
      parsedData.accuracy +
      ' Prioridad: ' +
      parsedData.priority
    movesContainer.appendChild(parsedMove)

    let moveDescription = document.createElement('div')
    if (parsedData.effect_entries.length !== 0) {
      const entry =
        parsedData.effect_entries.find((e) => e.language.name === 'en') ||
        parsedData.effect_entries[0]
      moveDescription.textContent = entry.effect
    } else {
      moveDescription.textContent = 'No hay descripción'
    }
    movesContainer.appendChild(moveDescription)

    let blank = document.createElement('hr')
    movesContainer.appendChild(blank)
  })
}

function changeShiny() {
  if (!shiny_toggle.value.checked) {
    image.value.src = currentData.default_image
  } else {
    image.value.src = currentData.shiny_image
  }
}

async function searchEvolutionChain(evolutionChainUrl) {
  const parts = evolutionChainUrl.split('/')
  const id = parts[parts.length - 2]
  const { data, statusCode } = await useFetch(`${BASE_URL}/evolution-chain/${id}`).get().json()
  if (statusCode.value !== 200) return ''
  return data.value.chain
}

async function parsedEvolution(evolutionChainUrl, speciesData) {
  let evolutionData = await searchEvolutionChain(evolutionChainUrl)

  let baseForm = []
  let firstPhaseForm = []
  let lastPhaseForm = []

  baseForm.push(evolutionData.species.name)
  if (evolutionData.evolves_to && evolutionData.evolves_to.length > 0) {
    for (let i = 0; i < evolutionData.evolves_to.length; i++) {
      firstPhaseForm.push(evolutionData.evolves_to[i].species.name)
      if (evolutionData.evolves_to[i].evolves_to) {
        for (let j = 0; j < evolutionData.evolves_to[i].evolves_to.length; j++) {
          lastPhaseForm.push(evolutionData.evolves_to[i].evolves_to[j].species.name)
        }
      }
    }
  }

  let fullLine = [baseForm]
  if (firstPhaseForm.length > 0) fullLine.push(firstPhaseForm)
  if (lastPhaseForm.length > 0) fullLine.push(lastPhaseForm)

  let formattedLine = formatEvolutionLine(fullLine)
  formattedLine = formatVarieties(formattedLine, speciesData)

  return formattedLine
}

function formatVarieties(formattedLine, speciesData) {
  if (speciesData && speciesData.varieties.length > 1) {
    const varieties = speciesData.varieties.filter((v) => !v.is_default).map((v) => v.pokemon.name)
    if (varieties.length > 0) {
      formattedLine += ' | Formas alternativas: ' + varieties.join(', ')
    }
  }
  return formattedLine
}

function formatEvolutionLine(fullLine) {
  let formattedLine = ''
  for (let i = 0; i < fullLine.length; i++) {
    let separator = ' -> '
    if (fullLine[i].length > 1) {
      separator = ', '
    }
    for (let j = 0; j < fullLine[i].length; j++) {
      if (i === fullLine.length - 1 && j === fullLine[i].length - 1) {
        formattedLine = formattedLine + fullLine[i][j]
      } else {
        formattedLine = formattedLine + fullLine[i][j] + separator
      }
    }
  }
  return formattedLine
}

async function updateEvolutionLine(pokemonName) {
  try {
    const { data, statusCode } = await useFetch(`${BASE_URL}/pokemon-species/${pokemonName}`)
      .get()
      .json()
    if (statusCode.value !== 200) return pokemonName
    let evolutionChainUrl = data.value.evolution_chain.url
    return await parsedEvolution(evolutionChainUrl, data.value)
  } catch (e) {
    return pokemonName
  }
}

async function changeUI(parsed) {
  const canvas = stats_graph.value
  const ctx = canvas.getContext('2d')

  name.value.textContent = parsed.name.toUpperCase()
  pokedex_id.value.textContent = 'Id: ' + parsed.id
  changeShiny()
  types.value.textContent = parsed.types
  abilities.value.textContent = changeAbilitiesUI(parsed.abilities)
  statsGraph(ctx, parsed.base_stats)
  height_weight.value.textContent =
    'Altura: ' + parsed.height + ' m, Peso: ' + parsed.weight + ' kg'
  evolution_line.value.textContent = await updateEvolutionLine(parsed.name)
  await changeMoveList(parsed.moves, move_list.value)
}

async function checkIsFavorite(pokemonName) {
  const token = localStorage.getItem('token')
  if (!token) return false
  try {
    const { data, statusCode } = await useFetch(`${BASE_URL}/favorites`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .get()
      .json()
    if (statusCode.value === 200) {
      return data.value.some((f) => f.pokemon_name === pokemonName)
    }
  } catch (e) {
    console.error(e)
  }
  return false
}

async function startSearch(pokemonName) {
  try {
    const { data, statusCode } = await useFetch(`${BASE_URL}/pokemon/${pokemonName}`).get().json()
    if (statusCode.value !== 200) throw new Error('Pokemon not found')
    let parsed = parseData(data.value)

    is_favorite.value = await checkIsFavorite(parsed.name)
    currentData.favorite = is_favorite.value

    changeUI(parsed)
  } catch (error) {
    alert('Error: Ha ocurrido un error en la busqueda')
    console.log('Error: ' + error.message)
  } finally {
    loading.value = false
  }
}

async function saveFavoritePokemon() {
  if (pokedex_id.value.textContent === 'Id') {
    alert('Busca un Pokemon primero')
    return
  }
  const token = localStorage.getItem('token')
  if (!token) {
    alert('Debes iniciar sesión para guardar favoritos')
    return
  }

  if (currentData.favorite) {
    try {
      const { statusCode } = await useFetch(`${BASE_URL}/favorites/${currentData.name}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .delete()
        .json()
      if (statusCode.value === 200) {
        currentData.favorite = false
        is_favorite.value = false
        saved.value = false
        removed.value = true
      }
    } catch (e) {
      console.error(e)
    }
  } else {
    try {
      const { statusCode } = await useFetch(`${BASE_URL}/favorites`, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      })
        .post(
          JSON.stringify({
            pokemon_name: currentData.name,
            pokemon_data: JSON.stringify(currentData),
          }),
        )
        .json()
      if (statusCode.value === 200) {
        currentData.favorite = true
        is_favorite.value = true
        saved.value = true
        removed.value = false
      }
    } catch (e) {
      console.error(e)
    }
  }
}

watch(search_bar, (newValue, _) => {
  if (!newValue) return
  loading.value = true
  saved.value = false
  removed.value = false
  is_favorite.value = false
  clearTimeout(timer)
  timer = setTimeout(() => {
    startSearch(newValue)
  }, 1000)
})
</script>

<template>
  <div>
    <h2>Buscador de datos de Pokemon</h2>
    <div class="text-container">
      <input v-model="search_bar" placeholder="Busca por nombre o id..." value="" />
      <div class="text-container" style="max-width: 30%">
        Shiny:
        <input ref="shiny_toggle" type="checkbox" @click="changeShiny" />
      </div>
      <button ref="save_favorite" @click="saveFavoritePokemon">Guardar en Favoritos</button>
    </div>

    <h3 class="changing-container" v-if="loading">Cargando datos...</h3>
    <h3 class="changing-container" v-if="removed">Eliminado!</h3>
    <h3 class="changing-container" v-if="saved">Guardado!</h3>
    <h3 class="changing-container" style="" v-if="is_favorite">Favorito</h3>
    <div id="general-info">
      <h3 ref="name" style="margin: 4px">Nombre</h3>
      <h4 ref="pokedex_id" style="margin: 4px">Id</h4>
      <img ref="image" alt="Imagen de Pokemon" src="/default-img.jpg" />

      <div id="pokemon-info">
        <div class="text-container" ref="types">Tipos:</div>
        <div class="text-container" ref="abilities">Habilidades:</div>
        <hr />
        <div class="text-container" ref="base-stats">Estadisticas:</div>
        <div class="text-container">
          <canvas ref="stats_graph" width="200" height="150"></canvas>
        </div>
        <div class="text-container" ref="height_weight">Peso y Altura:</div>
      </div>
    </div>
    <div>
      <h5>Línea evolutiva</h5>
      <div ref="evolution_line" class="text-container"></div>
    </div>
    <div>
      <h5>Movimientos</h5>
      <div id="move-list" ref="move_list"></div>
    </div>
  </div>
</template>

<style scoped>
img {
  min-width: 20%;
  min-height: 20%;
  max-width: 20%;
  max-height: 20%;
  margin: 10px;
}
input {
  margin: 6px;
  border-radius: 3px;
}
button {
  background-color: #f76998;
  margin: 5px;
  border-radius: 5px;
  transition: scale 0.2s ease-in;
}
button:hover {
  cursor: pointer;
  scale: 1.1;
}

#general-info {
  align-items: center;
  justify-content: center;
  display: flex;
}

.changing-container {
  background-color: #feffd7;
  margin: 4px;
  padding: 8px;
  display: flex;
  border-radius: 5px;
  text-align: center;
  justify-content: center;
  color: rgb(188, 59, 182);
}

.text-container {
  background-color: #feffd7;
  color: black;
  margin: 4px;
  padding: 8px;
  display: flex;
  border-radius: 5px;
}

#move-list {
  background-color: #feffd7;
  color: black;
  margin: 4px;
  padding: 8px;
  border-radius: 5px;
  display: block;
}

@media screen and (max-width: 480px) {
  img {
    min-width: 40%;
    min-height: 40%;
    max-width: 40%;
    max-height: 40%;
    margin: 5px;
  }
  .text-container {
    margin: 4px;
    padding: 8px;
    display: inline-block;
    border-radius: 5px;
    min-width: 20%;
  }
  #general-info {
    align-items: normal;
    justify-content: inherit;
    display: inline-block;
  }
}
</style>

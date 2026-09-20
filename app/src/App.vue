<script setup>
import { computed, onBeforeUnmount, ref, shallowRef, watch } from 'vue'

const palettes = [
  {
    id: 'db8',
    name: 'DawnBringer 8',
    colors: [
      [220, 245, 255],
      [230, 200, 110],
      [100, 185, 100],
      [80, 140, 215],
      [215, 115, 85],
      [100, 105, 100],
      [85, 65, 95],
      [0, 0, 0],
    ],
  },
  {
    id: 'db16',
    name: 'DawnBringer 16',
    colors: [
      [20, 12, 28],
      [68, 36, 52],
      [48, 52, 109],
      [78, 74, 78],
      [133, 76, 48],
      [52, 101, 36],
      [208, 70, 72],
      [117, 113, 97],
      [89, 125, 206],
      [210, 125, 44],
      [133, 149, 161],
      [109, 170, 44],
      [210, 170, 153],
      [109, 194, 202],
      [218, 212, 94],
      [222, 238, 214],
    ],
  },
  {
    id: 'db32',
    name: 'DawnBringer 32',
    colors: [
      [0, 0, 0],
      [34, 32, 52],
      [69, 40, 60],
      [102, 57, 49],
      [143, 86, 59],
      [223, 113, 38],
      [217, 160, 102],
      [238, 195, 154],
      [251, 242, 54],
      [153, 229, 80],
      [106, 190, 48],
      [55, 148, 110],
      [75, 105, 47],
      [82, 75, 36],
      [50, 60, 57],
      [63, 63, 116],
      [48, 96, 130],
      [91, 110, 225],
      [99, 155, 255],
      [95, 205, 228],
      [203, 219, 252],
      [255, 255, 255],
      [155, 173, 183],
      [132, 126, 135],
      [105, 106, 106],
      [89, 86, 82],
      [118, 66, 138],
      [172, 50, 50],
      [217, 87, 99],
      [215, 123, 186],
      [143, 151, 74],
      [138, 111, 48],
    ],
  },
]

const fileInput = ref(null)
const sourceImage = shallowRef(null)
const sourceUrl = ref('')
const outputUrl = ref('')
const fileName = ref('')
const fileSize = ref(0)
const sourceDimensions = ref(null)
const outputDimensions = ref(null)
const pixelSize = ref(8)
const paletteId = ref('db16')
const theme = ref('dark')
const currentYear = new Date().getFullYear()
const status = ref('idle')
const errorMessage = ref('')
const isDragging = ref(false)
const fileLoadId = ref(0)
const conversionId = ref(0)

const selectedPalette = computed(
  () => palettes.find((palette) => palette.id === paletteId.value) ?? palettes[0],
)

const isConverting = computed(() => status.value === 'converting')
const hasImage = computed(() => Boolean(sourceImage.value))
const isDark = computed(() => theme.value === 'dark')

const croppedDimensions = computed(() => {
  const dimensions = sourceDimensions.value
  const size = Number(pixelSize.value)

  if (!dimensions || !Number.isInteger(size) || size < 1) {
    return null
  }

  return {
    width: dimensions.width - (dimensions.width % size),
    height: dimensions.height - (dimensions.height % size),
  }
})

const canConvert = computed(
  () =>
    hasImage.value &&
    !isConverting.value &&
    croppedDimensions.value?.width > 0 &&
    croppedDimensions.value?.height > 0,
)

const statusText = computed(() => {
  if (status.value === 'loading') return 'Loading'
  if (status.value === 'converting') return 'Converting'
  if (status.value === 'done') return 'Ready'
  if (status.value === 'error') return 'Error'
  return hasImage.value ? 'Ready' : ''
})

const downloadName = computed(() => `${baseName(fileName.value)}_pixelart.png`)

function baseName(name) {
  return name.replace(/\.[^/.]+$/, '') || 'image'
}

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDimensions(dimensions) {
  return dimensions ? `${dimensions.width} x ${dimensions.height}` : '--'
}

function colorValue(color) {
  return `rgb(${color.join(', ')})`
}

function openFilePicker() {
  fileInput.value?.click()
}

function toggleTheme() {
  theme.value = isDark.value ? 'light' : 'dark'
}

function handleFileSelection(event) {
  const [file] = event.target.files ?? []
  event.target.value = ''
  if (file) loadImage(file)
}

function handleDrop(event) {
  isDragging.value = false
  const [file] = event.dataTransfer.files ?? []
  if (file) loadImage(file)
}

function loadImage(file) {
  if (!file.type.startsWith('image/')) {
    errorMessage.value = 'Choose an image file.'
    status.value = 'error'
    return
  }

  const currentLoadId = ++fileLoadId.value
  conversionId.value += 1
  revokeUrl(sourceUrl)
  revokeOutput()
  sourceImage.value = null
  sourceDimensions.value = null
  fileName.value = file.name
  fileSize.value = file.size
  errorMessage.value = ''
  status.value = 'loading'

  const objectUrl = URL.createObjectURL(file)
  const image = new Image()
  image.decoding = 'async'
  image.onload = () => {
    if (currentLoadId !== fileLoadId.value) {
      URL.revokeObjectURL(objectUrl)
      return
    }

    sourceImage.value = image
    sourceUrl.value = objectUrl
    sourceDimensions.value = {
      width: image.naturalWidth,
      height: image.naturalHeight,
    }
    status.value = 'ready'
  }
  image.onerror = () => {
    if (currentLoadId !== fileLoadId.value) {
      URL.revokeObjectURL(objectUrl)
      return
    }

    URL.revokeObjectURL(objectUrl)
    errorMessage.value = 'This image could not be read.'
    status.value = 'error'
  }
  image.src = objectUrl
}

function revokeUrl(url) {
  if (url.value) {
    URL.revokeObjectURL(url.value)
    url.value = ''
  }
}

function revokeOutput() {
  revokeUrl(outputUrl)
  outputDimensions.value = null
}

function removeImage() {
  fileLoadId.value += 1
  conversionId.value += 1
  revokeUrl(sourceUrl)
  revokeOutput()
  sourceImage.value = null
  sourceDimensions.value = null
  fileName.value = ''
  fileSize.value = 0
  errorMessage.value = ''
  status.value = 'idle'
}

function nearestColor(red, green, blue, palette) {
  let closest = palette[0]
  let minimumDistance = Number.POSITIVE_INFINITY

  for (const color of palette) {
    const redDistance = color[0] - red
    const greenDistance = color[1] - green
    const blueDistance = color[2] - blue
    const distance = redDistance ** 2 + greenDistance ** 2 + blueDistance ** 2

    if (distance < minimumDistance) {
      minimumDistance = distance
      closest = color
    }
  }

  return closest
}

function canvasToBlob(canvas) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob)
      } else {
        reject(new Error('The browser could not create a PNG.'))
      }
    }, 'image/png')
  })
}

async function convertImage() {
  if (!canConvert.value || !sourceImage.value || !croppedDimensions.value) return

  const image = sourceImage.value
  const dimensions = croppedDimensions.value
  const size = Number(pixelSize.value)
  const palette = selectedPalette.value.colors
  const currentConversionId = ++conversionId.value

  revokeOutput()
  errorMessage.value = ''
  status.value = 'converting'

  await new Promise((resolve) => window.setTimeout(resolve, 0))

  try {
    const canvas = document.createElement('canvas')
    canvas.width = dimensions.width
    canvas.height = dimensions.height

    const context = canvas.getContext('2d', { willReadFrequently: true })
    if (!context) throw new Error('Canvas is not available in this browser.')

    context.imageSmoothingEnabled = false
    context.drawImage(image, 0, 0)

    const imageData = context.getImageData(0, 0, dimensions.width, dimensions.height)
    const pixels = imageData.data

    for (let y = 0; y < dimensions.height; y += size) {
      for (let x = 0; x < dimensions.width; x += size) {
        let red = 0
        let green = 0
        let blue = 0

        for (let blockY = y; blockY < y + size; blockY += 1) {
          for (let blockX = x; blockX < x + size; blockX += 1) {
            const index = (blockY * dimensions.width + blockX) * 4
            red += pixels[index]
            green += pixels[index + 1]
            blue += pixels[index + 2]
          }
        }

        const area = size ** 2
        const color = nearestColor(red / area, green / area, blue / area, palette)

        for (let blockY = y; blockY < y + size; blockY += 1) {
          for (let blockX = x; blockX < x + size; blockX += 1) {
            const index = (blockY * dimensions.width + blockX) * 4
            pixels[index] = color[0]
            pixels[index + 1] = color[1]
            pixels[index + 2] = color[2]
            pixels[index + 3] = 255
          }
        }
      }
    }

    if (currentConversionId !== conversionId.value) return

    context.putImageData(imageData, 0, 0)
    const blob = await canvasToBlob(canvas)

    if (currentConversionId !== conversionId.value) return

    outputUrl.value = URL.createObjectURL(blob)
    outputDimensions.value = dimensions
    status.value = 'done'
  } catch (error) {
    if (currentConversionId !== conversionId.value) return

    errorMessage.value = error instanceof Error ? error.message : 'Conversion failed.'
    status.value = 'error'
  }
}

watch([pixelSize, paletteId], () => {
  if (isConverting.value) return
  if (outputUrl.value) {
    revokeOutput()
    status.value = hasImage.value ? 'ready' : 'idle'
  }
})

onBeforeUnmount(() => {
  fileLoadId.value += 1
  conversionId.value += 1
  revokeUrl(sourceUrl)
  revokeOutput()
})
</script>

<template>
  <div class="app-shell" :class="`theme-${theme}`">
    <main class="page-content">
      <section class="hero">
        <button
          class="theme-toggle"
          type="button"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        >
          <svg v-if="isDark" class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"></path>
          </svg>
          <svg v-else class="theme-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5 8.5 8.5 0 1 0 20.5 14.5Z"></path>
          </svg>
        </button>
        <h1>Pixel Art Converter</h1>
        <p>Free. No Ads. No tracking. Just Art.</p>
      </section>

      <section class="workspace" aria-label="Pixel art converter">
        <aside class="controls-panel">
          <input
            ref="fileInput"
            class="sr-only"
            type="file"
            accept="image/*"
            @change="handleFileSelection"
          />

          <div
            class="drop-zone"
            :class="{ 'is-dragging': isDragging }"
            role="button"
            tabindex="0"
            @click="openFilePicker"
            @keydown.enter="openFilePicker"
            @keydown.space.prevent="openFilePicker"
            @dragenter.prevent="isDragging = true"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
          >
            <template v-if="!hasImage">
              <span class="upload-glyph" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M12 16V4M12 4 7.5 8.5M12 4l4.5 4.5M4 15.5v2A2.5 2.5 0 0 0 6.5 20h11a2.5 2.5 0 0 0 2.5-2.5v-2" />
                </svg>
              </span>
              <strong>Drop an image here</strong>
              <button class="choose-button" type="button" @click.stop="openFilePicker">Choose image</button>
            </template>
            <template v-else>
              <div class="file-summary">
                <span class="file-badge">IMG</span>
                <span class="file-details">
                  <strong>{{ fileName }}</strong>
                  <span>{{ formatBytes(fileSize) }} / {{ formatDimensions(sourceDimensions) }}</span>
                </span>
                <button
                  class="remove-button"
                  type="button"
                  aria-label="Remove image"
                  @click.stop="removeImage"
                >
                  x
                </button>
              </div>
              <span class="replace-hint">Drop another image or click to replace</span>
            </template>
          </div>

          <div class="controls">
            <div class="control-group">
              <div class="control-label-row">
                <label for="pixel-size">Pixel size</label>
                <output for="pixel-size">{{ pixelSize }} px</output>
              </div>
              <input
                id="pixel-size"
                v-model.number="pixelSize"
                type="range"
                min="2"
                max="64"
                step="1"
                :disabled="!hasImage || isConverting"
              />
            </div>

            <div class="control-group">
              <div class="control-label-row">
                <label for="palette">Palette</label>
              </div>
              <select id="palette" v-model="paletteId" :disabled="!hasImage || isConverting">
                <option v-for="palette in palettes" :key="palette.id" :value="palette.id">
                  {{ palette.name }}
                </option>
              </select>
              <div class="swatches" :aria-label="`${selectedPalette.name} colors`">
                <span
                  v-for="(color, index) in selectedPalette.colors"
                  :key="`${selectedPalette.id}-${index}`"
                  class="swatch"
                  :style="{ backgroundColor: colorValue(color) }"
                  :title="colorValue(color)"
                ></span>
              </div>
            </div>
          </div>

          <div class="action-area">
            <p
              v-if="hasImage && (croppedDimensions?.width === 0 || croppedDimensions?.height === 0)"
              class="inline-warning"
            >
              Choose a smaller pixel size.
            </p>
            <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
            <button class="primary-button" type="button" :disabled="!canConvert" @click="convertImage">
              <span v-if="isConverting" class="button-spinner" aria-hidden="true"></span>
              <span>{{ isConverting ? 'Converting' : outputUrl ? 'Convert again' : 'Convert' }}</span>
            </button>
            <a v-if="outputUrl" class="download-button" :href="outputUrl" :download="downloadName">
              Download PNG
            </a>
          </div>
        </aside>

        <section class="preview-panel" aria-live="polite">
          <div v-if="status !== 'idle'" class="status-pill" :class="`status-${status}`">
            <span class="status-dot" aria-hidden="true"></span>
            {{ statusText }}
          </div>

          <div class="preview-grid">
            <article class="preview-card">
              <div class="card-label">
                <span>Source</span>
                <span>{{ formatDimensions(sourceDimensions) }}</span>
              </div>
              <div class="image-stage" :class="{ 'has-image': sourceUrl }">
                <img v-if="sourceUrl" class="preview-image original-image" :src="sourceUrl" alt="Uploaded source" />
                <div v-else class="empty-state">
                  <span class="empty-icon" aria-hidden="true">+</span>
                  <span>Choose an image</span>
                </div>
              </div>
            </article>

            <article class="preview-card">
              <div class="card-label">
                <span>Result</span>
                <span>{{ formatDimensions(outputDimensions) }}</span>
              </div>
              <div class="image-stage" :class="{ 'has-image': outputUrl }">
                <img v-if="outputUrl" class="preview-image pixel-image" :src="outputUrl" alt="Converted pixel art" />
                <div v-else class="empty-state">
                  <span class="pixel-placeholder" aria-hidden="true">
                    <i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>
                  </span>
                  <span>Convert to preview</span>
                </div>
              </div>
            </article>
          </div>

          <div class="preview-footer">
            <div class="footer-stat">
              <span>Crop</span>
              <strong>{{ formatDimensions(croppedDimensions) }}</strong>
            </div>
            <div class="footer-stat">
              <span>Block</span>
              <strong>{{ pixelSize }} x {{ pixelSize }} px</strong>
            </div>
          </div>
        </section>
      </section>

      <footer class="site-footer">
        <span>&copy; {{ currentYear }} Camilo Hern&aacute;ndez</span>
        <a
          href="https://github.com/blobbeliblob/pixelart_converter"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Pixel Art Converter on GitHub"
        >
          <img src="/favicon.png" alt="GitHub" />
        </a>
      </footer>
    </main>
  </div>
</template>

<style>
@import url('https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap');

:root {
  color: #111111;
  background: #111111;
  font-family: Satoshi, Arial, sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  min-width: 320px;
  margin: 0;
}

button,
input,
select {
  font: inherit;
}

button,
a,
select,
input[type="range"] {
  -webkit-tap-highlight-color: transparent;
}

button,
a {
  cursor: pointer;
}

button:focus-visible,
a:focus-visible,
select:focus-visible,
input:focus-visible,
.drop-zone:focus-visible {
  outline: 2px solid var(--text);
  outline-offset: 3px;
}

.app-shell {
  --text: #111111;
  --muted: rgba(17, 17, 17, 0.68);
  --line: rgba(17, 17, 17, 0.18);
  --panel: rgba(255, 255, 255, 0.82);
  --field: rgba(255, 255, 255, 0.58);
  --soft: rgba(17, 17, 17, 0.07);
  --button: #111111;
  --button-text: #ffffff;
  min-height: 100vh;
  color: var(--text);
  font-family: Satoshi, Arial, sans-serif;
  background-color: #f3f1ed;
  background-position: center;
  background-size: cover;
  background-attachment: fixed;
  background-repeat: no-repeat;
}

.app-shell.theme-dark {
  --text: #ffffff;
  --muted: rgba(255, 255, 255, 0.7);
  --line: rgba(255, 255, 255, 0.2);
  --panel: rgba(13, 13, 13, 0.84);
  --field: rgba(0, 0, 0, 0.22);
  --soft: rgba(255, 255, 255, 0.09);
  --button: #ffffff;
  --button-text: #111111;
  background-color: #111111;
  background-image: linear-gradient(rgba(9, 10, 16, 0.73), rgba(9, 10, 16, 0.82)),
    url('/assets/akihabara_night_pixelart.png');
}

.app-shell.theme-light {
  background-image: linear-gradient(rgba(247, 246, 242, 0.73), rgba(247, 246, 242, 0.82)),
    url('/assets/akihabara_day_pixelart.png');
}

.app-shell * {
  font-family: inherit;
}

.page-content {
  display: flex;
  width: min(1120px, calc(100% - 32px));
  min-height: 100vh;
  margin: 0 auto;
  flex-direction: column;
  padding: 52px 0 20px;
}

.hero {
  position: relative;
  padding: 34px 48px 0;
  text-align: center;
}

.hero h1 {
  margin: 0;
  color: var(--text);
  font-size: clamp(2.5rem, 6vw, 5.2rem);
  font-weight: 700;
  letter-spacing: -0.065em;
  line-height: 0.98;
}

.hero p {
  margin: 18px 0 0;
  color: var(--muted);
  font-size: clamp(0.95rem, 1.8vw, 1.1rem);
  font-weight: 500;
}

.theme-toggle {
  position: absolute;
  top: 0;
  right: 0;
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--panel);
  color: var(--text);
  backdrop-filter: blur(12px);
}

.theme-toggle:hover {
  background: var(--soft);
}

.theme-icon {
  display: block;
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.6;
}

.workspace {
  display: grid;
  width: 100%;
  margin-top: 52px;
  grid-template-columns: 310px minmax(0, 1fr);
  align-items: stretch;
  gap: 16px;
}

.controls-panel,
.preview-panel {
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--panel);
  box-shadow: 0 16px 50px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(16px);
}

.controls-panel {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.preview-panel {
  padding: 20px;
}

.drop-zone {
  display: flex;
  min-height: 160px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--line);
  border-radius: 7px;
  color: var(--muted);
  text-align: center;
  transition: border-color 160ms ease, background 160ms ease;
}

.drop-zone:hover,
.drop-zone.is-dragging {
  border-color: var(--text);
  background: var(--soft);
}

.drop-zone strong {
  color: var(--text);
  font-size: 0.92rem;
  font-weight: 500;
}

.upload-glyph {
  display: grid;
  width: 30px;
  height: 30px;
  margin-bottom: 13px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 50%;
}

.upload-glyph svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  stroke-linecap: square;
  stroke-linejoin: miter;
  stroke-width: 1.5;
}

.choose-button {
  margin-top: 15px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: transparent;
  color: var(--text);
  font-size: 0.78rem;
  font-weight: 500;
}

.choose-button:hover,
.remove-button:hover {
  background: var(--soft);
}

.file-summary {
  display: flex;
  width: calc(100% - 28px);
  align-items: center;
  gap: 10px;
  text-align: left;
}

.file-badge {
  display: grid;
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 5px;
  color: var(--text);
  font-size: 0.6rem;
  font-weight: 700;
}

.file-details {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 3px;
}

.file-details strong {
  overflow: hidden;
  color: var(--text);
  font-size: 0.78rem;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-details span,
.replace-hint {
  color: var(--muted);
  font-size: 0.68rem;
}

.remove-button {
  display: grid;
  width: 25px;
  height: 25px;
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: transparent;
  color: var(--muted);
  font-size: 0.75rem;
}

.replace-hint {
  margin-top: 14px;
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 28px;
}

.control-label-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 10px;
}

.control-label-row label,
.control-label-row output {
  color: var(--text);
  font-size: 0.8rem;
  font-weight: 500;
}

.control-label-row output {
  color: var(--muted);
}

input[type='range'] {
  width: 100%;
  height: 18px;
  margin: 0;
  accent-color: var(--button);
}

input[type='range']:disabled,
select:disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 5px;
  outline: none;
  background: var(--field);
  color: var(--text);
  font-size: 0.8rem;
}

.swatches {
  display: flex;
  overflow: hidden;
  height: 10px;
  margin-top: 13px;
  border-radius: 2px;
}

.swatch {
  min-width: 4px;
  flex: 1;
}

.action-area {
  margin-top: auto;
  padding-top: 30px;
}

.primary-button,
.download-button {
  display: flex;
  width: 100%;
  min-height: 42px;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  font-size: 0.8rem;
  font-weight: 500;
  text-decoration: none;
  transition: opacity 160ms ease, transform 160ms ease;
}

.primary-button {
  gap: 8px;
  border: 1px solid var(--button);
  background: var(--button);
  color: var(--button-text);
}

.primary-button:hover:not(:disabled),
.download-button:hover {
  opacity: 0.78;
  transform: translateY(-1px);
}

.primary-button:disabled {
  cursor: not-allowed;
  opacity: 0.35;
}

.download-button {
  margin-top: 8px;
  border: 1px solid var(--line);
  color: var(--text);
}

.button-spinner {
  width: 12px;
  height: 12px;
  border: 1.5px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 700ms linear infinite;
}

.inline-warning,
.error-message {
  margin: 0 0 11px;
  font-size: 0.75rem;
  line-height: 1.4;
}

.inline-warning {
  color: #9a5b13;
}

.error-message {
  color: #a33e35;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 14px;
  color: var(--muted);
  font-size: 0.72rem;
}

.status-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text);
}

.status-converting .status-dot {
  animation: pulse 900ms ease-in-out infinite alternate;
}

.status-error {
  color: #a33e35;
}

.status-error .status-dot {
  background: #a33e35;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.preview-card {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 7px;
  background: var(--field);
}

.card-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 11px 12px;
  color: var(--muted);
  font-size: 0.72rem;
}

.card-label span:first-child {
  color: var(--text);
  font-weight: 500;
}

.image-stage {
  display: grid;
  min-height: 350px;
  place-items: center;
  overflow: hidden;
  border-top: 1px solid var(--line);
  background-color: var(--soft);
  background-image: linear-gradient(45deg, rgba(127, 127, 127, 0.08) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(127, 127, 127, 0.08) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(127, 127, 127, 0.08) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(127, 127, 127, 0.08) 75%);
  background-position: 0 0, 0 8px, 8px -8px, -8px 0;
  background-size: 16px 16px;
}

.image-stage.has-image {
  padding: 14px;
}

.preview-image {
  display: block;
  max-width: 100%;
  max-height: 470px;
  object-fit: contain;
}

.pixel-image {
  image-rendering: pixelated;
  image-rendering: crisp-edges;
}

.empty-state {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 12px;
  color: var(--muted);
  font-size: 0.75rem;
}

.empty-icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid var(--line);
  border-radius: 50%;
  font-size: 1.2rem;
  font-weight: 300;
}

.pixel-placeholder {
  display: grid;
  width: 48px;
  height: 48px;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 3px;
}

.pixel-placeholder i {
  display: block;
  background: var(--line);
}

.pixel-placeholder i:nth-child(2),
.pixel-placeholder i:nth-child(5),
.pixel-placeholder i:nth-child(9) {
  background: var(--text);
}

.preview-footer {
  display: grid;
  margin-top: 12px;
  grid-template-columns: 1fr 1fr;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}

.footer-stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 11px 12px;
  border-right: 1px solid var(--line);
}

.footer-stat:last-child {
  border-right: 0;
}

.footer-stat span {
  color: var(--muted);
  font-size: 0.68rem;
}

.footer-stat strong {
  color: var(--text);
  font-size: 0.75rem;
  font-weight: 500;
}

.site-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: auto;
  padding-top: 44px;
  color: var(--muted);
  font-size: 0.72rem;
}

.site-footer a {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--text);
  text-decoration: none;
}

.site-footer a:hover {
  opacity: 0.7;
}

.site-footer img {
  width: 19px;
  height: 19px;
  object-fit: contain;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  to {
    opacity: 0.4;
  }
}

@media (max-width: 850px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .controls-panel {
    min-height: 0;
  }

  .action-area {
    margin-top: 28px;
  }
}

@media (max-width: 560px) {
  .page-content {
    width: min(100% - 24px, 480px);
    padding-top: 32px;
  }

  .hero {
    padding: 37px 24px 0;
  }

  .hero h1 {
    font-size: clamp(2.35rem, 12vw, 3.7rem);
  }

  .workspace {
    margin-top: 40px;
  }

  .controls-panel,
  .preview-panel {
    padding: 14px;
  }

  .preview-grid {
    grid-template-columns: 1fr;
  }

  .image-stage {
    min-height: 260px;
  }

  .site-footer {
    padding-top: 32px;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
</style>

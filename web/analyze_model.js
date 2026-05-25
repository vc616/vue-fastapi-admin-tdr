const fs = require('fs')
const buffer = fs.readFileSync('public/models/pump.glb')
const jsonChunkLength = buffer.readUInt32LE(12)
const jsonBuffer = buffer.slice(16, 16 + jsonChunkLength)
const jsonStr = jsonBuffer.toString('utf8')
const gltf = JSON.parse(jsonStr)

let globalMin = [Infinity, Infinity, Infinity]
let globalMax = [-Infinity, -Infinity, -Infinity]

gltf.accessors.forEach((acc) => {
  if (acc.min && acc.max && acc.type === 'VEC3') {
    globalMin[0] = Math.min(globalMin[0], acc.min[0])
    globalMin[1] = Math.min(globalMin[1], acc.min[1])
    globalMin[2] = Math.min(globalMin[2], acc.min[2])
    globalMax[0] = Math.max(globalMax[0], acc.max[0])
    globalMax[1] = Math.max(globalMax[1], acc.max[1])
    globalMax[2] = Math.max(globalMax[2], acc.max[2])
  }
})

const center = [
  (globalMin[0] + globalMax[0]) / 2,
  (globalMin[1] + globalMax[1]) / 2,
  (globalMin[2] + globalMax[2]) / 2
]

const result = `Global Bounding Box:
  Min: ${globalMin.map(v => v.toFixed(3))}
  Max: ${globalMax.map(v => v.toFixed(3))}
  Center (旋转中心): ${center.map(v => v.toFixed(3))}
  Size: ${globalMax.map((v, i) => (v - globalMin[i]).toFixed(3))}`

fs.writeFileSync('analysis_result.txt', result)
console.log(result)
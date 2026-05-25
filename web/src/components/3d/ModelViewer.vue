<template>
  <div class="model-viewer">
    <TresCanvas
      v-model:clear-color="clearColor"
      :antialias="true"
      :alpha="true"
    >
      <TresPerspectiveCamera :position="cameraPosition" />
      <!--
        OrbitControls 旋转控制参数：
        enable-damping: 是否启用阻尼（惯性）
        damping-factor: 阻尼系数，越大停止越慢
        target: 旋转轴心点 [x, y, z]
        min-polar-angle: 最小俯仰角（弧度），控制上下旋转范围
        max-polar-angle: 最大俯仰角（弧度）
      -->
      <OrbitControls
        enable-damping
        :damping-factor="0.05"
        :target="target"
        :min-polar-angle="0.8"
        :max-polar-angle="1.4"
      />
      <!--
        灯光参数：
        AmbientLight: 环境光，intensity 数值越大整体越亮
        DirectionalLight: 方向光，position 是光源位置，intensity 是亮度
      -->
      <TresAmbientLight :intensity="0.5" />
      <TresDirectionalLight :position="[10, 10, 10]" :intensity="3" />
      <TresDirectionalLight :position="[-5, 5, -5]" :intensity="0.8" />
      <!-- 模型容器，自动居中后应用旋转 -->
      <TresGroup :position="modelOffset" :rotation="finalRotation">
        <Suspense v-if="modelPath">
          <GLTFModel :path="modelPath" />
        </Suspense>
      </TresGroup>
      <TresMesh v-if="!modelPath">
        <TresBoxGeometry :args="[1, 1, 1]" />
        <TresMeshStandardMaterial color="#18a058" />
      </TresMesh>
    </TresCanvas>
    <div class="controls-hint">鼠标左键旋转（仅Y轴） · 滚轮缩放 · 右键平移</div>
    <div v-if="!modelPath" class="no-model-hint">请将模型文件放入 public/models/ 目录</div>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue'
import { TresCanvas } from '@tresjs/core'
import { GLTFModel, OrbitControls, useGLTF } from '@tresjs/cientos'
import * as THREE from 'three'

const props = defineProps({
  modelPath: { type: String, default: '' }, // 模型文件路径，如 '/models/pump.glb'
  cameraPosition: { type: Array, default: () => [0, 2, 5] }, // 相机位置 [x, y, z]
  target: { type: Array, default: () => [0, 0, 0] }, // 旋转轴心 [x, y, z]
  modelRotation: { type: Array, default: () => [0, 0, 0] }, // 模型初始旋转 [rx, ry, rz]，单位：弧度
  autoRotate: { type: Boolean, default: false }, // 是否自动旋转
  autoRotateSpeed: { type: Number, default: 1 } // 自动旋转速度
})

const clearColor = ref('#1a1a2e')

// 模型中心偏移量，自动计算
const modelOffset = ref([0, 0, 0])

// 累积自动旋转角度
const autoRotateY = ref(0)

// 加载模型并计算中心
watchEffect(async () => {
  if (props.modelPath) {
    try {
      const { scene } = await useGLTF(props.modelPath)
      const box = new THREE.Box3().setFromObject(scene)
      const center = box.getCenter(new THREE.Vector3())
      modelOffset.value = [-center.x, -center.y, -center.z]
    } catch (e) {
      console.error('模型加载失败', e)
    }
  }
})

// 合并初始旋转和自动旋转
const finalRotation = computed(() => [
  props.modelRotation[0],
  props.modelRotation[1] + (props.autoRotate ? autoRotateY.value : 0),
  props.modelRotation[2]
])
</script>

<style scoped>
.model-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.controls-hint {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  padding: 6px 16px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 12px;
  border-radius: 20px;
  pointer-events: none;
}

.no-model-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 12px 24px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 14px;
  border-radius: 8px;
  pointer-events: none;
}
</style>
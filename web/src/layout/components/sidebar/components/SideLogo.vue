<template>
  <router-link class="side-logo" to="/">
    <img :src="logoUrl" class="logo-img" :class="{ collapsed: appStore.collapsed }" />
    <h2
      v-show="!appStore.collapsed"
      class="logo-title"
    >
      {{ title }}
    </h2>
  </router-link>
</template>

<script setup>
import { useAppStore } from '@/store'
import logoUrl from '@/assets/svg/logo.png'

const title = import.meta.env.VITE_TITLE

const appStore = useAppStore()
</script>

<style scoped>
.side-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: auto;
  padding: 16px 8px;
  text-decoration: none;
}

.logo-img {
  width: 150px;
  height: 40px;
  object-fit: contain;
  transition: width 0.3s, height 0.3s;
}

.logo-img.collapsed {
  width: 36px;
  height: 36px;
}

.logo-title {
  margin: 6px 0 0 0;
  max-width: 150px;
  flex-shrink: 0;
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color, #18a058);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

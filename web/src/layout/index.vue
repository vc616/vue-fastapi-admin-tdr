<template>
  <n-layout has-sider wh-full :class="isDark ? 'dark-layout' : 'light-layout'">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :native-scrollbar="false"
      :collapsed="appStore.collapsed"
      :class="isDark ? 'sider-dark' : 'sider-light'"
    >
      <SideBar />
    </n-layout-sider>

    <article flex-col flex-1 overflow-hidden>
      <header
        class="flex items-center border-b px-15"
        :class="isDark ? 'bg-dark-1 border-dark-3' : 'bg-white border-gray-200'"
        :style="`height: ${header.height}px`"
      >
        <AppHeader />
      </header>
      <section v-if="tags.visible" hidden border-b sm:block :class="isDark ? 'bg-dark-1 border-dark-3' : 'bg-white border-gray-200'">
        <AppTags :style="{ height: `${tags.height}px` }" />
      </section>
      <section flex-1 overflow-hidden :class="isDark ? 'bg-dark' : 'bg-gray-50'">
        <AppMain />
      </section>
    </article>
  </n-layout>
</template>

<script setup>
import AppHeader from './components/header/index.vue'
import SideBar from './components/sidebar/index.vue'
import AppMain from './components/AppMain.vue'
import AppTags from './components/tags/index.vue'
import { useAppStore } from '@/store'
import { header, tags } from '~/settings'
import { useDark } from '@vueuse/core'

const appStore = useAppStore()
const isDark = useDark()

// 移动端适配
import { useBreakpoints } from '@vueuse/core'

const breakpointsEnum = {
  xl: 1600,
  lg: 1199,
  md: 991,
  sm: 666,
  xs: 575,
}
const breakpoints = reactive(useBreakpoints(breakpointsEnum))
const isMobile = breakpoints.smaller('sm')
const isPad = breakpoints.between('sm', 'md')
const isPC = breakpoints.greater('md')
watchEffect(() => {
  if (isMobile.value) {
    appStore.setCollapsed(true)
    appStore.setFullScreen(false)
  }

  if (isPad.value) {
    appStore.setCollapsed(true)
    appStore.setFullScreen(false)
  }

  if (isPC.value) {
    appStore.setCollapsed(false)
    appStore.setFullScreen(true)
  }
})
</script>

<style scoped>
.light-layout {
  background: #F8FAFC;
}
.dark-layout {
  background: #020617;
}
.sider-light {
  background: #ffffff;
  border-color: #e5e7eb;
}
.sider-dark {
  background: #0F172A;
  border-color: #334155;
}
</style>

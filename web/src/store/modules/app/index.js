import { defineStore } from 'pinia'
import { nextTick } from 'vue'
import { useDark } from '@vueuse/core'
import { lStorage } from '@/utils'
import i18n from '~/i18n'

const currentLocale = lStorage.get('locale')
const { locale } = i18n.global

const isDark = useDark()
export const useAppStore = defineStore('app', {
  state() {
    return {
      reloadFlag: true,
      collapsed: false,
      fullScreen: true,
      /** keepAlive路由的key，重新赋值可重置keepAlive */
      aliveKeys: {},
      isDark,
      locale: currentLocale || 'en',
    }
  },
  actions: {
    async reloadPage() {
      $loadingBar.start()
      this.reloadFlag = false
      const key = this.aliveKeys['__reload__'] || 0
      this.aliveKeys['__reload__'] = key + 1
      await nextTick()
      await nextTick()
      this.reloadFlag = true

      setTimeout(() => {
        document.documentElement.scrollTo({ left: 0, top: 0 })
        $loadingBar.finish()
      }, 100)
    },
    switchCollapsed() {
      this.collapsed = !this.collapsed
    },
    setCollapsed(collapsed) {
      this.collapsed = collapsed
    },
    setFullScreen(fullScreen) {
      this.fullScreen = fullScreen
    },
    setAliveKeys(key, val) {
      this.aliveKeys[key] = val
    },
    /** 设置暗黑模式 */
    setDark(isDark) {
      this.isDark = isDark
    },
    /** 切换/关闭 暗黑模式 */
    toggleDark() {
      this.isDark = !this.isDark
    },
    setLocale(newLocale) {
      this.locale = newLocale
      locale.value = newLocale
      lStorage.set('locale', newLocale)
    },
  },
})

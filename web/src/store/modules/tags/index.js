import { defineStore } from 'pinia'
import { activeTag, tags, WITHOUT_TAG_PATHS } from './helpers'
import { router } from '@/router'
import { lStorage } from '@/utils'

export const useTagsStore = defineStore('tag', {
  state() {
    return {
      tags: tags || [],
      activeTag: activeTag || '',
    }
  },
  getters: {
    activeIndex() {
      return this.tags.findIndex((item) => item.path === this.activeTag)
    },
  },
  actions: {
    setActiveTag(path) {
      this.activeTag = path
      lStorage.set('activeTag', path)
    },
    setTags(tags) {
      this.tags = tags
      lStorage.set('tags', tags)
    },
    addTag(tag = {}) {
      if (WITHOUT_TAG_PATHS.includes(tag.path)) return
      const existsIndex = this.tags.findIndex((item) => item.path === tag.path)
      if (existsIndex !== -1) {
        // 已存在：先移除旧的，再添加到末尾
        const newTags = this.tags.filter((item) => item.path !== tag.path)
        this.setTags([...newTags, tag])
      } else {
        this.setTags([...this.tags, tag])
      }
      this.setActiveTag(tag.path)
    },
    removeTag(path) {
      if (path === this.activeTag) {
        if (this.activeIndex > 0) {
          router.push(this.tags[this.activeIndex - 1].path)
        } else {
          router.push(this.tags[this.activeIndex + 1].path)
        }
      }
      this.setTags(this.tags.filter((tag) => tag.path !== path))
    },
    removeOther(curPath = this.activeTag) {
      this.setTags(this.tags.filter((tag) => tag.path === curPath))
      if (curPath !== this.activeTag) {
        router.push(this.tags[this.tags.length - 1].path)
      }
    },
    removeLeft(curPath) {
      const curIndex = this.tags.findIndex((item) => item.path === curPath)
      const filterTags = this.tags.filter((item, index) => index >= curIndex)
      this.setTags(filterTags)
      if (!filterTags.find((item) => item.path === this.activeTag)) {
        router.push(filterTags[filterTags.length - 1].path)
      }
    },
    removeRight(curPath) {
      const curIndex = this.tags.findIndex((item) => item.path === curPath)
      const filterTags = this.tags.filter((item, index) => index <= curIndex)
      this.setTags(filterTags)
      if (!filterTags.find((item) => item.path === this.activeTag)) {
        router.push(filterTags[filterTags.length - 1].path)
      }
    },
    resetTags() {
      this.setTags([])
      this.setActiveTag('')
    },
  },
})

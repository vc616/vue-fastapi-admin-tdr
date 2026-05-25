<template>
  <n-menu
    ref="menu"
    class="side-menu"
    accordion
    :indent="18"
    :collapsed-icon-size="22"
    :collapsed-width="64"
    :options="menuOptions"
    :value="activeKey"
    @update:value="handleMenuSelect"
  />
</template>

<script setup>
import { usePermissionStore, useAppStore } from '@/store'
import { renderCustomIcon, renderIcon, isExternal } from '@/utils'

const router = useRouter()
const curRoute = useRoute()
const permissionStore = usePermissionStore()
const appStore = useAppStore()

const activeKey = computed(() => curRoute.meta?.activeMenu || curRoute.path)

const menuOptions = computed(() => {
  return permissionStore.menus.map((item) => getMenuItem(item)).sort((a, b) => a.order - b.order)
})

const menu = ref(null)
watch(curRoute, async () => {
  await nextTick()
  menu.value?.showOption()
})

function resolvePath(basePath, path) {
  if (isExternal(path)) return path
  return (
    '/' +
    [basePath, path]
      .filter((path) => !!path && path !== '/')
      .map((path) => path.replace(/(^\/)|(\/$)/g, ''))
      .join('/')
  )
}

function getMenuItem(route, basePath = '') {
  const itemPath = resolvePath(basePath, route.path)
  let menuItem = {
    label: (route.meta && route.meta.title) || route.name,
    key: itemPath,
    path: itemPath,
    icon: getIcon(route.meta),
    order: route.meta?.order || 0,
  }

  const visibleChildren = route.children
    ? route.children.filter((item) => item.name && !item.isHidden)
    : []

  if (!visibleChildren.length) return menuItem

  // 如果是目录类型(menu_type=catalog)，始终显示子菜单不扁平化
  const isCatalog = route.menuType === 'catalog' || route.isCatalog

  if (visibleChildren.length === 1 && !isCatalog) {
    // 单个子路由处理（只有非catalog才扁平化）
    const singleRoute = visibleChildren[0]
    const childPath = resolvePath(menuItem.path, singleRoute.path)
    menuItem = {
      ...menuItem,
      label: singleRoute.meta?.title || singleRoute.name,
      key: childPath,
      path: childPath,
      icon: getIcon(singleRoute.meta),
    }
    const visibleItems = singleRoute.children
      ? singleRoute.children.filter((item) => item.name && !item.isHidden)
      : []

    if (visibleItems.length === 1) {
      menuItem = getMenuItem(visibleItems[0], menuItem.path)
    } else if (visibleItems.length > 1) {
      menuItem.children = visibleItems
        .map((item) => getMenuItem(item, menuItem.path))
        .sort((a, b) => a.order - b.order)
    }
  } else {
    menuItem.children = visibleChildren
      .map((item) => getMenuItem(item, menuItem.path))
      .sort((a, b) => a.order - b.order)
  }
  return menuItem
}

function getIcon(meta) {
  if (meta?.customIcon) return renderCustomIcon(meta.customIcon, { size: 18 })
  if (meta?.icon) return renderIcon(meta.icon, { size: 18 })
  return null
}

function handleMenuSelect(key, item) {
  if (isExternal(item.path)) {
    window.open(item.path)
  } else {
    // 如果是目录类型且有 redirect，优先跳转到 redirect
    const targetPath = item.redirect || item.path
    if (targetPath === curRoute.path) {
      appStore.reloadPage()
    } else {
      router.push(targetPath)
    }
  }
}
</script>

<style lang="scss">
.side-menu:not(.n-menu--collapsed) {
  .n-menu-item-content {
    &::before {
      left: 5px;
      right: 5px;
    }
    &.n-menu-item-content--selected,
    &:hover {
      &::before {
        border-left: 4px solid var(--primary-color);
      }
    }
  }
}
</style>

import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import { setupRouterGuard } from './guard'
import { basicRoutes, EMPTY_ROUTE, NOT_FOUND_ROUTE } from './routes'
import { getToken, isNullOrWhitespace } from '@/utils'
import { useUserStore, usePermissionStore } from '@/store'

const isHash = import.meta.env.VITE_USE_HASH === 'true'
export const router = createRouter({
  history: isHash ? createWebHashHistory('/') : createWebHistory('/'),
  routes: basicRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

export async function setupRouter(app) {
  await addDynamicRoutes()
  setupRouterGuard(router)
  app.use(router)
}

export async function resetRouter() {
  const basicRouteNames = getRouteNames(basicRoutes)
  router.getRoutes().forEach((route) => {
    const name = route.name
    if (!basicRouteNames.includes(name)) {
      router.removeRoute(name)
    }
  })
}

/**
 * Flatten intermediate catalog routes for Vue Router.
 * Vue Router 4 cannot properly render when there are two consecutive
 * routes with component: null (catalog → catalog → menu). This
 * creates flat top-level routes with absolute paths.
 *
 * The original route tree (used by the sidebar) is NOT modified.
 */
function flattenNestedCatalogs(routes) {
  const result = []
  for (const route of routes) {
    if (route.isCatalog && !route.component && route.children?.length) {
      // 将 catalog 的子路由提取为顶级路由
      const flatRoutes = extractFlatRoutes(route.children, route.path)
      result.push(...flatRoutes)
    } else {
      result.push(route)
    }
  }
  return result
}

function extractFlatRoutes(children, parentPath) {
  const result = []
  for (const child of children) {
    if (child.isCatalog && !child.component && child.children?.length) {
      // 递归处理嵌套 catalog
      const childPath = parentPath ? `${parentPath}/${child.path}` : child.path
      result.push(...extractFlatRoutes(child.children, childPath))
    } else {
      // 非 catalog 节点：构建完整路径
      const fullPath = parentPath
        ? (child.path.startsWith('/') ? child.path : `${parentPath}/${child.path}`)
        : (child.path.startsWith('/') ? child.path : `/${child.path}`)
      
      // 使用完整路径作为路由名称，确保唯一性
      const uniqueName = fullPath.replace(/\//g, '_').replace(/^_/, '')
      
      // 如果有子路由（默认子路由包含实际组件），保留嵌套结构并确保子路由名称唯一
      if (child.children?.length) {
        const uniqueChildren = child.children.map(gc => {
          const childUniqueName = gc.path
            ? `${uniqueName}_${gc.path.replace(/\//g, '_')}`
            : `${uniqueName}_default`
          return { ...gc, name: childUniqueName }
        })
        result.push({
          ...child,
          path: fullPath,
          name: uniqueName,
          children: uniqueChildren,
        })
      } else {
        result.push({ ...child, path: fullPath, name: uniqueName })
      }
    }
  }
  return result
}

export async function addDynamicRoutes() {
  const token = getToken()

  // 没有token情况
  if (isNullOrWhitespace(token)) {
    router.addRoute(EMPTY_ROUTE)
    return
  }
  // 有token的情况
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()
  !userStore.userId && (await userStore.getUserInfo())
  try {
    const accessRoutes = await permissionStore.generateRoutes()
    await permissionStore.getAccessApis()
    const flatAccessRoutes = flattenNestedCatalogs(accessRoutes)

    flatAccessRoutes.forEach((route) => {
      console.log(`[addRoute] Adding: ${route.name} (${route.path}), children: ${route.children?.map(c => c.name).join(', ') || 'none'}`)
      !router.hasRoute(route.name) && router.addRoute(route)
    })
    router.hasRoute(EMPTY_ROUTE.name) && router.removeRoute(EMPTY_ROUTE.name)
    router.addRoute(NOT_FOUND_ROUTE)
  } catch (error) {
    console.error('error', error)
    const userStore = useUserStore()
    await userStore.logout()
  }
}

export function getRouteNames(routes) {
  return routes.map((route) => getRouteName(route)).flat(1)
}

function getRouteName(route) {
  const names = [route.name]
  if (route.children && route.children.length) {
    names.push(...route.children.map((item) => getRouteName(item)).flat(1))
  }
  return names
}

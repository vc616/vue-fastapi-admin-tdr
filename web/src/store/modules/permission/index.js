import { defineStore } from 'pinia'
import { defineAsyncComponent } from 'vue'
import { basicRoutes, vueModules } from '@/router/routes'
import api from '@/api'

const Layout = () => import('@/layout/index.vue')

// * 后端路由相关函数
// 根据后端传来数据构建出前端路由

function buildRoutes(routes = [], parentPath = '') {
  return routes.map((e) => {
    const isCatalog = e.menu_type === 'catalog'

    // 绝对路径直接用，相对路径拼接父路径
    const fullPath = e.path.startsWith('/')
      ? e.path
      : (parentPath ? `${parentPath}/${e.path}` : `/${e.path}`)

    // 如果是目录类型(menu_type=catalog)，component 为 null；否则使用 Layout
    const route = {
      name: e.name,
      path: e.path,
      fullPath,
      component: isCatalog ? null : Layout,
      isHidden: e.is_hidden,
      redirect: e.redirect,
      menuType: e.menu_type,
      isCatalog,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单，递归处理
      route.children = buildRoutes(e.children, fullPath)
    } else if (e.component && e.component !== 'Layout') {
      // 是叶子节点且有实际组件，加载组件
      const componentPath = `/src/views${e.component}/index.vue`
      const componentLoader = vueModules[componentPath]
      const component = componentLoader ? defineAsyncComponent(componentLoader) : null
      route.children.push({
        name: `${e.name}Default`,
        path: '',
        component: component,
        isHidden: true,
        meta: {
          title: e.name,
          icon: e.icon,
          order: e.order,
          keepAlive: e.keepalive,
        },
      })
    }

    return route
  })
}

export const usePermissionStore = defineStore('permission', {
  state() {
    return {
      accessRoutes: [],
      accessApis: [],
    }
  },
  getters: {
    routes() {
      return basicRoutes.concat(this.accessRoutes)
    },
    menus() {
      return this.routes.filter((route) => route.name && !route.isHidden)
    },
    apis() {
      return this.accessApis
    },
  },
  actions: {
    async generateRoutes() {
      const res = await api.getUserMenu() // 调用接口获取后端传来的菜单路由
      this.accessRoutes = buildRoutes(res.data) // 处理成前端路由格式
      return this.accessRoutes
    },
    async getAccessApis() {
      const res = await api.getUserApi()
      this.accessApis = res.data
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})

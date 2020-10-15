import Vue from 'vue'
import VueRouter, { RouteConfig, Route } from 'vue-router'

import store from '@/store'
import http from '@/api'
import { PROXY_OPERATE, CLOUD_VIEW, CLOUD_CREATE, CLOUD_EDIT } from '@/router/action-map'
import axios from 'axios'

Vue.use(VueRouter)
// 获取modules下的所有模块
const routeFiles = require.context('./modules', true, /\.ts$/)
const pageRoute = routeFiles.keys().reduce<RouteConfig[]>((route, modulePath) => {
  const value = routeFiles(modulePath)
  route.push(value.default)
  return route
}, [])

const MainEntry = () => import(/* webpackChunkName: 'entry' */'@/views/index.vue')
const NotFound = () => import(/* webpackChunkName: 'none' */'@/views/404.vue')

const routes = [
  {
    path: '/',
    component: MainEntry,
    children: [
      {
        path: '',
        redirect: {
          name: 'agentStatus'
        }
      },
      ...pageRoute.flat()
    ]
  },
  // 404
  {
    path: '*',
    name: '404',
    component: NotFound
  }
]

const router = new VueRouter({
  mode: 'hash',
  routes
})

const cancelRequest = async () => {
  const allRequest = http.queue.get() as any[]
  const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange)
  await http.cancel(requestQueue.map(request => request.requestId))
}

router.beforeEach(async (to, from, next) => {
  const { customContent, title, navId, authority } = to.meta
  // 设置自定义导航内容
  store.commit('setCustomNavContent', customContent)
  // 设置标题
  store.commit('setNavTitle', to.params.title || window.i18n.t(title))
  // 更新当前导航name
  store.commit('updateCurrentNavName', navId)
  // 更新子导航name
  store.commit('updateSubMenuName', to.name)
  // 重置业务权限
  store.commit('updateBizAction', authority ? authority.page : 'agent_view')
  await cancelRequest()
  next()
})

// 校验普通界面权限
const validateBizAuth = async (to: Route) => {
  const { authority } = to.meta
  if (window.PROJECT_CONFIG.USE_IAM === 'True' && authority?.page) {
    store.commit('setNmMainLoading', true)
    const list = await store.dispatch('getBkBizPermission', { action: authority.page, updateBiz: true })
    // 设置当前路由的界面权限
    store.commit('updatePagePermission', !axios.isCancel(list) ? !!list.length : true)
  }
  store.commit('setNmMainLoading', false)
}
// 校验云区域界面
const validateCloudAuth = async (to: Route) => {
  const { authority } = to.meta
  // const authorityMap = store.getters['cloud/authority']
  const permissionSwitch = window.PROJECT_CONFIG.USE_IAM === 'True'
  if (permissionSwitch) {
    // 获取权限
    const promiseList = [
      store.dispatch('cloud/getCloudPermission'),
      store.dispatch('getBkBizPermission', { action: 'proxy_operate', updateBiz: true })
    ]
    const [cloudAction, proxyOperateList] = await Promise.all(promiseList)
    if (!axios.isCancel(cloudAction) && !axios.isCancel(proxyOperateList)) {
      store.commit('cloud/setAuthority', {
        ...cloudAction,
        proxy_operate: proxyOperateList
      })
    }
    // 设置界面显示
    let isAuth = true
    if (to?.name === 'addCloudManager' && !axios.isCancel(cloudAction)) {
      const { edit_action: editAction, create_action: createAction } = cloudAction
      if (to.params?.type === 'edit') {
        store.commit('updateBizAction', CLOUD_EDIT)
        isAuth = editAction?.includes(Number(to.params.id))
      } else {
        store.commit('updateBizAction', CLOUD_CREATE)
        isAuth = !!createAction
      }
    } else if (authority?.page === PROXY_OPERATE && !axios.isCancel(proxyOperateList)) {
      isAuth = !!proxyOperateList.length
    } else if (authority?.page === CLOUD_VIEW && !axios.isCancel(cloudAction)) {
      const { view_action: viewAction } = cloudAction
      isAuth = viewAction?.includes(Number(to.params.id))
    }
    // 设置当前路由的界面权限
    store.commit('updatePagePermission', isAuth)
  } else {
    // 设置默认值
    store.commit('cloud/setAuthority', {
      edit_action: [],
      delete_action: [],
      create_action: true,
      view_action: [],
      proxy_operate: []
    })
  }
}
router.afterEach(async (to) => {
  // 重置界面权限
  store.commit('updatePagePermission', true)
  const { navId } = to.meta
  if (navId === 'cloudManager') {
    await validateCloudAuth(to)
  } else {
    await validateBizAuth(to)
  }
})

export default router

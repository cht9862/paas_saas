/* eslint-disable max-len */
import { RouteConfig, Route } from 'vue-router'
import store from '@/store'
const GseConfig = () => import(/* webpackChunkName: 'GseConfig' */'@/views/global-config/gse-config.vue')
const AccessPoint = () => import(/* webpackChunkName: 'AccessPoint' */'@/views/global-config/set-access-point/access-point.vue')
const TaskConfig = () => import(/* webpackChunkName: 'TaskConfig' */'@/views/global-config/task-config.vue')

export default [
  {
    path: 'global-config',
    name: 'globalConfig',
    redirect: {
      name: 'GseConfig'
    }
  },
  {
    path: 'global-config/gse-config',
    name: 'gseConfig',
    component: GseConfig,
    meta: {
      navId: 'globalConfig',
      title: 'GSE环境管理'
    }
  },
  {
    path: 'global-config/access-point/:pointId?',
    name: 'accessPoint',
    props: true,
    component: AccessPoint,
    meta: {
      navId: 'globalConfig',
      title: 'config',
      needBack: true
    },
    beforeEnter: (to: Route, from: Route, next: () => void) => {
      store.commit('config/resetDetail')
      store.commit('setNavTitle', !to.params.pointId ? window.i18n.t('新增接入点') : window.i18n.t('编辑接入点'))
      store.commit('setToggleDefaultContent', true)
      next()
    }
  },
  {
    path: 'global-config/task-config',
    name: 'taskConfig',
    component: TaskConfig,
    meta: {
      navId: 'globalConfig',
      title: '任务配置'
    }
  }
] as RouteConfig[]

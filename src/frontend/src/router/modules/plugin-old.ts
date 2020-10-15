import { RouteConfig } from 'vue-router'
import { PLUGIN_VIEW } from '@/router/action-map'
const PluginOld = () => import(/* webpackChunkName: 'PluginOld' */'@/views/plugin/plugin-old/index.vue')
export default [
  {
    path: 'plugin-manager',
    name: 'pluginManager',
    redirect: {
      name: 'pluginOld'
    }
  },
  /**
   * 1.3版本组件
   */
  {
    path: 'plugin-manager/plugin',
    name: 'pluginOld',
    component: PluginOld,
    meta: {
      navId: 'pluginManager',
      title: '插件管理',
      customContent: true,
      authority: {
        page: PLUGIN_VIEW
      }
    }
  }
] as RouteConfig[]

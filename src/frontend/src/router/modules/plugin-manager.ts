/* eslint-disable max-len */
import { RouteConfig } from 'vue-router'
const Plugin = () => import(/* webpackChunkName: 'Plugin' */'@/views/plugin/plugin.vue')
const pluginRule = () => import(/* webpackChunkName: 'PluginRule' */'@/views/plugin/plugin-rule/plugin-rule.vue')
const PluginPackage = () => import(/* webpackChunkName: 'PluginPackage' */'@/views/plugin/plugin-package/plugin-package.vue')
const AddRule = () => import(/* webpackChunkName: 'AddRule' */'@/views/plugin/plugin-rule/plugin-rule-add.vue')

export default [
  {
    path: 'plugin-manager/list',
    name: 'plugin',
    component: Plugin,
    meta: {
      navId: 'pluginManagerNew',
      title: '节点列表'
    }
  },
  {
    path: 'plugin-manager/rule',
    name: 'pluginRule',
    component: pluginRule,
    meta: {
      navId: 'pluginManagerNew',
      title: '部署策略'
    }
  },
  {
    path: 'plugin-manager/rule/add',
    name: 'addRule',
    component: AddRule,
    meta: {
      navId: 'pluginManagerNew',
      parentId: 'pluginRule',
      title: '新建策略',
      needBack: true
    }
  },
  {
    path: 'plugin-manager/package',
    name: 'pluginPackage',
    component: PluginPackage,
    meta: {
      navId: 'pluginManagerNew',
      title: '插件包'
    }
  }
] as RouteConfig[]

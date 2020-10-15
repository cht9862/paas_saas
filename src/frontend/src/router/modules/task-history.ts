import store from '@/store'
import { Route } from 'vue-router'
import { TASK_HISTORY_VIEW } from '@/router/action-map'
const TaskHistory = () => import(/* webpackChunkName: 'TaskHistory' */'@/views/task/task-history.vue')
const TaskDetail = () => import(/* webpackChunkName: 'TaskDetail' */'@/views/task/task-detail.vue')
const TaskLog = () => import(/* webpackChunkName: 'TaskLog' */'@/views/task/task-log.vue')

export default [
  {
    path: 'task-history',
    name: 'taskHistory',
    component: TaskHistory,
    meta: {
      navId: 'taskHistory',
      title: '任务历史',
      authority: {
        page: TASK_HISTORY_VIEW
      }
    }
  },
  {
    path: 'task-history/detail/:taskId',
    name: 'taskDetail',
    props: true,
    component: TaskDetail,
    meta: {
      navId: 'taskHistory',
      title: '任务详情',
      needBack: true,
      customContent: true
    },
    beforeEnter: (to: Route, from: Route, next: () => void) => {
      store.commit('task/setRouterParent', from.name)
      store.commit('setToggleDefaultContent', true)
      next()
    }
  },
  {
    path: 'task-history/:taskId/log/:instanceId',
    name: 'taskLog',
    props: true,
    component: TaskLog,
    meta: {
      navId: 'taskHistory',
      title: '执行日志',
      needBack: true,
      customContent: true
    },
    beforeEnter: (to: Route, from: Route, next: () => void) => {
      store.commit('task/setRouterParent', from.name)
      next()
    }
  }
]

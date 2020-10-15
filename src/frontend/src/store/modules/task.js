import {
  listJob, // 任务列表
  retrieveJob, // 任务详情 & 主机列表
  getJobLog, // 查询日志
  retryJob, // 重试
  retryNode, // 原子重试
  revokeJob, // 终止
  collectJobLog, // 日志上报
  getJobCommands // 获取手动安装命令
} from '@/api/modules/job'
import { getFilterCondition } from '@/api/modules/meta'
import { transformDataKey, sort } from '@/common/util'

export default {
  namespaced: true,
  state: {
    routetParent: ''
  },
  getters: {
    routetParent: state => state.routetParent
  },
  mutations: {
    setRouterParent(state, name) {
      state.routetParent = name
    }
  },
  actions: {
    // 历史任务列表
    async requestHistoryTaskList({}, params) {
      const data = await listJob(params).catch(() => ({
        total: 0,
        list: []
      }))
      data.list.forEach((row) => {
        row.status = row.status.toLowerCase()
      })
      return transformDataKey(data)
    },
    // 单个任务详情, 包含主机列表
    async requestHistoryTaskDetail({}, { id, params }) {
      const res = await retrieveJob(id, params).catch(() => {})
      if (res) {
        res.list.forEach((row) => {
          if (row.bk_cloud_id === 0 || row.bk_cloud_name === 'default area') {
            row.bk_cloud_name = window.i18n.t('直连区域')
          }
          row.status = row.status.toLowerCase()
        })
      }
      return res ? transformDataKey(res) : false
    },
    // 主机日志详情
    async requestHistoryHostLog({}, { job_id, query }) {
      const data = await getJobLog(job_id, query).catch(() => {})
      if (data) {
        data.forEach((row) => {
          row.status = row.status.toLowerCase()
        })
      }
      return data
    },
    // 任务重试
    async requestTaskRetry({}, { jobId, params }) {
      const data = await retryJob(jobId, params, { needRes: true }).catch(() => ({}))
      return data
    },
    // 任务终止
    async requestTaskStop({}, { jobId, params }) {
      const res = await revokeJob(jobId, params, { needRes: true }).catch(() => ({}))
      return res
    },
    // 原子重试
    async requestNodeRetry({}, { jobId, params }) {
      const res = await retryNode(jobId, params, { needRes: true }).catch(() => ({}))
      return res
    },
    /**
     * 获取筛选条件
     * @param {*} param0
     * @param {*} params
     */
    async getFilterCondition() {
      const data = await getFilterCondition({
        category: 'job'
      }).then((res) => {
        const userName = window.PROJECT_CONFIG ? window.PROJECT_CONFIG.USERNAME || '' : ''
        const list = res.map((item) => {
          item.multiable = true
          if (item.id === 'job_type' && Array.isArray(item.children)) {
            const sortAgent = []
            const sortProxy = []
            const sortPlugin = []
            const sortOther = []
            item.children.forEach((item) => {
              if (/agent/ig.test(item.id)) {
                sortAgent.push(item)
              } else if (/proxy/ig.test(item.id)) {
                sortProxy.push(item)
              } else if (/plug/ig.test(item.id)) {
                sortPlugin.push(item)
              } else {
                sortOther.push(item)
              }
            })
            item.children = sort(sortAgent, 'name').concat(
              sort(sortProxy, 'name'),
              sort(sortPlugin, 'name'),
              sort(sortOther, 'name')
            )
          }
          if (userName && item.id === 'created_by' && item.children && item.children.length) {
            item.children.forEach((item) => {
              if (item.id === userName) {
                item.name = window.i18n.t('我')
              }
            })
          }
          if (item.children && item.children.length) {
            item.children = item.children.map((child) => {
              child.checked = false
              return child
            })
          }
          return item
        })
        return list
      })
        .catch(() => [])
      return data
    },
    /**
     * 日志上报
     */
    async requestReportLog({}, { job_id, params }) {
      const data = await collectJobLog(job_id, params).catch(() => {})
      return data
    },
    async requestCommands({}, { jobId, params }) {
      const data = await getJobCommands(jobId, params).catch(() => {})
      return transformDataKey(data)
    }
  }
}

import { listHost, listProcess, listPackage, operatePlugin } from '@/api/modules/plugin'
import { getFilterCondition } from '@/api/modules/meta'
import { sort } from '@/common/util'

const state = {}
const getters = {}
const mutations = {}
const actions = {
  /**
   * 获取主机列表
   * @param {*} param0
   * @param {*} params
   */
  async getHostList({}, params) {
    const data = await listHost(params).catch(() => ({
      total: 0,
      list: []
    }))
    data.list = data.list.map((item) => {
      item.status = item.status ? item.status.toLowerCase() : 'unknown'
      item.version = item.version ? item.version : '--'
      item.job_result = item.job_result ? item.job_result : {}
      item.topology = item.topology && item.topology.length ? item.topology : []
      return item
    })
    return data
  },
  /**
   * 获取筛选条件
   * @param {*} param0
   * @param {*} params
   */
  async getFilterCondition() {
    let data = await getFilterCondition({
      category: 'plugin'
    }).catch(() => [])
    data = data.map((item) => {
      if (item.children && item.children.length) {
        item.multiable = true
        item.children = item.children.filter(child => (`${child.id}`) && (`${child.name}`)).map((child) => {
          child.checked = false
          child.name = `${child.name}`
          return child
        })
      }
      if (item.id === 'bk_cloud_id') {
        item.showSearch = true
        item.width = 180
        item.align = 'right'
        item.children = sort(item.children, 'name')
      }
      return item
    })
    return data
  },
  /**
   * 获取插件列表
   * @param {*} param0
   * @param {*} pk
   */
  async getProcessList({}, pk) {
    const data = await listProcess(pk).catch(() => [])
    return data
  },
  /**
   * 插件包列表
   * @param {*} param0
   * @param {*} params
   */
  async listPackage({}, params) {
    const data = await listPackage(params.pk, params.data).catch(() => [])
    return data
  },
  /**
   * 插件操作
   * @param {*} param0
   * @param {*} params
   */
  async operatePlugin({}, params) {
    const data = await operatePlugin(params).catch(() => false)
    return data
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}

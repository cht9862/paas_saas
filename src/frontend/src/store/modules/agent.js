import { listHost, removeHost } from '@/api/modules/host'
import { installJob, operateJob } from '@/api/modules/job'
import { listAp } from '@/api/modules/ap'
import { listCloud } from '@/api/modules/cloud'
import { getFilterCondition } from '@/api/modules/meta'
import { fetchPwd } from '@/api/modules/tjj'
import { sort } from '@/common/util'

export const SET_AP_LIST = 'setApList'
export const SET_CLOUD_LIST = 'setCloudList'
export const UPDATE_AP_URL = 'updateApUrl'

const state = {
  apList: [],
  cloudList: [],
  apUrl: ''
}
const getters = {
  apList: state => state.apList,
  cloudList: state => state.cloudList,
  apUrl: state => state.apUrl
}
const mutations = {
  [SET_CLOUD_LIST](state, data = []) {
    state.cloudList = data
  },
  [SET_AP_LIST](state, data = []) {
    state.apList = data
  },
  [UPDATE_AP_URL](state, apUrl = '') {
    state.apUrl = apUrl
  }
}
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
      const {
        bt_speed_limit: btSpeedLimit,
        peer_exchange_switch_for_agent: peerExchangeSwitchForAgent
      } = item.extra_data || {}
      item.status = item.status ? item.status.toLowerCase() : 'unknown'
      item.version = item.version ? item.version : '--'
      item.job_result = item.job_result ? item.job_result : {}
      item.topology = item.topology && item.topology.length ? item.topology : []
      item.bt_speed_limit = btSpeedLimit || ''
      item.peer_exchange_switch_for_agent = !!peerExchangeSwitchForAgent || false
      return item
    })
    return data
  },
  /**
   * 获取运行主机数量
   * @param {*} param0
   * @param {*} params
   */
  async getRunningHost({}, params) {
    const data = await listHost(params).catch(() => ({
      running_count: 0,
      no_permission_count: 0
    }))
    return data
  },
  /**
   * 获取主机IP信息
   * @param {*} param0
   * @param {*} params
   */
  async getHostIp({}, params) {
    const data = await listHost(params).catch(() => ({
      total: 0,
      list: []
    }))
    return data
  },
  /**
   * Agent相关安装
   */
  async installAgentJob({}, { params, config = {} }) {
    const data = await installJob(params, config).catch(() => false)
    return data
  },
  /**
   * 获取接入点
   * @param {*} param0
   * @param {*} params
   */
  async getApList({ commit }, autoSelect = true) {
    const data = await listAp().catch(() => [])
    // 编辑态且只有一个接入点时，不显示自动选择
    if (autoSelect || data.length > 1) {
      data.unshift({
        id: -1,
        name: window.i18n.t('自动选择')
      })
    }
    commit(SET_AP_LIST, data)
    return data
  },
  /**
   * 获取云区域列表
   * @param {*} param0
   * @param {*} params
   */
  async getCloudList({ commit }, params = {}) {
    // 权限中心模式 - 接口输出直连区域
    const isIam = window.PROJECT_CONFIG.USE_IAM === 'True'
    if (isIam) {
      Object.assign(params, { with_default_area: true })
    }
    let data = await listCloud(params).then(res => res.map(item => Object.assign(item, item.permissions)))
      .catch(() => [])
    // RUN_VER 非接口字段：ieod环境 添加 或 excel导入剔除直连区域
    if (isIam) {
      data.sort((a, b) => Number(b.view) - Number(a.view))
      if (params && params.RUN_VER === 'ieod') {
        data = data.filter(item => item.bk_cloud_id !== window.PROJECT_CONFIG.DEFAULT_CLOUD)
      }
    }
    if (!isIam && (!params || params.RUN_VER !== 'ieod')) {
      data.unshift({
        bk_cloud_id: window.PROJECT_CONFIG.DEFAULT_CLOUD,
        bk_cloud_name: window.i18n.t('直连区域')
      })
    }
    commit(SET_CLOUD_LIST, data)
    return data
  },
  /**
   * 获取筛选条件
   * @param {*} param0
   * @param {*} params
   */
  async getFilterCondition() {
    let data = await getFilterCondition({
      category: 'host'
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
   * 移除Host
   * @param {*} param0
   * @param {*} params
   */
  async removeHost({}, params) {
    const data = await removeHost(params).catch(() => false)
    return data
  },
  /**
   * 重启、卸载 主机
   * @param {*} param0
   * @param {*} params
   */
  async operateJob({}, params) {
    const data = await operateJob(params).catch(() => false)
    return data
  },
  /**
   * 主机是否可用铁将军
   * @param {*} param0
   * @param {*} params
   */
  async fetchPwd({}, params) {
    const data = await fetchPwd(params).catch(() => false)
    return data
  },
  setApUrl({ commit }, { id, urlType = 'package_outer_url' }) {
    let apUrl = ''
    if (!id && id !== 0) {
      commit(UPDATE_AP_URL)
      return
    }
    const filterAp = id === -1
      ? state.apList.filter(item => item.id !== -1)
      : state.apList.filter(item => item.id === id)
    if (filterAp.length) {
      apUrl = filterAp.map(item => item[urlType]).join(', ')
    }
    commit(UPDATE_AP_URL, apUrl)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}

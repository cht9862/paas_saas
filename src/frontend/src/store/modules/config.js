import Vue from 'vue'
import { transformDataKey } from '@/common/util'
import { apIsUsing, listAp, retrieveAp, createAp, updateAp, testAp, deleteAp, initPluginData } from '@/api/modules/ap'
import { retrieveGlobalSettings, jobSettings } from '@/api/modules/meta'
import { listApPermission } from '@/api/modules/permission'

export default {
  namespaced: true,
  state: {
    loading: true,
    detail: {}
  },
  getters: {
    loading: state => state.loading,
    detail: state => state.detail
  },
  mutations: {
    resetDetail(state) {
      state.detail = {
        name: '',
        region_id: '',
        city_id: '',
        zk_account: '',
        zk_password: '',
        zk_hosts: [
          { zk_ip: '', zk_port: '' }
        ],
        btfileserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        dataserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        taskserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        package_inner_url: '',
        package_outer_url: '',
        agent_config: {
          linux: {},
          windows: {}
        },
        description: ''
      }
    },
    updateDetail(state, detail) {
      // eslint-disable-next-line no-restricted-syntax
      for (const key in detail) {
        if (Object.prototype.hasOwnProperty.call(state.detail, key)) {
          state.detail[key] = detail[key]
        } else {
          Vue.set(state.detail, key, detail[key])
        }
      }
    },
    updataLoading(state, isLoading) {
      state.loading = isLoading
    }
  },
  actions: {
    // 获取接入点列表
    async requestAccessPointList() {
      const data = await listAp().then(res => res.map(item => Object.assign(item, item.permissions)))
        .catch(() => [])
      data.forEach((row, index) => {
        row.collapse = !index
        row.zk_hosts = row.zk_hosts || []
        row.BtfileServer = row.btfileserver || []
        row.DataServer = row.dataserver || []
        row.TaskServer = row.taskserver || []
      })
      return data
    },
    // 获取接入点是否被使用
    async requestAccessPointIsUsing() {
      const data = await apIsUsing().catch(() => {})
      return data
    },
    // 获取接入点详情
    async getGseDetail({ commit }, { pointId }) {
      commit('updataLoading', true)
      const data = await retrieveAp(pointId).catch(() => ({}))
      commit('updateDetail', data)
      commit('updataLoading', false)
      return data
    },
    // 创建接入点
    async requestCreatePoint({}, params) {
      const data = await createAp(params).catch(() => {})
      return data
    },
    // 修改接入点
    async requestEditPoint({}, { pointId, data }) {
      const result = await updateAp(pointId, data).catch(() => {})
      return result
    },
    // 删除接入点
    async requestDeletetPoint({}, { pointId }) {
      const data = await deleteAp(pointId, null, { needRes: true }).catch(() => {})
      return data
    },
    // 检查servers的可用性
    async requestCheckUsability({}, params) {
      const data = await testAp(params).catch(() => ({
        test_result: false,
        test_logs: []
      }))
      return data
    },
    // 加载插件基础信息
    async requestPluginBase({}, params) {
      const data = await initPluginData(params).catch(() => {})
      return data
    },
    // 拉取任务配置参数
    async requestGlobalSettings() {
      const data = await retrieveGlobalSettings({
        key: 'job_settings'
      }).catch(() => ({ jobSettings: {} }))
      return transformDataKey(data)
    },
    // 保存任务配置参数
    async saveGlobalSettings({}, params) {
      const data = await jobSettings(params, { needRes: true }).catch(() => ({}))
      return data
    },
    /**
     * 获取操作权限
     */
    async getApPermission({}, param) {
      const res = await listApPermission(param).catch(() => ({
        edit_action: [],
        delete_action: [],
        create_action: false
      }))
      return res
    }
  }
}

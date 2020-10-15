/**
 * @file main store
 * @author v_daoqgong@tencent.com <v_daoqgong@tencent.com>
 */

import Vue from 'vue'
import Vuex from 'vuex'
import http from '@/api'
import { unifyObjectStyle } from '@/common/util'
import navList from '@/router/navigation-config'
import { retrieveBiz, fetchTopo } from '@/api/modules/cmdb'
import { retrieveGlobalSettings } from '@/api/modules/meta'
import { fetchPermission } from '@/api/modules/permission'
import axios from 'axios'

Vue.use(Vuex)

// 获取modules下的所有模块
const moduleFiles = require.context('./modules', false, /\.js$/)
const modules = moduleFiles.keys().reduce((modules, modulePath) => {
  const moduleName = modulePath.replace(/^\.\/(.*)\.\w+$/, '$1')
  const value = moduleFiles(modulePath)
  modules[moduleName] = value.default
  return modules
}, {})

const store = new Vuex.Store({
  // 模块
  modules,
  // 公共 store
  state: {
    nmMainLoading: false, // 全局可视区域加载
    mainContentLoading: false,
    // 系统当前登录用户
    user: {},
    // 导航信息
    navList,
    // 当前一级导航name
    currentNavName: '',
    // 三级导航标题
    currentNavTitle: '',
    // 是否自定义导航内容
    customNavContent: false,
    // 是否展示默认背景
    isDefaultContent: false,
    // 业务范围
    bkBizList: [],
    // 当前选择的业务
    selectedBiz: [],
    // 云服务商列表
    ispList: [],
    // 表格字号设置
    fontSize: '',
    fontList: [],
    // 语音类型
    language: '',
    // 权限中心开关
    permissionSwitch: false,
    // 业务权限细化
    bizAction: '',
    // 当前页面是否有
    hasPagePermission: true
  },
  // 公共 getters
  getters: {
    mainContentLoading: state => state.mainContentLoading,
    nmMainLoading: state => state.nmMainLoading,
    user: state => state.user,
    navList: state => state.navList.filter(nav => !nav.disabled),
    currentNavName: state => state.currentNavName,
    currentNavTitle: state => state.currentNavTitle,
    customNavContent: state => state.customNavContent,
    isDefaultContent: state => state.isDefaultContent,
    bkBizList: state => state.bkBizList,
    ispList: state => state.ispList,
    selectedBiz: state => state.selectedBiz,
    fontSize: state => state.fontSize,
    fontList: state => state.fontList,
    language: state => state.language,
    permissionSwitch: state => state.permissionSwitch,
    bizAction: state => state.bizAction,
    hasPagePermission: state => state.hasPagePermission
  },
  // 公共 mutations
  mutations: {
    /**
     * 设置内容区的 loading 是否显示
     *
     * @param {Object} state store state
     * @param {boolean} loading 是否显示 loading
     */
    setMainContentLoading(state, loading) {
      state.mainContentLoading = loading
    },

    /**
     * 设置全局可视区域的 loading 是否显示
     *
     * @param {Object} state store state
     * @param {boolean} loading 是否显示 loading
     */
    setNmMainLoading(state, loading) {
      state.nmMainLoading = loading
    },
    /**
     * 更新当前用户 user
     *
     * @param {Object} state store state
     * @param {Object} user user 对象
     */
    updateUser(state, user) {
      state.user = Object.assign({}, user)
    },
    /**
     * 更新当前一级导航信息
     * @param {Object} state
     * @param {String} name
     */
    updateCurrentNavName(state, name) {
      state.currentNavName = name
    },
    /**
     * 更新二级导航激活菜单项
     * @param {Object} state
     * @param {String} name
     */
    updateSubMenuName(state, name) {
      const index = state.navList.findIndex(item => item.name === state.currentNavName)
      const exitChildren = state.navList[index]
        && state.navList[index].children
        && state.navList[index].children.some(item => item.name === name)
      if (exitChildren) {
        state.navList[index].currentActive = name
      }
    },
    /**
     * 设置三级导航标题
     * @param {*} state
     * @param {*} title
     */
    setNavTitle(state, title) {
      state.currentNavTitle = title
    },
    /**
     * 设置是否自定义导航内容
     * @param {*} state
     * @param {*} show
     */
    setCustomNavContent(state, show = false) {
      state.customNavContent = show
    },
    /**
     * 到顶部返回的路由背景重置为白色
     * @param {*} state
     * @param {*} isDefault
     */
    setToggleDefaultContent(state, isDefault = false) {
      state.isDefaultContent = isDefault
    },
    /**
     * 业务范围
     * @param {*} state
     * @param {*} list
     */
    setBkBizList(state, list = []) {
      state.bkBizList = list
    },
    /**
     * 云服务商
     * @param {*} state
     * @param {*} list
     */
    setIspList(state, list = []) {
      state.ispList = list
    },
    /**
     * 当前选中的业务范围
     * @param {*} state
     * @param {*} biz
     */
    setSelectedBiz(state, biz = []) {
      state.selectedBiz = biz
    },
    setFont(state, list = []) {
      Vue.set(state, 'fontList', list)
      const font = list.length ? list.find(item => item.checked) : false
      if (font) {
        state.fontSize = font.id
      }
    },
    /**
     * 当前语言类型
     * @param {String} language
     */
    setLanguage(state, language) {
      state.language = language
    },
    updatePermissionSwitch(state, permissionSwitch) {
      state.permissionSwitch = permissionSwitch
    },
    /**
     * 更新业务的拉取权限类型
     */
    updateBizAction(state, action) {
      state.bizAction = action
    },
    /**
     * 更新页面的查看权限
     */
    updatePagePermission(state, permission) {
      state.hasPagePermission = permission
    }
  },
  actions: {
    /**
     * 获取用户信息
     *
     * @param {Object} context store 上下文对象 { commit, state, dispatch }
     *
     * @return {Promise} promise 对象
     */
    userInfo(context, config = {}) {
      // ajax 地址为 USER_INFO_URL，如果需要 mock，那么只需要在 url 后加上 AJAX_MOCK_PARAM 的参数，
      // 参数值为 mock/ajax 下的路径和文件名，然后加上 invoke 参数，参数值为 AJAX_MOCK_PARAM 参数指向的文件里的方法名
      // 例如本例子里，ajax 地址为 USER_INFO_URL，mock 地址为 USER_INFO_URL?AJAX_MOCK_PARAM=index&invoke=getUserInfo

      // 后端提供的地址
      // const url = USER_INFO_URL
      // mock 的地址，示例先使用 mock 地址
      const mockUrl = `${USER_INFO_URL
        + (USER_INFO_URL.indexOf('?') === -1 ? '?' : '&') + AJAX_MOCK_PARAM}=index&invoke=getUserInfo`
      return http.get(mockUrl, {}, config).then((response) => {
        const userData = response.data || {}
        context.commit('updateUser', userData)
        return userData
      })
    },
    /**
     * 获取业务范围列表
     * @param {*} param0
     * @param {*} params
     */
    async getBkBizList({ commit }, params) {
      const list = await retrieveBiz(params).catch(() => ([]))
      commit('setBkBizList', list)
      return list
    },
    /**
     * 获取业务权限列表(权限接口是复用的业务列表接口，单独写是一个界面可能会发多次请求，但有些请求是不需要更新业务列表的)
     * @param {*} param0
     * @param {*} params
     */
    async getBkBizPermission({ commit }, { action,  updateBiz }) {
      const list = await retrieveBiz({ action }).catch((err) => {
        if (axios.isCancel(err)) {
          return err // 取消的请求需要自己处理
        }
        return []
      })
      updateBiz && Array.isArray(list) && commit('setBkBizList', list)
      return list
    },
    /**
     * 云服务商列表
     * @param {*} param0
     * @param {*} params
     */
    async getIspList({ commit }) {
      const data = await retrieveGlobalSettings({
        key: 'isp'
      }).catch(() => ([]))
      commit('setIspList', data.isp)
    },
    /**
     * 获取业务下的拓扑
     */
    async getBizTopo({}, { bk_biz_id }) {
      const res = await fetchTopo({ bk_biz_id }).catch(() => {})
      return res
    },
    /**
     * 获取权限申请详情
     * @param { instance_id, instance_name } param
     */
    async getApplyPermission({}, param) {
      const res = await fetchPermission(param).catch(() => ({
        apply_info: [],
        url: ''
      }))
      return res
    }
  }
})

/**
 * hack vuex dispatch, add third parameter `config` to the dispatch method
 *
 * @param {Object|string} _type vuex type
 * @param {Object} _payload vuex payload
 * @param {Object} config config 参数，主要指 http 的参数，详见 src/api/index initConfig
 *
 * @return {Promise} 执行请求的 promise
 */
store.dispatch = function (_type, _payload, config = {}) {
  const { type, payload } = unifyObjectStyle(_type, _payload)

  const action = { type, payload, config }
  const entry = store._actions[type]
  if (!entry) {
    if (NODE_ENV !== 'production') {
      console.error(`[vuex] unknown action type: ${type}`)
    }
    return
  }

  store._actionSubscribers.forEach(sub => sub(action, store.state))

  return entry.length > 1
    ? Promise.all(entry.map(handler => handler(payload, config)))
    : entry[0](payload, config)
}

export default store

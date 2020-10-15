import { VuexModule, Module, Action, getModule, Mutation } from 'vuex-module-decorators'
import store from '@/store'
import { listCloud, deleteCloud, createCloud, retrieveCloud, updateCloud } from '@/api/modules/cloud'
import { retrieveCloudProxies, updateHost, removeHost } from '@/api/modules/host'
import { listAp } from '@/api/modules/ap'
import { installJob, operateJob } from '@/api/modules/job'
import { listCloudPermission } from '@/api/modules/permission'
import { transformDataKey } from '@/common/util'
import { ICloudAuth } from '@/types/cloud/cloud'
import axios from 'axios'

export const SET_CLOUD_AP = 'SET_CLOUD_AP'
export const SET_CLOUD_LIST = 'SET_CLOUD_LIST'
export const UPDATE_AP_URL = 'updateApUrl'
// eslint-disable-next-line new-cap
@Module({ name: 'cloud', dynamic: true, namespaced: true, store })
class Cloud extends VuexModule {
  private apData: any[] = [] // 接入点
  private list: any[] = [] // 云区域列表
  private url = '' // 接入点Url
  private authorityMap: ICloudAuth = {}

  public get apList() {
    return this.apData
  }
  public get cloudList() {
    return this.list
  }
  public get apUrl() {
    return this.url
  }
  public get authority() {
    return this.authorityMap
  }

  // 接入点数据
  @Mutation
  public [SET_CLOUD_AP](data = []) {
    this.apData = data
  }
  @Mutation
  public [SET_CLOUD_LIST](data = []) {
    this.list = data
  }
  @Mutation
  public [UPDATE_AP_URL](apUrl = '') {
    this.url = apUrl
  }
  @Mutation
  public setAuthority(map: ICloudAuth = {}) {
    this.authorityMap = map
  }

  /**
    * 获取云区域列表
    * @param {s} param0
    * @param {*} params
    */
  @Action
  public async getCloudList(params: any) {
    let data = await listCloud(params).then((res: any) => res.map((item: any) => Object.assign(item, item.permissions)))
      .catch(() => [])
    // 排序 未安装 --> 异常 --> 正常
    data = transformDataKey(data).sort((pre: any, next: any) => {
      if (!pre.proxyCount || !next.proxyCount) {
        return pre.proxyCount - next.proxyCount
      }
      return Number(pre.exception !== 'abnormal') - Number(next.exception !== 'abnormal')
    })
    this[SET_CLOUD_LIST](data)
    return data
  }
  /**
   * 获取接入点
   */
  @Action
  public async getApList() {
    const data = await listAp().catch(() => [])
    this[SET_CLOUD_AP](data)
    return data
  }
  /**
   * 获取云区域详情
   * @param {*} pk
   */
  @Action
  public async getCloudDetail(pk: string) {
    const data = await retrieveCloud(pk).catch(() => ({}))
    return transformDataKey(data)
  }
  /**
   * 删除云区域
   * @param {*} params
   */
  @Action
  public async deleteCloud(params: any) {
    const data = await deleteCloud(params, null, { needRes: true }).catch(() => false)
    return data
  }
  /**
   * 创建云区域
   * @param {*} params
   */
  @Action
  public async createCloud(params: any) {
    const data = await createCloud(params).catch(() => false)
    return data
  }
  /**
   * 安装Proxy
   * @param {*} param0
   * @param {*} params
   */
  @Action
  public async setupProxy({ params, config }: any) {
    const data = installJob(params, config).catch(() => false)
    return data
  }
  /**
   * 更新云区域
   * @param {*} commit
   * @param {*} pk
   * @param {*} params
   */
  @Action
  public async updateCloud({ pk, params }: any) {
    const data = await updateCloud(pk, params).then(() => true)
      .catch(() => false)
    return data
  }
  /**
   * 获取云区域Proxy列表
   * @param {*} param0
   * @param {*} pk
   */
  @Action
  public async getCloudProxyList(params: any) {
    let data = await retrieveCloudProxies(params).catch(() => [])
    data = data.map((item: any) => {
      const {
        bt_speed_limit: btSpeedLimit,
        peer_exchange_switch_for_agent: peerExchangeSwitchForAgent
      } = item.extra_data || {}
      item.status = item.status ? item.status.toLowerCase() : ''
      item.bt_speed_limit = btSpeedLimit || ''
      item.peer_exchange_switch_for_agent = !!peerExchangeSwitchForAgent || false
      return item
    })
    return data
  }
  /**
   * 更新主机信息
   * @param {*} param0
   * @param {*} params
   */
  @Action
  public async updateHost(params: any) {
    const data = await updateHost(params).catch(() => false)
    return data
  }
  /**
   * Proxy 重启 下线 卸载操作
   * @param {*} param0
   * @param {*} params
   */
  @Action
  public async operateJob(params: any) {
    const data = await operateJob(params).catch(() => false)
    return data
  }
  /**
   * 移除Proxy
   * @param {*} param0
   * @param {*} params
   */
  @Action
  public async removeHost(params: any) {
    const data = await removeHost(params).catch(() => false)
    return data
  }
  /**
   * 获取服务信息
   * @param {*} param0
   * @param {*} params
   */
  // public async getServiceInfo(params) {
  //   const data = await serviceInfo(params).catch(() => ({}))
  //   return data
  // }
  /**
   * 安装proxy时获取ap的URL
   * @param {id} ap的id
   * @param {urlType} 节点需要的url类型
   */
  @Action
  public setApUrl({ id, urlType = 'package_outer_url' }: any) {
    let apUrl = ''
    if (!id && id !== 0) {
      this[UPDATE_AP_URL]()
      return
    }
    const filterAp = id === -1 ? this.apData.filter(item => item.id !== -1) : this.apData.filter(item => item.id === id)
    if (filterAp.length) {
      apUrl = filterAp.map(item => item[urlType]).join(', ')
    }
    this[UPDATE_AP_URL](apUrl)
  }
  /**
   * 获取操作权限
   */
  @Action
  public async getCloudPermission(param: any) {
    const res = await listCloudPermission(param).catch((err: any) => {
      if (axios.isCancel(err)) {
        return err
      }
      return {
        edit_action: [],
        delete_action: [],
        create_action: false,
        view_action: []
      }
    })
    return res
  }
}

export default getModule(Cloud)

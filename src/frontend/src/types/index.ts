import RequestQueue from '@/api/request-queue'
import CachedPromise from '@/api/cached-promise'
import { CancelToken, Canceler } from 'axios'

/* eslint-disable camelcase */
export interface ILoginData {
  width: number
  height: number
  login_url: string
  has_plain: boolean
}

export interface IAuth {
  permission: boolean
  apply_info: any
}

export interface ILoginRes {
  data: ILoginData
  config: any
  login_url: string
}

export type RequestMethods = 'delete' | 'get' | 'head' | 'post' | 'put' | 'patch'
export interface IUserConfig {
  // http 请求默认 id
  requestId?: string
  // 是否全局捕获异常
  globalError?: boolean
  // 是否直接复用缓存的请求
  fromCache?: boolean
  // 是否在请求发起前清楚缓存
  clearCache?: boolean
  // 响应结果是否返回原始数据
  originalResponse?: boolean
  // 当路由变更时取消请求
  cancelWhenRouteChange?: boolean
  // 取消上次请求
  cancelPrevious?: boolean
  cancelToken?: CancelToken
  cancelExcutor?: Canceler
}
export interface IResponse {
  config: IUserConfig
  response: any
  resolve: (value?: unknown, config?: unknown) => void
  reject: (value?: unknown) => void
}

export interface IAxiosConfig {
  checkData?: boolean
  needRes?: boolean
}

export interface INodemanHttp {
  queue: RequestQueue
  cache: CachedPromise
  cancelRequest: (id: string) => Promise<any>
  cancelCache: (id: string) => Promise<any>
  cancel: (id: string | string[]) => Promise<any>
  delete?: () => Promise<any>
  get?: () => Promise<any>
  head?: () => Promise<any>
  post?: () => Promise<any>
  put?: () => Promise<any>
  patch?: () => Promise<any>
  [prop: string]: any
}

export interface INavConfig {
  title?: string // 一级导航标题
  name: string // 一级导航ID
  path?: string // 一级导航path（如果有children属性则此字段无效）
  currentActive?: string // 当前二级导航选中项
  defaultActive?: string // 当前二级导航初始化选中项
  disabled?: boolean // 是否禁用一级导航
  children?: ISubNavConfig[] // 二级导航配置
}

export interface ISubNavConfig {
  title: string // 二级导航标题
  icon: string // 二级导航icon
  path: string // 二级导航Path
  name: string // 二级导航id
  group?: boolean // 是否显示分组线
}

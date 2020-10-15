import { TranslateResult } from 'vue-i18n'
export interface IPluginRule {
  [prop: string]: any
}

export interface IPagination {
  current: number
  count: number
  limit: number
}

export interface IMenu {
  id: string | number
  name: string | TranslateResult
  disabled?: boolean
}

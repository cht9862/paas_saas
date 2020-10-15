import { request } from '../base'

export const listHost = request('POST', 'plugin/search/')
export const listPackage = request('GET', 'plugin/{{pk}}/package/')
export const listProcess = request('GET', 'plugin/{{pk}}/process/')
export const listProcessStatus = request('POST', 'plugin/process/status/')
export const operatePlugin = request('POST', 'plugin/operate/')

export default {
    listHost,
    listPackage,
    listProcess,
    listProcessStatus,
    operatePlugin
}

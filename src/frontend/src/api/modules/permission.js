import { request } from '../base'

export const fetchPermission = request('POST', 'permission/fetch/')
export const listApPermission = request('GET', 'permission/ap/')
export const listCloudPermission = request('GET', 'permission/cloud/')

export default {
    fetchPermission,
    listApPermission,
    listCloudPermission
}

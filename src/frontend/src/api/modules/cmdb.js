import { request } from '../base'

export const fetchTopo = request('GET', 'cmdb/fetch_topo/')
export const retrieveBiz = request('GET', 'cmdb/biz/')

export default {
    fetchTopo,
    retrieveBiz
}

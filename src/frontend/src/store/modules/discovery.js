/* eslint-disable max-len */
function promiseData(data, timeout = 2000) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(data)
    }, timeout)
  })
}
function randomRange(min, max) {
  return Math.floor((Math.random() * ((max - min) + 1)) + min)
}
const requestDiscoveryListMock = () => promiseData({
  result: true,
  data: [
    { id: 11, ip: '127.0.0.11', type: 'pending', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 12, ip: '127.0.0.12', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'error', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 13, ip: '127.0.0.13', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 14, ip: '127.0.0.14', type: 'pending', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'error', version: '--', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 15, ip: '127.0.0.15', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 16, ip: '127.0.0.16', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'error', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 17, ip: '127.0.0.17', type: 'pending', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 18, ip: '127.0.0.18', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'error', version: '1.6.3', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 19, ip: '127.0.0.19', type: 'pending', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '--', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 20, ip: '127.0.0.20', type: 'pending', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'normal', version: '--', find_time: ' 2018-11-03 00:00:00', num: 123 },
    { id: 21, ip: '127.0.0.21', type: 'ignored', cloudId: '10', cloudName: '上海一区', sys: 'Windows', status: 'unknown', version: '--', find_time: ' 2018-11-03 00:00:00', num: 123 }
  ],
  message: 'success',
  code: 'OK'
})

const successOnly = () => promiseData(Object.assign({}, {
  result: true,
  data: null,
  message: 'success',
  code: 'OK'
}), randomRange(500, 2000))

export default {
  namespaced: true,
  state: {},
  getters: {},
  mutations: {},
  actions: {
    // 发现的主机列表
    async requestDiscoveryList({}) {
      const res = await requestDiscoveryListMock()
      return res
    },
    async setHostIdleStatus() {
      const res = await successOnly()
      return res
    }
  }
}

import './public-path'
import Vue from 'vue'

import App from '@/App.vue'
import router from '@/router'
import store from '@/store'
import { bus } from '@/common/bus'
import i18n from '@/setup'
import LoadingIcon from '@/components/loading-icon/loading-icon.vue'

if (process.env.NODE_ENV === 'development') {
  Vue.config.devtools = true
}

Vue.component('loading-icon', LoadingIcon)

global.bus = bus
global.i18n = i18n
global.mainComponent = new Vue({
  el: '#app',
  router,
  store,
  i18n,
  components: { App },
  template: '<App/>'
})

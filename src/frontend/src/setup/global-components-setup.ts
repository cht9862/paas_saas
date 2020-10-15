import Vue from 'vue'
// 全局组件
import '@/common/bkmagic'
import Exception from '@/components/exception/index.vue'
import AuthLogin from '@/components/auth/index.vue'
import AuthComponent from '@/components/auth/auth.vue'
import BkBizSelect from '@/components/biz-select/bk-biz-select.vue'

Vue.component('app-exception', Exception)
Vue.component('app-auth', AuthLogin)
Vue.component('auth-component', AuthComponent)
Vue.component('bk-biz-select', BkBizSelect)

import { Component, Vue } from 'vue-property-decorator'
import store from '@/store'

Component.registerHooks([
  'beforeRouteEnter'
])
// eslint-disable-next-line new-cap
export default () => Component(class authorityMixin extends Vue {
  public authority: {[propsName: string]: boolean} = {
    operate: true
  }
  public beforeRouteEnter(to: any, from: any, next: any) {
    next((vm: any) => {
      vm.handleInitPageAuthority(to.meta?.authority?.operate)
    })
  }
  public async handleInitPageAuthority(action: string) {
    if (!action || !store.getters.permissionSwitch) return
    const list = await store.dispatch('getBkBizPermission', { action })
    this.authority.operate = Array.isArray(list) ? !!list.length : true
  }
})


import { Module, VuexModule, getModule, Action } from 'vuex-module-decorators'
import store from '@/store'

// eslint-disable-next-line new-cap
@Module({ name: 'plugin', namespaced: true, dynamic: true, store })
class Plugin extends VuexModule {
  @Action
  public async getPluginRules() {
    return [
      {
        name: 'test'
      }
    ]
  }
}

export default getModule(Plugin)

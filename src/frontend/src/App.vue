<template>
  <div id="app" :class="systemCls">
    <nodeman-navigation>
      <div v-bkloading="{ isLoading: mainContentLoading, opacity: 1 }">
        <router-view :key="routerKey" v-show="!mainContentLoading" />
      </div>
    </nodeman-navigation>
    <app-auth ref="bkAuth"></app-auth>
    <permission-modal ref="permissionModal"></permission-modal>
  </div>
</template>
<script lang="ts">
import { mapGetters, mapMutations } from 'vuex'
import { bus } from '@/common/bus'
import NodemanNavigation from '@/components/navigation/navigation.vue'
import PermissionModal from '@/components/auth/PermissionModal.vue'
import AppAuth from '@/components/auth/index.vue'
import { STORAGE_KEY_BIZ, STORAGE_KEY_FONT } from '@/config/storage-key'
import { Vue, Component, Ref, Watch } from 'vue-property-decorator'
import { ILoginRes } from '@/types/index'

@Component({
  name: 'app',
  computed: mapGetters(['mainContentLoading', 'bkBizList', 'selectedBiz']),
  components: {
    NodemanNavigation,
    PermissionModal
  },
  methods: mapMutations([
    'setSelectedBiz',
    'setFont',
    'setLanguage',
    'updatePermissionSwitch'
  ])
})
export default class App extends Vue {
  @Ref('bkAuth') private readonly bkAuth!: AppAuth
  @Ref('permissionModal') private readonly permissionModal!: any

  private readonly mainContentLoading!: boolean
  private readonly setSelectedBiz!: Function
  private readonly setFont!: Function
  private readonly setLanguage!: Function
  private readonly updatePermissionSwitch!: Function
  private readonly bkBizList!: any[]
  private readonly selectedBiz!: (string | number)[]

  private routerKey = +new Date()
  private systemCls = 'mac'
  private fontList = [
    {
      id: 'standard',
      name: window.i18n.t('标准'),
      checked: true
    },
    {
      id: 'large',
      name: window.i18n.t('偏大'),
      checked: false
    }
  ]

  @Watch('bkBizList')
  private handleBizListChange(v: any[]) {
    const selectedBiz = this.selectedBiz.filter(id => v.find(data => data.bk_biz_id === id))
    this.setSelectedBiz(selectedBiz)
  }

  private created() {
    const platform = window.navigator.platform.toLowerCase()
    if (platform.indexOf('win') === 0) {
      this.systemCls = 'win'
    }
    this.setLanguage(window.language)
    this.handleInit()
  }
  private mounted() {
    bus.$on('show-login-modal', (data: ILoginRes) => {
      if (process.env.NODE_ENV === 'development') {
        window.location.href = LOGIN_DEV_URL + window.location.href
      } else {
        const res = data?.data || {}
        const config = data?.config || {}
        const topWindow = (() => {
          try {
            if (window.top && window.top.document) {
              return window.top
            }
            return window
          } catch (_) {
            console.log('TOP对象无法获取')
            return window
          }
        })()
        if (res.has_plain) {
          topWindow.BLUEKING.corefunc.open_login_dialog(res.login_url, res.width, res.height, config.method)
        } else {
          const href = data.login_url ? data.login_url : (LOGIN_DEV_URL + window.location.href)
          window.location.href = href
        }
        // this.$refs.bkAuth.showLoginModal(res)
      }
    })
    bus.$on('close-login-modal', () => {
      this.bkAuth.hideLoginModal()
      setTimeout(() => {
        window.location.reload()
      }, 0)
    })
    bus.$on('show-permission-modal', (data: any) => {
      this.permissionModal.show(data)
    })
  }
  /**
   * 初始化应用
   */
  private handleInit() {
    let selectedBiz = []
    if (window.localStorage) {
      try {
        selectedBiz = JSON.parse(window.localStorage.getItem(STORAGE_KEY_BIZ) as string) || []
        const font = window.localStorage.getItem(STORAGE_KEY_FONT)
        if (font && this.fontList.find(item => item.id === font)) {
          this.fontList.forEach((item) => {
            item.checked = font === item.id
          })
        }
      } catch (_) {
        selectedBiz = []
      }
    }
    this.updatePermissionSwitch(window.PROJECT_CONFIG.USE_IAM === 'True')
    this.setFont(this.fontList)
    this.setSelectedBiz(selectedBiz)
  }
}
</script>
<!--全局样式-->
<style>
@import "./font/style.css";
@import "../src/css/reset.css";
@import "../src/css/app.css";
</style>

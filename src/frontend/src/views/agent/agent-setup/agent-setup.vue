<template>
  <article class="agent-setup">
    <!--左侧表单信息-->
    <section class="agent-setup-left">
      <tips class="mb20">
        <template #default>
          <p>
            {{ $t('安装要求tips', { type: 'Agent' }) }}
            <bk-link class="tips-link" theme="primary" @click="handleShowPanel">{{ $t('安装要求') }}</bk-link>
            {{ $t('表格展示设置tips') }}
            <bk-link class="tips-link" theme="primary" @click="handleShowSetting">{{ $t('表格展示设置') }}</bk-link>
          </p>
        </template>
      </tips>
      <div class="setup-form">
        <bk-form ref="form" class="mb30" :model="formData" :rules="rules">
          <install-method :is-manual="isManual" @change="installMethodHandle"></install-method>
          <bk-form-item error-display-type="normal" property="bk_biz_id" :label="$t('安装到业务')" required>
            <bk-biz-select class="content-basic"
                           v-model="formData.bk_biz_id"
                           :show-select-all="false"
                           :multiple="false"
                           :auto-update-storage="false"
                           :clearable="false"
                           @change="handleBizChange">
            </bk-biz-select>
          </bk-form-item>
          <bk-form-item error-display-type="normal" :label="$t('云区域')" property="bk_cloud_id" required>
            <permission-select
              :class="['content-basic', { 'is-error': ['no_proxy', 'overdue'].includes(proxyStatus) }]"
              searchable
              :permission="permissionSwitch"
              :permission-type="'cloud_view'"
              :permission-key="'view'"
              :placeholder="$t('选择云区域')"
              :loading="loadingCloudList"
              :option-list="bkCloudList"
              :option-id="'bk_cloud_id'"
              :option-name="'bk_cloud_name'"
              v-model="formData.bk_cloud_id"
              @change="handleCloudChange"
              @toggle="handleCloudToggle">
            </permission-select>
            <i18n
              :path="i18nPath"
              class="form-error-tip item-error-tips"
              tag="p"
              v-show="['no_proxy', 'overdue'].includes(proxyStatus)">
              <span
                class="btn"
                @click="handleGotoProxy">
                {{ proxyStatus === 'overdue' ? $t('前往更新') : $t('前往安装') }}
              </span>
            </i18n>
          </bk-form-item>
          <bk-form-item
            error-display-type="normal"
            property="ap_id"
            :label="$t('接入点')"
            required>
            <bk-select class="content-basic"
                       v-model="formData.ap_id"
                       v-bk-tooltips="{
                         delay: [300, 0],
                         content: $t('接入点已在云区域中设定'),
                         disabled: !apDisabled,
                         placement: 'right'
                       }"
                       :clearable="false"
                       :disabled="apDisabled || isEmptyCloud"
                       :loading="loadingApList">
              <bk-option v-for="item in curApList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
            </bk-select>
          </bk-form-item>
          <bk-form-item :label="$t('安装信息')" :class="{ 'mb30': isScroll }" required>
            <filter-ip-tips
              class="mb15 filter-tips"
              v-if="filterList.length && showFilterTips"
              @click="handleShowDetail">
            </filter-ip-tips>
            <setup-table
              :class="{ 'agent-setup-table': isManual }"
              ref="setupTable"
              :local-mark="'agent_steup'"
              :is-manual="isManual"
              :setup-info="setupInfo"
              :extra-params="extraParams"
              auto-sort
              @add="handleAddItem"
              @delete="handleDeleteItem">
            </setup-table>
          </bk-form-item>
        </bk-form>
        <div class="form-btn" :class="{ 'fixed': isScroll, 'shrink': isScroll && showRightPanel }">
          <bk-button theme="primary" ext-cls="nodeman-primary-btn" @click="handleSetup" :loading="loadingSetupBtn">
            <div class="form-btn-install">
              <span>{{ $t('安装') }}</span>
              <span class="num">{{ setupNum }}</span>
            </div>
          </bk-button>
          <bk-button class="nodeman-cancel-btn ml10" @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
      </div>
    </section>
    <!--右侧提示信息-->
    <section class="agent-setup-right" :class="{ 'right-panel': showRightPanel }">
      <right-panel v-model="showRightPanel" :host-type="hostType" :host-list="hostList"></right-panel>
      <!-- <right-panel v-model="showRightPanel" :list="tipsList" :title="$t('安装要求')"></right-panel> -->
    </section>
    <!--过滤ip信息-->
    <template>
      <filter-dialog v-model="showFilterDialog" :list="filterList" :title="$t('忽略详情')"></filter-dialog>
    </template>
  </article>
</template>
<script>
import Tips from '@/components/tips/tips.vue'
import RightPanel from '@/components/tips/right-panel-tips.vue'
import SetupTable from '@/components/setup-table/setup-table.vue'
import InstallMethod from '@/components/install-method/install-method.vue'
import FilterIpTips from '@/components/tips/filter-ip-tips'
import mixin from '@/components/tips/filter-ip-mixin'
import formLabelMixin from '@/common/form-label-mixin'
import FilterDialog from '@/components/tips/filter-dialog.vue'
import PermissionSelect from '@/components/permission-select/permission-select.vue'
import getTipsTemplate from '../config/tips-template'
import { setupTableConfig, setupTableManualConfig } from '../config/setupTableConfig'
import { addListener, removeListener } from 'resize-detector'
import { debounce, isEmpty, deepClone } from '@/common/util'
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'agent-setup',
  components: {
    Tips,
    RightPanel,
    SetupTable,
    InstallMethod,
    FilterIpTips,
    FilterDialog,
    PermissionSelect
  },
  mixins: [mixin, formLabelMixin],
  data() {
    return {
      // 是否为安装方式
      isManual: false,
      // 表单数据
      formData: {
        bk_biz_id: '',
        bk_cloud_id: '',
        ap_id: ''
      },
      // 表单校验
      rules: {
        bk_biz_id: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        bk_cloud_id: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        ap_id: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ]
      },
      // 右侧提示面板是否显示
      showRightPanel: false,
      // agent安装信息表格
      setupInfo: {
        header: setupTableConfig,
        data: []
      },
      // 监听界面滚动
      listenResize: null,
      isScroll: false,
      // 安装按钮加载中的状态
      loadingSetupBtn: false,
      // 云区域列表加载状态
      loadingCloudList: false,
      // 接入点列表加载状态
      loadingApList: false,
      // 安装信息数量
      setupNum: 1,
      apList: [],
      // 接入点是否只读
      apDisabled: false,
      // Proxy状态
      proxyStatus: '',
      // Proxy所在云区域ID
      proxyCloudId: undefined
    }
  },
  computed: {
    ...mapGetters(['permissionSwitch']),
    ...mapGetters('agent', ['cloudList', 'apUrl']),
    // 当前云区域列表
    bkCloudList() {
      return this.cloudList.filter(item => !item.bk_biz_scope || item.bk_biz_scope.includes(this.formData.bk_biz_id))
    },
    i18nPath() {
      if (this.proxyStatus === 'no_proxy') {
        return 'Proxy未安装'
      }
      return 'Proxy过期'
    },
    curApList() {
      if (this.isManual
        || (this.formData.bk_cloud_id === window.PROJECT_CONFIG.DEFAULT_CLOUD && this.apList.length === 2)) {
        return this.apList.filter(item => item.id !== -1)
      }
      return this.apList
    },
    // 右侧面板提示信息
    tipsList() {
      return getTipsTemplate({ apUrl: this.apUrl, net: this.isDefaultCloud })
    },
    isEmptyCloud() {
      return isEmpty(this.formData.bk_cloud_id)
    },
    isDefaultCloud() {
      return window.PROJECT_CONFIG.DEFAULT_CLOUD === this.formData.bk_cloud_id
    },
    // 编辑态额外参数 - 安装类型切换时会丢失已填数据
    extraParams() {
      return this.isManual ? ['port', 'account', 'auth_type', 'password', 'prove'] : ['password', 'prove']
    },
    hostType() {
      if (isEmpty(this.formData.bk_cloud_id)) {
        return 'mixed'
      } if (this.isDefaultCloud) {
        return 'agent'
      }
      return 'Pagent'
    },
    hostList() {
      const curCloud = this.cloudList.find(item => item.bk_cloud_id === this.formData.bk_cloud_id)
      return this.setupInfo.data.map(item => ({
        bk_cloud_id: this.formData.bk_cloud_id,
        bk_cloud_name: curCloud ? curCloud.bk_cloud_name : '',
        inner_ip: item ? item.inner_ip : '',
        ap_id: this.formData.ap_id
      }))
    }
  },
  watch: {
    'formData.ap_id'(val) {
      let urlType = ''
      if (isEmpty(this.formData.bk_cloud_id)) {
        urlType = ''
      } else if (this.isDefaultCloud) {
        urlType = 'package_inner_url'
      } else {
        urlType = 'package_outer_url'
      }
      this.setApUrl({
        id: val,
        urlType
      })
    }
  },
  created() {
    this.handleInit()
  },
  mounted() {
    this.listenResize = debounce(300, v => this.handleResize(v))
    addListener(this.$el, this.listenResize)
    this.initLabelWidth(this.$refs.form)
  },
  beforeDestroy() {
    this.setApUrl({ id: '' })
    removeListener(this.$el, this.listenResize)
  },
  methods: {
    ...mapActions('agent', ['installAgentJob', 'getApList', 'getCloudList', 'setApUrl']),
    handleInit() {
      this.initApList()
      this.initCloudList()
    },
    async initApList() {
      this.loadingApList = true
      this.apList = await this.getApList()
      this.loadingApList = false
    },
    async initCloudList() {
      this.loadingCloudList = true
      await this.getCloudList({ RUN_VER: window.PROJECT_CONFIG.RUN_VER })
      this.loadingCloudList = false
    },
    /**
     * 监听界面滚动
     */
    handleResize() {
      // 60：三级导航的高度  52： 一级导航高度
      this.isScroll = this.$el.scrollHeight + 60 > this.$root.$el.clientHeight - 52
    },
    /**
     * 获取表单数据
     */
    getFormData() {
      return this.$refs.setupTable.getData().map(item => ({
        ...item,
        bk_biz_id: this.formData.bk_biz_id,
        bk_cloud_id: this.formData.bk_cloud_id,
        ap_id: this.formData.ap_id,
        is_manual: this.isManual
      }))
    },
    /**
     * 开始安装agent
     */
    handleSetup() {
      const setupTableValidate = this.$refs.setupTable.validate()
      this.$refs.form.validate().then(async () => {
        if (setupTableValidate) {
          this.loadingSetupBtn = true
          const params = {
            job_type: 'INSTALL_AGENT',
            hosts: this.getFormData().map((item) => {
              if (isEmpty(item.login_ip)) {
                delete item.login_ip
              }
              if (isEmpty(item.bt_speed_limit)) {
                delete item.bt_speed_limit
              } else {
                item.bt_speed_limit = Number(item.bt_speed_limit)
              }
              item.peer_exchange_switch_for_agent += 0
              return item
            })
          }
          const res = await this.installAgentJob({
            params,
            config: {
              needRes: true,
              globalError: false
            }
          })
          this.loadingSetupBtn = false
          if (!res) return

          if (res.result || res.code === 3801018) {
            // 部分忽略
            // mixin: handleFilterIp 处理过滤IP信息
            this.handleFilterIp(res.data)
          } else if (res.code === 3801013) {
            // Proxy过期或者未安装
            const firstItem = res.data.ip_filter.find(item => ['no_proxy', 'overdue'].includes(item.exception)) || {}
            this.proxyStatus = firstItem.exception
            this.proxyCloudId = firstItem.bk_cloud_id
          } else {
            const message = res.message ? res.message : this.$t('请求出错')
            this.$bkMessage({
              message,
              delay: 3000,
              theme: 'error'
            })
          }
        }
      })
        .catch(() => {})
    },
    /**
     * 取消安装Agent
     */
    handleCancel() {
      this.$router.push({ name: 'agentStatus' })
    },
    /**
     * 添加
     */
    handleAddItem() {
      this.setupNum += 1
    },
    /**
     * 删除
     */
    handleDeleteItem() {
      this.setupNum -= 1
    },
    /**
     * 业务变更
     */
    handleBizChange() {
      this.formData.bk_cloud_id = ''
    },
    /**
     * 云区域变更
     */
    handleCloudChange(value) {
      const item = this.bkCloudList.find(item => item.bk_cloud_id === value)
      if (!this.isManual && item && item.bk_cloud_id !== window.PROJECT_CONFIG.DEFAULT_CLOUD) {
        this.apDisabled = true
        this.formData.ap_id = item.ap_id
      } else {
        this.apDisabled = false
        this.formData.ap_id = this.curApList.length ? this.curApList[0].id : -1
      }
    },
    handleCloudToggle(toggle) {
      if (toggle) {
        this.proxyStatus = ''
      }
    },
    /**
     * 安装方式变更
     */
    installMethodHandle(isManual = false) {
      this.isManual = isManual
      const apList = deepClone(this.apList)
      if (this.isManual) {
        this.setupInfo.header = setupTableManualConfig
        // 手动安装无自动选择
        this.apList = apList.filter(item => item.id !== -1)
        if (this.formData.ap_id === -1) {
          // 自动接入点改默认接入点
          const apDefault = this.isNotAutoSelect ? this.apList[0] : this.apList.find(item => item.is_default)
          // 替换为默认接入点
          this.formData.ap_id = apDefault ? apDefault.id : ''
        }
        // 手动安装可以自由选择接入点
        this.apDisabled = false
      } else {
        this.setupInfo.header = setupTableConfig
        if (!apList.find(item => item.id === -1)) {
          apList.unshift({
            id: -1,
            name: this.$t('自动选择')
          })
          this.apList = apList
        }
        this.handleCloudChange(this.formData.bk_cloud_id)
      }
      this.setupInfo.data = deepClone(this.$refs.setupTable.getData())
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
    },
    /**
     * 跳转Proxy界面
     */
    handleGotoProxy() {
      if (!this.proxyStatus || isEmpty(this.proxyCloudId)) return
      switch (this.proxyStatus) {
        case 'no_proxy': {
          const installRouteData = this.$router.resolve({
            name: 'setupCloudManager',
            params: {
              type: 'create',
              title: this.$t('安装Proxy'),
              id: this.proxyCloudId
            }
          })
          window.open(installRouteData.href, '_blank')
          break
        }
        case 'overdue': {
          const detailRouteData = this.$router.resolve({
            name: 'cloudManagerDetail',
            params: {
              id: this.proxyCloudId
            }
          })
          window.open(detailRouteData.href, '_blank')
          break
        }
      }
    },
    handleShowPanel() {
      this.setupInfo.data = this.getFormData()
      this.showRightPanel = true
    },
    handleCreateCloud() {
      this.$router.push({ name: 'cloudManager' })
    },
    handleShowSetting() {
      this.$refs.setupTable.handleToggleSetting(true)
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

>>> .bk-select {
  background-color: #fff;
  &.is-disabled {
    background-color: #fafbfd;
  }
}
>>> .input-type .bk-form-control {
  height: 32px;
}
>>> .setup-body-wrapper {
  overflow: initial;
}
.agent-setup {
  @mixin layout-flex row;
  &-left {
    flex: 1;
    >>> .agent-setup-table {
      max-width: 1200px;
    }
    .content-basic {
      width: 480px;
      &.is-error {
        border-color: #ff5656;
      }
    }
    .item-error-tips .btn {
      color: #3a84ff;
      cursor: pointer;
      &:hover {
        color: #699df4;
      }
    }
    .form-btn {
      transition: right .2s;

      @mixin layout-flex row, center, center;
      &-install {
        @mixin layout-flex row, center, center;
        .num {
          margin-left: 8px;
          padding: 0 6px;
          height: 16px;
          border-radius: 8px;
          background: #e1ecff;
          color: #3a84ff;
          font-weight: bold;
          font-size: 12px;

          @mixin layout-flex row, center, center;
        }
      }
      &.fixed {
        position: fixed;
        height: 54px;
        left: 60px;
        bottom: 0;
        right: 0;
        background: #fff;
        box-shadow: 0px -3px 6px 0px rgba(49,50,56,.05);
        z-index: 100;
        border-top: 1px solid #e2e2e2;
      }
    }
    .filter-tips {
      margin-top: 8px;
    }
  }
  &-right {
    width: 6px;
    transition: width .2s;
  }
}
</style>

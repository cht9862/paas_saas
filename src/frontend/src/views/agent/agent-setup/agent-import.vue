<template>
  <article class="agent-setup" v-bkloading="{ isLoading: loading }">
    <!--左侧表单信息-->
    <section class="agent-setup-left" ref="setupContent">
      <tips class="mb20">
        <template #default>
          <ul>
            <li v-if="!showSetupBtn" class="tips-content-item">{{ importTips }}</li>
            <li class="tips-content-item" v-if="showSetupBtn">
              {{ $t('安装要求tips', { type: 'Agent' }) }}
              <bk-link class="tips-link" theme="primary" @click="handleShowPanel">{{ $t('安装要求') }}</bk-link>
              {{ $t('表格展示设置tips') }}
              <bk-link class="tips-link" theme="primary" @click="handleShowSetting">{{ $t('表格展示设置') }}</bk-link>
            </li>
          </ul>
        </template>
      </tips>
      <filter-ip-tips
        class="mb15"
        v-if="filterList.length && showFilterTips"
        @click="handleShowDetail">
      </filter-ip-tips>
      <bk-form
        ref="form"
        v-if="showSetupBtn && !isEdit"
        class="mb20 fs0 label-tl-form auto-width-form"
        :label-width="0">
        <install-method :is-manual="isManual" @change="installMethodHandle"></install-method>
      </bk-form>
      <setup-table ref="setupTable"
                   :local-mark="`agent_${type}`"
                   :setup-info="setupInfo"
                   :is-manual="isManual"
                   :min-items="minItems"
                   :height="scrollHeight"
                   :need-plus="false"
                   :virtual-scroll="virtualScroll"
                   :extra-params="extraParams"
                   auto-sort
                   @delete="handleItemDelete">
        <template #empty>
          <parser-excel v-model="importDialog" @uploading="handleUploading"></parser-excel>
        </template>
      </setup-table>
      <div class="mt30 left-footer">
        <bk-button
          v-if="!showSetupBtn"
          theme="primary"
          ext-cls="nodeman-primary-btn mr10"
          :disabled="disabledImport"
          :loading="isUploading"
          @click="handleImport">
          {{ $t('导入') }}
        </bk-button>
        <div class="btn-wrapper" v-else>
          <bk-button theme="primary" ext-cls="nodeman-primary-btn mr10" @click="handleSetup" :loading="loadingSetupBtn">
            <div class="install">
              <span>{{ setupBtnText }}</span>
              <span class="num">{{ setupNum }}</span>
            </div>
          </bk-button>
          <bk-button
            class="nodeman-cancel-btn mr10"
            v-if="!isEdit"
            @click="handleLastStep">
            {{ $t('上一步') }}
          </bk-button>
        </div>
        <bk-button class="nodeman-cancel-btn" @click="handleCancel">{{ $t('取消') }}</bk-button>
      </div>
    </section>
    <!--右侧提示信息-->
    <section class="agent-setup-right" :class="{ 'right-panel': showRightPanel }">
      <right-panel v-model="showRightPanel" :host-type="hostType" :host-list="hostList"></right-panel>
    </section>
    <!--过滤ip信息-->
    <template>
      <filter-dialog v-model="showFilterDialog" :list="filterList" :title="$t('忽略详情')"></filter-dialog>
    </template>
  </article>
</template>
<script>
import RightPanel from '@/components/tips/right-panel-tips.vue'
import SetupTable from '@/components/setup-table/setup-table.vue'
import InstallMethod from '@/components/install-method/install-method.vue'
import Tips from '@/components/tips/tips.vue'
import FilterIpTips from '@/components/tips/filter-ip-tips'
import mixin from '@/components/tips/filter-ip-mixin'
import FilterDialog from '@/components/tips/filter-dialog.vue'
import ParserExcel from '../components/parser-excel.vue'
// import getTipsTemplate from '../config/tips-template'
import { tableConfig, tableManualConfig } from '../config/importTableConfig'
import { editConfig, editManualConfig } from '../config/editTableConfig'
import { addListener, removeListener } from 'resize-detector'
import { debounce, deepClone, isEmpty } from '@/common/util'
import { mapActions, mapMutations, mapGetters } from 'vuex'

export default {
  name: 'agent-import',
  components: {
    RightPanel,
    SetupTable,
    InstallMethod,
    ParserExcel,
    FilterDialog,
    Tips,
    FilterIpTips
  },
  mixins: [mixin],
  props: {
    tableData: {
      type: Array,
      default: () => []
    },
    // 是否是跨页全选（true时：tableData为标记删除的数据  false时：tableData为当前要编辑的数据）
    isSelectedAllPages: {
      type: Boolean,
      default: false
    },
    // 标记删除法的查询条件
    condition: {
      type: Object,
      default: () => ({})
    },
    // 操作类型
    type: {
      type: String,
      default: 'INSTALL_AGENT',
      validator(v) {
        return ['INSTALL_AGENT', 'REINSTALL_AGENT', 'RELOAD_AGENT', 'UPGRADE_AGENT', 'UNINSTALL_AGENT'].includes(v)
      }
    }
  },
  data() {
    return {
      isManual: false,
      // Excel 导入提示
      importTips: this.$t('excel导入提示'),
      // 右侧提示面板是否显示
      showRightPanel: false,
      // 总的数据备份，包括Excel导入数据
      tableDataBackup: [],
      // agent安装信息表格
      setupInfo: {
        header: tableConfig,
        data: []
      },
      // 监听界面滚动
      listenResize: null,
      isScroll: false,
      // 导入对话框
      importDialog: false,
      // 导入按钮加载状态
      isUploading: false,
      // 安装按钮加载状态
      loadingSetupBtn: false,
      // 是否显示安装按钮
      showSetupBtn: false,
      height: 0,
      // 安装信息加载状态
      loading: false,
      // 编辑head
      editTableHead: {
        editConfig: [],
        editManualConfig: []
      }
    }
  },
  computed: {
    // ...mapGetters(['bkBizList']),
    ...mapGetters('agent', ['apUrl', 'apList', 'cloudList']),
    // 导入按钮禁用状态
    disabledImport() {
      return !this.setupInfo.data.length
    },
    setupNum() {
      return this.setupInfo.data.length
    },
    // 是否支持虚拟滚动
    virtualScroll() {
      // 44 : 表格一行的高度
      return this.setupNum * 44 >= (this.height - this.surplusHeight)
    },
    // 虚拟滚动高度
    scrollHeight() {
      // 135： footer、表头和tips的高度
      return this.virtualScroll && this.height ? `${this.height - this.surplusHeight}px` : 'auto'
    },
    // 剩余高度
    surplusHeight() {
      let height = 135 // 以下条件可能并列出现
      // tips的行高
      height += 37
      // 全部过滤提示的行高
      if (this.filterList.length && this.showFilterTips) {
        height += 52
      }
      // 安装类型的行高
      if (this.showSetupBtn && !this.isEdit) {
        height += 52
      }
      return height
    },
    // 是否是编辑态
    isEdit() {
      return !!(this.tableData && this.tableData.length) || this.isSelectedAllPages
    },
    isNotAutoSelect() {
      return this.apList.length === 1
    },
    // 最小安装信息数目
    minItems() {
      if (this.isEdit) return 1
      return 0
    },
    // 安装按钮文案
    setupBtnText() {
      const textMap = {
        INSTALL_AGENT: this.$t('安装'),
        REINSTALL_AGENT: this.$t('重装'),
        RELOAD_AGENT: this.$t('重载配置'),
        UPGRADE_AGENT: this.$t('升级'),
        UNINSTALL_AGENT: this.$t('卸载')
      }
      return textMap[this.type]
    },
    // 编辑态额外参数
    extraParams() {
      if (this.isEdit) return ['bk_host_id', 'is_manual']
      return ['outer_ip', 'is_manual']
    },
    // 右侧面板提示类型
    hostType() {
      const isAgent = this.setupInfo.data.every(item => item
        && item.bk_cloud_id === window.PROJECT_CONFIG.DEFAULT_CLOUD)
      const isPagent = this.setupInfo.data.every(item => item
        && item.bk_cloud_id !== window.PROJECT_CONFIG.DEFAULT_CLOUD)
      if (isAgent) {
        return 'Agent'
      } if (isPagent) {
        return 'Pagent'
      }
      return 'mixed'
    },
    hostList() {
      const list = this.setupInfo.data.map((item) => {
        if (!item) {
          return {}
        }
        const cloudFind = this.cloudList.find(cloud => item.bk_cloud_id === cloud.bk_cloud_id)
        return {
          bk_cloud_id: item.bk_cloud_id,
          bk_cloud_name: cloudFind ? cloudFind.bk_cloud_name : '',
          inner_ip: item.inner_ip,
          ap_id: item.ap_id
        }
      })
      list.sort((a, b) => a.bk_cloud_id - b.bk_cloud_id)
      return list
    }
  },
  created() {
    switch (this.type) {
      case 'REINSTALL_AGENT':
        this.setNavTitle(this.$t('重装Agent'))
        break
      case 'RELOAD_AGENT':
        this.setNavTitle(this.$t('重载Agent配置'))
        break
    }
    this.resetTableHead()
  },
  mounted() {
    this.handleInit()
    this.listenResize = debounce(300, v => this.handleResize(v))
    addListener(this.$el, this.listenResize)
    this.height = this.$refs.setupContent.clientHeight
  },
  beforeDestroy() {
    this.setApUrl({ id: '' })
    removeListener(this.$el, this.listenResize)
  },
  methods: {
    ...mapMutations(['setNavTitle']),
    ...mapMutations('agent', ['setApList']),
    // ...mapActions(['getBkBizList']),
    ...mapActions('agent', ['getApList', 'getCloudList', 'installAgentJob', 'getHostList', 'setApUrl']),
    async handleInit() {
      this.loading = true
      const promiseList = []
      // ieod 环境：excel 导入去掉直连区域，编辑操作正常回写
      promiseList.push(this.getCloudList(this.isEdit ? {} : { RUN_VER: window.PROJECT_CONFIG.RUN_VER }))
      promiseList.push(this.getApList(!this.isEdit).then((res) => {
        this.setApUrl({ id: -1 })
        return res
      }))
      // if (!this.bkBizList.length) {
      //   promiseList.push(this.getBkBizList({ action: 'agent_view' }))
      // }
      await Promise.all(promiseList)
      if (this.isEdit) {
        await this.handleInitEditData()
      }
      this.$nextTick().then(() => {
        this.loading = false
      })
    },
    /**
     * 初始化编辑态数据
     */
    async handleInitEditData() {
      this.showSetupBtn = true
      let data = []
      const apDefault = this.isNotAutoSelect ? this.apList[0].id : ''
      if (this.isSelectedAllPages) {
        data = await this.getHostList(this.condition)
        data = data.list.map((item) => {
          const ap = this.isNotAutoSelect && item.ap_id === -1
            ? { ap_id: apDefault }
            : {}
          // 打平数据
          return Object.assign({}, item, item.identity_info, ap)
        })
      } else {
        data = JSON.parse(JSON.stringify(this.isNotAutoSelect
          ? this.tableData.map(item => (item.ap_id === -1 ? Object.assign(item, { ap_id: apDefault }) : item))
          : this.tableData))
      }
      // 将原始的数据备份；切换安装方式时，接入点的数据变更后的回退操作时需要用到
      this.tableDataBackup = data
      this.setupInfo.data = deepClone(data)
      this.isManual = this.setupInfo.data.some(item => item.is_manual)
      // 编辑态安装信息表格配置
      this.setupInfo.header = this.isManual ? this.editTableHead.editManualConfig : this.editTableHead.editConfig
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
    },
    /**
     * 监听界面滚动
     */
    handleResize() {
      // 60：三级导航的高度  52： 一级导航高度
      this.isScroll = this.$el.scrollHeight + 60 > this.$root.$el.clientHeight - 52
    },
    /**
     * 导入excel对话框
     */
    handleShowDialog() {
      this.importDialog = true
    },
    /**
     * 导入按钮点击事件
     */
    handleImport() {
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
      this.showSetupBtn = true
    },
    /**
     * 安装操作
     */
    async handleSetup() {
      const setupTableValidate = this.$refs.setupTable.validate()
      if (setupTableValidate) {
        this.loadingSetupBtn = true
        let hosts = this.$refs.setupTable.getData()
        hosts.forEach((item) => {
          if (isEmpty(item.login_ip)) {
            delete item.login_ip
          }
          if (isEmpty(item.bt_speed_limit)) {
            delete item.bt_speed_limit
          } else {
            item.bt_speed_limit = Number(item.bt_speed_limit)
          }
          item.peer_exchange_switch_for_agent += 0
        })
        // 安装agent或pagent时，需要设置初始的安装类型
        if (this.type === 'INSTALL_AGENT') {
          const isManual = { is_manual: this.isManual }
          hosts = hosts.map(item => Object.assign(item, isManual))
        }
        const params = {
          job_type: this.type,
          hosts
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
          // mixin: handleFilterIp 处理过滤IP信息
          this.handleFilterIp(res.data, this.type === 'INSTALL_AGENT')
        } else if (res.code === 3801013) {
          // Proxy过期或者未安装
          const data = this.$refs.setupTable.getTableData().map((item) => {
            const filterProxy = res.data.ip_filter.find((obj) => {
              const objId = `${obj.ip}${obj.bk_cloud_id}`
              const itemId = `${item.inner_ip}${item.bk_cloud_id}`
              return objId === itemId
            })
            if (filterProxy) {
              item.proxyStatus = filterProxy.exception
            }
            return item
          })
          this.$refs.setupTable.handleUpdateData(data)
          this.$refs.setupTable.validate() // 重新排序
        } else {
          const message = res.message ? res.message : this.$t('请求出错')
          this.$bkMessage({
            message,
            delay: 3000,
            theme: 'error'
          })
        }
      }
    },
    /**
     * 上一步
     */
    handleLastStep() {
      this.showFilterTips = false
      this.filterList.splice(0, this.filterList.length)
      this.setupInfo.data.splice(0, this.setupInfo.data.length)
      this.tableDataBackup.splice(0, this.tableDataBackup.length)
      this.showSetupBtn = false
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
    },
    /**
     * 取消安装Agent
     */
    handleCancel() {
      this.$router.push({ name: 'agentStatus' })
    },
    /**
     * 处理文件上传状态
     * @param {Boolean} loading true: 正在解析 false：解析完毕
     * @param {Array} v 解析数据
     */
    handleUploading(loading, v) {
      this.isUploading = loading
      if (!this.isUploading && v && v.length) {
        this.tableDataBackup = v
        this.setupInfo.data = deepClone(v)
      }
    },
    /**
     * 删除item
     */
    handleItemDelete(index) {
      this.setupInfo.data.splice(index, 1)
      this.tableDataBackup.splice(index, 1)
      if (!this.setupInfo.data.length) {
        this.handleLastStep()
      }
    },
    /**
     * 安装方式切换
     */
    installMethodHandle(isManual = false) {
      this.isManual = isManual
      const data = deepClone(this.$refs.setupTable.getData())
      let apList = deepClone(this.apList)
      if (this.isManual) {
        this.setupInfo.header = tableManualConfig
        // 手动安装无自动选择
        apList = apList.filter(item => item.id !== -1)
        // 自动接入点改默认接入点
        const apDefault = this.isNotAutoSelect
          ? this.apList[0]
          : this.apList.find(item => item.is_default)
        const apDefaultId = apDefault ? apDefault.id : ''
        // 将自动选择的行 替换为默认接入点
        data.forEach((item) => {
          if (item.ap_id === -1) {
            item.ap_id = apDefaultId
          }
        })
      } else {
        if (!apList.find(item => item.id === -1)) {
          apList.unshift({
            id: -1,
            name: this.$t('自动选择')
          })
        }
        this.setupInfo.header = tableConfig
        data.forEach((item, index) => {
          item.ap_id = this.tableDataBackup[index].ap_id
        })
      }
      this.setApList(apList)
      this.setupInfo.data = data
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
    },
    handleShowSetting() {
      this.$refs.setupTable.handleToggleSetting(true)
    },
    resetTableHead() {
      if (this.type === 'RELOAD_AGENT') {
        const reload = [
          'inner_ip',
          'bk_biz_id',
          'bk_cloud_id',
          'ap_id',
          'os_type',
          'peer_exchange_switch_for_agent',
          'bt_speed_limit'
        ]
        this.editTableHead.editConfig = editConfig.filter(item => reload.includes(item.prop) || item.type === 'operate')
          .map(item => Object.assign({ ...item }, { show: true }))
        this.editTableHead.editManualConfig = editManualConfig.map(item => Object.assign({ ...item }, { show: true }))
      } else {
        this.editTableHead.editConfig = editConfig
        this.editTableHead.editManualConfig = editManualConfig
      }
    },
    handleShowPanel() {
      this.setupInfo.data = deepClone(this.$refs.setupTable.getData())
      this.showRightPanel = true
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

.agent-setup {
  @mixin layout-flex row;
  &-left {
    flex: 1;
    height: calc(100vh - 120px);
    .left-footer {
      @mixin layout-flex row, center, center;
      .btn-wrapper {
        @mixin layout-flex row;
      }
      .install {
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
    }
  }
}
</style>

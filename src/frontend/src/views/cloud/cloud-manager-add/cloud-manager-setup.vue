<template>
  <article class="setup-cloud mt15 pb20">
    <div class="setup-cloud-left">
      <!--安装Proxy表单-->
      <section class="left-form">
        <!-- <tips :list="topTips" v-if="type === 'replace'" class="mb20"></tips> -->
        <tips class="mb20">
          <template #default>
            <ul>
              <template v-if="type === 'replace'">
                <li class="tips-content-item" v-for="(tip, index) in topTips" :key="index">
                  {{ tip }}
                </li>
              </template>
              <li class="tips-content-item">
                {{ $t('安装要求tips', { type: 'Proxy' }) }}
                <bk-link class="tips-link" theme="primary" @click="handleToggle">{{ $t('安装要求') }}</bk-link>
                {{ $t('表格展示设置tips') }}
                <bk-link class="tips-link" theme="primary" @click="handleShowSetting">{{ $t('表格展示设置') }}</bk-link>
              </li>
            </ul>
          </template>
        </tips>
        <bk-form :label-width="marginLeft" :model="formData" :rules="rules" ref="form">
          <install-method :is-manual="isManual" @change="installMethodHandle"></install-method>
          <bk-form-item :label="$t('安装信息')">
            <filter-ip-tips
              class="mb15 filter-tips"
              v-if="filterList.length && showFilterTips"
              @click="handleShowDetail">
            </filter-ip-tips>
            <setup-table
              :class="{ 'cloud-setup-table': isManual }"
              :local-mark="`proxy_setup`"
              @change="handleSetupTableChange"
              :setup-info="formData.bkCloudSetupInfo"
              :key="net.active"
              ref="setupTable">
            </setup-table>
          </bk-form-item>
          <bk-form-item error-display-type="normal" :label="$t('密码安全')" required>
            <bk-radio-group v-model="formData.retention" class="content-basic">
              <bk-radio :value="1">{{ $t('保存1天') }}</bk-radio>
              <bk-radio class="ml35" :value="-1">{{ $t('长期保存') }}</bk-radio>
            </bk-radio-group>
          </bk-form-item>
          <bk-form-item error-display-type="normal" :label="$t('操作系统')" property="osType" required>
            <bk-select
              class="content-basic"
              :placeholder="$t('请选择')"
              v-model="formData.osType"
              :clearable="false"
              v-bk-tooltips.right="$t('仅支持Linux64位操作系统')"
              disabled>
              <bk-option id="LINUX" name="Linux(64位)"></bk-option>
            </bk-select>
          </bk-form-item>
          <template v-if="!isManual">
            <bk-form-item error-display-type="normal" :label="$t('登录端口')" property="port" required>
              <bk-input class="content-basic" :placeholder="$t('请输入')" v-model="formData.port"></bk-input>
            </bk-form-item>
            <bk-form-item error-display-type="normal" :label="$t('登录账号')" property="account" required>
              <bk-input class="content-basic" :placeholder="$t('请选择')" v-model="formData.account"></bk-input>
            </bk-form-item>
          </template>
          <bk-form-item error-display-type="normal" :label="$t('归属业务')" property="bkBizId" required>
            <bk-biz-select
              v-model="formData.bkBizId"
              class="content-basic"
              :placeholder="$t('待选择')"
              :show-select-all="false"
              :multiple="false"
              :auto-update-storage="false">
            </bk-biz-select>
          </bk-form-item>
        </bk-form>
      </section>
      <!--操作按钮-->
      <section class="left-footer">
        <bk-button
          theme="primary"
          ext-cls="nodeman-primary-btn"
          :style="{ marginLeft: `${marginLeft}px` }"
          :loading="loadingSetup"
          @click="handleSetup">
          {{ saveBtnText }}
        </bk-button>
        <bk-button class="nodeman-cancel-btn ml5" @click="handleCancel">{{ $t('取消') }}</bk-button>
      </section>
    </div>
    <!--右侧提示栏-->
    <div class="setup-cloud-right" :class="{ 'right-panel': showRightPanel }">
      <right-panel v-model="showRightPanel" host-type="Proxy" :host-list="hostList"></right-panel>
      <!-- <right-panel v-model="showRightPanel" :list="tipsList" :tips="tips"></right-panel> -->
    </div>
    <!--过滤ip信息-->
    <template>
      <filter-dialog v-model="showFilterDialog" :list="filterList" :title="$t('忽略详情')"></filter-dialog>
    </template>
  </article>
</template>
<script>
import SetupTable from '@/components/setup-table/setup-table.vue'
import InstallMethod from '@/components/install-method/install-method.vue'
import RightPanel from '@/components/tips/right-panel-tips.vue'
import Tips from '@/components/tips/tips.vue'
import FilterIpTips from '@/components/tips/filter-ip-tips'
import mixin from '@/components/tips/filter-ip-mixin'
import formLabelMixin from '@/common/form-label-mixin'
import FilterDialog from '@/components/tips/filter-dialog.vue'
// import getTemplate from '../config/tips-template'
import { mapActions, mapMutations, mapGetters } from 'vuex'
import { setupInfo, setupManualInfo } from '../config/netTableConfig'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import CloudState from '@/store/modules/cloud'
import { defaultPort } from '@/config/config'

export default {
  name: 'cloud-manager-setup',
  components: {
    SetupTable,
    InstallMethod,
    RightPanel,
    Tips,
    FilterIpTips,
    FilterDialog
  },
  mixins: [mixin, formLabelMixin],
  props: {
    id: {
      type: [Number, String],
      required: true
    },
    innerIp: {
      type: String,
      default: ''
    },
    // 操作类型 创建、替换
    type: {
      type: String,
      default: 'create',
      validator(v) {
        return ['create', 'replace'].includes(v)
      }
    },
    // type 为 replace 时的主机ID
    replaceHostId: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      // 安装方式 目前跟type冲突，待处理
      isManual: false,
      // 表单数据
      formData: {},
      net: {
        list: [
          {
            name: this.$t('简单网络'),
            id: 'simple'
          },
          {
            name: this.$t('复杂网络'),
            id: 'complex'
          }
        ],
        active: 'simple'
      },
      // 表单校验
      rules: {
        osType: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        port: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            message: this.$t('端口范围', { range: '0-65535' }),
            trigger: 'blur',
            validator(v) {
              const reg = /^([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{4}|65[0-4]\d{2}|655[0-2]\d|6553[0-5])$/
              return reg.test(v)
            }
          }
        ],
        account: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        bkBizId: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ]
      },
      setupConfig: {
        header: setupInfo,
        data: []
      },
      // 是否显示右侧提示栏
      showRightPanel: false,
      // 内网IP
      innerIps: '',
      // 右侧面板提示
      tips: this.$t('安装要求提示'),
      // 顶部提示
      topTips: [
        this.$t('替换Proxy提示一'),
        this.$t('替换Proxy提示二')
      ],
      // 安装proxy加载状态
      loadingSetup: false,
      // 接入点
      apId: 0,
      marginLeft: 108,
      cloudName: ''
    }
  },
  computed: {
    ...mapGetters('cloud', ['apList', 'apUrl']),
    // 内部ip变化时填充模板内容
    // tipsList () {
    //     const apFilter = this.apId === '-1' ? this.apList.filter(item => item.id !== this.apId) : this.apList.filter(item => item.id === this.apId)
    //     let gesServerIps = ''
    //     if (apFilter.length) {
    //         gesServerIps = apFilter.map(ap => ap.servers.map(item => item.outer_ip).join(', ')).join(', ')
    //     }
    //     return getTemplate(this.apUrl, this.innerIps, this.formData.port, gesServerIps)
    // },
    // 保存按钮文案
    saveBtnText() {
      const textMap = {
        create: this.$t('安装'),
        replace: this.$t('替换')
      }
      return textMap[this.type]
    },
    hostList() {
      return this.setupConfig.data.map(item => ({
        bk_cloud_id: Number(this.id),
        bk_cloud_name: this.cloudName,
        ap_id: this.apId,
        inner_ip: item ? item.inner_ip : ''
      }))
    }
  },
  created() {
    this.handleInit()
  },
  mounted() {
    this.marginLeft = this.initLabelWidth(this.$refs.form)
    this.initRetryData()
  },
  methods: {
    ...mapMutations(['setNavTitle']),
    ...mapActions('cloud', ['setupProxy', 'getCloudDetail', 'getApList', 'setApUrl']),
    async handleInit() {
      switch (this.type) {
        case 'create':
          this.setNavTitle(this.$t('安装Proxy'))
          break
        case 'replace':
          this.setNavTitle(this.$t('替换Proxy', { ip: this.innerIp || this.id }))
          break
      }
      this.initForm()
      await this.getCloudBizList() // 拿到apId之后才能进行下一步
      if (!this.apList.length) {
        await this.getApList()
      }
      this.setApUrl({ id: this.apId })
    },
    initForm() {
      this.formData = {
        bkCloudSetupInfo: this.setupConfig,
        retention: -1,
        osType: 'LINUX',
        port: defaultPort,
        account: 'root',
        bkBizId: ''
      }
    },
    /**
     * 重试回填数据
     */
    initRetryData() {
      const data = this.$route.params.table
      if (data) {
        let bizId
        const table = []
        this.isManual = data.some(item => item.is_manual)
        data.forEach((item) => {
          bizId = item.bk_biz_id
          table.push({
            inner_ip: item.inner_ip,
            login_ip: item.login_ip,
            outer_ip: item.outer_ip,
            auth_type: item.auth_type,
            prove: true,
            retention: item.retention || -1
          })
        })
        this.setupConfig.data = table
        this.formData.bkBizId = bizId
        this.installMethodHandle(this.isManual)
      }
    },
    /**
     * 获取归属业务
     */
    async getCloudBizList() {
      if (!this.id) return
      const data = await this.getCloudDetail(this.id)
      this.apId = data.apId
      this.cloudName = data.bkCloudName
    },
    /**
     * 安装
     */
    handleSetup() {
      Promise.all([
        this.$refs.setupTable.validate(),
        this.$refs.form.validate()
      ]).then((result) => {
        const validate = result.every(item => !!item)
        if (validate) {
          const data = this.getFormData()
          const type = this.type === 'create' ? 'INSTALL_PROXY' : 'REPLACE_PROXY'
          this.handleCreateOrReplace(data, type)
        }
      })
    },
    /**
     * 获取表单数据
     */
    getFormData() {
      // 无替换操作 - 故当为手动安装时，直接把-1的接入点改为默认接入点
      let { apId } = this
      if (this.isManual && this.apId === -1) {
        const ap = this.apList.find(item => item.is_default)
        apId = ap ? ap.id : ''
      }
      return this.$refs.setupTable.getData().map((item) => {
        const data = {
          ...item,
          retention: this.formData.retention,
          port: this.formData.port,
          account: this.formData.account,
          os_type: this.formData.osType,
          bk_biz_id: this.formData.bkBizId,
          bk_cloud_id: this.id,
          ap_id: apId,
          is_manual: this.isManual
        }
        if (!data.login_ip) {
          delete data.login_ip
        }
        if (!data.bt_speed_limit) {
          delete data.bt_speed_limit
        } else {
          data.bt_speed_limit = Number(data.bt_speed_limit)
        }
        data.peer_exchange_switch_for_agent += 0
        return data
      })
    },
    /**
     * 创建和替换Proxy
     */
    async handleCreateOrReplace(data, type = 'INSTALL_PROXY') {
      this.loadingSetup = true
      const params = {
        job_type: type,
        hosts: data
      }
      if (type === 'REPLACE_PROXY') {
        params.replace_host_id = this.replaceHostId
      }
      const res = await this.setupProxy({
        params,
        config: {
          needRes: true,
          globalError: false
        }
      })
      this.loadingSetup = false
      if (!res) return

      if (res.result || res.code === 3801018) {
        // 部分忽略
        // mixin: handleFilterIp 处理过滤IP信息
        this.handleFilterIp(res.data)
      } else {
        const message = res.message ? res.message : this.$t('请求出错')
        this.$bkMessage({
          message,
          delay: 3000,
          theme: 'error'
        })
      }
    },
    /**
     * 取消
     */
    handleCancel() {
      this.$router.push({
        name: 'cloudManager'
      })
    },
    /**
     * 监听内部IP属性变化
     */
    handleSetupTableChange(value, item) {
      if (item.prop === 'inner_ip') {
        const tableData = this.$refs.setupTable.getTableData()
        this.innerIps = tableData.map(item => item.inner_ip).join(', ')
      }
    },
    /**
     * 安装方式切换
     */
    installMethodHandle(isManual = false) {
      this.isManual = isManual
      if (this.isManual) {
        this.setupConfig.header = setupManualInfo
      } else {
        this.setupConfig.header = setupInfo
      }
      this.$refs.setupTable.handleInit()
      this.$refs.setupTable.handleScroll()
    },
    handleToggle() {
      this.showRightPanel = true
      this.setupConfig.data = this.getFormData()
    },
    handleShowSetting() {
      this.$refs.setupTable.handleToggleSetting(true)
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

.setup-cloud {
  @mixin layout-flex row;
  &-left {
    flex: 1;
    .left-form {
      .cloud-setup-table {
        max-width: 822px;
      }
      .content-basic {
        width: 480px;
      }
      .net-btn {
        width: 210px;
      }
      .filter-tips {
        margin-top: 8px;
      }
    }
    .left-footer {
      margin-top: 30px;
    }
  }
}
</style>

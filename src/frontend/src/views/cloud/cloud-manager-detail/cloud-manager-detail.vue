<template>
  <article class="cloud-manager-detail">
    <!--详情左侧面板-->
    <section class="detail-left">
      <!--搜索云区域别名-->
      <div class="detail-left-search">
        <bk-input :placeholder="$t('搜索云区域名称')"
                  right-icon="bk-icon icon-search"
                  v-model="bkCloudName"
                  @change="handleValueChange">
        </bk-input>
      </div>
      <!--列表-->
      <div class="detail-left-list" ref="leftList" v-bkloading="{ isLoading: loading }">
        <ul>
          <auth-component
            class="list-auth-wrapper"
            v-for="(item, index) in area.data"
            :key="index"
            tag="li"
            :title="item.bkCloudName"
            :auth="{
              permission: item.view,
              apply_info: [{
                action: 'cloud_view',
                instance_id: item.bkCloudId,
                instance_name: item.bkCloudName
              }]
            }">
            <template slot-scope="{ disabled }">
              <div
                class="list-item"
                :class="{ 'is-selected': item.bkCloudId === area.active, 'auth-disabled': disabled }"
                @click="handleAreaChange(item)">
                <span class="list-item-name">{{ item.bkCloudName }}</span>
                <span v-bk-tooltips="{
                  content: $t('未安装Proxy'),
                  placement: 'top',
                  delay: [200, 0]
                }" v-if="!item.proxyCount" class="list-item-icon nodeman-icon nc-reduce-fill">
                </span>
                <span v-bk-tooltips="{
                  content: $t('存在异常Proxy'),
                  placement: 'top',
                  delay: [200, 0]
                }" v-else-if="item.exception === 'abnormal'" class="list-item-icon nodeman-icon nc-danger-fill-2">
                </span>
              </div>
            </template>
          </auth-component>
          <li class="list-item loading" v-show="isListLoading">
            <loading-icon></loading-icon>
            <span class="loading-name">{{ $t('加载中') }}</span>
          </li>
        </ul>
      </div>
    </section>
    <!--右侧表格-->
    <section class="detail-right">
      <!--自定义三级导航-->
      <div class="detail-right-title mb20">
        <i class="title-icon nodeman-icon nc-back-left" @click="handleRouteBack"></i>
        <span class="title-name">{{ navTitle }}</span>
      </div>
      <!--表格-->
      <div class="detail-right-content">
        <auth-component
          tag="div"
          :auth="{
            permission: !!proxyOperateList.length,
            apply_info: [{ action: 'proxy_operate' }]
          }">
          <template slot-scope="{ disabled }">
            <bk-button theme="primary"
                       class="nodeman-primary-btn"
                       ext-cls="content-btn"
                       :disabled="disabled"
                       @click="handleInstallProxy">
              {{ $t('安装Proxy') }}
            </bk-button>
          </template>
        </auth-component>
        <div v-bkloading="{ isLoading: loadingProxy }">
          <bk-table :class="`head-customize-table ${ fontSize }`" :data="proxyData" :span-method="colspanHandle">
            <bk-table-column label="Proxy IP" show-overflow-tooltip>
              <template #default="{ row }">
                <bk-button text @click="handleShowDetail(row)" class="row-btn">{{ row.inner_ip }}</bk-button>
              </template>
            </bk-table-column>
            <bk-table-column
              :label="$t('对外通讯IP')"
              v-if="filter['outer_ip'].mockChecked"
              :render-header="renderTipHeader">
              <template #default="{ row }">
                <span>{{ row.outer_ip | emptyDataFilter }}</span>
              </template>
            </bk-table-column>
            <bk-table-column
              key="login_ip"
              :label="$t('登录IP')"
              prop="login_ip"
              v-if="filter['login_ip'].mockChecked">
              <template #default="{ row }">
                {{ row.login_ip || emptyDataFilter }}
              </template>
            </bk-table-column>
            <bk-table-column
              :label="$t('归属业务')"
              prop="bk_biz_name"
              v-if="filter['bk_biz_name'].mockChecked" show-overflow-tooltip>
              <template #default="{ row }">
                <span>{{ row.bk_biz_name | emptyDataFilter }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('Proxy状态')" prop="status" v-if="filter['proxy_status'].mockChecked">
              <template #default="{ row }">
                <div class="col-status" v-if="statusMap[row.status]">
                  <span :class="'status-mark status-' + row.status"></span>
                  <span>{{ statusMap[row.status] }}</span>
                </div>
                <div class="col-status" v-else>
                  <span class="status-mark status-unknown"></span>
                  <span>{{ $t('未知') }}</span>
                </div>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('密码密钥')" prop="re_certification" v-if="filter['re_certification'].mockChecked">
              <template #default="{ row }">
                <span :class="['tag-switch', { 'tag-enable': !row.re_certification }]">
                  {{ row.re_certification ? $t('过期') : $t('有效') }}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('Proxy版本')" prop="version" v-if="filter['proxy_version'].mockChecked">
              <template #default="{ row }">
                <span>{{ row.version | emptyDataFilter }}</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('Agent数量')" prop="pagent_count" v-if="filter['pagent_count'].mockChecked">
              <template #default="{ row }">
                <span
                  class="link-pointer"
                  v-if="row.pagent_count"
                  @click="handleFilterAgent">
                  {{ row.pagent_count }}
                </span>
                <span v-else>0</span>
              </template>
            </bk-table-column>
            <bk-table-column :label="$t('安装方式')" prop="is_manual" v-if="filter['is_manual'].mockChecked">
              <template #default="{ row }">
                {{ row.is_manual ? $t('手动') : $t('远程') }}
              </template>
            </bk-table-column>
            <bk-table-column
              key="bt"
              prop="peer_exchange_switch_for_agent"
              width="110"
              :label="$t('BT传输加速')"
              v-if="filter['bt'].mockChecked">
              <template #default="{ row }">
                <span :class="['tag-switch', { 'tag-enable': row.peer_exchange_switch_for_agent }]">
                  {{ row.peer_exchange_switch_for_agent ? $t('启用') : $t('停用')}}
                </span>
              </template>
            </bk-table-column>
            <bk-table-column
              key="speedLimit"
              prop="bt_speed_limit"
              width="130"
              align="right"
              :label="`${this.$t('传输限速')}(MB/s)`"
              v-if="filter['speedLimit'].mockChecked">
              <template #default="{ row }">
                {{ row.bt_speed_limit || '--' }}
              </template>
            </bk-table-column>
            <bk-table-column
              v-if="filter['speedLimit'].mockChecked"
              min-width="20"
              :resizable="false">
            </bk-table-column>
            <bk-table-column
              :label="$t('安装时间')"
              width="200"
              prop="created_at"
              :resizable="false"
              v-if="filter['created_at'].mockChecked">
            </bk-table-column>
            <bk-table-column prop="colspaOpera" :label="$t('操作')" width="148" :resizable="false" fixed="right">
              <template #default="{ row }">
                <div class="col-operate">
                  <auth-component
                    tag="div"
                    v-if="['PENDING', 'RUNNING'].includes(row.job_result.status)"
                    :auth="{
                      permission: !proxyOperateList.includes(row.bk_biz_id),
                      apply_info: [{
                        action: 'proxy_operate',
                        instance_id: row.bk_biz_id,
                        instance_name: row.bk_biz_name
                      }]
                    }">
                    <template #default="{ disabled }">
                      <bk-button :disabled="disabled" text @click="handleGotoLog(row)">
                        <loading-icon vertical="text-bottom"></loading-icon>
                        <span
                          class="loading-name"
                          v-bk-tooltips="$t('查看任务详情')">
                          {{ row.job_result.current_step || $t('正在运行') }}
                        </span>
                      </bk-button>
                    </template>
                  </auth-component>
                  <div v-else>
                    <auth-component
                      :auth="{
                        permission: !proxyOperateList.includes(row.bk_biz_id),
                        apply_info: [{
                          action: 'proxy_operate',
                          instance_id: row.bk_biz_id,
                          instance_name: row.bk_biz_name
                        }]
                      }">
                      <template #default="{ disabled }">
                        <bk-popover
                          placement="bottom"
                          :delay="400"
                          :width="language === 'zh' ? 160 : 370"
                          :disabled="!row.re_certification || disabled"
                          :content="$t('认证资料过期不可操作', { type: $t('重装') })">
                          <bk-button
                            theme="primary"
                            text
                            :disabled="row.re_certification || disabled"
                            @click="handleReinstall(row)"
                            ext-cls="row-btn">
                            {{ $t('重装') }}
                          </bk-button>
                        </bk-popover>
                        <bk-button
                          theme="primary"
                          text
                          ext-cls="row-btn"
                          :disabled="disabled"
                          @click="handleEdit(row)">
                          {{ $t('编辑') }}
                        </bk-button>
                        <bk-popover :ref="row['bk_host_id']"
                                    theme="light agent-operate"
                                    trigger="click"
                                    :arrow="false"
                                    offset="30, 5"
                                    placement="bottom"
                                    :disabled="disabled">
                          <bk-button
                            theme="primary"
                            :disabled="disabled"
                            text
                            ext-cls="row-btn">
                            {{ $t('更多') }}
                          </bk-button>
                          <template #content>
                            <ul class="dropdown-list">
                              <li
                                v-for="item in operate"
                                :key="item.id"
                                :class="['list-item', fontSize , { 'disabled': getDisabledStatus(item.id, row) }] "
                                v-show="getOperateShow(row, item)"
                                v-bk-tooltips="{
                                  width: language === 'zh' ? 160 : 370,
                                  disabled: (item.id !== 'uninstall' && item.id !== 'reload') || !row.re_certification,
                                  content: $t('认证资料过期不可操作', { type: $t('卸载') })
                                }"
                                @click="handleTriggerClick(item.id, row)">
                                {{ item.name }}
                              </li>
                            </ul>
                          </template>
                        </bk-popover>
                      </template>
                    </auth-component>
                  </div>
                </div>
              </template>
            </bk-table-column>
            <!--自定义字段显示列-->
            <bk-table-column
              key="setting"
              prop="colspaSetting"
              :render-header="renderHeader"
              width="42"
              :resizable="false"
              fixed="right">
            </bk-table-column>
          </bk-table>
        </div>
      </div>
    </section>
    <!--侧栏详情-->
    <section>
      <bk-sideslider :is-show.sync="sideslider.show" :width="sideslider.width" quick-close @hidden="handleSidesHidden">
        <template #header>{{ sideslider.title }}</template>
        <template #content>
          <sideslider-content-edit
            :basic="basicInfo"
            v-if="sideslider.isEdit"
            @close="handleClose"
            @change="handleSideDataChange">
          </sideslider-content-edit>
          <sideslider-content :basic="basicInfo" v-else></sideslider-content>
        </template>
      </bk-sideslider>
    </section>
  </article>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
import { debounce, isEmpty } from '@/common/util'
import ColumnSetting from '@/components/column-setting/column-setting'
import SidesliderContent from '../components/sideslider-content.vue'
import SidesliderContentEdit from '../components/sideslider-content-edit.vue'
import pollMixin from '@/common/poll-mixin'
import routerBackMixin from '@/common/router-back-mixin'
import { STORAGE_KEY_COL } from '@/config/storage-key'

export default {
  name: 'cloud-manager-detail',
  components: {
    SidesliderContent,
    SidesliderContentEdit
  },
  filters: {
    emptyDataFilter(v) {
      return !isEmpty(v) ? v : '--'
    }
  },
  mixins: [pollMixin, routerBackMixin],
  props: {
    id: {
      type: [Number, String],
      default: 0
    },
    // 是否是首次加载
    isFirst: {
      type: Boolean,
      default: true
    },
    search: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // 别名
      bkCloudName: this.search,
      // 别名搜索防抖
      handleValueChange() {},
      // proxy表格数据
      proxyData: [],
      // 区域列表
      area: {
        list: [],
        data: [],
        isAll: false, // 标志是否加载完毕数据
        lastOffset: -1,
        offset: 0, // 上一次滚动的位置
        active: Number(this.id) // 当前选中的云区域
      },
      loading: false,
      // 左侧列表加载状态
      isListLoading: false,
      // Proxy操作
      operate: [
        {
          id: 'uninstall',
          name: this.$t('卸载'),
          disabled: false,
          show: true
        },
        {
          id: 'remove',
          name: this.$t('移除'),
          disabled: false,
          show: true
        },
        {
          id: 'reboot',
          name: this.$t('重启'),
          disabled: false,
          show: true
        },
        {
          id: 'reload',
          name: this.$t('重载配置'),
          disabled: false,
          show: true
        },
        {
          id: 'upgrade',
          name: this.$t('升级'),
          disabled: false,
          show: true
        },
        {
          id: 'log',
          name: this.$t('最新执行日志'),
          disabled: false,
          show: true
        }
      ],
      // 状态map
      statusMap: {
        running: this.$t('正常'),
        terminated: this.$t('异常'),
        unknown: this.$t('未知')
      },
      // 侧滑
      sideslider: {
        show: false,
        title: '',
        isEdit: false,
        width: 780
      },
      // Proxy列表加载
      loadingProxy: false,
      basicInfo: {},
      firstLoad: this.isFirst,
      // 列表字段显示配置
      filter: {
        inner_ip: {
          checked: true,
          disabled: true,
          mockChecked: true,
          name: 'Proxy IP',
          id: 'inner_ip'
        },
        proxy_version: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('Proxy版本'),
          id: 'version'
        },
        outer_ip: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('对外通讯IP'),
          id: 'outer_ip'
        },
        login_ip: {
          checked: false,
          disabled: false,
          mockChecked: true,
          name: this.$t('登录IP'),
          id: 'login_ip'
        },
        pagent_count: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('Agent数量'),
          id: 'pagent_count'
        },
        bk_biz_name: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('归属业务'),
          id: 'bk_biz_name'
        },
        is_manual: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('安装方式'),
          id: 'is_manual'
        },
        proxy_status: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('Proxy状态'),
          id: 'proxy_status'
        },
        // inner_ip bk_biz_name status re_certification version pagent_count
        created_at: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('安装时间'),
          id: 'created_at'
        },
        re_certification: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('密码密钥'),
          id: 're_certification'
        },
        bt: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('BT传输加速'),
          id: 'peer_exchange_switch_for_agent'
        },
        speedLimit: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('传输限速'),
          id: 'bt_speed_limit'
        }
      },
      localMark: '_proxy'
    }
  },
  computed: {
    ...mapGetters(['bkBizList', 'selectedBiz', 'fontSize', 'permissionSwitch', 'language']),
    ...mapGetters('cloud', ['cloudList', 'authority']),
    // 导航title
    navTitle() {
      const cloudArea = this.area.list.find(item => item.bkCloudId === this.area.active)
      return cloudArea ? cloudArea.bkCloudName : this.$t('未选中云区域')
    },
    proxyOperateList() {
      return this.authority.proxy_operate || []
    }
  },
  watch: {
    id(newValue, oldValue) {
      if (!isEmpty(newValue) && parseInt(newValue, 10) !== parseInt(oldValue, 10)) {
        this.area.active = parseInt(newValue, 10)
        this.handleInit()
      }
    }
  },
  created() {
    this.handleInit()
  },
  mounted() {
    this.handleValueChange = debounce(300, this.handleSearch)
  },
  methods: {
    ...mapActions('agent', ['getAreaList']),
    ...mapActions('cloud', ['setupProxy', 'getCloudList', 'getCloudProxyList', 'operateJob', 'removeHost']),
    async handleInit() {
      this.initCustomColStatus()
      this.handleGetCloudList()
      this.handleGetProxyList()
    },
    initCustomColStatus() {
      const data = this.handleGetStorage()
      if (data && Object.keys(data).length) {
        Object.keys(this.filter).forEach((key) => {
          this.filter[key].mockChecked = !!data[key]
          this.filter[key].checked = !!data[key]
        })
      }
    },
    /**
     * 搜索云区域别名
     */
    handleSearch() {
      this.area.data = this.bkCloudName.length === 0
        ? this.area.list
        : this.area.list.filter((item) => {
          const originName = item.bkCloudName.toLocaleLowerCase()
          const currentName = this.bkCloudName.toLocaleLowerCase()
          return originName.indexOf(currentName) > -1
        })
    },
    /**
     * 获取云区域列表
     */
    async handleGetCloudList() {
      this.loading = true
      const params = {}
      if (this.selectedBiz.length && this.selectedBiz.length !== this.bkBizList.length) {
        params.bk_biz_scope = this.selectedBiz.join(',')
      }
      let list = []
      if (!this.firstLoad) {
        list = this.cloudList
      } else {
        list = await this.getCloudList(params)
      }
      this.area.list = this.permissionSwitch ? list.filter(item => item.view) : list
      this.area.data = this.area.list
      if (this.firstLoad) {
        this.$nextTick(() => {
          this.scrollToView()
        })
      }
      this.firstLoad = false
      this.loading = false
      this.handleSearch()
    },
    /**
     * 获取云区域Proxy列表
     */
    async handleGetProxyList(loading = true) {
      this.loadingProxy = loading
      this.proxyData = await this.getCloudProxyList({ bk_cloud_id: this.area.active })
      this.runingQueue = []
      const isRunning = this.proxyData.some(item => item.job_result && item.job_result.status === 'RUNNING')
      if (isRunning) {
        this.runingQueue.push(this.area.active)
      }
      this.loadingProxy = false
    },
    /**
     * 处理轮询的数据
     */
    async handlePollData() {
      await this.handleGetProxyList(false)
    },
    /**
     * 获取区域列表信息
     */
    async handleGetAreaList() {
      if (this.area.lastOffset === this.area.offset) return
      this.isListLoading = true
      const list = await this.getAreaList({
        offset: this.area.offset,
        listLength: this.area.list.length
      })
      if (list.length) {
        this.area.list.push(...list)
        this.area.lastOffset = this.area.offset
        this.area.offset = list[list.length - 1].id
      } else {
        this.area.isAll = true
      }
      this.isListLoading = false
    },
    /**
     * 返回上一层路由
     */
    handleRouteBack() {
      this.routerBack()
    },
    /**
     * 新增Proxy
     */
    handleInstallProxy() {
      this.$router.push({
        name: 'setupCloudManager',
        params: {
          type: 'create',
          id: this.id
        }
      })
    },
    /**
     * 重装
     * @param {Object} row 当前行
     */
    async handleReinstall(row) {
      const reinstall = async (row) => {
        this.loadingProxy = true
        const result = await this.operateJob({
          job_type: 'REINSTALL_PROXY',
          bk_host_id: [row.bk_host_id]
        })
        this.loadingProxy = false
        if (result.job_id) {
          this.$router.push({ name: 'taskDetail', params: { taskId: result.job_id } })
        }
      }
      this.$bkInfo({
        title: this.$t('确定重装选择的主机'),
        confirmFn: () => {
          reinstall(row)
        }
      })
    },
    async handleReload(row) {
      this.loadingProxy = true
      const paramKey = [
        'ap_id', 'bk_biz_id', 'bk_cloud_id', 'inner_ip', 'outer_ip',
        'is_manual', 'peer_exchange_switch_for_agent', 'bk_host_id'
      ]
      const paramExtraKey = ['bt_speed_limit', 'login_ip', 'data_ip']
      const copyRow = Object.keys(row).reduce((obj, item) => {
        if (paramKey.includes(item)) {
          obj[item] = item === 'peer_exchange_switch_for_agent' ? row[item] + 0 : row[item]
        }
        if (paramExtraKey.includes(item) && row[item]) {
          obj[item] = row[item]
        }
        return obj
      }, { os_type: 'LINUX' })
      const res = await this.setupProxy({ params: { job_type: 'RELOAD_PROXY', hosts: [copyRow] } })
      this.loadingProxy = false
      // eslint-disable-next-line @typescript-eslint/prefer-optional-chain
      if (res && res.job_id) {
        this.$router.push({ name: 'taskDetail', params: { taskId: res.job_id } })
      }
    },
    handleAreaChange(item) {
      if (this.area.active === item.bkCloudId) return
      this.$router.replace({
        name: 'cloudManagerDetail',
        params: {
          id: item.bkCloudId,
          isFirst: false,
          search: this.bkCloudName
        }
      })
    },
    /**
     * 显示Proxy详情
     * @param { Object } row 当前行
     */
    handleShowDetail(row) {
      this.setSideslider({
        show: true,
        title: row.inner_ip,
        isEdit: false,
        width: 780
      }, row)
    },
    /**
     * 编辑Proxy
     */
    handleEdit(row) {
      this.setSideslider({
        show: true,
        title: this.$t('修改登录信息'),
        isEdit: true,
        width: 600
      }, row)
    },
    setSideslider(data, row) {
      this.sideslider = data
      this.$set(this, 'basicInfo', row)
    },
    /**
     * 替换Proxy
     * @param {Object} row 当前行
     */
    handleReplace(row) {
      this.$router.push({
        name: 'setupCloudManager',
        params: {
          id: row.bk_cloud_id,
          innerIp: row.inner_ip,
          replaceHostId: row.bk_host_id,
          type: 'replace'
        }
      })
    },
    /**
     * 更多操作事件
     * @param {String} id
     */
    async handleTriggerClick(id, row) {
      const disabled = this.getDisabledStatus(id, row)
      if (disabled) return
      this.$refs[row.bk_host_id] && this.$refs[row.bk_host_id].instance.hide()
      switch (id) {
        case 'replace':
          this.handleReplace(row)
          break
        case 'uninstall':
          this.$bkInfo({
            title: this.$t('确定卸载该主机'),
            confirmFn: () => {
              this.handleOperateHost(row, 'UNINSTALL_PROXY')
            }
          })
          break
        case 'remove':
          this.$bkInfo({
            title: this.$t('确定移除选择的主机'),
            confirmFn: () => {
              this.handleRemoveHost(row)
            }
          })
          break
        case 'reboot':
          this.$bkInfo({
            title: this.$t('确定重启选择的主机'),
            confirmFn: () => {
              this.handleOperateHost(row, 'RESTART_PROXY')
            }
          })
          break
        case 'reload':
          this.$bkInfo({
            title: this.$t('确定重载选择的主机配置'),
            confirmFn: () => {
              this.handleReload(row)
            }
          })
          break
        case 'upgrade':
          this.$bkInfo({
            title: this.$t('确定升级选择的主机'),
            confirmFn: () => {
              this.handleOperateHost(row, 'UPGRADE_PROXY')
            }
          })
          break
        case 'log':
          this.$router.push({
            name: 'taskLog',
            params: {
              instanceId: row.job_result.instance_id,
              taskId: row.job_result.job_id
            }
          })
      }
    },
    /**
     * 主机操作：升级主机、卸载主机、重启主机
     */
    async handleOperateHost(row, type) {
      this.loadingProxy = true
      const result = await this.operateJob({
        job_type: type,
        bk_host_id: [row.bk_host_id]
      })
      this.loadingProxy = false
      if (result.job_id) {
        this.$router.push({ name: 'taskDetail', params: { taskId: result.job_id } })
      }
    },
    /**
     * 移除主机
     */
    async handleRemoveHost(row) {
      this.loadingProxy = true
      const data = await this.removeHost({
        is_proxy: true,
        bk_host_id: [row.bk_host_id]
      })
      this.loadingProxy = false
      if (data) {
        this.handleGetProxyList()
      }
    },
    /**
     * 获取下线操作的禁用状态
     */
    getDisabledStatus(id, row) {
      const ids = ['uninstall', 'remove']
      const isExpired = id === 'uninstall' && row.re_certification
      const exitNormalHost = this.proxyData.filter((item) => {
        const status = item.status.toLowerCase()
        return item.bk_host_id !== row.bk_host_id && status === 'normal'
      }).length
      return isExpired || (row.pagent_count !== 0 && ids.includes(id) && !exitNormalHost)
    },
    /**
     * 详情数据变更
     */
    handleSideDataChange(data) {
      const index = this.proxyData.findIndex(item => item.bk_host_id === data.bk_host_id)
      if (index > -1) {
        this.handleGetProxyList(true)
        // this.$set(this.proxyData, index, Object.assign(this.proxyData[index], data))
      }
    },
    handleSidesHidden() {
      this.$set(this, 'basicInfo', {})
    },
    /**
     * 跳转日志详情
     * @param {Object} row 当前行
     */
    handleGotoLog(row) {
      if (!row || !row.job_result) return
      this.$router.push({
        name: 'taskLog',
        params: {
          instanceId: row.job_result.instance_id,
          taskId: row.job_result.job_id
        }
      })
    },
    /**
     * 当前操作项是否显示
     */
    getOperateShow(row, config) {
      if (config.id === 'log' && (!row.job_result || !row.job_result.job_id)) {
        return false
      }
      return config.show
    },
    /**
     * 滚动列表到可视区域
     */
    scrollToView() {
      if (!this.$refs.leftList) return
      const itemHeight = 42 // 每项的高度
      const offsetHeight = itemHeight * this.area.list.findIndex(item => item.bkCloudId === this.area.active)
      if (offsetHeight > this.$refs.leftList.clientHeight) {
        this.$refs.leftList.scrollTo(0, offsetHeight - itemHeight)
      }
    },
    handleClose() {
      this.sideslider.show = false
    },
    /**
     * 自定义字段显示列
     * @param {createElement 函数} h 渲染函数
     */
    renderHeader() {
      return <ColumnSetting
        filter-head
        localMark={this.localMark}
        value={this.filter}
        onUpdate={data => this.handleColumnUpdate(data)}>
      </ColumnSetting>
    },
    /**
     * tips类型表头
     */
    renderTipHeader(h, data) {
      const directive = {
        name: 'bkTooltips',
        theme: 'light',
        content: this.$t('对外通讯IP提示'),
        width: 238,
        placement: 'top'
      }
      return <span class="text-underline" v-bk-tooltips={ directive }>{ data.column.label }</span>
    },
    /**
     * 字段显示列确认事件
     */
    handleColumnUpdate(data) {
      this.filter = data
      this.$forceUpdate()
    },
    /**
     * 获取存储信息
     */
    handleGetStorage() {
      let data = {}
      try {
        data = JSON.parse(window.localStorage.getItem(this.localMark + STORAGE_KEY_COL))
      } catch (_) {
        data = {}
      }
      return data
    },
    /**
     * 合并最后两列
     */
    colspanHandle({ column }) {
      if (column.property === 'colspaOpera') {
        return [1, 2]
      } if (column.property === 'colspaSetting') {
        return [0, 0]
      }
    },
    handleFilterAgent() {
      const cloud = this.cloudList.find(item => Number(this.id) === item.bkCloudId)
      if (!cloud) return
      this.$router.push({
        name: 'agentStatus',
        params: {
          cloud: {
            id: cloud.bkCloudId,
            name: cloud.bkCloudName
          }
        }
      })
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";
@import "@/css/transition.css";

@define-mixin col-row-status $color {
  margin-right: 10px;
  margin-top: -1px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $color;
}

.cloud-manager-detail {
  height: calc(100vh - 52px);

  @mixin layout-flex row;
  .detail-left {
    padding-top: 20px;
    flex: 0 0 240px;
    background-color: #fafbfd;
    &-search {
      margin-bottom: 16px;
      padding: 0 20px;
    }
    &-list {
      width: 240px;
      height: calc(100% - 55px);
      overflow-y: auto;
      .list-auth-wrapper {
        display: block;
      }
      .list-item {
        padding-left: 24px;
        padding-right: 20px;
        line-height: 42px;
        height: 42px;
        font-size: 14px;
        cursor: pointer;
        &-name {
          max-width: 160px;
          display: inline-block;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }
        &-icon {
          font-size: 14px;
          color: #c4c6cc;
          float: right;
          line-height: 42px;
        }
        &:hover {
          background: #f0f1f5;
        }
        &.loading {
          color: #979ba5;
          .loading-name {
            font-size: 12px;
          }
        }
        &.is-selected {
          background: #3a84ff;
          color: #fff;
          > .list-item-icon {
            color: #fff;
          }
        }
        &.auth-disabled {
          color: #dcdee5;
          .list-item-icon {
            color: #dcdee5;
          }
        }
      }
    }
  }
  .detail-right {
    flex: 1;
    padding: 20px 24px 0 24px;
    border-left: 1px solid #dcdee5;
    width: calc(100% - 240px);
    overflow-y: auto;
    &-title {
      line-height: 20px;

      @mixin layout-flex row;
      .title-icon {
        position: relative;
        top: -4px;
        height: 20px;
        font-size: 28px;
        color: #3a84ff;
        cursor: pointer;
      }
      .title-name {
        font-size: 16px;
        color: #313238;
      }
    }
    &-content {
      .row-btn {
        padding: 0;
        margin-right: 10px;
        white-space: nowrap;
      }
      .content-btn {
        margin-bottom: 14px;
      }
      .col-operate {
        @mixin layout-flex row, center;
        .loading-icon {
          display: inline-block;
          animation: loading 1s linear infinite;
          font-size: 14px;
          min-width: 24px;
          text-align: center;
        }
        .loading-name {
          margin-left: 7px;
        }
        .link-icon {
          font-size: 14px;
        }
      }
      .link-pointer {
        color: #3a84ff;
        cursor: pointer;
      }
    }
  }
}
</style>

<template>
  <article class="agent">
    <!--agent操作-->
    <section class="agent-operate mb15">
      <!--agent操作-->
      <div class="agent-operate-left">
        <!--安装Agent-->
        <auth-component
          tag="div"
          :auth="{
            permission: authority.operate,
            apply_info: [{ action: 'agent_operate' }]
          }">
          <template slot-scope="{ disabled }">
            <bk-dropdown-menu
              trigger="click"
              font-size="medium"
              :disabled="disabled || selectionCount"
              @show="handleDropdownShow('isSetupDropdownShow')"
              @hide="handleDropdownHide('isSetupDropdownShow')">
              <bk-button
                ext-cls="setup-btn"
                slot="dropdown-trigger"
                theme="primary"
                :disabled="disabled || !!selectionCount">
                <span class="icon-down-wrapper">
                  <span>{{ $t('安装Agent') }}</span>
                  <i :class="['bk-icon icon-angle-down setup-btn-icon', { 'icon-flip': isSetupDropdownShow }]"></i>
                </span>
              </bk-button>
              <ul class="bk-dropdown-list" slot="dropdown-content">
                <li><a @click.prevent="triggerHandler({ type: 'setup' })">{{ $t('普通安装') }}</a></li>
                <li><a @click.prevent="triggerHandler({ type: 'import' })">{{ $t('Excel导入安装') }}</a></li>
              </ul>
            </bk-dropdown-menu>
          </template>
        </auth-component>
        <!--复制IP-->
        <bk-dropdown-menu
          trigger="click"
          ref="copyIp"
          font-size="medium"
          class="ml10"
          :disabled="loadingCopyBtn || table.data.length === 0"
          @show="handleDropdownShow('isCopyDropdownShow')"
          @hide="handleDropdownHide('isCopyDropdownShow')">
          <bk-button
            class="dropdown-btn"
            slot="dropdown-trigger"
            :loading="loadingCopyBtn"
            :disabled="table.data.length === 0">
            <span class="icon-down-wrapper">
              <span>{{ $t('复制') }}</span>
              <i :class="['bk-icon icon-angle-down', { 'icon-flip': isCopyDropdownShow }]"></i>
            </span>
          </bk-button>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <li>
              <a :class="{ 'item-disabled': selectionCount === 0 }"
                 @click.prevent.stop="triggerHandler({
                   type: 'checkedIp',
                   disabled: selectionCount === 0
                 })">
                {{ $t('勾选IP') }}
              </a>
            </li>
            <li><a @click.prevent="triggerHandler({ type: 'allIp' })">{{ $t('所有IP') }}</a></li>
          </ul>
        </bk-dropdown-menu>
        <!--批量操作-->
        <bk-dropdown-menu
          trigger="click"
          ref="batch"
          font-size="medium"
          class="ml10"
          :disabled="!isSingleHosts || !(indeterminate || isAllChecked)"
          @show="handleDropdownShow('isbatchDropdownShow')"
          @hide="handleDropdownHide('isbatchDropdownShow')">
          <bk-button
            slot="dropdown-trigger"
            :disabled="!isSingleHosts || !(indeterminate || isAllChecked)">
            <bk-popover
              placement="bottom"
              :delay="400"
              :disabled="!(!isSingleHosts && (indeterminate || isAllChecked))"
              :content="$t('不同安装方式的Agent不能统一批量操作')">
              <span class="icon-down-wrapper">
                <span>{{ $t('批量') }}</span>
                <i :class="['bk-icon icon-angle-down', { 'icon-flip': isbatchDropdownShow }]"></i>
              </span>
            </bk-popover>
          </bk-button>
          <ul class="bk-dropdown-list" slot="dropdown-content">
            <template v-for="item in operate">
              <li v-if="!item.single" :key="item.id" :class="{ 'disabled': getBatchMenuStaus(item) }">
                <a @click.prevent="!getBatchMenuStaus(item) && triggerHandler({ type: item.id })">{{ item.name }}</a>
              </li>
            </template>
          </ul>
        </bk-dropdown-menu>
        <!--选择业务-->
        <bk-biz-select
          v-model="search.biz"
          class="ml10"
          min-width="200"
          ext-cls="left-select"
          :placeholder="$t('全部业务')"
          @change="handleBizChange">
        </bk-biz-select>
        <bk-popover class="ml10 mr10 topo-cascade" :delay="200" :disabled="search.biz.length === 1">
          <bk-cascade
            clearable
            check-any-level
            ref="topoSelect"
            v-model="search.topo"
            :placeholder="$t('业务拓扑')"
            :disabled="!bkBizList.length || search.biz.length !== 1"
            :list="topoBizFilterList"
            @change="topoSelectchange"
            @toggle="handleTopoChange">
            <!-- scroll-width="200"  组件有bug -->
            <!-- :remote-method="topoRemotehandler" -->
          </bk-cascade>
          <!-- check-any-level -->
          <div slot="content">
            {{ $t('选择模块frist') }}<b>{{ $t('选择模块center') }}</b> {{ $t('选择模块last') }}
          </div>
        </bk-popover>
      </div>
      <!--agent搜索-->
      <div class="agent-operate-right">
        <bk-search-select
          ref="searchSelect"
          ext-cls="right-select"
          :data="searchSelectData"
          v-model="searchSelectValue"
          :show-condition="false"
          :placeholder="$t('agent列表搜索')"
          @paste.native.capture.prevent="handlePaste"
          @change="handleSearchSelectChange">
        </bk-search-select>
      </div>
    </section>
    <!--agent列表-->
    <section class="agent-content" v-bkloading="{ isLoading: loading }">
      <bk-table
        ext-cls="agent-content-table"
        ref="agentTable"
        :class="`head-customize-table ${ fontSize }`"
        :cell-class-name="handleCellClass"
        :span-method="colspanHandle"
        :data="table.data"
        @sort-change="handleSort">
        <template #prepend>
          <transition name="tips">
            <div class="selection-tips" v-show="!checkLoading && isAllChecked && selectionCount">
              <div>
                {{ $t('已选') }}
                <span class="tips-num">{{ selectionCount }}</span>
                {{ $t('条') }},
              </div>
              <bk-button ext-cls="tips-btn" text v-if="!isSelectedAllPages" @click="handleSelectionAll">
                {{ $t('选择所有') }}
                <span class="tips-num">{{ table.pagination.count }}</span>
                {{ $t('条') }}
              </bk-button>
              <bk-button
                ext-cls="tips-btn"
                text
                v-else
                @click="handleClearSelection">
                {{ $t('清除所有数据') }}
              </bk-button>
            </div>
          </transition>
        </template>
        <bk-table-column
          key="selection"
          width="70"
          align="center"
          fixed
          :resizable="false"
          :render-header="renderSelectionHeader">
          <template #default="{ row }">
            <auth-component
              tag="div"
              :auth="{
                permission: row.operate_permission,
                apply_info: [{
                  action: 'agent_operate',
                  instance_id: row.bk_biz_id,
                  instance_name: row.bk_biz_name
                }]
              }">
              <template slot-scope="{ disabled }">
                <bk-checkbox
                  :value="row.selection"
                  :disabled="row.job_result.status === 'RUNNING' || disabled"
                  @change="handleRowCheck(arguments, row)">
                </bk-checkbox>
              </template>
            </auth-component>
          </template>
        </bk-table-column>
        <bk-table-column
          key="IP"
          label="IP"
          prop="inner_ip">
        </bk-table-column>
        <bk-table-column
          key="login_ip"
          :label="$t('登录IP')"
          prop="login_ip"
          v-if="filter['login_ip'].mockChecked">
          <template #default="{ row }">
            {{ row.login_ip || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          key="biz"
          :label="$t('归属业务')"
          prop="bk_biz_name"
          v-if="filter['bk_biz_name'].mockChecked">
        </bk-table-column>
        <bk-table-column
          key="cloudArea"
          :label="$t('云区域')"
          :render-header="renderFilterHeader"
          prop="bk_cloud_id"
          v-if="filter['bk_cloud_id'].mockChecked">
          <template #default="{ row }">
            {{ row.bk_cloud_name || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          key="system"
          :label="$t('操作系统')"
          prop="os_type"
          :render-header="renderFilterHeader"
          v-if="filter['os_type'].mockChecked">
          <template #default="{ row }">
            {{ osMap[row.os_type] || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          key="status"
          :label="$t('Agent状态')"
          prop="status"
          min-width="100"
          :render-header="renderFilterHeader">
          <template #default="{ row }">
            <div class="col-status" v-if="row.status_display">
              <span :class="'status-mark status-' + row.status"></span>
              <span>{{ row.status_display }}</span>
            </div>
            <div class="col-status" v-else>
              <span class="status-mark status-unknown"></span>
              <span>{{ row.status_display }}</span>
            </div>
          </template>
        </bk-table-column>
        <!-- sortable="custom" -->
        <bk-table-column
          key="version"
          :label="$t('Agent版本')"
          prop="version"
          :render-header="renderFilterHeader"
          v-if="filter['agent_version'].mockChecked">
        </bk-table-column>
        <bk-table-column
          key="is_manual"
          :label="$t('安装方式')"
          prop="is_manual"
          v-if="filter['is_manual'].mockChecked"
          :render-header="renderFilterHeader">
          <template #default="{ row }">
            {{ row.is_manual ? $t('手动') : $t('远程') }}
          </template>
        </bk-table-column>
        <bk-table-column
          key="bt"
          prop="peer_exchange_switch_for_agent"
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
          align="right"
          :label="`${this.$t('传输限速')}(MB/s)`"
          v-if="filter['speedLimit'].mockChecked">
          <template #default="{ row }">
            {{ row.bt_speed_limit || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column v-if="filter['speedLimit'].mockChecked" min-width="30" :resizable="false">
        </bk-table-column>
        <bk-table-column
          key="created_at"
          :label="$t('安装时间')"
          width="200"
          prop="created_at"
          :resizable="false"
          v-if="filter['created_at'].mockChecked">
        </bk-table-column>
        <bk-table-column
          key="updated_at"
          :label="$t('更新时间')"
          width="200"
          prop="updated_at"
          :resizable="false"
          v-if="filter['updated_at'].mockChecked">
          <template #default="{ row }">
            {{ row.updated_at || '--' }}
          </template>
        </bk-table-column>
        <bk-table-column
          key="topology"
          :label="$t('业务拓扑')"
          prop="topology"
          min-width="100"
          v-if="filter['topology'].mockChecked"
          :resizable="false">
          <template #default="{ row }">
            <div v-bk-tooltips="{
                   content: row.topology.join('<br>'),
                   theme: 'light',
                   delay: [300, 0],
                   placements: 'bottom',
                   disabled: row.topology.length === 1
                 }"
                 v-if="row.topology.length">
              <span :class="{ 'col-topo': row.topology.length > 1 }"
                    :title="row.topology.length === 1 ? row.topology.join('') : ''">
                {{ row.topology.join(', ') }}
              </span>
            </div>
            <span v-else>--</span>
          </template>
        </bk-table-column>
        <bk-table-column
          key="num"
          width="60"
          :resizable="false"
          v-if="filter['topology'].mockChecked">
          <template #default="{ row }">
            <span
              class="col-num"
              v-if="row.topology.length > 1"
              v-bk-tooltips="{
                content: row.topology.join('<br>'),
                theme: 'light',
                delay: [300, 0],
                placements: 'bottom',
                disabled: row.topology.length === 1
              }">
              {{ `+${row.topology.length}` }}
            </span>
          </template>
        </bk-table-column>
        <bk-table-column
          key="operate"
          prop="colspaOpera"
          :label="$t('操作')"
          width="150"
          :resizable="false"
          fixed="right">
          <template #default="{ row }">
            <div class="col-operate">
              <auth-component
                v-if="['PENDING', 'RUNNING'].includes(row.job_result.status)"
                class="col-btn ml10"
                tag="div"
                :auth="{
                  permission: row.operate_permission,
                  apply_info: [{
                    action: 'agent_operate',
                    instance_id: row.bk_biz_id,
                    instance_name: row.bk_biz_name
                  }]
                }">
                <template slot-scope="{ disabled }">
                  <bk-button text :disabled="disabled" @click="handleGotoLog(row)">
                    <loading-icon></loading-icon>
                    <span class="loading-name" v-bk-tooltips.top="$t('查看任务详情')">
                      {{ row.job_result.current_step || $t('正在运行') }}
                    </span>
                  </bk-button>
                </template>
              </auth-component>
              <auth-component
                v-else
                class="header-left"
                tag="div"
                :auth="{
                  permission: row.operate_permission,
                  apply_info: [{
                    action: 'agent_operate',
                    instance_id: row.bk_biz_id,
                    instance_name: row.bk_biz_name
                  }]
                }">
                <template slot-scope="{ disabled }">
                  <bk-button theme="primary"
                             text
                             ext-cls="reinstall"
                             :disabled="disabled"
                             @click="handleOperate('reinstall', [row])">
                    {{ row.status === 'not_installed' ? $t('安装') : $t('重装') }}
                  </bk-button>
                  <bk-popover
                    :ref="row['bk_host_id']"
                    theme="light agent-operate"
                    trigger="click"
                    :arrow="false"
                    offset="30, 5"
                    placement="bottom"
                    :disabled="disabled">
                    <bk-button theme="primary" class="ml10" text :disabled="disabled">{{ $t('更多') }}</bk-button>
                    <template #content>
                      <ul class="dropdown-list">
                        <li
                          v-for="item in operate"
                          v-show="getOperateShow(row, item)"
                          :class="[
                            'list-item',
                            fontSize,
                            { 'disabled': row.status === 'not_installed' && item.id !== 'log' }
                          ]"
                          :key="item.id"
                          @click="handleOperate(item.id, [row])">
                          {{ item.name }}
                        </li>
                      </ul>
                    </template>
                  </bk-popover>
                </template>
              </auth-component>
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
      <bk-pagination
        ext-cls="pagination"
        size="small"
        :limit="table.pagination.limit"
        :count="table.pagination.count"
        :current="table.pagination.current"
        :limit-list="table.pagination.limitList"
        align="right"
        show-total-count
        show-selection-count
        :selection-count="selectionCount"
        @change="handlePageChange"
        @limit-change="handlePageLimitChange">
      </bk-pagination>
    </section>
    <bk-footer></bk-footer>
  </article>
</template>
<script>
import { mapActions, mapGetters } from 'vuex'
import ColumnSetting from '@/components/column-setting/column-setting'
import ColumnCheck from './components/column-check'
import tableHeaderMixins from '@/components/filter-header/table-header-mixins'
import pollMixin from '@/common/poll-mixin'
import authorityMixin from '@/common/authority-mixin'
import { copyText, debounce, isEmpty } from '@/common/util'
import { bus } from '@/common/bus'
import { STORAGE_KEY_COL } from '@/config/storage-key'
import BkFooter from '@/components/footer/footer'

export default {
  name: 'agent-list',
  components: {
    BkFooter
  },
  mixins: [tableHeaderMixins, pollMixin, authorityMixin()],
  data() {
    return {
      table: {
        // 所有运行主机的数量
        runningCount: 0,
        // 无操作全选的主机
        noPermissionCount: 0,
        // 列表数据
        data: [],
        // 分页
        pagination: {
          current: 1,
          count: 0,
          limit: 50,
          limitList: [50, 100, 200]
        }
      },
      sortData: {
        head: null,
        sort_type: null
      },
      loading: true,
      // 跨页全选loading
      checkLoading: false,
      // ip复制按钮加载状态
      loadingCopyBtn: false,
      // 列表字段显示配置
      filter: {
        inner_ip: {
          checked: true,
          disabled: true,
          mockChecked: true,
          name: 'IP',
          id: 'inner_ip'
        },
        login_ip: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('登录IP'),
          id: 'login_ip'
        },
        agent_version: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('Agent版本'),
          id: 'agent_version'
        },
        agent_status: {
          checked: true,
          disabled: true,
          mockChecked: true,
          name: this.$t('Agent状态'),
          id: 'agent_status'
        },
        bk_cloud_id: {
          checked: true,
          mockChecked: true,
          disabled: false,
          name: this.$t('云区域'),
          id: 'bk_cloud_id'
        },
        bk_biz_name: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('归属业务'),
          id: 'bk_biz_name'
        },
        topology: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('业务拓扑'),
          id: 'topology'
        },
        os_type: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('操作系统'),
          id: 'os_type'
        },
        is_manual: {
          checked: true,
          disabled: false,
          mockChecked: true,
          name: this.$t('安装方式'),
          id: 'is_manual'
        },
        created_at: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('安装时间'),
          id: 'created_at'
        },
        updated_at: {
          checked: false,
          disabled: false,
          mockChecked: false,
          name: this.$t('更新时间'),
          id: 'updated_at'
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
      // 是否显示复制按钮下拉菜单
      isCopyDropdownShow: false,
      // 是否显示批量按钮下拉菜单
      isbatchDropdownShow: false,
      isSetupDropdownShow: false,
      // 状态map
      statusMap: {
        running: this.$t('正常'),
        terminated: this.$t('异常'),
        unknown: this.$t('未知')
      },
      osMap: {
        LINUX: 'Linux',
        WINDOWS: 'Windows',
        AIX: 'AIX'
      },
      // 批量操作
      operate: [
        {
          id: 'reinstall',
          name: this.$t('安装重装'),
          disabled: false,
          show: false
        },
        {
          id: 'upgrade',
          name: this.$t('升级'),
          disabled: false,
          show: true
        },
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
          id: 'reload',
          name: this.$t('重载配置'),
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
          id: 'log',
          name: this.$t('最新执行日志'),
          disabled: false,
          show: true,
          single: true
        }
      ],
      // 搜索相关
      search: {
        biz: [],
        topo: []
      },
      // 集群/模块 topo
      topoBizFormat: {},
      // topo选中的String
      topoSelectStr: '',
      // 选择的层级
      topoSelectChild: {},
      // 搜索防抖
      initAgentListDebounce() {},
      // 是否是跨页全选
      isSelectedAllPages: false,
      // 标记删除数组
      markDeleteArr: [],
      ipRegx: new RegExp('^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$'),
      localMark: '_agent',
      operateBiz: [] // 有操作权限的业务
    }
  },
  computed: {
    ...mapGetters(['fontSize']),
    ...mapGetters('agent', ['cloudList']),
    ...mapGetters(['bkBizList', 'selectedBiz']),
    // 可操作的数据
    datasheets() {
      return this.table.data.filter(item => item.job_result.status !== 'RUNNING' && item.operate_permission)
    },
    // 当前列表选择数据
    selection() {
      return this.datasheets.filter(item => item.selection)
    },
    // 当前是否是半选状态
    indeterminate() {
      if (this.isSelectedAllPages) {
        // 跨页全选半选状态
        return !this.isAllChecked && !!this.markDeleteArr.length
      }
      return !this.isAllChecked && this.datasheets.some(item => item.selection)
    },
    // 是否全选
    isAllChecked() {
      if (this.isSelectedAllPages) {
        // 标记删除的数组为空
        return !this.markDeleteArr.length
      }
      return this.datasheets.every(item => item.selection)
    },
    // 是否禁用全选checkbox
    disabledCheckBox() {
      return !this.datasheets.length
    },
    // 跨页全选未勾选条数
    deleteCount() {
      return this.markDeleteArr.length + this.table.runningCount + this.table.noPermissionCount
    },
    // 已勾选条数
    selectionCount() {
      return this.isSelectedAllPages
        ? this.table.pagination.count - this.deleteCount
        : this.selection.length
    },
    // 是否筛选过一种安装方式 或者 仅存在一种安装方式 那么跨页全选也是可批量操作的
    isSingleInstallFilter() {
      const installFilter = this.filterData.find(item => item.id === 'is_manual' && item.children.length === 1)
      return installFilter || this.searchSelectValue.find(item => item.id === 'is_manual' && item.values.length === 1)
    },
    // 选中机器是否为单种安装类型
    isSingleHosts() {
      if (this.isSingleInstallFilter) {
        return true
      }
      if (this.isSelectedAllPages || !this.selectionCount) {
        return false
      }
      return new Set(this.selection.map(item => item.is_manual)).size === 1
    },
    // topo根据业务来展示
    topoBizFilterList() {
      if (this.search.biz.length !== 1) {
        return []
      }
      const bizIdKey = this.search.biz.join('')
      return this.topoBizFormat[bizIdKey] ? this.topoBizFormat[bizIdKey].children || [] : []
    },
    checkAllPermission() {
      return this.table.data.length
        ? this.table.data.some(item => item.operate_permission)
        : true
    }
  },
  watch: {
    searchSelectValue: {
      handler() {
        this.table.pagination.current = 1
        this.initAgentListDebounce()
      },
      deep: true
    },
    bkBizList() {
      this.initTopoFormat()
    }
  },
  created() {
    this.search.biz = this.selectedBiz
  },
  mounted() {
    this.handleInit()
    this.initAgentListDebounce = debounce(300, this.initAgentList)
  },
  methods: {
    ...mapActions(['getBizTopo']),
    ...mapActions('agent', [
      'getHostList',
      'getFilterCondition',
      'getHostIp',
      'removeHost',
      'operateJob',
      'getRunningHost'
    ]),
    async handleInit() {
      this.initCustomColStatus()
      const { cloud } = this.$route.params
      if (!cloud) {
        this.initAgentList()
      }
      this.getFilterCondition().then((data) => {
        this.filterData = data
        if (cloud) {
          this.handleSearchSelectChange([
            {
              name: '云区域',
              id: 'bk_cloud_id',
              values: [cloud]
            }
          ])
          this.handlePushValue('bk_cloud_id', [cloud], false)
        }
      })
      if (this.bkBizList) {
        this.initTopoFormat()
      }
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
    initTopoFormat() {
      const bizFormat = {}
      this.bkBizList.forEach((item) => {
        bizFormat[item.bk_biz_id] = {
          id: item.bk_biz_id,
          name: item.bk_biz_name,
          disabled: item.disabled || false,
          children: [],
          needLoad: true
        }
      })
      this.topoBizFormat = bizFormat
      if (this.search.biz.length === 1) {
        const bizIdKey = this.search.biz.join('')
        if (Object.prototype.hasOwnProperty.call(this.topoBizFormat, bizIdKey)
            && this.topoBizFormat[bizIdKey].needLoad) {
          this.topoRemotehandler(this.topoBizFormat[bizIdKey])
        }
      }
    },
    /**
     * 初始化agent列表
     * @param {Boolean} spreadChecked 是否是跨页操作
     */
    async initAgentList(spreadChecked = false) {
      this.loading = true
      if (!spreadChecked) {
        this.isSelectedAllPages = false
        this.markDeleteArr.splice(0, this.markDeleteArr.length)
        this.handleClearSelection() // 防止二次勾选时还是处于跨页全选状态
      }

      this.runingQueue.splice(0, this.runingQueue.length)
      clearTimeout(this.timer)
      this.timer = null

      const extraData = ['job_result', 'identity_info']
      if (this.filter.topology.mockChecked) {
        extraData.push('topology')
      }
      const params = this.getSearchCondition(extraData)
      const data = await this.getHostList(params)
      this.table.data = data.list.map((item) => {
        // 跨页勾选
        item.selection = this.isSelectedAllPages
        && this.markDeleteArr.findIndex(v => v.bk_host_id === item.bk_host_id) === -1
        // 轮询任务队列
        if (item.job_result.status && item.job_result.status === 'RUNNING') {
          this.runingQueue.push(item.bk_host_id)
        }
        return item
      })
      this.table.pagination.count = data.total
      this.loading = false
    },
    /**
     * 运行轮询任务
     */
    async handlePollData() {
      const data = await this.getHostList({
        page: 1,
        pagesize: this.runingQueue.length,
        bk_host_id: this.runingQueue,
        extra_data: ['job_result', 'identity_info']
      })
      this.handleChangeStatus(data)
    },
    /**
     * 变更轮询回来的数据状态
     * @param {Object} data
     */
    handleChangeStatus(data) {
      data.list.forEach((item) => {
        const index = this.table.data.findIndex(row => row.bk_host_id === item.bk_host_id)
        if (index > -1) {
          if (item.job_result.status !== 'RUNNING') {
            const i = this.runingQueue.findIndex(id => id === item.bk_host_id)
            this.runingQueue.splice(i, 1)
          }
          this.$set(this.table.data, index, item)
        }
      })
    },
    getCommonCondition() {
      const params = {
        conditions: []
      }
      if (this.sortData.head && this.sortData.sort_type) {
        params.sort = Object.assign({}, this.sortData)
      }
      if (this.search.biz.length && this.search.biz.length !== this.bkBizList.length) {
        params.bk_biz_id = this.search.biz
      }
      // 其他搜索条件
      this.searchSelectValue.forEach((item) => {
        if (Array.isArray(item.values)) {
          params.conditions.push({
            key: item.id,
            value: item.values.map(value => value.id)
          })
        } else {
          params.conditions.push({
            key: 'query',
            value: item.name
          })
        }
      })
      /**
       * 非 set|module 的类型为 自定义层级
       * 自定义层级下一定为 set | 自定义层级
       * 选中为自定义层级需要拿到其下所有的set
       */
      const topoLen = this.search.topo.length
      if (topoLen) {
        const value = {
          bk_biz_id: this.search.biz[0]
        }
        const len = this.topoSelectChild.length
        const lastSelect = this.topoSelectChild[len - 1]
        if (lastSelect.type === 'set') {
          value.bk_set_ids = [lastSelect.id]
        } else if (lastSelect.type === 'module') {
          // module的上级必定为set
          const penultSelect = this.topoSelectChild[len - 2]
          value.bk_set_ids = [penultSelect.id]
          value.bk_module_ids = [lastSelect.id]
        } else {
          value.bk_set_ids = this.getTopoSetDeep(lastSelect, [])
        }
        params.conditions.push({
          key: 'topology',
          value
        })
      }
      return params
    },
    /**
     * 找到 自定义层级 下的所有 set
     */
    getTopoSetDeep(topoItem, setArr) {
      if (topoItem.type === 'set') {
        setArr.push(topoItem.id)
      } else if (topoItem.type !== 'module') {
        if (topoItem.children && topoItem.children.length) {
          topoItem.children.forEach((item) => {
            this.getTopoSetDeep(item, setArr)
          })
        }
      }
      return setArr
    },
    /**
     * 获取主机列表当前所有查询条件
     */
    getSearchCondition(extraData = []) {
      const params = {
        page: this.table.pagination.current,
        pagesize: this.table.pagination.limit,
        extra_data: extraData
      }

      return Object.assign(params, this.getCommonCondition(extraData))
    },
    /**
     * 标记删除法查询参数
     */
    getExcludeHostCondition(extraData = []) {
      const params = {
        pagesize: -1,
        exclude_hosts: this.markDeleteArr.map(item => item.bk_host_id),
        extra_data: extraData
      }

      return Object.assign(params, this.getCommonCondition(extraData))
    },
    /**
     * 获取所有勾选IP信息查询条件
     */
    getCheckedIpCondition() {
      const params = {
        pagesize: -1,
        only_ip: true
      }
      // 跨页全选
      if (this.isSelectedAllPages) {
        params.exclude_hosts = this.markDeleteArr.map(item => item.bk_host_id)
      }

      return Object.assign(params, this.getCommonCondition())
    },
    /**
     * 获取所有IP信息的查询条件
     */
    getAllIpCondition() {
      const params = {
        pagesize: -1,
        only_ip: true
      }

      return Object.assign(params, this.getCommonCondition())
    },
    /**
     * 获取删除主机信息的查询条件
     */
    getDeleteHostCondition(data = []) {
      const params = {
        is_proxy: false
      }
      if (this.isSelectedAllPages) {
        params.exclude_hosts = this.markDeleteArr.map(item => item.bk_host_id)
      } else {
        params.bk_host_id = data.length
          ? data.map(item => item.bk_host_id)
          : this.selection.map(item => item.bk_host_id)
      }

      return Object.assign(params, this.getCommonCondition())
    },
    /**
     * 获取重启主机的查询条件
     */
    getOperateHostCondition(data = [], operateType) {
      const params = {
        job_type: operateType
      }
      if (this.isSelectedAllPages) {
        params.exclude_hosts = this.markDeleteArr.map(item => item.bk_host_id)
      } else {
        params.bk_host_id = data.length
          ? data.map(item => item.bk_host_id)
          : this.selection.map(item => item.bk_host_id)
      }

      return Object.assign(params, this.getCommonCondition())
    },
    /**
     * 业务变更
     */
    handleBizChange(newValue) {
      if (newValue.length !== 1) {
        // topo未选择时 清空biz不会触发 cascade组件change事件
        if (this.search.topo.length) {
          this.$refs.topoSelect.clearData()
          return false
        }
      } else {
        const bizIdKey = newValue.join('')
        if (Object.prototype.hasOwnProperty.call(this.topoBizFormat, bizIdKey)
            && this.topoBizFormat[bizIdKey].needLoad) {
          this.topoRemotehandler(this.topoBizFormat[bizIdKey])
        }
      }
      this.table.pagination.current = 1
      this.initAgentListDebounce()
    },
    /**
     * 拉取拓扑
     */
    handleTopoChange(toggle) {
      if (toggle) {
        this.topoSelectStr = this.search.topo.join(',')
      } else {
        if (this.topoSelectStr !== this.search.topo.join(',')) {
          this.table.pagination.current = 1
          this.initAgentListDebounce()
        }
      }
    },
    /**
     * 拿到最后一次选择的层级
     */
    topoSelectchange(newValue, oldValue, selectList) {
      this.topoSelectChild = selectList
      // 组件bug，clear事件并未派发出来
      if (!newValue.length) {
        this.table.pagination.current = 1
        this.initAgentListDebounce()
      }
    },
    async topoRemotehandler(item, resolve) {
      if (item.needLoad && !item.isLoading) {
        this.$set(item, 'isLoading', true)
        const res = await this.getBizTopo({ bk_biz_id: item.id })
        if (res) {
          if (!Array.isArray(res)) {
            return []
          }
          item.needLoad = false
          item.children = res
          const bizIdKey = item.id
          if (Object.prototype.hasOwnProperty.call(this.topoBizFormat, 'bizIdKey')) {
            this.topoBizFormat[bizIdKey].children = res
            this.topoBizFormat[bizIdKey].needLoad = false
          }
        }
      }
      // resolve更新children, 数据放store会有bug
      if (resolve) {
        resolve(item)
      }
    },
    /**
     * 安装 Agent（普通安装）
     */
    handleSetupAgent() {
      this.$router.push({ name: 'agentSetup' })
    },
    /**
     * 安装 Agent（Excel 导入）
     */
    handleImportAgent() {
      this.$router.push({ name: 'agentImport' })
    },
    handlePageChange(page) {
      this.table.pagination.current = page || 1
      this.initAgentList(true)
    },
    handlePageLimitChange(limit) {
      this.table.pagination.current = 1
      this.table.pagination.limit = limit
      this.initAgentList(true)
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
     * 字段显示列确认事件
     */
    handleColumnUpdate(data) {
      const originTopoChecked = this.filter.topology.mockChecked
      const currentTopoChecked = data.topology.mockChecked
      this.filter = data
      if (currentTopoChecked && currentTopoChecked !== originTopoChecked) {
        this.initAgentList()
      }
      this.$forceUpdate()
    },
    handleDropdownShow(value) {
      this[value] = true
    },
    handleDropdownHide(value) {
      this[value] = false
    },
    /**
     * 复制勾选 IP
     */
    async handleCopyCheckedIp() {
      this.loadingCopyBtn = true
      let data = {
        total: this.selection.length,
        list: this.selection.map(item => item.inner_ip)
      }
      if (this.isSelectedAllPages) {
        data = await this.getHostIp(this.getCheckedIpCondition())
      }
      const checkedIpText = data.list.join('\n')
      if (!checkedIpText) return
      const result = copyText(checkedIpText)
      if (result) {
        this.$bkMessage({ theme: 'success', message: this.$t('IP复制成功', { num: data.total }) })
      }
      this.loadingCopyBtn = false
    },
    /**
     * 复制所有 IP
     */
    async handleCopyAllIp() {
      this.loadingCopyBtn = true
      const data = await this.getHostIp(this.getAllIpCondition())
      const allIpText = data.list.join('\n')
      if (!allIpText) return
      const result = copyText(allIpText)
      if (result) {
        this.$bkMessage({ theme: 'success', message: this.$t('IP复制成功', { num: data.total }) })
      }
      this.loadingCopyBtn = false
    },
    /**
     * 操作
     * @param {Object} item
     */
    triggerHandler(item) {
      if (item.disabled) return
      const data = this.isSelectedAllPages ? this.markDeleteArr : this.selection
      switch (item.type) {
        // 复制IP
        case 'checkedIp':
          this.handleCopyCheckedIp()
          break
          // 复制所有IP
        case 'allIp':
          this.handleCopyAllIp()
          break
          // 批量重启 批量重装 批量重载配置 批量卸载 批量升级
        case 'reboot':
        case 'reinstall':
        case 'reload':
        case 'uninstall':
        case 'upgrade':
          this.handleOperate(item.type, data, true)
          break
          // 移除
        case 'remove':
          this.handleRemoveHost()
          break
          // 普通安装
        case 'setup':
          this.handleSetupAgent()
          break
          // Excel 导入
        case 'import':
          this.handleImportAgent()
          break
      }
      this.$refs.copyIp.hide()
      this.$refs.batch.hide()
    },
    /**
     * row勾选事件
     */
    handleRowCheck(arg, row) {
      // 跨页全选采用标记删除法
      if (this.isSelectedAllPages) {
        if (!arg[0]) {
          this.markDeleteArr.push(row)
        } else {
          const index = this.markDeleteArr.findIndex(item => item.bk_host_id === row.bk_host_id)
          if (index > -1) {
            this.markDeleteArr.splice(index, 1)
          }
        }
      }
      this.$set(row, 'selection', arg[0])
    },
    /**
     * 自定义selection表头
     */
    renderSelectionHeader() {
      return <ColumnCheck
        ref="customSelectionHeader"
        indeterminate={this.indeterminate}
        isAllChecked={this.isAllChecked}
        loading={this.checkLoading}
        disabled={this.disabledCheckBox}
        action="agent_operate"
        checkAllPermission={this.checkAllPermission}
        onChange={(value, type) => this.handleCheckAll(value, type)}>
      </ColumnCheck>
    },
    /**
     * 表头勾选事件
     * @param {Boolean} value 全选 or 取消全选
     * @param {String} type 当前页全选 or 跨页全选
     */
    async handleCheckAll(value, type) {
      if (type === 'current' && this.disabledCheckBox) return
      // 跨页全选
      this.isSelectedAllPages = value && type === 'all'
      // 删除标记数组
      this.markDeleteArr.splice(0, this.markDeleteArr.length)
      if (this.isSelectedAllPages) {
        this.checkLoading = true
        const params = Object.assign({
          pagesize: -1,
          running_count: true
        }, this.getCommonCondition())
        const {
          running_count: runningCount,
          no_permission_count: noPermissionCount
        } = await this.getRunningHost(params)
        this.table.runningCount = runningCount
        this.table.noPermissionCount = noPermissionCount
        this.checkLoading = false
      }
      this.table.data.forEach((item) => {
        if (item.job_result.status !== 'RUNNING' && item.operate_permission) {
          this.$set(item, 'selection', value)
        }
      })
    },
    /**
     * Agent操作
     * @param {String} type 操作类型
     * @param {Array} data agent数据
     * @param {Boolean} batch 是否是批量操作
     *
     * 重装都需要经过编辑页面 *****
     * Linux升级走job不需要编辑，windows升级需要编辑不走job， 混合走编辑 *****
     * Linux、window卸载都不需要经过编辑页面 *****
     */
    handleOperate(type, data, batch = false) {
      if (!batch && data[0].status === 'not_installed' && type !== 'reinstall' && type !== 'log') {
        return
      }
      if (!batch && this.$refs[data[0].bk_host_id]) {
        this.$refs[data[0].bk_host_id].instance.hide()
      }

      let jobType = ''

      switch (type) {
        // 重启
        case 'reboot':
          this.handleOperatetHost(data, batch, 'RESTART_AGENT')
          break
          // 移除
        case 'remove':
          this.handleRemoveHost(data, batch)
          break
          // 重装
        case 'reinstall':
          // title = this.$t('重装Agent')
          jobType = 'REINSTALL_AGENT'
          break
          // 重装
        case 'reload':
          jobType = 'RELOAD_AGENT'
          break
          // 卸载
        case 'uninstall':
          jobType = 'UNINSTALL_AGENT'
          // this.handleOperatetHost(data, batch, 'UNINSTALL_AGENT')
          break
          // 升级
        case 'upgrade':
          this.handleOperatetHost(data, batch, 'UPGRADE_AGENT')
          break
          // 日志详情
        case 'log':
          this.handleGotoLog(data[0])
          break
      }
      if (!jobType) return

      this.$router.push({
        name: 'agentEdit',
        params: {
          tableData: data.map(item => Object.assign({}, item, item.identity_info)),
          type: jobType,
          // true：跨页全选（tableData表示标记删除的数据） false：非跨页全选（tableData表示编辑的数据）
          isSelectedAllPages: batch && this.isSelectedAllPages,
          condition: this.getExcludeHostCondition(['identity_info'])
        }
      })
    },
    /**
     * 跳转日志详情
     */
    handleGotoLog(data) {
      if (!data || !data.job_result) return
      this.$router.push({
        name: 'taskLog',
        params: {
          instanceId: data.job_result.instance_id,
          taskId: data.job_result.job_id
        }
      })
    },
    /**
     * 重启、卸载 Host
     * @param {Array} data
     */
    handleOperatetHost(data, batch, operateType) {
      const titleObj = {
        firstIp: batch ? this.selection[0].inner_ip : data[0].inner_ip,
        num: batch ? this.selectionCount : data.length
      }
      const operateJob = async (data) => {
        this.loading = true
        const params = this.getOperateHostCondition(data, operateType)
        const result = await this.operateJob(params)
        this.loading = false
        if (result.job_id) {
          this.$router.push({ name: 'taskDetail', params: { taskId: result.job_id } })
        }
      }
      let titleKey = ''
      switch (operateType) {
        // 重启
        case 'RESTART_AGENT':
          titleKey = '重启lower'
          break
          // 卸载
        case 'UNINSTALL_AGENT':
          titleKey = '卸载lower'
          break
          // 升级
        case 'UPGRADE_AGENT':
          titleKey = '升级lower'
          break
      }
      this.$bkInfo({
        title: batch
          ? this.$t('请确认是否批量操作', { type: this.$t(titleKey) })
          : this.$t('请确认是否操作', { type: this.$t(titleKey) }),
        subTitle: batch
          ? this.$t('批量确认操作提示', {
            ip: titleObj.firstIp,
            num: titleObj.num,
            type: this.$t(titleKey),
            suffix: operateType === 'UPGRADE_AGENT' ? this.$t('到最新版本') : '' })
          : this.$t('单条确认操作提示', {
            ip: titleObj.firstIp,
            type: this.$t(titleKey),
            suffix: operateType === 'UPGRADE_AGENT' ? this.$t('到最新版本') : ''
          }),
        confirmFn: () => {
          operateJob(data)
        }
      })
    },
    /**
     * 移除Agent
     * @param {Array} data
     */
    handleRemoveHost(data = []) {
      const deleteHost = async (data) => {
        this.loading = true
        const param = this.getDeleteHostCondition(data)
        const result = await this.removeHost(param)
        if (result) {
          this.$bkMessage({
            theme: 'success',
            message: result.fail && result.fail.length
              ? this.$t('删除完成提示', { success: result.success, fail: result.fail })
              : this.$t('删除成功')
          })
          this.initAgentList()
        } else {
          this.loading = false
        }
      }
      this.$bkInfo({
        title: this.$t('确定移除选择的主机'),
        confirmFn: () => {
          deleteHost(data)
        }
      })
    },
    /**
     * 跨页全选
     */
    handleSelectionAll() {
      bus.$emit('checked-all-agent')
    },
    /**
     * 取消跨页全选
     */
    handleClearSelection() {
      bus.$emit('unchecked-all-agent')
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
     * search select复制逻辑
     */
    handlePaste(e) {
      const [data] = e.clipboardData.items
      data.getAsString((value) => {
        const { searchSelect } = this.$refs
        let isIpType = false // 是否为IP类型
        // 已选择特定类型的情况下 - 保持原有的粘贴行为（排除IP类型的粘贴）
        if (searchSelect.input && !isEmpty(searchSelect.input.value)) {
          const val = searchSelect.input.value
          isIpType = /ip/i.test(searchSelect.input.value)
          Object.assign(e.target, { innerText: isIpType ? '' : val + value }) // 数据清空或合并
          this.$refs.searchSelect.handleInputChange(e) // 回填并响应数据
          this.$refs.searchSelect.handleInputFocus(e) // contenteditable类型 - 光标移动到最后
        } else {
          isIpType = true
        }
        if (isIpType) {
          const str = value.replace(/;+|；+|_+|\\+|，+|,+|、+|\s+/g, ',').replace(/,+/g, ' ')
            .trim()
          const splitCode = ['，', ' ', '、', ',', '\n'].find(split => str.indexOf(split) > 0) || '\n'
          const tmpStr = str.trim().split(splitCode)
          const isIp = tmpStr.every(item => this.ipRegx.test(item))
          if (isIp) {
            this.handlePushValue('inner_ip', tmpStr.map(ip => ({
              id: ip,
              name: ip
            })))
          } else {
            this.searchSelectValue.push({
              id: str.trim().replace('\n', ''),
              name: str.trim().replace('\n', '')
            })
          }
        }
      })
    },
    /**
     * agent 版本排序
     */
    handleSort({ prop, order }) {
      Object.assign(this.sortData, {
        head: prop,
        sort_type: order === 'ascending' ? 'ASC' : 'DEC'
      })
      this.handlePageChange()
    },
    /**
     * 单元格样式
     */
    handleCellClass({ column }) {
      if (column.property && column.property === 'topology') {
        return 'col-topology'
      }
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
     * 合并最后两列
     */
    colspanHandle({ column }) {
      if (column.property === 'colspaOpera') {
        return [1, 2]
      } if (column.property === 'colspaSetting') {
        return [0, 0]
      }
    },
    getBatchMenuStaus(item) {
      return !this.isSelectedAllPages && !(['reinstall', 'log'].includes(item.id))
        ? this.selection.every(row => row.status === 'not_installed')
        : false
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

.tips-enter-active {
  transition: opacity .5s;
}
.tips-enter,
.tips-leave-to {
  opacity: 0;
}
>>> .bk-icon.right-icon {
  margin-left: 6px;
}
>>> .bk-table-row .is-first .cell {
  text-align: left;
}
>>> .bk-dropdown-list {
  max-height: none;
  li {
    cursor: pointer;
    &.disabled a {
      color: #c4c6cc;
      cursor: not-allowed;
    }
  }
}
>>> .bk-table tr:hover {
  .col-num {
    background: #dcdee5;
  }
}
>>> .icon-down-wrapper {
  position: relative;
  left: 3px;
}
.agent {
  min-height: calc(100vh - 112px);
  padding-bottom: 82px;
  &-operate {
    @mixin layout-flex row, center, space-between;
    &-left {
      @mixin layout-flex row;
      .dropdown-btn {
        >>> .bk-button-loading {
          /* stylelint-disable-next-line declaration-no-important */
          background-color: unset !important;
          * {
            /* stylelint-disable-next-line declaration-no-important */
            background-color: #63656e !important;
          }
        }
      }
      .setup-btn {
        min-width: 130px;
        transition: none;
        .setup-btn-icon {
          transition: transform .2s ease;
        }
        &[disabled],
        >>> &[disabled] * {
          /* stylelint-disable-next-line declaration-no-important */
          border-color: #dcdee5 !important;

          /* stylelint-disable-next-line declaration-no-important */
          color: #fff!important;

          /* stylelint-disable-next-line declaration-no-important */
          background-color: #dcdee5!important;
        }
      }
      .item-disabled {
        cursor: not-allowed;
        color: #c4c6cc;
        &:hover {
          background: transparent;
          color: #c4c6cc;
        }
      }
      .left-select {
        width: 200px;
        background: #fff;
      }
      .topo-cascade {
        min-width: 200px;
        height: 32px;
        background: #fff;
        >>> .bk-tooltip-ref {
          width: 100%;
        }
      }
    }
    &-right {
      flex-basis: 400px;
      .right-select {
        background: #fff;
      }
    }
  }
  &-content {
    >>> .col-topology {
      .cell {
        padding-right: 0;
      }
    }
    .col-topo {
      cursor: default;
    }
    .col-num {
      background: #e6e8f0;
      border-radius: 8px;
      height: 14px;
      padding: 0 6px;
      margin-left: -15px;
    }
    .col-operate {
      .reinstall {
        padding: 0;
        min-width: 24px;
      }
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
    .selection-tips {
      height: 30px;
      background: #ebecf0;

      @mixin layout-flex row, center, center;
      .tips-num {
        font-weight: bold;
      }
      .tips-btn {
        font-size: 12px;
        margin-left: 5px;
      }
    }
    .pagination {
      margin-top: -1px;
      padding: 14px 16px;
      height: 60px;
      border: 1px solid #dcdee5;
      background: #fff;
      >>> .bk-page-total-count {
        color: #63656e;
      }
      >>> .bk-page-count {
        margin-top: -1px;
      }
    }
  }
}
</style>

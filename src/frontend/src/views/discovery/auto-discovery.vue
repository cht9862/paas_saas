<template>
    <section :class="['auto-discovery-wrapper', { 'footer-fixed': isScroll && tableList.length }]">
        <Tips :list="tipsList" class="mb20"></Tips>
        <div class="filter clearfix">
            <div class="bk-button-group fl">
                <bk-button :class="['minw100', { 'is-selected': filterType === 'pending' }]" @click="handleTypeChange">{{ $t('待处理') }}</bk-button>
                <bk-button :class="['minw100', { 'is-selected': filterType === 'ignored' }]" @click="handleTypeChange">{{ $t('已忽略') }}</bk-button>
            </div>
            <bk-search-select class="discovery-filter-select"
                              filter
                              :placeholder="$t('请选择条件搜索')"
                              :data="filterData"
                              v-model="selected">
                              <!-- :filter-menu-method="handleFilterMenuMethod"
                :filter-child-menu-method="handleFilterChildeMenuMethod"> -->
            </bk-search-select>
        </div>
        <section class="discovery-table-wrapper" v-bkloading="{ isLoading: loading }">
            <bk-table
                ref="discoveryTable"
                :data="tableList"
                row-key="id"
                size="small"
                :row-style="getRowStyle"
                @select="handleTableSelect"
                @select-all="handleTableSelect">
                <bk-table-column type="selection" width="60" align="center"></bk-table-column>
                <bk-table-column label="IP" prop="ip" :resizable="false"></bk-table-column>
                <bk-table-column :label="$t('云区域_ID')" :resizable="false">
                    <template #default="{ row }">
                        {{ `${ row.cloudName } (${ row.cloudId })` }}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('操作系统')" prop="sys" :resizable="false" :render-header="renderFilterHeader"></bk-table-column>
                <bk-table-column :label="$t('Agent状态')" prop="status" :resizable="false" :render-header="renderFilterHeader">
                    <template #default="{ row }">
                        <div class="col-status" v-if="statusMap[row.status]">
                            <span :class="'status-' + row.status"></span>
                            <span>{{ statusMap[row.status].name }}</span>
                        </div>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('Agent版本')" prop="version" :resizable="false" :render-header="renderFilterHeader"></bk-table-column>
                <bk-table-column :label="$t('发现时间')" prop="find_time" :resizable="false"></bk-table-column>
                <bk-table-column :label="$t('操作')" :resizable="false" :width="180">
                    <template #default="{ row }" v-if="filterType === 'pending'">
                        <bk-button theme="primary" text ext-cls="col-operate-btn" @click.stop="handleCommit('enter', row)">{{ $t('确认录入') }}</bk-button>
                        <bk-button theme="primary" text ext-cls="col-operate-btn" @click.stop="handleCommit('ignore', row)">{{ $t('忽略') }}</bk-button>
                    </template>
                    <template #default="{ row }" v-else>
                        <bk-button theme="primary" text ext-cls="col-operate-btn" @click.stop="handleCommit('restore', row)">{{ $t('恢复') }}</bk-button>
                    </template>
                </bk-table-column>
            </bk-table>
            <section class="auto-discovery-footer" v-if="tableList.length">
                <template v-if="filterType === 'pending'">
                    <bk-button class="nodeman-primary-btn" :disabled="!selectTable.length" theme="primary" @click.stop="handleCommit('enterMup')">{{ $t('确认录入') }}</bk-button>
                    <bk-button class="minw80" :disabled="!selectTable.length" @click.stop="handleCommit('ignoreMup')">{{ $t('忽略') }}</bk-button>
                </template>
                <template v-else>
                    <bk-button class="nodeman-primary-btn" theme="primary" :disabled="!selectTable.length" @click.stop="handleCommit('restoreMup')">{{ $t('恢复') }}</bk-button>
                </template>
            </section>
        </section>
    </section>
</template>

<script>
import { mapActions } from 'vuex'
import Tips from '@/components/tips/tips.vue'
import { mixins } from '@/components/filter-header/table-header-mixins'
import { addListener, removeListener } from 'resize-detector'
import { debounce } from '@/common/util'

export default {
  name: 'AutoDiscovery',
  components: {
    Tips
  },
  mixins: [mixins],
  data() {
    return {
      loading: true,
      tipsList: this.$t('自动发现topTip'),
      // 监听界面滚动
      listenResize: null,
      isScroll: false,
      filterType: 'pending',
      filterData: [
        { name: this.$t('IP地址'), type: 'ip', id: '1' },
        { name: this.$t('操作系统'), type: 'sys', id: '2', multiable: true, children: [
          { id: 'windows', name: 'Windows', checked: false }, { id: 'linux', name: 'Linux', checked: false }
        ] },
        { name: this.$t('Agent状态'), type: 'status', id: '3', multiable: true, children: [
          { id: 'normal', name: this.$t('正常'), checked: false }, { id: 'error', name: this.$t('异常'), checked: false }
        ] },
        { name: this.$t('Agent版本'), type: 'version', id: '4', multiable: true, children: [
          { id: '1.6.3', name: '1.6.3', checked: false }
        ] }
      ],
      // 表格勾选列表
      selectTable: [],
      // 联动搜索框
      selected: [],
      // 未拆分状态的表格
      tableAllList: [],
      operationMap: {
        ignore: this.$t('是否忽略此IP'),
        ignoreMup: this.$t('是否忽略选中的IP'),
        enter: this.$t('是否录入此IP'),
        enterMup: this.$t('是否录入选中的IP'),
        restore: this.$t('是否恢复此IP'),
        restoreMup: this.$t('是否恢复选中的IP')
      },
      statusMap: {
        normal: {
          name: this.$t('正常'),
          status: 'normal'
        },
        error: {
          name: this.$t('异常'),
          status: 'error'
        },
        unknown: {
          name: this.$t('未知'),
          status: 'unknown'
        }
      }
    }
  },
  computed: {
    // 表格展示
    tableList() {
      return this.tableAllList.filter(item => item.type === this.filterType)
    }
  },
  mounted() {
    this.requesTableList()
    this.listenResize = debounce(300, v => this.handleResize(v))
    addListener(this.$el, this.listenResize)
  },
  beforeDestroy() {
    removeListener(this.$el, this.listenResize)
  },
  methods: {
    ...mapActions('discovery', ['requestDiscoveryList', 'setHostIdleStatus']),
    handleResize() {
      // 60：三级导航的高度  52： 一级导航高度
      this.isScroll = this.$el.scrollHeight + 60 > this.$root.$el.clientHeight - 52
    },
    async handleCommit(type, row) {
      // Object.assign(this.dialog, {
      //     typeOpera: type,
      //     content: this.operationMap[type],
      //     data: row
      // })
      this.loading = true
      const data = type.includes('Mup') ? this.selectTable : [row]
      const params = { type, data }
      const res = await this.$store.dispatch('discovery/setHostIdleStatus', params)
      // ignore, enter, restore
      if (type.includes('ignore') || type.includes('restore')) { // 忽略 或 恢复
        this.tableAllList.forEach((host) => {
          if (data.find(item => item.id === host.id)) {
            host.type = type.includes('ignore') ? 'ignored' : 'pending'
          }
        })
      }
      if (type.includes('enter')) { // 录入
        this.tableAllList = this.tableAllList.filter(row => !(data.find(host => row.id === host.id)))
      }
      this.$refs.discoveryTable.clearSelection()
      if (res.message) {
        this.$bkMessage({
          theme: 'success',
          message: res.message
        })
      }
      this.loading = false
    },
    async requesTableList() {
      this.loading = true
      const res = await this.requestDiscoveryList()
      this.tableAllList.splice(0, this.tableAllList.length, ...res.data)
      this.loading = false
    },
    // 切换tab
    handleTypeChange() {
      this.filterType = this.filterType === 'pending' ? 'ignored' : 'pending'
      this.selected.splice(0, this.selected.length)
      this.clearTableSelect()
    },
    // 表格选中事件
    handleTableSelect(select) {
      this.selectTable.splice(0, this.selectTable.length, ...select)
    },
    getRowStyle() {
      return this.filterType === 'pending' ? {} : { color: '#979BA5' }
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

@define-mixin col-row-status $color {
  margin-right: 10px;
  margin-top: -1px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $color;
}

.auto-discovery-wrapper {
  .filter {
    margin-bottom: 14px;
  }
  .minw100 {
    min-width: 100px;
  }
  .minw80 {
    min-width: 80px;
  }
  .discovery-filter-select {
    float: right;
    width: 500px;
    background: #fff;
  }
  .discovery-table-wrapper {
    position: relative;
    padding-bottom: 62px;
  }
  .col-operate-btn {
    padding: 0;
    & + .col-operate-btn {
      margin-left: 10px;
    }
  }
  .auto-discovery-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    margin-top: 30px;
    width: 100%;
    text-align: center;
    font-size: 0;
    .bk-button + .bk-button {
      margin-left: 10px;
    }
  }
  &.footer-fixed {
    .auto-discovery-footer {
      position: fixed;
      margin: 0;
      padding: 10px 0;
      border-top: 1px solid #e2e2e2;
      background: #fff;
      z-index: 5;
    }
  }
  .col-status {
    @mixin layout-flex row, center;
    .status-normal {
      @mixin col-row-status #2DCB56;
    }
    .status-error {
      @mixin col-row-status #EA3636;
    }
    .status-unknown {
      @mixin col-row-status #DCDEE5;
    }
  }
}
</style>

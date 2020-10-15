<template>
  <article class="cloud-manager">
    <!--提示-->
    <section class="cloud-tips mb20">
      <tips :list="tipsList"></tips>
    </section>
    <!--内容区域-->
    <section class="cloud-content">
      <div class="content-header mb15">
        <!--创建云区域-->
        <auth-component
          tag="div"
          :auth="{
            permission: authority.create_action,
            apply_info: [{ action: 'cloud_create' }]
          }">
          <template slot-scope="{ disabled }">
            <bk-button
              theme="primary"
              :disabled="disabled"
              ext-cls="header-btn"
              @click="handleAddCloud">
              {{ $t("新建") }}
            </bk-button>
          </template>
        </auth-component>
        <!--搜索云区域-->
        <bk-input
          :placeholder="$t('搜索名称')"
          right-icon="bk-icon icon-search"
          ext-cls="header-input"
          v-model="searchValue"
          @change="handleValueChange">
        </bk-input>
      </div>
      <!--云区域列表-->
      <div class="content-table" v-bkloading="{ isLoading: loading }">
        <bk-table
          :class="`head-customize-table ${ fontSize }`"
          :pagination="pagination"
          :span-method="colspanHandle"
          :data="tableData"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange">
          <bk-table-column :label="$t('云区域名称')" prop="cloudNameCopy" sortable show-overflow-tooltip>
            <template #default="{ row }">
              <auth-component
                class="auth-inline"
                tag="div"
                :auth="{
                  permission: row.view,
                  apply_info: [{
                    action: 'cloud_view',
                    instance_id: row.bkCloudId,
                    instance_name: row.bkCloudName
                  }]
                }">
                <template slot-scope="{ disabled }">
                  <span
                    class="text-btn"
                    :disabled="disabled"
                    @click="handleGotoDetail(row)">
                    {{ row.bkCloudName }}
                  </span>
                </template>
              </auth-component>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('云区域ID')" prop="bkCloudId"></bk-table-column>
          <bk-table-column align="right" width="55" :resizable="false">
            <template #default="{ row }">
              <img :src="`data:image/svg+xml;base64,${row.ispIcon}`" class="col-svg" v-if="row.ispIcon">
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('云服务商')" prop="ispName" sortable show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.ispName || '--' }}
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('Proxy数量')"
            width="150"
            prop="proxyCount"
            align="right"
            :resizable="false"
            sortable>
            <template #default="{ row }">
              <auth-component
                v-if="row.proxyCount"
                class="auth-inline"
                tag="div"
                :auth="{
                  permission: row.view,
                  apply_info: [{
                    action: 'cloud_view',
                    instance_id: row.bkCloudId,
                    instance_name: row.bkCloudName
                  }]
                }">
                <template slot-scope="{ disabled }">
                  <bk-button ext-cls="col-btn"
                             theme="primary"
                             text
                             :disabled="disabled"
                             @click="handleGotoDetail(row)">
                    {{ row.proxyCount }}
                  </bk-button>
                </template>
              </auth-component>
              <auth-component
                v-else
                class="auth-inline"
                tag="span"
                :auth="{
                  permission: !!proxyOperateList.length,
                  apply_info: [{ action: 'proxy_operate' }]
                }">
                <template slot-scope="{ disabled }">
                  <span class="install-proxy" :disabled="disabled" v-bk-tooltips="$t('点击前往安装')">
                    <i class="install-proxy-icon nodeman-icon nc-minus"></i>
                    <span @click="handleInstallProxy(row)">{{ $t('未安装') }}</span>
                  </span>
                </template>
              </auth-component>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('节点数量')" prop="nodeCount" align="right" :resizable="false" sortable>
            <template #default="{ row }">
              <span v-if="row.nodeCount" class="text-btn" @click="handleGotoAgent(row)">{{ row.nodeCount }}</span>
              <span v-else>0</span>
            </template>
          </bk-table-column>
          <bk-table-column align="right" min-width="40"></bk-table-column>
          <bk-table-column :label="$t('接入点')" prop="apName" show-overflow-tooltip></bk-table-column>
          <bk-table-column
            prop="colspaOpera"
            :label="$t('操作')"
            :width="fontSize === 'large' ? 175 : 155"
            :resizable="false">
            <template #default="{ row }">
              <auth-component
                tag="div"
                :auth="{
                  permission: !!proxyOperateList.length,
                  apply_info: row.view ? [{ action: 'proxy_operate' }] : [
                    {
                      action: 'proxy_operate'
                    },
                    {
                      action: 'cloud_view',
                      instance_id: row.bkCloudId,
                      instance_name: row.bkCloudName
                    }
                  ]
                }">
                <template slot-scope="{ disabled }">
                  <bk-button
                    text
                    ext-cls="col-btn"
                    theme="primary"
                    :disabled="disabled"
                    @click="handleInstallProxy(row)">
                    {{ $t("Proxy安装") }}
                  </bk-button>
                </template>
              </auth-component>
              <auth-component
                class="auth-inline"
                tag="div"
                :auth="{
                  permission: row.edit,
                  apply_info: [{
                    action: 'cloud_edit',
                    instance_id: row.bkCloudId,
                    instance_name: row.bkCloudName
                  }]
                }">
                <template slot-scope="{ disabled }">
                  <bk-button
                    ext-cls="col-btn ml10"
                    theme="primary" text
                    :disabled="disabled"
                    @click="handleEdit(row)">
                    {{ $t("编辑") }}
                  </bk-button>
                </template>
              </auth-component>
              <auth-component
                class="auth-inline"
                tag="div"
                :auth="{
                  permission: row.delete,
                  apply_info: [{
                    action: 'cloud_delete',
                    instance_id: row.bkCloudId,
                    instance_name: row.bkCloudName
                  }]
                }">
                <template slot="default" slot-scope="{ disabled }">
                  <bk-popover :content="deleteTips" :disabled="!(row.proxyCount || row.nodeCount)" class="ml10">
                    <bk-button ext-cls="col-btn"
                               :disabled="disabled || !!(row.proxyCount || row.nodeCount)"
                               theme="primary"
                               text
                               @click="handleDelete(row)">
                      {{ $t("删除") }}
                    </bk-button>
                  </bk-popover>
                </template>
              </auth-component>
            </template>
          </bk-table-column>
          <!--自定义字段显示列-->
          <bk-table-column
            key="setting"
            prop="colspaSetting"
            :render-header="renderHeader"
            width="42"
            :resizable="false">
          </bk-table-column>
        </bk-table>
      </div>
    </section>
  </article>
</template>
<script>
import Tips from '@/components/tips/tips.vue'
import { mapActions, mapGetters } from 'vuex'
import { debounce } from '@/common/util'
import ColumnSetting from '@/components/column-setting/column-setting'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import CloudState from '@/store/modules/cloud'

export default {
  name: 'cloud-manager',
  components: {
    Tips
  },
  props: {
    // 编辑ID
    id: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      // 提示信息
      tipsList: [
        this.$t('云区域管理提示一')
      ],
      // 表格属性
      table: {
        list: [],
        data: []
      },
      pagination: {
        current: 1,
        limit: 20,
        count: 0
      },
      // 搜索值
      searchValue: '',
      // 支持搜索的字段
      searchParams: [
        'bkCloudName',
        'bkCloudId',
        'ispName',
        'apName'
      ],
      // 搜索防抖
      handleValueChange() {},
      // 表格加载
      loading: false,
      // 删除操作禁用提示
      deleteTips: this.$t('删除禁用提示')
    }
  },
  computed: {
    ...mapGetters(['fontSize', 'permissionSwitch']),
    ...mapGetters('cloud', ['authority']),
    tableData() {
      const { current, limit } = this.pagination
      const start = (current - 1) * limit
      return this.table.data.slice(start, start + limit)
    },
    proxyOperateList() {
      return this.authority.proxy_operate || []
    }
  },
  created() {
    this.handleInit()
  },
  mounted() {
    this.handleValueChange = debounce(300, this.handleSearch)
  },
  methods: {
    ...mapActions('cloud', ['getCloudList', 'deleteCloud']),
    /**
     * 初始化
     */
    async handleInit() {
      this.loading = true
      const promiseAll = [this.getCloudList()]
      const [data] = await Promise.all(promiseAll)
      if (this.permissionSwitch) {
        data.sort((a, b) => Number(b.view) - Number(a.view))
      }
      // 利用组件自带的排序给云区域名称做一个不区分大小写的排序优化
      this.table.list = data.map(item => ({
        ...item,
        cloudNameCopy: item.bkCloudName.toLocaleLowerCase()
      }))
      this.handleSearch()
      this.loading = false
    },
    /**
     * 前端搜索
     */
    handleSearch() {
      this.table.data = this.searchValue.length === 0
        ? this.table.list
        : this.table.list.filter(item => this.searchParams.some((param) => {
          const value = this.searchValue.toLocaleLowerCase()
          return item[param] && ~item[param].toString().toLocaleLowerCase()
            .indexOf(value)
        }))
      this.pagination.current = 1
      this.pagination.count = this.table.data.length
    },
    /**
     * 编辑
     * @param {Object} row
     */
    handleEdit(row) {
      this.$router.push({
        name: 'addCloudManager',
        params: {
          id: row.bkCloudId,
          type: 'edit'
        }
      })
    },
    /**
     * 删除
     * @param {Object} row
     */
    handleDelete(row) {
      const deleteCloud = async (id) => {
        this.loading = true
        const result = await this.deleteCloud(id)
        if (result) {
          this.$bkMessage({
            theme: 'success',
            message: this.$t('删除成功')
          })
          this.handleInit()
        } else {
          this.loading = false
        }
      }
      this.$bkInfo({
        title: this.$t('确定删除该云区域'),
        confirmFn: () => {
          deleteCloud(row.bkCloudId)
        }
      })
    },
    /**
     * 添加云区域
     */
    handleAddCloud() {
      this.$router.push({
        name: 'addCloudManager',
        params: {
          type: 'add'
        }
      })
    },
    /**
     * 跳转详情
     * @param {Object} row
     */
    handleGotoDetail(row) {
      this.$router.push({
        name: 'cloudManagerDetail',
        params: {
          id: row.bkCloudId
        }
      })
    },
    /**
     * 新增Proxy
     */
    handleInstallProxy(row) {
      this.$router.push({
        name: 'setupCloudManager',
        params: {
          type: 'create',
          id: row.bkCloudId
        }
      })
    },
    /**
     * 自定义字段显示列
     * @param {createElement 函数} h 渲染函数
     */
    renderHeader() {
      return <ColumnSetting></ColumnSetting>
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
    /**
     * 跳转agent并筛选出云区域
     */
    handleGotoAgent(row) {
      this.$router.push({
        name: 'agentStatus',
        params: {
          cloud: {
            id: row.bkCloudId,
            name: row.bkCloudName
          }
        }
      })
    },
    handlePageChange(newPage) {
      this.pagination.current = newPage || 1
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit || 20
      this.handlePageChange()
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";
@import "@/css/variable.css";

>>> .bk-table-header th.is-right.is-sortable .cell {
  position: relative;
  left: 20px;
}
>>> .bk-table th :hover {
  background-color: unset;
}
.cloud-manager {
  padding-bottom: 20px;
}
.content-header {
  @mixin layout-flex row, center, space-between;
  .header-btn {
    width: 120px;
  }
  .header-input {
    width: 500px;
  }
}
.content-table {
  .col-svg {
    margin-top: 5px;
    height: 20px;
    margin-right: -15px;
  }
  .col-btn {
    padding: 0;
  }
  .text-btn {
    color: #3a84ff;
    cursor: pointer;
    &[disabled] {
      color: #dcdee5;
    }
  }
  .auth-inline {
    display: inline;
  }
  .install-proxy {
    cursor: pointer;
    &-icon {
      font-size: 14px;
      color: #c4c6cc;
    }
    &:hover {
      > * {
        color: #3a84ff;
      }
    }
    &[disabled] {
      color: #dcdee5;
    }
  }
}
</style>

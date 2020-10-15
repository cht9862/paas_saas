<template>
    <bk-table show-overflow-tooltip :data="guideTable">
        <bk-table-column prop="source" :label="$t('源地址')" show-overflow-tooltip>
            <template #default="{ row }">
                <template v-if="row.sourceKey === 'agent'">
                    {{ row.source }}
                    <bk-popover v-if="row.sourceRe && detail[row.sourceKey]" theme="light" placement="top" :content="$t('复制')">
                        <i18n class="text-link" path="agent数量" tag="span" @click.stop="handleCopy(row.sourceKey)">
                            <template #num>
                                <font color="3A84FF">{{ detail[row.sourceKey] }}</font>
                            </template>
                        </i18n>
                    </bk-popover>
                </template>
                <bk-popover
                    v-else
                    theme="light strategy-table"
                    placement="top"
                    :disabled="!(detail[row.sourceKey] || (row.sourceKey === 'proxy' && notAvailableProxy))">
                    <span :class="{ 'text-link': detail[row.sourceKey] }" @click.stop="handleCopy(row.sourceKey)">{{ row.source }}</span>
                    <ul slot="content">
                        <template v-if="row.sourceKey === 'proxy' && notAvailableProxy">
                            <li>{{ $t('该云区域下暂未安装Proxy') }}</li>
                            <li class="mt5">
                                <bk-link theme="primary" @click.stop="handleGotoProxy">{{ $t('前往安装') }}</bk-link>
                            </li>
                        </template>
                        <template v-else>
                            <li class="" v-for="ip in area[row.sourceKey]" :key="ip">{{ ip }}</li>
                            <li class="mt5">
                                <bk-link theme="primary" @click.stop="handleCopy(row.sourceKey)">{{ $t('点击复制') }}</bk-link>
                            </li>
                        </template>
                    </ul>
                </bk-popover>
            </template>
        </bk-table-column>
        <bk-table-column prop="targetAdress" :label="$t('目标地址')" show-overflow-tooltip>
            <template #default="{ row }">
                <template v-if="row.targetKey === 'agent'">
                    {{ row.targetAdress }}
                    <bk-popover v-if="row.targetRe && detail[row.targetKey]" theme="light" placement="top" :content="$t('复制')">
                        <i18n class="text-link" path="agent数量" tag="span" @click.stop="handleCopy(row.targetKey)">
                            <template #num>
                                <font color="3A84FF">{{ detail[row.targetKey] }}</font>
                            </template>
                        </i18n>
                    </bk-popover>
                </template>
                <bk-popover v-else theme="light strategy-table" placement="top" :disabled="!(detail[row.targetKey] || (row.targetKey === 'proxy' && notAvailableProxy))">
                    <span :class="{ 'text-link': detail[row.targetKey] }" @click.stop="handleCopy(row.targetKey)">{{ row.targetAdress }}</span>
                    <ul slot="content">
                        <template v-if="row.targetKey === 'proxy' && notAvailableProxy">
                            <li>{{ $t('该云区域下暂未安装Proxy') }}</li>
                            <li class="mt5">
                                <bk-link theme="primary" @click.stop="handleGotoProxy">{{ $t('前往安装') }}</bk-link>
                            </li>
                        </template>
                        <template v-else>
                            <li class="" v-for="ip in area[row.targetKey]" :key="ip">{{ ip }}</li>
                            <li class="mt5">
                                <bk-link theme="primary" @click.stop="handleCopy(row.targetKey)">{{ $t('点击复制') }}</bk-link>
                            </li>
                        </template>
                    </ul>
                </bk-popover>
            </template>
        </bk-table-column>
        <bk-table-column prop="port" :label="$t('端口')" show-overflow-tooltip></bk-table-column>
        <bk-table-column prop="protocol" :label="$t('协议')" show-overflow-tooltip></bk-table-column>
        <bk-table-column prop="use" :label="$t('用途')" show-overflow-tooltip></bk-table-column>
        <bk-table-column prop="remarks" :label="$t('备注')" show-overflow-tooltip></bk-table-column>
    </bk-table>
</template>

<script>
import { copyText } from '@/common/util'

export default {
  name: 'StrategyTable',
  props: {
    hostType: {
      type: String,
      default: 'Agent'
    },
    area: {
      type: Object,
      default: () => ({
        dataserver: [],
        taskserver: [],
        btfileserver: [],
        proxy: [],
        zk: [],
        agent: []
      })
    }
  },
  data() {
    return {
      sourceMap: ['Agent', 'GSE_btsvr'],
      table: {
        Agent: [
          {
            source: 'Agent',
            targetAdress: this.$t('节点管理后台'),
            protocol: 'TCP',
            port: '80,443',
            use: this.$t('TCP上报日志获取配置'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'agent'
          },
          {
            source: 'Agent',
            targetAdress: 'zk',
            protocol: 'TCP',
            port: '2181',
            use: this.$t('获取配置'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'zk'
          },
          {
            source: 'Agent',
            targetAdress: 'GSE_task',
            protocol: 'TCP',
            port: '48668',
            use: this.$t('任务服务端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'taskserver'
          },
          {
            source: 'Agent',
            targetAdress: 'GSE_data',
            protocol: 'TCP',
            port: '58625',
            use: this.$t('数据上报端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'dataserver'
          },
          {
            source: 'Agent',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP',
            port: '58925',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'btfileserver'
          },
          {
            source: 'Agent',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'btfileserver'
          },
          {
            source: 'Agent',
            targetAdress: 'GSE_btsvr',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'btfileserver'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'Agent',
            protocol: 'TCP,UDP',
            port: '60020-60030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'agent'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP',
            port: '58930',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'btfileserver'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'btfileserver'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'GSE_btsvr',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'btfileserver'
          },
          {
            source: 'Agent',
            targetAdress: 'Agent',
            protocol: 'TCP,UDP',
            port: '60020-60030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'agent'
          },
          {
            source: 'Agent',
            targetAdress: '',
            protocol: '',
            port: this.$t('监听随机端口'),
            use: this.$t('BT传输可不开通'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'agent'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: '',
            protocol: '',
            port: this.$t('监听随机端口'),
            use: this.$t('BT传输可不开通'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'btfileserver'
          }
        ],
        Pagent: [
          {
            source: 'Agent',
            targetAdress: 'Proxy',
            protocol: 'TCP',
            port: '17980,17981',
            use: this.$t('nginx下载nginx代理'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Agent',
            targetAdress: 'Proxy(GSE_agent)',
            protocol: 'TCP',
            port: '48668',
            use: this.$t('任务服务端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Agent',
            targetAdress: 'Proxy(GSE_transit)',
            protocol: 'TCP',
            port: '58625',
            use: this.$t('数据上报端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Agent',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP',
            port: '58925',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Agent',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Agent',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'Agent',
            protocol: 'TCP,UDP',
            port: '60020-60030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceKey: 'proxy',
            targetKey: 'agent'
          },
          {
            source: 'Agent',
            targetAdress: 'Agent',
            protocol: 'TCP,UDP',
            port: '60020-60030',
            use: this.$t('BT传输'),
            remarks: this.$t('同一子网'),
            sourceRe: true,
            targetRe: true,
            sourceKey: 'agent',
            targetKey: 'agent'
          },
          {
            source: 'Agent',
            targetAdress: '',
            protocol: '',
            port: this.$t('监听随机端口'),
            use: this.$t('BT传输可不开通'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'agent'
          }
        ],
        Proxy: [
          {
            source: 'Proxy(GSE_agent)',
            targetAdress: 'GSE_task',
            protocol: 'TCP',
            port: '48668',
            use: this.$t('任务服务端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'taskserver'
          },
          {
            source: 'Proxy(GSE_transit)',
            targetAdress: 'GSE_data',
            protocol: 'TCP',
            port: '58625',
            use: this.$t('数据上报端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'dataserver'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP',
            port: '58930',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'btfileserver'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'GSE_btsvr',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'btfileserver'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'GSE_btsvr',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'btfileserver'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP',
            port: '58930',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'proxy'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'proxy'
          },
          {
            source: 'GSE_btsvr',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'btfileserver',
            targetKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP',
            port: '58930',
            use: this.$t('BT传输'),
            remarks: this.$t('同一子网'),
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'TCP,UDP',
            port: '10020',
            use: this.$t('BT传输'),
            remarks: this.$t('同一子网'),
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: 'Proxy(GSE_btsvr)',
            protocol: 'UDP',
            port: '10030',
            use: this.$t('BT传输'),
            remarks: this.$t('同一子网'),
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_opts)',
            targetAdress: 'GSE_ops',
            protocol: 'TCP',
            port: '58725',
            use: this.$t('ping告警数据上报端口'),
            remarks: '',
            sourceRe: true,
            targetRe: true,
            sourceKey: 'proxy',
            targetKey: 'dataserver'
          },
          {
            source: 'Proxy(GSE_agent)',
            targetAdress: '',
            protocol: '',
            port: this.$t('监听随机端口'),
            use: this.$t('BT传输可不开通'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'proxy'
          },
          {
            source: 'Proxy(GSE_btsvr)',
            targetAdress: '',
            protocol: '',
            port: this.$t('监听随机端口'),
            use: this.$t('BT传输可不开通'),
            remarks: '',
            sourceRe: true,
            sourceKey: 'proxy'
          }
        ]
      }
    }
  },
  computed: {
    guideTable() {
      return this.table[this.hostType]
    },
    detail() {
      return {
        /**
         * Agent: agent, zk, dataserver, taskserver, btfileserver
         * Pagent: agent, proxy
         * Proxy: proxy, dataserver, taskserver, btfileserver
         */
        agent: this.area.agent.length,
        zk: this.area.zk.length,
        dataserver: this.area.dataserver.length,
        taskserver: this.area.taskserver.length,
        btfileserver: this.area.btfileserver.length,
        proxy: this.area.proxy.length
      }
    },
    // 云区域下无可用的proxy
    notAvailableProxy() {
      return this.hostType === 'Pagent' && (this.area.bk_cloud_id || this.area.bk_cloud_id === 0) && !this.detail.proxy
    }
  },
  methods: {
    getFontHtml(param) {
      return `<font color="3A84FF">${param}</font>`
    },
    handleCopy(str) {
      if (this.detail[str]) {
        const content = { theme: 'error', message: this.$t('IP复制失败') }
        const result = copyText(this.area[str].join('\n'))
        if (result) {
          Object.assign(content, {
            theme: 'success',
            message: this.$t('IP复制成功', { num: this.detail[str] })
          })
        }
        this.$bkMessage(content)
      }
    },
    handleGotoProxy() {
      if (this.area.bk_cloud_id || this.area.bk_cloud_id === 0) {
        this.$router.push({
          name: 'setupCloudManager',
          params: {
            type: 'create',
            title: this.$t('安装Proxy'),
            id: this.area.bk_cloud_id
          }
        })
      }
    }
  }
}
</script>
<style lang="scss" scoped>
    .text-link {
      cursor: pointer;
    }
</style>

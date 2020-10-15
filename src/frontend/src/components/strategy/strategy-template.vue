<template>
    <div class="operation-tips">
        <p class="operation-step" v-for="(item, index) in tipList" :key="`operation${index}`">{{ `${ index + 1 }. ${ item }` }}</p>
        <div class="cloud-panel" v-if="cloudAreaList.length">
            <RightPanel
                v-for="cloudArea in cloudAreaList" :key="cloudArea.bk_cloud_id"
                :class="['cloud-panel-item', { 'is-close': !cloudArea.collapse }]"
                :need-border="false"
                :icon-style="{ padding: '4px 4px', fontSize: '12px' }"
                collapse-color="#979BA5"
                title-bg-color="#F0F1F5"
                :collapse="cloudArea.collapse"
                :type="cloudArea.bk_cloud_name"
                @change="handleToggle">
                <div class="collapse-header" slot="title">
                    {{ `${ cloudArea.bk_cloud_name } - ${ cloudArea.ap_name }` }}
                </div>
                <div class="collapse-container" slot>
                    <StrategyTable :host-type="cloudArea.type" :area="cloudArea"></StrategyTable>
                </div>
            </RightPanel>
        </div>
        <div class="mt15" v-else>
            <StrategyTable :host-type="hostType === 'mixed' ? 'Agent' : hostType"></StrategyTable>
        </div>
    </div>
</template>

<script>
import RightPanel from '@/components/right-panel/right-panel.vue'
import StrategyTable from '@/components/strategy/strategy-table'
import { isEmpty } from '@/common/util'
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'StrategyTemplate',
  components: {
    StrategyTable,
    RightPanel
  },
  props: {
    hostType: {
      type: String,
      default: 'Agent'
    },
    // key => bk_cloud_id、inner_ip、bk_cloud_name (ap_id、ap_name)
    hostList: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      loading: true,
      cloudAreaList: []
    }
  },
  computed: {
    ...mapGetters('agent', ['apList', 'cloudList']),
    tipList() {
      if (this.hostType === 'Proxy') {
        return [
          this.$t('Agent安装Tip1'),
          this.$t('Agent安装Tip2'),
          this.$t('Agent安装Tip3')
        ]
      }
      return [
        this.$t('Proxy安装Tip1'),
        this.$t('Proxy安装Tip2')
      ]
    }
  },
  async mounted() {
    if (!this.apList.length) {
      await this.getApList()
    }
    if (!this.cloudList.length) {
      this.getCloudList()
    }
    this.formatData()
  },
  methods: {
    ...mapActions('agent', ['getApList', 'getCloudList']),
    formatData() {
      const cloudMap = this.hostList.reduce((obj, item) => {
        const idKey = item.bk_cloud_id
        const cloud = this.cloudList.find(child => child.bk_cloud_id === item.bk_cloud_id)
        const proxy = (cloud ? cloud.proxy_count : false) ? cloud.proxies : []
        let type = ''
        if (this.hostType === 'Proxy') {
          type = 'Proxy'
        } else {
          type = item.bk_cloud_id === window.PROJECT_CONFIG.DEFAULT_CLOUD ? 'Agent' : 'Pagent'
        }
        if (!isEmpty(idKey) && item.inner_ip && item.bk_cloud_name) {
          const copyItem = Object.assign({ type, proxy }, item)
          if (Object.prototype.hasOwnProperty.call(obj, idKey)) {
            obj[idKey].push(copyItem)
          } else {
            obj[idKey] = [copyItem]
          }
        }
        return obj
      }, {})
      let collapse = true
      // 填充 接入点信息、proxy信息
      this.cloudAreaList = Object.values(cloudMap).reduce((arr, children) => {
        const apMap = {}
        children.forEach((cloud) => {
          let idKey = cloud.ap_id
          let ap = this.apList.find(apItem => apItem.id === idKey)
          // 先排除掉找不到接入点的主机
          if (ap) {
            if (ap.id === -1 && this.apList.length === 2) {
              ap = this.apList.find(item => item.id !== -1)
              idKey = ap.id
            }
            if (Object.prototype.hasOwnProperty.call(apMap, idKey)) {
              apMap[idKey].agent.push(cloud.inner_ip)
            } else {
              const serverKey = cloud.type === 'Agent' ? 'inner_ip' : 'outer_ip' // Pagent 非必要
              const proxyKey = cloud.type === 'Proxy' ? 'outer_ip' : 'inner_ip' // Agent 非必要
              apMap[idKey] = {
                collapse: collapse || false,
                type: cloud.type,
                bk_cloud_id: cloud.bk_cloud_id,
                bk_cloud_name: cloud.bk_cloud_name,
                ap_id: idKey,
                ap_name: ap.name,
                zk: ap.zk_hosts.map(zk => zk.zk_ip), // 仅Agent
                btfileserver: ap.btfileserver.map(server => server[serverKey]),
                dataserver: ap.dataserver.map(server => server[serverKey]),
                taskserver: ap.taskserver.map(server => server[serverKey]),
                proxy: cloud.proxy.map(item => item[proxyKey]),
                agent: [cloud.inner_ip] // Proxy 非必要
              }
            }
            collapse = false
          }
        })
        Object.values(apMap).reduce((arrChild, item) => {
          arrChild.push(item)
          return arrChild
        }, arr)
        return arr
      }, [])
    },
    /**
     * 手风琴模式
     */
    handleToggle(value, type) {
      this.cloudAreaList.forEach((item) => {
        item.collapse = item.bk_cloud_name === type ? value : false
      })
    }
  }
}
</script>
<style lang="scss" scoped>
  .operation-step {
    line-height: 24px;
  }
  .cloud-panel {
    margin-top: 14px;
    border-top: 1px solid #dcdee5;
    border-left: 1px solid #dcdee5;
    border-right: 1px solid #dcdee5;
    .collapse-header {
      font-size: 14px;
      font-weight: 700;
      color: #63656e;
    }
    .cloud-panel-item.is-close {
      border-bottom: 1px solid #dcdee5;
    }
  }
</style>

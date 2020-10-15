<template>
    <bk-sideslider
        :is-show="show"
        :width="880"
        :title="title"
        :quick-close="true"
        :before-close="handleToggleTips">
        <StrategyTemplate v-if="show" slot="content" class="operation-tips" :host-type="hostType" :host-list="hostList"></StrategyTemplate>
    </bk-sideslider>
</template>
<script>
import StrategyTemplate from '@/components/strategy/strategy-template'

export default {
  name: 'panel-tips',
  components: {
    StrategyTemplate
  },
  model: {
    prop: 'show',
    event: 'update'
  },
  props: {
    title: {
      type: String,
      default: window.i18n.t('安装策略')
    },
    show: {
      type: Boolean,
      default: false
    },
    hostType: {
      type: String,
      default: 'Agent'
    },
    hostList: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    handleToggleTips() {
      this.$emit('update', false)
    }
  }
}
</script>
<style lang="postcss" scoped>
    @import "@/css/mixins/nodeman.css";

    .operation-tips {
      padding: 20px 30px;
      background: #fff;
    }
</style>

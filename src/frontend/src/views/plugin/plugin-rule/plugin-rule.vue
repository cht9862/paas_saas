<template>
  <div>
    <PluginRuleOperate></PluginRuleOperate>
    <PluginRuleTable class="mt15"></PluginRuleTable>
  </div>
</template>
<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import PluginRuleOperate from './plugin-rule-operate.vue'
import PluginRuleTable from './plugin-rule-table.vue'

@Component({
  name: 'plugin-rule',
  components: {
    PluginRuleOperate,
    PluginRuleTable
  }
})
export default class PluginRule extends Vue {

}
</script>

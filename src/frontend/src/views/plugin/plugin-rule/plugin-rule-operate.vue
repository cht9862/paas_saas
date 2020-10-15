<template>
  <div class="rule-operate">
    <div class="rule-operate-left">
      <bk-button theme="primary" @click="handleAddRule">{{ $t('新建策略') }}</bk-button>
      <bk-biz-select
        v-model="biz"
        class="ml10 select"
        :placeholder="$t('全部业务')"
        @change="handleBizChange">
      </bk-biz-select>
      <bk-select
        :placeholder="$t('选择部署策略')"
        class="ml10 select">
      </bk-select>
    </div>
    <div class="rule-operate-right">
      <bk-input
        :placeholder="$t('搜索插件')"
        clearable
        :right-icon="'bk-icon icon-search'"
        v-model="searchValue">
      </bk-input>
    </div>
  </div>
</template>
<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'

@Component({ name: 'plugin-rule-operate' })
export default class PluginRuleOperate extends Vue {
  private biz: (string | number)[] = []
  private searchValue = ''

  public handleBizChange() {}

  public handleAddRule() {
    this.$router.push({ name: 'addRule' })
  }
}
</script>
<style lang="postcss" scoped>
.rule-operate {
  display: flex;
  justify-content: space-between;
  &-left {
    display: flex;
    >>> .bk-select {
      background: #fff;
    }
    .select {
      width: 240px;
    }
  }
  &-right {
    flex-basis: 500px;
  }
}
</style>

<template>
  <bk-form ref="form">
    <bk-form-item
      :label="$t('插件功能')"
      error-display-type="normal"
      required>
    </bk-form-item>
    <bk-form-item
      :label="$t('部署策略')"
      error-display-type="normal"
      required>
    </bk-form-item>
  </bk-form>
</template>
<script lang="ts">
import { Component, Mixins, Ref } from 'vue-property-decorator'
import FormLabelMixin from '@/common/form-label-mixin'

@Component({ name: 'rule-add' })
export default class RuleAdd extends Mixins(FormLabelMixin) {
  @Ref('form') private readonly form!: Vue
  private mounted() {
    this.minWidth = 64
    this.initLabelWidth(this.form)
  }
}
</script>
<style lang="postcss" scoped>

</style>

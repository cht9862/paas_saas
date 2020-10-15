<template>
  <component
    class="auth-box"
    :is="tag"
    v-cursor="{
      active: isAuthorized
    }"
    @click.stop="handleAuthApplication">
    <slot :disabled="isAuthorized" class="diabled-auth"></slot>
  </component>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'
import { mapGetters } from 'vuex'
import { bus } from '@/common/bus'
import { IAuth } from '@/types/index'

@Component({
  name: 'auth-component',
  computed: mapGetters(['permissionSwitch'])
})
export default class AuthComponent extends Vue {
  @Prop({ type: Object, required: true }) private readonly auth!: IAuth
  @Prop({ default: 'span' }) private readonly tag!: string

  private permissionSwitch!: boolean
  private get isAuthorized() {
    return this.permissionSwitch && !this.auth.permission
  }
  /**
   * @param { action, instance_id, instance_name }
   */
  private handleAuthApplication() {
    if (this.isAuthorized) {
      bus.$emit('show-permission-modal', {
        apply_info: this.auth.apply_info
      })
    }
    this.$emit('click', !this.isAuthorized) // hasPermission
  }
}
</script>

<style lang="postcss" scoped>
    .auth-box {
      display: inline-block;
    }
</style>

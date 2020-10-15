<template>
    <section class="nodeman-side">
        <!--左侧导航-->
        <bk-navigation-menu
            :default-active="currentActive"
            @select="handleSelect">
            <bk-navigation-menu-item
                v-for="item in list"
                :has-child="item.children && !!item.children.length"
                :group="item.group"
                :key="item.title"
                :icon="item.icon"
                :disabled="item.disabled"
                :id="item.name">
                <span>{{ $t(item.title) }}</span>
            </bk-navigation-menu-item>
        </bk-navigation-menu>
    </section>
</template>
<script>
const EVENT_SELECT_SUB_MENU = 'select-change'
export default {
  name: 'NavSide',
  props: {
    currentActive: {
      type: String,
      default: ''
    },
    list: {
      type: Array,
      default: () => ([])
    }
  },
  methods: {
    /**
     * router 跳转
     *
     * @param {string} name 页面组件名称
     */
    handleSelect(name) {
      if (this.$route.name === name) return
      this.$router.push({
        name
      })
      this.$emit(EVENT_SELECT_SUB_MENU, name)
    }
  }
}
</script>

<style lang="postcss" scoped>
.nodeman-side {
  color: #fff;
  >>> span.bk-icon {
    /* stylelint-disable-next-line declaration-no-important */
    font-family: "nodeman" !important;
  }
}
</style>

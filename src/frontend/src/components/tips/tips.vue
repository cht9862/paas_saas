<template>
    <article class="tips" v-show="showTips">
        <!--提示icon-->
        <section class="tips-icon">
            <i class="nodeman-icon nc-tips"></i>
        </section>
        <!--提示内容-->
        <section class="tips-content">
            <slot v-bind="{ list }">
                <ul v-if="Array.isArray(list)">
                    <li v-for="(item, index) in list" :key="index" class="tips-content-item">{{ item }}</li>
                </ul>
                <span class="tips-content-item" v-else>
                    {{ list }}
                </span>
            </slot>
            <span class="tips-content-close" text @click="handleHide" v-if="showClose">{{ $t('不再提示') }}</span>
        </section>
    </article>
</template>
<script>
export default {
  name: 'tips',
  props: {
    list: {
      type: [Array, String],
      default: () => ['提示1', '提示2']
    },
    // 是否显示关闭提示按钮
    showClose: {
      type: Boolean,
      default: false
    },
    // tips隐藏过期时间
    expire: {
      type: Number,
      default: 3600000 * 24 * 30
    },
    // 存储key
    storageKey: {
      type: String,
      default: '__nodeman_tips__'
    }
  },
  data() {
    return {
      showTips: true
    }
  },
  created() {
    this.handleInit()
  },
  methods: {
    handleInit() {
      if (window.localStorage && this.showClose) {
        const expireTime = window.localStorage.getItem(this.storageKey)
        this.showTips = new Date().getTime() > expireTime
      }
    },
    // 隐藏tips
    handleHide() {
      if (window.localStorage) {
        const dateTime = new Date().getTime() + this.expire
        window.localStorage.setItem(this.storageKey, dateTime)
        this.showTips = false
      }
    }
  }
}
</script>
<style lang="postcss" scoped>
  @import "@/css/mixins/nodeman.css";
  @import "@/css/variable.css";

  $tipsBackground: #f0f8ff;
  $tipsBorder: #c5daff;

  .tips {
    padding: 7px 15px 7px 10px;
    min-height: 32px;
    border: 1px solid $tipsBorder;
    border-radius: 2px;
    background: $tipsBackground;

    @mixin layout-flex row;
    .tips-icon {
      font-size: 16px;
      color: $primaryFontColor;

      @mixin layout-flex row;
    }
    .tips-content {
      flex: 1;
      margin-left: 8px;

      @mixin layout-flex row, flex-start, space-between;
      &-item {
        line-height: 16px;
        &:not(:first-child) {
          margin-top: 6px;
        }
      }
      &-close {
        line-height: 16px;
        font-size: 12px;
        color: #699df4;
        cursor: pointer;
      }
    }
  }
</style>

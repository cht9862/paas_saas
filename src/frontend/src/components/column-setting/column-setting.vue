<template>
    <bk-popover
        class="popover"
        theme="light table-setting"
        trigger="click"
        placement="bottom-end"
        :on-hide="handleOnHide"
        ref="popover">
        <span v-bk-tooltips.top="$t('表格展示设置')" class="col-setting">
            <i class="bk-icon icon-cog-shape"></i>
        </span>
        <template #content>
            <div class="set-filter" ref="filterPanel">
                <div class="set-filter-title">{{ $t('表格设置') }}</div>
                <ul class="set-filter-list" v-if="filterHead">
                    <li class="list-item">
                        {{ $t('字段显示设置') }}
                        <!-- <span class="list-item-tips">{{ $t('最多选8项') }}</span> -->
                    </li>
                    <li class="list-item">
                        <bk-checkbox :value="isAllChecked" @change="handleCheckedAll">{{ $t('全选') }}</bk-checkbox>
                    </li>
                    <li v-for="item in filter" :key="item.id" class="list-item">
                        <bk-checkbox
                            :value="item.checked"
                            :disabled="item.disabled"
                            @change="handleCheckedChange($event, item)">
                            {{ item.name }}
                        </bk-checkbox>
                    </li>
                </ul>
                <section class="set-font mb30" v-if="fontSetting">
                    <div class="set-font-title">
                        {{ $t('字号设置') }}
                    </div>
                    <div class="bk-button-group">
                        <bk-button
                            v-for="config in fontConfig"
                            :key="config.id"
                            :class="{ 'is-selected': config.checked }"
                            @click="fontSetHandle(config)">{{ config.name }}</bk-button>
                    </div>
                </section>
                <div class="set-filter-footer">
                    <bk-button theme="primary" class="footer-btn" @click="handleFilterConfirm">{{ $t('确认') }}</bk-button>
                    <bk-button class="ml10" @click="handleFilterCancel">{{ $t('取消') }}</bk-button>
                </div>
            </div>
        </template>
    </bk-popover>
</template>
<script>
import { mapGetters, mapMutations } from 'vuex'
import { bus } from '@/common/bus'
import { STORAGE_KEY_COL, STORAGE_KEY_FONT } from '@/config/storage-key'
export default {
  name: 'column-filter',
  props: {
    // 不同表格的区分
    localMark: {
      type: String,
      default: ''
    },
    value: {
      type: Object,
      default: () => ({})
    },
    filterHead: {
      type: Boolean,
      default: false
    },
    fontSetting: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      filter: JSON.parse(JSON.stringify(this.value)),
      fontConfig: []
    }
  },
  computed: {
    ...mapGetters(['fontList']),
    // 是否勾选所有项
    isAllChecked() {
      return Object.keys(this.filter).every((key) => {
        const item = this.filter[key]
        return item.disabled || (!item.disabled && item.checked)
      })
    }
  },
  watch: {
    value: {
      handler() {
        this.filter = JSON.parse(JSON.stringify(this.value))
      },
      deep: true
    },
    fontList: {
      handler() {
        this.fontConfig = JSON.parse(JSON.stringify(this.fontList))
      },
      deep: true
    }
  },
  created() {
    bus.$on('toggleSetting', this.togglePopover)
    this.fontConfig = JSON.parse(JSON.stringify(this.fontList))
  },
  beforDistory() {
    bus.$off('toggleSetting', this.togglePopover)
  },
  methods: {
    ...mapMutations(['setFont']),
    /**
     * 全选事件
     * @param {Boolean} v
     */
    handleCheckedAll(v) {
      Object.keys(this.filter).forEach((key) => {
        if (!this.filter[key].disabled) {
          this.filter[key].checked = v
        }
      })
    },
    /**
     * 表头列勾选事件
     * @param {Boolean} v
     * @param {Object} item
     */
    handleCheckedChange(v, item) {
      if (item) {
        item.checked = v
      }
    },
    /**
     * 设置表格字体大小
     */
    fontSetHandle(config) {
      this.fontConfig.forEach((item) => {
        item.checked = config.id === item.id
      })
    },
    /**
     * 确定
     */
    handleFilterConfirm() {
      Object.keys(this.filter).forEach((key) => {
        this.filter[key].mockChecked = this.filter[key].checked
      })
      const data = Object.keys(this.filter).reduce((obj, next) => {
        obj[next] = !!this.filter[next].mockChecked
        return obj
      }, {})
      this.setFont(this.fontConfig)
      const currFont = this.fontConfig.find(item => item.checked)
      this.handleSetStorage(data, currFont ? currFont.id : '')
      this.$emit('update', this.filter)
      this.$refs.popover && this.$refs.popover.instance.hide()
    },
    /**
     * 取消
     */
    handleFilterCancel() {
      this.$emit('cancel', this.filter)
      this.$refs.popover && this.$refs.popover.instance.hide()
    },
    /**
     * 设置存储信息
     */
    handleSetStorage(data, font) {
      try {
        window.localStorage.setItem(this.localMark + STORAGE_KEY_COL, JSON.stringify(data))
        window.localStorage.setItem(STORAGE_KEY_FONT, font)
      } catch (_) {
        this.$bkMessage({
          theme: 'error',
          message: this.$t('浏览器不支持本地存储')
        })
      }
    },
    /**
     * 弹窗显示
     */
    handleOnHide() {
      window.setTimeout(() => {
        this.filter = JSON.parse(JSON.stringify(this.value))
        this.fontConfig = JSON.parse(JSON.stringify(this.fontList))
      }, 500)
    },
    togglePopover(isShow) {
      if (this.$refs.popover) {
        if (isShow) {
          this.$refs.popover.instance.show()
        } else {
          this.handleFilterCancel()
        }
      }
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

.popover {
  cursor: pointer;

  @mixin layout-flex row, center, center;
}
.col-setting {
  margin-left: -1px;
  font-size: 14px;
  color: #979ba5;
  outline: 0;
  width: 42px;
  height: 42px;

  @mixin layout-flex row, center, center;
  &:hover {
    color: #63656f;
  }
}
</style>

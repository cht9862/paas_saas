<template>
  <div class="setup-header">
    <bk-popover theme="light" placement="top" :content="tips" :disabled="!Boolean(tips)" width="200">
      <span
        class="header-label"
        :class="{
          'header-label-required': required,
          'header-label-tips': Boolean(tips)
        }">
        {{ $t(label) }}
      </span>
    </bk-popover>
    <bk-popover
      v-if="batch"
      theme="light batch-edit"
      trigger="manual"
      placement="bottom"
      ref="batch"
      :tippy-options="{ 'hideOnClick': false }"
      :on-show="handleOnShow"
      :on-hide="handleOnHide">
      <span
        v-bk-tooltips.top="{
          'content': $t('批量编辑', { title: '' }),
          'delay': [300, 0]
        }"
        class="batch-icon nodeman-icon nc-bulk-edit"
        :class="{ 'active': isActive }"
        @click="handleBatchClick"
        v-show="isBatchIconShow">
      </span>
      <template #content>
        <div class="batch-edit">
          <template v-if="type === 'password'">
            <div class="batch-edit-title">
              {{ $t('批量编辑', { title: $t('密码') }) }}
            </div>
            <div class="batch-edit-content" v-if="isShow">
              <input-type
                v-bind="{ type: 'password' }"
                v-model="value"
                @enter="handleBatchConfirm">
              </input-type>
              <div class="tip">{{ subTitle }}</div>
            </div>
            <div class="batch-edit-title">
              {{ $t('批量编辑', { title: $t('密钥') }) }}
            </div>
            <div class="batch-edit-content" v-if="isShow">
              <input-type
                v-bind="{ type: 'file' }"
                @upload-change="handleFileChange">
              </input-type>
              <div class="tip">{{ $t('仅对密钥认证生效') }}</div>
            </div>
          </template>
          <template v-else>
            <div class="batch-edit-title">
              {{ $t('批量编辑', { title: $t(label) }) }}
            </div>
            <div class="batch-edit-content" v-if="isShow">
              <input-type
                v-bind="{
                  type: type,
                  options: options,
                  multiple: multiple,
                  appendSlot: appendSlot,
                  placeholder
                }"
                v-model="value"
                @enter="handleBatchConfirm">
              </input-type>
              <div class="tip" v-if="subTitle">{{ subTitle }}</div>
            </div>
          </template>
          <div class="batch-edit-footer">
            <bk-button text ext-cls="footer-confirm" @click="handleBatchConfirm">{{ $t('确定') }}</bk-button>
            <bk-button text ext-cls="footer-cancel" class="ml20" @click="handleBatchCancel">{{ $t('取消') }}</bk-button>
          </div>
        </div>
      </template>
    </bk-popover>
  </div>
</template>
<script>
import { bus } from '@/common/bus'
import InputType from './input-type.vue'

export default {
  name: 'table-header',
  components: {
    InputType
  },
  props: {
    // 是否有悬浮提示
    tips: {
      type: String,
      default: ''
    },
    // 表头label
    label: {
      type: String,
      default: ''
    },
    // 是否显示必填标识
    required: {
      type: Boolean,
      default: false
    },
    // 是否有批量编辑框
    batch: {
      type: Boolean,
      default: false
    },
    // 是否显示批量编辑图标
    isBatchIconShow: {
      type: Boolean,
      default: true
    },
    // 批量编辑框类型
    type: {
      type: String,
      default: ''
    },
    // 批量编辑提示信息
    subTitle: {
      type: String,
      default: ''
    },
    // 下拉框类型options
    options: {
      type: Array,
      default: () => []
    },
    multiple: {
      type: Boolean,
      default: false
    },
    placeholder: {
      type: String,
      default: ''
    },
    appendSlot: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      // 当前批量编辑icon是否激活
      isActive: false,
      value: '',
      isShow: false,
      // 密钥信息
      fileInfo: null
    }
  },
  created() {
    bus.$on('batch-btn-click', this.hidePopover)
  },
  methods: {
    handleBatchClick() {
      this.$refs.batch && this.$refs.batch.instance.show()
      this.isActive = true
      bus.$emit('batch-btn-click', this)
    },
    handleBatchConfirm() {
      this.$emit('confirm', this.value, this.fileInfo)
      this.handleBatchCancel()
    },
    handleBatchCancel() {
      this.isActive = false
      this.$refs.batch && this.$refs.batch.instance.hide()
    },
    handleOnShow() {
      this.value = ''
      this.isShow = true
    },
    handleOnHide() {
      this.isShow = false
    },
    hidePopover(instance) {
      if (instance === this) return
      this.handleBatchCancel()
    },
    handleFileChange(fileInfo) {
      this.fileInfo = fileInfo
    }
  }
}
</script>
<style lang="postcss" scoped>
  @import "@/css/mixins/nodeman.css";

  .setup-header {
    font-weight: normal;
    text-align: left;

    @mixin layout-flex row, center;
    .header-label {
      position: relative;
      display: flex;
      line-height: 20px;
      &-required {
        margin-right: 6px;
        &::after {
          content: "*";
          color: #ff5656;
          position: absolute;
          top: 2px;
          right: -7px;
        }
      }
      &-tips {
        border-bottom: 1px dashed #c4c6cc;
        cursor: default;
      }
    }
    .batch-icon {
      margin-left: 6px;
      font-size: 16px;
      color: #979ba5;
      cursor: pointer;
      outline: 0;
      &:hover {
        color: #3a84ff;
      }
      &.active {
        color: #3a84ff;
      }
    }
  }
</style>

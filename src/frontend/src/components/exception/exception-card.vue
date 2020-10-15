<template>
  <div :class="['bk-exception-card', { 'has-border': hasBorder }]" v-show="show">
    <div class="exception-content">
      <img class="exception-img" :src="image">
      <template v-if="$slots.message">
        <slot name="message"></slot>
      </template>
      <template v-else>
        <p class="exception-text">{{ message }}</p>
        <p v-if="type === 'notPower'" class="exception-text text-link" @click="handleClick">{{ $t('去申请') }}</p>
      </template>
    </div>
  </div>
</template>

<script>
import imgNotData from '@/images/not-data.png'
import imgNotPower from '@/images/not-power.png'
import imgNotResult from '@/images/not-result.png'
import imgDataAbnormal from '@/images/data-abnormal.png'

export default {
  name: 'app-exception-card',
  props: {
    type: {
      type: String,
      default: 'notData'
    },
    delay: {
      type: Number,
      default: 0
    },
    text: {
      type: String,
      default: ''
    },
    hasBorder: {
      type: Boolean,
      default: true
    }
  },
  data() {
    let message = ''
    let image = ''

    switch (this.type) {
      case 'notData':
        image = imgNotData
        message = window.i18n.t('没有数据')
        break

      case 'notPower':
        image = imgNotPower
        message = window.i18n.t('没有权限')
        break

      case 'notResult':
        image = imgNotResult
        message = window.i18n.t('搜索为空')
        break

      case 'dataAbnormal':
        image = imgDataAbnormal
        message = window.i18n.t('数据异常')
        break
    }

    if (this.text) {
      message = this.text
    }

    return {
      show: false,
      message,
      image
    }
  },
  created() {
    setTimeout(() => {
      this.show = true
    }, this.delay)
  },
  methods: {
    handleClick() {
      this.$emit('click', this.type)
    }
  }
}
</script>

<style lang="postcss" scoped>
.bk-exception-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 260px;
  background: #fff;
  &.has-border {
    border: 1px solid #dcdee5;
    border-radius: 2px;
  }
  .exception-content {
    text-align: center;
  }
  .exception-img {
    width: 120px;
  }
  .exception-text {
    margin: 0;
    line-height: 19px;
    font-size: 14px;
    font-weight: normal;
    color: #63656e;
    &.text-link {
      margin-top: 10px;
      line-height: 16px;
      font-size: 12px;
      color: #3a84ff;
      cursor: pointer;
    }
  }
}
</style>

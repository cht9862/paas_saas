<template>
    <div class="right-panel" :class="{ 'need-border': needBorder }">
        <div @click="handleTitleClick" class="right-panel-title" :class="{ 'align-center': alignCenter, 'is-collapse': isEndCollapse }" :style="{ 'backgroundColor': titleBgColor }">
            <slot name="panel">
                <slot name="pre-panel"></slot>
                <div class="panel-sub">
                    <i class="bk-icon title-icon" :style="[iconStyle, { 'color': collapseColor }]" :class="[collapse ? 'icon-down-shape' : 'icon-right-shape']"></i>
                </div>
                <div class="title-desc">
                    <slot name="title">
                        已选择<span class="title-desc-num">{{title.num}}</span>个{{title.type || '主机'}}
                    </slot>
                </div>
            </slot>
        </div>
        <transition :css="false"
                    @before-enter="beforeEnter" @enter="enter" @after-enter="afterEnter"
                    @before-leave="beforeLeave" @leave="leave" @after-leave="afterLeave" @leave-cancelled="afterLeave">
            <div class="right-panel-content" v-show="collapse">
                <slot>

                </slot>
            </div>
        </transition>
    </div>
</template>
<script>
export default {
  name: 'right-panel',
  model: {
    prop: 'collapse',
    event: 'change'
  },
  props: {
    collapse: Boolean,
    alignCenter: {
      type: Boolean,
      default: true
    },
    title: {
      type: Object,
      default() {
        return {
          num: 0,
          type: '主机'
        }
      }
    },
    collapseColor: {
      type: String,
      default: '#63656E'
    },
    titleBgColor: {
      type: String,
      default: '#FAFBFD'
    },
    type: String,
    needBorder: Boolean,
    iconStyle: [String, Object]
  },
  data() {
    return {
      isEndCollapse: this.collapse
    }
  },
  methods: {
    beforeEnter(el) {
      el.classList.add('collapse-transition')
      el.style.height = '0'
    },
    enter(el) {
      el.dataset.oldOverflow = el.style.overflow
      if (el.scrollHeight !== 0) {
        el.style.height = `${el.scrollHeight}px`
      } else {
        el.style.height = ''
      }
      this.$nextTick().then(() => {
        this.isEndCollapse = this.collapse
      })
      el.style.overflow = 'hidden'
      setTimeout(() => {
        el.style.height = ''
        el.style.overflow = el.dataset.oldOverflow
      }, 300)
    },
    afterEnter(el) {
      el.classList.remove('collapse-transition')
    },
    beforeLeave(el) {
      el.dataset.oldOverflow = el.style.overflow
      el.style.height = `${el.scrollHeight}px`
      el.style.overflow = 'hidden'
    },
    leave(el) {
      if (el.scrollHeight !== 0) {
        el.classList.add('collapse-transition')
        el.style.height = 0
      }
      setTimeout(() => {
        this.isEndCollapse = this.collapse
      }, 300)
    },
    afterLeave(el) {
      el.classList.remove('collapse-transition')
      setTimeout(() => {
        el.style.height = ''
        el.style.overflow = el.dataset.oldOverflow
      }, 300)
    },
    handleTitleClick() {
      this.$emit('update:collapse', !this.collapse)
      this.$emit('change', !this.collapse, this.type)
    }
  }
}
</script>
<style lang="postcss" scoped>
  .right-panel {
    &.need-border {
      border: 1px solid #dcdee5;
      border-radius: 2px;
    }
    .right-panel-title {
      display: flex;
      background: #fafbfd;
      color: #63656e;
      font-weight: bold;
      padding: 0 16px;
      cursor: pointer;
      &.is-collapse {
        border-bottom: 1px solid #dcdee5;
      }
      .panel-sub {
        padding: 14px 5px 0 0;
      }
      .title-icon {
        font-size: 16px;
        &:hover {
          cursor: pointer;
        }
      }
      .title-desc {
        color: #979ba5;
        &-num {
          color: #3a84ff;
          margin: 0 3px;
        }
      }
      &.align-center {
        height: 40px;
        align-items: center;
        &.is-collapse {
          height: 41px;
        }
        .panel-sub {
          padding: 0 5px 0 0;
        }
      }
    }
    .right-panel-content {
      /deep/ .bk-table {
        border: 0;
        .bk-table-header {
          th {
            background: #fff;
          }
        }
        &::after {
          width: 0;
        }
      }
    }
    .collapse-transition {
      transition: .3s height ease-in-out;
    }
  }
</style>

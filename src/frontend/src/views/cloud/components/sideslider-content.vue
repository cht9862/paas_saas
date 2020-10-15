<template>
  <section class="sideslider-content">
    <div class="sideslider-content-basic">
      <!--基础信息-->
      <div class="basic-title">{{ $t('基础信息') }}</div>
      <div class="basic-form">
        <div
          v-for="(item, index) in basicInfo"
          :key="index"
          class="basic-form-item"
          :class="index % 2 === 0 ? 'basic-form-even' : 'basic-form-odd'">
          <div class="item-label" :style="{ flexBasis: `${labelMaxWidth}px` }">
            <span :class="{ 'has-tip': item.tip }" v-bk-tooltips="{
              width: 200,
              delay: [300, 0],
              theme: 'light',
              content: item.tip,
              disabled: !item.tip
            }">{{ item.label }}</span>：
          </div>
          <div class="item-content">
            <!--普通类型-->
            <div v-if="item.prop !== 'auth_type'" class="item-content-form">
              <span class="form-input" v-if="item.type === 'tag-switch'">
                <span :class="['tag-switch', { 'tag-enable': item.value }]">
                  {{ item.value ? item.onText || $t('启用') : item.offText || $t('停用') }}
                </span>
              </span>
              <span class="form-input" v-else>
                {{ getFormValue(item) }}
              </span>
            </div>
            <!--认证类型-->
            <div class="item-content-form auth" v-else>
              <span class="auth-type">
                {{ getAuthName(item.authType) }}
              </span>
              <span class="key-icon nodeman-icon nc-key" v-show="item.authType === 'KEY'"></span>
              <span class="form-input"
                    :class="{ 'password': item.authType === 'PASSWORD' }"
                    :title="getAuthValue(item)">
                {{ getAuthValue(item) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
<script>
import { mapGetters, mapActions } from 'vuex'
import { detailConfig } from '../config/proxy-detail-config'
import { authentication } from '@/config/config'

export default {
  name: 'sideslider-content',
  props: {
    // 基础信息
    basic: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      loading: false,
      // 基础信息和服务信息数据
      basicInfo: [],
      // 认证方式
      authentication,
      labelMaxWidth: 100
    }
  },
  computed: {
    ...mapGetters(['bkBizList']),
    ...mapGetters('cloud', ['apList', 'apUrl']),
    apId() {
      return this.basic.ap_id
    }
  },
  watch: {
    basic: {
      async handler(data) {
        const basicInfo = detailConfig.map((config) => {
          if (config.prop === 'auth_type') {
            config.authType = data.auth_type || 'PASSWORD'
            config.value = config.authType === 'TJJ_PASSWORD' ? this.$t('自动拉取') : ''
          } else {
            config.value = data[config.prop] || ''
          }
          return JSON.parse(JSON.stringify(config))
        })
        this.basicInfo.splice(0, this.basicInfo.length, ...basicInfo)
      },
      immediate: true
    }
  },
  created() {
    this.handleInit()
  },
  mounted() {
    this.labelMaxWidth = this.getLabelMaxWidth()
  },
  methods: {
    ...mapActions('cloud', ['getApList', 'setApUrl']),
    async handleInit() {
      if (!this.apList.length) {
        await this.getApList()
      }
      this.setApUrl({ id: this.apId })
    },
    /**
     * 获取认证方式对应的name
     */
    getAuthName(id) {
      const auth = this.authentication.find(auth => auth.id === id) || {}
      return auth.name || ''
    },
    /**
     * 认证方式表单值
     */
    getAuthValue(item) {
      if (item.authType === 'PASSWORD') {
        return new Array(6).fill('*')
          .join('')
      } if (item.authType === 'KEY') {
        return 'key'
      }
      return item.value
    },
    /**
     * 回显表单值
     */
    getFormValue(item) {
      if (item.prop === 'bk_biz_scope') {
        return this.bkBizList.filter(biz => item.value.includes(biz.bk_biz_id)).map(biz => biz.bk_biz_name)
          .join(', ')
      }
      if (item.unit) {
        return item.value ? `${item.value} ${item.unit}` : '--'
      }
      return item.value
    },
    getLabelMaxWidth() {
      const el = this.$el
      const $labelWidthList = el.querySelectorAll('.item-label')
      let max = 100
      $labelWidthList.forEach((item) => {
        const { width } = item.querySelector('span').getBoundingClientRect()
        max = Math.max(max, width)
      })
      return Math.ceil(max)
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

@define-mixin title {
  font-size: 14px;
  color: #313238;
  margin-bottom: 14px;
  font-weight: bold;
}
@define-mixin form {
  @mixin layout-flex row, center, flex-start, wrap;
  &-item {
    margin-bottom: 8px;
    font-size: 14px;

    @mixin layout-flex row, center;
    .item-label {
      flex-basis: 100px;
      text-align: right;
      color: #979ba5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .item-content {
      width: 0;
      flex: 1;
      padding: 0 8px;
      height: 32px;

      @mixin layout-flex row, center, space-between;
    }
  }
}
@define-mixin name-overflow {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
@define-mixin font-size-color $color, $size {
  font-size: $size;
  color: $color;
}

.sideslider-content {
  height: calc(100vh - 60px);
  padding: 24px 30px 0 30px;
  &-basic {
    .basic-title {
      @mixin title;
    }
    .basic-form {
      @mixin form;
      &-odd {
        flex: 0 0 60%;
      },
      &-even {
        flex: 0 0 40%;
      }
      .has-tip {
        border-bottom: 1px dashed #979ba5;
      }
      .item-content {
        &-form {
          width: 0;
          flex: 1;

          @mixin layout-flex row, center;
          @mixin name-overflow;
          .key-icon {
            margin-right: 4px;

            @mixin font-size-color #C4C6CC, 18px;
          }
          .auth-type {
            min-width: 55px;
            border-right: 1px solid #dcdee5;
            margin-right: 12px;

            @mixin layout-flex row, center, space-between;

          },
          .form-input {
            width: 0;
            flex: 1;

            @mixin name-overflow;
            &.password {
              margin-top: 4px;
            }
          }
        }
      }
    }
  }
}
</style>

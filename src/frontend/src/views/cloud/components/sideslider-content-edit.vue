<template>
  <section class="sideslider-content">
    <bk-form form-type="vertical" :model="proxyData" ref="form">
      <bk-form-item :label="$t('内网IP')" required>
        <bk-input v-model="proxyData.inner_ip" readonly></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t('对外通讯IP')"
        property="outer_ip"
        error-display-type="normal"
        :rules="rules.outerIp"
        required
        :desc="descTip">
        <bk-input v-model="proxyData.outer_ip"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('登录IP')" property="login_ip" error-display-type="normal" :rules="rules.loginIp">
        <bk-input v-model="proxyData.login_ip" :placeholder="$t('留空默认为内网IP')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('认证方式')">
        <div class="item-auth">
          <bk-select v-model="proxyData.auth_type" :clearable="false" ext-cls="auth-select">
            <bk-option v-for="item in authentication"
                       :key="item.id"
                       :id="item.id"
                       :name="item.name">
            </bk-option>
          </bk-select>
          <div class="item-auth-content ml10" :class="{ 'is-error': showErrMsg }">
            <bk-input ext-cls="auth-input"
                      v-model="proxyData.password"
                      :type="passwordType"
                      :placeholder="$t('请输入')"
                      v-if="proxyData.auth_type === 'PASSWORD'"
                      @focus="handleFocus"
                      @blur="handleBlur">
            </bk-input>
            <bk-input ext-cls="auth-input"
                      :value="$t('自动拉取')"
                      v-else-if="proxyData.auth_type === 'TJJ_PASSWORD'"
                      readonly>
            </bk-input>
            <upload v-model="proxyData.key"
                    class="auth-key"
                    parse-text
                    :max-size="10"
                    unit="KB"
                    @change="handleFileChange"
                    v-else>
            </upload>
            <p class="error-tip" v-if="showErrMsg">{{ $t('认证资料过期') }}</p>
          </div>
        </div>
      </bk-form-item>
      <bk-form-item :label="$t('登录端口')" property="port" error-display-type="normal" :rules="rules.port" required>
        <bk-input v-model="proxyData.port"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('登录账号')" property="account" error-display-type="normal" :rules="rules.account" required>
        <bk-input v-model="proxyData.account"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('BT传输加速')" property="peer_exchange_switch_for_agent">
        <bk-switcher
          theme="primary"
          size="small"
          v-model="proxyData.peer_exchange_switch_for_agent">
        </bk-switcher>
      </bk-form-item>
      <bk-form-item :label="$t('传输限速')" property="bt_speed_limit" error-display-type="normal" :rules="rules.speedLimit">
        <bk-input v-model="proxyData.bt_speed_limit"></bk-input>
      </bk-form-item>
    </bk-form>
    <div class="mt30 mb10">
      <bk-button
        theme="primary"
        class="nodeman-cancel-btn"
        :loading="loading"
        @click="handleSave">
        {{ $t('保存') }}
      </bk-button>
      <bk-button class="nodeman-cancel-btn ml10" @click="handleCancel">{{ $t('取消') }}</bk-button>
    </div>
  </section>
</template>
<script>
import { isEmpty } from '@/common/util'
import { authentication } from '@/config/config'
import Upload from '@/components/setup-table/upload'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import CloudState from '@/store/modules/cloud'
import { mapActions } from 'vuex'

export default {
  name: 'sideslider-content-edit',
  components: {
    Upload
  },
  props: {
    // 基础信息
    basic: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      authentication,
      descTip: {
        width: 200,
        theme: 'light',
        content: this.$t('对外通讯IP提示')
      },
      proxyData: {},
      rules: {
        outerIp: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            message: this.$t('IP不符合规范'),
            trigger: 'blur',
            validator: (val) => {
              const regx = '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$'
              return new RegExp(regx).test(val)
            }
          }
        ],
        loginIp: [
          {
            message: this.$t('IP不符合规范'),
            trigger: 'blur',
            validator: (val) => {
              if (isEmpty(val)) return true
              const regx = '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$'
              return new RegExp(regx).test(val)
            }
          }
        ],
        port: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            message: this.$t('端口范围', { range: '0-65535' }),
            trigger: 'blur',
            validator: (val) => {
              const regx = '^([0-9]|[1-9]\\d{1,3}|[1-5]\\d{4}|6[0-4]\\d{4}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$'
              return new RegExp(regx).test(val)
            }
          }
        ],
        account: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        speedLimit: [
          {
            message: this.$t('整数最小值校验提示', { min: 1 }),
            trigger: 'blur',
            validator: val => !val || /^[1-9]\d*$/.test(val)
          }
        ]
      },
      loading: false,
      showErrMsg: false
    }
  },
  computed: {
    passwordType() {
      if (!isEmpty(this.proxyData.password)) {
        return 'password'
      }
      return 'text'
    }
  },
  watch: {
    basic: {
      handler(data) {
        this.proxyData = JSON.parse(JSON.stringify(data))
      },
      immediate: true
    }
  },
  methods: {
    ...mapActions('cloud', ['updateHost']),
    handleSave() {
      const isValidate = this.getAuthTypeValidate()

      if (!isValidate) return
      this.$refs.form.validate().then(async () => {
        this.loading = true
        const params = {
          bk_cloud_id: this.proxyData.bk_cloud_id,
          bk_host_id: this.proxyData.bk_host_id,
          account: this.proxyData.account,
          outer_ip: this.proxyData.outer_ip,
          port: this.proxyData.port
        }
        if (this.proxyData.login_ip) {
          params.login_ip = this.proxyData.login_ip
        }

        if (this.proxyData.auth_type) {
          const authType = this.proxyData.auth_type.toLocaleLowerCase()
          if (this.proxyData[authType]) {
            params.auth_type = this.proxyData.auth_type
            params[authType] = this.proxyData[authType]
          }
        }
        if (this.proxyData.bt_speed_limit) {
          params.bt_speed_limit = this.proxyData.bt_speed_limit
        }
        params.peer_exchange_switch_for_agent = Number(this.proxyData.peer_exchange_switch_for_agent || false)
        const result = await this.updateHost(params)
        if (result) {
          this.$bkMessage({
            theme: 'success',
            message: this.$t('修改成功')
          })
          params.re_certification = false
          this.$emit('change', params)
          this.$emit('close')
        }
        this.loading = false
      })
    },
    handleCancel() {
      this.$emit('close')
    },
    handleFocus() {
      this.showErrMsg = false
    },
    handleBlur() {
      this.getAuthTypeValidate()
    },
    handleFileChange() {
      this.getAuthTypeValidate()
    },
    getAuthTypeValidate() {
      this.showErrMsg = this.basic.re_certification
                    && isEmpty(this.proxyData[this.proxyData.auth_type.toLocaleLowerCase()])
      return !this.showErrMsg
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

>>> .bk-form.bk-form-vertical .bk-form-item+.bk-form-item {
  margin-top: 12px;
}
.sideslider-content {
  padding: 24px 30px 0 30px;
  .item-auth {
    @mixin layout-flex row, center;
    &-content {
      flex: 1;
      &.is-error {
        >>> input[type=text] {
          border-color: #ff5656;
        }
        >>> button.upload-btn {
          border: 1px solid #ff5656;
        }
      }
    }
    .error-tip {
      position: absolute;
      margin: 4px 0 0;
      font-size: 12px;
      color: #ea3636;
      line-height: 1;
    }
    .auth-select {
      width: 124px;
    }
    .auth-input {
      flex: 1;
    }
    .auth-key {
      width: 100%;
    }
  }
}
</style>

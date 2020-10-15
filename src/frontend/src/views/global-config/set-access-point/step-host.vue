<template>
  <div class="access-point-host">
    <bk-form :label-width="labelWidth" :model="formData" ref="formData">
      <bk-form-item
        :label="$t('接入点名称')"
        :required="true" :rules="rules.name"
        property="name"
        error-display-type="normal">
        <bk-input v-model.trim="formData.name" :placeholder="$t('用户创建的接入点')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('接入点说明')">
        <bk-input
          ext-cls="bg-white textarea-description"
          type="textarea"
          :rows="4"
          :maxlength="100"
          :placeholder="$t('接入点说明placeholder')"
          v-model.trim="formData.description">
        </bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t('区域')"
        :required="true"
        :rules="rules.required"
        property="region_id"
        error-display-type="normal">
        <bk-input v-model.trim="formData.region_id" :placeholder="$t('请输入')"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t('城市')"
        :required="true"
        :rules="rules.required"
        property="city_id"
        error-display-type="normal">
        <bk-input v-model.trim="formData.city_id" :placeholder="$t('请输入')"></bk-input>
      </bk-form-item>
      <bk-form-item
        class="mt40"
        :label="$t('Zookeeper用户名')"
        :required="true"
        :rules="rules.required"
        property="zk_account"
        error-display-type="normal">
        <bk-input v-model.trim="formData.zk_account" :placeholder="$t('请输入')"></bk-input>
      </bk-form-item>
      <bk-form-item
        :label="$t('Zookeeper密码')"
        :required="!isEdit"
        :rules="isEdit ? [] : rules.required"
        property="zk_password"
        error-display-type="normal">
        <bk-input :type="zkPasswordType" v-model.trim="formData.zk_password" :placeholder="$t('请输入')"></bk-input>
      </bk-form-item>
      <div
        v-for="(label, labelIndex) in labelTableList" :key="labelIndex"
        :style="{ width: `${relatedContentWidth}px` }"
        :class="['bk-form-item ip-related-item clearfix', { mb40: !labelIndex }]">
        <div class="bk-form-item is-required">
          <label class="bk-label" :style="{ width: `${ labelWidth }px` }">
            <span class="bk-label-text">{{label.name}}</span>
          </label>
          <div class="bk-form-content" :style="{ 'margin-left': `${ labelWidth }px` }">
            <setup-form-table
              ref="zookeeperTable"
              :table-head="checkConfig[label.thead]">
              <tbody class="setup-body" slot="tbody">
                <tr v-for="(host, index) in formData[label.key]" :key="`${label.key}td${index}`">
                  <td>{{ index + 1 }}</td>
                  <td
                    class="is-required"
                    v-for="(config, idx) in checkConfig[label.key]"
                    :key="`${label.key}td${idx}`">
                    <verify-input
                      position="right"
                      ref="checkItem"
                      required
                      :rules="config.rules"
                      :id="index"
                      :default-validator="getDefaultValidator()">
                      <input-type
                        v-model.trim="host[config.prop]"
                        v-bind="{
                          type: 'text',
                          placeholder: $t('请输入'),
                          disabled: checkLoading
                        }">
                      </input-type>
                    </verify-input>
                  </td>
                  <td>
                    <div class="opera-icon-group">
                      <i
                        :class="['nodeman-icon nc-plus', { 'disable-icon': checkLoading }]"
                        @click="addAddress(index, label.key)">
                      </i>
                      <i
                        :class="['nodeman-icon nc-minus', { 'disable-icon': formData[label.key].length <= 1 }]"
                        @click="deleteAddress(index, label.key)">
                      </i>
                    </div>
                  </td>
                </tr>
              </tbody>
            </setup-form-table>
          </div>
        </div>
      </div>
      <bk-form-item
        class="mt40"
        :label="$t('Agent安装包URL')"
        :required="true"
        :rules="rules.url"
        property="package_inner_url"
        error-display-type="normal">
        <bk-input
          v-model.trim="formData.package_inner_url"
          :disabled="checkLoading"
          :placeholder="$t('请输入内网下载URL')">
        </bk-input>
      </bk-form-item>
      <bk-form-item class="mt10" label="" :rules="rules.url" property="package_outer_url" error-display-type="normal">
        <bk-input
          v-model.trim="formData.package_outer_url"
          :disabled="checkLoading"
          :placeholder="$t('请输入外网下载URL')">
        </bk-input>
      </bk-form-item>
      <bk-form-item class="mt30">
        <bk-button
          class="check-btn"
          theme="primary"
          :loading="checkLoading"
          :disabled="checkedResult"
          @click.stop="checkCommit">
          {{ $t('测试Server及URL可用性') }}
        </bk-button>
        <section class="check-result" v-if="isChecked">
          <div class="check-result-detail">
            <template v-if="isChecked">
              <h4 class="result-title">{{ $t('测试结果') }}</h4>
              <template v-for="(info, index) in checkedResultList">
                <p :key="index" :class="{ error: info.log_level === 'ERROR' }">{{ `- ${ info.log }` }}</p>
              </template>
            </template>
          </div>
        </section>
      </bk-form-item>
      <bk-form-item class="item-button-group mt30">
        <bk-button
          class="nodeman-primary-btn"
          theme="primary"
          :disabled="!checkedResult || checkLoading"
          @click="submitInfo">
          {{ $t('下一步') }}
        </bk-button>
        <bk-button
          class="nodeman-cancel-btn"
          @click="cancel">
          {{ $t('取消') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import { mapGetters, mapMutations, mapActions } from 'vuex'
import VerifyInput from '@/components/verify-input/verify-input.vue'
import InputType from '@/components/setup-table/input-type.vue'
import formLabelMixin from '@/common/form-label-mixin'
import SetupFormTable from './step-form-table.vue'
import { isEmpty } from '@/common/util'

export default {
  name: 'StepHost',
  components: {
    VerifyInput,
    InputType,
    SetupFormTable
  },
  mixins: [formLabelMixin],
  props: {
    pointId: {
      type: String,
      default: ''
    },
    stepCheck: {
      type: Boolean,
      defautl: false
    },
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    const ipRegExp = '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$'
    return {
      checkLoading: false,
      isInit: true,
      checkedResult: false, // 检测结果
      isChecked: false, // 是否已进行过检测
      checkedResultList: [], // 检测详情
      formData: {
        name: '',
        description: '',
        region_id: '',
        city_id: '',
        zk_account: '',
        zk_password: '',
        zk_hosts: [
          {
            zk_ip: '',
            zk_port: ''
          }
        ],
        btfileserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        dataserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        taskserver: [
          { inner_ip: '', outer_ip: '' }
        ],
        package_inner_url: '',
        package_outer_url: ''
      },
      labelTableList: [
        { name: 'Zookeeper', key: 'zk_hosts', thead: 'zkHead' },
        { name: 'Btfileserver', key: 'btfileserver', thead: 'head' },
        { name: 'Dataserver', key: 'dataserver', thead: 'head' },
        { name: 'Taskserver', key: 'taskserver', thead: 'head' }
      ],
      checkConfig: {
        zkHead: [
          { name: this.$t('序号'), width: 60 },
          { name: 'IP', width: 230 },
          { name: 'PORT', width: 230 },
          { name: '', width: 70 }
        ],
        head: [
          { name: this.$t('序号'), width: 60 },
          { name: this.$t('内网IP'), width: 230 },
          { name: this.$t('外网IP'), width: 230 },
          { name: '', width: 70 }
        ],
        zk_hosts: [
          {
            prop: 'zk_ip',
            classExt: 'ip-input ip-input-inner',
            required: true,
            placeholder: window.i18n.t('请输入Zookeeper主机的IP'),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'zk_ip',
                  type: 'zk_hosts'
                })
              }
            ]
          },
          {
            prop: 'zk_port',
            classExt: 'ip-input ip-input-outer',
            placeholder: window.i18n.t('请输入Zookeeper主机的端口号'),
            rules: [
              {
                content: this.$t('数字0_65535'),
                regx: '^([0-9]|[1-9]\\d{1,3}|[1-5]\\d{4}|6[0-4]\\d{4}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$'
              },
              {
                content: this.$t('冲突校验', { prop: this.$t('端口') }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'zk_port',
                  type: 'zk_hosts'
                })
              }
            ]
          }
        ],
        btfileserver: [
          {
            prop: 'inner_ip',
            classExt: 'ip-input ip-input-inner',
            required: true,
            placeholder: window.i18n.t('请输入Server的内网IP', { type: 'Btfile' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'inner_ip',
                  type: 'btfileserver'
                })
              }
            ]
          },
          {
            prop: 'outer_ip',
            classExt: 'ip-input ip-input-outer',
            placeholder: window.i18n.t('请输入Server的外网IP', { type: 'Btfile' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'outer_ip',
                  type: 'btfileserver'
                })
              }
            ]
          }
        ],
        dataserver: [
          {
            prop: 'inner_ip',
            classExt: 'ip-input ip-input-inner',
            required: true,
            placeholder: window.i18n.t('请输入Server的内网IP', { type: 'Data' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'inner_ip',
                  type: 'dataserver'
                })
              }
            ]
          },
          {
            prop: 'outer_ip',
            classExt: 'ip-input ip-input-outer',
            placeholder: window.i18n.t('请输入Server的外网IP', { type: 'Data' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'outer_ip',
                  type: 'dataserver'
                })
              }
            ]
          }
        ],
        taskserver: [
          {
            prop: 'inner_ip',
            classExt: 'ip-input ip-input-inner',
            required: true,
            placeholder: window.i18n.t('请输入Server的内网IP', { type: 'Task' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'inner_ip',
                  type: 'taskserver'
                })
              }
            ]
          },
          {
            prop: 'outer_ip',
            classExt: 'ip-input ip-input-outer',
            placeholder: window.i18n.t('请输入Server的外网IP', { type: 'Task' }),
            rules: [
              {
                regx: ipRegExp,
                content: this.$t('IP格式不正确')
              },
              {
                content: this.$t('冲突校验', { prop: 'IP' }),
                validator: (value, index) => this.validateUnique(value, {
                  index,
                  prop: 'outer_ip',
                  type: 'taskserver'
                })
              }
            ]
          }
        ]
      },
      urlReg: /^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w.-]+)+[\w\-._~:/?#[\]@!$&'*+,;=.]+$/,
      rules: {
        required: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        name: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator: val => /^[A-Za-z0-9_\u4e00-\u9fa5]{3,32}$/.test(val),
            message: this.$t('长度为3_32的字符'),
            trigger: 'blur'
          }
        ],
        url: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator: val => this.urlReg.test(val),
            message: this.$t('URL格式不正确'),
            trigger: 'blur'
          }
        ]
      },
      labelWidth: 170
    }
  },
  computed: {
    ...mapGetters('config', ['detail']),
    // 动态表单类型内容宽度
    relatedContentWidth() {
      // 580: 两个输入框宽度
      return this.labelWidth + 580
    },
    // 动态表单类型第一个item宽度
    firstRelatedInputWidth() {
      // 285: 输入框的宽度
      return this.labelWidth + 285
    },
    zkPasswordType() {
      if (!isEmpty(this.formData.zk_password)) {
        return 'password'
      }
      return 'text'
    }
  },
  watch: {
    formData: {
      deep: true,
      handler() {
        if (this.isInit) { // 第二步到第一步的时候保持检查结果为通过
          this.isInit = false
        } else {
          this.checkedResult = false
        }
      }
    }
  },
  mounted() {
    this.initDetail()
    this.checkedResult = this.stepCheck
    this.labelWidth = this.initLabelWidth(this.$refs.formData)
  },
  methods: {
    ...mapMutations('config', ['updateDetail']),
    ...mapActions('config', ['requestCheckUsability']),
    initDetail() {
      Object.keys(this.formData).forEach((key) => {
        if (this.detail[key]) {
          this.formData[key] = key === 'zk_hosts' || /server/g.test(key)
            ? JSON.parse(JSON.stringify(this.detail[key])) : this.detail[key]
        }
      })
    },
    checkCommit() {
      this.$refs.formData.validate().then(() => {
        this.validate(async () => {
          this.checkLoading = true
          const { btfileserver, dataserver, taskserver, package_inner_url, package_outer_url } = this.formData
          const data = await this.requestCheckUsability({
            btfileserver, dataserver, taskserver, package_inner_url, package_outer_url
          })
          this.checkedResult = !!data.test_result
          this.checkedResultList = data.test_logs || []
          this.isChecked = true
          this.checkLoading = false
        })
      }, () => {
        this.validate()
      })
    },
    submitInfo() {
      this.updateDetail(this.formData)
      this.$emit('change', true)
      this.$emit('step')
    },
    addAddress(index, type) {
      if (this.checkLoading) return
      this.formData[type].splice(index + 1, 0, type === 'zk_hosts'
        ? { zk_ip: '', zk_port: '' } : { inner_ip: '', outer_ip: '' })
    },
    deleteAddress(index, type) {
      if (this.formData[type].length <= 1) return
      this.formData[type].splice(index, 1)
    },
    cancel() {
      this.$router.push({
        name: 'gseConfig'
      })
    },
    /**
     * 外部调用的校验方法
     */
    validate(callback) {
      return new Promise((resolve, reject) => {
        let isValidate = true
        let count = 0
        // eslint-disable-next-line @typescript-eslint/no-this-alias
        const that = this
        // 调用各个组件内部校验方法
        Object.values(this.$refs.checkItem).forEach((instance) => {
          instance.handleValidate((validator) => {
            if (validator.show) {
              isValidate = false
              reject(validator)
              return false
            }
            count += 1
            if (count === that.$refs.checkItem.length) {
              resolve(isValidate)
              if (typeof callback === 'function') {
                callback(isValidate)
              }
            }
          })
        })
      })
    },
    getDefaultValidator() {
      return {
        show: false,
        content: '',
        errTag: true
      }
    },
    validateUnique(value, { prop, type, index }) {
      let repeat = false
      if (!this.formData[type]) return !repeat
      if (['zk_port', 'zk_ip'].includes(prop)) {
        const negateProp = prop === 'zk_ip' ? 'zk_port' : 'zk_ip'
        const zk = this.formData.zk_hosts[index]
        if (isEmpty(zk[negateProp])) {
          return !repeat
        }
        // zk_host校验 ip + port 不相等
        repeat = this.formData[type].some((item, i) => i !== index
                  && (item.zk_ip + item.zk_port === zk.zk_ip + zk.zk_port))
      } else {
        repeat = this.formData[type].some((item, i) => i !== index && item[prop] === value)
      }
      return !repeat
    }
  }
}
</script>

<style lang="postcss" scoped>
@import "@/css/variable.css";

>>> .bk-form-content .bk-form-control {
  width: 580px;
}
.access-point-host {
  .bg-white {
    background: $whiteColor;
  }
  /deep/ .textarea-description .bk-limit-box {
    line-height: 1;
  }
  .check-result {
    position: relative;
    padding-top: 10px;
    width: 580px;
    &:before {
      position: absolute;
      top: 6px;
      left: 108px;
      display: block;
      width: 5px;
      height: 5px;
      content: "";
      border: 1px solid #dcdee5;
      border-left-color: transparent;
      border-bottom-color: transparent;
      background: #f0f1f5;
      transform: rotateZ(-45deg);
    }
  }
  .check-result-detail {
    padding: 15px 20px;
    min-height: 125px;
    max-height: 500px;
    line-height: 24px;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    font-size: 12px;
    color: #63656e;
    background: #f0f1f5;
    overflow-y: auto;
    .result-title {
      margin: 0;
    }
    .success {
      color: #2dcb56;
    }
    .error {
      color: #ea3636;
    }
  }
  .setup-body {
    background: #fff;
    tr {
      height: 44px;
      td {
        padding: 0 5px;
        &:first-child {
          padding-left: 16px;
        }
      }
    }
  }
  .ip-related-item {
    position: relative;
    .bk-label {
      line-height: 44px;
    }
    >>> .bk-form-content .bk-form-control {
      width: auto;
    }
  }
  .ip-input-outer {
    /deep/ .bk-label {
      display: none;
    }
    /deep/ .bk-form-content {
      /* stylelint-disable-next-line declaration-no-important */
      margin: 0 !important;
    }
  }
  .opera-icon-group {
    display: flex;
    align-items: center;
    height: 32px;
    font-size: 18px;
    color: #c4c6cc;
    i {
      cursor: pointer;
      &:hover {
        color: #979ba5;
      }
      & + i {
        margin-left: 10px;
      }
      &.disable-icon {
        color: #dcdee5;
        cursor: not-allowed;
      }
    }
  }
  .check-btn {
    min-width: 216px;
  }
}
</style>

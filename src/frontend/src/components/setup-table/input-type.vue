<template>
  <div class="input-type" :style="{ 'z-index': zIndex }">
    <!--input类型-->
    <bk-input
      :ref="type"
      v-if="isInput"
      :type="type"
      :value="inputValue"
      :placeholder="placeholder"
      :readonly="readonly"
      :disabled="disabled"
      @change="handleChange"
      @blur="handleBlur"
      @enter="handleEnter">
      <template v-if="appendSlot" slot="append">
        <div class="group-text">{{ appendSlot }}</div>
      </template>
    </bk-input>
    <div v-else-if="type === 'textarea'">
      <bk-input
        :ref="type"
        :type="type"
        :value="inputValue"
        :placeholder="placeholder"
        :readonly="readonly"
        :disabled="disabled"
        :rows="currentRows"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
        @enter="handleEnter">
      </bk-input>
      <span v-if="showEllipsis" class="input-text" @click="handleShowTextArea">{{ valueText }}</span>
    </div>
    <!-- 密码框 -->
    <bk-input
      :ref="type"
      v-else-if="type === 'password'"
      :type="passwordType"
      :value="inputValue"
      :placeholder="placeholder"
      :readonly="readonly"
      :disabled="disabled"
      :native-attributes="{
        autocomplete: 'off'
      }"
      @change="handleChange"
      @blur="handleBlur"
      @enter="handleEnter">
    </bk-input>
    <!--select类型-->
    <permission-select
      v-else-if="type === 'select'"
      ext-cls="input-select"
      permission-key="view"
      :permission="permission"
      :ref="type"
      :clearable="false"
      :value="inputValue"
      :popover-options="{ 'boundary': 'window' }"
      :placeholder="placeholder"
      :readonly="readonly"
      :disabled="disabled"
      :popover-min-width="popoverMinWidth"
      :option-list="options"
      :extension="prop === 'bk_cloud_id' && !options.length"
      @extension="handleCreate"
      @change="handleChange"
      @toggle="handleSelectChange">
    </permission-select>
    <!-- <bk-select
            v-else
            :ref="type"
            v-else-if="type === 'select'"
            :clearable="false"
            ext-cls="input-select"
            :value="inputValue"
            :popover-options="{ 'boundary': 'window' }"
            :placeholder="placeholder"
            :readonly="readonly"
            :disabled="disabled"
            :popover-min-width="popoverMinWidth"
            @change="handleChange"
            @toggle="handleSelectChange">
            <bk-option v-for="option in options"
                :key="option.id"
                :id="option.id"
                :name="option.name">
            </bk-option>
            仅云区域可添加
            <div v-if="prop === 'bk_cloud_id' && !options.length" slot="extension" @click="handleCreate" style="cursor: pointer;">
                <i class="bk-icon icon-plus-circle mr5"></i>{{ $t('新增') }}
            </div>
        </bk-select> -->
    <!--file类型-->
    <div v-else-if="type === 'file'">
      <upload :value="inputValue"
              parse-text
              :max-size="10"
              unit="KB"
              :file-info="fileInfo"
              @change="handleUploadChange"></upload>
    </div>
    <!--业务选择器-->
    <div v-else-if="type === 'biz'">
      <bk-biz-select
        :value="inputValue"
        :show-select-all="false"
        :default-checked="false"
        :auto-update-storage="false"
        :multiple="multiple"
        :disabled="disabled"
        :readonly="readonly"
        :auto-request="autoRequest"
        :ref="type"
        min-width="auto"
        @change="handleChange"
        @toggle="handleSelectChange">
      </bk-biz-select>
    </div>
    <!--权限类型-->
    <div v-else-if="type === 'auth'" class="input-auth">
      <bk-dropdown-menu
        :class="{ 'dropdown': authType === 'TJJ_PASSWORD' }"
        @show="handleDropdownShow()"
        @hide="handleDropdownHide()"
        ref="authType">
        <div slot="dropdown-trigger" class="auth-type">
          <span>{{ authName }}</span>
          <i :class="['arrow-icon nodeman-icon nc-arrow-down', { 'icon-flip': isDropdownShow }]"></i>
        </div>
        <ul class="bk-dropdown-list" slot="dropdown-content">
          <li v-for="auth in authentication"
              :key="auth.id"
              class="auth-options"
              @click.stop="handleAuthChange(auth)">
            <a>{{ auth.name }}</a>
          </li>
        </ul>
      </bk-dropdown-menu>
      <bk-input
        :value="$t('自动拉取')"
        class="auth-input"
        v-if="authType === 'TJJ_PASSWORD'"
        disabled>
      </bk-input>
      <bk-input
        :value="inputValue"
        :type="passwordType"
        class="auth-input"
        v-else-if="authType === 'PASSWORD'"
        :native-attributes="{
          autocomplete: 'off'
        }"
        @change="handleChange"
        @blur="handleBlur">
      </bk-input>
      <upload
        :value="inputValue"
        :disable-hover-cls="true"
        class="auth-input file"
        parse-text
        :max-size="10"
        unit="KB"
        v-else-if="authType === 'KEY'"
        @change="handleUploadChange">
      </upload>
    </div>
    <bk-switcher
      theme="primary"
      size="small"
      v-else-if="type === 'switcher'"
      :value="inputValue"
      @change="handleChange">
    </bk-switcher>
    <span v-else>--</span>
  </div>
</template>
<script>
import Upload from './upload.vue'
import PermissionSelect from '@/components/permission-select/permission-select.vue'
import { authentication } from '@/config/config'
import { isEmpty } from '@/common/util'
import emitter from '@/common/emitter'

const EVENT_BLUR = 'blur' // 失焦校验事件
const EVENT_UPDATE = 'update' // 自定义v-model事件，更新value值
const EVENT_CHANGE = 'change' // change事件
const EVENT_TOGGLE = 'toggle' // 业务选择器折叠和收起时触发
const EVENT_ENTER = 'enter'
const EVENT_UPLOAD_CHANGE = 'upload-change'

// 支持的输入类型
const basicInputType = ['text', 'number', 'email', 'url', 'date']
export default {
  name: 'input-type',
  components: {
    Upload,
    PermissionSelect
  },
  mixins: [emitter],
  model: {
    prop: 'inputValue',
    event: 'update'
  },
  props: {
    inputValue: {
      type: [String, Array, Number]
    },
    // 输入框类型
    type: {
      type: String,
      default: ''
    },
    prop: {
      type: String,
      default: ''
    },
    // 值分隔方式
    splitCode: {
      type: Array,
      default: () => []
    },
    // 是否自动聚焦
    autofocus: {
      type: Boolean,
      default: false
    },
    // 是否只读
    readonly: {
      type: Boolean,
      default: false
    },
    // 是否禁用
    disabled: {
      type: Boolean,
      default: false
    },
    placeholder: {
      type: String,
      default: window.i18n.t('请输入')
    },
    // biz select 框是否支持多选
    multiple: {
      type: Boolean,
      default: true
    },
    // 下拉框数据源
    options: {
      type: Array,
      default: () => []
    },
    popoverMinWidth: Number,
    autoRequest: {
      type: Boolean,
      default: true
    },
    subType: {
      type: String,
      default: ''
    },
    // input类型插槽
    appendSlot: {
      type: String,
      default: ''
    },
    // select 权限控制
    permission: {
      type: Boolean,
      default: false
    },
    fileInfo: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      authentication,
      authType: this.subType,
      // inputValue: this.value,
      isDropdownShow: false,
      isFocus: false,
      maxRows: 8,
      rows: 1
    }
  },
  computed: {
    authName() {
      const auth = this.authentication.find(auth => auth.id === this.authType) || {}
      return auth.name || ''
    },
    isInput() {
      return basicInputType.includes(this.type)
    },
    passwordType() {
      if (!isEmpty(this.inputValue)) {
        return 'password'
      }
      return 'text'
    },
    zIndex() {
      return this.isFocus ? 99 : 0
    },
    currentRows() {
      return this.isFocus ? this.rows : 1
    },
    valueText() {
      if (this.rows > 1 && this.inputValue) {
        const data = this.inputValue.split('\n').map(text => text.trim())
          .filter(text => text)
        return data.join(',')
      }
      return this.inputValue
    },
    showEllipsis() {
      if (this.type === 'textarea') {
        return this.isFocus ? false : (this.rows > 1)
      }
      return false
    }
  },
  watch: {
    inputValue() {
      this.$nextTick(this.setRows)
    }
  },
  created() {
    this.dispatch('step-verify-input', 'verify-registry', this)
  },
  mounted() {
    // 是否自动聚焦
    if (this.autofocus) {
      if (this.isInput || this.type === 'password') {
        // 输入框类型自动focus
        this.$refs[this.type] && this.$refs[this.type].focus()
      } else if (['select', 'biz'].includes(this.type)) {
        // select框类型focus（展示下拉列表）
        this.$refs[this.type] && this.$refs[this.type].show()
      }
    }
  },
  beforeDestroy() {
    this.dispatch('step-verify-input', 'verify-remove')
  },
  methods: {
    /**
     * input change时触发
     */
    handleChange(value) {
      this.$emit(EVENT_UPDATE, value)
      this.$emit(EVENT_CHANGE, value, this)
    },
    /**
     * 失焦
     */
    handleBlur(value) {
      this.isFocus = false
      this.$emit(EVENT_BLUR, value, this)
      this.dispatch('step-verify-input', 'verify-blur', this.inputValue)
    },
    /**
     * 文件变更时事件
     */
    handleUploadChange(value, fileInfo) {
      this.$emit(EVENT_UPDATE, value, this)
      this.$emit(EVENT_UPLOAD_CHANGE, {
        value,
        ...fileInfo
      }, this)
    },
    /**
     * 业务选择器折叠和收起时触发事件
     */
    handleSelectChange(toggle, selectedItems) {
      if (!toggle) {
        this.$emit(EVENT_BLUR, this.inputValue, this)
        this.dispatch('step-verify-input', 'verify-blur', this.inputValue)
      }
      this.$emit(EVENT_TOGGLE, toggle, selectedItems)
    },
    /**
     * 认证方式change
     * @param {Object} auth
     */
    handleAuthChange(auth) {
      this.authType = auth.id
      this.inputValue = ''
      if (this.authType === 'TJJ_PASSWORD') {
        this.handleBlur(this.$t('自动拉取'))
      }
      this.$refs.authType.hide()
    },
    handleDropdownShow() {
      this.isDropdownShow = true
    },
    handleDropdownHide() {
      this.isDropdownShow = false
    },
    handleEnter(value) {
      this.$emit(EVENT_ENTER, value, this)
    },
    handleFocus() {
      this.isFocus = true
    },
    setRows() {
      if (this.type !== 'textarea') return
      const rows = this.inputValue.split('\n').length || 1
      this.rows = Math.min(10, rows)
    },
    handleShowTextArea() {
      this.isFocus = true
      this.$refs[this.type] && this.$refs[this.type].focus()
    },
    // select 下拉新增事件 - 少量，不做派发
    handleCreate() {
      if (this.prop === 'bk_cloud_id') {
        this.$router.push({ name: 'cloudManager' })
      }
    }
  }
}
</script>
<style lang="postcss" scoped>
  @import "@/css/mixins/nodeman.css";

  .input-type {
    width: 100%;
    >>> .bk-textarea-wrapper textarea {
      height: auto;
      min-height: 29px;
    }
    .input-select {
      width: 100%;
    }
    .input-auth {
      @mixin layout-flex row;
      .dropdown {
        z-index: 1;
      }
      .auth-type {
        padding: 0 6px;
        margin-right: -1px;
        border: 1px solid #c4c6cc;
        border-radius: 2px 0 0 2px;
        min-width: 80px;
        height: 32px;
        background: #fafbfd;

        @mixin layout-flex row, center, center;
        .arrow-icon {
          font-size: 20px;
          transition: all .2s ease;
          &.icon-flip {
            transform: rotate(180deg)
          }
        }
      }
      .auth-options {
        cursor: pointer;
      }
      .auth-input {
        &.file {
          width: 100%;
          >>> .upload-info {
            border: 1px solid #c4c6cc;
          }
        }
        >>> .bk-form-input {
          border-radius: 0 2px 2px 0;
        }
        >>> .upload-btn {
          border-radius: 0 2px 2px 0;
        }
      }
    }
    .input-text {
      position: absolute;
      top: 0;
      left: 0;
      padding: 5px 10px;
      height: 32px;
      width: 100%;
      color: #63656e;
      border: 1px solid #c4c6cc;
      background-color: #fff;
      padding: 5px 10px;
      z-index: 1;
      cursor: text;
      line-height: 20px;
      border-radius: 2px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .group-text {
      padding: 0 4px;
    }
  }
</style>

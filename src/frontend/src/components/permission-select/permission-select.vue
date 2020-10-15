<template>
    <bk-select
        ref="permissionSelect"
        :value="selectValue"
        :placeholder="placeholder"
        :loading="loading"
        :ext-cls="extCls"
        :searchable="searchable"
        :multiple="multiple"
        :clearable="clearable"
        :readonly="readonly"
        :disabled="disabled"
        :popover-options="{ 'boundary': 'window' }"
        :popover-min-width="popoverMinWidth"
        @selected="handleSelected"
        @toggle="handleToggle"
        @change="handleChange"
        @clear="handleClear">
        <template v-for="item in optionList">
            <bk-option
                :key="item[optionId]"
                :id="item[optionId]"
                :name="item[optionName]"
                :class="{ 'is-auth-disabled': openPermission && !(item.permission || item[permissionKey]) }"
                :disabled="item.disabled">
                <div class="bk-option-content-default" :title="item[optionName]">
                    <span class="bk-option-name">
                        {{ item[optionName] }}
                    </span>
                    <i class="select-item-icon bk-option-icon bk-icon icon-check-1" v-if="multiple && selectValue.includes(item[optionId])"></i>
                    <auth-component
                        v-if="openPermission && !(item.permission || item[permissionKey])"
                        class="bk-option-content-default"
                        tag="div"
                        :title="item[optionName]"
                        :auth="{
                            permission: item.permission || item[permissionKey] || false,
                            apply_info: [{
                                action: item.permissionType || permissionType,
                                instance_id: item[instanceId],
                                instance_name: item[instanceName]
                            }]
                        }"
                        @click="handleSelectClose">
                    </auth-component>
                </div>
            </bk-option>
        </template>
        <div v-if="extension" slot="extension" style="cursor: pointer;" @click="handleExtension">
            <i class="bk-icon icon-plus-circle mr5"></i>{{ $t('新增') }}
        </div>
    </bk-select>
</template>
<script>
import { mapGetters } from 'vuex'

export default {
  name: 'permission-select',
  model: {
    prop: 'value',
    event: 'update'
  },
  props: {
    value: {
      type: [String, Array, Number],
      default: ''
    },
    optionList: {
      type: Array,
      default: () => []
    },
    // 外部样式
    extCls: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    multiple: {
      type: Boolean,
      default: false
    },
    searchable: {
      type: Boolean,
      default: false
    },
    clearable: {
      type: Boolean,
      default: false
    },
    readonly: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    optionId: {
      type: String,
      default: 'id'
    },
    optionName: {
      type: String,
      default: 'name'
    },
    // extension slot
    extension: {
      type: Boolean,
      default: false
    },
    // 权限控制
    permission: {
      type: [String, Boolean, Number],
      default: true
    },
    // 权限字段
    permissionKey: {
      type: String,
      default: ''
    },
    // 权限类型
    permissionType: {
      type: String,
      default: ''
    },
    // 自定义权限实例的id 和name
    permissionId: {
      type: String,
      default: ''
    },
    permissionName: {
      type: String,
      default: ''
    },
    popoverMinWidth: Number
  },
  data() {
    return {
      loading: false, // select框加载
      selectValue: this.value,
      remoteMethod: this.handleRemoteMethod
      // searchValue: ''
    }
  },
  computed: {
    ...mapGetters(['permissionSwitch']),
    openPermission() {
      return this.permissionSwitch && this.permission
    },
    selectedItems() {
      if (this.selectValue instanceof Array) {
        return this.optionList.filter(item => this.selectValue.includes(item[this.optionId])
                && (this.openPermission ? item.permission || item[this.permissionKey] : true))
      }
      return this.optionList.filter(item => this.selectValue === item[this.optionId]
              && (this.openPermission ? item.permission || item[this.permissionKey] : true))
    },
    // 实例id
    instanceId() {
      return this.openPermission ? this.permissionId || this.optionId : this.optionId
    },
    // 实例名称
    instanceName() {
      return this.openPermission ? this.permissionName || this.optionName : this.optionName
    }
  },
  watch: {
    value(v) {
      this.selectValue = v
    }
  },
  created() {
    this.handleInit()
  },
  methods: {
    async handleInit() {
      if (this.openPermission) {
        const copyValue = JSON.stringify(this.selectValue)
        if (Array.isArray(this.selectValue)) {
          this.selectValue = this.optionList.filter(item => this.selectValue.includes(item[this.optionId])
            && (item.permission || item[this.permissionKey]))
        } else {
          const option = this.optionList.find(item => this.selectValue === item[this.optionId]
            && (item.permission || item[this.permissionKey]))
          this.selectValue = option ? option[this.optionId] : ''
        }
        this.$emit('update', this.selectValue)
        if (JSON.stringify(this.selectValue) !== copyValue) {
          this.$emit('change', this.selectValue, copyValue, this.selectedItems)
        }
      }
    },
    handleSelected(value, options) {
      this.$emit('selected', value, options, this.selectedItems)
    },
    handleToggle(toggle) {
      this.$emit('toggle', toggle, this.selectedItems)
    },
    handleChange(newValue, oldValue) {
      this.selectValue = newValue
      this.$emit('update', newValue)
      this.$emit('change', newValue, oldValue, this.selectedItems)
    },
    handleClear(oldValue) {
      this.$emit('clear', oldValue, this.selectedItems)
    },
    handleSelectClose() {
      this.$refs.permissionSelect.close()
    },
    handleExtension() {
      this.$emit('extension')
    },
    show() {
      this.$refs.permissionSelect && this.$refs.permissionSelect.show()
    }
  }
}
</script>
<style lang="postcss" scoped>
  >>> .bk-select-loading {
    top: 6px;
  }
  .select {
    &-item {
      display: flex;
      &-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: 4px;
      }
      &-id {
        color: #c4c6cc;
        margin-right: 20px;
      }
      >>> .bk-icon {
        top: 3px;
      }
    }
  }
</style>

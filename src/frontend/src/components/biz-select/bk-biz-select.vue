<template>
  <bk-select
    class="select"
    :value="selectValue"
    :show-select-all="showSelectAll"
    :placeholder="innerPlaceholder"
    :search-placeholder="$t('请输入业务名称或业务ID')"
    :loading="loading"
    :ext-cls="extCls"
    searchable
    :multiple="multiple"
    :style="{ 'min-width': minWidth }"
    :popover-options="{ 'boundary': 'window' }"
    :clearable="clearable"
    :popover-min-width="160"
    :readonly="readonly"
    :disabled="disabled"
    :remote-method="remoteMethod"
    ref="select"
    @selected="handleSelected"
    @toggle="handleToggle"
    @change="handleChange"
    @clear="handleClear">
    <bk-option
      v-for="option in filterBkBizList"
      :key="option.bk_biz_id"
      :id="option.bk_biz_id"
      :name="option.bk_biz_name"
      :disabled="option.disabled">
      <div class="select-item">
        <span class="select-item-name"
              :title="option.bk_biz_name">
          {{ `[${option.bk_biz_id}] ${option.bk_biz_name}` }}
        </span>
        <!-- <span class="select-item-id" v-show="searchValue">{{ `(#${option.bk_biz_id})` }}</span> -->
        <i
          class="select-item-icon bk-option-icon bk-icon icon-check-1"
          v-if="multiple && selectValue.includes(option.bk_biz_id)">
        </i>
      </div>
    </bk-option>
    <div slot="extension"
         class="extension-container"
         v-if="permissionSwitch"
         @click="handleApplyBiz">
      <i class="bk-icon icon-plus-circle"></i>
      <span class="ml5 extension-text">{{ $t('申请业务权限') }}</span>
    </div>
  </bk-select>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from 'vuex'
import { STORAGE_KEY_BIZ } from '@/config/storage-key'

export default {
  name: 'bk-biz-select',
  model: {
    prop: 'value',
    event: 'update'
  },
  props: {
    value: {
      type: [String, Array, Number],
      default: ''
    },
    // 是否显示全选
    showSelectAll: {
      type: Boolean,
      default: true
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
    // 是否默认选中storage中勾选的业务
    defaultChecked: {
      type: Boolean,
      default: true
    },
    multiple: {
      type: Boolean,
      default: true
    },
    // 是否自动更新storage
    autoUpdateStorage: {
      type: Boolean,
      default: true
    },
    minWidth: {
      type: String,
      default: '240px'
    },
    clearable: {
      type: Boolean,
      default: true
    },
    readonly: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    autoRequest: {
      type: Boolean,
      default: true
    },
    action: {
      type: String,
      default: 'agent_view'
    }
  },
  data() {
    return {
      loading: false, // select框加载
      selectValue: this.value,
      storageKey: STORAGE_KEY_BIZ, // bizId存储Key
      innerPlaceholder: this.placeholder || this.$t('选择业务'),
      remoteMethod: this.handleRemoteMethod,
      searchValue: ''
    }
  },
  computed: {
    ...mapGetters(['bkBizList', 'bizAction', 'permissionSwitch']),
    selectedItems() {
      if (this.selectValue instanceof Array) {
        return this.bkBizList.filter(item => this.selectValue.includes(item.bk_biz_id))
      }
      return this.bkBizList.filter(item => this.selectValue === item.bk_biz_id)
    },
    filterBkBizList() {
      return this.bkBizList.reduce((pre, item) => {
        const filterId = item.bk_biz_id.toString().indexOf(this.searchValue) > -1
        const filterName = item.bk_biz_name.toString().toLocaleLowerCase()
          .indexOf(this.searchValue.toLocaleLowerCase()) > -1
        if (filterId || filterName || !this.searchValue) {
          pre.push(item)
        }
        return pre
      }, [])
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
    ...mapActions(['getBkBizList', 'getApplyPermission']),
    ...mapMutations(['setSelectedBiz']),
    async handleInit() {
      if (!this.bkBizList.length && this.autoRequest) {
        this.loading = true
        await this.getBkBizList({ action: this.bizAction })
        !this.bkBizList.length && this.$store.commit('updatePagePermission', false)
        this.loading = false
      }
      this.selectValue = JSON.parse(JSON.stringify(this.value))
      this.$emit('update', this.selectValue)
    },
    handleSelected(value, options) {
      this.$emit('selected', value, options, this.selectedItems)
    },
    handleToggle(toggle) {
      this.$emit('toggle', toggle, this.selectedItems)
    },
    handleChange(newValue, oldValue) {
      this.selectValue = newValue
      if (this.autoUpdateStorage) {
        this.handleSetStorage()
      }
      this.$emit('update', newValue)
      this.$emit('change', newValue, oldValue, this.selectedItems)
    },
    handleClear(oldValue) {
      this.$emit('clear', oldValue, this.selectedItems)
    },
    /**
     * 设置存储当前选择的业务ID
     */
    handleSetStorage() {
      if (window.localStorage) {
        window.localStorage.setItem(this.storageKey, JSON.stringify(this.selectValue))
      }
      this.setSelectedBiz(this.selectValue)
    },
    handleRemoteMethod(v) {
      this.searchValue = v
    },
    async handleApplyBiz() {
      this.loading = true
      const res = await this.getApplyPermission({ apply_info: [{ action: this.bizAction }] })
      if (res.url) {
        if (self === top) {
          window.open(res.url, '__blank')
        } else {
          try {
            window.top.BLUEKING.api.open_app_by_other('bk_iam', res.url)
          } catch (_) {
            window.open(res.url, '__blank')
          }
        }
      }
      this.loading = false
    },
    show() {
      this.$refs.select && this.$refs.select.show()
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
      right: 0;
    }
  }
}
</style>

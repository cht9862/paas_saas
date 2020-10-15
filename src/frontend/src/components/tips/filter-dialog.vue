<template>
    <bk-dialog
        :value="value"
        header-position="left"
        :title="title"
        width="800"
        @value-change="handleValueChange"
        @confirm="confirm"
        @cancel="cancel">
        <template #default>
            <bk-table :data="data" max-height="464" v-if="data.length && value" ref="table">
                <bk-table-column label="IP" prop="ip" width="180"></bk-table-column>
                <bk-table-column :label="$t('过滤原因')" prop="msg" show-overflow-tooltip></bk-table-column>
            </bk-table>
        </template>
        <template #footer>
            <div class="footer">
                <bk-button @click="handleFilterExport">{{ $t('导出') }}</bk-button>
                <div class="footer-right">
                    <bk-button theme="primary" @click="handleFilterConfirm">{{ $t('确定') }}</bk-button>
                </div>
            </div>
        </template>
    </bk-dialog>
</template>
<script>
export default {
  name: 'filter-dialog',
  model: {
    prop: 'value',
    event: 'change'
  },
  props: {
    value: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    list: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      data: JSON.parse(JSON.stringify(this.list))
    }
  },
  watch: {
    list(v) {
      this.data = JSON.parse(JSON.stringify(v))
    }
  },
  methods: {
    handleValueChange(v) {
      this.$emit('change', v)
    },
    confirm() {
      this.$emit('confirm', this.data)
    },
    cancel() {
      this.$emit('cancel', this.data)
    },
    handleFilterExport() {
      const elt = this.$refs.table.$el
      import('xlsx').then((XLSX) => {
        const wb = XLSX.utils.table_to_book(elt, { sheet: this.$t('过滤列表') })
        XLSX.writeFile(wb, `${this.$t('过滤列表')}.xlsx`)
      })
      this.$emit('filter-export', this.data)
      this.$emit('change', false)
    },
    handleFilterConfirm() {
      this.$emit('filter-confirm', this.data)
      this.$emit('change', false)
    }
  }
}
</script>
<style lang="postcss" scoped>
  @import "@/css/mixins/nodeman.css";

  >>> .bk-dialog-body {
    padding: 0;
  }
  >>> .bk-dialog-footer {
    border-top: 0;
  }
  >>> .is-first {
    .cell {
      padding-left: 24px;
    }
  }
  .footer {
    @mixin layout-flex row, center, space-between;
    .footer-right {
      @mixin layout-flex row;
    }
  }
</style>

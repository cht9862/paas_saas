<template>
  <bk-table :data="data" :pagination="pagination">
    <bk-table-column :label="$t('部署策略')" sortable></bk-table-column>
    <bk-table-column :label="$t('插件名称')" sortable></bk-table-column>
    <bk-table-column :label="$t('已部署节点')" sortable></bk-table-column>
    <bk-table-column :label="$t('包含业务')" sortable></bk-table-column>
    <bk-table-column :label="$t('操作账号')" sortable></bk-table-column>
    <bk-table-column :label="$t('最近操作时间')" sortable></bk-table-column>
    <bk-table-column :label="$t('操作')" width="200">
      <template #default="{ row }">
        <div class="operate">
          <bk-button text disabled>{{ $t('调整目标') }}</bk-button>
          <bk-badge dot theme="danger">
            <bk-button text class="ml10">
              {{ $t('升级') }}
            </bk-button>
          </bk-badge>
          <bk-button text class="ml10">{{ $t('编辑参数') }}</bk-button>
          <span class="more-btn" @click="handleShowMore($event, row)">
            <i class="bk-icon icon-more"></i>
          </span>
        </div>
      </template>
    </bk-table-column>
  </bk-table>
</template>
<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { IPluginRule, IPagination } from '@/types/plugin/plugin-type'
import PluginState from '@/store/modules/plugin-new'
import MoreOperate from './more-operate.vue'

@Component({ name: 'plugin-rule-table' })
export default class PluginRuleTable extends Vue {
  private data: IPluginRule[] = []
  private pagination: IPagination = {
    current: 0,
    count: 0,
    limit: 20
  }
  private instance: MoreOperate = new MoreOperate().$mount()
  private popoverInstance: any = null

  private created() {
    this.getPluginRules()
  }

  public async getPluginRules() {
    this.data = await PluginState.getPluginRules()
  }

  public handleShowMore(e: Event, row: IPluginRule) {
    this.instance.data = [
      {
        id: 'stop',
        name: this.$t('停用'),
        disabled: row.disabled
      },
      {
        id: 'reboot',
        name: this.$t('重启')
      },
      {
        id: 'restart',
        name: this.$t('重载')
      }
    ]
    if (!this.popoverInstance) {
      this.popoverInstance = this.$bkPopover(e.target as EventTarget, {
        content: this.instance.$el,
        trigger: 'manual',
        arrow: false,
        theme: 'light menu',
        maxWidth: 280,
        offset: '0, 5',
        sticky: true,
        duration: [275, 0],
        interactive: true,
        boundary: 'window',
        placement: 'bottom'
      })
    }
    this.popoverInstance.show()
  }
}
</script>
<style lang="postcss" scoped>
>>> .bk-badge-wrapper .bk-badge.pinned.top-right {
  top: 6px;
}
>>> .bk-badge-wrapper .bk-badge.dot {
  width: 6px;
  height: 6px;
  min-width: 6px;
}
.operate {
  display: flex;
  align-items: center;
  .more-btn {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    cursor: pointer;
    color: #979ba5;
    &:hover {
      color: #3a84ff;
      background: #dcdee5;
    }
  }
}
</style>

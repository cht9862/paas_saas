<template>
  <div class="gse-config-wrapper" v-bkloading="{ isLoading: loading }">
    <template>
      <Tips :list="tipsList" class="mb20"></Tips>
      <auth-component
        class="mb14"
        tag="div"
        :auth="{
          permission: apCreatePermission,
          apply_info: [{ action: 'ap_create' }]
        }">
        <template slot-scope="{ disabled }">
          <bk-button
            class="w100"
            theme="primary"
            :disabled="disabled"
            @click.stop="operaHandler($event, 'add')">
            {{ $t('新建') }}
          </bk-button>
        </template>
      </auth-component>
      <section class="access-point-collapse">
        <template v-for="accessPoint in accessPointList">
          <RightPanel
            class="access-point-item"
            :align-center="false"
            :key="accessPoint.id"
            :need-border="true"
            collapse-color="#313238"
            title-bg-color="#FAFBFD"
            :collapse.sync="accessPoint.collapse">
            <div class="collapse-header" slot="title">
              <div class="access-point-status">
                <div class="col-status" v-if="accessPoint.status">
                  <span :class="`status-mark status-${ accessPoint.status.toLocaleLowerCase() }`"></span>
                </div>
                <div class="col-status" v-else>
                  <span class="status-mark status-unknown"></span>
                </div>
              </div>
              <div class="header-title">
                <div class="block-flex">
                  <h3 class="access-point-title">
                    {{ accessPoint.name }}
                  </h3>
                  <span class="title-tag" v-if="accessPoint.ap_type === 'system'">{{ $t('默认') }}</span>
                  <auth-component
                    tag="div"
                    :auth="{

                      permission: accessPoint.edit,
                      apply_info: [{
                        action: 'ap_edit',
                        instance_id: accessPoint.id,
                        instance_name: accessPoint.name
                      }]
                    }">
                    <template slot-scope="{ disabled }">
                      <bk-button
                        ext-cls="access-point-operation"
                        text
                        :disabled="disabled"
                        @click.stop="operaHandler(accessPoint, 'edit')">
                        <i class="nodeman-icon nc-icon-edit-2"></i>
                      </bk-button>
                    </template>
                  </auth-component>
                  <auth-component
                    tag="div"
                    :auth="{
                      permission: accessPoint.delete,
                      apply_info: [{
                        action: 'ap_delete',
                        instance_id: accessPoint.id,
                        instance_name: accessPoint.name
                      }]
                    }">
                    <template slot-scope="{ disabled }">
                      <bk-popover placement="top" :disabled="!accessPoint.is_used">
                        <bk-button
                          ext-cls="access-point-operation"
                          v-if="accessPoint.ap_type !== 'system'"
                          text
                          :disabled="disabled || accessPoint.is_used"
                          @click.stop="operaHandler(accessPoint, 'delete')">
                          <i class="nodeman-icon nc-delete-2"></i>
                        </bk-button>
                        <div slot="content">{{ $t('该接入点被使用中无法删除') }}</div>
                      </bk-popover>
                    </template>
                  </auth-component>
                </div>
                <p class="access-point-remarks" v-if="accessPoint.description">
                  <span>ID:</span>
                  <span class="point-id">{{ `  ${ accessPoint.id || '--' }` }}</span>
                  <span class="point-desc" v-if="accessPoint.description">{{ accessPoint.description }}</span>
                </p>
              </div>
            </div>
            <div class="collapse-container" slot>
              <AccessPointTable
                v-if="accessPoint.view"
                class="not-outer-border"
                :access-point="accessPoint">
              </AccessPointTable>
              <exception-card
                v-else
                type="notPower"
                :has-border="false"
                @click="handleApplyPermission(accessPoint)">
              </exception-card>
            </div>
          </RightPanel>
        </template>
      </section>
    </template>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { bus } from '@/common/bus'
import RightPanel from '@/components/right-panel/right-panel.vue'
import AccessPointTable from './access-point-table.vue'
import Tips from '@/components/tips/tips.vue'
import ExceptionCard from '@/components/exception/exception-card'

export default {
  name: 'GseConfig',
  components: {
    RightPanel,
    AccessPointTable,
    Tips,
    ExceptionCard
  },
  data() {
    return {
      loading: true,
      tipsList: [
        this.$t('gseTopTips1'),
        this.$t('gseTopTips2')
      ],
      accessPointList: [],
      apCreatePermission: false
    }
  },
  computed: {
    ...mapGetters(['permissionSwitch'])
  },
  mounted() {
    if (this.permissionSwitch) {
      this.getCreatePermission()
    }
    this.getAccessPointList()
  },
  methods: {
    ...mapActions('config', [
      'requestAccessPointList', 'requestAccessPointIsUsing', 'requestDeletetPoint',
      'requestPluginBase', 'getApPermission'
    ]),
    async getAccessPointList() {
      this.loading = true
      const data = await this.requestAccessPointList()
      data.forEach((point) => {
        point.is_used = true
      })
      this.accessPointList.splice(0, this.accessPointList.length, ...data)
      this.loading = false
      const status = await this.requestAccessPointIsUsing()
      if (status) {
        data.forEach((point) => {
          point.is_used = point.is_default || status.some(id => id === point.id)
        })
        this.accessPointList.splice(0, this.accessPointList.length, ...data)
      }
    },
    operaHandler(data, type) {
      if (type === 'delete') {
        this.$bkInfo({
          type: 'warning',
          title: this.$t('确认删除此接入点'),
          confirmFn: async (vm) => {
            vm.close()
            this.loading = true
            const res = await this.requestDeletetPoint({ pointId: data.id })
            if (!!res && res.result) {
              const index = this.accessPointList.findIndex(item => item.id === data.id)
              this.accessPointList.splice(index, 1)
              this.$bkMessage({
                theme: 'success',
                message: this.$t('删除接入点成功')
              })
            }
            this.loading = false
          }
        })
      } else {
        const route = {
          name: 'accessPoint'
        }
        if (type !== 'add') {
          route.params = {
            pointId: `${data.id}`
          }
        }
        this.$router.push(route)
      }
    },
    async getCreatePermission() {
      const res = await this.getApPermission()
      this.apCreatePermission = res.create_action
    },
    handleApplyPermission(accessPoint) {
      bus.$emit('show-permission-modal', {
        apply_info: [{
          action: 'ap_view',
          instance_id: accessPoint.id,
          instance_name: accessPoint.name
        }]
      })
    }
  }
}
</script>

<style lang="postcss" scoped>
.mb14 {
  margin-bottom: 14px;
}
.w100 {
  width: 100px;
}
.gse-config-wrapper {
  padding-bottom: 20px;
  min-height: calc(100vh - 142px);
  overflow: auto;
  .gse-config-container {
    margin-top: 24px;
  }
  .access-point-collapse {
    /deep/ .right-panel-title {
      padding-right: 14px;
    }
    /deep/ .title-desc {
      width: 100%;
    }
  }
  .access-point-item + .access-point-item {
    margin-top: 20px;
  }
  .collapse-header {
    display: flex;
    padding: 14px 0 15px 5px;
    .access-point-status {
      padding-top: 4px;
      font-size: 0;
    }
    .status-mark {
      margin-right: 0;
    }
    .status-normal {
      border-color: #e5f6ea;
      background: #3fc06d;
    }
    .status-abnormal {
      border-color: #ffe6e6;
      background: #ea3636;
    }
    .header-title {
      flex: 1;
      padding-left: 12px;
      font-size: 0;
    }
    .block-flex {
      display: flex;
      align-items: center;
    }
    .access-point-title {
      display: inline-block;
      margin: 0;
      font-size: 14px;
      color: #313238;
    }
    .title-tag {
      display: inline-block;
      margin-left: 10px;
      padding: 0 4px;
      line-height: 16px;
      border-radius: 2px;
      font-size: 12px;
      font-weight: normal;
      color: #fff;
      background: #979ba5;
    }
    .access-point-remarks {
      display: flex;
      margin-top: 6px;
      line-height: 14px;
      font-size: 12px;
      font-weight: normal;
      color: #979ba5;
    }
    .point-id {
      padding-left: 10px;
    }
    .point-desc {
      margin-left: 10px;
      padding-left: 10px;
      border-left: 1px solid #dcdee5;
    }
  }
  .access-point-operation {
    margin-left: 10px;
    height: auto;
    font-size: 14px;
    color: #979ba5;
    &:not(.is-disabled):hover {
      color: #3a84ff;
    }
  }
  .collapse-container {
    background: #fff;
  }
  .not-outer-border {
    margin: 0 -1px;
    /deep/ table {
      margin: -2px 0 -1px 0;
      z-index: 50;
    }
  }
}
</style>

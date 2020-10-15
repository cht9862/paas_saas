<template>
    <bk-dialog
        :value="show"
        width="1105"
        :show-footer="false"
        @value-change="handleValueChange">
        <template>
            <div class="log-version" v-bkloading="{ isLoading: loading }">
                <div class="log-version-left">
                    <ul class="left-list">
                        <li class="left-list-item"
                            :class="{ 'item-active': index === active }"
                            v-for="(item,index) in logList"
                            :key="index"
                            @click="handleItemClick(index)">
                            <span class="item-title">{{item.title}}</span>
                            <span class="item-date">{{item.date}}</span>
                            <span v-if="index === current" class="item-current"> {{ $t('当前版本') }} </span>
                        </li>
                    </ul>
                </div>
                <div class="log-version-right">
                    <!-- eslint-disable-next-line vue/no-v-html -->
                    <div class="detail-container" v-html="currentLog.detail"></div>
                </div>
            </div>
        </template>
    </bk-dialog>
</template>
<script>
import { axiosInstance } from '@/api'

export default {
  name: 'log-version',
  props: {
    // 是否显示
    dialogShow: Boolean
  },
  data() {
    return {
      show: false,
      current: 0,
      active: 0,
      logList: [],
      loading: false
    }
  },
  computed: {
    currentLog() {
      return this.logList[this.active] || {}
    }
  },
  watch: {
    dialogShow: {
      async handler(v) {
        this.show = v
        if (v) {
          this.loading = true
          this.logList = await this.getVersionLogsList()
          if (this.logList.length) {
            await this.handleItemClick()
          }
          this.loading = false
        }
      },
      immediate: true
    }
  },
  beforeDestroy() {
    this.show = false
    this.$emit('update:dialogShow', false)
  },
  methods: {
    //  dialog显示变更触发
    handleValueChange(v) {
      this.$emit('update:dialogShow', v)
    },
    // 点击左侧log查看详情
    async handleItemClick(v = 0) {
      this.active = v
      if (!this.currentLog.detail) {
        this.loading = true
        const detail = await this.getVersionLogsDetail()
        this.currentLog.detail = detail
        this.loading = false
      }
    },
    // 获取左侧版本日志列表
    async getVersionLogsList() {
      const url = 'version_log/version_logs_list/'
      const { data } = await axiosInstance({
        method: 'get',
        url,
        baseURL: window.PROJECT_CONFIG.SITE_URL
      }).catch(() => ({ data: [] }))
      console.info(data)
      return data.map(item => ({ title: item[0], date: item[1], detail: '' }))
    },
    // 获取右侧对应的版本详情
    async getVersionLogsDetail() {
      const url = 'version_log/version_log_detail/'
      const { data } = await axiosInstance({
        method: 'get',
        url,
        baseURL: window.PROJECT_CONFIG.SITE_URL,
        params: {
          log_version: this.currentLog.title
        }
      }).catch(() => ({ data: '' }))
      return data
    }
  }
}
</script>
<style lang="scss" scoped>
.log-version {
  display: flex;
  margin: -33px -24px -26px;
  &-left {
    flex: 0 0 260px;
    background-color: #fafbfd;
    border-right: 1px solid #dcdee5;
    padding: 40px 0;
    display: flex;
    font-size: 12px;
    .left-list {
      border-top: 1px solid #dcdee5;
      border-bottom: 1px solid #dcdee5;
      height: 520px;
      overflow: auto;
      display: flex;
      flex-direction: column;
      width: 100%;
      &-item {
        flex: 0 0 54px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-left: 30px;
        position: relative;
        border-bottom: 1px solid #dcdee5;
        &:hover {
          cursor: pointer;
          background-color: #fff;
        }
        .item-title {
          color: #313238;
          font-size: 16px;
        }
        .item-date {
          color: #979ba5;
        }
        .item-current {
          position: absolute;
          right: 20px;
          top: 8px;
          background-color: #699df4;
          border-radius: 2px;
          width: 58px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
        }
        &.item-active {
          background-color: #fff;
          &::before {
            content: " ";
            position: absolute;
            top: 0px;
            bottom: 0px;
            left: 0;
            width: 6px;
            background-color: #3a84ff;
          }
        }
      }
    }
  }
  &-right {
    flex: 1;
    padding: 25px 30px 50px 45px;
    .detail-container {
      max-height: 525px;
      overflow: auto;
    }
  }
}
</style>

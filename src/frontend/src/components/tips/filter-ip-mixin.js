export default {
  data() {
    return {
      // 过滤ip列表
      filterList: [],
      // 是否显示过滤提示
      showFilterTips: false,
      // ip过滤对话框
      showFilterDialog: false
    }
  },
  methods: {
    /**
     * 处理过滤IP信息
     */
    handleFilterIp(result, isInstall) {
      if (result) {
        if (result.job_id) {
          // this.handleShowFilterMsg(result.ip_filter)
          isInstall ? this.$router.push({ name: 'taskDetail', params: { taskId: result.job_id } })
            : this.$router.replace({ name: 'taskDetail', params: { taskId: result.job_id } })
        } else {
          this.handleShowMsg(result.ip_filter)
        }
      }
    },
    /**
     * 部分过滤提示
     */
    handleShowFilterMsg(data = []) {
      if (!data || !data.length) return
      this.$bkMessage({
        theme: 'warning',
        message: this.$t('部分过滤提示', { firstIp: data[0].ip, total: data.length })
      })
    },
    /**
     * 全部过滤错误提示
     */
    handleShowMsg(data) {
      this.filterList = data
      const h = this.$createElement
      this.$bkMessage({
        theme: 'error',
        message: h('p', [
          this.$t('全部过滤提示'),
          h('span', {
            style: {
              color: '#3A84FF',
              cursor: 'pointer'
            },
            on: {
              click: this.handleShowDetail
            }
          }, this.$t('查看详情'))
        ]),
        onClose: () => {
          this.showFilterTips = true
        }
      })
    },
    /**
     * 显示过滤IP详情
     */
    handleShowDetail() {
      this.showFilterDialog = true
    }
  }
}

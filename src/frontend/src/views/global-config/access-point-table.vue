<template>
    <div>
        <table class="access-point-table">
            <thead>
                <tr>
                    <th with="125"></th>
                    <th with="100"></th>
                    <th with="100"></th>
                    <th with="735"></th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td :rowspan="rowspanNum.servers + 3">{{ $t('Server信息') }}</td>
                    <td rowspan="2">{{ $t('地域信息') }}</td>
                    <td>{{ $t('区域') }}</td>
                    <td class="table-content">{{ formData.region_id }}</td>
                </tr>
                <tr>
                    <td>{{ $t('城市') }}</td>
                    <td class="table-content">{{ formData.city_id }}</td>
                </tr>
                <tr>
                    <td>Zookeeper</td>
                    <td>{{ $t('集群地址') }}</td>
                    <td class="table-content">{{ zookeeper }}</td>
                </tr>
                <template v-for="(str, idx) in serversMap">
                    <tr v-for="(server, index) in formData[str]" :key="`server${idx + index}`">
                        <td>{{ `${str} ${ index + 1 }` }}</td>
                        <td>IP</td>
                        <td class="table-content">{{ `${ $t('内网') + server.inner_ip };  ${ $t('外网') + server.outer_ip }` }}</td>
                    </tr>
                </template>
                <tr>
                    <td :rowspan="rowspanNum.agent">{{ $t('Agent信息') }}</td>
                    <td>{{ $t('安装包') }}</td>
                    <td>URL</td>
                    <td class="table-content">{{ `${ $t('内网') + formData.package_inner_url };  ${ $t('外网') + formData.package_outer_url }` }}</td>
                </tr>
                <template v-if="rowspanNum.linux">
                    <tr v-for="(path, index) in formData.linux" :key="index + 100">
                        <td v-if="index === 0" :rowspan="rowspanNum.linux">Linux</td>
                        <td>{{ path.name }}</td>
                        <td class="table-content">{{ path.value }}</td>
                    </tr>
                </template>
                <template v-if="rowspanNum.windows">
                    <tr v-for="(path, index) in formData.windows" :key="index + 200">
                        <td v-if="index === 0" :rowspan="rowspanNum.windows">Windows</td>
                        <td>{{ path.name }}</td>
                        <td class="table-content">{{ path.value }}</td>
                    </tr>
                </template>
            </tbody>
        </table>
    </div>
</template>

<script>
export default {
  name: 'AccessPointTable',
  props: {
    accessPoint: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      pathMap: {
        dataipc: 'dataipc',
        setup_path: this.$t('安装路径'),
        data_path: this.$t('数据文件路径'),
        run_path: this.$t('运行时路径'),
        log_path: this.$t('日志文件路径'),
        temp_path: this.$t('临时文件路径')
      },
      serversMap: ['BtfileServer', 'DataServer', 'TaskServer'],
      sortLinux: ['dataipc', 'setup_path', 'data_path', 'run_path', 'log_path'],
      sortWin: ['dataipc', 'setup_path', 'data_path', 'log_path'],
      formData: {}
    }
  },
  computed: {
    // 将表格rowspan的值计算出来
    rowspanNum() {
      const tableRow = {
        servers: 0,
        agent: 0,
        linux: this.sortLinux.length,
        windows: this.sortWin.length
      }
      this.serversMap.forEach((item) => {
        tableRow.servers += this.accessPoint[item] ? this.accessPoint[item].length : 0
      })
      tableRow.agent = tableRow.linux + tableRow.windows + 1
      return tableRow
    },
    zookeeper() {
      if (this.accessPoint.zk_hosts) {
        return this.accessPoint.zk_hosts.map(host => `${host.zk_ip}:${host.zk_port}`).join(',')
      }
      return ''
    }
  },
  created() {
    this.resetData()
  },
  methods: {
    resetData() {
      // agent_config 需要按顺序排序
      const { agent_config: { linux, windows } } = this.accessPoint
      const sortLinux = this.sortLinux.map(item => ({
        name: this.pathMap[item],
        value: linux[item]
      }))
      const sortWindows = this.sortWin.map(item => ({
        name: this.pathMap[item],
        value: windows[item]
      }))
      this.formData = Object.assign({}, this.accessPoint, { linux: sortLinux, windows: sortWindows })
    }
  }
}
</script>

<style lang="postcss">
.access-point-table {
  width: 100%;
  color: #313238;
  thead {
    display: none;
  }
  th,
  td {
    padding: 0 15px;
    line-height: 42px;
    border: 1px solid #dcdee5;
  }
  .table-content {
    color: #63656e;
  }
}
</style>

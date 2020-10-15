<template>
  <div class="access-point-info">
    <bk-form :label-width="120" :model="formData" ref="formData">
      <template v-for="(system, index) in pathSet">
        <h3 :class="['block-title', { mt40: !index }]" :key="index">{{ system.title }}</h3>
        <bk-form-item
          v-for="(path, itemIndex) in system.childrend"
          error-display-type="normal"
          :label="path.label"
          :property="path.prop"
          :required="path.required"
          :rules="rules[path.rules]"
          :key="`${system.type}-${itemIndex}`">
          <bk-input
            v-model.trim="formData[path.prop]"
            :placeholder="path.placeholder || $t('请输入')"
            @blur="pathRepair(arguments, path.prop)">
          </bk-input>
        </bk-form-item>
      </template>

      <bk-form-item class="mt30 item-button-group">
        <bk-button
          class="nodeman-primary-btn"
          theme="primary"
          :disabled="submitLoading"
          @click.stop.prevent="submitHandle">
          {{ $t('确认') }}
        </bk-button>
        <bk-button
          class="nodeman-cancel-btn"
          :disabled="submitLoading"
          @click="stepNext">
          {{ $t('上一步') }}
        </bk-button>
        <bk-button
          class="nodeman-cancel-btn"
          :disabled="submitLoading"
          @click="cancel">
          {{ $t('取消') }}
        </bk-button>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
import formLabelMixin from '@/common/form-label-mixin'
import { mapGetters, mapActions } from 'vuex'
import { isEmpty, transformDataKey, toLine } from '@/common/util'

export default {
  name: 'StepInfo',
  mixins: [formLabelMixin],
  props: {
    pointId: {
      type: String,
      default: ''
    },
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      submitLoading: false,
      pathSet: [
        {
          type: 'linux',
          title: this.$t('Linux系统的Agent信息'),
          childrend: [
            { label: 'dataipc', required: true, prop: 'linuxDataipc', rules: 'linuxDataipc', placeholder: '' },
            {
              label: this.$t('安装路径'), required: true, prop: 'linuxSetupPath',
              rules: 'linuxInstallPath', placeholder: ''
            },
            { label: this.$t('数据文件路径'), required: true, prop: 'linuxDataPath', rules: 'linuxPath', placeholder: '' },
            { label: this.$t('运行时路径'), required: true, prop: 'linuxRunPath', rules: 'linuxPath', placeholder: '' },
            { label: this.$t('日志文件路径'), required: true, prop: 'linuxLogPath', rules: 'linuxPath', placeholder: '' },
            { label: this.$t('临时文件路径'), required: true, prop: 'linuxTempPath', rules: 'linuxPath', placeholder: '' }
          ]
        },
        {
          type: 'windows',
          title: this.$t('Windows系统的Agent信息'),
          childrend: [
            {
              label: 'dataipc',
              required: true,
              prop: 'windowsDataipc',
              rules: 'winDataipc',
              placeholder: this.$t('请输入不小于零的整数')
            },
            {
              label: this.$t('安装路径'),
              required: true,
              prop: 'windowsSetupPath',
              rules: 'winInstallPath',
              placeholder: ''
            },
            { label: this.$t('数据文件路径'), required: true, prop: 'windowsDataPath', rules: 'winPath', placeholder: '' },
            { label: this.$t('日志文件路径'), required: true, prop: 'windowsLogPath', rules: 'winPath', placeholder: '' },
            { label: this.$t('临时文件路径'), required: true, prop: 'windowsTempPath', rules: 'winPath', placeholder: '' }
          ]
        }
      ],
      formData: {
        linuxDataipc: '/var/run/ipc.state.report.cloud',
        linuxSetupPath: '/usr/local/gse',
        linuxDataPath: '/usr/local/gse',
        linuxRunPath: '/usr/local/gse',
        linuxLogPath: '/usr/log/gse',
        linuxTempPath: '/tmp',
        windowsDataipc: '',
        windowsSetupPath: 'C:\\gse',
        windowsDataPath: 'C:\\gse',
        windowsLogPath: 'C:\\gse\\logs',
        windowsTempPath: 'C:\\tmp'
      },
      // 目录名可以包含但不相等，所以末尾加了 /, 校验的时候给值也需要加上 /
      linuxNotInclude: [
        '/etc/', '/root/', '/boot/', '/dev/', '/sys/', '/tmp/', '/var/', '/usr/lib/',
        '/usr/lib64/', '/usr/include/', '/usr/local/etc/', '/usr/local/sa/', '/usr/local/lib/',
        '/usr/local/lib64/', '/usr/local/bin/', '/usr/local/libexec/', '/usr/local/sbin/'
      ],
      linuxNotIncludeError: [
        '/etc', '/root', '/boot', '/dev', '/sys', '/tmp', '/var', '/usr/lib',
        '/usr/lib64', '/usr/include', '/usr/local/etc', '/usr/local/sa', '/usr/local/lib',
        '/usr/local/lib64', '/usr/local/bin', '/usr/local/libexec', '/usr/local/sbin'
      ],
      // 转换为正则需要四个 \
      winNotInclude: [
        'C:\\\\Windows\\\\', 'C:\\\\Windows\\\\', 'C:\\\\config\\\\',
        'C:\\\\Users\\\\', 'C:\\\\Recovery\\\\'
      ],
      winNotIncludeError: ['C:\\Windows', 'C:\\Windows', 'C:\\config', 'C:\\Users', 'C:\\Recovery'],
      rules: {
        linuxDataipc: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              return /^(\/[A-Za-z0-9_.]{1,}){1,}$/.test(val)
            },
            message: this.$t('LinuxIpc校验不正确'),
            trigger: 'blur'
          }
        ],
        winDataipc: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              return /^(0|[1-9][0-9]*)$/.test(val)
            },
            message: this.$t('winIpc校验不正确'),
            trigger: 'blur'
          }
        ],
        linuxPath: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              return /^(\/[A-Za-z0-9_]{1,16}){1,}$/.test(val)
            },
            message: this.$t('Linux路径格式不正确'),
            trigger: 'blur'
          }
        ],
        winPath: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              return /^([c-zC-Z]:)(\\[A-Za-z0-9_]{1,16}){1,}$/.test(val)
            },
            message: this.$t('windows路径格式不正确'),
            trigger: 'blur'
          }
        ],
        linuxInstallPath: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              // / 开头，至少包含两级目录，且为长度不超过16的大小写英文、数字和下划线
              return /^(\/[A-Za-z0-9_]{1,16}){2,}$/.test(val)
            },
            message: this.$t('Linux路径格式不正确'),
            trigger: 'blur'
          },
          {
            validator: (val) => {
              // 前缀不能匹配到以下
              // /etc, /root, /boot, /dev, /sys, /tmp, /var,
              // /usr/lib, /usr/lib64, /usr/include,
              // /usr/local/etc, /usr/local/sa, /usr/local/lib, /usr/local/lib64, /usr/local/bin, /usr/local/;libexec, /usr/local/sbin
              const path = `${val}/`
              return !this.linuxNotInclude.find(item => path.search(item) > -1)
            },
            message: () => this.$t('不能以如下内容开头', { path: this.linuxNotIncludeError.join(', ') }),
            trigger: 'blur'
          }
        ],
        winInstallPath: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator(val) {
              // [c-zC-Z]:\ 开头，至少包含一级目录，且为长度不超过16的大小写英文、数字和下划线
              return /^([c-zC-Z]:)(\\[A-Za-z0-9_]{1,16}){1,}$/.test(val)
            },
            message: this.$t('windows路径格式不正确'),
            trigger: 'blur'
          },
          {
            validator: (val) => {
              // 前缀不能匹配到 C:\Windows, C:\config, C:\Users, C:\Recovery
              const path = `${val}\\\\`
              return !this.winNotInclude.find(item => path.search(new RegExp(item, 'i')) > -1)
            },
            message: () => this.$t('不能以如下内容开头', { path: this.winNotIncludeError.join(', ') }),
            trigger: 'blur'
          }
        ]
      }
    }
  },
  computed: {
    ...mapGetters('config', ['detail'])
  },
  mounted() {
    this.initConfig()
    this.initLabelWidth(this.$refs.formData)
  },
  methods: {
    ...mapActions('config', ['requestCreatePoint', 'requestEditPoint']),
    initConfig() {
      const { agent_config: { linux, windows } } = this.detail
      try {
        const dataMap = {}
        Object.keys(linux).forEach((key) => {
          if (this.isEdit || linux[key]) {
            dataMap[`linux_${key}`] = linux[key] || ''
          }
        })
        Object.keys(windows).forEach((key) => {
          // 非编辑模式下不能覆盖默认值
          if (this.isEdit || windows[key]) {
            dataMap[`windows_${key}`] = windows[key] || ''
          }
        })
        Object.assign(this.formData, transformDataKey(dataMap))
      } catch (_) {}
    },
    submitHandle() {
      this.$refs.formData.validate().then(async () => {
        const {
          name, zk_account, zk_password, region_id, city_id, zk_hosts, btfileserver,
          dataserver, taskserver, package_inner_url, package_outer_url, description
        } = this.detail
        this.submitLoading = true
        const agentConfig = {
          linux: {},
          windows: {}
        }
        Object.keys(this.formData).forEach((key) => {
          if (/linux/ig.test(key)) {
            const str = toLine(key).replace(/linux_/g, '')
            agentConfig.linux[str] = this.formData[key]
          }
          if (/windows/ig.test(key)) {
            const str = toLine(key).replace(/windows_/g, '')
            agentConfig.windows[str] = this.formData[key]
          }
        })
        const formatData = {
          name,
          zk_account,
          region_id,
          city_id,
          zk_hosts,
          btfileserver,
          dataserver,
          taskserver,
          package_inner_url,
          package_outer_url,
          agent_config: agentConfig,
          description
        }
        // 编辑状态下 zk_password 可以为空
        if (!this.isEdit || !isEmpty(zk_password)) {
          Object.assign(formatData, { zk_password })
        }
        let res
        if (this.isEdit) {
          res = await this.requestEditPoint({ pointId: this.pointId, data: formatData })
        } else {
          res = await this.requestCreatePoint(formatData)
        }
        this.submitLoading = false
        if (res) {
          this.$bkMessage({
            theme: 'success',
            message: this.isEdit ? this.$t('修改接入点成功') : this.$t('新增接入点成功')
          })
          this.cancel()
        }
      }, () => {})
    },
    stepNext() {
      this.$emit('step', 1)
    },
    cancel() {
      this.$router.push({
        name: 'gseConfig'
      })
    },
    // 安装路径修复 - 若路径以 / 结尾，则去掉末尾的 /
    pathRepair(arg, prop) {
      const value = arg[0].trim().replace(/[/\\]+/ig, '/')
      const pathArr = value.split('/').filter(item => !!item)
      if (/linux/ig.test(prop)) {
        this.formData[prop] = `/${pathArr.join('/')}`
      } else {
        if (prop === 'windowsDataipc') {
          return
        }
        this.formData[prop] = pathArr.join('\\')
      }
    }
  }
}
</script>

<style lang="postcss" scoped>

.access-point-info {
  /deep/ form {
    width: 620px;
  }
  .block-title {
    margin: 30px 0 20px 0;
    padding: 0 0 10px 0;
    border-bottom: 1px solid #dcdee5;
    font-size: 14px;
    font-weight: bold;
  }
}
</style>

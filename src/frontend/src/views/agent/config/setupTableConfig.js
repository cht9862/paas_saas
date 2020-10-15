import { authentication, defaultPort } from '@/config/config'

const useTjj = window.PROJECT_CONFIG.USE_TJJ === 'True'
const splitCodeArr = ['\n', '，', ' ', '、', ',']

export const setupTableConfig = [
  {
    label: 'IP地址',
    prop: 'inner_ip',
    type: 'textarea',
    required: true,
    splitCode: splitCodeArr,
    unique: true,
    noRequiredMark: false,
    placeholder: window.i18n.t('多ip输入提示'),
    width: '20%',
    errTag: true,
    rules: [
      {
        content: window.i18n.t('IP不符合规范'),
        validator(value) {
          if (!value) return true
          const regx = new RegExp('^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$')
          const splitCode = splitCodeArr.find(split => value.indexOf(split) > 0)
          value = value.split(splitCode).filter(text => !!text)
            .map(text => text.trim())
          // IP校验
          const ipValidate = value.some(item => !regx.test(item))
          return !ipValidate
        }
      },
      {
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(value) {
          // 一个输入框内不能重复
          if (!value) return true
          const splitCode = splitCodeArr.find(split => value.indexOf(split) > 0)
          value = value.split(splitCode).filter(text => !!text)
            .map(text => text.trim())
          return new Set(value).size === value.length
        }
      },
      {
        trigger: 'blur',
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(v, id) {
          // 与其他输入框的值不能重复
          if (!v) return true
          const row = this.table.data.find(item => item.id === id)
          if (!row) return
          return this.handleValidateUnique(row, {
            prop: 'inner_ip',
            splitCode: splitCodeArr
          })
        }
      },
      {
        trigger: 'blur',
        content: '',
        async validator(v, id) {
          if (!useTjj) return true
          // 铁将军校验
          const splitCode = splitCodeArr.find(split => v.indexOf(split) > 0)
          v = v.split(splitCode).filter(text => !!text)
            .map(text => text.trim())
          const data = await this.fetchPwd({
            hosts: v
          })
          if (data && data.success_ips.length === v.length) {
            const row = this.table.data.find(item => item.id === id)
            if (!row) return true
            if (row.os_type === 'LINUX') {
              row.port = 36000
            }
            row.auth_type = 'TJJ_PASSWORD'
          }
          return true
        }
      }
    ]
  },
  {
    label: '操作系统',
    prop: 'os_type',
    type: 'select',
    batch: true,
    required: true,
    default: 'LINUX',
    options: [
      {
        id: 'WINDOWS',
        name: 'Windows'
      },
      {
        id: 'LINUX',
        name: 'Linux'
      },
      {
        id: 'AIX',
        name: 'AIX'
      }
    ],
    handleValueChange(row) {
      if (row.os_type === 'WINDOWS') {
        row.port = 445
        row.account = 'Administrator'
      } else {
        row.port = defaultPort
        row.account = 'root'
      }
    }
  },
  {
    label: '登录端口',
    prop: 'port',
    type: 'text',
    required: true,
    batch: true,
    default: defaultPort,
    rules: [
      {
        regx: '^([0-9]|[1-9]\\d{1,3}|[1-5]\\d{4}|6[0-4]\\d{4}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$',
        content: window.i18n.t('端口范围', { range: '0-65535' })
      }
    ],
    getReadonly(row) {
      return row && row.os_type === 'WINDOWS'
    }
  },
  {
    label: '登录账号',
    prop: 'account',
    type: 'text',
    required: true,
    batch: true,
    default: 'root'
  },
  {
    label: '认证方式',
    prop: 'auth_type',
    type: 'select',
    required: true,
    batch: true,
    default: 'PASSWORD',
    subTitle: window.i18n.t('密钥方式仅对Linux/AIX系统生效'),
    getOptions(row) {
      return row.os_type === 'WINDOWS' ? authentication.filter(auth => auth.id !== 'KEY') : authentication
    },
    handleValueChange(row) {
      const auth = authentication.find(auth => auth.id === row.auth_type) || {}
      row.prove = auth.default || ''
    }
  },
  {
    label: '密码密钥',
    required: true,
    prop: 'prove',
    type: 'password',
    batch: true,
    subTitle: window.i18n.t('仅对密码认证生效'),
    getReadonly(row) {
      return row.auth_type && row.auth_type === 'TJJ_PASSWORD'
    },
    getCurrentType(row) {
      const auth = authentication.find(auth => auth.id === row.auth_type) || {}
      return auth.type || 'text'
    }
  },
  {
    label: '登录IP',
    prop: 'login_ip',
    type: 'text',
    required: false,
    unique: true,
    noRequiredMark: true,
    placeholder: window.i18n.t('请输入'),
    width: '15%',
    errTag: true,
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
      },
      {
        trigger: 'blur',
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(v, id) {
          // 与其他输入框的值不能重复
          if (!v) return true
          const row = this.table.data.find(item => item.id === id)
          return this.handleValidateUnique(row, {
            prop: 'login_ip'
          })
        }
      }
    ]
  },
  {
    label: 'BT传输加速',
    prop: 'peer_exchange_switch_for_agent',
    type: 'switcher',
    default: true,
    batch: true,
    required: false,
    noRequiredMark: false,
    width: 115
  },
  {
    label: '传输限速',
    prop: 'bt_speed_limit',
    type: 'text',
    batch: true,
    required: false,
    noRequiredMark: false,
    appendSlot: 'MB/s',
    iconOffset: 40,
    width: 160,
    rules: [
      {
        regx: '^[1-9]\\d*$',
        content: window.i18n.t('整数最小值校验提示', { min: 1 })
      }
    ]
  },
  {
    label: '',
    prop: '',
    type: 'operate',
    width: 60
  }
]

export const setupTableManualConfig = [
  {
    label: 'IP地址',
    prop: 'inner_ip',
    type: 'textarea',
    required: true,
    splitCode: splitCodeArr,
    unique: true,
    noRequiredMark: false,
    placeholder: window.i18n.t('多ip输入提示'),
    width: 'auto',
    errTag: true,
    rules: [
      {
        content: window.i18n.t('IP不符合规范'),
        validator(value) {
          if (!value) return true
          const regx = new RegExp('^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$')
          const splitCode = splitCodeArr.find(split => value.indexOf(split) > 0)
          value = value.trim().split(splitCode)
          // IP校验
          const ipValidate = value.some(item => !regx.test(item))
          return !ipValidate
        }
      },
      {
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(value) {
          // 一个输入框内不能重复
          if (!value) return true
          const splitCode = splitCodeArr.find(split => value.indexOf(split) > 0)
          value = value.trim().split(splitCode)
          return new Set(value).size === value.length
        }
      },
      {
        trigger: 'blur',
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(v, id) {
          // 与其他输入框的值不能重复
          if (!v) return true
          const row = this.table.data.find(item => item.id === id)
          if (!row) return
          return this.handleValidateUnique(row, {
            prop: 'inner_ip',
            splitCode: splitCodeArr
          })
        }
      },
      {
        trigger: 'blur',
        content: '',
        async validator(v, id) {
          if (!useTjj) return true
          // 铁将军校验
          const splitCode = splitCodeArr.find(split => v.indexOf(split) > 0)
          v = v.trim().split(splitCode)
          const data = await this.fetchPwd({
            hosts: v
          })
          if (data && data.success_ips.length === v.length) {
            const row = this.table.data.find(item => item.id === id)
            if (!row) return true
            if (row.os_type === 'LINUX') {
              row.port = 36000
            }
            row.auth_type = 'TJJ_PASSWORD'
          }
          return true
        }
      }
    ]
  },
  {
    label: '操作系统',
    prop: 'os_type',
    type: 'select',
    batch: true,
    required: true,
    default: 'LINUX',
    width: 'auto',
    options: [
      {
        id: 'WINDOWS',
        name: 'Windows'
      },
      {
        id: 'LINUX',
        name: 'Linux'
      },
      {
        id: 'AIX',
        name: 'AIX'
      }
    ],
    handleValueChange(row) {
      if (row.os_type === 'WINDOWS') {
        row.port = 445
        row.account = 'Administrator'
      } else {
        row.port = defaultPort
        row.account = 'root'
      }
    }
  },
  {
    label: '登录IP',
    prop: 'login_ip',
    type: 'text',
    required: false,
    unique: true,
    noRequiredMark: true,
    placeholder: window.i18n.t('请输入'),
    width: 'auto',
    errTag: true,
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
      },
      {
        trigger: 'blur',
        content: window.i18n.t('冲突校验', { prop: 'IP' }),
        validator(v, id) {
          // 与其他输入框的值不能重复
          if (!v) return true
          const row = this.table.data.find(item => item.id === id)
          return this.handleValidateUnique(row, {
            prop: 'login_ip'
          })
        }
      }
    ]
  },
  {
    label: 'BT传输加速',
    prop: 'peer_exchange_switch_for_agent',
    type: 'switcher',
    default: true,
    batch: true,
    required: false,
    noRequiredMark: false,
    width: 115
  },
  {
    label: '传输限速',
    prop: 'bt_speed_limit',
    type: 'text',
    batch: true,
    required: false,
    noRequiredMark: false,
    appendSlot: 'MB/s',
    iconOffset: 40,
    width: 160,
    rules: [
      {
        regx: '^[1-9]\\d*$',
        content: window.i18n.t('整数最小值校验提示', { min: 1 })
      }
    ]
  },
  {
    label: '',
    prop: '',
    type: 'operate',
    width: 60
  }
]

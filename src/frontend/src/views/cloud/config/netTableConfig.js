import { authentication } from '@/config/config'
export const setupInfo = [
  {
    label: '内网IP',
    prop: 'inner_ip',
    tips: window.i18n.t('内网IP提示'),
    required: true,
    type: 'text',
    unique: true,
    errTag: true,
    iconOffset: 10,
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
            prop: 'inner_ip',
            splitCode: ['，', ' ', '、', ',']
          })
        }
      }
    ]
  },
  {
    label: '对外通讯IP',
    prop: 'outer_ip',
    tips: window.i18n.t('对外通讯IP提示'),
    type: 'text',
    unique: true,
    errTag: true,
    required: true,
    iconOffset: 10,
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
            prop: 'outer_ip',
            splitCode: ['，', ' ', '、', ',']
          })
        }
      }
    ]
  },
  {
    label: '登录IP',
    prop: 'login_ip',
    tips: window.i18n.t('登录IP提示'),
    type: 'text',
    required: false,
    unique: true,
    errTag: true,
    placeholder: window.i18n.t('留空默认为内网IP'),
    iconOffset: 10,
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
            prop: 'login_ip',
            splitCode: ['，', ' ', '、', ',']
          })
        }
      }
    ]
  },
  {
    label: '认证方式',
    prop: 'auth_type',
    type: 'select',
    required: true,
    default: 'PASSWORD',
    iconOffset: 10,
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
    subTitle: window.i18n.t('仅对密码认证生效'),
    iconOffset: 10,
    getReadonly(row) {
      return row.auth_type && row.auth_type === 'TJJ_PASSWORD'
    },
    getCurrentType(row) {
      const auth = authentication.find(auth => auth.id === row.auth_type) || {}
      return auth.type || 'text'
    }
  },
  {
    label: 'BT传输加速',
    prop: 'peer_exchange_switch_for_agent',
    type: 'switcher',
    default: true,
    required: false,
    width: 115
  },
  {
    label: '传输限速',
    prop: 'bt_speed_limit',
    type: 'text',
    required: false,
    appendSlot: 'MB/s',
    iconOffset: 45,
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
    width: 50
  }
]

export const setupManualInfo = [
  {
    label: '内网IP',
    prop: 'inner_ip',
    tips: window.i18n.t('内网IP提示'),
    required: true,
    type: 'text',
    unique: true,
    errTag: true,
    iconOffset: 10,
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
            prop: 'inner_ip',
            splitCode: ['，', ' ', '、', ',']
          })
        }
      }
    ]
  },
  {
    label: '对外通讯IP',
    prop: 'outer_ip',
    tips: window.i18n.t('对外通讯IP提示'),
    type: 'text',
    unique: true,
    errTag: true,
    required: true,
    iconOffset: 10,
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
            prop: 'outer_ip',
            splitCode: ['，', ' ', '、', ',']
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
    required: false,
    width: 115
  },
  {
    label: '传输限速',
    prop: 'bt_speed_limit',
    type: 'text',
    required: false,
    appendSlot: 'MB/s',
    iconOffset: 45,
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
    width: 50,
    local: true
  }
]

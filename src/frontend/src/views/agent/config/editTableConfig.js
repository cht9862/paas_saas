import { authentication, defaultPort } from '@/config/config'

export const editConfig = [
  {
    label: 'IP地址',
    prop: 'inner_ip',
    type: 'text',
    required: true,
    noRequiredMark: false,
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
      }
    ],
    readonly: true
  },
  {
    label: '业务',
    prop: 'bk_biz_id',
    type: 'biz',
    required: true,
    multiple: false,
    noRequiredMark: false,
    readonly: true,
    placeholder: window.i18n.t('选择业务')
  },
  {
    label: '云区域',
    prop: 'bk_cloud_id',
    type: 'select',
    required: true,
    popoverMinWidth: 160,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
    getOptions() {
      return this.cloudList.map(item => ({
        name: item.bk_cloud_name,
        id: item.bk_cloud_id
      }))
    },
    getProxyStatus(row) {
      return row.proxyStatus
    },
    readonly: true
  },
  {
    label: '接入点',
    prop: 'ap_id',
    type: 'select',
    required: true,
    batch: true,
    default: -1,
    options: [],
    popoverMinWidth: 160,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
    getOptions() {
      return this.apList
    }
  },
  {
    label: '操作系统',
    prop: 'os_type',
    type: 'select',
    required: true,
    batch: true,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
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
    getReadonly(row) {
      return row.is_manual || /RELOAD_AGENT/ig.test(this.localMark)
    },
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
    placeholder: window.i18n.t('请输入')
  },
  {
    label: '认证方式',
    prop: 'auth_type',
    type: 'select',
    required: true,
    batch: true,
    subTitle: window.i18n.t('密钥方式仅对Linux/AIX系统生效'),
    default: 'PASSWORD',
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
    prop: 'prove',
    type: 'password',
    required: false,
    show: true, // 常显项
    batch: true,
    noRequiredMark: false,
    subTitle: window.i18n.t('仅对密码认证生效'),
    placeholder: window.i18n.t('请输入'),
    rules: [
      {
        content: window.i18n.t('认证信息过期'),
        validator(v, id) {
          const row = this.table.data.find(row => row.id === id)
          const isValueEmpty = typeof v === 'undefined' || v === null || v === ''
          return !(isValueEmpty && row && (!row.is_manual && row.re_certification)) // 手动安装不需要校验密码过期
        }
      }
    ],
    getReadonly(row) {
      return row.auth_type && row.auth_type === 'TJJ_PASSWORD'
    },
    getCurrentType(row) {
      const auth = authentication.find(auth => auth.id === row.auth_type) || {}
      return auth.type || 'text'
    },
    getDefaultValue(row) {
      if (row.auth_type === 'TJJ_PASSWORD') {
        return window.i18n.t('自动选择')
      }
      return ''
    }
  },
  {
    label: '登录IP',
    prop: 'login_ip',
    type: 'text',
    required: false,
    noRequiredMark: false,
    placeholder: window.i18n.t('请输入'),
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
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
    placeholder: window.i18n.t('请输入'),
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
    width: 35
  }
]

export const editManualConfig = [
  {
    label: 'IP地址',
    prop: 'inner_ip',
    type: 'text',
    required: true,
    noRequiredMark: false,
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
      }
    ],
    readonly: true
  },
  {
    label: '业务',
    prop: 'bk_biz_id',
    type: 'biz',
    required: true,
    multiple: false,
    noRequiredMark: false,
    readonly: true
  },
  {
    label: '云区域',
    prop: 'bk_cloud_id',
    type: 'select',
    required: true,
    popoverMinWidth: 160,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
    getOptions() {
      return this.cloudList.map(item => ({
        name: item.bk_cloud_name,
        id: item.bk_cloud_id
      }))
    },
    getProxyStatus(row) {
      return row.proxyStatus
    },
    readonly: true
  },
  {
    label: '接入点',
    prop: 'ap_id',
    type: 'select',
    required: true,
    batch: true,
    default: -1,
    options: [],
    popoverMinWidth: 160,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
    getOptions() {
      return this.apList
    }
  },
  {
    label: '操作系统',
    prop: 'os_type',
    type: 'select',
    required: true,
    batch: true,
    noRequiredMark: false,
    placeholder: window.i18n.t('请选择'),
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
    noRequiredMark: false,
    placeholder: window.i18n.t('请输入'),
    rules: [
      {
        regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
        content: window.i18n.t('IP不符合规范')
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
    placeholder: window.i18n.t('请输入'),
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
    width: 35
  }
]

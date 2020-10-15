export const detailConfig = [
  {
    prop: 'bk_cloud_id',
    label: window.i18n.t('云区域ID'),
    readonly: true
  },
  {
    prop: 'bk_biz_name',
    label: window.i18n.t('归属业务'),
    readonly: true
  },
  {
    prop: 'inner_ip',
    label: window.i18n.t('内网IP'),
    type: 'text',
    readonly: true,
    validation: {
      regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
      content: window.i18n.t('IP不符合规范')
    }
  },
  {
    prop: 'account',
    label: window.i18n.t('登录账号'),
    type: 'text',
    readonly: true
  },
  {
    prop: 'outer_ip',
    label: window.i18n.t('对外通讯IP'),
    tip: window.i18n.t('对外通讯IP提示'),
    type: 'text',
    readonly: true,
    validation: {
      regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
      content: window.i18n.t('IP不符合规范')
    }
  },
  {
    prop: 'port',
    label: window.i18n.t('登录端口'),
    type: 'text',
    readonly: true,
    validation: {
      regx: '^([0-9]|[1-9]\\d{1,3}|[1-5]\\d{4}|6[0-4]\\d{4}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$',
      content: window.i18n.t('端口范围', { range: '0-65535' })
    }
  },
  {
    prop: 'login_ip',
    label: window.i18n.t('登录IP'),
    type: 'text',
    readonly: true,
    validation: {
      regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$',
      content: window.i18n.t('IP不符合规范')
    }
  },
  {
    prop: 'auth_type',
    label: window.i18n.t('认证方式'),
    type: 'auth',
    readonly: true
  },
  {
    prop: 'peer_exchange_switch_for_agent',
    label: window.i18n.t('BT传输加速'),
    type: 'tag-switch',
    readonly: true
  },
  {
    prop: 'bt_speed_limit',
    label: window.i18n.t('传输限速'),
    type: 'text',
    unit: 'MB/s',
    readonly: true
  }
]

export default detailConfig

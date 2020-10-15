<template>
    <div :class="['task-config-wrapper', { 'permission-disabled': !hasPermission }]" v-bkloading="{ isLoading: loading }">
        <section class="task-config-container" v-if="hasPermission">
            <bk-form class="task-config-form" :label-width="165" :model="configParam" ref="taskConfigForm">
                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('安装PAgent超时时间')" :required="true" :rules="rules.outTime" property="installPAgentTimeout" error-display-type="normal">
                        <bk-input v-model.trim="configParam.installPAgentTimeout" :placeholder="$t('请输入')">
                            <template slot="append">
                                <div class="group-text">s</div>
                            </template>
                        </bk-input>
                        <bk-popover theme="light" placement="right-start" class="info-tooltips">
                            <span class="nodeman-icon nc-tips-fill fl info-tooltips-icon"></span>
                            <div class="info-tooltips-content" slot="content">{{ $t('安装PAgent超时时间tip') }}</div>
                        </bk-popover>
                    </bk-form-item>
                </div>

                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('安装Agent超时时间')" :required="true" :rules="rules.outTime" property="installAgentTimeout" error-display-type="normal">
                        <bk-input v-model.trim="configParam.installAgentTimeout" :placeholder="$t('请输入')">
                            <template slot="append">
                                <div class="group-text">s</div>
                            </template>
                        </bk-input>
                        <bk-popover theme="light" placement="right-start" class="info-tooltips">
                            <span class="nodeman-icon nc-tips-fill fl info-tooltips-icon"></span>
                            <div class="info-tooltips-content" slot="content">{{ $t('安装Agent超时时间tip') }}</div>
                        </bk-popover>
                    </bk-form-item>
                </div>

                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('安装Proxy超时时间')" :required="true" :rules="rules.outTime" property="installProxyTimeout" error-display-type="normal">
                        <bk-input v-model.trim="configParam.installProxyTimeout" :placeholder="$t('请输入')">
                            <template slot="append">
                                <div class="group-text">s</div>
                            </template>
                        </bk-input>
                        <bk-popover theme="light" placement="right-start" class="info-tooltips">
                            <span class="nodeman-icon nc-tips-fill fl info-tooltips-icon"></span>
                            <div class="info-tooltips-content" slot="content">{{ $t('安装Proxy超时时间tip') }}</div>
                        </bk-popover>
                    </bk-form-item>
                </div>

                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('安装下载限速')" :required="true" :rules="rules.speed" property="installDownloadLimitSpeed" error-display-type="normal">
                        <bk-input v-model.trim="configParam.installDownloadLimitSpeed" :placeholder="$t('请输入')">
                            <template slot="append">
                                <div class="group-text">KB/s</div>
                            </template>
                        </bk-input>
                        <bk-popover theme="light" placement="right-start" class="info-tooltips">
                            <span class="nodeman-icon nc-tips-fill fl info-tooltips-icon"></span>
                            <div class="info-tooltips-content" slot="content">{{ $t('安装下载限速tip') }}</div>
                        </bk-popover>
                    </bk-form-item>
                </div>

                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('并行安装数')" :required="true" :rules="rules.install" property="parallelInstallNumber" error-display-type="normal">
                        <bk-input v-model.trim="configParam.parallelInstallNumber" :placeholder="$t('请输入')"></bk-input>
                    </bk-form-item>
                </div>
                <div class="bk-form-info-item clearfix">
                    <bk-form-item class="fl" :label="$t('节点管理日志级别')" :required="true" :rules="rules.must" property="nodeManLogLevel" error-display-type="normal">
                        <bk-select v-model="configParam.nodeManLogLevel" ext-cls="log-level-select" :clearable="false">
                            <bk-option v-for="option in logLevelMap"
                                       :key="option.id"
                                       :id="option.id"
                                       :name="option.name">
                            </bk-option>
                        </bk-select>
                    </bk-form-item>
                </div>

                <div class="bk-form-info-item item-button-group mt30 clearfix">
                    <bk-form-item>
                        <bk-button
                            class="nodeman-primary-btn"
                            theme="primary"
                            :loading="submitLoading"
                            :disabled="submitLoading"
                            @click="submitHandler">
                            {{ $t('保存') }}
                        </bk-button>
                        <bk-button
                            class="nodeman-cancel-btn"
                            theme="default"
                            :disabled="submitLoading"
                            @click="resetHandler">
                            {{ $t('重置') }}
                        </bk-button>
                    </bk-form-item>
                </div>
            </bk-form>
        </section>
        <exception-page v-else type="notPower" :sub-title="$t('全局任务Auth')" @click="handleApplyPermission"></exception-page>
    </div>
</template>

<script>
import formLabelMixin from '@/common/form-label-mixin'
import ExceptionPage from '@/components/exception/exception-page'
import { bus } from '@/common/bus'
import { mapActions } from 'vuex'

export default {
  name: 'TaskConfig',
  components: {
    ExceptionPage
  },
  mixins: [formLabelMixin],
  data() {
    return {
      loading: false,
      submitLoading: false,
      configParam: {
        installPAgentTimeout: 300,
        installAgentTimeout: 300,
        installProxyTimeout: 300,
        installDownloadLimitSpeed: 0,
        parallelInstallNumber: 100,
        nodeManLogLevel: 'ERROR'
      },
      defaultsParam: {},
      logLevelMap: [
        { id: 'ERROR', name: 'Error' },
        { id: 'INFO', name: 'Info' },
        { id: 'DEBUG', name: 'Debug' }
      ],
      hasPermission: true,
      rules: {
        must: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ],
        speed: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator: val => /^\d+$/.test(val),
            message: this.$t('整数最小值校验提示', { min: 0 }),
            trigger: 'blur'
          }
        ],
        install: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator: val => /^\+?[1-9][0-9]*$/.test(val) && Number(val) <= 2000,
            message: this.$t('整数范围校验提示', { max: 2000, min: 1 }),
            trigger: 'blur'
          }
        ],
        outTime: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            validator: val => /^\d+$/.test(val) && Number(val) <= 86400,
            message: this.$t('整数范围校验提示', { max: 86400, min: 0 }),
            trigger: 'blur'
          }
        ]
      }
    }
  },
  created() {
    this.hasPermission = window.PROJECT_CONFIG.GLOBAL_TASK_CONFIG_PERMISSION === 'True'
  },
  mounted() {
    if (this.hasPermission) {
      Object.assign(this.defaultsParam, this.configParam)
      this.requestConfig()
      this.initLabelWidth(this.$refs.taskConfigForm)
    }
  },
  methods: {
    ...mapActions('config', ['requestGlobalSettings', 'saveGlobalSettings']),
    submitHandler() {
      this.$refs.taskConfigForm.validate().then(() => {
        this.saveConfig()
      })
        .catch(() => {})
    },
    resetHandler() {
      Object.assign(this.configParam, this.defaultsParam)
    },
    async requestConfig() {
      this.loading = true
      const res = await this.requestGlobalSettings()
      Object.assign(this.configParam, res.jobSettings)
      this.loading = false
    },
    async saveConfig() {
      this.submitLoading = true
      const {
        installPAgentTimeout, installAgentTimeout, installProxyTimeout,
        installDownloadLimitSpeed, parallelInstallNumber, nodeManLogLevel
      } = this.configParam
      const res = await this.saveGlobalSettings({
        install_p_agent_timeout: installPAgentTimeout,
        install_agent_timeout: installAgentTimeout,
        install_proxy_timeout: installProxyTimeout,
        install_download_limit_speed: installDownloadLimitSpeed,
        parallel_install_number: parallelInstallNumber,
        node_man_log_level: nodeManLogLevel
      })
      if (res.result) {
        this.$bkMessage({
          theme: 'success',
          message: this.$t('保存配置成功')
        })
      }
      this.submitLoading = false
    },
    handleApplyPermission() {
      bus.$emit('show-permission-modal', { apply_info: [{ action: 'globe_task_config' }] })
    }
  }
}
</script>

<style lang="postcss" scoped>
  .task-config-wrapper {
    min-height: calc(100vh - 142px);
    &.permission-disabled {
      display: flex;
    }
    .task-config-container {
      margin-top: 24px;
      display: flex; /** 为了处理form验证后自定义tooltip不生效问题 */
      padding-bottom: 40px;
    }
    .task-config-form {
      width: 525px;
    }
    /deep/ .bk-form-control {
      width: 315px;
    }
    .bk-form-info-item {
      font-size: 0;
      .group-text {
        padding: 0;
        width: 31px;
        text-align: center;
      }
    }
    .bk-form-info-item + .bk-form-info-item {
      margin-top: 20px;
    }
    .info-tooltips {
      position: absolute;
      top: 0;
      left: 100%;
      height: 100%;
    }
    .info-tooltips-icon {
      margin: 7px 0 0 10px;
      font-size: 16px;
      color: #c4c6cc;
    }
    .log-level-select {
      width: 315px;
      background: #fff;
    }
  }
  .info-tooltips-content {
    max-width: 370px;
    color: #63656e;
  }
</style>

<template>
  <div class="bk-plugin-operation">
    <div class="bk-operat-nav">
      <bk-tab ext-cls="bk-plugin-tab" :active.sync="tabActive" type="unborder-card" @tab-change="changeNav">
        <bk-tab-panel
          v-for="(panel, index) in navBar"
          v-bind="panel"
          :key="index">
        </bk-tab-panel>
      </bk-tab>
    </div>
    <!-- 进程管理 -->
    <div class="bk-operat-process" v-if="tabActive === 'manager'">
      <div class="bk-process-info">
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('选择操作') }}：</span>
          </div>
          <div class="bk-operation-right">
            <div class="bk-button-group">
              <bk-button v-for="(item, index) in process.operationList"
                         :key="index"
                         ext-cls="plugin-btn"
                         :class="item.complete ? 'is-selected' : ''"
                         @click="changeOperation(item, index)">
                {{ item.name }}
              </bk-button>
            </div>
          </div>
        </div>
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('插件类型') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="process.pluginTypeSelected"
              :clearable="false"
              @change="changePluginType">
              <bk-option
                v-for="item in process.pluginTypeList"
                :key="item.id"
                :id="item.id"
                :name="item.name">
              </bk-option>
            </bk-select>
          </div>
        </div>
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('选择插件') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="process.plugInfo.name"
              searchable
              :clearable="false"
              @change="changePlugin">
              <bk-option
                v-for="item in process.pluginList"
                :key="item.id"
                :id="item.name"
                :name="item.name"
                :disabled="item.disabled">
              </bk-option>
            </bk-select>
            <div class="bk-right-info" v-if="process.plugInfo.name">
              <span class="bk-info-icon">!</span>
              <span>
                <span style="margin-right: 14px">{{process.plugInfo.name}}</span>{{process.plugInfo.details}}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 插件更新 -->
    <div class="bk-operat-process" v-if="tabActive === 'update'">
      <div class="bk-process-info">
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('选择要变更的服务') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="pluginUpload.serviceSelected"
              :disabled="pluginUpload.serviceDisabled">
              <bk-option
                v-for="item in pluginUpload.serviceList"
                :key="item.id"
                :id="item.id"
                :name="item.name">
              </bk-option>
            </bk-select>
          </div>
        </div>
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('插件类型') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="process.pluginTypeSelected"
              :clearable="false"
              @change="changePluginType">
              <bk-option
                v-for="item in process.pluginTypeList"
                :id="item.id"
                :key="item.id"
                :name="item.name">
              </bk-option>
            </bk-select>
          </div>
        </div>
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('选择要更新的插件') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="process.plugInfo.name"
              searchable
              :clearable="false"
              @selected="changePlugin">
              <bk-option
                v-for="item in process.pluginList"
                :key="item.id"
                :id="item.name"
                :name="item.name"
                :disabled="item.disabled">
              </bk-option>
            </bk-select>
            <div class="bk-right-info" v-if="process.plugInfo.name">
              <span class="bk-info-icon">!</span>
              <span>
                <span style="margin-right: 14px">{{process.plugInfo.name}}</span>{{process.plugInfo.details}}
              </span>
            </div>
          </div>
        </div>
        <div class="bk-process-operation clearfix-none">
          <div class="bk-operation-left">
            <span>{{ $t('选择新包') }}：</span>
          </div>
          <div class="bk-operation-right">
            <bk-select
              v-model="pluginUpload.packageSelected"
              :clearable="false"
              :loading="loadingPackage"
              @change="changePackage">
              <bk-option
                v-for="item in pluginUpload.newPackageList"
                :key="item.id"
                :id="item.id"
                :name="item.name">
              </bk-option>
            </bk-select>
            <!-- <div class="bk-package-prompt">
                <p></p>
                <p>{{ $t('请联系运维') }}：</p>
                <p>{{ $t('将插件包上传到中控机的/data/src/目录并解压') }}</p>
                <p>{{ $t('然后执行./bkeec(或bkcec) pack gse_plugin 更新插件信息到/data/src下') }}</p>
                <span class="bk-prompt-square"></span>
            </div> -->
            <div class="bk-right-info" v-if="pluginUpload.packageSelected !== ''">
              <span class="bk-info-icon">!</span>
              <span>
                <span>
                  M D 5 {{ $t('值') }}:<span style="margin-left: 10px">{{pluginUpload.packageInfo.mdFive}}</span>
                </span>
                <br />
                <span>
                  <!-- eslint-disable-next-line vue/no-v-html -->
                  {{ $t('更新时间') }}:<span style="margin-left: 10px" v-html="pluginUpload.packageInfo.uploadTime"></span>
                </span>
              </span>
            </div>
            <div class="bk-right-checkbox">
              <form class="bk-form">
                <div class="bk-form-item">
                  <div
                    class="bk-form-content"
                    style="margin-left: 0px;"
                    v-for="(node, index) in pluginUpload.packageCheckList"
                    :key="index">
                    <label
                      :class="['bk-form-checkbox', { 'is-checked': node.checkStatus }]"
                      @click="checkPackage(node, index)">
                      <span class="bk-checkbox"></span>
                      <input type="hidden" name="checkPackage" :checked="node.checkStatus">
                      <span class="bk-checkbox-text">{{node.name}}</span>
                    </label>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 文件预览 -->
    <div class="bk-shade" v-if="fileInfo.showStatus">
      <div class="bk-file-more">
        <div class="bk-head">
          <span>{{ $t('文件预览') }}</span>
          <span class="bk-head-close" @click="closeFile"><i class="bk-icon icon-close"></i></span>
        </div>
        <div class="bk-content">
          <ul>
            <li v-for="(item, index) in fileInfo.list" :key="index">
              <span>{{item.name}}</span>
            </li>
          </ul>
        </div>
        <div class="bk-file-btn">
          <bk-button type="default" @click="closeFile">
            {{ $t('关闭') }}
          </bk-button>
        </div>
      </div>
    </div>
    <div class="bk-process-btn mt30">
      <bk-button theme="default" @click="stepHandle(1)" :disabled="secondClick">
        {{ $t('上一步') }}
      </bk-button>
      <span style="margin-left: 20px"></span>
      <bk-button theme="primary" @click="clickNext" :loading="secondClick">
        {{ $t('立即执行') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
// import Tips from '@/components/tips/tips.vue'
import { mapActions } from 'vuex'
export default {
  // components: {
  //     Tips
  // },
  props: {
    ipInfo: {
      type: Object,
      default() {
        return {
          os_type: '',
          bk_biz_id: [],
          conditions: [],
          isAllChecked: false,
          exclude_hosts: [],
          bk_host_id: []
        }
      },
      validator(info) {
        return info ? info.os_type : false
      }
    }
  },
  data() {
    return {
      secondClick: false,
      tabActive: 'manager',
      navBar: [
        { id: 1, name: 'manager', label: this.$t('进程管理'), complete: true },
        { id: 2, name: 'update', label: this.$t('插件更新'), complete: false }
      ],
      // 进程管理
      process: {
        operationList: [],
        pluginTypeList: [],
        pluginTypeSelected: 1,
        pluginList: [],
        completeCheck: false,
        plugInfo: {
          name: '',
          details: ''
        }
      },
      // 进程参数
      processForm: {
        bk_cloud_id: '',
        node_type: 'AGENT',
        op_type: '',
        global_params: {
          plugin: {}
        },
        hosts: [{ conn_ips: '' }]
      },
      // 插件更新
      plugForm: {
        bk_cloud_id: '',
        node_type: 'AGENT',
        op_type: 'MAIN_INSTALL_PLUGIN',
        global_params: {
          plugin: {},
          package: {},
          control: {},
          option: {
            keep_config: 0,
            no_restart: 0,
            no_delegate: 0
          },
          upgrade_type: 'APPEND'
        },
        hosts: [{ conn_ips: '' }]
      },
      // 插件更新
      pluginUpload: {
        serviceList: [
          { id: 1, name: `GSE ${this.$t('插件')}` }
        ],
        serviceSelected: 1,
        serviceDisabled: true,
        // 选择新包
        newPackageList: [],
        packageSelected: 0,
        packageInfo: {
          mdFive: '',
          uploadTime: ''
        },
        packageCheckList: [
          { id: 1, name: this.$t('保留原有配置文件'), checkStatus: false },
          { id: 2, name: this.$t('仅更新文件，不重启进程'), checkStatus: false }
        ],
        // 更新类型
        uploadTypeList: [
          { id: 1, name: this.$t('增量更新(仅覆盖)'), type: 'APPEND' },
          { id: 2, name: this.$t('覆盖更新(先删除原目录后覆盖)'), type: 'OVERRIDE' }
        ],
        uploadTypeSelected: 1
      },
      // 配置更新
      configuUpload: {
        fileFormat: [
          { id: 1, name: 'yaml', checkStatus: true },
          { id: 2, name: 'json', checkStatus: false },
          { id: 3, name: 'ini', checkStatus: false }
        ]
      },
      // 文件预览
      fileInfo: {
        showStatus: false,
        list: []
      },
      loadingPackage: false
    }
  },
  created() {
    this.getOperatList()
    this.getPlufList()
  },
  methods: {
    ...mapActions('plugin', ['getProcessList', 'listPackage', 'operatePlugin']),
    // 获取操作列表数据
    getOperatList() {
      this.process.operationList = [
        { id: 'MAIN_START_PLUGIN', name: this.$t('启动') },
        { id: 'MAIN_STOP_PLUGIN', name: this.$t('停止') },
        { id: 'MAIN_RESTART_PLUGIN', name: this.$t('重启') },
        { id: 'MAIN_RELOAD_PLUGIN', name: this.$t('重载') },
        { id: 'MAIN_DELEGATE_PLUGIN', name: this.$t('托管') },
        { id: 'MAIN_UNDELEGATE_PLUGIN', name: this.$t('取消托管') }
      ]
      this.process.operationList.forEach((item) => {
        item.complete = false
      })
    },
    // 获取插件分类
    getPlufList() {
      this.process.pluginTypeList = []
      const res = [
        { id: 'official', name: this.$t('官方插件') },
        { id: 'external', name: this.$t('第三方插件') },
        { id: 'scripts', name: this.$t('脚本插件') }
      ]
      for (let i = 0; i < res.length; i++) {
        this.process.pluginTypeList.push({
          id: i + 1,
          name: res[i].name,
          info: res[i].id
        })
      }
      if (!this.process.pluginTypeList.length) {
        return
      }
      const value = this.process.pluginTypeList[0].info
      this.getPlugInfo(value)
    },
    // 按分类获取插件列表
    async getPlugInfo(value) {
      const data = await this.getProcessList(value)
      this.process.pluginList = data
      if (data.length) {
        const firstItem = data[0]
        this.changePlugin(firstItem.name)
      } else {
        this.changePlugin('')
      }
    },
    // 按插件获取包
    async getPackageList(value) {
      this.loadingPackage = true
      const info = this.ipInfo.os_type
      const data = await this.listPackage({
        pk: value,
        data: {
          os: info
        }
      })
      this.pluginUpload.newPackageList = data
      this.pluginUpload.newPackageList.forEach((item) => {
        item.name = item.pkg_name
      })
      this.pluginUpload.packageInfo.mdFive = ''
      this.pluginUpload.packageInfo.uploadTime = ''
      this.loadingPackage = false
    },
    // 选择导航类型
    changeNav(name) {
      const index = this.navBar.findIndex(item => item.name === name)
      this.navBar.forEach((item) => {
        item.complete = false
      })
      this.navBar[index].complete = true
      if (index === 1) {
        this.pluginUpload.newPackageList = []
        this.pluginUpload.packageSelected = 0
      }
      this.clearInfo()
    },
    clearInfo() {
      this.processForm = {
        bk_cloud_id: '',
        node_type: 'AGENT',
        op_type: '',
        global_params: {
          plugin: {}
        },
        hosts: [{ conn_ips: '' }]
      }
      this.plugForm = {
        bk_cloud_id: '',
        node_type: 'AGENT',
        op_type: 'MAIN_INSTALL_PLUGIN',
        global_params: {
          plugin: {},
          package: {},
          control: {},
          option: {
            keep_config: 0,
            no_restart: 0,
            no_delegate: 0
          },
          upgrade_type: 'APPEND'
        },
        hosts: [{ conn_ips: '' }]
      }
      this.pluginUpload.packageCheckList.forEach((item) => {
        item.checkStatus = false
      })
      this.pluginUpload.uploadTypeSelected = 1
      this.process.plugInfo.name = ''
      this.process.plugInfo.details = ''
    },
    // 进程管理
    // 选择操作
    changeOperation(item, index) {
      this.process.operationList.forEach((item, i) => {
        item.complete = index === i
      })
      this.process.operationList[index].complete = true
      this.processForm.op_type = item.id
      this.process.operationList = JSON.parse(JSON.stringify(this.process.operationList))
    },
    // 插件类型
    changePluginType(id) {
      const data = this.process.pluginTypeList.find(item => item.id === id)
      const value = data.info
      this.getPlugInfo(value)
      // 清空插件信息
      this.processForm.global_params.plugin = {}
      this.pluginUpload.packageSelected = ''
      this.pluginUpload.newPackageList = []
    },
    // 选择插件
    changePlugin(val) {
      const item = this.process.pluginList.find(item => item.name === val)
      if (!item) {
        this.process.plugInfo.name = ''
        this.process.plugInfo.details = ''
        return
      }
      this.process.pluginList.forEach((item) => {
        item.complete = false
      })
      this.process.plugInfo.name = item.name
      this.process.plugInfo.details = this.$i18n.locale === 'en' ? item.scenario_en : item.scenario
      // 插件信息
      this.processForm.global_params.plugin = item

      if (this.navBar[1].complete) {
        // 重置新包选项
        this.pluginUpload.packageSelected = ''
        this.pluginUpload.newPackageList = []

        const value = item.name
        this.getPackageList(value)
        // this.getRoadInfo(value)
      }
    },
    // 插件更新
    // 选择新包
    changePackage(id) {
      const data = this.pluginUpload.newPackageList.find(item => item.id === id)
      if (!data) return
      this.pluginUpload.packageInfo.mdFive = data.md5
      this.pluginUpload.packageInfo.uploadTime = data.pkg_mtime

      this.plugForm.global_params.package = data
    },
    // 选择包文件配置
    checkPackage(node) {
      node.checkStatus = !node.checkStatus
      this.pluginUpload.packageCheckList = JSON.parse(JSON.stringify(this.pluginUpload.packageCheckList))
    },
    // 参数校验
    checkProcessInfo() {
      let msg = this.$t('请选择操作')
      msg = this.processForm.op_type && this.processForm.global_params.plugin.id ? '' :  this.$t('请选择插件')
      if (msg) {
        this.$bkMessage({
          message: msg,
          theme: 'error'
        })
      }
      return !!msg
    },
    // 进程管理操作
    processManage() {
      if (this.secondClick) {
        return
      }
      const params = {
        job_type: this.processForm.op_type,
        plugin_params: {
          name: this.processForm.global_params.plugin.name
        },
        bk_biz_id: this.ipInfo.bk_biz_id
      }
      if (this.ipInfo.isAllChecked) {
        params.conditions = this.ipInfo.conditions
        params.exclude_hosts = this.ipInfo.exclude_hosts
      } else {
        params.bk_host_id = this.ipInfo.bk_host_id
      }
      this.uploadAjax(params)
    },
    // 参数校验
    checkPlugInfo() {
      let msg = this.$t('请选择插件')
      if (this.processForm.global_params.plugin.id) {
        if (this.pluginUpload.packageSelected !== '') {
          msg = this.pluginUpload.uploadTypeSelected !== '' ? '' : this.$t('请选择更新类型')
        } else {
          msg = this.$t('请选择新包')
        }
      }
      if (msg) {
        this.$bkMessage({
          message: msg,
          theme: 'error'
        })
      }
      return !!msg
    },
    // 插件更新
    plugUploadInfo() {
      if (this.secondClick) {
        return
      }
      this.secondClick = true
      this.plugForm.global_params.option.keep_config = this.pluginUpload.packageCheckList[0].checkStatus ? 1 : 0
      this.plugForm.global_params.option.no_restart = this.pluginUpload.packageCheckList[1].checkStatus ? 1 : 0
      this.plugForm.global_params.option.no_delegate = 0
      const params = {
        job_type: this.plugForm.op_type,
        plugin_params: {
          name: this.processForm.global_params.plugin.name,
          version: this.plugForm.global_params.package.version,
          keep_config: this.plugForm.global_params.option.keep_config,
          no_restart: this.plugForm.global_params.option.no_restart
        },
        bk_biz_id: this.ipInfo.bk_biz_id
      }
      if (this.ipInfo.isAllChecked) {
        params.conditions = this.ipInfo.conditions
        params.exclude_hosts = this.ipInfo.exclude_hosts
      } else {
        params.bk_host_id = this.ipInfo.bk_host_id
      }
      this.uploadAjax(params)
    },
    async uploadAjax(params) {
      this.secondClick = true
      const data = await this.operatePlugin(params)
      if (data ? data.job_id : false) {
        this.$router.push({ name: 'taskDetail', params: { taskId: data.job_id } })
      }
      this.secondClick = false
    },
    // 立即执行
    clickNext() {
      if (this.navBar[0].complete) {
        if (this.checkProcessInfo()) {
          return
        }
        this.processManage()
      }
      if (this.navBar[1].complete) {
        if (this.checkPlugInfo()) {
          return
        }
        this.plugUploadInfo()
      }
    },
    stepHandle(step) {
      this.$emit('stepChange', step)
    },
    // 返回上一步
    backPrevious() {
      this.clearInfo()
      this.$parent.originalTree()
    },
    // 关闭文件预览
    closeFile() {
      this.fileInfo.showStatus = !this.fileInfo.showStatus
    }
  }
}
</script>
<style lang="postcss" scoped>
  .bk-form-checkbox {
    font-size: 14px;
    color: #666;
    margin-right: 30px;
    line-height: 18px;
    display: inline-block;
    padding: 7px 0;
  }
  .bk-form-checkbox.bk-checkbox-small input[type=checkbox] {
    width: 14px;
    height: 14px;
    background-position: 0 -95px;
  }
  .bk-plugin-operation {
    position: relative;
  }
  .bk-plugin-tab {
    padding: 0 35px;
  }
  .plugin-btn {
    width: 120px;
    >>> span {
      width: 88px;
      display: inline-block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }
  .bk-operat-process {  /* 进程管理 */
    position: relative;
    padding: 10px 0px 0 0;
    background-color: #fff;
    .bk-process-info {
      position: relative;
      left: 50%;
      transform: translateX(-50%);
      width: 780px;
    }
    .bk-process-operation {
      line-height: 36px;
      margin-bottom: 20px;
      .bk-operation-right {
        width: 596px;
        font-size: 14px;
        color: #737987;
        float: left;
        position: relative;
        top: 2px;
        ul {
          width: 601px;
          border-left: 1px solid #c3cdd7;
          border-top: 1px solid #c3cdd7;
          li {
            float: left;
            width: 120px;
            border: 1px solid #c3cdd7;
            line-height: 34px;
            border-top: 0;
            border-left: 0;
            text-align: center;
            cursor: pointer;
            text-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
            &.bk-operation-click {
              background-color: #3c96ff;
              color: #fff;
            }
          }
          .bk-operation-disabled {
            background-color: #fafbfd;
            color: #dde4eb;
            border-color: #dde4eb;
            cursor: not-allowed;
          }
        }
        .bk-right-info {
          width: 100%;
          padding: 10px;
          background-color: #ebf4ff;
          margin-top: 30px;
          padding-left: 38px;
          position: relative;
          .bk-info-icon {
            position: absolute;
            top: 20px;
            left: 14px;
            width: 16px;
            height: 16px;
            text-align: center;
            line-height: 16px;
            background-color: #737987;
            color: #fff;
            font-size: 12px;
            font-weight: bold;
            border-radius: 50%;
          }
        }
        .bk-right-none {
          margin-top: 20px;
          height: 56px;
        }
        .bk-right-file {
          position: relative;
          .bk-file-style {
            width: 316px;
            line-height: 34px;
            border: 1px solid #c3cdd7;
            text-align: center;
            background-color: #fff;
            color: #3c96ff;
            cursor: pointer;
            .bk-file-change {
              position: absolute;
              top: 0;
              left: 336px;
              input {
                /* stylelint-disable-next-line declaration-no-important */
                height: 14px !important;
              }
            }
            .bk-file-success {
              position: absolute;
              top: 34px;
              left: 0;
              color: #737987;
              .bk-see-more {
                color: #3c96ff;
                cursor: pointer;
                margin-left: 20px;
              }
              .bk-file-icon {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 1px solid #55df90;
                border-radius: 50%;
                font-size: 12px;
                color: #55df90;
                text-align: center;
                line-height: 15px;
              }
            }
          }
          .bk-file-info {
            position: absolute;
            top: 0;
            left: 0;
            width: 316px;
            height: 36px;
            opacity: 0;
            cursor: pointer;
          }
        }
        .bk-package-prompt {
          position: absolute;
          top: 0;
          right: -245px;
          font-size: 12px;
          color: #fff;
          background-color: #4c4c4c;
          line-height: 20px;
          width: 224px;
          padding: 5px 10px;
          .bk-prompt-square {
            position: absolute;
            top: 13px;
            left: -5px;
            width: 10px;
            height: 10px;
            background-color: #4c4c4c;
            transform: rotate(45deg);
          }
        }
      }
      .bk-operation-left {
        width: 140px;
        font-size: 14px;
        color: #737987;
        float: left;
        text-align: right;
        padding-right: 10px;
        white-space: nowrap;
      }
    }
  }
  .bk-process-btn {
    text-align: center;
    button {
      min-width: 100px;
    }
  }
  .bk-shade {/* 弹窗 */
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    display: table-cell;
    height: 100%;
    width: 100%;
    z-index: 2001;
    background-color: rgba(75, 75, 75, .5);
  }
  .bk-file-more {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 740px;
    height: 780px;
    box-shadow: 0 0 7px 3px rgba(0, 0, 0, .1);
    border-radius: 2px;
    background-color: #fff;
    z-index: 2002;
    padding: 35px;
    .bk-head {
      text-align: center;
      font-size: 20px;
      color: #333;
      margin-bottom: 20px;
      position: relative;
      .bk-head-close {
        position: absolute;
        top: -18px;
        right: -18px;
        width: 24px;
        height: 24px;
        font-size: 14px;
        text-align: center;
        line-height: 14px;
        padding: 5px;
        color: #737987;
        cursor: pointer;
        &:hover {
          background-color: #333;
          color: #fff;
          border-radius: 50%;
        }
      }
    }
    .bk-content {
      border: 1px solid #c3cdd7;
      height: 630px;
      overflow: auto;
      padding: 16px 24px;
      line-height: 26px;
      font-size: 12px;
      color: #737987;
    }
    .bk-file-btn {
      text-align: center;
      margin-top: 20px;
      button {
        width: 110px;
        height: 36px;
      }
    }
  }
  .clearfix-none::after {
    display: block;
    clear: both;
    content: "";
    font-size: 0;
    visibility: hidden;
  }
</style>

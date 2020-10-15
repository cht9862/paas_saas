<template>
  <div class="parser-excel">
    <div class="parser-excel-file">
      <div class="file-wrapper"
           :class="{ hover: isHover }"
           v-show="status === 'import'"
           @mouseenter="handleMouseEnter"
           @mouseleave="handleMouseLeave">
        <i class="upload-icon nodeman-icon nc-upload-cloud"></i>
        <i18n path="将文件拖到此处或" class="mt5">
          <span class="upload-btn">{{ $t('点击上传') }}</span>
        </i18n>
        <input
          ref="upload"
          @change="handleFileChange"
          :accept="accept"
          :multiple="false"
          title=""
          type="file"
          class="file-input">
      </div>
      <div
        v-show="status === 'parsing'"
        class="file-uploading"
        :class="{ 'error': file.status === 'error', 'loading': isLoading }"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave">
        <i class="abort-icon nodeman-icon nc-delete" @click="handleAbortParse" v-show="showAbort && isLoading"></i>
        <i class="uploading-icon nodeman-icon nc-excel"></i>
        <div class="uploading-file ml10">
          <div class="file-left">
            <div class="file-info">
              <span>{{ file.name }}</span>
              <span v-if="file.status === 'loading'">{{ `${file.progress} %` }}</span>
            </div>
            <div class="file-loading">
              <div class="progress" v-if="file.status === 'loading'">
                <div class="progress-bar" :style="{ width: `${file.progress}%` }"></div>
              </div>
              <div class="parsing-success" v-else-if="file.status === 'success'">
                <i class="nodeman-icon nc-check-small"></i>
                {{ $t('上传成功') }}
              </div>
              <div class="parsing-error" v-else-if="file.status === 'error'">
                {{ file.msg }}
              </div>
            </div>
          </div>
          <div class="file-right" v-show="['success', 'error'].includes(file.status)">
            <span v-if="file.status === 'success'" class="file-size">{{ file.size | fileSizeFormat }}</span>
            <span class="error" v-else>
              <i class="error-retry nodeman-icon nc-retry" @click="handleRetry"></i>
              <i class="error-delete nodeman-icon nc-delete" @click="handleDelete"></i>
            </span>
          </div>
        </div>
      </div>
    </div>
    <div class="parser-excel-tips">
      <i18n path="仅支持xlsx格式的文件下载">
        <span class="tips-btn" @click="handleDownload">{{ $t('模板文件') }}</span>
      </i18n>
    </div>
  </div>
</template>
<script>
import { tableConfig } from '../config/importTableConfig'
import { authentication } from '@/config/config'
import { mapGetters } from 'vuex'
import { isEmpty } from '@/common/util'

export default {
  name: 'parser-excel',
  filters: {
    fileSizeFormat(v) {
      const SIZE_1KB = 1024
      const SIZE_MB = v / (SIZE_1KB ** 2)
      return `${SIZE_MB.toFixed(2)} M`
    }
  },
  props: {
    accept: {
      type: String,
      default: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
  },
  data() {
    return {
      // 导入状态 import--导入  parsing--解析
      status: 'import',
      // 文件最大值MB
      maxFileSize: 20,
      // 文件信息
      file: {},
      // 解析数据
      data: {},
      showAbort: false,
      // 可选列
      optional: [
        'auth_type',
        'bk_biz_id',
        'bk_cloud_id',
        'ap_id',
        'login_ip',
        'peer_exchange_switch_for_agent',
        'bt_speed_limit'
      ],
      isHover: false,
      // 额外参数
      extraParams: [
        {
          prop: 'outer_ip',
          label: `${this.$t('外网IP')}${this.$t('可选')}`,
          regx: '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$'
        }
      ]
    }
  },
  computed: {
    ...mapGetters(['bkBizList']),
    ...mapGetters('agent', ['apList', 'cloudList']),
    // 当前是否处于解析中的状态
    isLoading() {
      return !['success', 'error'].includes(this.file.status) && this.status === 'parsing'
    }
  },
  watch: {
    value(v) {
      if (!v) {
        this.file = {}
        this.status = 'import'
        this.$refs.upload.value = ''
      }
    }
  },
  methods: {
    validateFile(file) {
      const result = {
        success: true,
        message: ''
      }
      if (file.size > this.maxFileSize * 1024 * 1024) {
        result.success = false
        result.message = this.$t('文件不能超过', { size: this.maxFileSize })
      } else if (file.type !== this.accept) {
        result.success = false
        result.message = this.$t('只支持“xlsx”格式的文件')
      }
      if (!result.success) {
        this.$refs.upload.value = ''
        this.$bkMessage({
          theme: 'error',
          message: result.message
        })
      }
      return result.success
    },
    /**
     * 导入文件
     */
    async handleFileChange(e) {
      const { files } = e.target
      if (!files.length) return
      const [file] = files
      const validate = this.validateFile(file)
      if (!validate) return
      this.file = this.getFileInfo(file)
      await this.parseFile(file)
    },
    /**
     * 解析文件
     */
    async parseFile(file) {
      this.$emit('uploading', true, [])
      this.status = 'parsing'
      const fileReader = new FileReader()
      fileReader.onload = (ev) => {
        try {
          const data = ev.target.result
          import('xlsx').then((XLSX) => {
            const workbook = XLSX.read(data, { type: 'binary' })
            const sheets = Object.keys(workbook.Sheets)
            const sheetData = XLSX.utils.sheet_to_json(workbook.Sheets[sheets[0]])

            const validator = this.validateExcelData(sheetData)
            if (validator.status === 'ok') {
              const parseData = this.getImportData(sheetData)
              this.$emit('uploading', false, parseData)
              setTimeout(() => {
                this.file.status = 'success'
              }, 200)
            } else {
              this.$emit('uploading', false)
              setTimeout(() => {
                this.file.msg = validator.msg
                this.file.status = 'error'
              }, 200)
            }
          })
        } catch (_) {
          this.$emit('uploading', false)
          setTimeout(() => {
            this.file.msg = this.$t('解析文件失败')
            this.file.status = 'error'
          }, 200)
        }
      }
      fileReader.onprogress = (ev) => {
        this.file.progress = parseInt((ev.loaded / ev.total) * 100, 10)
      }
      fileReader.readAsBinaryString(file)
    },
    /**
             * 验证excel数据
             * @param {Array} sheetsData excel json数据
             */
    validateExcelData(sheetsData) {
      const validator = {
        status: 'ok',
        msg: ''
      }
      if (sheetsData.length !== 0) {
        // excel表头
        const sheetsHeaders = Object.keys(sheetsData[0])
        // 必有表头字段
        const configHeaders = tableConfig.filter(item => !this.optional.includes(item.prop)).map(item => item.label)

        const firstMissLabel = configHeaders.find(label => !sheetsHeaders.includes(this.$t(label)))
        if (firstMissLabel) { // 第一个未缺失的表头
          validator.status = 'error'
          validator.msg = this.$t('列缺失', { label: firstMissLabel })
        } else {
          validator.status = 'ok'
          validator.msg = ''
        }
      } else {
        validator.status = 'error'
        validator.msg = this.$t('Excel数据为空')
      }
      return validator
    },
    /**
     * 处理Excel导入数据
     * @param {Array} jsonData
     */
    getImportData(jsonData) {
      let parseData = []
      const optional = [
        this.$t('登录IP'),
        this.$t('BT传输加速'),
        this.$t('传输限速')
      ]
      try {
        jsonData.forEach((item) => {
          const info = {}
          // 表格参数
          let isIgnoreProve = false // prove 跳过赋值
          tableConfig.forEach((header) => {
            const key = this.$t(header.label)
            if (key === this.$t('业务')) {
              const data = this.bkBizList.find(data => data.bk_biz_name === item[`${key}${this.$t('可选')}`])
              info[header.prop] = data && !isEmpty(data.bk_biz_id) ? data.bk_biz_id : ''
            } else if (key === this.$t('云区域')) {
              const data = this.cloudList.find(data => data.bk_cloud_name === item[`${key}${this.$t('可选')}`])
              info[header.prop] = data && !isEmpty(data.bk_cloud_id) ? data.bk_cloud_id : ''
            } else if (key === this.$t('接入点')) {
              const data = this.apList.find(data => data.name === item[`${key}${this.$t('可选')}`])
              info[header.prop] = data && !isEmpty(data.id) ? data.id : -1
            } else if (optional.includes(key)) {
              info[header.prop] = !isEmpty(item[`${key}${this.$t('可选')}`]) ? item[`${key}${this.$t('可选')}`] : ''
            } else if (key === this.$t('认证方式')) { // 密钥 || 铁将军 需覆盖填写值
              let val = ''
              if (!isEmpty(item[key])) {
                const verifict = authentication.find(auth => auth.name === item[key])
                if (verifict) {
                  val = verifict.id
                  if (val !== 'PASSWORD') {
                    info.prove = verifict.default || ''
                    isIgnoreProve = true
                  }
                }
              }
              info[header.prop] = val
            } else if (header.prop) {
              if (!isIgnoreProve || header.prop !== 'prove') {
                info[header.prop] = !isEmpty(item[key]) ? item[key] : ''
              }
            }
          })
          // 自定义额外参数
          this.extraParams.forEach((config) => {
            const value = item[config.label]
            const validate = !config.regx || new RegExp(config.regx).test(value)
            if (validate) {
              info[config.prop] = value
            }
          })
          info.is_manual = false // Excel导入默认不为手动安装
          if (Object.keys(info).length) {
            parseData.push(info)
          }
        })
      } catch (_) {
        parseData = []
      }
      return parseData
    },
    /**
     * 组装文件信息
     */
    getFileInfo(file) {
      return {
        name: file.name,
        size: file.size,
        origin: file,
        progress: 0,
        status: 'loading',
        msg: ''
      }
    },
    /**
     * 重试解析错误的文件
     */
    handleRetry() {
      this.file.status = 'loading'
      this.parseFile(this.file.origin)
    },
    /**
     * 删除解析错误的文件
     */
    handleDelete() {
      this.file = {}
      this.$refs.upload.value = ''
      this.status = 'import'
    },
    /**
     * 终止解析文件
     */
    handleAbortParse() {
      this.handleDelete()
    },
    handleMouseEnter() {
      this.isHover = true
      this.showAbort = true
    },
    handleMouseLeave() {
      this.isHover = false
      this.showAbort = false
    },
    /**
     * 下载模板文件
     */
    handleDownload() {
      // 待优化方案，前端传表头与数据给后端，直接产出对应的Excel，但不能包含IP等敏感信息
      const url = `${window.PROJECT_CONFIG.STATIC_URL}download/bk_nodeman_info_${window.language}.xlsx`
      const element = document.createElement('a')
      element.setAttribute('href', url)
      element.setAttribute('download', 'bk_nodeman_info.xlsx')
      element.style.display = 'none'
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

@define-mixin text-btn {
  color: #3a84ff;
  cursor: pointer;
}

.parser-excel {
  width: 480px;
  font-size: 12px;
  &-file {
    .file-wrapper {
      position: relative;
      border: 1px dashed #dcdee5;
      border-radius: 2px;
      background: #fafbfd;
      height: 80px;

      @mixin layout-flex column, center, center;
      &.hover {
        border-color: #3a84ff;
        .upload-icon {
          color: #3a84ff;
        }
      }
      .upload-icon {
        font-size: 24px;
        color: #c4c6cc;
      }
      .upload-btn {
        @mixin text-btn;
      }
      input {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        cursor: pointer;
        opacity: 0;
      }
    }
    .file-uploading {
      position: relative;
      height: 60px;
      border: 1px solid #c4c6cc;
      border-radius: 2px;
      padding: 14px 15px;

      @mixin layout-flex row;
      &.loading {
        &:hover {
          background: #f0f1f5;
        }
      }
      &.error {
        border-color: #ea3636;
        background: rgba(254,221,220,.25);
      }
      .abort-icon {
        position: absolute;
        right: 0;
        top: 0;
        font-size: 24px;
        color: #979ba5;
        border-radius: 50%;
        cursor: pointer;
      }
      .uploading-icon {
        font-size: 32px;
        color: #c4c6cc;
      }
      .uploading-file {
        flex: 1;

        @mixin layout-flex row, center, space-between;
        .file-left {
          flex: 1;
          .file-info {
            @mixin layout-flex row, center, space-between;
          }
          .file-loading {
            .progress {
              margin-top: 7px;
              width: 100%;
              height: 2px;
              background: #dcdee5;
              border-radius: 1px;
              &-bar {
                height: 2px;
                border-radius: 1px;
                background: #3a84ff;
                transition: width .3s ease-in-out;
              }
            }
            .parsing-success {
              color: #2dcb56;
              height: 16px;

              @mixin layout-flex row, center;
              i {
                font-size: 24px;
                margin-left: -6px;
              }
            }
            .parsing-error {
              color: #ea3636;
            }
          }
        }
        .file-right {
          .file-size {
            font-weight: bold;
          }
          .error {
            color: #ea3636;
            cursor: pointer;

            @mixin layout-flex row, center, center;
            &-retry {
              margin: 0 6px 2px 0;
            }
            &-delete {
              font-size: 24px;
            }
          }
        }
      }
    }
  }
  &-tips {
    margin-top: 8px;
    text-align: center;
    .tips-btn {
      margin-left: 3px;

      @mixin text-btn;
    }
  }
}
</style>

<template>
  <div class="upload">
    <div v-if="!Object.keys(file).length" class="upload-wrapper">
      <bk-button ext-cls="upload-btn">
        <span class="upload-btn-content">
          <i :class="icon" :style="{ 'font-size': iconSize + 'px' }"></i>
          <span>{{ title }}</span>
        </span>
      </bk-button>
      <input
        ref="uploadel"
        @change="handleChange"
        :accept="accept"
        :multiple="false"
        :name="name"
        title=""
        type="file"
        class="upload-input">
    </div>
    <slot name="uploadInfo" v-bind="{ file, fileChange: handleChange }" v-else>
      <div class="upload-info"
           :class="{ hover: hoverInfo && !disableHoverCls }"
           @mouseenter="handleMouseEnter"
           @mouseleave="handleMouseLeave">
        <div class="info-left">
          <i :class="fileIcon"></i>
        </div>
        <div class="info-right ml5">
          <div class="info-name">
            <span class="file-name" :title="file.name">{{ file.name || 'name' }}</span>
            <span class="file-extension">{{ file.extension || '' }}</span>
            <i class="file-abort nodeman-icon nc-delete" @click="handleAbortUpload" v-show="hoverInfo"></i>
          </div>
          <div class="info-progress" v-show="file.percentage !== '100%'">
            <div class="progress-bar"
                 :class="{ 'fail-background': file.hasError }"
                 :style="{ width: file.percentage || 0 }">
            </div>
          </div>
        </div>
      </div>
    </slot>
  </div>
</template>

<script>
export default {
  name: 'upload',
  model: {
    prop: 'value',
    event: 'change'
  },
  props: {
    value: {
      type: String,
      default: ''
    },
    // 上传至服务器的名称
    name: {
      type: String,
      default: 'file_data'
    },
    // mime类型
    accept: {
      type: String,
      default: ''
    },
    // 接受类型提示信息
    acceptTips: {
      type: String,
      default: ''
    },
    // URL
    action: {
      type: String,
      default: ''
    },
    // 最大文件大小
    maxSize: {
      type: Number,
      default: 500 // 单位M
    },
    unit: {
      type: String,
      default: 'MB',
      validator(v) {
        return ['KB', 'MB'].includes(v)
      }
    },
    // 请求头
    headers: {
      type: [Array, Object]
    },
    withCredentials: {
      type: Boolean,
      default: false
    },
    // 上传失败回调
    onUploadError: {
      type: Function,
      default: () => {}
    },
    // 上传成功回调
    onUploadSuccess: {
      type: Function,
      default: () => {}
    },
    // 上传进度回调
    onUploadProgress: {
      type: Function,
      default: () => {}
    },
    // 上传text图标
    icon: {
      type: String,
      default: 'bk-icon icon-plus'
    },
    fileIcon: {
      type: String,
      default: 'nodeman-icon nc-key'
    },
    iconSize: {
      type: [Number, String],
      default: '22'
    },
    // 上传按钮文字信息
    title: {
      type: String,
      default: window.i18n.t('上传文件')
    },
    // 是否前端解析
    parseText: {
      type: Boolean,
      default: false
    },
    // 禁用文件框悬浮样式
    disableHoverCls: {
      type: Boolean,
      default: false
    },
    // 回显文件信息
    fileInfo: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      file: {}, // 当前文件对象
      reqsMap: {}, // 文件请求Map（用于终止）
      fileIndex: 1, // 文件索引
      hoverInfo: false // 鼠标悬浮状态
    }
  },
  computed: {
    maxFileSize() {
      switch (this.unit) {
        case 'KB':
          return this.maxSize * (2 ** 10)
        case 'MB':
          return this.maxSize * (2 ** 20)
        default:
          return this.maxSize * (2 ** 20)
      }
    }
  },
  watch: {
    fileInfo: {
      handler(v) {
        if (v && Object.keys(v).length) {
          this.file = JSON.parse(JSON.stringify(this.fileInfo))
        }
      },
      immediate: true
    }
  },
  methods: {
    // 文件变更
    handleChange(e) {
      const { files } = e.target
      const [file] = Array.from(files)
      if (this.validateFile(file)) {
        this.file = {}
        this.parseText ? this.handleParseText(file) : this.handleUploadFiles(file)
        this.$refs.uploadel.value = ''
      }
      this.$refs.uploadel.value = ''
    },
    // 组装文件对象，添加额外属性
    handleAssembleFile(file) {
      const ext = file.name.slice((file.name.lastIndexOf('.') - 1 >>> 0) + 1)
      const fileName = file.name.substring(0, file.name.lastIndexOf(ext))
      const uid = this.fileIndex
      this.fileIndex += 1
      return {
        name: fileName,
        type: file.type,
        size: file.size,
        percentage: 0,
        uid: Date.now() + uid,
        originFile: file,
        status: 'uploading',
        hasError: false,
        errorMsg: '',
        extension: ext
      }
    },
    // 校验文件
    validateFile(file) {
      if (!file) return false
      const validate = {
        message: '',
        success: true
      }
      if (file.size > this.maxFileSize) {
        validate.success = false
        validate.message = `文件不能超过 ${this.maxSize} ${this.unit}`
      }
      if (this.accept && !this.accept.split(',').includes(file.type)) {
        validate.success = false
        validate.message = this.acceptTips
      }
      if (!validate.success) {
        this.$bkMessage({
          theme: 'error',
          message: validate.message
        })
      }
      return validate.success
    },
    // 前端解析上传文件
    handleParseText(file) {
      // 修改原file对象的属性
      this.file = this.handleAssembleFile(file)
      const fileReader = new FileReader()
      fileReader.onload = (ev) => {
        try {
          const key = ev.target.result
          this.$emit('change', key, this.file)
          this.onUploadSuccess(key, this.file)
        } catch (e) {
          this.$bkMessage({
            theme: 'error',
            message: e || this.$t('解析文件失败')
          })
          this.file.hasError = true
          this.onUploadError(e, this.file)
        }
      }
      fileReader.onprogress = (ev) => {
        // eslint-disable-next-line radix
        this.file.percentage = `${parseInt((ev.loaded / ev.total) * 100)}%`
      }
      fileReader.readAsText(file)
    },
    // 上传文件
    handleUploadFiles(file) {
      this.$emit('before-upload')
      // 修改原file对象的属性
      this.file = this.handleAssembleFile(file)
      const { originFile, uid } = this.file
      const options = {
        headers: this.headers,
        withCredentials: this.withCredentials,
        file: originFile,
        filename: this.name,
        action: this.action,
        onProgress: (e) => {
          this.handleHttpProgress(e, originFile)
        },
        onSuccess: (res) => {
          this.handleHttpSuccess(res, originFile)
          delete this.reqsMap[uid]
        },
        onError: (err) => {
          this.handleHttpError(err, originFile)
          delete this.reqsMap[uid]
        }
      }
      const req = this.handleHttpRequest(options)
      this.reqsMap[uid] = req
    },
    // 终止文件上传
    handleAbortUpload() {
      if (this.file.uid && this.reqsMap[this.file.uid]) {
        this.reqsMap[this.file.uid].abort()
        delete this.reqsMap[this.file.uid]
      }
      this.file = {}
      this.hoverInfo = false
      this.$emit('change', '', this.file)
    },
    // 发送HTTP请求
    handleHttpRequest(option) {
      if (typeof XMLHttpRequest === 'undefined') return

      const xhr = new XMLHttpRequest()
      if (xhr.upload) {
        xhr.upload.onprogress = (e) => {
          if (e.total > 0) {
            e.percent = Math.round((e.loaded * 100) / e.total)
          }
          option.onProgress(e)
        }
      }

      const formData = new FormData()
      formData.append(option.filename, option.file, option.file.name)
      xhr.onerror = (e) => {
        option.onError(e)
      }

      const { action } = option
      xhr.onload = () => {
        if (xhr.status < 200 || xhr.status >= 300 || !JSON.parse(xhr.response).result) {
          return option.onError(this.onError(action, xhr))
        }
        option.onSuccess(this.onSuccess(xhr))
      }
      xhr.open('post', action, true)

      if ('withCredentials' in xhr) {
        xhr.withCredentials = option.withCredentials
      }
      const { headers } = option
      if (headers) {
        if (Array.isArray(headers)) {
          headers.forEach((head) => {
            const headerKey = head.name
            const headerVal = head.value
            xhr.setRequestHeader(headerKey, headerVal)
          })
        } else {
          const headerKey = headers.name
          const headerVal = headers.value
          xhr.setRequestHeader(headerKey, headerVal)
        }
      }
      xhr.send(formData)
      return xhr
    },
    // 默认失败回调
    onError(action, xhr) {
      let msg
      if (xhr.response) {
        try {
          msg = `${JSON.parse(xhr.response).message || xhr.response}`
        } catch (_) {
          msg = xhr.response
        }
      } else if (xhr.responseText) {
        msg = `${xhr.responseText}`
      } else {
        msg = `fail to post ${action} ${xhr.status}`
      }

      const err = new Error(msg)
      err.status = xhr.status
      err.method = 'post'
      err.url = action
      return err
    },
    // 默认成功回调
    onSuccess(xhr) {
      const text = xhr.responseText || xhr.response
      if (!text) return text

      try {
        return JSON.parse(text)
      } catch (e) {
        return text
      }
    },
    // 获取进度并触发props函数
    handleHttpProgress(e, postFiles) {
      this.file.percentage = `${e.percent}%`
      this.file.status = 'uploading'
      this.onUploadProgress(e, postFiles)
    },
    // 成功处理并触发props函数
    handleHttpSuccess(res, postFiles) {
      this.file.status = 'success'
      this.onUploadSuccess(res, postFiles)
    },
    // 失败处理并触发props函数
    handleHttpError(err, postFiles) {
      this.file.hasError = true
      this.file.errorMsg = err.message
      this.file.status = 'error'
      this.onUploadError(err, postFiles)
    },
    // 鼠标悬浮
    handleMouseEnter() {
      this.hoverInfo = true
    },
    // 鼠标离开
    handleMouseLeave() {
      this.hoverInfo = false
    },
    // 文件上传重试
    handleRetry() {
      if (this.file.originFile) {
        this.handleUploadFiles(this.file.originFile)
      }
    }
  }
}
</script>
<style lang="postcss" scoped>
  @import "@/css/mixins/nodeman.css";

  .upload-wrapper {
    position: relative;
    &:hover {
      button {
        border-color: #979ba5;
        color: #63656e;
      }
    }
    .upload-btn {
      width: 100%;
    }
    .upload-btn-content {
      position: relative;
      left: -2px;

      @mixin layout-flex row, center, center;
      i {
        top: 0;
      }
    }
    .upload-input {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      cursor: pointer;
      opacity: 0;
    }
  }
  .upload-info {
    padding-left: 2px;
    padding-right: 5px;
    height: 32px;

    @mixin layout-flex row, center;
    &.hover {
      background: #f0f1f5;
      border-radius: 2px;
    }
    .info-left {
      font-size: 18px;
      color: #c4c6cc;
    }
    .info-right {
      width: 0;
      flex: 1;
      .info-name {
        position: relative;
        line-height: 16px;

        @mixin layout-flex row;
        .file-name {
          height: 16px;
          word-break: break-all;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .file-extension {
          margin-right: 20px;
        }
        .file-abort {
          position: absolute;
          right: 0;
          font-size: 18px;
          cursor: pointer;
        }
      }
      .info-progress {
        width: 100%;
        height: 2px;
        background: #dcdee5;
        border-radius: 1px;
        .progress-bar {
          height: 2px;
          border-radius: 1px;
          background: #3a84ff;
          transition: width .3s ease-in-out;
        }
      }
    }
  }
</style>

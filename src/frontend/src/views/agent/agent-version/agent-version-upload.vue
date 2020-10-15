<template>
    <div class="agent-version">
        <bk-form :label-width="100" ref="form">
            <bk-form-item :label="$t('MD5')" required>
                <bk-input class="content-basic" :placeholder="$t('请输入')"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('版本包')" required>
                <Upload class="content-basic" :on-upload-error="handleOnUploadError"></Upload>
            </bk-form-item>
        </bk-form>
        <bk-button
            :style="{ marginLeft: `${marginLeft}px` }"
            theme="primary"
            class="nodeman-primary-btn mt30"
            :disabled="disabledUploadBtn"
            @click="handleNext">
            {{ $t('下一步') }}
        </bk-button>
    </div>
</template>
<script>
import Upload from '@/components/upload/upload'
import formLabelMixin from '@/common/form-label-mixin'
export default {
  name: 'agent-version-upload',
  components: {
    Upload
  },
  mixins: [formLabelMixin],
  data() {
    return {
      // 上传按钮禁用状态
      disabledUploadBtn: true,
      isUploading: false,
      dynamicSlotName: 'default',
      file: null,
      marginLeft: 100
    }
  },
  mounted() {
    this.marginLeft = this.initLabelWidth(this.$refs.form)
  },
  methods: {
    handleOnUploadError(res, file) {
      this.disabledUploadBtn = false
      this.file = file
    },
    handleNext() {
      this.$router.push({
        name: 'agentVersionDetail',
        params: {
          name: this.file.name
        }
      })
    }
  }
}
</script>
<style lang="postcss" scoped>
.agent-version {
  .content-basic {
    width: 480px;
  }
}
</style>

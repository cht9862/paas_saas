<template>
  <article class="add-cloud" v-bkloading="{ isLoading: loading }">
    <!--提示-->
    <section class="add-cloud-tips mb20">
      <tips :list="tipsList"></tips>
    </section>
    <!--表单-->
    <section class="add-cloud-form">
      <bk-form :label-width="116" :model="formData" :rules="rules" ref="form">
        <bk-form-item error-display-type="normal" :label="$t('云区域名称')" property="bkCloudName" required>
          <bk-input class="content-basic" :placeholder="$t('请输入')" v-model="formData.bkCloudName"></bk-input>
        </bk-form-item>
        <bk-form-item error-display-type="normal" :label="$t('云服务商')" property="isp" required>
          <bk-select
            class="content-basic"
            :placeholder="$t('请选择')"
            v-model="formData.isp"
            :clearable="false"
            :loading="ispLoading">
            <bk-option v-for="option in ispList"
                       :key="option.isp"
                       :id="option.isp"
                       :name="option.isp_name">
              <img :src="`data:image/svg+xml;base64,${option.isp_icon}`" class="option-icon mr5" v-if="option.isp_icon">
              <span>{{ option.isp_name }}</span>
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item
          error-display-type="normal"
          :ext-cls="apList.length > 1 ? 'content-access' : ''"
          :label="$t('选择接入点')"
          required>
          <div v-if="apList.length > 1">
            <div class="access-content">
              <bk-checkbox
                v-model="formData.apId"
                :true-value="-1"
                @change="handleDefaultApChange">
                {{ $t('自动选择接入点') }}
              </bk-checkbox>
            </div>
            <div class="bk-button-group mt10" v-show="formData.apId !== -1">
              <bk-button
                v-for="item in apList"
                :key="item.id"
                @click="handleChangeAp(item)"
                :class="{ 'is-selected': item.id === formData.apId }">
                {{ item.name }}
              </bk-button>
            </div>
          </div>
          <div v-else>
            <bk-input class="content-basic" :placeholder="$t('请输入')" :value="defaultAp.name" disabled></bk-input>
          </div>
        </bk-form-item>
      </bk-form>
    </section>
    <!--操作按钮-->
    <section class="add-cloud-footer">
      <bk-button theme="primary"
                 :style="{ marginLeft: `${marginLeft}px` }"
                 ext-cls="nodeman-primary-btn"
                 :loading="loadingSubmitBtn"
                 @click="handleSubmit">
        {{ submitBtnText }}
      </bk-button>
      <bk-button class="nodeman-cancel-btn ml5" @click="handleCancel">{{ $t('取消') }}</bk-button>
    </section>
    <bk-dialog
      v-model="dialog.show"
      theme="primary"
      :mask-close="false"
      :show-footer="false">
      <div class="bk-info-box">
        <div class="bk-dialog-type-body">
          <i class="bk-icon bk-dialog-mark bk-dialog-success icon-check-1"></i>
        </div>
        <div class="bk-dialog-type-header has-sub-header">
          <div class="header">{{ $t('创建云区域成功') }}</div>
        </div>
        <div class="bk-dialog-type-sub-header">
          <div class="header">
            <a class="info-dialog-btn" @click="handleCancel">{{ $t('返回列表') }}</a>
            <auth-component
              tag="div"
              class="ml30"
              :auth="{
                permission: !!proxyOperateList.length,
                apply_info: [{ action: 'proxy_operate' }]
              }">
              <template slot-scope="{ disabled }">
                <a class="info-dialog-btn" :disabled="disabled" @click="setupProxy">{{ $t('安装Proxy') }}</a>
              </template>
            </auth-component>
          </div>
        </div>
      </div>
    </bk-dialog>
  </article>
</template>
<script>
import Tips from '@/components/tips/tips.vue'
import { mapGetters, mapMutations, mapActions } from 'vuex'
import formLabelMixin from '@/common/form-label-mixin'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import CloudState from '@/store/modules/cloud'

export default {
  name: 'cloud-manager-add',
  components: {
    Tips
  },
  mixins: [formLabelMixin],
  props: {
    id: {
      type: [Number, String],
      default: 0
    },
    // 操作类型 编辑 or 新增
    type: {
      type: String,
      default: 'add',
      validator(v) {
        return ['add', 'edit'].includes(v)
      }
    }
  },
  data() {
    return {
      tipsList: [
        this.$t('云区域管理提示一')
      ],
      // 表单数据
      formData: {
        bkCloudName: '',
        isp: '',
        apId: -1
      },
      // 表单校验
      rules: {
        bkCloudName: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          },
          {
            message: this.$t('不能超过32个字符'),
            trigger: 'blur',
            validator(v) {
              return v.length <= 32
            }
          },
          {
            message: this.$t('特殊字符限制'),
            trigger: 'blur',
            validator(v) {
              // 仅支持 _ 特殊字符
              const pattern = new RegExp('^[\u4e00-\u9fa5A-Za-z0-9-_]+$')
              return pattern.test(v)
            }
          }
        ],
        isp: [
          {
            required: true,
            message: this.$t('必填项'),
            trigger: 'blur'
          }
        ]
      },
      loading: false,
      // 是否显示下一步加载效果
      loadingSubmitBtn: false,
      apList: [],
      // isp下拉框加载
      ispLoading: false,
      marginLeft: 116,
      dialog: {
        show: false,
        bk_cloud_id: null
      }
    }
  },
  computed: {
    ...mapGetters(['ispList']),
    ...mapGetters('cloud', ['authority']),
    defaultAp() {
      return this.apList.length === 1 ? this.apList[0] : { id: -1, name: this.$t('自动选择接入点') }
    },
    submitBtnText() {
      const textMap = {
        add: this.$t('提交'),
        edit: this.$t('保存')
      }

      return textMap[this.type]
    },
    proxyOperateList() {
      return this.authority.proxy_operate || []
    }
  },
  watch: {
    id: {
      handler() {
        this.handleInit()
      },
      immediate: true
    }
  },
  mounted() {
    this.marginLeft = this.initLabelWidth(this.$refs.form)
  },
  methods: {
    ...mapMutations(['setNavTitle']),
    ...mapActions('cloud', ['updateCloud', 'createCloud', 'getApList', 'getCloudDetail']),
    ...mapActions(['getIspList']),
    async handleInit() {
      this.initFormData()
      const promiseList = []
      promiseList.push(this.handleGetApList())
      if (!this.ispList.length) {
        promiseList.push(this.handleGetIspList())
      }
      if (this.id) {
        this.loading = true
        this.setNavTitle(this.$t('编辑云区域'))
        promiseList.push(this.handleGetCloudDetail())
      }
      await Promise.all(promiseList)
      this.loading = false

      if (this.apList.length === 1) {
        this.formData.apId = this.apList[0].id
      }
    },
    /**
     * 获取云区域详情
     */
    async handleGetCloudDetail() {
      const form = await this.getCloudDetail(this.id)
      this.$set(this, 'formData', Object.assign(this.formData, form))
    },
    /**
     * 获取云服务商
     */
    async handleGetIspList() {
      this.ispLoading = true
      await this.getIspList()
      this.ispLoading = false
    },
    /**
     * 获取接入点信息
     */
    async handleGetApList() {
      this.apList = await this.getApList()
    },
    /**
     * 初始化表单
     */
    initFormData() {
      this.formData = {
        bkCloudName: '',
        isp: '',
        apId: -1
      }
    },
    /**
     * 接入点选择事件
     * @param {Object} item
     */
    handleChangeAp(item) {
      this.formData.apId = item.id
    },
    /**
     * 提交
     */
    handleSubmit() {
      this.$refs.form.validate().then(async () => {
        this.loadingSubmitBtn = true
        let data = null
        if (this.type === 'add') {
          data = await this.handleCreateCloud()
        } else {
          data = await this.handleUpdateCloud()
        }
        this.loadingSubmitBtn = false
        if (!data) return

        if (this.type === 'add') {
          this.handleCreateSuccess(data)
        } else {
          this.handleEditSuccess()
        }
      })
    },
    /**
     * 编辑成功后处理逻辑
     */
    handleEditSuccess() {
      this.$bkMessage({ theme: 'success', message: this.$t('编辑成功') })
      this.handleCancel()
    },
    /**
     * 创建成功后处理逻辑
     */
    handleCreateSuccess(data) {
      this.dialog.show = true
      this.dialog.bk_cloud_id = data.bk_cloud_id
    },
    /**
     * 创建云区域
     */
    async handleCreateCloud() {
      const data = await this.createCloud({
        bk_cloud_name: this.formData.bkCloudName,
        isp: this.formData.isp,
        ap_id: this.formData.apId
      })
      return data
    },
    /**
     * 编辑云区域
     */
    async handleUpdateCloud() {
      const data = await this.updateCloud({
        pk: this.id,
        params: {
          bk_cloud_name: this.formData.bkCloudName,
          isp: this.formData.isp,
          ap_id: this.formData.apId
        }
      })
      return data
    },
    /**
     * 取消
     */
    handleCancel() {
      this.$router.push({ name: 'cloudManager' })
    },
    /**
     * 默认接入点变更
     */
    handleDefaultApChange(value) {
      if (!value && !this.formData.apId && this.apList.length) {
        this.formData.apId = this.apList[0].id
      }
    },
    setupProxy() {
      this.dialog.show = false
      this.$router.replace({
        name: 'setupCloudManager',
        params: {
          id: this.dialog.bk_cloud_id || this.id,
          type: 'create'
        }
      })
    }
  }
}
</script>
<style lang="postcss" scoped>
@import "@/css/mixins/nodeman.css";

>>> .tooltips-icon {
  /* stylelint-disable-next-line declaration-no-important */
  right: 10px !important;
}
.option-icon {
  height: 20px;
  position: relative;
  top: 5px;
}
.add-cloud-form {
  .content-basic {
    width: 480px;
  }
  .content-access {
    margin-top: 15px;
  }
}
.add-cloud-footer {
  margin-top: 30px;
}
.info-dialog-btn {
  text-decoration: none;
  cursor: pointer;
  color: #3a84ff;
  &[disabled] {
    color: #c4c6cc;
  }
}
</style>

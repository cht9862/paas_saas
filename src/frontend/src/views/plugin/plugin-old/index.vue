<template>
  <div class="plugin-wrapper">
    <div class="plugin-title">
      <bk-steps ext-cls="plugin-step" :cur-step.sync="curStep" :steps="objectSteps"></bk-steps>
      <!-- <bk-steps ext-cls="plugin-step" direction="vertical" :cur-step.sync="curStep" :steps="objectSteps"></bk-steps> -->
    </div>
    <div class="plugin-content">
      <StepSelectHost
        class="plugin-steps"
        v-if="curStep === 1"
        @stepChange="stepHandle"
        @paramsChange="paramsChange">
      </StepSelectHost>
      <!-- 第二步 -->
      <StepPluginOperation
        class="plugin-steps"
        v-if="curStep === 2"
        :ip-info="ipInfo"
        @stepChange="stepHandle">
      </StepPluginOperation>
      <!-- 日志弹框 -->
      <bk-sideslider :is-show.sync="cmdbSettings.isShow" :title="cmdbSettings.title" :width="553" :quick-close="true">
        <div class="p20 bk-open-window" slot="content">
          <!-- 详细安装步骤 -->
          <div class="bk-install-step" id="bkStep">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="bk-step-info" v-html="cmdbSettings.info"></div>
          </div>
        </div>
      </bk-sideslider>
    </div>
  </div>
</template>

<script>
import StepPluginOperation from './step-plugin-operation.vue'
import StepSelectHost from './step-select-host.vue'

export default {
  name: 'plugin-index',
  components: {
    StepSelectHost,
    StepPluginOperation
  },
  data() {
    return {
      curStep: 1,
      objectSteps: [ // 步骤
        { title: this.$t('选择主机'), icon: 1 },
        { title: this.$t('选择操作类型'), icon: 2 }
      ],
      ipInfo: {}, // 第一步回填的参数

      /*
        * old
        */
      // 节点日志信息
      cmdbSettings: {
        isShow: false,
        title: this.$t('精确'),
        info: '123'
      },
      stepInterval: '',
      logId: ''
    }
  },
  methods: {
    stepHandle(step) {
      this.curStep = step || this.curStep + 1
    },
    paramsChange(params) {
      this.ipInfo = params
    },
    /**
             * old
             */
    // 显示运行节点日志弹框
    showSlider(item) {
      this.cmdbSettings.isShow = !this.cmdbSettings.isShow
      const { appId } = this
      const { id } = item
      this.logId = id
      this.$store.dispatch('stall/getStepInfo', { appId, id }).then((res) => {
        this.cmdbSettings.info = res.data.logs
      }, (res) => {
        this.cmdbSettings.info = res.data.msg
      })
      this.logSetInterval()
    },
    logSetInterval() {
      const { appId } = this
      const id = this.logId
      this.stepInterval = setInterval(() => {
        this.$store.dispatch('stall/getStepInfo', { appId, id }).then((res) => {
          this.cmdbSettings.info = res.data.logs
          const [dom] = document.getElementsByClassName('bk-sideslider-wrapper')
          dom.scrollTop = document.getElementsByClassName('bk-open-window')[0].offsetHeight
          if (res.data.status === 'FAILED' || res.data.status === 'SUCCESS' || !this.cmdbSettings.isShow) {
            clearInterval(this.stepInterval)
          }
        }, () => {
          clearInterval(this.stepInterval)
        })
      }, 2000)
    }
  }
}
</script>
<style lang="postcss" scoped>

  .plugin-wrapper {
    position: relative;
    height: calc(100vh - 52px);
    background: #fff;
    overflow: hidden;
  }
  .plugin-title {
    position: absolute;
    top: 0;
    left: 0;
    padding: 18px 0;
    width: 100%;
    height: 60px;
    border-bottom: 1px solid #dde4eb;
    background: #fff;
    z-index: 20;
    .plugin-step {
      margin: 0 auto;
      max-width: 800px;
    }
  }
  .plugin-content {
    /* display: flex; */
    padding-top: 60px;
    height: 100%;
    overflow: auto;
  }
  .plugin-steps {
    padding-bottom: 25px;
    width: 100%;
    height: 100%;
    overflow: auto;
  }
</style>

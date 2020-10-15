<template>
  <div class="gse-config-wrapper" v-bkloading="{ isLoading: loading }">
    <section class="process-wrapper" v-if="!loading">
      <StepHost
        v-if="curStep === 1"
        :point-id="pointId"
        :step-check="stepCheck"
        :is-edit="isEdit"
        @change="checkedChange"
        @step="stepChange">
      </StepHost>
      <StepInfo
        v-if="curStep === 2"
        :point-id="pointId"
        :is-edit="isEdit"
        @step="stepChange">
      </StepInfo>
    </section>
  </div>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex'
import StepHost from './step-host'
import StepInfo from './step-info'
import { isEmpty } from '@/common/util'

export default {
  name: 'AccessPoint',
  components: {
    StepHost,
    StepInfo
  },
  props: {
    pointId: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      curStep: 1,
      stepCheck: false // 第一步操作是否成功
    }
  },
  computed: {
    ...mapGetters('config', ['detail', 'loading']),
    isEdit() {
      return !isEmpty(this.pointId)
    }
  },
  async mounted() {
    if (this.isEdit) {
      this.stepCheck = true // 编辑时默认连通性检测通过
      await this.getGseDetail({ pointId: this.pointId })
    } else {
      this.$nextTick(() => {
        this.updataLoading(false)
      })
    }
  },
  beforeRouteLeave(to, from, next) {
    this.setToggleDefaultContent() // 带返回的路由背景置为白色
    next()
  },
  methods: {
    ...mapMutations(['setToggleDefaultContent']),
    ...mapMutations('config', ['updataLoading', 'updateDetail']),
    ...mapActions('config', ['getGseDetail']),
    checkedChange(isChecked) {
      this.stepCheck = !!isChecked
    },
    stepChange(stepNum) {
      this.curStep = stepNum || this.curStep + 1
    }
  }
}
</script>

<style lang="postcss">
    .gse-config-wrapper {
      min-height: calc(100vh - 142px);
      padding: 0 0 40px 0;
      .gse-config-container {
        margin-top: 24px;
      }
    }
</style>

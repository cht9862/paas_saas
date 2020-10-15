import { Vue, Component, Watch } from 'vue-property-decorator'

@Component
class NodemanVue extends Vue {
  public handlePollData!: Function
}

@Component
export default class PollMixin extends NodemanVue {
  public runingQueue = []
  public timer: any = null
  public interval = 5000

  // eslint-disable-next-line new-cap
  @Watch('runingQueue')
  public handleQueueChange(v: any[]) {
    if (v && v.length > 0 && !this.timer) {
      // 开启定时任务
      this.handleRunTimer()
    } else if (!v || v.length === 0) {
      // 当且仅当运行队列为空时才能移除timer
      // 结束所有任务
      clearTimeout(this.timer)
      this.timer = null
    }
  }
  public beforeDestroy() {
    clearTimeout(this.timer)
    this.timer = null
    this.runingQueue = []
  }

  public async handleRunTimer() {
    const fn = async () => {
      if (this.runingQueue.length === 0) {
        clearTimeout(this.timer)
        this.timer = null
        return
      }
      this.handlePollData && await this.handlePollData()
      this.timer = setTimeout(() => {
        fn()
      }, this.interval)
    }
    this.timer = setTimeout(fn, this.interval)
  }
}

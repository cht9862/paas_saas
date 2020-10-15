import { mapGetters } from 'vuex'
import { Vue, Component } from 'vue-property-decorator'

// eslint-disable-next-line new-cap
@Component({
  computed: mapGetters(['currentNavName'])
})
export default class RouterBackMixin extends Vue {
  private readonly currentNavName!: string
  public routerBack() {
    if (window.history.length <= 1) {
      this.currentNavName
        ? this.$router.push({ name: this.currentNavName })
        : this.$router.push({ path: '/' })
    } else {
      this.$router.back()
    }
  }
}

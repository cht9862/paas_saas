import Vue from 'vue'
// 给vue对象添加自定义方法
declare module 'vue/types/vue' {
  interface Vue {
    $bkPopover: (e: EventTarget, options: { [prop: string]: any }) => {}
    $bkMessage: (options: { [prop: string]: any }) => {}
  }
}

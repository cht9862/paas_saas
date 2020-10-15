// 全局函数
const topWindow = getTopWindow()
const topDocument = topWindow.document
try {
  topWindow.BLUEKING.corefunc.open_login_dialog = openLoginDialog
  topWindow.BLUEKING.corefunc.close_login_dialog = closeLoginDialog
  console.log('弹窗方法已注册到TOP窗口', window.top.BLUEKING.corefunc.close_login_dialog)
} catch (_) {
  topWindow.BLUEKING = {
    corefunc: {
      open_login_dialog: openLoginDialog,
      close_login_dialog: closeLoginDialog
    }
  }
  window.open_login_dialog = openLoginDialog
  window.close_login_dialog = closeLoginDialog
  console.log('弹窗方法已注册到当前窗口', window.close_login_dialog)
}
export function openLoginDialog(src: string, width = 460, height = 490, method = 'get') {
  if (!src) return
  const isWraperExit = topDocument.querySelector('#bk-gloabal-login-iframe')
  if (isWraperExit) return
  window.needReloadPage = method === 'get' // 是否需要刷新界面
  const closeIcon = topDocument.createElement('span')
  // eslint-disable-next-line max-len
  closeIcon.style.cssText = 'outline: 10px solid;outline-offset: -22px;transform: rotate(45deg);position: absolute;right: 0;cursor: pointer;color: #979ba5;width: 26px;height: 26px;border-radius: 50%;'
  closeIcon.id = 'bk-gloabal-login-close'
  topDocument.addEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)

  const frame = topDocument.createElement('iframe')
  frame.setAttribute('src', src)
  frame.style.cssText = `border: 0;outline: 0;width:${width}px;height:${height}px;background:#fff;`

  const dialogDiv = topDocument.createElement('div')
  dialogDiv.style.cssText = 'position: absolute;left: 50%;top: 20%;transform: translateX(-50%);'
  dialogDiv.appendChild(closeIcon)
  dialogDiv.appendChild(frame)

  const wraper = topDocument.createElement('div')
  wraper.id = 'bk-gloabal-login-iframe'
  // eslint-disable-next-line max-len
  wraper.style.cssText = 'position: fixed;top: 0;bottom: 0;left: 0;right: 0;background-color: rgba(0,0,0,.6);height: 100%;z-index: 1000;'
  wraper.appendChild(dialogDiv)
  topDocument.body.appendChild(wraper)
}
export function closeLoginDialog(e: Event) {
  try {
    e.stopPropagation()
    const el = e.target as HTMLElement
    const closeIcon = topDocument.querySelector('#bk-gloabal-login-close')
    if (closeIcon !== el) return
    topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
    // if (el) {
    //     el.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
    // }
    topDocument.body.removeChild<any>(el.parentElement?.parentElement)
  } catch (_) {
    topDocument.removeEventListener('click', topWindow.BLUEKING.corefunc.close_login_dialog)
    const wraper = topDocument.querySelector('#bk-gloabal-login-iframe')
    if (wraper) {
      topDocument.body.removeChild(wraper)
    }
  }
  window.needReloadPage && window.location.reload()
}

function getTopWindow() {
  try {
    if (window.top && window.top.document) {
      console.log('TOP窗口对象获取成功')
      return window.top
    }
    console.log('TOP窗口对象获取失败，已切换到当前窗口对象')
    return window
  } catch (err) {
    console.log(err)
    console.log('TOP窗口对象获取失败，已切换到当前窗口对象')
    return window
  }
}

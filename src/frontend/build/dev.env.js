/**
 * @file development env
 * @author v_daoqgong@tencent.com <v_daoqgong@tencent.com>
 */

// 环境变量里的值需要 JSON.stringify 化，原因如下：
// 这里的变量是给 new webpack.DefinePlugin 插件使用的，这个插件有如下两个特点：
// 1、如果传入的变量是字符串，那么它将被用作代码片段。
// 2、如果传入的变量不是字符串，那么它将被字符串化(包括函数)。
// 例如：
// 在代码中使用如下代码
// if (a === VARI)
// 如果这里定义的是 VART: JSON.stringify('abcde') 那么这段代码会替换为 if (a === 'abcde')
// 如果这里定义的是 VART: 'abcde' 那么这段代码会替换为 if (a === abcde) 会报错

import merge from 'webpack-merge'
import prodEnv from './prod.env'

const NODE_ENV = JSON.stringify('development')

export default merge(prodEnv, {
    NODE_ENV: NODE_ENV,
    LOCAL_DEV_URL: JSON.stringify(''), // 本地代理地址（和host的配置保持一致）
    LOCAL_DEV_PORT: JSON.stringify('8005'),
    AJAX_URL_PREFIX: JSON.stringify('api/'),
    AJAX_MOCK_PARAM: JSON.stringify('mock-file'),
    USER_INFO_URL: JSON.stringify('account/get_user_info/'),
    LOGIN_DEV_URL: JSON.stringify(``)// paas平台登录地址
})

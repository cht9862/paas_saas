/**
 * @file 替换 asset css 中的 BK_STATIC_URL，__webpack_public_path__ 没法解决 asset 里静态资源的 url
 * @author v_daoqgong@tencent.com <v_daoqgong@tencent.com>
 */

import { extname } from 'path'

export default class ReplaceCSSStaticUrlPlugin {
    apply (compiler, callback) {
        // emit: 在生成资源并输出到目录之前
        compiler.hooks.emit.tapAsync('ReplaceCSSStaticUrlPlugin', (compilation, callback) => {
            const assets = Object.keys(compilation.assets)
            const assetsLen = assets.length
            for (let i = 0; i < assetsLen; i++) {
                const fileName = assets[i]
                if (extname(fileName) !== '.css' && fileName !== 'index.html') {
                    continue
                }

                const asset = compilation.assets[fileName]

                let minifyFileContent = null
                if (fileName === 'index.html') {
                    minifyFileContent = asset.source().toString().replace(
                        /\{\{\s*STATIC_URL\s*\}\}\/nodeman/g,
                        () => '{{STATIC_URL}}nodeman'
                    )
                } else {
                    minifyFileContent = asset.source().toString().replace(
                        /\{\{\s*STATIC_URL\s*\}\}/g,
                        () => '../../'
                    )
                }
                // 设置输出资源
                compilation.assets[fileName] = {
                    // 返回文件内容
                    source: () => minifyFileContent,
                    // 返回文件大小
                    size: () => Buffer.byteLength(minifyFileContent, 'utf8')
                }
            }

            callback()
        })
    }
}

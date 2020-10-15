/**
 * @file util
 * @author v_daoqgong@tencent.com <v_daoqgong@tencent.com>
 */

import path from 'path'

export function resolve (dir) {
    return path.join(__dirname, '..', dir)
}

export function assetsPath (_path) {
    const assetsSubDirectory = 'nodeman'
    return path.posix.join(assetsSubDirectory, _path)
}

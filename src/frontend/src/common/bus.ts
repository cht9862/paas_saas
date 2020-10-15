/**
 * @file event bus
 * @author v_daoqgong@tencent.com <v_daoqgong@tencent.com>
 */

import Vue from 'vue'

// Use a bus for components communication,
// see https://vuejs.org/v2/guide/components.html#Non-Parent-Child-Communication
export const bus = new Vue()

export default bus

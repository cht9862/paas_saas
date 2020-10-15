<template>
    <div class="ip-select" :style="{ minWidth: minWidth + 'px',height: height + 'px' }" v-bind="$attrs">
        <!--IP选择器左侧tree区域-->
        <div class="ip-select-left">
            <!--静态/动态 tab页-->
            <div class="left-tab">
                <span
                    class="left-tab-item"
                    :class="[active === 0 ? 'active' : 'tab-item', { 'tab-disabled': tabDisabled === 0 }]"
                    :style="{ 'border-right': active === 1 ? '1px solid #DCDEE5' : 'none' }"
                    @click="tabDisabled !== 0 && handleTabClick(0)"
                    @mouseleave="handleStaticMouseLeave"
                    @mouseenter="handleStaticMouseEnter">
                    <span ref="staticTab"><slot name="left-tab">静态</slot></span>
                </span>
                <span class="left-tab-item "
                    :class="[active === 1 ? 'active' : 'tab-item', { 'tab-disabled': tabDisabled === 1 }]"
                    :style="{ 'border-left': active === 0 ? '1px solid #DCDEE5' : 'none' }"
                    @click="tabDisabled !== 1 && handleTabClick(1)"
                    @mouseleave="handleDynamicMouseLeave"
                    @mouseenter="handleDynamicMouseEnter">
                    <span ref="dynamicTab"><slot name="left-tab">动态</slot></span>
                </span>
            </div>
            <!--静态/动态 tree-->
            <div class="left-content">
                <!--静态输入方式1. 业务拓扑 2. IP输入-->
                <bk-select v-if="active === 0 && !selectUnshow.includes(active)" v-model="select.staticActive" class="left-content-select" :popover-min-width="200" :clearable="false" @change="handleActiveSelectChange">
                    <bk-option v-for="option in select.staticList"
                        :disabled="activeDiabled.includes(option.id)"
                        :key="option.id"
                        :id="option.id"
                        :name="option.name"
                        v-show="!activeUnshow.includes(option.id)">
                    </bk-option>
                </bk-select>
                <!--动态输入方式1. 业务拓扑 2. 动态分组-->
                <bk-select v-if="active === 1 && !selectUnshow.includes(active)" v-model="select.dynamicActive" class="left-content-select" :popover-min-width="200" :clearable="false" @change="handleActiveSelectChange">
                    <bk-option v-for="option in select.dynamicList"
                        :key="option.id"
                        :disabled="activeDiabled.includes(option.id)"
                        :id="option.id"
                        :name="option.name"
                        v-show="!activeUnshow.includes(option.id)">
                    </bk-option>
                </bk-select>
                <!--静态/动态 tree组件-->
                <div class="left-content-wrap" :style="{ '--height': height + 'px' }" v-bkloading="{ isLoading: isShowTreeLoading && leftLoading }">
                    <keep-alive>
                        <template>
                            <!--静态-IP输入-->
                            <slot v-if="curActive === 0"
                                name="static-input"
                                v-bind="{
                                    defaultText: staticInput.defaultText,
                                    checked: handleSelectChecked
                                }">
                                <template>
                                    <static-input
                                        :default-text="staticInput.defaultText"
                                        @checked="handleSelectChecked"
                                        @change-input="handleChangeInput">
                                        <slot name="change-input"></slot>
                                    </static-input>
                                </template>
                            </slot>
                            <!--静态-业务拓扑-->
                            <slot v-else-if="curActive === 1"
                                name="static-topo"
                                v-bind="{
                                    treeData: staticTopo.treeData,
                                    checkedData: staticChecked,
                                    disabledData: staticTopo.disabledData,
                                    filterMethod: filterMethod,
                                    keyword: search.keyword,
                                    nodeCheck: handleSelectChecked
                                }">
                                <template>
                                    <static-topo
                                        v-if="staticTopo.treeData.length"
                                        :tree-data="staticTopo.treeData"
                                        :checked-data="staticChecked"
                                        :disabled-data="staticTopo.disabledData"
                                        :filter-method="filterMethod"
                                        :keyword="search.keyword"
                                        :is-search-no-data.sync="isSearchNoData"
                                        :default-expand-node="staticTopo.defaultExpandNode"
                                        @node-check="handleSelectChecked"></static-topo>
                                </template>
                            </slot>
                            <!--动态-业务拓扑-->
                            <slot v-else-if="curActive === 2"
                                name="dynamic-topo"
                                v-bind="{
                                    treeData: dynamicTopo.treeData,
                                    checkedData: dynamicTopo.checkedData,
                                    disabledData: dynamicTopo.disabledData,
                                    filterMethod: filterMethod,
                                    keyword: search.keyword,
                                    refs: $refs.dynamicTopo,
                                    nodeCheck: handleSelectChecked
                                }">
                                <template>
                                    <dynamic-topo
                                        v-if="dynamicTopo.treeData.length"
                                        :tree-data="dynamicTopo.treeData"
                                        :checked-data="dynamicTopo.checkedData"
                                        :disabled-data="dynamicTopo.disabledData"
                                        :filter-method="filterMethod"
                                        :keyword="search.keyword"
                                        :is-search-no-data.sync="isSearchNoData"
                                        ref="dynamicTopo"
                                        :default-expand-node="dynamicTopo.defaultExpandNode"
                                        @node-check="handleSelectChecked"></dynamic-topo>
                                </template>
                            </slot>
                            <!--动态-动态分组-->
                            <slot v-else-if="curActive === 3"
                                name="dynamic-group"
                                v-bind="{
                                    treeData: dynamicGroup.treeData,
                                    checkedData: dynamicGroup.checkedData,
                                    disabledData: dynamicGroup.disabledData,
                                    filterMethod: filterMethod,
                                    keyword: search.keyword,
                                    refs: $refs.dynamicGroup,
                                    nodeCheck: handleSelectChecked
                                }">
                                <template>
                                    <dynamic-group
                                        v-if="dynamicGroup.treeData.length"
                                        :tree-data="dynamicGroup.treeData"
                                        :checked-data="dynamicGroup.checkedData"
                                        :disabled-data="dynamicGroup.disabledData"
                                        :filter-method="filterMethod"
                                        :keyword="search.keyword"
                                        ref="dynamicGroup"
                                        @node-check="handleSelectChecked"></dynamic-group>
                                </template>
                            </slot>
                        </template>
                    </keep-alive>
                    <!--空数据-->
                    <div v-if="isSearchNoData" class="search-none">
                        <slot name="search-noData"></slot>
                    </div>
                </div>
            </div>
            <!--tree搜索-->
            <div class="left-footer" :class="{ 'input-focus': search.focus }" v-show="curActive !== 0">
                <i class="bk-icon icon-search left-footer-icon"></i>
                <input class="left-footer-input"
                    :placeholder="searchPlaceholder"
                    @focus="handleSearchFocus"
                    @blur="search.focus = false"
                    v-model="search.keyword" />
            </div>
        </div>
        <!--IP选择器右侧表格区域-->
        <div class="ip-select-right">
            <div :key="staticIp.type" class="right-wrap"
                :class="{ 'is-expand': staticIp.expand }"
                v-if="staticTableData.length"
                v-bkloading="{ isLoading: isShowTableLoading && staticLoading }">
                <right-panel v-model="staticIp.expand" type="staticIp" @change="handleCollapseChange" :title="{ num: curComp.tableData.length }">
                    <slot name="static-ip-panel"
                        v-bind="{
                            data: staticTableData,
                            deleteClick: handleDeleteStaticIp
                        }">
                        <bk-table :data="staticTableData" empty-text="暂无数据">
                            <bk-table-column prop="ip" label="IP" min-width="210">
                            </bk-table-column>
                            <bk-table-column prop="agent" label="状态">
                            </bk-table-column>
                            <bk-table-column prop="cloud" label="云区域">
                            </bk-table-column>
                            <bk-table-column label="操作" align="center" width="80">
                                <template slot-scope="scope">
                                    <bk-button text @click="handleDeleteStaticIp(scope)">移除</bk-button>
                                </template>
                            </bk-table-column>
                        </bk-table>
                    </slot>
                </right-panel>
            </div>
            <div :key="dynamicTopo.type" class="right-wrap"
                v-bkloading="{ isLoading: isShowTableLoading && dynamicTopo.loading }"
                :class="{ 'is-expand': dynamicTopo.expand }"
                v-if="dynamicTopo.tableData.length">
                <right-panel v-model="dynamicTopo.expand" @change="handleCollapseChange" type="dynamicTopo" :title="{ num: dynamicTopo.tableData.length, 'type': '节点' }">
                    <slot name="dynamic-topo-panel" v-bind="{
                        data: dynamicTopo.tableData,
                        deleteClick: handleDelDynamicTopo
                    }">
                        <ul class="topo-list">
                            <li class="topo-list-item" v-for="(item,index) in dynamicTopo.tableData" :key="index">
                                <span class="item-name">{{item.name}}</span>
                                <div class="item-desc">
                                    现有主机<span class="status-host">{{item.host}}</span>，<span class="status-unusual">{{item.unusual}}</span>台主机Agent异常
                                </div>
                                <bk-button text class="item-btn" @click="handleDelDynamicTopo(index,item)">移除</bk-button>
                            </li>
                        </ul>
                    </slot>
                </right-panel>
            </div>
            <div :key="dynamicGroup.type" class="right-wrap"
                v-bkloading="{ isLoading: isShowTableLoading && dynamicGroup.loading }"
                :class="{ 'is-expand': dynamicGroup.expand }"
                v-if="dynamicGroup.tableData.length">
                <right-panel v-model="curComp.expand" @change="handleCollapseChange" type="dynamicTopo">
                    <slot name="dynamic-group-panel"
                        v-bind="{
                            data: dynamicGroup.tableData
                        }">
                    </slot>
                </right-panel>
            </div>
            <div key="right-empty" class="right-empty" v-if="isNoData">
                <span class="icon-monitor icon-hint"></span>
                <div class="right-empty-title">未选择任何内容</div>
                <div class="right-empty-desc">{{defaultEmptyDesc}}</div>
            </div>
        </div>
    </div>
</template>
<script>
    import RightPanel from './right-panel'
    import StaticInput from './static-input'
    import StaticTopo from './static-topo'
    import DynamicTopo from './dynamic-topo'
    import DynamicGroup from './dynamic-group'

    const EVENT_ACTIVESELECTCHANGE = 'active-select-change'

    export default {
        name: 'ip-select',
        components: {
            RightPanel,
            StaticInput,
            StaticTopo,
            DynamicTopo,
            DynamicGroup
        },
        props: {
            // IP选择器最小宽度
            minWidth: {
                type: [Number, String],
                default: 850
            },
            // IP选择器高度
            height: {
                type: [Number, String],
                default: 460
            },
            idKey: {
                type: String,
                default: 'id'
            },
            nameKey: {
                type: String,
                default: 'name'
            },
            childrenKey: {
                type: String,
                default: 'children'
            },
            // 禁用 静态/动态 tab页
            tabDisabled: {
                type: Number,
                default: -1
            },
            // 禁用 静态/动态 输入方式
            activeDiabled: {
                type: Array,
                default () {
                    return [3]
                }
            },
            // 是否显示 静态/动态 输入方式（选项）
            activeUnshow: {
                type: Array,
                default () {
                    return []
                }
            },
            // 是否显示 静态/动态 输入方式（select框）
            selectUnshow: {
                type: Array,
                default () {
                    return []
                }
            },
            // 默认激活的 静态/动态 tab页
            defaultActive: {
                type: Number,
                required: true
            },
            // 右侧表格空数据text
            defaultEmptyDesc: {
                type: String,
                default: '请在左侧选择主机/节点/动态分组'
            },
            inputIpSplit: {
                type: String,
                default: '|'
            },
            // 获取默认数据（tree数据、默认勾选数据、禁用数据、表格数据、默认展开节点数据）！！！！
            getDefaultData: {
                type: Function, // 需返回 treeData、checkedData（可选）、disabledData（可选）、tableData（可选）、defaultExpandNode（可选）
                required: true
            },
            // 勾选树节点时会触发此方法获取数据 ！！！！
            getFetchData: {
                type: Function,
                required: true
            },
            // 树过滤方法
            filterMethod: {
                type: Function,
                default: () => () => {}
            },
            isShowTreeLoading: {
                type: Boolean,
                default: true
            },
            isShowTableLoading: {
                type: Boolean,
                default: true
            },
            // 是否是实例（实例对象只能选择动态tab的业务拓扑）
            isInstance: Boolean
        },
        data () {
            return {
                active: 0, // 当前 active 的 tab
                changeInput: false,
                // 静态/动态 输入方式数据
                select: {
                    staticList: [
                        {
                            id: 0,
                            name: 'IP输入',
                            type: 'staticInput'
                        },
                        {
                            id: 1,
                            name: '业务拓扑',
                            type: 'staticTopo'
                        }
                    ],
                    dynamicList: [
                        {
                            id: 2,
                            name: '业务拓扑',
                            type: 'dynamicTopo'
                        },
                        {
                            id: 3,
                            name: '动态分组',
                            type: 'dynamicGroup'
                        }
                    ],
                    staticActive: 0,
                    dynamicActive: 2
                },
                // 静态输入
                staticInput: {
                    name: 'staticIp',
                    defaultText: '',
                    expand: false,
                    checkedData: [],
                    tableData: [],
                    type: 'static-ip',
                    mark: false,
                    loading: false
                },
                // 静态拓扑（tree）
                staticTopo: {
                    name: 'staticIp',
                    treeData: [],
                    checkedData: [],
                    disabledData: [],
                    expand: false,
                    tableData: [],
                    type: 'static-topo',
                    loading: false,
                    defaultExpandNode: 1
                },
                // 动态拓扑（tree）
                dynamicTopo: {
                    name: 'dynamicTopo',
                    treeData: [],
                    checkedData: [],
                    disabledData: [],
                    expand: false,
                    tableData: [],
                    type: 'dynamic-topo',
                    loading: false,
                    defaultExpandNode: 1
                },
                dynamicGroup: {
                    name: 'dynamicGroup',
                    treeData: [],
                    checkedData: [],
                    disabledData: [],
                    expand: false,
                    tableData: [],
                    type: 'dynamic-group',
                    loading: false
                },
                // 搜索关键字
                search: {
                    keyword: '',
                    focus: false
                },
                leftLoading: false,
                isSearchNoData: false,
                staticIp: {
                    expand: false
                },
                instance: {
                    dynamic: null,
                    static: null
                },
                // 搜索框placeholder
                searchPlaceholder: '请输入IP'
            }
        },
        computed: {
            curComp () {
                return this[this.curItem.type]
            },
            // 当前输入方式
            curActive () {
                return this.active === 0 ? this.select.staticActive : this.select.dynamicActive
            },
            curItem () {
                return this.active === 0 ? this.select.staticList.find(item => item.id === this.select.staticActive) : this.select.dynamicList.find(item => item.id === this.select.dynamicActive)
            },
            staticTableData () {
                let arr = this.handleStaticTableData(this.staticInput.tableData, this.staticTopo.tableData)
                const hash = {}
                arr = arr.reduce((item, next) => {
                    if (!hash[next.name]) {
                        hash[next.name] = true
                        item.push(next)
                    }
                    return item
                }, [])
                return arr
            },
            staticChecked () {
                const ids = this.handleStaticTableData(this.staticInput.checkedData, this.staticTopo.checkedData, false)
                ids.concat(this.staticTopo.checkedData)
                return Array.from(new Set(ids))
            },
            staticLoading () {
                return this.staticInput.loading || this.staticTopo.loading
            },
            isNoData () {
                return !this.staticTableData.length && !this.dynamicTopo.tableData.length && !this.dynamicGroup.tableData.length
            }
        },
        watch: {
            curActive: {
                handler: 'handlerCurActiveChange'
                // immediate: true
            },
            defaultActive: {
                handler (v, old) {
                    if (v === 0 || v === 1) {
                        this.active = 0
                        this.select.staticActive = v
                        this.curComp.expand = true
                        this.staticIp.expand = true
                    } else if (v === 2 || v === 3) {
                        this.active = 1
                        this.select.dynamicActive = v
                        this.curComp.expand = true
                    }
                },
                immediate: true
            }
        },
        methods: {
            // 节点勾选时触发
            async handleSelectChecked (type, payload) {
                const curComp = this.curComp
                try {
                    curComp.loading = true
                    const { checkedData, tableData, disabledData } = await this.getFetchData(type, payload)
                    this.setCurActivedCheckedData(checkedData)
                    this.setCurActivedDisabledData(disabledData)
                    this.setCurActivedTableData(tableData)
                    this.handleCollapseChange(true, curComp.name)
                } catch (e) {
                    return e
                } finally {
                    curComp.loading = false
                }
            },
            // 切花 tab 时事件
            async handlerCurActiveChange (v, old) {
                try {
                    this.active === 0 ? this.searchPlaceholder = '请输入IP' : this.searchPlaceholder = '搜索节点' // 静态和动态搜索款Placeholder
                    if (typeof this.getDefaultData === 'function') {
                        this.leftLoading = true
                        if ((v > 0 && this.curComp.treeData.length === 0) || (v === 0 && !this.curComp.mark)) {
                            const data = await this.getDefaultData(this.curComp.type)
                            this.leftLoading = false
                            if (data) {
                                if (v > 0) {
                                    this.curComp.treeData = data.treeData || []
                                    this.curComp.checkedData = data.checkedData || []
                                    this.curComp.disabledData = data.disabledData || []
                                    this.curComp.tableData = data.tableData || []
                                    this.curComp.defaultExpandNode = data.defaultExpandNode || 1
                                } else {
                                    this.curComp.tableData = data.tableData || []
                                    this.curComp.mark = true
                                    this.curComp.defaultText = (data.defaultText || '').replace(new RegExp(`\\${this.inputIpSplit}`, 'gm'), '\n')
                                }
                            }
                        }
                    }
                } catch (e) {
                    return e
                } finally {
                    this.leftLoading = false
                }
            },
            handleStaticTableData (data1, data2, value = true) {
                const data = new Map()
                let len = Math.max(data1.length, data2.length)
                while (len) {
                    const item1 = data1[len - 1]
                    const item2 = data2[len - 1]
                    if (item1) {
                        if (item1[this.idKey]) {
                            data.set(item1[this.idKey], item1)
                        } else {
                            data.set(item1, item1)
                        }
                    }
                    if (item2) {
                        if (item2[this.idKey]) {
                            data.set(item2[this.idKey], item2)
                        } else {
                            data.set(item2, item2)
                        }
                    }
                    len--
                }
                return value ? Array.from(data.values()) : Array.from(data.keys())
            },
            handleSearchFocus () {
                this.search.focus = true
            },
            handleCollapseChange (v, set) {
                if (v) {
                    ['staticIp', 'dynamicTopo'].forEach(key => {
                        this[key].expand = set === key
                    })
                } else {
                    this[set].expand = v
                }
            },
            handleDeleteStaticIp (scope) {
                this.staticInput.tableData = this.staticInput.tableData.filter(item => item[this.idKey] !== scope.row[this.idKey])
                this.staticTopo.tableData = this.staticTopo.tableData.filter(item => item[this.idKey] !== scope.row[this.idKey])
            },
            handleDelDynamicTopo (index, item) {
                const setIndex = this.dynamicTopo.checkedData.findIndex(setId => setId === item[this.idKey])
                if (setIndex > -1) {
                    this.$refs.dynamicTopo.handleSetChecked([this.dynamicTopo.checkedData[setIndex]], false)
                    this.dynamicTopo.checkedData.splice(setIndex, 1)
                }
                this.dynamicTopo.tableData.splice(index, 1)
            },
            handleTabClick (active) {
                this.active = active
            },
            getValues () {
                return {
                    staticIp: this.staticTableData,
                    dynamicTopo: this.dynamicTopo.tableData
                }
            },
            setCurActivedCheckedData (checkedData) {
                if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
                    this.staticInput.checkedData = Array.isArray(checkedData) ? checkedData.slice() : []
                    this.staticTopo.checkedData = this.staticInput.checkedData
                } else {
                    this.curComp.checkedData = Array.isArray(checkedData) ? checkedData.slice() : []
                }
            },
            setCurActivedDisabledData (disabledData) {
                if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
                    this.staticInput.disabledData = Array.isArray(disabledData) ? disabledData.slice() : []
                    this.staticTopo.disabledData = this.staticInput.disabledData
                } else {
                    this.curComp.disabledData = Array.isArray(disabledData) ? disabledData.slice() : []
                }
            },
            setCurActivedTableData (tableData) {
                if (this.curComp.type === 'static-ip' || this.curComp.type === 'static-topo') {
                    this.staticInput.tableData = Array.isArray(tableData) ? tableData.slice() : []
                    this.staticTopo.tableData = this.staticInput.tableData
                } else {
                    this.curComp.tableData = Array.isArray(tableData) ? tableData.slice() : []
                }
            },
            handleStaticMouseEnter (e) {
                if (this.tabDisabled === 1 || this.tabDisabled === -1) {
                    if (this.instance.static) {
                        this.instance.static.destroy(true)
                        this.instance.static = null
                    }
                    return false
                }
                const staticRef = this.$refs.staticTab
                let content = '支持静态IP的选择方式'
                if (this.tabDisabled === 0 && this.isInstance) {
                    content = '监控对象为服务，只能选择动态方式'
                } else if (this.tabDisabled === 0) {
                    content = '动态和静态不能混用'
                }
                if (!this.instance.static) {
                    this.instance.static = this.$bkPopover(staticRef, {
                        content,
                        arrow: true,
                        maxWidth: 250,
                        showOnInit: true,
                        distance: 14,
                        placement: 'right'
                    })
                }
                this.instance.static.set({ content })
                this.instance.static && this.instance.static.show(100)
            },
            handleStaticMouseLeave (e) {
                this.instance.static && this.instance.static.hide(0)
            },
            handleDynamicMouseEnter (e) {
                if (this.tabDisabled === 0 || this.tabDisabled === -1) {
                    if (this.instance.dynamic) {
                        this.instance.dynamic.destroy(true)
                        this.instance.dynamic = null
                    }
                    return false
                }
                let content = '支持按拓扑节点动态变化进行采集'
                if (this.tabDisabled === 1) {
                    content = '动态和静态不能混用'
                }
                const dynamicRef = this.$refs.dynamicTab
                if (!this.instance.dynamic) {
                    this.instance.dynamic = this.$bkPopover(dynamicRef, {
                        content,
                        arrow: true,
                        maxWidth: 250,
                        showOnInit: true,
                        distance: 14,
                        placement: 'right'
                    })
                }
                this.instance.dynamic.set({ content })
                this.instance.dynamic && this.instance.dynamic.show(100)
            },
            handleDynamicMouseLeave (e) {
                this.instance.dynamic && this.instance.dynamic.hide(0)
            },
            handleChangeInput (v) {
                this.$emit('change-input', v)
            },
            // 当前active select选项改变
            handleActiveSelectChange (v, old) {
                this.$emit(EVENT_ACTIVESELECTCHANGE, {
                    newValue: v,
                    oldValue: old
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
.ip-select {
    display: flex;
    background-color: #FFFFFF;
    border-radius: 2px;
    color: #63656E;
    font-size: 12px;
    &-left {
        flex: 0 0 240px;
        background-image: linear-gradient(180deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%),linear-gradient(90deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%),linear-gradient(-90deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%),linear-gradient(0deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%);
        background-size: 100% 100%;
        position: relative;
        .left-tab {
            display: flex;
            height: 42px;
            font-size: 14px;
            &-item {
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #DCDEE5;
                background: #FAFBFD;
                &:first-child {
                    border-right: none
                }
                &.active {
                    background: #FFFFFF;
                    border-bottom: none;
                    height: 41px;
                }
                &.tab-item:hover {
                    border-color: #3A84FF !important;
                    cursor: pointer;
                    color: #3A84FF;
                }
                &.tab-disabled {
                    color: #C4C6CC;
                    &:hover {
                        cursor: not-allowed;
                        border-color: #DCDEE5 !important;
                        color: #C4C6CC;
                    }
                }
            }
        }
        .left-content {
            padding: 20px;
            &-select {
                width: 200px;
            }
            &-wrap {
                height: calc(var(--height) - 142px);
                max-width: 200px;
                overflow: auto;

            }
            .search-none {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 250px;
            }
        }
        .left-footer {
            height: 32px;
            display: flex;
            align-items: center;
            border: 1px solid #DCDEE5;
            color: #C4C6CC;
            position: absolute;
            left: 0;
            bottom: 0;
            right: 0;
            ::placeholder {
                color: #979BA5;
            }
            &.input-focus {
                border-color: #3A84FF;
                .icon-search {
                    color: #3A84FF
                }
            }
            &-icon {
                font-size: 14px;
                flex: 0 0 34px;
                text-align: center;
            }
            &-input {
                color: #63656E;
                height: 30px;
                width: 100%;
                border: none;
            }
        }
    }
    &-right {
        flex: 1;
        background-image: linear-gradient(180deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%),linear-gradient(-90deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%),linear-gradient(0deg, #DCDEE5 1px, rgba(0, 0, 0, 0)
        1px, rgba(0, 0, 0, 0) 100%);
        background-size: 100% 100%;
        border-left: none;
        overflow: auto;
        .right-wrap {
            border: 1px solid #DCDEE5;
            border-left: 0;
            &.is-expand {
                border-bottom: 0;
            }
            &+.right-wrap{
                border-top: 0
            }
            .topo-list {
                color: #63656E;
                font-size: 12px;
                &-item {
                    height: 40px;
                    display: flex;
                    align-items: center;
                    border-bottom: 1px solid #dfe0e5;
                    padding-left: 32px;
                    &:hover {
                        background-color: #f0f1f5;
                    }
                    .item-desc{
                        flex: 1;
                        margin-left: 94px;
                        color: #979BA5;
                        .status-host {
                            color: #3A84FF;
                            font-weight: bold;
                        }
                        .status-unusual {
                            color: #EA3636;
                            font-weight: bold;
                        }
                    }
                    .item-btn {
                        margin-right: 21px;
                        font-size: 12px;
                    }
                }
            }
        }
        .right-empty {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 164px;
            .icon-monitor {
                font-size: 28px;
                color: #DCDEE5;
                margin-bottom: 8px;
            }
            &-title {
                font-size: 14px;
                margin-bottom: 3px;
            }
            &-desc {
                color: #C4C6CC;
            }
        }
    }
}
</style>

<template>
    <section class="agent-manager-area" v-bkloading="{ isLoading: loading }">
        <!--左侧区域面板-->
        <div class="area-left">
            <transition-group class="area-button-group" :class="{ 'fold-group': !hasExpand }" :name="flip" tag="div">
                <!--全部按钮-->
                <span
                    @click="handleAreaClick({ id: -1 })"
                    class="area-button area-all"
                    key="all"
                    :class="{
                        'is-edit': type === 'edit',
                        'is-select': area.active === -1 && type !== 'edit',
                        'is-disabled': type === 'edit'
                    }">
                    {{ $t('全部区域') }}
                </span>
                <!--区域面板-->
                <span
                    class="area-button"
                    v-for="(item, index) in area.list"
                    :key="item.id"
                    :class="btnClassObject(item, index)"
                    @drag="handleDrag(index, $event)"
                    @dragstart="handleDragStart(index, item, $event)"
                    @dragend="handleDragEnd(index, $event)"
                    @dragenter="handleDragEnter(index)"
                    :ref="item.id"
                    @click="handleAreaClick(item)"
                    :draggable="type === 'edit'">
                    <span class="area-icon" v-html="cloudProvider[item.provider].svg" v-if="cloudProvider[item.provider]"></span>
                    <span class="area-name">{{ item.name }}</span>
                    <i class="close-icon bk-icon icon-close-circle-shape" v-if="type === 'edit'" @click.stop="handleHideArea(item)"></i>
                </span>
                <!--占据剩余宽度-->
                <span class="area-button area-button-space" v-show="newLineIndex === -1 && type !== 'edit'" key="space"></span>
            </transition-group>
        </div>
        <!--右侧操作面板-->
        <div class="area-right">
            <span
                class="agent-area-button more-button"
                @click="handleExpand"
                :class="{ 'is-select': activeMoreArea && !hasExpand, 'is-disabled': type === 'edit' }"
                v-show="newLineIndex !== -1 || type === 'edit'">
                <span class="text" :title="moreBtnText">{{ moreBtnText }}</span>
                <i class="icon bk-icon" :class="[hasExpand ? 'icon-up-shape' : 'icon-down-shape']"></i>
            </span>
            <span
                class="agent-area-button setting-button"
                v-bk-tooltips.top-start="settingTips"
                :class="{ 'is-disabled': type === 'edit' }"
                @click="handleShowSetting">
                <i class="bk-icon icon-cog-shape"></i>
            </span>
        </div>
    </section>
</template>
<script>
    import { addListener, removeListener } from 'resize-detector'
    import { debounce } from '@/common/util'

    export default {
        name: 'area-filter',
        props: {
            loading: {
                type: Boolean,
                default: false
            },
            type: {
                type: String,
                default: 'view',
                validator (v) {
                    return ['view', 'edit'].includes(v)
                }
            },
            list: {
                type: Array,
                default: () => []
            },
            defaultExpand: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                area: {
                    list: this.list,
                    active: -1
                },
                hasExpand: this.defaultExpand,
                listenResize () {},
                // 折行的索引
                newLineIndex: -1,
                settingTips: this.type !== 'edit' ? this.$t('云区域显示设置') : '',
                drag: {
                    newIndex: -1,
                    oldIndex: -1
                },
                flip: '',
                // 服务商Map
                cloudProvider: {
                    阿里云: {
                        name: '阿里云',
                        svg: `<svg width="30px" height="18px" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg"><g fill="#ff5e00"><path d="M22.5,44.9c-1.3-1.1-6.2-1.9-8.3-2.6c-2.1-0.8-3.3-2-3.3-4.8c0-2.8,0-5.5,0-5.5s0-2.6,0-5.5 c0-2.8,1.2-4,3.3-4.8c2.1-0.8,7.1-1.6,8.3-2.6c1.3-1.1,3.3-4.6,3.3-4.6H14c-5.5,0-10,4.5-10,10v15c0,5.5,4.5,10,10,10h11.8 C25.8,49.5,23.8,45.9,22.5,44.9z" /><path d="M50,14.5H38.2c0,0,2,3.6,3.3,4.6c1.3,1.1,6.2,1.9,8.3,2.6c2.1,0.8,3.3,2,3.3,4.8c0,2.8,0,5.5,0,5.5 s0,2.6,0,5.5c0,2.8-1.2,4-3.3,4.8c-2.1,0.8-7.1,1.6-8.3,2.6c-1.3,1.1-3.3,4.6-3.3,4.6H50c5.5,0,10-4.5,10-10v-15 C60,19,55.5,14.5,50,14.5z" /></g><path fill="#ff5e00" d="M23 30H41V34H23z" /></svg>`
                    },
                    AWS: {
                        name: 'AWS',
                        svg: `<svg width="30px" height="18px" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg"><path fill="#202f3f" d="M19.8,28.5c-0.3-0.8-0.1-4.7,0-7.4s-1.4-5.2-5-5.6S8,16.8,7.6,17.1c-0.4,0.3-0.3,1.9,0.2,2c0.5,0,1.7-0.6,2.5-0.8c0.9-0.2,4.5-1,5.7,0.6c1.1,1.6,0.6,4.2,0.6,4.2S14,22.3,12,22.5c-1.4,0.1-5.5,0.8-5.6,5c-0.1,4.2,2.7,5.2,5.8,5.1c3.1-0.1,4.7-2.5,4.7-2.5s1.3,2.2,1.7,2.2s2-1.2,2.1-1.6C20.8,30.4,20,29.3,19.8,28.5z M16,28.8c-1,1-2.2,1.6-4,1.6s-2.2-1.6-2.3-2.2c0-0.6-0.2-2.9,2.1-3.3s4.9,0.4,4.9,0.4S17,27.8,16,28.8z" /><path fill="#202f3f" d="M22.4,16c-0.5,0-1.1-0.1-0.7,1.2s4.2,13.7,4.3,14.1c0.2,0.4,0.1,0.9,1.1,0.9c1,0,1.3,0,1.8,0c0.5,0,0.6-0.3,1.1-1.9s2.6-10.8,2.6-10.8l2.3,9.4c0,0,0.5,1.9,0.6,2.3c0.1,0.4,0.1,0.9,1.1,1s1.4,0,1.9,0c0.5,0,0.7-0.8,1.4-3s3.6-11.4,3.8-12.1c0.2-0.7,0.3-1.2-1-1.1c-1.3,0.1-1.7-0.6-2.4,2.2s-2.8,10.9-2.8,10.9s-2.7-11.1-2.8-12s-0.4-1.2-1.5-1.2c-1.1,0-1.9-0.3-2.3,1.6s-2.8,11.4-2.8,11.4s-2.6-10.2-2.8-11.2c-0.3-1-0.1-1.9-1.4-1.8C22.4,16,22.4,16,22.4,16z" /><path fill="#202f3f" d="M56.3,17c-0.2-0.5-2.3-1.6-5.8-1.5c-3.5,0.2-5.3,2.8-5.2,5s1.7,3.6,4.6,4.6s4.3,1.3,4.3,2.8c0,1.5-1.3,2.5-3.9,2.5c-2.6,0-4.6-1.4-4.9-1.2c-0.4,0.2-0.3,1.3-0.3,1.6s0.3,1.1,2.7,1.6S54,33,55.9,31s1.4-4.9,0.7-5.8c-0.7-0.9-2.1-1.7-4.5-2.4s-4.1-1.3-3.6-3.4c0.5-2,3.9-1.5,4.6-1.4c0.7,0.1,2.6,1,3,0.9C56.4,18.7,56.4,17.4,56.3,17z"/><path fill="#ff9400" d="M4.3,37.2c0.3-0.6,3.9,1.9,5.7,2.7c1.8,0.8,11,4.7,19.7,4.8c8.7,0.1,12.7-0.9,15.4-1.5c2.7-0.6,6.1-1.9,6.9-2.3c0.8-0.4,1.8-1.2,2.5-0.3c0.7,0.9-3.8,4.2-11.6,6.6c-7.9,2.4-19.8,1.5-26.5-1.5C9.7,42.6,3.8,37.9,4.3,37.2z" /><path fill="#ff9400" d="M49.3,38.5c0.2-0.4,2-2,5-2.3c3-0.2,4.8,0.2,5.3,0.8s0.1,3.4-0.7,5.2c-0.8,1.7-2.6,4.4-3.4,4.1c-0.8-0.3,0.5-1.9,1.1-3.6c0.6-1.7,0.7-3.1,0.5-3.7c-0.3-0.5-1.7-0.8-3.7-0.7C51.2,38.5,49.1,38.9,49.3,38.5z" /></svg>`
                    },
                    腾讯云: {
                        name: '腾讯云',
                        svg: `<svg width="30px" height="18px" viewBox="0 0 64 64" version="1.1" xmlns="http://www.w3.org/2000/svg"><path fill="#00a3ff" d="M52.5,44.7c-1,1-2.8,2.1-5.7,2.2c-1.4,0-2.9,0.1-3.6,0.1c-0.8,0-7.7,0-15.7,0c5.7-5.5,10.7-10.4,11.3-10.9 c0.5-0.5,1.7-1.6,2.7-2.5c2.2-2,4.2-2.4,5.6-2.4c2.2,0,4.2,0.9,5.6,2.4C55.7,36.6,55.6,41.6,52.5,44.7 M56.3,29.9 C53.9,27.5,50.7,26,47,26c-3.1,0-5.8,1.1-8.2,3c-1,0.8-2.1,1.8-3.5,3.2c-0.7,0.7-20.2,19.6-20.2,19.6c1,0.1,2.4,0.2,3.7,0.2 c1.2,0,23.6,0,24.6,0c1.9,0,3.1,0,4.4-0.1c3-0.2,5.9-1.3,8.2-3.6C61.2,43.2,61.3,35,56.3,29.9z" /><path fill="#00c8dc" d="M24.7,28.7C22.4,27,19.9,26,17,26c-3.6,0-6.9,1.5-9.2,3.9c-5,5.1-4.9,13.3,0.2,18.4c2.1,2,4.6,3.1,7.2,3.5 l5-4.9c-0.8,0-2,0-3,0c-2.9-0.1-4.7-1.2-5.7-2.2c-3.1-3.1-3.2-8.1-0.1-11.2c1.4-1.4,3.4-2.3,5.6-2.4c1.4,0,3.2,0.4,5.4,2.1 c1,0.8,3.2,2.8,4.2,3.7c0.1,0,0.1,0,0.2,0l3.5-3.4c0.1-0.1,0.1-0.1,0-0.2C28.5,31.9,26.2,29.7,24.7,28.7" /><path fill="#006eff" d="M48.4,23.1C46,16.3,39.6,11.5,32,11.5c-8.7,0-15.9,6.4-17.2,14.7c0.7-0.1,1.4-0.2,2.1-0.2c1,0,2,0.1,2.9,0.3 c0,0,0,0,0.1,0c1.2-5.6,6.1-9.8,12.1-9.8c4.9,0,9.2,3,11.2,7.2c0,0.1,0.1,0.1,0.1,0.1c1.5-0.4,3.2-0.6,4.9-0.5 C48.4,23.3,48.5,23.2,48.4,23.1" /></svg>`
                    }
                }
            }
        },
        computed: {
            // ...mapGetters('agent', ['area']),
            // 展开更多按钮文案
            moreBtnText () {
                const activeIndex = this.area.list.findIndex(item => item.id === this.area.active)
                if (!this.hasExpand && this.newLineIndex !== -1 && activeIndex >= this.newLineIndex) {
                    return this.area.list[activeIndex].name
                }
                return this.hasExpand ? this.$t('收起更多') : this.$t('展开更多')
            },
            // 选中展开更多按钮
            activeMoreArea () {
                const activeIndex = this.area.list.findIndex(item => item.id === this.area.active)
                return this.newLineIndex !== -1 && activeIndex >= this.newLineIndex
            },
            btnClassObject () {
                return (item, index) => ({
                    'is-edit': this.type === 'edit',
                    'is-select': item.id === this.area.active && this.type !== 'edit',
                    'auto-width': this.newLineIndex >= 0 && this.newLineIndex > index
                })
            }
        },
        watch: {
            list: {
                handler (v) {
                    this.area.list = v
                    const hasActiveItem = this.area.list.some(item => item.id === this.area.active)
                    if (!hasActiveItem) {
                        this.area.active = -1
                    }
                    this.$nextTick(_ => {
                        this.handleResize()
                    })
                },
                deep: true
            }
        },
        created () {
            this.handleInit()
        },
        mounted () {
            this.listenResize = debounce(300, v => this.handleResize(v))
            addListener(this.$el, this.listenResize)
            this.handleResize()
        },
        beforeDestroy () {
            removeListener(this.$el, this.listenResize)
        },
        methods: {
            // ...mapActions('agent', ['getAreaList']),
            async handleInit () {
                // this.loading = true
                // if (!this.area.list.length) {
                //     await this.getAreaList()
                // }
                // await this.$nextTick()
                // this.handleResize()
                // this.loading = false
            },
            handleAreaClick (item) {
                if (this.type === 'edit') return
                this.area.active = item.id
            },
            handleExpand () {
                if (this.type === 'edit') return
                this.hasExpand = !this.hasExpand
            },
            handleResize (v) {
                this.newLineIndex = this.area.list.findIndex(item => this.$refs[item.id] && this.$refs[item.id][0] && this.$refs[item.id][0].offsetTop > 0)
            },
            handleShowSetting () {
                if (this.type === 'edit') return
                this.$emit('setting')
            },
            handleHideArea (item) {
                this.$emit('hideItem', item)
            },
            handleDragStart (i, item, e) {
                // e.dataTransfer.setData('text/plain', item.id)
                // e.dropEffect = 'move'
                this.drag.oldIndex = i
                this.flip = 'flip-list'
            },
            handleDrag (i, e) {
                // const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop
                // if (e.y < 180) {
                //     window.scrollTo(e.x, scrollTop - 9)
                // }
            },
            handleDragEnd (i, e) {
                e.preventDefault()
                if (this.drag.oldIndex !== this.drag.newIndex) {
                    const data = this.area.list.splice(this.drag.oldIndex, 1)
                    this.area.list.splice(this.drag.newIndex, 0, data[0])
                }
            },
            handleDragEnter (i) {
                this.drag.newIndex = i
            }
        }
    }
</script>
<style lang="postcss" scoped>
    @import '@/css/mixins/nodeman.css';

    @define-mixin name-overflow {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    @define-mixin area-btn {
        padding: 0 20px;
        height: 38px;
        line-height: 38px;
        border: 1px solid #DCDEE5;
        background: #FAFBFD;
        cursor: pointer;
        transition: background-color .3s ease;
        font-size: 14px;
        text-align: center;
        user-select: none;
        &:hover {
            color: #3a84ff;
            border-color: #3a84ff;
            z-index: 1;
        }
        &.is-select {
            background-color: #e1ecff;
            border-color: #3a84ff;
            color: #3a84ff;
            z-index: 1;
        }
        &.is-edit {
            padding: 0 10px 0 10px;
            margin-right: 7px;
            border: 1px dashed #C4C6CC;
            border-radius: 2px;
            color: #63656E;
            cursor: move;
        }
        &.is-disabled {
            border: 1px solid #DCDEE5;
            color: #DCDEE5;
            cursor: not-allowed;
        }
    }
    .flip-list-move {
        transition: transform 1s !important;
    }
    .agent-area-button {
        @mixin area-btn;
    }
    .agent-manager-area {
        @mixin layout-flex row, flex-start, space-between;
        .area-left {
            flex: 1;
            .area-button-group {
                @mixin layout-flex row, stretch, flex-start, wrap;
                .area-button {
                    @mixin area-btn;
                    @mixin layout-flex row, center, center;
                    flex: 0 1 auto;
                    margin: 0 0 10px -1px;
                    /* max-width: 264px; */
                    &.area-all {
                        flex-basis: 100px;
                    }
                    &:first-child {
                        margin-left: 0;
                        border-radius: 2px 0 0 2px;
                    }
                    &.area-button-space {
                        flex: 1;
                        max-width: none;
                        pointer-events: none;
                    }
                    &.auto-width {
                        flex: 1;
                        /* max-width: none; */
                    }
                    .area-icon {
                        @mixin layout-flex row, center;
                        margin: 0 2px 0 -6px;
                    }
                    .area-name {
                        @mixin name-overflow;
                    }
                    .close-icon {
                        color: #C4C6CC;
                        margin-left: 4px;
                        cursor: pointer;
                    }
                }
                &.fold-group {
                    height: 38px;
                    overflow: hidden;
                }
            }
        }
        .area-right {
            @mixin layout-flex row;
            .more-button {
                @mixin layout-flex row, center, center;
                margin-left: -1px;
                width: 120px;
                &:hover {
                    .icon {
                        color: #3A84FF;
                    }
                }
                &.is-select {
                    .icon {
                        color: #3A84FF;
                    }
                }
                &.is-disabled {
                    .icon {
                        color: #DCDEE5;
                    }
                }
                .text {
                    @mixin name-overflow;
                }
                .icon {
                    color: #979BA5;
                    margin-left: 6px;
                }
            }
            .setting-button {
                @mixin layout-flex row, center, center;
                border-radius: 0 2px 2px 0;
                border-left: 0;
                width: 42px;
                outline: 0;
                color: #979BA5;
                &:hover {
                    color: #63656F;
                    border-color: #DCDEE5;
                    background: #f0f1f5;
                }
                &.is-disabled {
                    color: #DCDEE5;
                    background: #FAFBFD;
                }
            }
        }
    }
</style>

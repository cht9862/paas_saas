<template>
    <transition name="slide">
        <section class="cloud-area-setting" v-show="value">
            <div class="cloud-area">
                <!--云区域分组-->
                <div class="cloud-area-group">
                    <area-filter-panel type="edit" default-expand @hideItem="handleHideAreaItem" :list="list"></area-filter-panel>
                </div>
                <!--隐藏区域-->
                <div class="cloud-area-hide mt20">
                    <div class="hide-title">
                        {{ `${$t('隐藏云区域')}（${hideCount}/${totalCount}）` }}
                    </div>
                    <div class="hide-item" v-if="hideList.length">
                        <div class="item-col" v-for="(col, index) in colNum" :key="index">
                            <div v-for="(item, i) in colItemNum" :key="i" class="row">
                                <i class="nodeman-icon nc-increase-2"
                                    v-if="hideList[i + index * colItemNum]"
                                    @click="handleAddHideArea(hideList[i + index * colItemNum])">
                                </i>
                                <span v-if="hideList[i + index * colItemNum]" class="row-name" :title="hideList[i + index * colItemNum].name">{{ hideList[i + index * colItemNum].name }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="hide-empty" v-else>
                        {{ $t('暂无被隐藏的云区域从展示区点') }}
                        <i class="bk-icon icon-close-circle-shape"></i>
                        {{ $t('即可隐藏') }}
                    </div>
                </div>
                <!--保存和取消-->
                <div class="cloud-area-footer mt30">
                    <bk-button theme="primary" class="nodeman-primary-btn" @click="handleSave">{{ $t('保存') }}</bk-button>
                    <bk-button @click="handleCancel" class="nodeman-cancel-btn ml10">{{ $t('取消') }}</bk-button>
                </div>
            </div>
        </section>
    </transition>
</template>
<script>
    import { mapGetters, mapMutations } from 'vuex'
    import { SET_AREA_LIST } from '@/store/modules/agent'
    import AreaFilterPanel from './area-filter-panel'

    export default {
        name: 'area-filter-setting',
        components: {
            AreaFilterPanel
        },
        model: {
            prop: 'value',
            event: 'update'
        },
        props: {
            value: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                colItemNum: 3, // 一列个数
                list: [], // 云区域
                hideList: [], // 隐藏区域
                totalCount: 0 // 区域总个数
            }
        },
        computed: {
            ...mapGetters('agent', ['area']),
            // 隐藏区域个数
            hideCount () {
                return this.hideList.length
            },
            // // 总区域个数
            // totalCount () {
            //     return this.area.hideList.length + this.area.list.length - 1
            // },
            // 列数
            colNum () {
                return Math.ceil(this.hideCount / this.colItemNum)
            }
        },
        watch: {
            value: {
                handler (v) {
                    if (v) {
                        this.list = this.cloneList(this.area.list)
                        this.hideList = this.cloneList(this.area.hideList)
                        this.totalCount = this.area.hideList.length + this.area.list.length
                    }
                },
                immediate: true
            }
        },
        methods: {
            ...mapMutations('agent', [SET_AREA_LIST]),
            /**
             * 保存操作
             */
            handleSave () {
                this[SET_AREA_LIST]({
                    list: this.list,
                    hideList: this.hideList
                })
                this.$emit('update', false)
            },
            /**
             * 取消操作
             */
            handleCancel () {
                this.$emit('update', false)
            },
            /**
             * 隐藏区域
             */
            handleHideAreaItem (obj) {
                const index = this.list.findIndex(item => item.id === obj.id)
                this.list.splice(index, 1)
                this.hideList.push(obj)
            },
            /**
             * 显示区域
             */
            handleAddHideArea (obj) {
                const index = this.hideList.findIndex(item => item.id === obj.id)
                this.hideList.splice(index, 1)
                this.list.push(obj)
            },
            cloneList (data) {
                return JSON.parse(JSON.stringify(data))
            }
        }
    }
</script>
<style lang="postcss" scoped>
    @import '@/css/transition.css';
    @import '@/css/mixins/nodeman.css';

    @define-mixin area-btn {
        padding: 0 4px 0 10px;
        height: 38px;
        line-height: 38px;
        font-size: 14px;
        border: 1px dashed #C4C6CC;
        background: #FAFBFD;
        cursor: pointer;
        border-radius: 2px;
        &.is-disabled {
            border: 1px solid #DCDEE5;
            color: #DCDEE5;
            cursor: not-allowed;
        }
    }
    .cloud-area-setting {
        position: fixed;
        top: 52px;
        right: 0;
        bottom: 0;
        left: 0;
        background-color: rgba(0, 0, 0, .6);
        z-index: 10;
        overflow-y: auto;
    }
    .cloud-area {
        top: 0;
        background-color: #fff;
        overflow-y: auto;
        padding: 20px 60px 30px 60px;
        &-hide {
            .hide-title {
                font-size: 14px;
                color: #313238;
            }
            .hide-item {
                @mixin layout-flex row, stretch, flex-start, wrap;
                .item-icon {
                    font-size: 16px;
                    color: #C4C6CC;
                }
                .item-col {
                    margin-top: 18px;
                    flex-basis: 200px;
                    font-size: 14px;
                    line-height: 1;
                    .row {
                        @mixin layout-flex row, center;
                        max-width: 200px;
                        &:not(:first-child) {
                            margin-top: 16px;
                        }
                        .row-name {
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        }
                        i {
                            margin-right: 8px;
                            font-size: 20px;
                            color: #C4C6CC;
                            cursor: pointer;
                            &:hover {
                                color: #3A84FF;
                            }
                        }
                    }
                }
            }
            .hide-empty {
                @mixin layout-flex row, center;
                margin-top: 12px;
                color: #979BA5;
                i {
                    margin: 0 4px;
                    color: #C4C6CC;
                }
            }
        }
        &-footer {
            @mixin layout-flex row;
        }
    }
</style>

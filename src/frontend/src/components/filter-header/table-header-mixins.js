
import FilterHeader from '@/components/filter-header/filter-header'
import { toLine } from '@/common/util'

export default {
  data() {
    return {
      filterData: [],
      // search select绑定值
      searchSelectValue: []
    }
  },
  computed: {
    searchSelectData() { // search select数据源
      const ids = this.searchSelectValue.map(item => item.id)
      return this.filterData.filter(item => !ids.includes(item.id))
    },
    headerData() { // 表头筛选列表数据源
      return this.filterData.reduce((obj, item) => {
        if (item.children && item.children.length) {
          obj[item.id] = item.children
        }
        return obj
      }, {})
    }
  },
  methods: {
    // 自定筛选表头
    renderFilterHeader(h, data) {
      const filterList = this.headerData[data.column.property] || this.headerData[toLine(data.column.property)] || []
      const item = this.filterData.find((item) => {
        const { property } = data.column
        return item.id === property || item.id === toLine(property)
      }) || {}
      const title = data.column.label || ''
      const property = data.column.property || ''

      return <FilterHeader
                name={ title } property={ property } filterList={ filterList }
                onConfirm={ (prop, list) => this.handleFilterHeaderConfirm(prop, list) }
                onReset={ prop => this.handleFilterHeaderReset(prop) }
                showSearch={ !!item.showSearch }
                checkAll={ !!item.showCheckAll }
                width={ item.width }
                align={ item.align }>
            </FilterHeader>
    },
    /**
         * search select输入框信息变更
         */
    handleSearchSelectChange(list) {
      this.filterData.forEach((data) => {
        const item = list.find(item => item.id === data.id)
        if (data.children) {
          data.children = data.children.map((child) => {
            if (!item) {
              child.checked = false
            } else {
              child.checked = item.values.some(value => value.id === child.id)
            }
            return child
          })
        }
      })
    },
    // 表头筛选清空
    handleFilterHeaderReset(prop) {
      const index = this.searchSelectValue.findIndex(item => item.id === prop)
      if (index > -1) {
        this.searchSelectValue.splice(index, 1)
      }
    },
    // 表头筛选变更
    handleFilterHeaderConfirm(prop, list) {
      const index = this.searchSelectValue.findIndex(item => item.id === prop || item.id === toLine(prop))
      const values = list.reduce((pre, item) => {
        if (item.checked) {
          pre.push({
            id: item.id,
            name: item.name
          })
        }
        return pre
      }, [])
      if (index > -1) {
        // 已经存在就覆盖
        this.searchSelectValue[index].values = values
      } else {
        const data = this.filterData.find(data => data.id === prop || data.id === toLine(prop))
        // 不存在就添加
        this.searchSelectValue.push({
          id: prop,
          name: data ? data.name : '',
          values
        })
      }
    },
    handlePushValue(prop, values, merged = true) {
      if (!values || !Array.isArray(values)) return
      const index = this.searchSelectValue.findIndex(item => item.id === prop || item.id === toLine(prop))
      if (index > -1) {
        const originValues = merged ? this.searchSelectValue[index].values || [] : []
        values.forEach((value) => {
          const isExist = originValues.some(item => item && item.id === value.id)
          if (!isExist) {
            originValues.push(value)
          }
        })
        this.searchSelectValue[index].values = originValues
      } else if (prop) {
        const data = this.filterData.find(data => data.id === prop || data.id === toLine(prop))
        this.searchSelectValue.push({
          id: prop,
          name: data ? data.name : '',
          values
        })
      }
    }
  }
}

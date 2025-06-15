<template>
  <div class="mobile-stock">
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索食材"
        size="large"
        clearable
      >
        <template #append>
          <el-button :icon="Search" />
        </template>
      </el-input>
    </div>

    <div class="stock-list">
      <div 
        v-for="item in filteredStock" 
        :key="item.id" 
        class="stock-item"
        @click="showDetail(item)"
      >
        <div class="item-name">{{ item.name }}</div>
        <div class="item-info">
          <span class="item-category">{{ item.category }}</span>
          <span class="item-quantity">{{ item.quantity }}{{ item.unit }}</span>
        </div>
      </div>
    </div>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30]"
        layout="prev, pager, next"
        :total="totalItems"
        small
      />
    </div>

    <el-drawer
      v-model="drawerVisible"
      title="库存详情"
      direction="btt"
      size="70%"
    >
      <div class="detail-content" v-if="currentItem">
        <h3>{{ currentItem.name }}</h3>
        <div class="detail-row">
          <span class="label">分类:</span>
          <span>{{ currentItem.category }}</span>
        </div>
        <div class="detail-row">
          <span class="label">库存量:</span>
          <span>{{ currentItem.quantity }}{{ currentItem.unit }}</span>
        </div>
        <div class="detail-row">
          <span class="label">最后更新:</span>
          <span>{{ currentItem.lastUpdate }}</span>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(100)
const drawerVisible = ref(false)
const currentItem = ref(null)

// 模拟库存数据
const stockData = ref([
  {
    id: 1,
    name: '大米',
    category: '主食',
    quantity: 500,
    unit: 'kg',
    lastUpdate: '2023-05-01 08:30'
  },
  {
    id: 2,
    name: '食用油',
    category: '调味品',
    quantity: 30,
    unit: '桶',
    lastUpdate: '2023-05-02 10:15'
  },
  // 更多模拟数据...
])

const filteredStock = computed(() => {
  return stockData.value.filter(item =>
    item.name.includes(searchQuery.value) ||
    item.category.includes(searchQuery.value)
  )
})

const showDetail = (item) => {
  currentItem.value = item
  drawerVisible.value = true
}
</script>

<style scoped>
.mobile-stock {
  padding: 10px;
}
.search-bar {
  margin-bottom: 15px;
}
.stock-list {
  margin-bottom: 15px;
}
.stock-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
}
.item-name {
  font-weight: bold;
  margin-bottom: 5px;
}
.item-info {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 14px;
}
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}
.detail-content {
  padding: 20px;
}
.detail-row {
  margin: 15px 0;
  display: flex;
}
.detail-row .label {
  width: 80px;
  color: #888;
}
</style>
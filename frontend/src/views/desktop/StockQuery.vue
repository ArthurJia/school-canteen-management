<template>
  <div class="stock-query">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span>库存查询</span>
          <div class="header-actions">
            <el-input
              v-model="searchQuery"
              placeholder="输入食材名称查询"
              style="width: 300px"
              clearable
            >
              <template #append>
                <el-button :icon="Search" />
              </template>
            </el-input>
            <el-button type="primary" :icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredStock" border style="width: 100%">
        <el-table-column prop="name" label="食材名称" width="180" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="quantity" label="库存量" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="lastUpdate" label="最后更新时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)"
              >详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalItems"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'

const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(100)

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

const handleEdit = row => {
  console.log('编辑行:', row)
}
</script>

<style scoped>
.stock-query {
  padding: 20px;
}
.query-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}
.header-actions {
  display: flex;
  gap: 10px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
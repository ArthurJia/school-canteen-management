<template>
  <div class="stock-query">
    <el-card class="query-card">
      <template #header>
        <div class="card-header">
          <span>库存查询</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 350px"
              @change="fetchStockData"
            />
            <el-input
              v-model="searchQuery"
              placeholder="输入食材名称查询"
              style="width: 300px"
              clearable
            >
              <template #append>
                <el-button :icon="Search" @click="fetchStockData" />
              </template>
            </el-input>
            <el-button type="primary" :icon="Refresh" @click="fetchStockData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredStock" border style="width: 100%" v-loading="loading">
        <el-table-column prop="in_time" label="入库时间" width="180" sortable>
          <template #default="{row}">
            {{ formatDate(row.in_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="食材名称" width="150" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column prop="quantity" label="数量" width="100" align="right">
          <template #default="{row}">
            {{ row.quantity }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价(元)" width="120" align="right">
          <template #default="{row}">
            {{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="subtotal" label="小计(元)" width="120" align="right">
          <template #default="{row}">
            {{ row.subtotal.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">详情</el-button>
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
          @current-change="fetchStockData"
          @size-change="fetchStockData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)
const loading = ref(false)
const stockData = ref([])

const fetchStockData = async () => {
  try {
    loading.value = true
    let url = '/api/stock-ins?'
    
    if (dateRange.value && dateRange.value.length === 2) {
      const [startTime, endTime] = dateRange.value
      url += `startTime=${startTime}&endTime=${endTime}&`
    }
    
    url += `page=${currentPage.value}&pageSize=${pageSize.value}`
    
    if (searchQuery.value) {
      url += `&search=${searchQuery.value}`
    }

    const response = await axios.get(url)
    stockData.value = response.data.data || []
    totalItems.value = response.data.total || 0
  } catch (error) {
    console.error('获取库存数据失败:', error)
    ElMessage.error('获取库存数据失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const filteredStock = computed(() => {
  return stockData.value.filter(item =>
    item.name.includes(searchQuery.value) ||
    item.category.includes(searchQuery.value) ||
    item.supplier?.includes(searchQuery.value)
  )
})

const handleEdit = row => {
  console.log('编辑行:', row)
}

onMounted(() => {
  fetchStockData()
})
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
  align-items: center;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
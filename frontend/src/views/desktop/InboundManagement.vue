<template>
  <div class="inbound-management">
    <el-card class="form-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>食材入库</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="入库日期" required>
              <el-date-picker
                v-model="form.stockInDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="备注">
              <el-input v-model="form.note" type="textarea" :rows="1" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="食材名称" required>
              <el-input
                v-model="form.name"
                placeholder="请输入食材名称"
                @change="handleIngredientInput"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分类" required>
              <el-select v-model="form.category" placeholder="请选择食材分类">
                <el-option-group
                  v-for="group in categories"
                  :key="group.label"
                  :label="group.label"
                >
                  <el-option
                    v-for="item in group.options"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-option-group>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商" required>
              <el-select v-model="form.supplier" placeholder="请选择供应商">
                <el-option
                  v-for="supplier in suppliers"
                  :key="supplier.value"
                  :label="supplier.label"
                  :value="supplier.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量" required>
              <el-input 
                v-model="form.quantity" 
                type="number"
                :min="1"
                placeholder="请输入数量"
                style="width: 60%"
              />
              <el-select v-model="form.unit" placeholder="单位" style="width: 38%; margin-left: 2%">
                <el-option label="千克(kg)" value="kg" />
                <el-option label="升(L)" value="L" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价(元)" required>
              <el-input 
                v-model="form.price" 
                type="number"
                :min="0"
                :step="0.01"
                placeholder="请输入单价"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="小计(元)">
              <el-input :value="subtotal" readonly />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">一键入库</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="today-records card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>今日入库记录</span>
          <el-button type="primary" link @click="refreshTodayRecords">刷新</el-button>
        </div>
      </template>
      
      <el-table 
        :data="todayRecords" 
        style="width: 100%" 
        stripe
        :max-height="todayRecordsMaxHeight"
        class="today-records-table"
      >
        <el-table-column label="入库时间">
          <template #default="scope">
            {{ formatDateTime(scope.row.in_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="食材名称" />
        <el-table-column prop="category_label" label="分类" />
        <el-table-column prop="supplier_label" label="供应商" />
        <el-table-column label="数量">
          <template #default="scope">
            {{ scope.row.quantity }} {{ scope.row.unit === 'kg' ? '千克' : '升' }}
          </template>
        </el-table-column>
        <el-table-column prop="price" label="单价(元)" />
        <el-table-column prop="subtotal" label="小计(元)" />
        <el-table-column prop="note" label="备注" />
      </el-table>
    </el-card>

    <div class="totals-row cards-flex">
      <el-card class="totals-card card-hover card-glow">
        <template #header>
          <div class="card-header">
            <span>今日分类价格总计</span>
            <el-button type="primary" link @click="fetchTodayCategoryTotals">刷新</el-button>
          </div>
        </template>
        
        <div>
          <el-table :data="todayCategoryTotals" style="width: 100%" stripe>
            <el-table-column prop="category" label="分类">
              <template #default="scope">
                {{ categories.flatMap(group => group.options).find(opt => opt.value === scope.row.category)?.label || scope.row.category }}
              </template>
            </el-table-column>
            <el-table-column prop="total" label="总计(元)">
              <template #default="scope">
                {{ scope.row.total.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
          <div class="total-sum">
            总计金额：{{ todayTotalSum.toFixed(2) }} 元
          </div>
        </div>
      </el-card>

      <el-card class="totals-card card-hover card-glow">
        <template #header>
          <div class="card-header">
            <span>本月分类价格总计</span>
            <el-button type="primary" link @click="fetchMonthCategoryTotals">刷新</el-button>
          </div>
        </template>
        
        <div>
          <el-table :data="monthCategoryTotals" style="width: 100%" stripe>
            <el-table-column prop="category" label="分类">
              <template #default="scope">
                {{ categories.flatMap(group => group.options).find(opt => opt.value === scope.row.category)?.label || scope.row.category }}
              </template>
            </el-table-column>
            <el-table-column prop="total" label="总计(元)">
              <template #default="scope">
                {{ scope.row.total.toFixed(2) }}
              </template>
            </el-table-column>
          </el-table>
          <div class="total-sum">
            总计金额：{{ monthTotalSum.toFixed(2) }} 元
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createStockIn, getStockIns, getTodayCategoryTotals, getMonthCategoryTotals, getAllMonthlySuppliers, createStockOut } from '@/api'

// 设置今日入库记录表格的最大高度，约为8行记录的高度（每行40px）
const todayRecordsMaxHeight = 320 // 8行 * 40px = 320px

// 格式化日期时间（只显示年月日）
const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return ''
  try {
    const date = new Date(dateTimeStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch (error) {
    console.error('日期格式化错误:', error)
    return dateTimeStr
  }
}

const todayRecords = ref([])
const todayCategoryTotals = ref([])
const monthCategoryTotals = ref([])
const monthlySuppliers = ref([]) // 存储历史每月供应商记录

// 计算今日分类价格总计和
const todayTotalSum = computed(() => {
  return todayCategoryTotals.value.reduce((sum, item) => sum + item.total, 0)
})

// 计算本月分类价格总计和
const monthTotalSum = computed(() => {
  return monthCategoryTotals.value.reduce((sum, item) => sum + item.total, 0)
})

// 获取今日入库记录
const fetchTodayRecords = async () => {
  try {
    // 获取当前日期（使用本地时区）
    const today = new Date()
    // 格式化为YYYY-MM-DD格式，确保使用本地时区
    const dateStr = today.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).replace(/\//g, '-')
    
    console.log(`获取今日入库记录: date=${dateStr}`)
    const response = await getStockIns({ startTime: dateStr, endTime: dateStr })
    
    if (!response.data) {
      console.error('API返回数据格式不正确:', response)
      ElMessage.warning('获取数据格式不正确')
      todayRecords.value = []
      return
    }
    
    todayRecords.value = response.data.map(record => ({
      ...record,
      category_label: categories.value.flatMap(group => group.options).find(opt => opt.value === record.category)?.label || record.category,
      supplier_label: suppliers.value.find(s => s.value === record.supplier)?.label || record.supplier,
      subtotal: (record.quantity * record.price).toFixed(2)
    }))
  } catch (error) {
    console.error('获取今日入库记录失败:', error)
    ElMessage.error('获取今日入库记录失败')
  }
}

// 刷新今日记录
const refreshTodayRecords = () => {
  fetchTodayRecords()
}

// 获取今日分类价格总计
const fetchTodayCategoryTotals = async () => {
  try {
    const response = await getTodayCategoryTotals()
    todayCategoryTotals.value = response.data
    console.log('今日分类价格总计:', todayCategoryTotals.value)
  } catch (error) {
    console.error('获取今日分类价格总计失败:', error)
    ElMessage.error(error.message || '获取今日分类价格总计失败')
  }
}

// 获取本月分类价格总计
const fetchMonthCategoryTotals = async () => {
  try {
    const response = await getMonthCategoryTotals()
    monthCategoryTotals.value = response.data
    console.log('本月分类价格总计:', monthCategoryTotals.value)
  } catch (error) {
    console.error('获取本月分类价格总计失败:', error)
    ElMessage.error(error.message || '获取本月分类价格总计失败')
  }
}

// 获取今天的日期，格式为YYYY-MM-DD
const getTodayDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const form = ref({
  id: null, // 食材ID
  name: '',
  category: '',
  supplier: '',
  quantity: 0,
  price: 0,
  unit: 'kg', // 默认单位为千克
  note: '',
  selectedIngredient: null, // 新增选择器绑定
  stockInDate: getTodayDate() // 默认为今天的日期
})

// 获取历史每月供应商记录
const fetchMonthlySuppliers = async () => {
  try {
    const response = await getAllMonthlySuppliers()
    monthlySuppliers.value = response.data
    console.log('历史每月供应商记录:', monthlySuppliers.value)
  } catch (error) {
    console.error('获取历史每月供应商记录失败:', error)
    ElMessage.error('获取历史每月供应商记录失败')
  }
}

// 根据入库日期和分类自动选择供应商
const updateSupplierByDateAndCategory = () => {
  if (!form.value.stockInDate || !form.value.category) return
  
  // 从入库日期中提取年月
  const date = new Date(form.value.stockInDate)
  const year = date.getFullYear()
  const month = date.getMonth() + 1 // JavaScript月份从0开始
  
  // 在历史每月供应商记录中查找匹配的供应商
  const matchedSupplier = monthlySuppliers.value.find(supplier => {
    return supplier.year === year && 
           supplier.month === month && 
           supplier.supplyItems && 
           supplier.supplyItems.includes(form.value.category)
  })
  
  if (matchedSupplier) {
    // 找到匹配的供应商，更新表单
    const supplierOption = suppliers.value.find(s => s.label === matchedSupplier.name)
    if (supplierOption) {
      form.value.supplier = supplierOption.value
      console.log(`根据日期(${year}-${month})和分类(${form.value.category})自动选择供应商: ${matchedSupplier.name}`)
    }
  }
}

// 组件挂载时获取今日记录和分类总计
onMounted(() => {
  fetchTodayRecords()
  fetchTodayCategoryTotals()
  fetchMonthCategoryTotals()
  fetchMonthlySuppliers()
})

const handleIngredientInput = () => {
  // 这里可以添加自动完成或验证逻辑
  if (!form.value.name) {
    form.value.id = null
    form.value.category = ''
    form.value.supplier = ''
  }
}

// 监听入库日期和分类变化，自动选择供应商
watch(() => [form.value.stockInDate, form.value.category], () => {
  updateSupplierByDateAndCategory()
}, { deep: true })

const subtotal = computed(() => {
  return (form.value.quantity * form.value.price).toFixed(2)
})

// 当天类食材和储存类食材的分类
const dailyCategories = [
  { value: 'vegetable', label: '蔬菜类' },
  { value: 'meat', label: '鲜肉类' },
  { value: 'frozen', label: '冷冻类' },
  { value: 'tofu', label: '豆制品类' },
  { value: 'egg', label: '禽蛋类' },
  { value: 'fruit', label: '水果类' },
  { value: 'dessert', label: '点心类' },
  { value: 'flour', label: '面粉制品' }
]

const storageCategories = [
  { value: 'rice', label: '大米' },
  { value: 'oil', label: '食用油类' },
  { value: 'seasoning', label: '调味品类' }
]

const categories = ref([
  {
    label: '当天类食材',
    options: dailyCategories
  },
  {
    label: '储存类食材',
    options: storageCategories
  }
])

// 判断是否为当天类食材
const isDailyCategory = (category) => {
  return dailyCategories.some(item => item.value === category)
}

const suppliers = ref([
  { value: 'maidelong', label: '麦德龙' },
  { value: 'hetianyu', label: '禾田裕' },
  { value: 'tianyuan', label: '天源' },
  { value: 'hejiahuang', label: '合家欢' },
  { value: 'yurun', label: '雨润' },
  { value: 'zhonghe', label: '中合' },
  { value: 'zhongxin', label: '中鑫' },
  { value: 'suhe', label: '苏合' },
  { value: 'huacheng', label: '华诚' },
  { value: 'xuezihan', label: '学子膳' },
  { value: 'yaozhiwei', label: '肴之味' },
  { value: 'yuanwei', label: '原味' },
  { value: 'huihai', label: '汇海' },
  { value: 'zuming', label: '祖名' },
  { value: 'yafu', label: '亚夫' },
  { value: 'longmen', label: '龙门' },
  { value: 'weigang', label: '卫岗' },
  { value: 'tiangu', label: '天谷' },
  { value: 'sushi', label: '苏食' },
  { value: 'hengshun', label: '恒顺' },
  { value: 'zhongrun', label: '中润' },
  { value: 'guoguo', label: '果果' },
  { value: 'furun', label: '富润' }
])

const handleSubmit = async () => {
  // 表单验证
  if (!form.value.name) {
    ElMessage.error('请输入食材名称')
    return
  }
  if (!form.value.category) {
    ElMessage.error('请选择食材分类')
    return
  }
  if (!form.value.supplier) {
    ElMessage.error('请选择供应商')
    return
  }
  if (!form.value.quantity || form.value.quantity <= 0) {
    ElMessage.error('请输入有效的入库数量')
    return
  }
  if (!form.value.price || form.value.price <= 0) {
    ElMessage.error('请输入有效的单价')
    return
  }
  if (!form.value.unit) {
    ElMessage.error('请选择单位')
    return
  }

  try {
    // 发送API请求
    const payload = {
      name: form.value.name,
      category: form.value.category,
      supplier: form.value.supplier,
      quantity: Number(form.value.quantity),
      price: Number(Number(form.value.price).toFixed(2)), // 确保价格保留两位小数
      unit: form.value.unit,
      note: form.value.note,
      is_daily: isDailyCategory(form.value.category),
      subtotal: Number(subtotal.value), // 添加小计金额
      stockInDate: form.value.stockInDate // 添加入库日期
    }
    console.log('发送入库请求数据:', payload)
    
    const result = await createStockIn(payload)
    
    // 如果是当天类食材，自动创建出库记录
    if (isDailyCategory(form.value.category)) {
      try {
        const outPayload = {
          ...payload,
          stockOutDate: payload.stockInDate // 使用相同的日期
        }
        await createStockOut(outPayload)
        ElMessage.success('入库成功，当天类食材已自动出库')
      } catch (outError) {
        console.error('自动出库失败:', outError)
        ElMessage.warning('入库成功，但自动出库失败: ' + (outError.message || '未知错误'))
      }
    } else {
      ElMessage.success('入库成功')
    }
    
    // 清空表单
    form.value = {
      id: null,
      name: '',
      category: '',
      supplier: '',
      quantity: 0,
      price: 0,
      unit: 'kg',
      note: '',
      selectedIngredient: null,
      stockInDate: getTodayDate() // 重置为今天的日期
    }
    
    // 刷新今日入库记录和价格总计
    fetchTodayRecords()
    fetchTodayCategoryTotals()
    fetchMonthCategoryTotals()
  } catch (error) {
    console.error('入库错误:', error)
    ElMessage.error(error.message || '入库失败，请检查网络连接或联系管理员')
  }
}
</script>

<style scoped>
.inbound-management {
  padding: 20px;
}
.form-card {
  margin-bottom: 20px;
}
.today-records {
  margin-top: 20px;
}

/* 今日入库记录表格样式 */
.today-records-table {
  /* 确保表格内容超出时显示滚动条 */
  overflow: auto;
}

/* 自定义滚动条样式 */
:deep(.today-records-table .el-scrollbar__bar) {
  opacity: 0.3;
}

:deep(.today-records-table .el-scrollbar__bar:hover) {
  opacity: 0.8;
}

/* 确保表头固定 */
:deep(.today-records-table .el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #fff;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}
/* 减少表单项之间的间距 */
:deep(.el-form-item) {
  margin-bottom: 15px;
}
/* 调整表格样式 */
:deep(.el-table) {
  margin-top: 10px;
}
/* 总计卡片行样式 */
.totals-row {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}
/* 总计卡片样式 */
.totals-card {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}
/* 总计金额样式 */
.total-sum {
  margin-top: 15px;
  text-align: right;
  font-weight: bold;
  font-size: 16px;
  color: #409EFF;
  padding-right: 20px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .totals-row {
    flex-direction: column;
  }
  .totals-card {
    margin-bottom: 20px;
  }
}
</style>
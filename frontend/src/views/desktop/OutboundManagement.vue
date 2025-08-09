<template>
  <div class="outbound-management">
    <!-- 数据统计区域 -->
    <div class="statistics-section">
      <!-- 月份选择器 -->
      <div class="month-selector">
        <el-date-picker v-model="selectedStatMonth" type="month" format="YYYY年MM月" value-format="YYYY-MM"
          placeholder="选择统计月份" @change="calculateUsageStatistics" />
      </div>

      <!-- 统计卡片 -->
      <div class="statistics-cards">
        <el-card class="stat-card card-hover card-glow">
          <div class="stat-content">
            <div class="stat-title">大米使用量</div>
            <div class="stat-value">{{ riceUsage.toFixed(2) }} 元</div>
            <div class="stat-desc">{{ formatSelectedStatMonth }}</div>
          </div>
        </el-card>

        <el-card class="stat-card card-hover card-glow">
          <div class="stat-content">
            <div class="stat-title">食用油类使用量</div>
            <div class="stat-value">{{ oilUsage.toFixed(2) }} 元</div>
            <div class="stat-desc">{{ formatSelectedStatMonth }}</div>
          </div>
        </el-card>

        <el-card class="stat-card card-hover card-glow">
          <div class="stat-content">
            <div class="stat-title">调味品类使用量</div>
            <div class="stat-value">{{ seasoningUsage.toFixed(2) }} 元</div>
            <div class="stat-desc">{{ formatSelectedStatMonth }}</div>
          </div>
        </el-card>
      </div>
    </div>

    <el-card class="form-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>储存类食材出库</span>
        </div>
      </template>

      <el-form :model="storageForm" label-width="120px" v-loading="calculationLoading">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="出库年月" required>
              <el-date-picker v-model="storageForm.outboundMonth" type="month" placeholder="选择年月" format="YYYY年MM月"
                value-format="YYYY-MM" style="width: 100%" @change="handleMonthChange" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="备注">
              <el-input v-model="storageForm.note" type="textarea" :rows="1" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="食材名称" required>
              <el-select v-model="storageForm.ingredientName" placeholder="请选择食材名称" filterable remote
                :remote-method="searchStorageIngredients" :loading="ingredientSearchLoading"
                @change="handleIngredientChange" style="width: 100%">
                <el-option v-for="ingredient in storageIngredientOptions" :key="ingredient.id" :label="ingredient.name"
                  :value="ingredient.name" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="分类">
              <el-input v-model="storageForm.category" readonly placeholder="自动填充" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="供应商">
              <el-input v-model="storageForm.supplier" readonly placeholder="自动填充" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="数量">
              <el-input v-model="storageForm.quantity" readonly placeholder="自动计算" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单价(元)">
              <el-input v-model="storageForm.unitPrice" readonly placeholder="自动计算" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="小计(元)">
              <el-input v-model="storageForm.subtotal" readonly placeholder="自动计算" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="handleStorageOutbound" :disabled="!canSubmit">一键出库</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="all-records card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>所有出库记录</span>
          <el-button type="primary" link @click="refreshAllRecords">刷新</el-button>
        </div>
      </template>

      <el-table :data="allRecords" style="width: 100%" stripe v-loading="recordsLoading" class="all-records-table">
        <el-table-column label="出库时间">
          <template #default="scope">
            {{ formatDateTime(scope.row.out_time) }}
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

      <!-- 分页器 -->
      <div class="pagination-container">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
          :total="totalRecords" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createStockOut, getStockOuts, getTodayOutCategoryTotals, getMonthOutCategoryTotals, getAllMonthlySuppliers } from '@/api'
import axios from 'axios'

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

// 出库记录相关数据
const allRecords = ref([])
const recordsLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20) // 默认显示20条记录
const totalRecords = ref(0)
const monthlySuppliers = ref([]) // 存储历史每月供应商记录

// 储存类食材出库相关数据
const storageForm = ref({
  outboundMonth: '',
  note: '',
  ingredientName: '',
  category: '',
  supplier: '',
  quantity: '',
  unitPrice: '',
  subtotal: ''
})

const storageIngredientOptions = ref([])
const ingredientSearchLoading = ref(false)
const calculationLoading = ref(false)

// 计算属性 - 是否可以提交
const canSubmit = computed(() => {
  return storageForm.value.outboundMonth &&
    storageForm.value.ingredientName &&
    storageForm.value.quantity &&
    storageForm.value.subtotal
})

// 统计相关数据
const selectedStatMonth = ref('')
const riceUsage = ref(0)
const oilUsage = ref(0)
const seasoningUsage = ref(0)



// 计算属性 - 格式化选中的统计月份
const formatSelectedStatMonth = computed(() => {
  if (!selectedStatMonth.value) {
    return '请选择月份'
  }
  const [year, month] = selectedStatMonth.value.split('-')
  return `${year}年${month}月`
})

// 获取所有出库记录
const fetchAllRecords = async () => {
  recordsLoading.value = true
  try {
    console.log(`获取所有出库记录: page=${currentPage.value}, pageSize=${pageSize.value}`)
    const response = await getStockOuts({
      page: currentPage.value,
      pageSize: pageSize.value
    })

    if (!response.data) {
      console.error('API返回数据格式不正确:', response)
      ElMessage.warning('获取数据格式不正确')
      allRecords.value = []
      totalRecords.value = 0
      return
    }

    allRecords.value = response.data.map(record => ({
      ...record,
      category_label: categories.value.flatMap(group => group.options).find(opt => opt.value === record.category)?.label || record.category,
      supplier_label: suppliers.value.find(s => s.value === record.supplier)?.label || record.supplier,
      subtotal: (record.quantity * record.price).toFixed(2)
    }))

    totalRecords.value = response.total || 0
  } catch (error) {
    console.error('获取所有出库记录失败:', error)
    ElMessage.error('获取所有出库记录失败')
  } finally {
    recordsLoading.value = false
  }
}

// 刷新所有记录
const refreshAllRecords = () => {
  fetchAllRecords()
}

// 分页器事件处理
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchAllRecords()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchAllRecords()
}

// 储存类食材出库相关函数

// 搜索储存类食材
const searchStorageIngredients = async (query) => {
  if (!query) {
    storageIngredientOptions.value = []
    return
  }

  ingredientSearchLoading.value = true
  try {
    const response = await axios.get('/api/storage-ingredients')
    const allIngredients = response.data.data || []

    // 模糊搜索
    storageIngredientOptions.value = allIngredients.filter(ingredient =>
      ingredient.name.toLowerCase().includes(query.toLowerCase())
    )
  } catch (error) {
    console.error('搜索储存类食材失败:', error)
    ElMessage.error('搜索储存类食材失败')
  } finally {
    ingredientSearchLoading.value = false
  }
}

// 获取分类标签
const getCategoryLabel = (categoryValue) => {
  const categoryMap = {
    'rice': '大米',
    'oil': '食用油类',
    'seasoning': '调味品类'
  }
  return categoryMap[categoryValue] || categoryValue
}

// 处理年月变化
const handleMonthChange = () => {
  if (storageForm.value.ingredientName) {
    calculateStorageOutbound()
  }
}

// 处理食材选择变化
const handleIngredientChange = async () => {
  if (!storageForm.value.ingredientName) {
    resetStorageForm()
    return
  }

  // 获取选中的食材信息
  const selectedIngredient = storageIngredientOptions.value.find(
    ingredient => ingredient.name === storageForm.value.ingredientName
  )

  if (selectedIngredient) {
    // 设置分类
    storageForm.value.category = getCategoryLabel(selectedIngredient.category)

    // 根据年月和分类确定供应商
    await setSupplierByMonthAndCategory()

    // 计算数量、单价和小计
    await calculateStorageOutbound()
  }
}

// 根据年月和分类确定供应商
const setSupplierByMonthAndCategory = async () => {
  if (!storageForm.value.outboundMonth || !storageForm.value.category) {
    return
  }

  const [year, month] = storageForm.value.outboundMonth.split('-')
  const categoryValue = getCategoryValueByLabel(storageForm.value.category)

  // 在历史每月供应商记录中查找匹配的供应商
  const matchedSupplier = monthlySuppliers.value.find(supplier => {
    return supplier.year === parseInt(year) &&
      supplier.month === parseInt(month) &&
      supplier.supplyItems &&
      supplier.supplyItems.includes(categoryValue)
  })

  if (matchedSupplier) {
    storageForm.value.supplier = matchedSupplier.name
  } else {
    storageForm.value.supplier = '未找到匹配供应商'
  }
}

// 获取分类值（英文）
const getCategoryValueByLabel = (label) => {
  const labelMap = {
    '大米': 'rice',
    '食用油类': 'oil',
    '调味品类': 'seasoning'
  }
  return labelMap[label] || 'seasoning'
}

// 计算储存类食材出库数量和金额
const calculateStorageOutbound = async () => {
  if (!storageForm.value.outboundMonth || !storageForm.value.ingredientName) {
    return
  }

  calculationLoading.value = true
  try {
    const [year, month] = storageForm.value.outboundMonth.split('-')
    const currentMonth = `${year}-${month}`
    const prevMonth = getPreviousMonth(currentMonth)

    // 获取月底库存数据
    const inventoryResponse = await axios.get('/api/monthly-inventory')
    const inventoryData = inventoryResponse.data.data || []

    // 获取入库数据
    const stockResponse = await axios.get('/api/stock-ins', {
      params: { pageSize: 1000 }
    })
    const stockData = stockResponse.data.data || []

    // 计算上个月月底库存
    const prevMonthInventory = inventoryData.find(item =>
      item.date === prevMonth && item.name === storageForm.value.ingredientName
    )
    const prevQuantity = prevMonthInventory ? prevMonthInventory.quantity : 0
    const prevAmount = prevMonthInventory ? (prevMonthInventory.unitPrice * prevMonthInventory.quantity) : 0

    // 计算当月月底库存
    const currentMonthInventory = inventoryData.find(item =>
      item.date === currentMonth && item.name === storageForm.value.ingredientName
    )
    const currentQuantity = currentMonthInventory ? currentMonthInventory.quantity : 0
    const currentAmount = currentMonthInventory ? (currentMonthInventory.unitPrice * currentMonthInventory.quantity) : 0

    // 计算当月入库
    const currentMonthStockIn = stockData.filter(item => {
      const itemDate = new Date(item.in_time)
      const itemYearMonth = `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}`
      return itemYearMonth === currentMonth && item.name === storageForm.value.ingredientName
    })

    const stockInQuantity = currentMonthStockIn.reduce((sum, item) => sum + item.quantity, 0)
    const stockInAmount = currentMonthStockIn.reduce((sum, item) => sum + item.subtotal, 0)

    // 计算使用量：上月库存 + 当月入库 - 当月库存
    const usageQuantity = prevQuantity + stockInQuantity - currentQuantity
    const usageAmount = prevAmount + stockInAmount - currentAmount

    // 计算单价：小计/数量
    const unitPrice = usageQuantity > 0 ? (usageAmount / usageQuantity) : 0

    // 设置表单值
    storageForm.value.quantity = Math.max(0, usageQuantity).toFixed(2)
    storageForm.value.unitPrice = unitPrice.toFixed(2)
    storageForm.value.subtotal = Math.max(0, usageAmount).toFixed(2)

  } catch (error) {
    console.error('计算储存类食材出库失败:', error)
    ElMessage.error('计算储存类食材出库失败')
  } finally {
    calculationLoading.value = false
  }
}

// 获取上个月的年月字符串
const getPreviousMonth = (yearMonth) => {
  const [year, month] = yearMonth.split('-').map(Number)
  const date = new Date(year, month - 1, 1) // month - 1 因为JavaScript月份从0开始
  date.setMonth(date.getMonth() - 1) // 减去一个月

  const prevYear = date.getFullYear()
  const prevMonth = String(date.getMonth() + 1).padStart(2, '0')
  return `${prevYear}-${prevMonth}`
}

// 重置储存类食材表单
const resetStorageForm = () => {
  storageForm.value = {
    outboundMonth: storageForm.value.outboundMonth, // 保留年月选择
    note: storageForm.value.note, // 保留备注
    ingredientName: '',
    category: '',
    supplier: '',
    quantity: '',
    unitPrice: '',
    subtotal: ''
  }
}

// 处理储存类食材出库
const handleStorageOutbound = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请完善出库信息')
    return
  }

  try {
    const [year, month] = storageForm.value.outboundMonth.split('-')
    const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate()

    const totalQuantity = parseFloat(storageForm.value.quantity)
    const totalAmount = parseFloat(storageForm.value.subtotal)

    // 获取分类值
    const categoryValue = getCategoryValueByLabel(storageForm.value.category)

    let outboundRecords = []
    let successMessage = ''

    // 判断出库方式：数量少于2时一次性出库，否则分4次出库
    if (totalQuantity < 2) {
      // 一次性出库：在所选年月的最后一天
      outboundRecords = [
        {
          date: `${year}-${month}-${String(lastDay).padStart(2, '0')}`,
          quantity: totalQuantity,
          amount: totalAmount
        }
      ]
      successMessage = '储存类食材出库成功，已创建1条出库记录'
    } else {
      // 分4次出库：原有逻辑
      const quarterQuantity = Math.floor(totalQuantity / 4)
      const quarterAmount = Math.floor(totalAmount / 4)

      // 最后一次出库的数量和金额（包含余数）
      const lastQuantity = totalQuantity - (quarterQuantity * 3)
      const lastAmount = totalAmount - (quarterAmount * 3)

      outboundRecords = [
        {
          date: `${year}-${month}-${String(lastDay).padStart(2, '0')}`,
          quantity: lastQuantity,
          amount: lastAmount
        },
        {
          date: `${year}-${month}-${String(lastDay - 7).padStart(2, '0')}`,
          quantity: quarterQuantity,
          amount: quarterAmount
        },
        {
          date: `${year}-${month}-${String(lastDay - 14).padStart(2, '0')}`,
          quantity: quarterQuantity,
          amount: quarterAmount
        },
        {
          date: `${year}-${month}-${String(lastDay - 21).padStart(2, '0')}`,
          quantity: quarterQuantity,
          amount: quarterAmount
        }
      ]
      successMessage = '储存类食材出库成功，已创建4条出库记录'
    }

    // 创建出库记录
    for (const record of outboundRecords) {
      const outboundData = {
        name: storageForm.value.ingredientName,
        category: categoryValue,
        supplier: getSupplierValue(storageForm.value.supplier),
        quantity: record.quantity,
        price: parseFloat(storageForm.value.unitPrice),
        unit: 'kg', // 储存类食材默认使用千克
        note: storageForm.value.note || `储存类食材出库 - ${storageForm.value.outboundMonth}`,
        is_daily: false, // 储存类食材不是当天类
        subtotal: record.amount,
        stockOutDate: record.date
      }

      await createStockOut(outboundData)
    }

    ElMessage.success(successMessage)

    // 重置表单
    resetStorageForm()

    // 刷新出库记录
    fetchAllRecords()

  } catch (error) {
    console.error('储存类食材出库失败:', error)
    ElMessage.error('储存类食材出库失败：' + error.message)
  }
}

// 获取供应商值（英文）
const getSupplierValue = (supplierName) => {
  const supplier = suppliers.value.find(s => s.label === supplierName)
  return supplier ? supplier.value : 'unknown'
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
  stockOutDate: getTodayDate() // 默认为今天的日期
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

// 根据出库日期和分类自动选择供应商
const updateSupplierByDateAndCategory = () => {
  if (!form.value.stockOutDate || !form.value.category) return

  // 从出库日期中提取年月
  const date = new Date(form.value.stockOutDate)
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

// 计算使用量统计的方法
const calculateUsageStatistics = async () => {
  if (!selectedStatMonth.value) {
    riceUsage.value = 0
    oilUsage.value = 0
    seasoningUsage.value = 0
    return
  }

  try {
    const [year, month] = selectedStatMonth.value.split('-')
    const currentMonth = selectedStatMonth.value
    const prevMonth = getPreviousMonth(selectedStatMonth.value)

    // 获取月底库存数据
    const inventoryResponse = await axios.get('/api/monthly-inventory')
    const inventoryData = inventoryResponse.data.data || []

    // 获取入库数据
    const stockResponse = await axios.get('/api/stock-ins', {
      params: { pageSize: 1000 }
    })
    const stockData = stockResponse.data.data || []

    // 按分类计算使用量统计
    const calculateCategoryUsage = (categoryName, categoryValue) => {
      // 计算上个月月底库存金额（按分类汇总）
      const prevMonthInventory = inventoryData.filter(item =>
        item.date === prevMonth && item.category === categoryName
      )
      const prevAmount = prevMonthInventory.reduce((sum, item) =>
        sum + (item.unitPrice * item.quantity), 0
      )

      // 计算当月月底库存金额（按分类汇总）
      const currentMonthInventory = inventoryData.filter(item =>
        item.date === currentMonth && item.category === categoryName
      )
      const currentAmount = currentMonthInventory.reduce((sum, item) =>
        sum + (item.unitPrice * item.quantity), 0
      )

      // 计算当月入库金额（按分类汇总）
      const currentMonthStockIn = stockData.filter(item => {
        const itemDate = new Date(item.in_time)
        const itemYearMonth = `${itemDate.getFullYear()}-${String(itemDate.getMonth() + 1).padStart(2, '0')}`
        return itemYearMonth === currentMonth && item.category === categoryValue
      })
      const stockInAmount = currentMonthStockIn.reduce((sum, item) => sum + item.subtotal, 0)

      // 计算使用量：上月库存金额 + 当月入库金额 - 当月库存金额
      const usageAmount = prevAmount + stockInAmount - currentAmount
      return Math.max(0, usageAmount)
    }

    // 分别计算三个分类的使用量
    riceUsage.value = calculateCategoryUsage('大米', '大米')
    oilUsage.value = calculateCategoryUsage('食用油类', '食用油类')
    seasoningUsage.value = calculateCategoryUsage('调味品类', '调味品类')

  } catch (error) {
    console.error('计算使用量统计失败:', error)
    ElMessage.error('计算使用量统计失败')
    // 如果API调用失败，设置为0
    riceUsage.value = 0
    oilUsage.value = 0
    seasoningUsage.value = 0
  }
}

// 组件挂载时获取所有记录
onMounted(() => {
  fetchAllRecords()
  fetchMonthlySuppliers()

  // 设置默认统计月份为当前月份
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  selectedStatMonth.value = `${year}-${month}`

  // 设置默认出库年月为当前月份
  storageForm.value.outboundMonth = `${year}-${month}`

  calculateUsageStatistics()
})

const handleIngredientInput = () => {
  // 这里可以添加自动完成或验证逻辑
  if (!form.value.name) {
    form.value.id = null
    form.value.category = ''
    form.value.supplier = ''
  }
}

// 监听出库日期和分类变化，自动选择供应商
watch(() => [form.value.stockOutDate, form.value.category], () => {
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
    ElMessage.error('请输入有效的出库数量')
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
      stockOutDate: form.value.stockOutDate // 添加出库日期
    }
    console.log('发送出库请求数据:', payload)

    const result = await createStockOut(payload)

    ElMessage.success('出库成功')
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
      stockOutDate: getTodayDate() // 重置为今天的日期
    }

    // 刷新所有出库记录
    fetchAllRecords()
  } catch (error) {
    console.error('出库错误:', error)
    ElMessage.error(error.message || '出库失败，请检查网络连接或联系管理员')
  }
}
</script>

<style scoped>
.outbound-management {
  padding: 20px;
}

/* 统计区域样式 */
.statistics-section {
  margin-bottom: 30px;
}

.month-selector {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
}

.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: #ffffff;
  border: none;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border-left: 5px solid #667eea;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stat-card:nth-child(2) {
  border-left: 5px solid #f39c12;
}

.stat-card:nth-child(3) {
  border-left: 5px solid #4facfe;
}

.stat-content {
  padding: 20px;
  text-align: center;
  position: relative;
  z-index: 2;
}

.stat-card:nth-child(1) .stat-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #667eea;
  letter-spacing: 0.5px;
}

.stat-card:nth-child(2) .stat-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #f39c12;
  letter-spacing: 0.5px;
}

.stat-card:nth-child(3) .stat-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #4facfe;
  letter-spacing: 0.5px;
}

.stat-card:nth-child(1) .stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #5a67d8;
  font-family: 'Arial', sans-serif;
  letter-spacing: 1px;
}

.stat-card:nth-child(2) .stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #e67e22;
  font-family: 'Arial', sans-serif;
  letter-spacing: 1px;
}

.stat-card:nth-child(3) .stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #3182ce;
  font-family: 'Arial', sans-serif;
  letter-spacing: 1px;
}

.stat-desc {
  font-size: 15px;
  color: #666666;
  font-weight: 500;
}

.form-card {
  margin-bottom: 20px;
}

.all-records {
  margin-top: 20px;
}

/* 所有出库记录表格样式 */
.all-records-table {
  /* 确保表格内容超出时显示滚动条 */
  overflow: auto;
}

/* 自定义滚动条样式 */
:deep(.all-records-table .el-scrollbar__bar) {
  opacity: 0.3;
}

:deep(.all-records-table .el-scrollbar__bar:hover) {
  opacity: 0.8;
}

/* 确保表头固定 */
:deep(.all-records-table .el-table__header-wrapper) {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #fff;
}

/* 分页器容器样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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


/* 响应式布局 */
@media (max-width: 768px) {
  .outbound-management {
    padding: 10px;
  }

  .statistics-cards {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .stat-content {
    padding: 15px;
  }

  .stat-value {
    font-size: 24px !important;
  }


}

@media (max-width: 1200px) {
  .statistics-cards {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* 卡片动画效果 */
.statistics-section,
.form-card,
.all-records {
  animation: cardFadeIn 0.3s ease-out;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
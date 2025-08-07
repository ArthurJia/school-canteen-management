<template>
  <div class="monthly-inventory">
    <!-- 数据统计区域 -->
    <div class="statistics-section">
      <!-- 月份选择器 -->
      <div class="month-selector">
        <el-date-picker
          v-model="selectedStatMonth"
          type="month"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          placeholder="选择统计月份"
          @change="calculateUsageStatistics"
        />
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

    <!-- 月底库存卡片 -->
    <el-card class="form-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>月底库存</span>
          <el-button type="primary" :icon="Plus" @click="showAddInventoryDialog = true">
            添加库存记录
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="inventoryList" 
        border 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="date" label="时间（年月）" min-width="140" />
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column prop="unit" label="单位" min-width="80" />
        <el-table-column prop="category" label="分类" min-width="120" />
        <el-table-column prop="unitPrice" label="单价（元）" min-width="120" align="right">
          <template #default="{ row }">
            {{ row.unitPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="库存数量" min-width="120" align="right" />
        <el-table-column label="库存金额（元）" min-width="140" align="right">
          <template #default="{ row }">
            {{ (row.unitPrice * row.quantity).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ $index }">
            <el-button size="small" @click="editInventoryItem($index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteInventoryItem($index)">
              删除
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无库存记录" />
        </template>
      </el-table>
    </el-card>

    <!-- 出库分类卡片 -->
    <el-card class="query-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>出库分类</span>
          <el-button type="primary" :icon="Plus" @click="showAddCategoryDialog = true">
            添加分类
          </el-button>
        </div>
      </template>
      
      <el-table 
        :data="categoryList" 
        border 
        style="width: 100%" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="name" label="分类名称" width="200" />
        <el-table-column prop="unit" label="单位" width="120" />
        <el-table-column prop="unitPrice" label="单价（元）" width="120" align="right">
          <template #default="{ row }">
            {{ row.unitPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格" />
        <el-table-column label="操作" width="180">
          <template #default="{ $index }">
            <el-button size="small" @click="editCategory($index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory($index)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无分类数据" />
        </template>
      </el-table>
    </el-card>

    <!-- 添加/编辑库存记录对话框 -->
    <el-dialog 
      v-model="showAddInventoryDialog" 
      :title="editingInventoryIndex !== -1 ? '编辑库存记录' : '添加库存记录'" 
      width="50%"
      @closed="closeAddInventoryDialog"
    >
      <el-form :model="newInventoryItem" :rules="inventoryRules" ref="inventoryFormRef" label-width="120px">
        <el-form-item label="时间（年月）" prop="date">
          <el-date-picker
            v-model="newInventoryItem.date"
            type="month"
            format="YYYY年MM月"
            value-format="YYYY-MM"
            placeholder="选择月份"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-select v-model="newInventoryItem.name" placeholder="请选择分类名称" style="width: 100%">
            <el-option value="">请选择分类名称</el-option>
            <el-option 
              v-for="category in categoryList" 
              :key="category.name" 
              :value="category.name"
              :label="category.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input 
            v-model="newInventoryItem.unit" 
            placeholder="自动填充"
            readonly
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input 
            v-model="newInventoryItem.category" 
            placeholder="自动填充"
            readonly
          />
        </el-form-item>
        <el-form-item label="单价（元）" prop="unitPrice">
          <el-input 
            v-model.number="newInventoryItem.unitPrice" 
            type="number"
            :step="0.01"
            placeholder="自动填充"
            readonly
          />
        </el-form-item>
        <el-form-item label="库存数量" prop="quantity">
          <el-input 
            v-model.number="newInventoryItem.quantity" 
            type="number"
            :step="0.01"
            placeholder="请输入库存数量"
          />
        </el-form-item>
        <el-form-item label="库存金额（元）">
          <el-input 
            :value="(newInventoryItem.unitPrice * newInventoryItem.quantity || 0).toFixed(2)" 
            readonly
            placeholder="自动计算"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeAddInventoryDialog">取消</el-button>
          <el-button type="primary" @click="addOrUpdateInventoryItem">
            {{ editingInventoryIndex !== -1 ? '确认修改' : '确认添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加/编辑分类对话框 -->
    <el-dialog 
      v-model="showAddCategoryDialog" 
      :title="editingCategoryIndex !== -1 ? '编辑分类' : '添加分类'" 
      width="50%"
      @closed="closeAddCategoryDialog"
    >
      <el-form :model="newCategory" :rules="categoryRules" ref="categoryFormRef" label-width="120px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="newCategory.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="newCategory.unit" placeholder="请选择单位" style="width: 100%">
            <el-option label="千克" value="千克" />
            <el-option label="升" value="升" />
          </el-select>
        </el-form-item>
        <el-form-item label="单价（元）" prop="unitPrice">
          <el-input 
            v-model.number="newCategory.unitPrice" 
            type="number"
            :step="0.01"
            placeholder="请输入单价"
          />
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="newCategory.specification" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeAddCategoryDialog">取消</el-button>
          <el-button type="primary" @click="addOrUpdateCategory">
            {{ editingCategoryIndex !== -1 ? '确认修改' : '确认添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const loading = ref(false)
const inventoryList = ref([])
const categoryList = ref([])
const showAddInventoryDialog = ref(false)
const showAddCategoryDialog = ref(false)
const editingCategoryIndex = ref(-1)
const editingInventoryIndex = ref(-1)

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

// 表单引用
const inventoryFormRef = ref(null)
const categoryFormRef = ref(null)

// 新库存记录
const newInventoryItem = ref({
  date: '',
  name: '',
  category: '',
  unitPrice: 0,
  quantity: 0,
  unit: ''
})

// 新分类
const newCategory = ref({
  name: '',
  unit: '千克',
  unitPrice: 0,
  specification: ''
})

// 监听器 - 当选择名称时自动填充分类、单价和单位
watch(() => newInventoryItem.value.name, (newName) => {
  const selectedCategory = categoryList.value.find(cat => cat.name === newName)
  if (selectedCategory) {
    // 根据名称设置分类显示规则
    if (newName === '大米') {
      newInventoryItem.value.category = '大米'
    } else if (newName === '大豆油') {
      newInventoryItem.value.category = '食用油类'
    } else {
      newInventoryItem.value.category = '调味品类'
    }
    newInventoryItem.value.unitPrice = selectedCategory.unitPrice
    newInventoryItem.value.unit = selectedCategory.unit // 自动填充单位
  } else {
    newInventoryItem.value.category = ''
    newInventoryItem.value.unitPrice = 0
    newInventoryItem.value.unit = ''
  }
})

// 表单验证规则
const inventoryRules = {
  date: [
    { required: true, message: '请选择时间', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请选择名称', trigger: 'change' }
  ],
  quantity: [
    { required: true, message: '请输入库存数量', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存数量必须大于等于0', trigger: 'blur' }
  ]
}

const categoryRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请选择单位', trigger: 'change' }
  ],
  unitPrice: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价必须大于等于0', trigger: 'blur' }
  ]
}


// 方法
const loadData = () => {
  try {
    const savedInventory = localStorage.getItem('monthlyInventory')
    const savedCategories = localStorage.getItem('outboundCategories')
    
    if (savedInventory) {
      inventoryList.value = JSON.parse(savedInventory)
    }
    
    if (savedCategories) {
      categoryList.value = JSON.parse(savedCategories)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

const saveData = () => {
  try {
    localStorage.setItem('monthlyInventory', JSON.stringify(inventoryList.value))
    localStorage.setItem('outboundCategories', JSON.stringify(categoryList.value))
  } catch (error) {
    console.error('保存数据失败:', error)
    ElMessage.error('保存数据失败')
  }
}

const addOrUpdateInventoryItem = async () => {
  if (!inventoryFormRef.value) return
  
  inventoryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingInventoryIndex.value !== -1) {
          // 编辑模式
          inventoryList.value[editingInventoryIndex.value] = {
            date: newInventoryItem.value.date,
            name: newInventoryItem.value.name,
            category: newInventoryItem.value.category,
            unitPrice: newInventoryItem.value.unitPrice,
            quantity: newInventoryItem.value.quantity,
            unit: newInventoryItem.value.unit
          }
          ElMessage.success('修改库存记录成功')
        } else {
          // 添加模式
          inventoryList.value.push({
            date: newInventoryItem.value.date,
            name: newInventoryItem.value.name,
            category: newInventoryItem.value.category,
            unitPrice: newInventoryItem.value.unitPrice,
            quantity: newInventoryItem.value.quantity,
            unit: newInventoryItem.value.unit
          })
          ElMessage.success('添加库存记录成功')
        }
        
        saveData()
        closeAddInventoryDialog()
      } catch (error) {
        console.error('操作库存记录失败:', error)
        ElMessage.error('操作库存记录失败')
      }
    }
  })
}

const editInventoryItem = (index) => {
  editingInventoryIndex.value = index
  newInventoryItem.value = { ...inventoryList.value[index] }
  showAddInventoryDialog.value = true
}

const deleteInventoryItem = async (index) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条库存记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    inventoryList.value.splice(index, 1)
    saveData()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addOrUpdateCategory = async () => {
  if (!categoryFormRef.value) return
  
  categoryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingCategoryIndex.value !== -1) {
          // 编辑模式
          categoryList.value[editingCategoryIndex.value] = { ...newCategory.value }
          ElMessage.success('修改分类成功')
        } else {
          // 添加模式
          categoryList.value.push({ ...newCategory.value })
          ElMessage.success('添加分类成功')
        }
        
        saveData()
        closeAddCategoryDialog()
      } catch (error) {
        console.error('操作分类失败:', error)
        ElMessage.error('操作分类失败')
      }
    }
  })
}

const editCategory = (index) => {
  editingCategoryIndex.value = index
  newCategory.value = { ...categoryList.value[index] }
  showAddCategoryDialog.value = true
}

const deleteCategory = async (index) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分类吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    categoryList.value.splice(index, 1)
    saveData()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const closeAddInventoryDialog = () => {
  showAddInventoryDialog.value = false
  editingInventoryIndex.value = -1
  newInventoryItem.value = {
    date: '',
    name: '',
    category: '',
    unitPrice: 0,
    quantity: 0,
    unit: ''
  }
  inventoryFormRef.value?.resetFields()
}

const closeAddCategoryDialog = () => {
  showAddCategoryDialog.value = false
  editingCategoryIndex.value = -1
  newCategory.value = {
    name: '',
    unit: '千克',
    unitPrice: 0,
    specification: ''
  }
  categoryFormRef.value?.resetFields()
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
    
    // 计算当月月底库存金额
    const currentMonthInventory = inventoryList.value.filter(item => item.date === selectedStatMonth.value)
    const currentRiceAmount = currentMonthInventory
      .filter(item => item.category === '大米')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)
    const currentOilAmount = currentMonthInventory
      .filter(item => item.category === '食用油类')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)
    const currentSeasoningAmount = currentMonthInventory
      .filter(item => item.category === '调味品类')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)

    // 计算上个月月底库存金额
    const prevMonth = getPreviousMonth(selectedStatMonth.value)
    const prevMonthInventory = inventoryList.value.filter(item => item.date === prevMonth)
    const prevRiceAmount = prevMonthInventory
      .filter(item => item.category === '大米')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)
    const prevOilAmount = prevMonthInventory
      .filter(item => item.category === '食用油类')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)
    const prevSeasoningAmount = prevMonthInventory
      .filter(item => item.category === '调味品类')
      .reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0)

    // 模拟从库存查询中获取当月入库数据（这里使用模拟数据，实际应该调用API）
    const stockInRiceAmount = 0 // 实际应该从库存查询API获取
    const stockInOilAmount = 0 // 实际应该从库存查询API获取
    const stockInSeasoningAmount = 0 // 实际应该从库存查询API获取

    // 计算使用量：当月库存 + 当月入库 - 上月库存
    riceUsage.value = currentRiceAmount + stockInRiceAmount - prevRiceAmount
    oilUsage.value = currentOilAmount + stockInOilAmount - prevOilAmount
    seasoningUsage.value = currentSeasoningAmount + stockInSeasoningAmount - prevSeasoningAmount

    // 确保使用量不为负数
    riceUsage.value = Math.max(0, riceUsage.value)
    oilUsage.value = Math.max(0, oilUsage.value)
    seasoningUsage.value = Math.max(0, seasoningUsage.value)

  } catch (error) {
    console.error('计算使用量统计失败:', error)
    ElMessage.error('计算使用量统计失败')
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

// 生命周期
onMounted(() => {
  loadData()
  // 设置默认统计月份为当前月份
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  selectedStatMonth.value = `${year}-${month}`
  calculateUsageStatistics()
})
</script>

<style scoped>
.monthly-inventory {
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

/* 减少表单项之间的间距 */
:deep(.el-form-item) {
  margin-bottom: 15px;
}

/* 调整表格样式 */
:deep(.el-table) {
  margin-top: 10px;
}

/* 对话框样式调整 */
:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #e4e7ed;
  border-radius: 12px 12px 0 0;
}

:deep(.el-dialog) {
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

/* 表格行悬浮效果 */
:deep(.el-table tbody tr:hover > td) {
  background-color: #f8f9fa !important;
}

/* 按钮组样式 */
:deep(.el-button-group .el-button) {
  border-radius: 6px;
  transition: all 0.3s ease;
}

:deep(.el-button-group .el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 输入框美化 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 选择器美化 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

/* 日期选择器美化 */
:deep(.el-date-editor.el-input) {
  border-radius: 8px;
}

/* 空状态样式 */
:deep(.el-empty) {
  padding: 40px 0;
}

:deep(.el-empty__description) {
  color: #909399;
  font-size: 14px;
}

/* 表格边框美化 */
:deep(.el-table--border) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table--border::after) {
  display: none;
}

:deep(.el-table--border::before) {
  display: none;
}

/* 表格头部样式 */
:deep(.el-table th.el-table__cell) {
  background: #f8f9fa;
  color: #333;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
}

/* 表格单元格样式 */
:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid #e9ecef;
}

/* 加载状态美化 */
:deep(.el-loading-mask) {
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

/* 消息框美化 */
:deep(.el-message-box) {
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

:deep(.el-message-box__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #e4e7ed;
  border-radius: 12px 12px 0 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .monthly-inventory {
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
    font-size: 24px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table th.el-table__cell),
  :deep(.el-table td.el-table__cell) {
    padding: 8px;
  }
  
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 10px;
  }
  
  :deep(.el-form-item__content) {
    flex-direction: column;
  }
}

@media (max-width: 1200px) {
  .statistics-cards {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
}

/* 卡片动画效果 */
.form-card,
.query-card {
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

/* 按钮悬浮效果增强 */
:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 表格条纹效果 */
:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafafa;
}

/* 表格选中行效果 */
:deep(.el-table__body tr.current-row > td) {
  background-color: #ecf5ff !important;
}
</style>

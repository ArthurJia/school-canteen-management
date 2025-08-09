<template>
  <div class="monthly-inventory">

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

      <el-table :data="paginatedInventoryList" border style="width: 100%" v-loading="loading" stripe>
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
          <template #default="{ row, $index }">
            <el-button size="small" @click="editInventoryItem(row, $index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteInventoryItem(row, $index)">
              删除
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无库存记录" />
        </template>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentInventoryPage"
          v-model:page-size="inventoryPageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="inventoryList.length"
        />
      </div>
    </el-card>

    <!-- 储存类食材明细卡片 -->
    <el-card class="query-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <span>储存类食材明细</span>
          <el-button type="primary" :icon="Plus" @click="showAddIngredientDialog = true">
            添加食材
          </el-button>
        </div>
      </template>

      <el-table :data="paginatedIngredientList" border style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="unit" label="单位" width="120" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryLabel(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="unitPrice" label="单价（元）" width="120" align="right">
          <template #default="{ row }">
            {{ row.unitPrice.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格" />
        <el-table-column label="操作" width="180">
          <template #default="{ row, $index }">
            <el-button size="small" @click="editIngredient(row, $index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteIngredient(row, $index)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无食材数据" />
        </template>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentIngredientPage"
          v-model:page-size="ingredientPageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="ingredientList.length"
        />
      </div>
    </el-card>

    <!-- 添加/编辑库存记录对话框 -->
    <el-dialog v-model="showAddInventoryDialog" :title="editingInventoryIndex !== -1 ? '编辑库存记录' : '添加库存记录'" width="50%"
      @closed="closeAddInventoryDialog">
      <el-form :model="newInventoryItem" :rules="inventoryRules" ref="inventoryFormRef" label-width="120px">
        <el-form-item label="时间（年月）" prop="date">
          <el-date-picker v-model="newInventoryItem.date" type="month" format="YYYY年MM月" value-format="YYYY-MM"
            placeholder="选择月份" style="width: 100%" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-select v-model="newInventoryItem.name" placeholder="请选择食材名称" style="width: 100%">
            <el-option value="">请选择食材名称</el-option>
            <el-option v-for="ingredient in ingredientList" :key="ingredient.name" :value="ingredient.name"
              :label="ingredient.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="newInventoryItem.unit" placeholder="自动填充" readonly />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="newInventoryItem.category" placeholder="自动填充" readonly />
        </el-form-item>
        <el-form-item label="单价（元）" prop="unitPrice">
          <el-input v-model.number="newInventoryItem.unitPrice" type="number" :step="0.01" placeholder="自动填充"
            readonly />
        </el-form-item>
        <el-form-item label="库存数量" prop="quantity">
          <el-input v-model.number="newInventoryItem.quantity" type="number" :step="0.01" placeholder="请输入库存数量" />
        </el-form-item>
        <el-form-item label="库存金额（元）">
          <el-input :value="(newInventoryItem.unitPrice * newInventoryItem.quantity || 0).toFixed(2)" readonly
            placeholder="自动计算" />
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

    <!-- 添加/编辑食材对话框 -->
    <el-dialog v-model="showAddIngredientDialog" :title="editingIngredientIndex !== -1 ? '编辑食材' : '添加食材'" width="50%"
      @closed="closeAddIngredientDialog">
      <el-form :model="newIngredient" :rules="ingredientRules" ref="ingredientFormRef" label-width="120px">
        <el-form-item label="食材名称" prop="name">
          <el-input v-model="newIngredient.name" placeholder="请输入食材名称" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="newIngredient.unit" placeholder="请选择单位" style="width: 100%">
            <el-option label="千克" value="千克" />
            <el-option label="升" value="升" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="newIngredient.category" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="item in storageCategories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="单价（元）" prop="unitPrice">
          <el-input v-model.number="newIngredient.unitPrice" type="number" :step="0.01" placeholder="请输入单价" />
        </el-form-item>
        <el-form-item label="规格" prop="specification">
          <el-input v-model="newIngredient.specification" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeAddIngredientDialog">取消</el-button>
          <el-button type="primary" @click="addOrUpdateIngredient">
            {{ editingIngredientIndex !== -1 ? '确认修改' : '确认添加' }}
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
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const inventoryList = ref([])
const ingredientList = ref([])
const showAddInventoryDialog = ref(false)
const showAddIngredientDialog = ref(false)
const editingIngredientIndex = ref(-1)
const editingInventoryIndex = ref(-1)

// 分页相关
const currentInventoryPage = ref(1)
const inventoryPageSize = ref(10)
const currentIngredientPage = ref(1)
const ingredientPageSize = ref(10)



// 计算属性 - 分页后的库存列表
const paginatedInventoryList = computed(() => {
  const startIndex = (currentInventoryPage.value - 1) * inventoryPageSize.value
  const endIndex = startIndex + inventoryPageSize.value
  return inventoryList.value.slice(startIndex, endIndex)
})

// 计算属性 - 分页后的食材列表
const paginatedIngredientList = computed(() => {
  const startIndex = (currentIngredientPage.value - 1) * ingredientPageSize.value
  const endIndex = startIndex + ingredientPageSize.value
  return ingredientList.value.slice(startIndex, endIndex)
})

// 表单引用
const inventoryFormRef = ref(null)
const ingredientFormRef = ref(null)

// 新库存记录
const newInventoryItem = ref({
  date: '',
  name: '',
  category: '',
  unitPrice: 0,
  quantity: 0,
  unit: ''
})

// 储存类食材分类选项
const storageCategories = [
  { value: 'rice', label: '大米' },
  { value: 'oil', label: '食用油类' },
  { value: 'seasoning', label: '调味品类' }
]

// 新食材
const newIngredient = ref({
  name: '',
  unit: '千克',
  unitPrice: 0,
  specification: '',
  category: 'seasoning'
})

// 获取分类标签的函数
const getCategoryLabel = (categoryValue) => {
  const category = storageCategories.find(item => item.value === categoryValue)
  return category ? category.label : categoryValue
}

// 根据食材名称自动设置分类
const getCategoryByName = (name) => {
  if (!name) return 'seasoning'
  
  const nameLower = name.toLowerCase()
  
  // 大米类
  if (name.includes('大米') || name.includes('米') || nameLower.includes('rice')) {
    return 'rice'
  }
  
  // 食用油类
  if ((name.includes('油') && name.includes('食用')) || name.includes('大豆油') || name.includes('菜籽油') || name.includes('花生油') || name.includes('玉米油') || nameLower.includes('oil')) {
    return 'oil'
  }
  
  // 调味品类（默认）
  return 'seasoning'
}

// 监听器 - 当选择名称时自动填充分类、单价和单位
watch(() => newInventoryItem.value.name, (newName) => {
  const selectedIngredient = ingredientList.value.find(ingredient => ingredient.name === newName)
  if (selectedIngredient) {
    // 使用储存类食材明细中的分类
    newInventoryItem.value.category = getCategoryLabel(selectedIngredient.category)
    newInventoryItem.value.unitPrice = selectedIngredient.unitPrice
    newInventoryItem.value.unit = selectedIngredient.unit // 自动填充单位
  } else {
    newInventoryItem.value.category = ''
    newInventoryItem.value.unitPrice = 0
    newInventoryItem.value.unit = ''
  }
})

// 监听器 - 当输入食材名称时自动设置分类
watch(() => newIngredient.value.name, (newName) => {
  if (newName) {
    newIngredient.value.category = getCategoryByName(newName)
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

const ingredientRules = {
  name: [
    { required: true, message: '请输入食材名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  unit: [
    { required: true, message: '请选择单位', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  unitPrice: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价必须大于等于0', trigger: 'blur' }
  ]
}


// 方法
const loadData = async () => {
  try {
    loading.value = true

    // 加载月底库存数据
    const inventoryResponse = await axios.get('/api/monthly-inventory')
    inventoryList.value = inventoryResponse.data.data || []

// 加载储存类食材明细数据
    const ingredientsResponse = await axios.get('/api/storage-ingredients')
    // 保持原始输入顺序，不进行排序
    ingredientList.value = ingredientsResponse.data.data || []



  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const saveData = () => {
  // 不再需要手动保存，数据通过API实时保存
}

const addOrUpdateInventoryItem = async () => {
  if (!inventoryFormRef.value) return

  inventoryFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingInventoryIndex.value !== -1) {
          // 编辑模式
          const inventoryItem = inventoryList.value[editingInventoryIndex.value]
          await axios.put(`/api/monthly-inventory/${inventoryItem.id}`, {
            date: newInventoryItem.value.date,
            name: newInventoryItem.value.name,
            category: newInventoryItem.value.category,
            unitPrice: newInventoryItem.value.unitPrice,
            quantity: newInventoryItem.value.quantity,
            unit: newInventoryItem.value.unit
          })
          ElMessage.success('修改库存记录成功')
        } else {
          // 添加模式
          await axios.post('/api/monthly-inventory', {
            date: newInventoryItem.value.date,
            name: newInventoryItem.value.name,
            category: newInventoryItem.value.category,
            unitPrice: newInventoryItem.value.unitPrice,
            quantity: newInventoryItem.value.quantity,
            unit: newInventoryItem.value.unit
          })
          ElMessage.success('添加库存记录成功')
        }

        // 重新加载数据
        await loadData()
        closeAddInventoryDialog()
      } catch (error) {
        console.error('操作库存记录失败:', error)
        ElMessage.error('操作库存记录失败')
      }
    }
  })
}

const editInventoryItem = (row, pageIndex) => {
  // 找到该行在完整列表中的真实索引
  const realIndex = inventoryList.value.findIndex(item => item.id === row.id)
  editingInventoryIndex.value = realIndex
  newInventoryItem.value = { ...row }
  showAddInventoryDialog.value = true
}

const deleteInventoryItem = async (row, pageIndex) => {
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

    await axios.delete(`/api/monthly-inventory/${row.id}`)

    // 重新加载数据
    await loadData()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const addOrUpdateIngredient = async () => {
  if (!ingredientFormRef.value) return

  ingredientFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (editingIngredientIndex.value !== -1) {
          // 编辑模式
          const ingredient = ingredientList.value[editingIngredientIndex.value]
          await axios.put(`/api/storage-ingredients/${ingredient.id}`, {
            name: newIngredient.value.name,
            unit: newIngredient.value.unit,
            unitPrice: newIngredient.value.unitPrice,
            specification: newIngredient.value.specification,
            category: newIngredient.value.category
          })
          ElMessage.success('修改食材成功')
        } else {
          // 添加模式
          await axios.post('/api/storage-ingredients', {
            name: newIngredient.value.name,
            unit: newIngredient.value.unit,
            unitPrice: newIngredient.value.unitPrice,
            specification: newIngredient.value.specification,
            category: newIngredient.value.category
          })
          ElMessage.success('添加食材成功')
        }

        // 重新加载数据
        await loadData()
        closeAddIngredientDialog()
      } catch (error) {
        console.error('操作食材失败:', error)
        ElMessage.error('操作食材失败')
      }
    }
  })
}

const editIngredient = (row, pageIndex) => {
  // 找到该行在完整列表中的真实索引
  const realIndex = ingredientList.value.findIndex(item => item.id === row.id)
  editingIngredientIndex.value = realIndex
  newIngredient.value = { ...row }
  showAddIngredientDialog.value = true
}

const deleteIngredient = async (row, pageIndex) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个食材吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await axios.delete(`/api/storage-ingredients/${row.id}`)

    // 重新加载数据
    await loadData()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
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

const closeAddIngredientDialog = () => {
  showAddIngredientDialog.value = false
  editingIngredientIndex.value = -1
  newIngredient.value = {
    name: '',
    unit: '千克',
    unitPrice: 0,
    specification: '',
    category: 'seasoning'
  }
  ingredientFormRef.value?.resetFields()
}



// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.monthly-inventory {
  padding: 20px;
}



.form-card {
  margin-bottom: 20px;
}

.query-card {
  margin-bottom: 20px;
}

/* 分页样式 */
.pagination {
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

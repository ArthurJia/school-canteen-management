<template>
  <div class="supplier-management">
    <!-- 视图切换 -->
    <div class="view-switch">
      <el-radio-group v-model="currentView" @change="handleViewChange">
        <el-radio-button label="all">所有供应商</el-radio-button>
        <el-radio-button label="monthly">每月供应商</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 每月供应商视图 -->
    <template v-if="currentView === 'monthly'">
      <!-- 月份选择器 -->
      <div class="month-selector">
        <el-date-picker
          v-model="selectedDate"
          type="month"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          placeholder="选择月份"
          :locale="zhCn"
          @change="handleMonthChange"
        />
      </div>
      <!-- 当前月份供应商卡片 -->
      <el-card class="monthly-suppliers">
        <template #header>
          <div class="monthly-header">
            <div class="monthly-info">
              <h3>{{ formatSelectedMonth }}每月供应商</h3>
            </div>
          </div>
        </template>

        <div class="monthly-supplier-list">
          <el-empty v-if="monthlySuppliers.length === 0" description="暂无每月供应商" />
          <el-table v-else :data="monthlySuppliers" style="width: 100%">
            <el-table-column prop="name" label="供应商名称" />
            <el-table-column prop="contact" label="联系人" />
            <el-table-column prop="phone" label="联系电话" />
            <!-- 供应商全称列已移除 -->
            <el-table-column prop="supplyItems" label="供应品类">
              <template #default="{ row }">
                {{ formatSupplyItems(row.supplyItems) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click="handleRemoveMonthlySupplier(row)"
                >移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 历史每月供应商卡片 -->
      <el-card class="monthly-suppliers history-suppliers">
        <template #header>
          <div class="monthly-header">
            <div class="monthly-info">
              <h3>历史每月供应商记录</h3>
              <span>共 {{ allMonthlySuppliers.length }} 条记录</span>
            </div>
          </div>
        </template>

                  <el-table :data="allMonthlySuppliers" style="width: 100%">
                    <el-table-column label="供应月份" width="200">
                      <template #default="{ row }">
                        {{ row.year }}年{{ row.month }}月
                      </template>
                    </el-table-column>
                    <el-table-column prop="name" label="供应商名称" />
                    <el-table-column prop="contact" label="联系人" />
                    <el-table-column prop="phone" label="联系电话" />
                    <el-table-column prop="supplyItems" label="供应品类">
                      <template #default="{ row }">
                        {{ formatSupplyItems(row.supplyItems) }}
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                      <template #default="{ row }">
                        <el-button
                          type="danger"
                          size="small"
                          @click="handleRemoveMonthlySupplier(row)"
                        >移除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
      </el-card>
    </template>

    <!-- 年月选择器对话框 -->
    <el-dialog
      v-model="monthPickerVisible"
      title="选择供应月份"
      width="30%"
      destroy-on-close
    >
              <el-date-picker
                v-model="tempSelectedDate"
                type="month"
                format="YYYY年MM月"
                value-format="YYYY-MM"
                style="width: 100%"
                placeholder="请选择月份"
                :locale="zhCn"
              />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="monthPickerVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddMonthlySupplier">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 所有供应商视图 -->
    <template v-if="currentView === 'all'">
      <el-card>
        <template #header>
          <div class="toolbar-content">
            <el-button type="primary" :icon="Plus" @click="handleAdd">新增供应商</el-button>
            <div class="header-actions" style="display: flex; gap: 10px; align-items: center; margin-left: 20px">
              <el-input
                v-model="searchQuery"
                placeholder="输入查询内容"
                style="width: 300px"
                clearable
              >
                <template #append>
                  <el-button :icon="Search" />
                </template>
              </el-input>
              <el-button 
                type="success" 
                :icon="Download"
                @click="handleExportExcel"
              >
                导出Excel
              </el-button>
            </div>
          </div>
        </template>
      <el-table
        v-if="suppliers.length > 0"
        :data="suppliers"
        border
        style="width: 100%"
        v-loading="loading"
      >
        <el-table-column prop="name" label="供应商名称" width="200" />
        <el-table-column prop="fullName" label="供应商全称" width="300" />
        <el-table-column prop="contact" label="联系人" width="150" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column label="供应品类" class-name="supply-items-column">
          <template #default="scope">
            <span style="display: inline-block; min-width: 100px;">
              {{ formatSupplyItems(scope.row?.supplyItems || []) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" class-name="operation-column">
          <template #default="scope">
            <div style="display: flex; gap: 8px;">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
              <el-button 
                v-if="currentView === 'all'"
                size="small" 
                type="success" 
                @click="handleAddMonthlySupplier(scope.row)"
              >设为每月供应商</el-button>
            </div>
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
    </template>

    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑供应商' : '新增供应商'" 
      width="50%"
      @closed="supplierFormRef?.resetFields()"
    >
      <el-form :model="supplierForm" :rules="rules" ref="supplierFormRef" label-width="100px">
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="supplierForm.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="supplierForm.contact" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="supplierForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="供应商全称" prop="fullName">
          <el-input v-model="supplierForm.fullName" placeholder="请输入供应商全称" />
        </el-form-item>
        <el-form-item label="供应品类" prop="supplyItems">
          <el-select
            v-model="supplierForm.supplyItems"
            multiple
            placeholder="请选择供应品类"
          >
            <el-option
              v-for="item in supplyCategories"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Plus, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import * as XLSX from 'xlsx'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { 
  getSuppliers, 
  getSupplierById, 
  createSupplier, 
  updateSupplier, 
  deleteSupplier,
  getMonthlySuppliers,
  getAllMonthlySuppliers,
  addMonthlySupplier,
  deleteMonthlySupplier
} from '@/api'

// 每月供应商状态
const currentView = ref('all')
const selectedDate = ref('')
const monthlySuppliers = ref([])
const allMonthlySuppliers = ref([])

// 计算属性：格式化选中的月份
const formatSelectedMonth = computed(() => {
  if (!selectedDate.value) {
    const now = new Date()
    return `${now.getFullYear()}年${now.getMonth() + 1}月`
  }
  const [year, month] = selectedDate.value.split('-')
  return `${year}年${month}月`
})

// 视图切换处理
const handleViewChange = async (view) => {
  currentView.value = view
  if (view === 'monthly') {
    await fetchMonthlySuppliers()
    await fetchAllMonthlySuppliers()
  }
}

// 月份变更处理
const handleMonthChange = async () => {
  if (currentView.value === 'monthly') {
    await fetchMonthlySuppliers()
  }
}

// 获取每月供应商数据
const fetchMonthlySuppliers = async () => {
  try {
    if (!selectedDate.value) {
      const now = new Date()
      const year = now.getFullYear()
      const month = now.getMonth() + 1
      selectedDate.value = `${year}-${String(month).padStart(2, '0')}`
    }
    
    const [year, month] = selectedDate.value.split('-')
    
    const loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '加载每月供应商数据...'
    })
    
    try {
      const data = await getMonthlySuppliers(year, month)
      monthlySuppliers.value = data.data || []
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    ElMessage.error('获取每月供应商数据失败：' + error.message)
    monthlySuppliers.value = []
  }
}

// 添加每月供应商
const monthPickerVisible = ref(false)
const tempSelectedDate = ref(new Date())
const tempSupplier = ref(null)

const handleAddMonthlySupplier = (supplier) => {
  tempSupplier.value = supplier
  
  // 设置默认日期为当前月份，格式为 YYYY-MM
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  tempSelectedDate.value = `${year}-${month}`
  
  monthPickerVisible.value = true
}

const confirmAddMonthlySupplier = async () => {
  if (!tempSupplier.value) return
  
  try {
    if (!tempSelectedDate.value) {
      const now = new Date()
      const year = now.getFullYear()
      const month = now.getMonth() + 1
      tempSelectedDate.value = `${year}-${String(month).padStart(2, '0')}`
    }
    
    const [year, month] = tempSelectedDate.value.split('-')
    
    const loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '设置每月供应商中...'
    })
    
    try {
      await addMonthlySupplier(tempSupplier.value.id, year, month)
      ElMessage.success(`已将供应商设为${year}年${month}月供应商`)
      monthPickerVisible.value = false
      
      if (currentView.value === 'monthly') {
        await fetchMonthlySuppliers()
        await fetchAllMonthlySuppliers()
      }
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    ElMessage.error('设置每月供应商失败：' + error.message)
  }
}

// 获取所有历史每月供应商
const fetchAllMonthlySuppliers = async () => {
  try {
    const loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '加载历史每月供应商数据...'
    })
    
    try {
      const data = await getAllMonthlySuppliers()
      allMonthlySuppliers.value = data.data || []
      
      // 按年月倒序排序
      allMonthlySuppliers.value.sort((a, b) => {
        if (a.year !== b.year) {
          return b.year - a.year
        }
        return b.month - a.month
      })
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    ElMessage.error('获取历史每月供应商数据失败：' + error.message)
    allMonthlySuppliers.value = []
  }
}

// 移除每月供应商
const handleRemoveMonthlySupplier = async (supplier) => {
  try {
    if (!selectedDate.value) {
      const now = new Date()
      const year = now.getFullYear()
      const month = now.getMonth() + 1
      selectedDate.value = `${year}-${String(month).padStart(2, '0')}`
    }
    
    const [year, month] = selectedDate.value.split('-')

    await ElMessageBox.confirm(
      '确定要移除该每月供应商吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '移除每月供应商中...'
    })
    
    try {
      await deleteMonthlySupplier(supplier.id, year, month)
      ElMessage.success('已移除每月供应商')
      await fetchMonthlySuppliers()
      await fetchAllMonthlySuppliers()
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除每月供应商失败：' + error.message)
    }
  }
}

// 初始化
onMounted(async () => {
  // 设置默认日期为当前月份
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  selectedDate.value = `${year}-${month}`
  
  if (currentView.value === 'monthly') {
    await fetchMonthlySuppliers()
    await fetchAllMonthlySuppliers()
  }
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入供应商名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  contact: [
    { required: true, message: '请输入联系人姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  supplyItems: [
    { required: true, message: '请至少选择一个供应品类', trigger: 'change' }
  ]
}

const searchQuery = ref('')
const isEdit = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalItems = ref(0)
const dialogVisible = ref(false)
const supplierFormRef = ref(null)

const resetForm = () => {
  supplierForm.value = {
    name: '',
    contact: '',
    phone: '',
    fullName: '',
    supplyItems: []
  }
}

const supplierForm = ref({
  name: '',
  contact: '',
  phone: '',
  fullName: '',
  supplyItems: []
})

const supplyCategories = ref([
  { value: 'vegetable', label: '蔬菜类' },
  { value: 'meat', label: '鲜肉类' },
  { value: 'frozen', label: '冷冻类' },
  { value: 'tofu', label: '豆制品类' },
  { value: 'egg', label: '禽蛋类' },
  { value: 'fruit', label: '水果类' },
  { value: 'dessert', label: '点心类' },
  { value: 'flour', label: '面粉制品' },
  { value: 'rice', label: '大米' },
  { value: 'oil', label: '食用油类' },
  { value: 'seasoning', label: '调味品类' }
])

// 供应商数据
const suppliers = ref([])
const loading = ref(false)
const loadError = ref('')

// 获取供应商数据
const fetchSuppliers = async () => {
  loading.value = true
  loadError.value = ''
  
  try {
    const response = await getSuppliers({
      page: currentPage.value,
      pageSize: pageSize.value,
      search: searchQuery.value
    })
    
    suppliers.value = response.data || []
    totalItems.value = response.total || 0
  } catch (error) {
    loadError.value = error.message || '获取供应商数据失败'
    ElMessage.error(loadError.value)
    suppliers.value = []
    totalItems.value = 0
  } finally {
    loading.value = false
  }
}

// 监听分页和搜索参数变化
watch([currentPage, pageSize, searchQuery], () => {
  if (currentView.value === 'all') {
    fetchSuppliers()
  }
})

// 在组件挂载时获取数据
onMounted(() => {
  if (currentView.value === 'all') {
    fetchSuppliers()
  }
})

// 格式化供应品类，将英文值转换为中文标签
const formatSupplyItems = (items) => {
  if (!Array.isArray(items)) return '';
  try {
    return items.map(item => {
      const category = supplyCategories.value.find(cat => cat.value === item)
      return category ? category.label : item
    }).join('、')
  } catch (error) {
    console.error('Error formatting supply items:', error);
    return items?.toString() || '';
  }
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true
  dialogVisible.value = true
  
  const loadingInstance = ElLoading.service({
    fullscreen: true,
    text: '加载供应商详情...'
  })
  
  try {
    // 获取供应商详细信息
    const data = await getSupplierById(row.id)
    supplierForm.value = { ...data }
  } catch (error) {
    ElMessage.error('获取供应商详情失败：' + error.message)
    dialogVisible.value = false
  } finally {
    loadingInstance.close()
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除供应商 ${row.name} 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const loadingInstance = ElLoading.service({
      fullscreen: true,
      text: '删除中...'
    })
    
    try {
      await deleteSupplier(row.id)
      ElMessage.success('删除成功')
      fetchSuppliers() // 重新获取供应商列表
    } finally {
      loadingInstance.close()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除供应商失败：' + error.message)
    }
  }
}

const handleSubmit = async () => {
  if (!supplierFormRef.value) return
  
  supplierFormRef.value.validate(async (valid) => {
    if (valid) {
      const loadingInstance = ElLoading.service({
        fullscreen: true,
        text: isEdit.value ? '更新中...' : '添加中...'
      })
      
      try {
        if (isEdit.value) {
          // 编辑现有供应商
          await updateSupplier(supplierForm.value.id, supplierForm.value)
          ElMessage.success('供应商信息更新成功')
        } else {
          // 添加新供应商
          await createSupplier(supplierForm.value)
          ElMessage.success('供应商添加成功')
        }
        
        dialogVisible.value = false
        fetchSuppliers() // 重新获取供应商列表
      } catch (error) {
        ElMessage.error((isEdit.value ? '更新' : '添加') + '供应商失败：' + error.message)
      } finally {
        loadingInstance.close()
      }
    } else {
      return false
    }
  })
}

const handleExportExcel = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '正在准备导出数据...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  
  try {
    // 调用API获取所有供应商数据
    const response = await getSuppliers({
      page: 1,
      pageSize: 10000, // 获取所有数据
      search: searchQuery.value
    })

    // 准备导出数据
    const exportData = response.data.map(item => ({
      '供应商名称': item.name,
      '供应商全称': item.fullName,
      '联系人': item.contact,
      '联系电话': item.phone,
      '供应品类': formatSupplyItems(item.supplyItems || [])
    }))

    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)
    XLSX.utils.book_append_sheet(wb, ws, '供应商数据')

    // 生成Excel文件并下载
    const fileName = `供应商数据_${new Date().toLocaleDateString()}.xlsx`
    XLSX.writeFile(wb, fileName)

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    loading.close()
  }
}
</script>

<style scoped>
.supplier-management {
  padding: 20px;
}

.view-switch {
  margin-bottom: 20px;
}

.month-selector {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
}

.toolbar {
  margin-bottom: 20px;
}

.toolbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 每月供应商样式 */
.monthly-suppliers {
  margin-bottom: 20px;
}

.monthly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.monthly-info {
  display: flex;
  gap: 20px;
  color: #606266;
}

.monthly-supplier-list {
  padding: 20px;
}


/* 历史每月供应商卡片样式 */
.history-suppliers {
  margin-top: 20px;
}

.history-suppliers .el-table {
  margin-top: 10px;
}

.history-suppliers .monthly-header {
  padding: 10px 0;
}

.history-suppliers .monthly-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.history-suppliers .monthly-info h3 {
  margin: 0;
  color: #303133;
}

.history-suppliers .monthly-info span {
  color: #909399;
  font-size: 14px;
}
</style>
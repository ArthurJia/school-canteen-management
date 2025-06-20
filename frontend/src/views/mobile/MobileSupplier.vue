<template>
  <div class="mobile-supplier">
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索供应商"
        size="large"
        clearable
      >
        <template #append>
          <el-button :icon="Search" />
        </template>
      </el-input>
      <el-button 
        type="primary" 
        size="large" 
        :icon="Plus" 
        @click="showAddDialog"
        class="add-btn"
      >
        新增
      </el-button>
    </div>

    <div class="supplier-list">
      <div 
        v-for="supplier in filteredSuppliers" 
        :key="supplier.id" 
        class="supplier-card"
      >
        <div class="card-header">
          <span class="name">{{ supplier.name }}</span>
          <div class="actions">
            <el-button 
              size="small" 
              :icon="Edit" 
              circle 
              @click.stop="showEditDialog(supplier)"
            />
            <el-button 
              size="small" 
              :icon="Delete" 
              circle 
              type="danger" 
              @click.stop="handleDelete(supplier)"
            />
          </div>
        </div>
        <div class="card-content">
          <div class="info-row">
            <el-icon><User /></el-icon>
            <span>{{ supplier.contact }}</span>
          </div>
          <div class="info-row">
            <el-icon><Phone /></el-icon>
            <span>{{ supplier.phone }}</span>
          </div>
          <div class="info-row">
            <el-icon><Location /></el-icon>
            <span>{{ supplier.fullName }}</span>
          </div>
          <div class="info-row">
            <el-icon><Goods /></el-icon>
            <span>{{ formatSupplyItems(supplier.supplyItems) }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      direction="btt"
      size="80%"
    >
      <el-form :model="supplierForm" label-position="top">
        <el-form-item label="供应商名称" required>
          <el-input v-model="supplierForm.name" size="large" />
        </el-form-item>
        <el-form-item label="联系人" required>
          <el-input v-model="supplierForm.contact" size="large" />
        </el-form-item>
        <el-form-item label="联系电话" required>
          <el-input v-model="supplierForm.phone" size="large" />
        </el-form-item>
        <el-form-item label="全称">
          <el-input v-model="supplierForm.fullName" type="textarea" />
        </el-form-item>
        <el-form-item label="供应品类">
          <el-select
            v-model="supplierForm.supplyItems"
            multiple
            placeholder="请选择供应品类"
            size="large"
            style="width: 100%"
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
        <el-button size="large" @click="dialogVisible = false">取消</el-button>
        <el-button size="large" type="primary" @click="handleSubmit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  Search, Plus, Edit, Delete, User, Phone, Location, Goods 
} from '@element-plus/icons-vue'

const searchQuery = ref('')
const dialogVisible = ref(false)
const isEditing = ref(false)

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

// 模拟供应商数据
const suppliers = ref([
  {
    id: 1,
    name: '麦德龙',
    contact: '张经理',
    phone: '13800138000',
    fullName: '北京市朝阳区建国路88号',
    supplyItems: ['rice', 'oil', 'seasoning']
  },
  {
    id: 2,
    name: '禾田裕',
    contact: '李经理',
    phone: '13900139000',
    fullName: '上海市浦东新区张江高科技园区',
    supplyItems: ['vegetable', 'fruit']
  },
  // 更多模拟数据...
])

const dialogTitle = computed(() => isEditing.value ? '编辑供应商' : '新增供应商')

const filteredSuppliers = computed(() => {
  return suppliers.value.filter(
    supplier =>
      supplier.name.includes(searchQuery.value) ||
      supplier.contact.includes(searchQuery.value)
  )
})

const formatSupplyItems = (items) => {
  return items.map(item => {
    const category = supplyCategories.value.find(cat => cat.value === item)
    return category ? category.label : item
  }).join('、')
}

const showAddDialog = () => {
  supplierForm.value = {
    name: '',
    contact: '',
    phone: '',
    fullName: '',
    supplyItems: []
  }
  isEditing.value = false
  dialogVisible.value = true
}

const showEditDialog = (supplier) => {
  supplierForm.value = { ...supplier }
  isEditing.value = true
  dialogVisible.value = true
}

const handleDelete = (supplier) => {
  console.log('删除供应商:', supplier)
}

const handleSubmit = () => {
  console.log('提交供应商表单:', supplierForm.value)
  dialogVisible.value = false
}
</script>

<style scoped>
.mobile-supplier {
  padding: 10px;
}
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}
.add-btn {
  flex-shrink: 0;
}
.supplier-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.supplier-card {
  padding: 12px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.card-header .name {
  font-weight: bold;
  font-size: 16px;
}
.card-header .actions {
  display: flex;
  gap: 5px;
}
.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}
.info-row .el-icon {
  font-size: 16px;
}
</style>
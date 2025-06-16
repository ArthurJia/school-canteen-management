<template>
  <div class="outbound-management">
    <h2>出库管理</h2>
    
    <!-- 出库表单 -->
    <el-card class="mb-4">
      <template #header>
        <div class="card-header">
          <span>创建出库记录</span>
        </div>
      </template>
      
      <el-form :model="outboundForm" label-width="120px" @submit.prevent="handleSubmit">
        <el-form-item label="选择原料" required>
          <el-select v-model="outboundForm.ingredient_id" placeholder="请选择原料" style="width: 100%">
            <el-option
              v-for="item in ingredients"
              :key="item.id"
              :label="`${item.name} (库存: ${item.quantity}${item.unit || '个'})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="出库数量" required>
          <el-input-number 
            v-model="outboundForm.quantity" 
            :min="0.01" 
            :step="0.1" 
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="出库用途" required>
          <el-input v-model="outboundForm.purpose" placeholder="请输入出库用途" />
        </el-form-item>
        
        <el-form-item label="操作人">
          <el-input v-model="outboundForm.operator" placeholder="请输入操作人姓名" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交出库</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 出库记录列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>出库记录</span>
        </div>
      </template>
      
      <el-table :data="stockOuts" style="width: 100%" v-loading="loading">
        <el-table-column prop="ingredient_name" label="原料名称" />
        <el-table-column prop="quantity" label="出库数量" />
        <el-table-column prop="purpose" label="出库用途" />
        <el-table-column prop="operator" label="操作人" />
        <el-table-column prop="date" label="出库时间">
          <template #default="scope">
            {{ new Date(scope.row.date).toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createStockOut, getStockOuts } from '@/api'
import { useIngredientStore } from '@/stores/ingredient'

const ingredientStore = useIngredientStore()
const ingredients = ref([])
const stockOuts = ref([])
const loading = ref(false)

const outboundForm = ref({
  ingredient_id: '',
  quantity: 1,
  purpose: '',
  operator: ''
})

// 获取原料列表
const fetchIngredients = async () => {
  try {
    await ingredientStore.fetchIngredients()
    ingredients.value = ingredientStore.ingredients
  } catch (error) {
    ElMessage.error('获取原料列表失败')
  }
}

// 获取出库记录
const fetchStockOuts = async () => {
  loading.value = true
  try {
    stockOuts.value = await getStockOuts()
  } catch (error) {
    ElMessage.error('获取出库记录失败')
  } finally {
    loading.value = false
  }
}

// 提交出库表单
const handleSubmit = async () => {
  if (!outboundForm.value.ingredient_id || !outboundForm.value.quantity || !outboundForm.value.purpose) {
    ElMessage.warning('请填写必要信息')
    return
  }

  try {
    await createStockOut(outboundForm.value)
    ElMessage.success('出库成功')
    resetForm()
    fetchStockOuts() // 刷新出库记录列表
    fetchIngredients() // 刷新原料库存
  } catch (error) {
    ElMessage.error(error.message || '出库失败')
  }
}

// 重置表单
const resetForm = () => {
  outboundForm.value = {
    ingredient_id: '',
    quantity: 1,
    purpose: '',
    operator: ''
  }
}

onMounted(() => {
  fetchIngredients()
  fetchStockOuts()
})
</script>

<style scoped>
.outbound-management {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
<template>
  <div class="mobile-outbound">
    <!-- 出库表单 -->
    <van-form @submit="handleSubmit">
      <van-cell-group inset>
        <van-field
          v-model="selectedIngredientName"
          is-link
          readonly
          name="ingredient"
          label="选择原料"
          placeholder="点击选择原料"
          @click="showIngredientPicker = true"
          :rules="[{ required: true, message: '请选择原料' }]"
        />
        
        <van-field
          v-model="outboundForm.quantity"
          type="digit"
          name="quantity"
          label="出库数量"
          placeholder="请输入出库数量"
          :rules="[{ required: true, message: '请输入出库数量' }]"
        />
        
        <van-field
          v-model="outboundForm.purpose"
          name="purpose"
          label="出库用途"
          placeholder="请输入出库用途"
          :rules="[{ required: true, message: '请输入出库用途' }]"
        />
        
        <van-field
          v-model="outboundForm.operator"
          name="operator"
          label="操作人"
          placeholder="请输入操作人姓名"
        />
      </van-cell-group>
      
      <div style="margin: 16px">
        <van-button round block type="primary" native-type="submit">
          提交出库
        </van-button>
      </div>
    </van-form>

    <!-- 原料选择器 -->
    <van-popup v-model:show="showIngredientPicker" position="bottom">
      <van-picker
        :columns="ingredientColumns"
        @confirm="onIngredientConfirm"
        @cancel="showIngredientPicker = false"
        show-toolbar
        title="选择原料"
      />
    </van-popup>

    <!-- 出库记录列表 -->
    <van-cell-group inset title="出库记录">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="onLoad"
        >
          <van-cell v-for="item in stockOuts" :key="item.id">
            <template #title>
              <div class="outbound-item">
                <span class="ingredient-name">{{ item.ingredient_name }}</span>
                <span class="quantity">{{ item.quantity }}</span>
              </div>
            </template>
            <template #label>
              <div class="outbound-detail">
                <span>用途：{{ item.purpose }}</span>
                <span>操作人：{{ item.operator }}</span>
                <span>时间：{{ new Date(item.date).toLocaleString() }}</span>
              </div>
            </template>
          </van-cell>
        </van-list>
      </van-pull-refresh>
    </van-cell-group>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { showToast } from 'vant'
import { createStockOut, getStockOuts } from '@/api'
import { useIngredientStore } from '@/stores/ingredient'

const ingredientStore = useIngredientStore()
const ingredients = ref([])
const stockOuts = ref([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const showIngredientPicker = ref(false)
const selectedIngredientId = ref('')
const selectedIngredientName = ref('')

const outboundForm = ref({
  ingredient_id: '',
  quantity: '',
  purpose: '',
  operator: ''
})

// 原料选择器数据
const ingredientColumns = computed(() => {
  return ingredients.value.map(item => ({
    text: `${item.name} (库存: ${item.quantity}${item.unit || '个'})`,
    value: item.id
  }))
})

// 获取原料列表
const fetchIngredients = async () => {
  try {
    await ingredientStore.fetchIngredients()
    ingredients.value = ingredientStore.ingredients
  } catch (error) {
    showToast('获取原料列表失败')
  }
}

// 获取出库记录
const fetchStockOuts = async () => {
  loading.value = true
  try {
    const data = await getStockOuts()
    if (refreshing.value) {
      stockOuts.value = data
      refreshing.value = false
    } else {
      stockOuts.value = [...stockOuts.value, ...data]
    }
    finished.value = true // 由于没有分页，所以直接设置为完成
  } catch (error) {
    showToast('获取出库记录失败')
  } finally {
    loading.value = false
  }
}

// 提交出库表单
const handleSubmit = async () => {
  try {
    await createStockOut({
      ...outboundForm.value,
      ingredient_id: selectedIngredientId.value,
      quantity: parseFloat(outboundForm.value.quantity)
    })
    showToast('出库成功')
    resetForm()
    onRefresh()
    fetchIngredients()
  } catch (error) {
    showToast(error.message || '出库失败')
  }
}

// 选择原料
const onIngredientConfirm = (value) => {
  const ingredient = ingredients.value.find(item => item.id === value.value)
  if (ingredient) {
    selectedIngredientId.value = ingredient.id
    selectedIngredientName.value = ingredient.name
  }
  showIngredientPicker.value = false
}

// 重置表单
const resetForm = () => {
  outboundForm.value = {
    ingredient_id: '',
    quantity: '',
    purpose: '',
    operator: ''
  }
  selectedIngredientId.value = ''
  selectedIngredientName.value = ''
}

// 下拉刷新
const onRefresh = () => {
  finished.value = false
  refreshing.value = true
  fetchStockOuts()
}

// 加载更多
const onLoad = () => {
  // 由于没有分页，这里直接设置完成
  finished.value = true
}

onMounted(() => {
  fetchIngredients()
  fetchStockOuts()
})
</script>

<style scoped>
.mobile-outbound {
  padding-bottom: 50px;
}

.outbound-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ingredient-name {
  font-weight: bold;
}

.quantity {
  color: #666;
}

.outbound-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #666;
  font-size: 12px;
}
</style>
<template>
  <div class="mobile-inbound">
    <el-form :model="form" label-position="top">
      <el-form-item label="名称" required>
        <el-input 
          v-model="form.name" 
          placeholder="请输入食材名称"
          size="large"
        />
      </el-form-item>
      
      <el-form-item label="分类" required>
        <el-select 
          v-model="form.category" 
          placeholder="请选择食材分类"
          size="large"
        >
          <el-option
            v-for="category in categories"
            :key="category.value"
            :label="category.label"
            :value="category.value"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="供应商" required>
        <el-select 
          v-model="form.supplier" 
          placeholder="请选择供应商"
          size="large"
        >
          <el-option
            v-for="supplier in suppliers"
            :key="supplier.value"
            :label="supplier.label"
            :value="supplier.value"
          />
        </el-select>
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="数量" required>
            <el-input 
              v-model="form.quantity" 
              type="number"
              :min="0"
              size="large"
              style="width: 100%"
              placeholder="请输入数量"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="单价(元)" required>
            <el-input 
              v-model="form.price" 
              type="number"
              :min="0"
              :step="0.01"
              size="large"
              style="width: 100%"
              placeholder="请输入单价"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="小计(元)">
            <el-input 
              :value="subtotal" 
              readonly
              size="large"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="备注">
        <el-input 
          v-model="form.remark" 
          type="textarea" 
          :rows="2"
          placeholder="可输入特殊要求或说明"
        />
      </el-form-item>
      
      <el-button 
        type="primary" 
        size="large" 
        @click="handleSubmit"
        style="width: 100%; margin-top: 20px"
      >
        一键入库
      </el-button>
    </el-form>
    
    <div class="notice">
      <p>当天类食材（蔬菜、鲜肉等）：自动完成出入库记录</p>
      <p>储存类食材（大米、油等）：仅记录入库</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const form = ref({
  name: '',
  category: '',
  supplier: '',
  quantity: 0,
  price: 0,
  remark: ''
})

const subtotal = computed(() => {
  return (form.value.quantity * form.value.price).toFixed(2)
})

const categories = ref([
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

const handleSubmit = () => {
  // 处理入库逻辑
  console.log('提交表单:', form.value)
}
</script>

<style scoped>
.mobile-inbound {
  padding: 15px;
}
.notice {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
}
.notice p {
  margin: 5px 0;
}
</style>
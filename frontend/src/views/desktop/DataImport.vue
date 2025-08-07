<template>
  <div class="data-import">
    <div class="page-header">
      <h2>数据导入</h2>
      <p class="page-desc">支持导入库存查询数据和月底库存数据</p>
    </div>

    <!-- 库存查询数据导入卡片 -->
    <el-card class="import-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <div class="header-info">
            <span class="card-subtitle">上传Excel或CSV文件导入库存查询数据</span>
          </div>
          <div class="header-actions">
            <el-button type="success" :icon="Download" @click="downloadStockTemplate">
              下载模板
            </el-button>
            <el-button type="primary" :icon="Upload" @click="triggerStockFileUpload">
              选择文件
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="import-content">
        <div class="upload-area" @drop="handleStockFileDrop" @dragover.prevent @dragenter.prevent>
          <input 
            ref="stockFileInput" 
            type="file" 
            accept=".xlsx,.xls,.csv" 
            @change="handleStockFileSelect" 
            style="display: none"
          >
          
          <div v-if="!stockFile" class="upload-placeholder">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>将文件拖拽到此处，或<span class="upload-link" @click="triggerStockFileUpload">点击上传</span></p>
              <p class="upload-tip">支持 .xlsx、.xls、.csv 格式文件</p>
            </div>
          </div>
          
          <div v-else class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <div class="file-details">
              <p class="file-name">{{ stockFile.name }}</p>
              <p class="file-size">{{ formatFileSize(stockFile.size) }}</p>
            </div>
            <el-button type="danger" :icon="Delete" @click="removeStockFile" circle size="small" />
          </div>
        </div>
        
        <div class="import-actions">
          <el-button 
            type="primary" 
            :loading="stockImporting" 
            :disabled="!stockFile"
            @click="importStockData"
          >
            {{ stockImporting ? '导入中...' : '开始导入' }}
          </el-button>
          <el-button @click="clearStockImport">清空</el-button>
        </div>
        
        <div v-if="stockImportResult" class="import-result">
          <el-alert 
            :title="stockImportResult.success ? '导入成功' : '导入失败'" 
            :type="stockImportResult.success ? 'success' : 'error'"
            :description="stockImportResult.message"
            show-icon
            :closable="false"
          />
          <div v-if="stockImportResult.details" class="result-details">
            <p>成功导入：{{ stockImportResult.details.success }} 条</p>
            <p v-if="stockImportResult.details.failed > 0">失败：{{ stockImportResult.details.failed }} 条</p>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 月底库存数据导入卡片 -->
    <el-card class="import-card card-hover card-glow">
      <template #header>
        <div class="card-header">
          <div class="header-info">
            <span class="card-title">月底库存数据导入</span>
            <span class="card-subtitle">导入月底库存卡片的数据</span>
          </div>
          <div class="header-actions">
            <el-button type="success" :icon="Download" @click="downloadInventoryTemplate">
              下载模板
            </el-button>
            <el-button type="primary" :icon="Upload" @click="triggerInventoryFileUpload">
              选择文件
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="import-content">
        <div class="upload-area" @drop="handleInventoryFileDrop" @dragover.prevent @dragenter.prevent>
          <input 
            ref="inventoryFileInput" 
            type="file" 
            accept=".xlsx,.xls,.csv" 
            @change="handleInventoryFileSelect" 
            style="display: none"
          >
          
          <div v-if="!inventoryFile" class="upload-placeholder">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>将文件拖拽到此处，或<span class="upload-link" @click="triggerInventoryFileUpload">点击上传</span></p>
              <p class="upload-tip">支持 .xlsx、.xls、.csv 格式文件</p>
            </div>
          </div>
          
          <div v-else class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <div class="file-details">
              <p class="file-name">{{ inventoryFile.name }}</p>
              <p class="file-size">{{ formatFileSize(inventoryFile.size) }}</p>
            </div>
            <el-button type="danger" :icon="Delete" @click="removeInventoryFile" circle size="small" />
          </div>
        </div>
        
        <div class="import-actions">
          <el-button 
            type="primary" 
            :loading="inventoryImporting" 
            :disabled="!inventoryFile"
            @click="importInventoryData"
          >
            {{ inventoryImporting ? '导入中...' : '开始导入' }}
          </el-button>
          <el-button @click="clearInventoryImport">清空</el-button>
        </div>
        
        <div v-if="inventoryImportResult" class="import-result">
          <el-alert 
            :title="inventoryImportResult.success ? '导入成功' : '导入失败'" 
            :type="inventoryImportResult.success ? 'success' : 'error'"
            :description="inventoryImportResult.message"
            show-icon
            :closable="false"
          />
          <div v-if="inventoryImportResult.details" class="result-details">
            <p>成功导入：{{ inventoryImportResult.details.success }} 条</p>
            <p v-if="inventoryImportResult.details.failed > 0">失败：{{ inventoryImportResult.details.failed }} 条</p>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, 
  Download, 
  UploadFilled, 
  Document, 
  Delete 
} from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

// 响应式数据
const stockFile = ref(null)
const inventoryFile = ref(null)
const stockImporting = ref(false)
const inventoryImporting = ref(false)
const stockImportResult = ref(null)
const inventoryImportResult = ref(null)

// 文件输入引用
const stockFileInput = ref(null)
const inventoryFileInput = ref(null)

// 库存查询数据导入方法
const triggerStockFileUpload = () => {
  stockFileInput.value?.click()
}

const handleStockFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetStockFile(file)
  }
}

const handleStockFileDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetStockFile(file)
  }
}

const validateAndSetStockFile = (file) => {
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/csv'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('请选择 Excel 或 CSV 格式的文件')
    return
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  stockFile.value = file
  stockImportResult.value = null
}

const removeStockFile = () => {
  stockFile.value = null
  stockImportResult.value = null
  if (stockFileInput.value) {
    stockFileInput.value.value = ''
  }
}

const clearStockImport = () => {
  removeStockFile()
}

const importStockData = async () => {
  if (!stockFile.value) {
    ElMessage.error('请先选择要导入的文件')
    return
  }
  
  stockImporting.value = true
  stockImportResult.value = null
  
  try {
    const data = await readExcelFile(stockFile.value)
    
    // 验证数据格式
    if (!data || data.length === 0) {
      throw new Error('文件中没有找到有效数据')
    }
    
    // 验证必要的列
    const requiredColumns = ['入库时间', '食材名称', '分类', '供应商', '数量', '单位', '单价', '小计']
    const headers = Object.keys(data[0])
    const missingColumns = requiredColumns.filter(col => !headers.includes(col))
    
    if (missingColumns.length > 0) {
      throw new Error(`缺少必要的列：${missingColumns.join(', ')}`)
    }
    
    // 处理数据并保存到localStorage
    const processedData = data.map((row, index) => ({
      id: Date.now() + index, // 生成唯一ID
      in_time: row['入库时间'],
      name: row['食材名称'],
      category: row['分类'],
      supplier: row['供应商'],
      quantity: parseFloat(row['数量']) || 0,
      unit: row['单位'] || 'kg',
      price: parseFloat(row['单价']) || 0,
      subtotal: parseFloat(row['小计']) || 0,
      note: row['备注'] || ''
    }))
    
    // 保存到localStorage
    const existingData = JSON.parse(localStorage.getItem('stockQueryData') || '[]')
    const mergedData = [...existingData, ...processedData]
    localStorage.setItem('stockQueryData', JSON.stringify(mergedData))
    
    stockImportResult.value = {
      success: true,
      message: '库存查询数据导入成功',
      details: {
        success: processedData.length,
        failed: 0
      }
    }
    
    ElMessage.success(`成功导入 ${processedData.length} 条库存查询数据`)
    
  } catch (error) {
    console.error('导入库存查询数据失败:', error)
    stockImportResult.value = {
      success: false,
      message: error.message || '导入失败，请检查文件格式'
    }
    ElMessage.error(error.message || '导入失败')
  } finally {
    stockImporting.value = false
  }
}

// 月底库存数据导入方法
const triggerInventoryFileUpload = () => {
  inventoryFileInput.value?.click()
}

const handleInventoryFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndSetInventoryFile(file)
  }
}

const handleInventoryFileDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) {
    validateAndSetInventoryFile(file)
  }
}

const validateAndSetInventoryFile = (file) => {
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel',
    'text/csv'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('请选择 Excel 或 CSV 格式的文件')
    return
  }
  
  if (file.size > 10 * 1024 * 1024) { // 10MB
    ElMessage.error('文件大小不能超过 10MB')
    return
  }
  
  inventoryFile.value = file
  inventoryImportResult.value = null
}

const removeInventoryFile = () => {
  inventoryFile.value = null
  inventoryImportResult.value = null
  if (inventoryFileInput.value) {
    inventoryFileInput.value.value = ''
  }
}

const clearInventoryImport = () => {
  removeInventoryFile()
}

const importInventoryData = async () => {
  if (!inventoryFile.value) {
    ElMessage.error('请先选择要导入的文件')
    return
  }
  
  inventoryImporting.value = true
  inventoryImportResult.value = null
  
  try {
    const data = await readExcelFile(inventoryFile.value)
    
    // 验证数据格式
    if (!data || data.length === 0) {
      throw new Error('文件中没有找到有效数据')
    }
    
    // 验证必要的列
    const requiredColumns = ['时间（年月）', '名称', '分类', '单价', '库存数量']
    const headers = Object.keys(data[0])
    const missingColumns = requiredColumns.filter(col => !headers.includes(col))
    
    if (missingColumns.length > 0) {
      throw new Error(`缺少必要的列：${missingColumns.join(', ')}`)
    }
    
    // 处理数据并保存到localStorage
    const processedData = data.map(row => ({
      date: row['时间（年月）'],
      name: row['名称'],
      category: row['分类'],
      unitPrice: parseFloat(row['单价']) || 0,
      quantity: parseFloat(row['库存数量']) || 0
    }))
    
    // 保存到localStorage
    const existingData = JSON.parse(localStorage.getItem('monthlyInventory') || '[]')
    const mergedData = [...existingData, ...processedData]
    localStorage.setItem('monthlyInventory', JSON.stringify(mergedData))
    
    inventoryImportResult.value = {
      success: true,
      message: '月底库存数据导入成功',
      details: {
        success: processedData.length,
        failed: 0
      }
    }
    
    ElMessage.success(`成功导入 ${processedData.length} 条月底库存数据`)
    
  } catch (error) {
    console.error('导入月底库存数据失败:', error)
    inventoryImportResult.value = {
      success: false,
      message: error.message || '导入失败，请检查文件格式'
    }
    ElMessage.error(error.message || '导入失败')
  } finally {
    inventoryImporting.value = false
  }
}

// 通用方法
const readExcelFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const sheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[sheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        resolve(jsonData)
      } catch (error) {
        reject(new Error('文件解析失败，请检查文件格式'))
      }
    }
    
    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }
    
    reader.readAsArrayBuffer(file)
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 下载模板方法
const downloadStockTemplate = () => {
  const templateData = [
    {
      '入库时间': '2024-01-01',
      '食材名称': '优质大米',
      '分类': 'rice',
      '供应商': 'maidelong',
      '数量': 100,
      '单位': 'kg',
      '单价': 5.5,
      '小计': 550,
      '备注': '示例数据'
    },
    {
      '入库时间': '2024-01-02',
      '食材名称': '大豆油',
      '分类': 'oil',
      '供应商': 'yurun',
      '数量': 50,
      '单位': 'L',
      '单价': 12.8,
      '小计': 640,
      '备注': '食用油'
    },
    {
      '入库时间': '2024-01-03',
      '食材名称': '白菜',
      '分类': 'vegetable',
      '供应商': 'hetianyu',
      '数量': 30,
      '单位': 'kg',
      '单价': 2.5,
      '小计': 75,
      '备注': '新鲜蔬菜'
    }
  ]
  
  // 添加分类和供应商代码说明
  const categorySheet = [
    { '分类代码': 'vegetable', '分类名称': '蔬菜类' },
    { '分类代码': 'meat', '分类名称': '鲜肉类' },
    { '分类代码': 'frozen', '分类名称': '冷冻类' },
    { '分类代码': 'tofu', '分类名称': '豆制品类' },
    { '分类代码': 'egg', '分类名称': '禽蛋类' },
    { '分类代码': 'fruit', '分类名称': '水果类' },
    { '分类代码': 'dessert', '分类名称': '点心类' },
    { '分类代码': 'flour', '分类名称': '面粉制品' },
    { '分类代码': 'rice', '分类名称': '大米' },
    { '分类代码': 'oil', '分类名称': '食用油类' },
    { '分类代码': 'seasoning', '分类名称': '调味品类' }
  ]
  
  const supplierSheet = [
    { '供应商代码': 'maidelong', '供应商名称': '麦德龙' },
    { '供应商代码': 'hetianyu', '供应商名称': '禾田裕' },
    { '供应商代码': 'tianyuan', '供应商名称': '天源' },
    { '供应商代码': 'hejiahuang', '供应商名称': '合家欢' },
    { '供应商代码': 'yurun', '供应商名称': '雨润' },
    { '供应商代码': 'zhonghe', '供应商名称': '中合' },
    { '供应商代码': 'zhongxin', '供应商名称': '中鑫' },
    { '供应商代码': 'suhe', '供应商名称': '苏合' },
    { '供应商代码': 'huacheng', '供应商名称': '华诚' },
    { '供应商代码': 'xuezihan', '供应商名称': '学子膳' },
    { '供应商代码': 'yaozhiwei', '供应商名称': '肴之味' },
    { '供应商代码': 'yuanwei', '供应商名称': '原味' },
    { '供应商代码': 'huihai', '供应商名称': '汇海' },
    { '供应商代码': 'zuming', '供应商名称': '祖名' },
    { '供应商代码': 'yafu', '供应商名称': '亚夫' },
    { '供应商代码': 'longmen', '供应商名称': '龙门' },
    { '供应商代码': 'weigang', '供应商名称': '卫岗' },
    { '供应商代码': 'tiangu', '供应商名称': '天谷' },
    { '供应商代码': 'sushi', '供应商名称': '苏食' },
    { '供应商代码': 'hengshun', '供应商名称': '恒顺' },
    { '供应商代码': 'zhongrun', '供应商名称': '中润' },
    { '供应商代码': 'guoguo', '供应商名称': '果果' },
    { '供应商代码': 'furun', '供应商名称': '富润' }
  ]
  
  try {
    // 创建工作簿
    const workbook = XLSX.utils.book_new()
    
    // 添加示例数据工作表
    const dataSheet = XLSX.utils.json_to_sheet(templateData)
    XLSX.utils.book_append_sheet(workbook, dataSheet, '示例数据')
    
    // 添加分类代码说明工作表
    const catSheet = XLSX.utils.json_to_sheet(categorySheet)
    XLSX.utils.book_append_sheet(workbook, catSheet, '分类代码说明')
    
    // 添加供应商代码说明工作表
    const supSheet = XLSX.utils.json_to_sheet(supplierSheet)
    XLSX.utils.book_append_sheet(workbook, supSheet, '供应商代码说明')
    
    // 导出Excel文件
    XLSX.writeFile(workbook, '库存查询数据模板.xlsx')
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const downloadInventoryTemplate = () => {
  const templateData = [
    {
      '时间（年月）': '2024-01',
      '名称': '优质大米',
      '分类': '大米',
      '单价': 5.5,
      '库存数量': 100
    },
    {
      '时间（年月）': '2024-01',
      '名称': '大豆油',
      '分类': '食用油类',
      '单价': 12.8,
      '库存数量': 50
    },
    {
      '时间（年月）': '2024-01',
      '名称': '食盐',
      '分类': '调味品类',
      '单价': 3.2,
      '库存数量': 20
    }
  ]
  
  try {
    const worksheet = XLSX.utils.json_to_sheet(templateData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '月底库存数据')
    XLSX.writeFile(workbook, '月底库存数据模板.xlsx')
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}
</script>

<style scoped>
.data-import {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  color: #333;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 10px;
}

.page-desc {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.import-card {
  margin-bottom: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.import-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.card-subtitle {
  font-size: 14px;
  color: #666;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.import-content {
  padding: 20px 0;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.upload-text p {
  margin: 5px 0;
  color: #666;
}

.upload-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: underline;
}

.upload-link:hover {
  color: #66b1ff;
}

.upload-tip {
  font-size: 12px;
  color: #999;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.file-icon {
  font-size: 32px;
  color: #409eff;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.file-size {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.import-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.import-result {
  margin-top: 20px;
}

.result-details {
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.result-details p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-import {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .upload-area {
    padding: 30px 15px;
  }
  
  .file-info {
    flex-direction: column;
    text-align: center;
  }
  
  .import-actions {
    flex-direction: column;
    align-items: center;
  }
}

/* 动画效果 */
.import-card {
  animation: cardFadeIn 0.3s ease-out;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 按钮悬浮效果 */
:deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 警告框样式 */
:deep(.el-alert) {
  border-radius: 8px;
}

/* 卡片头部样式 */
:deep(.el-card__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #e4e7ed;
}
</style>

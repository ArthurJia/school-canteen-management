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
            <span class="card-title">库存查询数据导入</span>
            <span class="card-subtitle">上传Excel或CSV文件导入入库记录数据，用于库存查询和统计分析</span>
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
        
        <div class="import-options">
          <span class="option-label">导入方式：</span>
          <el-radio-group v-model="stockImportMode" size="small">
            <el-radio-button :value="'append'">新增数据</el-radio-button>
            <el-radio-button :value="'overwrite'">覆盖数据</el-radio-button>
          </el-radio-group>
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
            <span class="card-subtitle">上传Excel或CSV文件导入月底库存数据，用于库存统计和成本核算</span>
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
        
        <div class="import-options">
          <span class="option-label">导入方式：</span>
          <el-radio-group v-model="inventoryImportMode" size="small">
            <el-radio-button :value="'append'">新增数据</el-radio-button>
            <el-radio-button :value="'overwrite'">覆盖数据</el-radio-button>
          </el-radio-group>
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
import { ElMessage } from 'element-plus'
import { 
  Upload, 
  Download, 
  UploadFilled, 
  Document, 
  Delete 
} from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import axios from 'axios'

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// 响应式数据
const stockFile = ref(null)
const stockImporting = ref(false)
const stockImportResult = ref(null)
const stockImportMode = ref('append')

const inventoryFile = ref(null)
const inventoryImporting = ref(false)
const inventoryImportResult = ref(null)
const inventoryImportMode = ref('append')

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

// API函数：导入库存查询数据
const importStockDataToAPI = async (data, mode) => {
  try {
    console.log('开始批量导入库存查询数据:', { dataCount: data.length, mode })
    
    if (mode === 'overwrite') {
      // 覆盖模式：先清空现有数据
      const deleteResponse = await axios.delete(`${API_BASE_URL}/api/stock-ins/all`)
      console.log('清空现有数据响应:', deleteResponse.data)
    }
    
    // 批量导入数据
    let successCount = 0
    let failedCount = 0
    const errors = []
    
    for (const item of data) {
      try {
        const response = await axios.post(`${API_BASE_URL}/api/stock-ins`, item)
        if (response.data.success) {
          successCount++
        } else {
          failedCount++
          errors.push(`${item.name}: ${response.data.error || '未知错误'}`)
        }
      } catch (error) {
        failedCount++
        errors.push(`${item.name}: ${error.response?.data?.error || error.message}`)
      }
    }
    
    return {
      success: failedCount === 0,
      successCount,
      failedCount,
      errors,
      message: failedCount === 0 ? '所有数据导入成功' : `部分数据导入失败，成功${successCount}条，失败${failedCount}条`
    }
    
  } catch (error) {
    console.error('批量导入API调用失败:', error)
    
    if (error.response) {
      throw new Error(error.response.data?.error || `服务器错误: ${error.response.status}`)
    } else if (error.request) {
      throw new Error('网络错误：无法连接到服务器')
    } else {
      throw new Error(error.message || '未知错误')
    }
  }
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
    const requiredColumns = ['食材名称', '分类', '数量', '单位', '单价']
    const headers = Object.keys(data[0])
    const missingColumns = requiredColumns.filter(col => !headers.includes(col))
    
    if (missingColumns.length > 0) {
      throw new Error(`缺少必要的列：${missingColumns.join(', ')}`)
    }
    
    // 处理数据 - 将中文字段名映射为英文字段名
    const processedData = data.map(row => {
      // 处理日期格式
      let dateValue = row['入库时间'] || new Date().toISOString().split('T')[0];
      
      // 检查是否是Excel日期数值格式
      if (typeof dateValue === 'number' || (typeof dateValue === 'string' && !isNaN(dateValue) && !dateValue.includes('-') && !dateValue.includes('/'))) {
        // 将Excel日期数值转换为JavaScript日期对象
        const excelDate = parseInt(dateValue);
        const millisecondsPerDay = 24 * 60 * 60 * 1000;
        
        // 创建1900年1月1日的日期（Excel的起始日期）
        const excelStartDate = new Date(1900, 0, 1);
        
        // 如果日期大于60（1900年2月29日之后），需要减去1天（因为1900年不是闰年，但Excel认为是）
        const daysToAdd = excelDate > 60 ? excelDate - 1 : excelDate;
        
        // 计算JavaScript日期
        const jsDate = new Date(excelStartDate.getTime() + daysToAdd * millisecondsPerDay);
        
        // 格式化为YYYY-MM-DD
        dateValue = `${jsDate.getFullYear()}-${String(jsDate.getMonth() + 1).padStart(2, '0')}-${String(jsDate.getDate()).padStart(2, '0')}`;
      }
      
      // 处理分类映射
      const categoryMapping = {
        '蔬菜类': 'vegetable',
        '鲜肉类': 'meat',
        '冷冻类': 'frozen',
        '豆制品类': 'tofu',
        '禽蛋类': 'egg',
        '水果类': 'fruit',
        '点心类': 'dessert',
        '面粉制品': 'flour',
        '大米': 'rice',
        '食用油类': 'oil',
        '调味品类': 'seasoning'
      };
      
      // 处理供应商映射
      const supplierMapping = {
        '麦德龙': 'maidelong',
        '禾田裕': 'hetianyu',
        '天源': 'tianyuan',
        '合家欢': 'hejiahuang',
        '雨润': 'yurun',
        '中合': 'zhonghe',
        '中鑫': 'zhongxin',
        '苏合': 'suhe',
        '华诚': 'huacheng',
        '学子膳': 'xuezihan',
        '肴之味': 'yaozhiwei',
        '原味': 'yuanwei',
        '汇海': 'huihai',
        '祖名': 'zuming',
        '亚夫': 'yafu',
        '龙门': 'longmen',
        '卫岗': 'weigang',
        '天谷': 'tiangu',
        '苏食': 'sushi',
        '恒顺': 'hengshun',
        '中润': 'zhongrun',
        '果果': 'guoguo',
        '富润': 'furun'
      };
      
      // 处理单位映射
      const unitMapping = {
        '千克': 'kg',
        '公斤': 'kg',
        'kg': 'kg',
        '升': 'L',
        'L': 'L',
        '个': '个',
        '只': '只',
        '袋': '袋',
        '盒': '盒'
      };
      
      const quantity = parseFloat(row['数量']) || 0;
      const price = parseFloat(row['单价']) || 0;
      
      return {
        name: row['食材名称'],
        category: categoryMapping[row['分类']] || row['分类'],
        quantity: quantity,
        unit: unitMapping[row['单位']] || row['单位'] || 'kg',
        supplier: supplierMapping[row['供应商']] || row['供应商'] || '',
        price: price,
        note: row['备注'] || '',
        stockInDate: dateValue
      };
    });
    
    try {
      // 调用API将数据导入到后端数据库
      const apiResult = await importStockDataToAPI(processedData, stockImportMode.value)
      
      // 根据API返回结果更新显示
      if (apiResult.success) {
        stockImportResult.value = {
          success: true,
          message: stockImportMode.value === 'append' ? 
            '库存查询数据已成功添加到数据库' : 
            '库存查询数据已成功覆盖到数据库',
          details: {
            success: apiResult.successCount,
            failed: apiResult.failedCount
          }
        }
        
        if (apiResult.failedCount === 0) {
          ElMessage.success(`成功导入 ${apiResult.successCount} 条库存查询数据`)
        } else {
          ElMessage.warning(`导入完成：成功 ${apiResult.successCount} 条，失败 ${apiResult.failedCount} 条`)
        }
      } else {
        stockImportResult.value = {
          success: false,
          message: `导入部分失败：${apiResult.message}`,
          details: {
            success: apiResult.successCount,
            failed: apiResult.failedCount
          }
        }
        ElMessage.error(`导入失败：成功 ${apiResult.successCount} 条，失败 ${apiResult.failedCount} 条`)
      }
      
    } catch (apiError) {
      console.error('API调用失败:', apiError)
      stockImportResult.value = {
        success: false,
        message: `API调用失败: ${apiError.message || '网络错误'}`
      }
      ElMessage.error(`导入失败: ${apiError.message || '网络错误，请检查后端服务是否正常'}`)
    }
    
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

const downloadStockTemplate = () => {
  const templateData = [
    {
      '入库时间': '2025-08-08',
      '食材名称': '大白菜',
      '分类': '蔬菜类',
      '数量': 50,
      '单位': '千克',
      '供应商': '麦德龙',
      '单价': 2.5,
      '备注': '新鲜蔬菜'
    },
    {
      '入库时间': '2025-08-08',
      '食材名称': '猪肉',
      '分类': '鲜肉类',
      '数量': 20,
      '单位': '千克',
      '供应商': '雨润',
      '单价': 28.0,
      '备注': '优质猪肉'
    },
    {
      '入库时间': '2025-08-08',
      '食材名称': '大米',
      '分类': '大米',
      '数量': 100,
      '单位': '千克',
      '供应商': '天源',
      '单价': 5.5,
      '备注': '优质大米'
    }
  ]
  
  try {
    const worksheet = XLSX.utils.json_to_sheet(templateData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '库存查询数据')
    XLSX.writeFile(workbook, '库存查询数据模板.xlsx')
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
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

// API函数：导入月底库存数据
const importInventoryDataToAPI = async (data, mode) => {
  try {
    console.log('开始批量导入月底库存数据:', { dataCount: data.length, mode })
    
    // 使用批量导入API
    const response = await axios.post(`${API_BASE_URL}/api/monthly-inventory/batch`, {
      data: data,
      mode: mode // 'append' 或 'overwrite'
    })
    
    console.log('批量导入API响应:', response.data)
    return response.data
    
  } catch (error) {
    console.error('批量导入API调用失败:', error)
    
    // 如果是网络错误或服务器错误，抛出错误
    if (error.response) {
      // 服务器返回了错误响应
      throw new Error(error.response.data?.error || `服务器错误: ${error.response.status}`)
    } else if (error.request) {
      // 请求发送了但没有收到响应
      throw new Error('网络错误：无法连接到服务器')
    } else {
      // 其他错误
      throw new Error(error.message || '未知错误')
    }
  }
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
    
    // 处理数据 - 将中文字段名映射为英文字段名
    const processedData = data.map(row => {
      // 处理日期格式
      let dateValue = row['时间（年月）'];
      
      // 检查是否是Excel日期数值格式
      if (typeof dateValue === 'number' || (typeof dateValue === 'string' && !isNaN(dateValue) && !dateValue.includes('-') && !dateValue.includes('/'))) {
        // 将Excel日期数值转换为JavaScript日期对象
        const excelDate = parseInt(dateValue);
        const millisecondsPerDay = 24 * 60 * 60 * 1000;
        
        // 创建1900年1月1日的日期（Excel的起始日期）
        const excelStartDate = new Date(1900, 0, 1);
        
        // 如果日期大于60（1900年2月29日之后），需要减去1天（因为1900年不是闰年，但Excel认为是）
        const daysToAdd = excelDate > 60 ? excelDate - 1 : excelDate;
        
        // 计算JavaScript日期
        const jsDate = new Date(excelStartDate.getTime() + daysToAdd * millisecondsPerDay);
        
        // 格式化为YYYY-MM（月底库存只需要年月）
        dateValue = `${jsDate.getFullYear()}-${String(jsDate.getMonth() + 1).padStart(2, '0')}`;
      }
      
      return {
        date: dateValue,
        name: row['名称'],
        category: row['分类'],
        unitPrice: parseFloat(row['单价']) || 0,
        quantity: parseFloat(row['库存数量']) || 0,
        unit: row['单位'] || '千克' // 添加单位字段，默认为千克
      };
    });
    
    try {
      // 调用API将数据导入到后端数据库
      const apiResult = await importInventoryDataToAPI(processedData, inventoryImportMode.value)
      
      // 根据API返回结果更新显示
      if (apiResult.success) {
        inventoryImportResult.value = {
          success: true,
          message: inventoryImportMode.value === 'append' ? 
            '月底库存数据已成功添加到数据库' : 
            '月底库存数据已成功覆盖到数据库',
          details: {
            success: apiResult.successCount,
            failed: apiResult.failedCount
          }
        }
        
        if (apiResult.failedCount === 0) {
          ElMessage.success(`成功导入 ${apiResult.successCount} 条月底库存数据`)
        } else {
          ElMessage.warning(`导入完成：成功 ${apiResult.successCount} 条，失败 ${apiResult.failedCount} 条`)
        }
      } else {
        inventoryImportResult.value = {
          success: false,
          message: `导入部分失败：${apiResult.message}`,
          details: {
            success: apiResult.successCount,
            failed: apiResult.failedCount
          }
        }
        ElMessage.error(`导入失败：成功 ${apiResult.successCount} 条，失败 ${apiResult.failedCount} 条`)
      }
      
    } catch (apiError) {
      console.error('API调用失败:', apiError)
      inventoryImportResult.value = {
        success: false,
        message: `API调用失败: ${apiError.message || '网络错误'}`
      }
      ElMessage.error(`导入失败: ${apiError.message || '网络错误，请检查后端服务是否正常'}`)
    }
    
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

// 读取Excel文件
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

const downloadInventoryTemplate = () => {
  const templateData = [
    {
      '时间（年月）': '2025-06',
      '名称': '大米',
      '分类': '大米',
      '单价': 5.5,
      '库存数量': 100,
      '单位': '千克'
    },
    {
      '时间（年月）': '2025-06',
      '名称': '大豆油',
      '分类': '食用油类',
      '单价': 12.8,
      '库存数量': 20,
      '单位': '升'
    },
    {
      '时间（年月）': '2025-06',
      '名称': '生抽',
      '分类': '调味品类',
      '单价': 8.5,
      '库存数量': 5,
      '单位': '升'
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
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #333;
  margin-bottom: 10px;
}

.page-desc {
  color: #666;
  font-size: 14px;
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
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.upload-area:hover {
  border-color: #1890ff;
  background-color: #fafafa;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #d9d9d9;
}

.upload-text p {
  margin: 0;
  color: #666;
}

.upload-link {
  color: #1890ff;
  cursor: pointer;
}

.upload-link:hover {
  text-decoration: underline;
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
  background: #f8f9fa;
  border-radius: 8px;
}

.file-icon {
  font-size: 32px;
  color: #1890ff;
}

.file-details {
  flex: 1;
}

.file-name {
  margin: 0 0 5px 0;
  font-weight: 500;
  color: #333;
}

.file-size {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.import-options {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.option-label {
  font-weight: 500;
  color: #333;
}

.import-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.import-result {
  margin-top: 20px;
}

.result-details {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

.result-details p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}
</style>
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
            <span class="card-subtitle">上传Excel或CSV文件导入库存查询数据，用于入库记录管理</span>
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
      
      <div class="card-description">
        <div class="desc-content">
          <h4>功能说明</h4>
          <ul>
            <li><strong>数据用途：</strong>导入食材入库记录，包括入库时间、食材名称、分类、供应商、数量等信息</li>
            <li><strong>支持格式：</strong>Excel文件(.xlsx, .xls)和CSV文件，文件大小不超过10MB</li>
            <li><strong>必填字段：</strong>入库时间、食材名称、分类、供应商、数量、单位、单价、小计</li>
            <li><strong>导入方式：</strong>支持新增数据和覆盖数据两种模式</li>
          </ul>
        </div>
      </div>
      
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
          <el-radio-group v-model="importMode" size="small">
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
      
      <div class="card-description">
        <div class="desc-content">
          <h4>功能说明</h4>
          <ul>
            <li><strong>数据用途：</strong>导入每月月底的库存盘点数据，包括食材名称、分类、单价和库存数量</li>
            <li><strong>支持格式：</strong>Excel文件(.xlsx, .xls)和CSV文件，文件大小不超过10MB</li>
            <li><strong>必填字段：</strong>时间（年月）、名称、分类、单价、库存数量</li>
            <li><strong>导入方式：</strong>支持新增数据和覆盖数据两种模式</li>
          </ul>
        </div>
      </div>
      
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Upload, 
  Download, 
  UploadFilled, 
  Document, 
  Delete 
} from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// 响应式数据
const stockFile = ref(null)
const inventoryFile = ref(null)
const stockImporting = ref(false)
const inventoryImporting = ref(false)
const stockImportResult = ref(null)
const inventoryImportResult = ref(null)
const importMode = ref('append') // 导入模式：append(新增数据) 或 overwrite(覆盖数据)
const inventoryImportMode = ref('append') // 月底库存导入模式：append(新增数据) 或 overwrite(覆盖数据)

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

// 导入axios
import axios from 'axios'

// API函数：导入库存查询数据
const importStockDataToAPI = async (data, mode) => {
  try {
    // 使用axios直接调用后端API
    const response = await axios.post(`${API_BASE_URL}/api/stock-ins/batch`, {
      data: data,
      mode: mode // 'append' 或 'overwrite'
    });
    
    return response.data;
  } catch (error) {
    console.error('API导入失败:', error);
    
    // 如果API调用失败，使用localStorage作为备用
    console.log('使用localStorage作为备用存储');
    
    // 获取现有数据
    const existingData = JSON.parse(localStorage.getItem('stockQueryData') || '[]');
    let result = {
      success: true,
      overwritten: existingData.length,
      imported: data.length
    };
    
    // 根据模式处理数据
    if (mode === 'append') {
      localStorage.setItem('stockQueryData', JSON.stringify([...existingData, ...data]));
    } else {
      localStorage.setItem('stockQueryData', JSON.stringify(data));
    }
    
    throw error; // 继续抛出错误，让调用者知道API调用失败了
  }
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
    
    // 处理数据 - 将中文字段名映射为英文字段名
    const processedData = data.map((row, index) => {
      // 处理日期格式
      let inTime = row['入库时间'];
      
      // 检查是否是Excel日期数值格式（如45352）
      if (typeof inTime === 'number' || (typeof inTime === 'string' && !isNaN(inTime) && !inTime.includes('-') && !inTime.includes('/'))) {
        // 将Excel日期数值转换为JavaScript日期对象
        // Excel日期是从1900年1月1日开始的天数，而JavaScript日期是从1970年1月1日开始的毫秒数
        // 需要考虑Excel的1900年错误（Excel错误地认为1900年是闰年）
        const excelDate = parseInt(inTime);
        const millisecondsPerDay = 24 * 60 * 60 * 1000;
        
        // 创建1900年1月1日的日期（Excel的起始日期）
        const excelStartDate = new Date(1900, 0, 1);
        
        // 如果日期大于60（1900年2月29日之后），需要减去1天（因为1900年不是闰年，但Excel认为是）
        const daysToAdd = excelDate > 60 ? excelDate - 1 : excelDate;
        
        // 计算JavaScript日期
        const jsDate = new Date(excelStartDate.getTime() + daysToAdd * millisecondsPerDay);
        
        // 格式化为YYYY-MM-DD
        inTime = jsDate.toISOString().split('T')[0];
      }
      
      return {
        id: Date.now() + index, // 生成唯一ID
        in_time: inTime,
        name: row['食材名称'],
        category: row['分类'],
        supplier: row['供应商'],
        quantity: parseFloat(row['数量']) || 0,
        unit: row['单位'] || 'kg',
        price: parseFloat(row['单价']) || 0,
        subtotal: parseFloat(row['小计']) || 0,
        note: row['备注'] || ''
      };
    });
    
    try {
      // 调用API将数据导入到后端数据库
      const apiResult = await importStockDataToAPI(processedData, importMode.value)
      
      // 导入成功后，更新结果显示
      if (importMode.value === 'append') {
        stockImportResult.value = {
          success: true,
          message: '库存查询数据已成功添加',
          details: {
            success: processedData.length,
            failed: 0
          }
        }
        ElMessage.success(`成功添加 ${processedData.length} 条库存查询数据`)
      } else {
        stockImportResult.value = {
          success: true,
          message: '库存查询数据已成功覆盖',
          details: {
            success: processedData.length,
            failed: 0,
            overwritten: apiResult.overwritten || 0
          }
        }
        ElMessage.success(`已覆盖原有数据，导入 ${processedData.length} 条新数据`)
      }
    } catch (apiError) {
      console.error('API调用失败，使用本地存储作为备用:', apiError)
      
      // API调用失败，使用localStorage作为备用
      const existingData = JSON.parse(localStorage.getItem('stockQueryData') || '[]')
      let finalData = []
      
      if (importMode.value === 'append') {
        finalData = [...existingData, ...processedData]
        stockImportResult.value = {
          success: true,
          message: '库存查询数据已成功添加到本地存储（API调用失败）',
          details: {
            success: processedData.length,
            failed: 0
          }
        }
        ElMessage.warning(`API调用失败，数据已保存到本地存储。成功添加 ${processedData.length} 条库存查询数据`)
      } else {
        finalData = [...processedData]
        stockImportResult.value = {
          success: true,
          message: '库存查询数据已成功覆盖到本地存储（API调用失败）',
          details: {
            success: processedData.length,
            failed: 0,
            overwritten: existingData.length
          }
        }
        ElMessage.warning(`API调用失败，数据已保存到本地存储。已覆盖原有 ${existingData.length} 条数据，导入 ${processedData.length} 条新数据`)
      }
      
      // 更新localStorage
      localStorage.setItem('stockQueryData', JSON.stringify(finalData))
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
  
  // 添加分类说明
  const categorySheet = [
    { '分类名称': '大米', '说明': '主食类，包括各种大米' },
    { '分类名称': '食用油类', '说明': '各种食用油，如大豆油、花生油等' },
    { '分类名称': '调味品类', '说明': '调味料，如生抽、老抽、盐等' },
    { '分类名称': '蔬菜类', '说明': '新鲜蔬菜' },
    { '分类名称': '鲜肉类', '说明': '新鲜肉类' },
    { '分类名称': '冷冻类', '说明': '冷冻食品' },
    { '分类名称': '豆制品类', '说明': '豆腐、豆干等豆制品' },
    { '分类名称': '禽蛋类', '说明': '鸡蛋、鸭蛋等' },
    { '分类名称': '水果类', '说明': '各种水果' },
    { '分类名称': '点心类', '说明': '糕点、面包等' },
    { '分类名称': '面粉制品', '说明': '面条、面粉等' }
  ]
  
  try {
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    
    // 创建数据工作表
    const ws1 = XLSX.utils.json_to_sheet(templateData)
    XLSX.utils.book_append_sheet(wb, ws1, '月底库存数据模板')
    
    // 创建分类说明工作表
    const ws2 = XLSX.utils.json_to_sheet(categorySheet)
    XLSX.utils.book_append_sheet(wb, ws2, '分类说明')
    
    // 下载文件
    XLSX.writeFile(wb, '月底库存数据导入模板.xlsx')
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

.card-description {
  margin-bottom: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.desc-content h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.desc-content ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.desc-content li {
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 14px;
}

.desc-content li strong {
  color: #409eff;
  font-weight: 600;
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

.import-options {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.option-label {
  margin-right: 10px;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
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
  
  .card-description {
    margin-bottom: 15px;
    padding: 12px;
  }
  
  .desc-content h4 {
    font-size: 14px;
  }
  
  .desc-content li {
    font-size: 13px;
    margin-bottom: 6px;
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

<template>
  <div class="report-designer">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>报表设计及导出</h1>
      <p>使用可视化设计器创建个性化Excel报表模板</p>
    </div>

    <!-- 工具栏 -->
    <div class="designer-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="saveTemplate" :loading="saving">
          <el-icon><DocumentAdd /></el-icon>
          保存模板
        </el-button>
        <el-button @click="loadTemplate">
          <el-icon><FolderOpened /></el-icon>
          加载模板
        </el-button>
        <el-button type="success" @click="exportExcel">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button @click="clearAll" type="danger" plain>
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>

    <div class="designer-main">
      <!-- 左侧：Luckysheet Excel区域 -->
      <div class="excel-container">
        <div id="luckysheet" style="margin:0px;padding:0px;position:absolute;width:100%;height:100%;left: 0px;top: 0px;"></div>
      </div>

      <!-- 右侧：数据模块面板 -->
      <div class="modules-panel">
        <div class="panel-header">
          <h3>数据模块库</h3>
          <p class="panel-desc">拖拽或点击模块到左侧Excel中</p>
          <el-input 
            v-model="searchText" 
            placeholder="搜索模块..." 
            size="small"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="modules-content">
          <!-- 基础信息模块已移除 - 用户可以直接在Excel中手动输入标题、单位名称等信息 -->

          <!-- 每日数据模块 (31列) -->
          <div class="module-category">
            <div class="category-header">
              <el-icon><Calendar /></el-icon>
              <span>每日数据 (31列)</span>
            </div>
            <div class="module-list">
              <div 
                v-for="module in filteredDailyModules" 
                :key="module.id"
                class="module-card daily-module"
                :draggable="true"
                @dragstart="handleDragStart($event, module)"
                @click="insertModule(module)"
              >
                <div class="module-icon">📊</div>
                <div class="module-info">
                  <div class="module-title">{{ module.title }}</div>
                  <div class="module-desc">{{ module.description }}</div>
                  <div class="module-preview">
                    <span class="day-range">1日 → 31日</span>
                    <span class="sample-data">{{ module.sampleData }}</span>
                  </div>
                </div>
                <div class="module-badge">31列</div>
              </div>
            </div>
          </div>

          <!-- 汇总数据模块 -->
          <div class="module-category">
            <div class="category-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>汇总统计</span>
            </div>
            <div class="module-list">
              <div 
                v-for="module in filteredSummaryModules" 
                :key="module.id"
                class="module-card summary-module"
                :draggable="true"
                @dragstart="handleDragStart($event, module)"
                @click="insertModule(module)"
              >
                <div class="module-icon">🧮</div>
                <div class="module-info">
                  <div class="module-title">{{ module.title }}</div>
                  <div class="module-desc">{{ module.description }}</div>
                  <div class="module-data">{{ module.sampleData }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 格式化模块 -->
          <div class="module-category">
            <div class="category-header">
              <el-icon><Brush /></el-icon>
              <span>格式化</span>
            </div>
            <div class="module-list">
              <div 
                v-for="module in filteredFormatModules" 
                :key="module.id"
                class="module-card format-module"
                :draggable="true"
                @dragstart="handleDragStart($event, module)"
                @click="insertModule(module)"
              >
                <div class="module-icon">🎨</div>
                <div class="module-info">
                  <div class="module-title">{{ module.title }}</div>
                  <div class="module-desc">{{ module.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存模板对话框 -->
    <el-dialog v-model="saveDialogVisible" title="保存模板" width="500px">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称" required>
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="templateForm.description" 
            type="textarea" 
            placeholder="请输入模板描述"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSaveTemplate" :loading="saving">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  DocumentAdd, 
  FolderOpened, 
  Download, 
  Delete, 
  Search,
  Document,
  Calendar,
  DataAnalysis,
  Brush
} from '@element-plus/icons-vue'

export default {
  name: 'ReportDesigner',
  components: {
    DocumentAdd,
    FolderOpened,
    Download,
    Delete,
    Search,
    Document,
    Calendar,
    DataAnalysis,
    Brush
  },
  setup() {
    const saving = ref(false)
    const searchText = ref('')
    const saveDialogVisible = ref(false)
    const luckysheetInstance = ref(null)
    
    const templateForm = reactive({
      name: '',
      description: ''
    })

    // 基础信息模块 - 已移除，用户可以手动输入

    // 每日数据模块 (31列)
    const dailyModules = [
      {
        id: 'daily_vegetables',
        title: '每日蔬菜类支出',
        description: '31天蔬菜类每日支出金额',
        sampleData: '150.50, 120.30, 180.20...',
        type: 'daily',
        category: '蔬菜类',
        dataField: 'daily.vegetables',
        columns: 31
      },
      {
        id: 'daily_meat',
        title: '每日鲜肉类支出',
        description: '31天鲜肉类每日支出金额',
        sampleData: '280.00, 250.00, 320.00...',
        type: 'daily',
        category: '鲜肉类',
        dataField: 'daily.meat',
        columns: 31
      },
      {
        id: 'daily_frozen',
        title: '每日冷冻类支出',
        description: '31天冷冻类每日支出金额',
        sampleData: '80.00, 90.00, 75.00...',
        type: 'daily',
        category: '冷冻类',
        dataField: 'daily.frozen',
        columns: 31
      },
      {
        id: 'daily_tofu',
        title: '每日豆制品类支出',
        description: '31天豆制品类每日支出金额',
        sampleData: '45.00, 50.00, 40.00...',
        type: 'daily',
        category: '豆制品类',
        dataField: 'daily.tofu',
        columns: 31
      },
      {
        id: 'daily_eggs',
        title: '每日禽蛋类支出',
        description: '31天禽蛋类每日支出金额',
        sampleData: '60.00, 65.00, 55.00...',
        type: 'daily',
        category: '禽蛋类',
        dataField: 'daily.eggs',
        columns: 31
      },
      {
        id: 'daily_fruits',
        title: '每日水果类支出',
        description: '31天水果类每日支出金额',
        sampleData: '30.00, 35.00, 25.00...',
        type: 'daily',
        category: '水果类',
        dataField: 'daily.fruits',
        columns: 31
      },
      {
        id: 'daily_snacks',
        title: '每日点心类支出',
        description: '31天点心类每日支出金额',
        sampleData: '20.00, 25.00, 15.00...',
        type: 'daily',
        category: '点心类',
        dataField: 'daily.snacks',
        columns: 31
      },
      {
        id: 'daily_rice',
        title: '每日大米支出',
        description: '31天大米每日支出金额',
        sampleData: '100.00, 100.00, 100.00...',
        type: 'daily',
        category: '大米',
        dataField: 'daily.rice',
        columns: 31
      },
      {
        id: 'daily_flour',
        title: '每日面粉制品支出',
        description: '31天面粉制品每日支出金额',
        sampleData: '80.00, 85.00, 75.00...',
        type: 'daily',
        category: '面粉制品',
        dataField: 'daily.flour',
        columns: 31
      },
      {
        id: 'daily_oil',
        title: '每日食用油类支出',
        description: '31天食用油类每日支出金额',
        sampleData: '40.00, 45.00, 35.00...',
        type: 'daily',
        category: '食用油类',
        dataField: 'daily.oil',
        columns: 31
      },
      {
        id: 'daily_total',
        title: '每日支出合计',
        description: '31天每日支出总计金额',
        sampleData: '865.50, 865.30, 920.20...',
        type: 'daily',
        category: '合计',
        dataField: 'daily.total',
        columns: 31
      },
      {
        id: 'daily_diners',
        title: '每日就餐人数',
        description: '31天每日就餐人数',
        sampleData: '58, 58, 58...',
        type: 'daily',
        category: '就餐人数',
        dataField: 'daily.diners',
        columns: 31
      }
    ]

    // 汇总数据模块
    const summaryModules = [
      {
        id: 'total_vegetables',
        title: '蔬菜类月度合计',
        description: '本月蔬菜类支出总计',
        sampleData: '4,650.00',
        type: 'summary',
        category: '蔬菜类',
        dataField: 'totals.vegetables'
      },
      {
        id: 'total_meat',
        title: '鲜肉类月度合计',
        description: '本月鲜肉类支出总计',
        sampleData: '8,680.00',
        type: 'summary',
        category: '鲜肉类',
        dataField: 'totals.meat'
      },
      {
        id: 'total_frozen',
        title: '冷冻类月度合计',
        description: '本月冷冻类支出总计',
        sampleData: '2,480.00',
        type: 'summary',
        category: '冷冻类',
        dataField: 'totals.frozen'
      },
      {
        id: 'total_all',
        title: '月度总合计',
        description: '本月所有支出总计',
        sampleData: '26,850.00',
        type: 'summary',
        category: '总计',
        dataField: 'totals.all'
      },
      {
        id: 'avg_daily',
        title: '日均支出',
        description: '平均每日支出金额',
        sampleData: '865.80',
        type: 'summary',
        category: '平均值',
        dataField: 'totals.avgDaily'
      },
      {
        id: 'total_diners',
        title: '月度就餐总人次',
        description: '本月就餐总人次',
        sampleData: '1,798',
        type: 'summary',
        category: '就餐人次',
        dataField: 'totals.totalDiners'
      }
    ]

    // 格式化模块
    const formatModules = [
      {
        id: 'merge_title',
        title: '合并标题单元格',
        description: '将标题单元格合并居中',
        type: 'format',
        action: 'merge'
      },
      {
        id: 'bold_header',
        title: '表头加粗',
        description: '设置表头文字为粗体',
        type: 'format',
        action: 'bold'
      },
      {
        id: 'center_align',
        title: '居中对齐',
        description: '设置单元格内容居中对齐',
        type: 'format',
        action: 'center'
      },
      {
        id: 'add_border',
        title: '添加边框',
        description: '为选中区域添加边框',
        type: 'format',
        action: 'border'
      },
      {
        id: 'currency_format',
        title: '货币格式',
        description: '设置为货币格式显示',
        type: 'format',
        action: 'currency'
      }
    ]

    // 过滤后的模块 - 基础信息模块已移除

    const filteredDailyModules = computed(() => 
      dailyModules.filter(m => 
        m.title.includes(searchText.value) || 
        m.description.includes(searchText.value) ||
        m.category.includes(searchText.value)
      )
    )

    const filteredSummaryModules = computed(() => 
      summaryModules.filter(m => 
        m.title.includes(searchText.value) || 
        m.description.includes(searchText.value) ||
        m.category.includes(searchText.value)
      )
    )

    const filteredFormatModules = computed(() => 
      formatModules.filter(m => 
        m.title.includes(searchText.value) || 
        m.description.includes(searchText.value)
      )
    )

    // 初始化Luckysheet
    const initLuckysheet = () => {
      nextTick(() => {
        if (window.luckysheet) {
          const options = {
            container: 'luckysheet',
            title: '报表设计器',
            lang: 'zh',
            allowCopy: true,
            allowEdit: true,
            allowDelete: true,
            showtoolbar: true,
            showinfobar: true,
            showsheetbar: true,
            showstatisticBar: true,
            sheetBottomConfig: false,
            allowEdit: true,
            enableAddRow: true,
            enableAddCol: true,
            userInfo: false,
            myFolderUrl: '',
            data: [{
              name: "报表设计",
              color: "",
              index: 0,
              status: 1,
              order: 0,
              hide: 0,
              row: 50,
              column: 26,
              defaultRowHeight: 19,
              defaultColWidth: 73,
              celldata: [],
              config: {},
              scrollLeft: 0,
              scrollTop: 0,
              luckysheet_select_save: [],
              calcChain: [],
              isPivotTable: false,
              pivotTable: {},
              filter_select: {},
              filter: null,
              luckysheet_alternateformat_save: [],
              luckysheet_alternateformat_save_modelCustom: [],
              luckysheet_conditionformat_save: {},
              frozen: {},
              chart: [],
              zoomRatio: 1,
              image: [],
              showGridLines: 1,
              dataVerification: {}
            }],
            hook: {
              cellDragStop: function(cell, postion, sheetFile, ctx) {
                console.log('拖拽结束', cell, postion)
              }
            }
          }
          
          window.luckysheet.create(options)
          luckysheetInstance.value = window.luckysheet
          
          setupDropTarget()
        } else {
          console.error('Luckysheet未加载')
          ElMessage.error('Excel组件加载失败，请刷新页面重试')
        }
      })
    }

    // 设置拖拽目标
    const setupDropTarget = () => {
      const container = document.getElementById('luckysheet')
      if (container) {
        container.addEventListener('dragover', (e) => {
          e.preventDefault()
        })
        
        container.addEventListener('drop', (e) => {
          e.preventDefault()
          const moduleData = JSON.parse(e.dataTransfer.getData('application/json'))
          handleDropToSheet(moduleData, e)
        })
      }
    }

    // 拖拽开始
    const handleDragStart = (event, module) => {
      event.dataTransfer.setData('application/json', JSON.stringify(module))
      event.dataTransfer.effectAllowed = 'copy'
    }

    // 处理拖拽到表格
    const handleDropToSheet = (module, event) => {
      if (!luckysheetInstance.value) return
      
      const selection = luckysheetInstance.value.getRange()
      if (!selection || selection.length === 0) {
        ElMessage.warning('请先选择要插入数据的单元格')
        return
      }
      
      const startRow = selection[0].row[0]
      const startCol = selection[0].column[0]
      
      insertModuleData(module, startRow, startCol)
    }

    // 插入模块（点击插入）
    const insertModule = (module) => {
      if (!luckysheetInstance.value) return
      
      const selection = luckysheetInstance.value.getRange()
      if (!selection || selection.length === 0) {
        ElMessage.warning('请先选择要插入数据的单元格')
        return
      }
      
      const startRow = selection[0].row[0]
      const startCol = selection[0].column[0]
      
      insertModuleData(module, startRow, startCol)
    }

    // 插入模块数据
    const insertModuleData = (module, startRow, startCol) => {
      if (module.type === 'daily') {
        // 31列数据
        if (startCol + 30 >= 26) {
          ElMessage.warning('空间不足，无法插入31列数据。请选择更靠左的位置。')
          return
        }
        
        // 插入31列数据
        for (let i = 0; i < 31; i++) {
          const cellValue = `{${module.dataField}[${i}]}`
          luckysheetInstance.value.setCellValue(startRow, startCol + i, cellValue)
          
          luckysheetInstance.value.setRangeStyle({
            row: [startRow, startRow],
            column: [startCol + i, startCol + i]
          }, {
            bg: '#e6f3ff',
            fc: '#1890ff',
            bl: 1
          })
        }
        
        ElMessage.success(`已插入${module.title}（31列数据）`)
        
      } else if (module.type === 'summary') {
        const cellValue = `{${module.dataField}}`
        luckysheetInstance.value.setCellValue(startRow, startCol, cellValue)
        
        luckysheetInstance.value.setRangeStyle({
          row: [startRow, startRow],
          column: [startCol, startCol]
        }, {
          bg: '#f6ffed',
          fc: '#52c41a',
          bl: 1
        })
        
        ElMessage.success(`已插入${module.title}`)
        
      } else if (module.type === 'format') {
        applyFormat(module.action, startRow, startCol)
      }
    }

    // 应用格式
    const applyFormat = (action, row, col) => {
      const selection = luckysheetInstance.value.getRange()
      if (!selection || selection.length === 0) return
      
      const range = {
        row: selection[0].row,
        column: selection[0].column
      }
      
      switch (action) {
        case 'merge':
          luckysheetInstance.value.merge(range)
          break
        case 'bold':
          luckysheetInstance.value.setRangeStyle(range, { bl: 1 })
          break
        case 'center':
          luckysheetInstance.value.setRangeStyle(range, { vt: 1, ht: 1 })
          break
        case 'border':
          luckysheetInstance.value.setRangeStyle(range, { 
            bd: {
              color: '#000000',
              style: 1
            }
          })
          break
        case 'currency':
          luckysheetInstance.value.setRangeFormat(range, 'currency')
          break
      }
      
      ElMessage.success('格式应用成功')
    }

    // 保存模板
    const saveTemplate = () => {
      if (!luckysheetInstance.value) {
        ElMessage.error('Excel组件未初始化')
        return
      }
      
      templateForm.name = ''
      templateForm.description = ''
      saveDialogVisible.value = true
    }

    // 确认保存模板
    const confirmSaveTemplate = async () => {
      if (!templateForm.name.trim()) {
        ElMessage.error('请输入模板名称')
        return
      }

      saving.value = true
      try {
        const sheetData = luckysheetInstance.value.getAllSheets()
        
        const templateData = {
          name: templateForm.name,
          description: templateForm.description,
          sheetData: sheetData,
          created_at: new Date().toISOString()
        }

        const templates = JSON.parse(localStorage.getItem('reportDesignerTemplates') || '[]')
        templates.push({
          ...templateData,
          id: Date.now()
        })
        localStorage.setItem('reportDesignerTemplates', JSON.stringify(templates))
        
        ElMessage.success('模板保存成功')
        saveDialogVisible.value = false
      } catch (error) {
        console.error('保存模板失败:', error)
        ElMessage.error('保存模板失败')
      } finally {
        saving.value = false
      }
    }

    // 加载模板
    const loadTemplate = async () => {
      const templates = JSON.parse(localStorage.getItem('reportDesignerTemplates') || '[]')
      
      if (templates.length === 0) {
        ElMessage.warning('没有保存的模板')
        return
      }

      try {
        const templateNames = templates.map((t, i) => `${i + 1}. ${t.name}`).join('\n')
        const { value: templateIndex } = await ElMessageBox.prompt(
          '请选择要加载的模板：\n' + templateNames,
          '选择模板',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputPattern: /^[1-9]\d*$/,
            inputErrorMessage: '请输入有效的模板编号'
          }
        )

        const selectedTemplate = templates[parseInt(templateIndex) - 1]
        if (selectedTemplate && luckysheetInstance.value) {
          luckysheetInstance.value.loadUrl(selectedTemplate.sheetData)
          ElMessage.success(`已加载模板: ${selectedTemplate.name}`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('加载模板失败:', error)
          ElMessage.error('加载模板失败')
        }
      }
    }

    // 导出Excel
    const exportExcel = () => {
      if (!luckysheetInstance.value) {
        ElMessage.error('Excel组件未初始化')
        return
      }
      
      luckysheetInstance.value.exportXlsx('食堂报表模板.xlsx')
      ElMessage.success('Excel导出成功')
    }

    // 清空所有
    const clearAll = async () => {
      try {
        await ElMessageBox.confirm('确定要清空所有内容吗？', '确认清空', {
          type: 'warning'
        })
        
        if (luckysheetInstance.value) {
          luckysheetInstance.value.clearRange()
          ElMessage.success('已清空所有内容')
        }
      } catch (error) {
        // 用户取消
      }
    }

    onMounted(() => {
      if (window.luckysheet) {
        initLuckysheet()
      } else {
        ElMessage.error('Luckysheet未加载，请检查网络连接')
      }
    })

    onUnmounted(() => {
      if (luckysheetInstance.value) {
        luckysheetInstance.value.destroy()
      }
    })

    return {
      saving,
      searchText,
      saveDialogVisible,
      templateForm,
      filteredDailyModules,
      filteredSummaryModules,
      filteredFormatModules,
      handleDragStart,
      insertModule,
      saveTemplate,
      confirmSaveTemplate,
      loadTemplate,
      exportExcel,
      clearAll
    }
  }
}
</script>

<style scoped>
.report-designer {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.page-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 24px;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.designer-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1000;
}

.toolbar-left, .toolbar-right {
  display: flex;
  gap: 10px;
}

.designer-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.excel-container {
  flex: 1;
  position: relative;
  background: white;
  margin: 10px 0 10px 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.modules-panel {
  width: 380px;
  background: white;
  margin: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.panel-header h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.panel-desc {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 12px;
}

.modules-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.module-category {
  margin-bottom: 25px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module-card {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
  background: white;
  position: relative;
}

.module-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24,144,255,0.15);
  transform: translateY(-1px);
}

.module-card:active {
  cursor: grabbing;
}

.module-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.module-info {
  flex: 1;
  min-width: 0;
}

.module-title {
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 4px;
  color: #333;
}

.module-desc {
  font-size: 11px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 4px;
}

.module-data {
  font-size: 10px;
  color: #999;
  font-family: 'Courier New', monospace;
}

.module-preview {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.day-range {
  font-size: 10px;
  color: #1890ff;
  font-weight: bold;
}

.sample-data {
  font-size: 9px;
  color: #999;
  font-family: 'Courier New', monospace;
}

.module-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4d4f;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.basic-module {
  border-left: 4px solid #fa8c16;
}

.daily-module {
  border-left: 4px solid #1890ff;
}

.summary-module {
  border-left: 4px solid #52c41a;
}

.format-module {
  border-left: 4px solid #722ed1;
}

/* Luckysheet样式覆盖 */
:deep(.luckysheet-wa-editor) {
  z-index: 999 !important;
}

:deep(.luckysheet-modal-dialog-mask) {
  z-index: 1000 !important;
}
</style>
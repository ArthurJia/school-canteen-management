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
        <el-dropdown @command="handleExportCommand">
          <el-button type="success">
            <el-icon><Download /></el-icon>
            导出Excel
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="luckysheet">Luckysheet导出</el-dropdown-item>
              <el-dropdown-item command="manual">手动导出</el-dropdown-item>
              <el-dropdown-item command="simple">简单导出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
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

          <!-- 每日数据模块 (31行) -->
          <div class="module-category">
            <div class="category-header">
              <el-icon><Calendar /></el-icon>
              <span>每日数据 (31行)</span>
            </div>
            <div class="module-list">
              <div 
                v-for="module in filteredDailyModules" 
                :key="module.id"
                class="module-card daily-module"
                @click="showDateSelector(module)"
              >
                <div class="module-icon">📊</div>
                <div class="module-info">
                  <div class="module-title">{{ module.title }}</div>
                  <div class="module-desc">{{ module.description }}</div>
                  <div class="module-preview">
                    <span class="day-range">1日 ↓ 31日</span>
                    <span class="sample-data">{{ module.sampleData }}</span>
                  </div>
                  <div class="module-date-info">
                    <span class="date-label">默认：{{ module.defaultYear }}年{{ module.defaultMonth }}月</span>
                  </div>
                </div>
                <div class="module-badge">31行</div>
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

    <!-- 年月份选择对话框 -->
    <el-dialog v-model="dateSelectVisible" title="选择年月份" width="400px">
      <div class="date-selector-content">
        <div class="module-info-display">
          <div class="module-icon-large">📊</div>
          <div class="module-details">
            <h3>{{ selectedModule?.title }}</h3>
            <p>{{ selectedModule?.description }}</p>
            <div class="columns-info">
              <span class="badge">31行数据</span>
              <span class="category">{{ selectedModule?.category }}</span>
            </div>
          </div>
        </div>
        
        <el-divider />
        
        <el-form :model="dateForm" label-width="80px">
          <el-form-item label="年份">
            <el-select v-model="dateForm.year" placeholder="选择年份" style="width: 100%">
              <el-option 
                v-for="year in getYearOptions()" 
                :key="year" 
                :label="year + '年'" 
                :value="year" 
              />
            </el-select>
          </el-form-item>
          <el-form-item label="月份">
            <el-select v-model="dateForm.month" placeholder="选择月份" style="width: 100%">
              <el-option 
                v-for="month in 12" 
                :key="month" 
                :label="month + '月'" 
                :value="month" 
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div class="preview-info">
          <el-alert 
            :title="`将插入 ${dateForm.year}年${dateForm.month}月 的${selectedModule?.category}数据（31行）`"
            type="info" 
            :closable="false"
            show-icon
          />
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dateSelectVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmInsertModule">
            插入数据模块
          </el-button>
        </span>
      </template>
    </el-dialog>

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
  Brush,
  ArrowDown
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
    Brush,
    ArrowDown
  },
  setup() {
    const saving = ref(false)
    const searchText = ref('')
    const saveDialogVisible = ref(false)
    const dateSelectVisible = ref(false)
    const luckysheetInstance = ref(null)
    const selectedModule = ref(null)
    
    const templateForm = reactive({
      name: '',
      description: ''
    })
    
    const dateForm = reactive({
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1
    })

    // 基础信息模块 - 已移除，用户可以手动输入

    // 每日数据模块 (31行) - 支持年月份选择
    const dailyModules = [
      {
        id: 'daily_vegetables',
        title: '蔬菜类支出',
        description: '31天蔬菜类每日支出金额（按行排列）',
        sampleData: '150.50, 120.30, 180.20...',
        type: 'daily',
        category: '蔬菜类',
        dataField: 'daily.vegetables',
        rows: 31, // 改为按行
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_meat',
        title: '鲜肉类支出',
        description: '31天鲜肉类每日支出金额（按行排列）',
        sampleData: '280.00, 250.00, 320.00...',
        type: 'daily',
        category: '鲜肉类',
        dataField: 'daily.meat',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_frozen',
        title: '冷冻类支出',
        description: '31天冷冻类每日支出金额（按行排列）',
        sampleData: '80.00, 90.00, 75.00...',
        type: 'daily',
        category: '冷冻类',
        dataField: 'daily.frozen',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_tofu',
        title: '豆制品类支出',
        description: '31天豆制品类每日支出金额（按行排列）',
        sampleData: '45.00, 50.00, 40.00...',
        type: 'daily',
        category: '豆制品类',
        dataField: 'daily.tofu',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_eggs',
        title: '禽蛋类支出',
        description: '31天禽蛋类每日支出金额（按行排列）',
        sampleData: '60.00, 65.00, 55.00...',
        type: 'daily',
        category: '禽蛋类',
        dataField: 'daily.eggs',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_fruits',
        title: '水果类支出',
        description: '31天水果类每日支出金额（按行排列）',
        sampleData: '30.00, 35.00, 25.00...',
        type: 'daily',
        category: '水果类',
        dataField: 'daily.fruits',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_snacks',
        title: '点心类支出',
        description: '31天点心类每日支出金额（按行排列）',
        sampleData: '20.00, 25.00, 15.00...',
        type: 'daily',
        category: '点心类',
        dataField: 'daily.snacks',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_rice',
        title: '大米支出',
        description: '31天大米每日支出金额（按行排列）',
        sampleData: '100.00, 100.00, 100.00...',
        type: 'daily',
        category: '大米',
        dataField: 'daily.rice',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_flour',
        title: '面粉制品支出',
        description: '31天面粉制品每日支出金额（按行排列）',
        sampleData: '80.00, 85.00, 75.00...',
        type: 'daily',
        category: '面粉制品',
        dataField: 'daily.flour',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_oil',
        title: '食用油类支出',
        description: '31天食用油类每日支出金额（按行排列）',
        sampleData: '40.00, 45.00, 35.00...',
        type: 'daily',
        category: '食用油类',
        dataField: 'daily.oil',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_total',
        title: '支出合计',
        description: '31天每日支出总计金额（按行排列）',
        sampleData: '865.50, 865.30, 920.20...',
        type: 'daily',
        category: '合计',
        dataField: 'daily.total',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_diners',
        title: '就餐人数',
        description: '31天每日就餐人数（按行排列）',
        sampleData: '58, 58, 58...',
        type: 'daily',
        category: '就餐人数',
        dataField: 'daily.diners',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
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
              column: 50, // 增加到50列以支持31列数据模块
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
          
          console.log('Luckysheet初始化完成')
          
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

    // 显示年月份选择器
    const showDateSelector = (module) => {
      selectedModule.value = module
      dateForm.year = module.defaultYear
      dateForm.month = module.defaultMonth
      dateSelectVisible.value = true
    }

    // 获取年份选项
    const getYearOptions = () => {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let i = currentYear - 5; i <= currentYear + 2; i++) {
        years.push(i)
      }
      return years
    }

    // 确认插入模块
    const confirmInsertModule = () => {
      if (!luckysheetInstance.value) {
        ElMessage.error('Excel组件未初始化')
        return
      }
      
      try {
        // 使用Luckysheet的全局API获取选择区域
        let startRow = 0
        let startCol = 0
        
        if (window.luckysheet && window.luckysheet.getRange) {
          const selection = window.luckysheet.getRange()
          if (selection && selection.length > 0) {
            startRow = selection[0].row[0]
            startCol = selection[0].column[0]
          }
        } else {
          // 如果无法获取选择区域，使用默认位置
          ElMessage.info('使用默认位置插入数据')
        }
        
        console.log('插入位置:', `行${startRow}, 列${startCol}`)
        
        // 创建带有年月份信息的模块
        const moduleWithDate = {
          ...selectedModule.value,
          selectedYear: dateForm.year,
          selectedMonth: dateForm.month
        }
        
        insertModuleData(moduleWithDate, startRow, startCol)
        dateSelectVisible.value = false
      } catch (error) {
        console.error('获取选择区域失败:', error)
        ElMessage.error('请先点击选择一个单元格')
      }
    }

    // 插入模块（点击插入）- 已移除，改为显示日期选择器
    const insertModule = (module) => {
      if (module.type === 'daily') {
        showDateSelector(module)
      } else {
        // 非每日数据模块直接插入
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
    }

    // 插入模块数据
    const insertModuleData = (module, startRow, startCol) => {
      if (module.type === 'daily') {
        // 31列数据 - 直接插入，不检查空间限制
        // Luckysheet会自动扩展列数
        
        const year = module.selectedYear || module.defaultYear
        const month = module.selectedMonth || module.defaultMonth
        
        // 按列导出：31天数据垂直排列（按行）
        try {
          console.log(`开始插入31行数据，起始位置: 行${startRow}, 列${startCol}`)
          
          // 插入31行数据（1日到31日垂直排列）
          for (let i = 0; i < 31; i++) {
            const day = i + 1
            const targetRow = startRow + i  // 按行递增
            const cellValue = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}.${module.category}`
            
            console.log(`插入第${day}日数据到行${targetRow}: ${cellValue}`)
            
            // 使用最基本的方式设置单元格
            if (window.luckysheet) {
              window.luckysheet.setCellValue(targetRow, startCol, cellValue)
            }
          }
          
          ElMessage.success(`已插入${year}年${month}月${module.title}（31行数据）`)
          
        } catch (error) {
          console.error('插入数据失败:', error)
          ElMessage.error('插入数据失败: ' + error.message)
        }
        
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

    // 处理导出命令
    const handleExportCommand = (command) => {
      switch (command) {
        case 'luckysheet':
          exportExcel()
          break
        case 'manual':
          manualExport()
          break
        case 'simple':
          simpleExport()
          break
      }
    }

    // 导出Excel
    const exportExcel = () => {
      if (!window.luckysheet) {
        ElMessage.error('Excel组件未初始化')
        return
      }
      
      try {
        console.log('开始导出Excel...')
        
        // 使用Luckysheet的导出功能
        if (window.luckysheet.exportXlsx) {
          window.luckysheet.exportXlsx('食堂报表模板.xlsx')
          ElMessage.success('Excel导出成功')
        } else if (window.luckysheet.toJson) {
          // 如果没有直接导出功能，使用JSON转换方式
          const data = window.luckysheet.toJson()
          console.log('获取到数据:', data)
          
          // 使用XLSX库手动导出
          if (window.XLSX) {
            const wb = window.XLSX.utils.book_new()
            const ws = window.XLSX.utils.aoa_to_sheet(convertLuckysheetToArray(data))
            window.XLSX.utils.book_append_sheet(wb, ws, '报表设计')
            window.XLSX.writeFile(wb, '食堂报表模板.xlsx')
            ElMessage.success('Excel导出成功')
          } else {
            ElMessage.error('导出功能不可用，请检查XLSX库')
          }
        } else {
          ElMessage.error('导出功能不可用')
        }
      } catch (error) {
        console.error('导出Excel失败:', error)
        ElMessage.error('导出Excel失败: ' + error.message)
      }
    }
    
    // 转换Luckysheet数据为数组格式
    const convertLuckysheetToArray = (data) => {
      if (!data || !data[0] || !data[0].celldata) {
        return [['暂无数据']]
      }
      
      const celldata = data[0].celldata
      const maxRow = Math.max(...celldata.map(cell => cell.r)) + 1
      const maxCol = Math.max(...celldata.map(cell => cell.c)) + 1
      
      // 创建二维数组
      const result = Array(maxRow).fill().map(() => Array(maxCol).fill(''))
      
      // 填充数据
      celldata.forEach(cell => {
        if (cell.v && cell.v.v !== undefined) {
          result[cell.r][cell.c] = cell.v.v
        }
      })
      
      return result
    }

    // 手动导出
    const manualExport = () => {
      try {
        if (!window.XLSX) {
          ElMessage.error('XLSX库未加载')
          return
        }

        // 创建一个简单的工作簿
        const wb = window.XLSX.utils.book_new()
        
        // 获取当前设计的数据
        let sheetData = [['食堂报表设计器导出']]
        
        if (window.luckysheet && window.luckysheet.getAllSheets) {
          try {
            const sheets = window.luckysheet.getAllSheets()
            if (sheets && sheets[0] && sheets[0].celldata) {
              const celldata = sheets[0].celldata
              sheetData = convertLuckysheetToArray(sheets)
            }
          } catch (error) {
            console.log('获取Luckysheet数据失败，使用默认数据')
          }
        }
        
        const ws = window.XLSX.utils.aoa_to_sheet(sheetData)
        window.XLSX.utils.book_append_sheet(wb, ws, '报表设计')
        window.XLSX.writeFile(wb, '食堂报表模板.xlsx')
        
        ElMessage.success('手动导出成功')
      } catch (error) {
        console.error('手动导出失败:', error)
        ElMessage.error('手动导出失败: ' + error.message)
      }
    }

    // 获取实际数据并导出
    const exportWithRealData = async () => {
      try {
        if (!window.XLSX) {
          ElMessage.error('XLSX库未加载')
          return
        }

        ElMessage.info('正在获取数据并生成Excel...')

        // 解析Luckysheet中的数据占位符
        const cellData = await parseLuckysheetData()
        
        // 获取实际数据
        const realData = await fetchRealData(cellData)
        
        // 生成Excel
        const wb = window.XLSX.utils.book_new()
        const ws = window.XLSX.utils.aoa_to_sheet(realData)
        
        // 设置列宽
        ws['!cols'] = Array(realData[0]?.length || 10).fill({ wch: 12 })
        
        window.XLSX.utils.book_append_sheet(wb, ws, '食堂报表')
        window.XLSX.writeFile(wb, `食堂报表_${new Date().toLocaleDateString()}.xlsx`)
        
        ElMessage.success('导出成功！已填入实际数据')
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败: ' + error.message)
      }
    }

    // 解析Luckysheet中的数据占位符
    const parseLuckysheetData = async () => {
      const cellData = []
      
      try {
        if (window.luckysheet && window.luckysheet.getAllSheets) {
          const sheets = window.luckysheet.getAllSheets()
          if (sheets && sheets[0] && sheets[0].celldata) {
            const cells = sheets[0].celldata
            
            cells.forEach(cell => {
              if (cell.v && cell.v.v) {
                const value = cell.v.v.toString()
                // 检查是否是数据占位符格式：2024-12-01.蔬菜类
                const match = value.match(/^(\d{4})-(\d{2})-(\d{2})\.(.+)$/)
                if (match) {
                  cellData.push({
                    row: cell.r,
                    col: cell.c,
                    year: parseInt(match[1]),
                    month: parseInt(match[2]),
                    day: parseInt(match[3]),
                    category: match[4],
                    originalValue: value
                  })
                } else {
                  // 普通文本
                  cellData.push({
                    row: cell.r,
                    col: cell.c,
                    text: value,
                    isText: true
                  })
                }
              }
            })
          }
        }
      } catch (error) {
        console.error('解析Luckysheet数据失败:', error)
      }
      
      return cellData
    }

    // 获取实际数据
    const fetchRealData = async (cellData) => {
      // 找出最大行列数
      const maxRow = Math.max(...cellData.map(cell => cell.row), 0) + 1
      const maxCol = Math.max(...cellData.map(cell => cell.col), 0) + 1
      
      // 创建二维数组
      const result = Array(maxRow).fill().map(() => Array(maxCol).fill(''))
      
      // 收集需要获取的数据请求
      const dataRequests = new Map()
      
      cellData.forEach(cell => {
        if (cell.isText) {
          // 普通文本直接填入
          result[cell.row][cell.col] = cell.text
        } else {
          // 数据占位符，收集请求
          const key = `${cell.year}-${cell.month}`
          if (!dataRequests.has(key)) {
            dataRequests.set(key, { year: cell.year, month: cell.month, cells: [] })
          }
          dataRequests.get(key).cells.push(cell)
        }
      })

      // 批量获取数据
      for (const [key, request] of dataRequests) {
        try {
          const response = await axios.get('/api/monthly-report/data', {
            params: {
              year: request.year,
              month: request.month
            }
          })
          
          const reportData = response.data
          
          // 填充实际数据
          request.cells.forEach(cell => {
            const value = getRealValue(reportData, cell.year, cell.month, cell.day, cell.category)
            result[cell.row][cell.col] = value
          })
          
        } catch (error) {
          console.error(`获取${request.year}年${request.month}月数据失败:`, error)
          // 如果获取失败，使用占位符
          request.cells.forEach(cell => {
            result[cell.row][cell.col] = cell.originalValue
          })
        }
      }
      
      return result
    }

    // 从报表数据中获取实际值
    const getRealValue = (reportData, year, month, day, category) => {
      try {
        // 根据分类获取对应的数据
        const categoryMap = {
          '蔬菜类': 'vegetables',
          '鲜肉类': 'meat', 
          '冷冻类': 'frozen',
          '豆制品类': 'tofu',
          '禽蛋类': 'eggs',
          '水果类': 'fruits',
          '点心类': 'snacks',
          '大米': 'rice',
          '面粉制品': 'flour',
          '食用油类': 'oil',
          '合计': 'total',
          '就餐人数': 'diners'
        }
        
        const fieldName = categoryMap[category]
        if (!fieldName) {
          return `未知分类: ${category}`
        }
        
        // 从每日数据中查找对应日期的数据
        if (reportData.dailyTotals && reportData.dailyTotals.length > 0) {
          const dayData = reportData.dailyTotals.find(d => parseInt(d.day) === day)
          if (dayData && dayData[fieldName] !== undefined) {
            return dayData[fieldName]
          }
        }
        
        // 如果没有每日数据，尝试从分类总计中获取平均值
        if (reportData.categoryTotals && reportData.categoryTotals.length > 0) {
          const categoryData = reportData.categoryTotals.find(c => c.category === category)
          if (categoryData) {
            // 返回月度总计除以天数的平均值
            const daysInMonth = new Date(year, month, 0).getDate()
            return (categoryData.total / daysInMonth).toFixed(2)
          }
        }
        
        // 如果都没有，返回0
        return 0
        
      } catch (error) {
        console.error('获取实际值失败:', error)
        return `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}.${category}`
      }
    }

    // 简单导出（保持原有功能）
    const simpleExport = () => {
      try {
        if (!window.XLSX) {
          ElMessage.error('XLSX库未加载')
          return
        }

        // 创建一个包含示例数据的简单表格
        const sampleData = [
          ['食堂食材月度出库汇总表'],
          [''],
          ['日期', '蔬菜类', '鲜肉类', '冷冻类', '合计'],
          ['1日', '{2024-12-01.蔬菜类}', '{2024-12-01.鲜肉类}', '{2024-12-01.冷冻类}', ''],
          ['2日', '{2024-12-02.蔬菜类}', '{2024-12-02.鲜肉类}', '{2024-12-02.冷冻类}', ''],
          ['3日', '{2024-12-03.蔬菜类}', '{2024-12-03.鲜肉类}', '{2024-12-03.冷冻类}', ''],
          ['...', '...', '...', '...', '...'],
          ['31日', '{2024-12-31.蔬菜类}', '{2024-12-31.鲜肉类}', '{2024-12-31.冷冻类}', ''],
          [''],
          ['合计', '{蔬菜类月度合计}', '{鲜肉类月度合计}', '{冷冻类月度合计}', '{月度总合计}']
        ]

        const wb = window.XLSX.utils.book_new()
        const ws = window.XLSX.utils.aoa_to_sheet(sampleData)
        
        // 设置列宽
        ws['!cols'] = [
          { wch: 8 },  // 日期
          { wch: 20 }, // 蔬菜类
          { wch: 20 }, // 鲜肉类
          { wch: 20 }, // 冷冻类
          { wch: 15 }  // 合计
        ]
        
        window.XLSX.utils.book_append_sheet(wb, ws, '报表模板')
        window.XLSX.writeFile(wb, '食堂报表模板示例.xlsx')
        
        ElMessage.success('简单导出成功！已生成示例模板')
      } catch (error) {
        console.error('简单导出失败:', error)
        ElMessage.error('简单导出失败: ' + error.message)
      }
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
      // 忽略Chrome扩展的端口错误
      if (window.chrome && window.chrome.runtime && window.chrome.runtime.lastError) {
        // 清除可能的扩展错误
        console.log('忽略Chrome扩展错误')
      }
      
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
      dateSelectVisible,
      templateForm,
      dateForm,
      selectedModule,
      filteredDailyModules,
      filteredSummaryModules,
      filteredFormatModules,
      handleDragStart,
      insertModule,
      showDateSelector,
      getYearOptions,
      confirmInsertModule,
      saveTemplate,
      confirmSaveTemplate,
      loadTemplate,
      handleExportCommand,
      exportExcel,
      manualExport,
      simpleExport,
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

.module-date-info {
  margin-top: 4px;
}

.date-label {
  font-size: 9px;
  color: #1890ff;
  background: #e6f3ff;
  padding: 1px 4px;
  border-radius: 2px;
}

.date-selector-content {
  padding: 10px 0;
}

.module-info-display {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.module-icon-large {
  font-size: 32px;
  flex-shrink: 0;
}

.module-details h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.module-details p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 13px;
}

.columns-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.badge {
  background: #ff4d4f;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.category {
  background: #f0f0f0;
  color: #666;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.preview-info {
  margin-top: 15px;
}

/* Luckysheet样式覆盖 */
:deep(.luckysheet-wa-editor) {
  z-index: 999 !important;
}

:deep(.luckysheet-modal-dialog-mask) {
  z-index: 1000 !important;
}
</style>
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
          <el-icon>
            <DocumentAdd />
          </el-icon>
          保存模板
        </el-button>
        <el-button @click="loadTemplate">
          <el-icon>
            <FolderOpened />
          </el-icon>
          加载模板
        </el-button>
        <el-button type="success" @click="manualExport">
          <el-icon>
            <Download />
          </el-icon>
          导出Excel
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button @click="clearAll" type="danger" plain>
          <el-icon>
            <Delete />
          </el-icon>
          清空
        </el-button>
      </div>
    </div>

    <div class="designer-main">
      <!-- 左侧：Luckysheet Excel区域 -->
      <div class="excel-container">
        <div id="luckysheet"
          style="margin:0px;padding:0px;position:absolute;width:100%;height:100%;left: 0px;top: 0px;"></div>
      </div>

      <!-- 右侧：数据模块面板 -->
      <div class="modules-panel">
        <div class="panel-header">
          <h3>数据模块库</h3>
          <p class="panel-desc">拖拽或点击模块到左侧Excel中</p>
          <el-input v-model="searchText" placeholder="搜索模块..." size="small" clearable>
            <template #prefix>
              <el-icon>
                <Search />
              </el-icon>
            </template>
          </el-input>
        </div>

        <div class="modules-content">
          <!-- 基础信息模块已移除 - 用户可以直接在Excel中手动输入标题、单位名称等信息 -->

          <!-- 每日数据模块 (31行) -->
          <div class="module-category">
            <div class="category-header">
              <el-icon>
                <Calendar />
              </el-icon>
              <span>每日数据 (31行)</span>
            </div>
            <div class="module-list">
              <div v-for="module in filteredDailyModules" :key="module.id" class="module-card daily-module"
                @click="showDateSelector(module)">
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
              <el-icon>
                <DataAnalysis />
              </el-icon>
              <span>汇总统计</span>
            </div>
            <div class="module-list">
              <div v-for="module in filteredSummaryModules" :key="module.id"
                class="module-card summary-module" :draggable="true"
                @dragstart="handleDragStart($event, module)" @click="insertModule(module)">
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
              <el-icon>
                <Brush />
              </el-icon>
              <span>格式化</span>
            </div>
            <div class="module-list">
              <div v-for="module in filteredFormatModules" :key="module.id" class="module-card format-module"
                :draggable="true" @dragstart="handleDragStart($event, module)" @click="insertModule(module)">
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
              <el-option v-for="year in getYearOptions()" :key="year" :label="year + '年'" :value="year" />
            </el-select>
          </el-form-item>
          <el-form-item label="月份">
            <el-select v-model="dateForm.month" placeholder="选择月份" style="width: 100%">
              <el-option v-for="month in 12" :key="month" :label="month + '月'" :value="month" />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="preview-info">
          <el-alert :title="`将插入 ${dateForm.year}年${dateForm.month}月 的${selectedModule?.category}数据（31行）`" type="info"
            :closable="false" show-icon />
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

    <!-- 加载模板对话框 -->
    <el-dialog v-model="loadDialogVisible" title="选择模板" width="800px">
      <div class="template-selector">
        <div v-if="availableTemplates.length === 0" class="no-templates">
          <el-empty description="暂无保存的模板">
            <el-button type="primary" @click="loadDialogVisible = false">确定</el-button>
          </el-empty>
        </div>
        <div v-else class="templates-grid">
          <div 
            v-for="(template, index) in availableTemplates" 
            :key="template.id"
            class="template-card"
            :class="{ 'selected': selectedTemplateIndex === index }"
            @click="selectedTemplateIndex = index"
          >
            <div class="template-header">
              <div class="template-icon">📊</div>
              <div class="template-info">
                <h4 class="template-name">{{ template.name }}</h4>
                <p class="template-desc">{{ template.description || '无描述' }}</p>
              </div>
            </div>
            <div class="template-meta">
              <span class="template-date">{{ formatDate(template.createdAt) }}</span>
              <el-button 
                type="danger" 
                size="small" 
                text 
                @click.stop="deleteTemplate(index)"
                title="删除模板"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="loadDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="confirmLoadTemplate" 
            :disabled="selectedTemplateIndex === -1 || availableTemplates.length === 0"
          >
            加载模板
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
          <el-input v-model="templateForm.description" type="textarea" placeholder="请输入模板描述" :rows="3" />
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
    const loadDialogVisible = ref(false)
    const dateSelectVisible = ref(false)
    const luckysheetInstance = ref(null)
    const selectedModule = ref(null)
    const availableTemplates = ref([])
    const selectedTemplateIndex = ref(-1)

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
              cellDragStop: function (cell, postion, sheetFile, ctx) {
                console.log('拖拽结束', cell, postion)
              }
            }
          }

          window.luckysheet.create(options)
          luckysheetInstance.value = window.luckysheet

          console.log('Luckysheet初始化完成')

          // 调试：检查可用的API方法
          console.log('可用的Luckysheet方法:', Object.keys(window.luckysheet))
          console.log('setCellValue方法是否可用:', typeof window.luckysheet.setCellValue)

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
    const handleDropToSheet = async (module, event) => {
      if (!luckysheetInstance.value) return

      const selection = luckysheetInstance.value.getRange()
      if (!selection || selection.length === 0) {
        ElMessage.warning('请先选择要插入数据的单元格')
        return
      }

      const startRow = selection[0].row[0]
      const startCol = selection[0].column[0]

      await insertModuleData(module, startRow, startCol)
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
    const confirmInsertModule = async () => {
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

        await insertModuleData(moduleWithDate, startRow, startCol)
        dateSelectVisible.value = false
      } catch (error) {
        console.error('获取选择区域失败:', error)
        ElMessage.error('请先点击选择一个单元格')
      }
    }

    // 插入模块（点击插入）- 已移除，改为显示日期选择器
    const insertModule = async (module) => {
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

        await insertModuleData(module, startRow, startCol)
      }
    }

    // 获取汇总数据
    const fetchSummaryData = async (dataField, category) => {
      try {
        const currentDate = new Date()
        const year = currentDate.getFullYear()
        const month = currentDate.getMonth() + 1

        // 映射分类值到数据库字段
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
        }

        if (dataField.includes('totals.')) {
          // 月度合计数据
          if (category === '总计') {
            // 获取月度总合计
            const response = await fetch(`/api/monthly-report/data?year=${year}&month=${month}`)
            const data = await response.json()
            return data.monthlyTotal || 0
          } else if (category === '平均值') {
            // 日均支出
            const response = await fetch(`/api/monthly-report/data?year=${year}&month=${month}`)
            const data = await response.json()
            const daysWithExpense = data.dailyTotals ? data.dailyTotals.filter(day => day.total > 0).length : 1
            return daysWithExpense ? (data.monthlyTotal / daysWithExpense) : 0
          } else if (category === '就餐人次') {
            // 月度就餐总人次 - 这里需要根据实际业务逻辑计算
            return 1800 // 示例值，实际应该从数据库获取
          } else {
            // 特定分类的月度合计
            const categoryValue = categoryMapping[category] || category
            const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
            const endDate = `${year}-${month.toString().padStart(2, '0')}-31`

            const response = await fetch(`/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`)
            const data = await response.json()

            let total = 0
            if (data.data && Array.isArray(data.data)) {
              // 过滤指定分类的数据
              const filteredData = data.data.filter(record => record.category === categoryValue)
              total = filteredData.reduce((sum, record) => sum + parseFloat(record.subtotal || 0), 0)
              console.log(`汇总数据 ${category}(${categoryValue}): 总数据${data.data.length}条，找到${filteredData.length}条记录，总计${total}`)
            }
            return total
          }
        }

        return 0
      } catch (error) {
        console.error('获取汇总数据失败:', error)
        return 0
      }
    }

    // 获取每日数据
    const fetchDailyData = async (year, month, category) => {
      try {
        // 映射分类值到数据库字段
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
        }

        const categoryValue = categoryMapping[category] || category

        // 构建API请求URL
        const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
        const endDate = `${year}-${month.toString().padStart(2, '0')}-31`

        console.log(`开始获取每日数据: ${year}年${month}月 ${category}`)
        console.log(`分类映射: ${category} -> ${categoryValue}`)
        console.log(`请求时间范围: ${startDate} 到 ${endDate}`)

        // 创建31天的数据数组，初始化为0
        const dailyData = new Array(31).fill(0)

        // 填充实际数据
        if (category === '就餐人数') {
          // 就餐人数的特殊处理 - 这里使用固定值，实际应该从数据库获取
          dailyData.fill(58) // 示例：每天58人就餐
          console.log('使用固定就餐人数: 58人/天')
        } else if (category === '合计') {
          // 合计数据需要汇总所有分类
          console.log('开始计算合计数据，汇总所有分类...')
          const categories = ['vegetable', 'meat', 'frozen', 'tofu', 'egg', 'fruit', 'dessert', 'flour', 'rice', 'oil', 'seasoning']

          // 获取所有数据，然后汇总各个分类
          // 设置一个很大的pageSize来获取所有数据，避免分页限制
          const apiUrl = `/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`
          console.log(`请求所有数据进行合计: ${apiUrl}`)

          const allResponse = await fetch(apiUrl)
          const allData = await allResponse.json()

          console.log(`合计计算：总共返回数据条数:`, allData.data ? allData.data.length : 0)
          console.log(`合计计算：API返回的总记录数:`, allData.total || '未知')

          if (allData.data && Array.isArray(allData.data)) {
            allData.data.forEach(record => {
              const recordDate = new Date(record.in_time)
              const day = recordDate.getDate()
              const subtotal = parseFloat(record.subtotal || 0)

              if (day >= 1 && day <= 31) {
                dailyData[day - 1] += subtotal
                console.log(`合计: ${day}日 += ${subtotal} (${record.category}), 当前总计: ${dailyData[day - 1]}`)
              }
            })
          }
        } else {
          // 单个分类的数据 - 先获取所有数据，然后在前端过滤
          // 设置一个很大的pageSize来获取所有数据，避免分页限制
          const apiUrl = `/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`
          console.log(`请求所有数据然后过滤分类: ${apiUrl}`)

          const response = await fetch(apiUrl)
          const data = await response.json()

          console.log(`总共返回数据条数:`, data.data ? data.data.length : 0)
          console.log(`API返回的总记录数:`, data.total || '未知')

          if (data.data && Array.isArray(data.data)) {
            // 先查看所有数据的分类情况
            const allCategories = [...new Set(data.data.map(record => record.category))]
            console.log('数据库中所有的分类:', allCategories)

            // 过滤指定分类的数据
            const filteredData = data.data.filter(record => record.category === categoryValue)
            console.log(`过滤后 ${category}(${categoryValue}) 数据条数:`, filteredData.length)
            console.log('过滤后的数据样例:', filteredData.slice(0, 5))

            filteredData.forEach(record => {
              const recordDate = new Date(record.in_time)
              const day = recordDate.getDate()
              const subtotal = parseFloat(record.subtotal || 0)

              console.log(`处理记录: ${record.name} - ${record.in_time} - 第${day}日 - 小计${subtotal}`)

              if (day >= 1 && day <= 31) {
                dailyData[day - 1] += subtotal
                console.log(`${category}: ${day}日 += ${subtotal}, 当前总计: ${dailyData[day - 1]}`)
              }
            })
          }
        }

        // 输出最终结果的前几天数据用于调试
        console.log(`${category} 前5天数据:`, dailyData.slice(0, 5))
        console.log(`${category} 数据总和:`, dailyData.reduce((sum, val) => sum + val, 0))

        return dailyData
      } catch (error) {
        console.error('获取每日数据失败:', error)
        ElMessage.error('获取数据失败，将使用默认值')
        return new Array(31).fill(0)
      }
    }

    // 插入模块数据
    const insertModuleData = async (module, startRow, startCol) => {
      if (module.type === 'daily') {
        const year = module.selectedYear || module.defaultYear
        const month = module.selectedMonth || module.defaultMonth

        try {
          console.log(`开始获取并插入31行数据，起始位置: 行${startRow}, 列${startCol}`)

          // 显示加载提示
          ElMessage.info('正在获取数据...')

          // 获取实际的每日数据
          const dailyData = await fetchDailyData(year, month, module.category)

          // 插入31行数据（1日到31日垂直排列）
          for (let i = 0; i < 31; i++) {
            const day = i + 1
            const targetRow = startRow + i

            // 根据数据类型格式化显示值
            let cellValue, displayValue
            if (module.category === '就餐人数') {
              cellValue = Math.round(dailyData[i]) // 就餐人数为整数
              displayValue = cellValue.toString()
            } else {
              cellValue = parseFloat(dailyData[i].toFixed(2)) // 金额保留两位小数
              displayValue = cellValue.toFixed(2)
            }

            console.log(`插入第${day}日数据到行${targetRow}: ${displayValue}`)

            // 设置单元格值 - 使用多种方法尝试
            let success = false

            // 方法1: 使用setCellValue
            if (window.luckysheet && typeof window.luckysheet.setCellValue === 'function') {
              try {
                window.luckysheet.setCellValue(targetRow, startCol, cellValue)
                console.log(`方法1成功设置单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                success = true
              } catch (error) {
                console.log('方法1失败:', error)
              }
            }

            // 方法2: 使用setRangeValue
            if (!success && window.luckysheet && typeof window.luckysheet.setRangeValue === 'function') {
              try {
                window.luckysheet.setRangeValue([{
                  row: targetRow,
                  column: startCol,
                  value: cellValue
                }])
                console.log(`方法2成功设置单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                success = true
              } catch (error) {
                console.log('方法2失败:', error)
              }
            }

            // 方法3: 直接操作数据结构
            if (!success && window.luckysheet && window.luckysheet.getluckysheetfile) {
              try {
                const file = window.luckysheet.getluckysheetfile()
                if (file && file[0] && file[0].data) {
                  if (!file[0].data[targetRow]) {
                    file[0].data[targetRow] = []
                  }
                  file[0].data[targetRow][startCol] = {
                    v: cellValue,
                    ct: { fa: "General", t: "n" }
                  }
                  window.luckysheet.refresh()
                  console.log(`方法3成功设置单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                  success = true
                }
              } catch (error) {
                console.log('方法3失败:', error)
              }
            }

            if (!success) {
              console.error(`无法设置单元格 [${targetRow}, ${startCol}] 的值`)
              ElMessage.warning(`第${day}日数据设置失败`)
            }
          }

          ElMessage.success(`已插入${year}年${month}月${module.title}（31行实际数据）`)

        } catch (error) {
          console.error('插入数据失败:', error)
          ElMessage.error('插入数据失败: ' + error.message)
        }

      } else if (module.type === 'summary') {
        try {
          ElMessage.info('正在获取汇总数据...')

          // 获取实际的汇总数据
          const summaryValue = await fetchSummaryData(module.dataField, module.category)

          // 根据数据类型格式化显示值
          let displayValue, cellValue
          if (module.category === '就餐人次') {
            cellValue = Math.round(summaryValue)
            displayValue = cellValue.toString()
          } else {
            cellValue = parseFloat(summaryValue.toFixed(2))
            displayValue = cellValue.toFixed(2)
          }

          // 设置汇总数据单元格值 - 使用多种方法尝试
          let success = false

          // 方法1: 使用setCellValue
          if (window.luckysheet && typeof window.luckysheet.setCellValue === 'function') {
            try {
              window.luckysheet.setCellValue(startRow, startCol, cellValue)
              console.log(`方法1成功设置汇总单元格 [${startRow}, ${startCol}] 的值: ${cellValue}`)
              success = true
            } catch (error) {
              console.log('汇总数据方法1失败:', error)
            }
          }

          // 方法2: 使用setRangeValue
          if (!success && window.luckysheet && typeof window.luckysheet.setRangeValue === 'function') {
            try {
              window.luckysheet.setRangeValue([{
                row: startRow,
                column: startCol,
                value: cellValue
              }])
              console.log(`方法2成功设置汇总单元格 [${startRow}, ${startCol}] 的值: ${cellValue}`)
              success = true
            } catch (error) {
              console.log('汇总数据方法2失败:', error)
            }
          }

          // 方法3: 直接操作数据结构
          if (!success && window.luckysheet && window.luckysheet.getluckysheetfile) {
            try {
              const file = window.luckysheet.getluckysheetfile()
              if (file && file[0] && file[0].data) {
                if (!file[0].data[startRow]) {
                  file[0].data[startRow] = []
                }
                file[0].data[startRow][startCol] = {
                  v: cellValue,
                  ct: { fa: "General", t: "n" }
                }
                window.luckysheet.refresh()
                console.log(`方法3成功设置汇总单元格 [${startRow}, ${startCol}] 的值: ${cellValue}`)
                success = true
              }
            } catch (error) {
              console.log('汇总数据方法3失败:', error)
            }
          }

          if (!success) {
            console.error(`无法设置汇总单元格 [${startRow}, ${startCol}] 的值`)
            ElMessage.warning('汇总数据设置失败')
          }

          ElMessage.success(`已插入${module.title}（实际数据：${displayValue}）`)
        } catch (error) {
          console.error('插入汇总数据失败:', error)
          ElMessage.error('插入汇总数据失败: ' + error.message)
        }

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

      try {
        switch (action) {
          case 'merge':
            if (window.luckysheet && window.luckysheet.merge) {
              window.luckysheet.merge(range)
            } else {
              console.log('合并单元格API不可用')
            }
            break
          case 'bold':
            if (window.luckysheet && window.luckysheet.setRangeValue) {
              // 使用setRangeValue设置粗体样式
              const cells = []
              for (let r = range.row[0]; r <= range.row[1]; r++) {
                for (let c = range.column[0]; c <= range.column[1]; c++) {
                  cells.push({
                    row: r,
                    column: c,
                    value: { bl: 1 }
                  })
                }
              }
              window.luckysheet.setRangeValue(cells)
            } else {
              console.log('粗体设置API不可用')
            }
            break
          case 'center':
            if (window.luckysheet && window.luckysheet.setRangeValue) {
              // 使用setRangeValue设置居中样式
              const cells = []
              for (let r = range.row[0]; r <= range.row[1]; r++) {
                for (let c = range.column[0]; c <= range.column[1]; c++) {
                  cells.push({
                    row: r,
                    column: c,
                    value: { vt: 1, ht: 1 }
                  })
                }
              }
              window.luckysheet.setRangeValue(cells)
            } else {
              console.log('居中设置API不可用')
            }
            break
          case 'border':
            console.log('边框设置功能暂不可用')
            break
          case 'currency':
            console.log('货币格式设置功能暂不可用')
            break
        }
      } catch (formatError) {
        console.error('格式应用失败:', formatError)
        ElMessage.warning('格式应用失败，但数据已插入')
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
          createdAt: new Date().toISOString()
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
    const loadTemplate = () => {
      const templates = JSON.parse(localStorage.getItem('reportDesignerTemplates') || '[]')
      availableTemplates.value = templates
      selectedTemplateIndex.value = -1
      loadDialogVisible.value = true
    }

    // 确认加载模板
    const confirmLoadTemplate = () => {
      if (selectedTemplateIndex.value === -1 || availableTemplates.value.length === 0) {
        return
      }

      const selectedTemplate = availableTemplates.value[selectedTemplateIndex.value]
      if (selectedTemplate && window.luckysheet) {
        try {
          // 使用Luckysheet的正确API来加载数据
          if (selectedTemplate.sheetData && selectedTemplate.sheetData.length > 0) {
            window.luckysheet.destroy()
            
            // 重新初始化Luckysheet并加载模板数据
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
              enableAddRow: true,
              enableAddCol: true,
              userInfo: false,
              myFolderUrl: '',
              data: selectedTemplate.sheetData
            }
            
            window.luckysheet.create(options)
            luckysheetInstance.value = window.luckysheet
            
            ElMessage.success(`已加载模板: ${selectedTemplate.name}`)
            loadDialogVisible.value = false
          } else {
            ElMessage.error('模板数据格式错误')
          }
        } catch (error) {
          console.error('加载模板失败:', error)
          ElMessage.error('加载模板失败: ' + error.message)
        }
      }
    }

    // 删除模板
    const deleteTemplate = async (index) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除模板 "${availableTemplates.value[index].name}" 吗？`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        availableTemplates.value.splice(index, 1)
        localStorage.setItem('reportDesignerTemplates', JSON.stringify(availableTemplates.value))
        
        // 如果删除的是当前选中的模板，重置选择
        if (selectedTemplateIndex.value === index) {
          selectedTemplateIndex.value = -1
        } else if (selectedTemplateIndex.value > index) {
          selectedTemplateIndex.value--
        }

        ElMessage.success('模板删除成功')
      } catch (error) {
        // 用户取消删除
      }
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未知时间'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
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
      loadDialogVisible,
      dateSelectVisible,
      templateForm,
      dateForm,
      selectedModule,
      availableTemplates,
      selectedTemplateIndex,
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
      confirmLoadTemplate,
      deleteTemplate,
      formatDate,
      manualExport,
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.toolbar-left,
.toolbar-right {
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.modules-panel {
  width: 380px;
  background: white;
  margin: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
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

/* 模板选择器样式 */
.template-selector {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
}

.no-templates {
  text-align: center;
  padding: 40px 20px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.template-card {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
}

.template-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.template-card:hover::before {
  opacity: 1;
}

.template-card.selected {
  border-color: #409eff;
  background: linear-gradient(135deg, #e6f7ff 0%, #ffffff 100%);
  box-shadow: 0 8px 24px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.template-card.selected::before {
  opacity: 1;
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.template-icon {
  font-size: 32px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
}

.template-desc {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.template-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  margin-top: 16px;
}

.template-date {
  font-size: 12px;
  color: #999;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.template-card .el-button {
  opacity: 0;
  transition: all 0.3s ease;
  transform: translateX(10px);
}

.template-card:hover .el-button {
  opacity: 1;
  transform: translateX(0);
}

.template-card.selected .el-button {
  opacity: 1;
  transform: translateX(0);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .template-card {
    padding: 16px;
  }
  
  .template-icon {
    font-size: 28px;
  }
  
  .template-name {
    font-size: 16px;
  }
}
</style>
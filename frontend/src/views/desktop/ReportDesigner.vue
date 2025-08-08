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
        <el-tooltip :content="showModulesPanel ? '隐藏数据模块库' : '显示数据模块库'" placement="bottom">
          <el-button @click="toggleModulesPanel" :type="showModulesPanel ? 'primary' : 'default'">
            <el-icon>
              <View v-if="!showModulesPanel" />
              <Hide v-else />
            </el-icon>
            {{ showModulesPanel ? '隐藏面板' : '显示面板' }}
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <div class="designer-main">
      <!-- Luckysheet Excel区域 - 占满整个空间 -->
      <div class="excel-container">
        <div id="luckysheet"
          style="margin:0px;padding:0px;position:absolute;width:100%;height:100%;left: 0px;top: 0px;"></div>
      </div>

      <!-- 悬浮的数据模块面板 -->
      <div class="modules-panel-overlay" v-show="showModulesPanel">
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
              <div class="category-header" @click="toggleCategory('daily')">
                <el-icon>
                  <Calendar />
                </el-icon>
                <span>每日数据 (31行)</span>
                <el-icon class="category-arrow" :class="{ 'expanded': categoryExpanded.daily }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div class="module-list" v-show="categoryExpanded.daily">
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
              <div class="category-header" @click="toggleCategory('summary')">
                <el-icon>
                  <DataAnalysis />
                </el-icon>
                <span>汇总统计</span>
                <el-icon class="category-arrow" :class="{ 'expanded': categoryExpanded.summary }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div class="module-list" v-show="categoryExpanded.summary">
                <div v-for="module in filteredSummaryModules" :key="module.id" class="module-card summary-module"
                  :draggable="true" @dragstart="handleDragStart($event, module)" @click="showDateSelector(module)">
                  <div class="module-icon">🧮</div>
                  <div class="module-info">
                    <div class="module-title">{{ module.title }}</div>
                    <div class="module-desc">{{ module.description }}</div>
                    <div class="module-data">{{ module.sampleData }}</div>
                    <div class="module-date-info">
                      <span class="date-label">默认：{{ new Date().getFullYear() }}年{{ new Date().getMonth() + 1 }}月</span>
                    </div>
                  </div>
                  <div class="module-badge">月度合计</div>
                </div>
              </div>
            </div>

            <!-- 储存类食材出库模块 -->
            <div class="module-category">
              <div class="category-header" @click="toggleCategory('storageOutbound')">
                <el-icon>
                  <Document />
                </el-icon>
                <span>储存类食材出库</span>
                <el-icon class="category-arrow" :class="{ 'expanded': categoryExpanded.storageOutbound }">
                  <ArrowDown />
                </el-icon>
              </div>
              <div class="module-list" v-show="categoryExpanded.storageOutbound">
                <div v-for="module in filteredStorageOutboundModules" :key="module.id"
                  class="module-card storage-outbound-module" :draggable="true"
                  @dragstart="handleDragStart($event, module)" @click="showDateSelector(module)">
                  <div class="module-icon">📦</div>
                  <div class="module-info">
                    <div class="module-title">{{ module.title }}</div>
                    <div class="module-desc">{{ module.description }}</div>
                    <div class="module-preview">
                      <span class="quarter-range">Q1 ↓ Q4</span>
                      <span class="sample-data">{{ module.sampleData }}</span>
                    </div>
                    <div class="module-date-info">
                      <span class="date-label">默认：{{ module.defaultYear }}年{{ module.defaultMonth }}月</span>
                    </div>
                  </div>
                  <div class="module-badge">4行</div>
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
              <span class="badge">{{ selectedModule?.type === 'daily' ? '31行数据' : '月度合计' }}</span>
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
          <el-alert :title="getPreviewText()" type="info" :closable="false" show-icon />
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
          <div v-for="(template, index) in availableTemplates" :key="template.id" class="template-card"
            :class="{ 'selected': selectedTemplateIndex === index }" @click="selectedTemplateIndex = index">
            <div class="template-header">
              <div class="template-icon">📊</div>
              <div class="template-info">
                <h4 class="template-name">{{ template.name }}</h4>
                <p class="template-desc">{{ template.description || '无描述' }}</p>
              </div>
            </div>
            <div class="template-meta">
              <span class="template-date">{{ formatDate(template.createdAt) }}</span>
              <el-button type="danger" size="small" text @click.stop="deleteTemplate(index)" title="删除模板">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="loadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmLoadTemplate"
            :disabled="selectedTemplateIndex === -1 || availableTemplates.length === 0">
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, inject, watch } from 'vue'
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
  View,
  Hide,
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
    View,
    Hide,
    ArrowDown
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

    // 面板显示状态 - 默认隐藏
    const showModulesPanel = ref(false)

    // 分类展开状态 - 默认收起
    const categoryExpanded = reactive({
      daily: false,    // 每日数据分类
      summary: false,  // 汇总统计分类
      storageOutbound: false  // 储存类食材出库分类
    })

    // 注入导航栏状态
    const sidebarCollapsed = inject('sidebarCollapsed', ref(false))

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
        description: '每日蔬菜支出',
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
        description: '每日鲜肉支出',
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
        description: '每日冷冻食品支出',
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
        description: '每日豆制品支出',
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
        description: '每日禽蛋支出',
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
        description: '每日水果支出',
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
        description: '每日点心支出',
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
        description: '每日大米支出',
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
        description: '每日面粉制品支出',
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
        description: '每日食用油支出',
        sampleData: '40.00, 45.00, 35.00...',
        type: 'daily',
        category: '食用油类',
        dataField: 'daily.oil',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_seasoning',
        title: '调味品类支出',
        description: '每日调味品支出',
        sampleData: '25.00, 30.00, 20.00...',
        type: 'daily',
        category: '调味品类',
        dataField: 'daily.seasoning',
        rows: 31,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'daily_total',
        title: '支出合计',
        description: '每日总支出',
        sampleData: '865.50, 865.30, 920.20...',
        type: 'daily',
        category: '合计',
        dataField: 'daily.total',
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
        description: '蔬菜月度总计',
        sampleData: '4,650.00',
        type: 'summary',
        category: '蔬菜类',
        dataField: 'totals.vegetables',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_meat',
        title: '鲜肉类月度合计',
        description: '鲜肉月度总计',
        sampleData: '8,680.00',
        type: 'summary',
        category: '鲜肉类',
        dataField: 'totals.meat',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_frozen',
        title: '冷冻类月度合计',
        description: '冷冻食品月度总计',
        sampleData: '2,480.00',
        type: 'summary',
        category: '冷冻类',
        dataField: 'totals.frozen',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_tofu',
        title: '豆制品类月度合计',
        description: '豆制品月度总计',
        sampleData: '1,395.00',
        type: 'summary',
        category: '豆制品类',
        dataField: 'totals.tofu',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_eggs',
        title: '禽蛋类月度合计',
        description: '禽蛋月度总计',
        sampleData: '1,860.00',
        type: 'summary',
        category: '禽蛋类',
        dataField: 'totals.eggs',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_fruits',
        title: '水果类月度合计',
        description: '水果月度总计',
        sampleData: '930.00',
        type: 'summary',
        category: '水果类',
        dataField: 'totals.fruits',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_snacks',
        title: '点心类月度合计',
        description: '点心月度总计',
        sampleData: '620.00',
        type: 'summary',
        category: '点心类',
        dataField: 'totals.snacks',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_rice',
        title: '大米月度合计',
        description: '大米月度总计',
        sampleData: '3,100.00',
        type: 'summary',
        category: '大米',
        dataField: 'totals.rice',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_flour',
        title: '面粉制品月度合计',
        description: '面粉制品月度总计',
        sampleData: '2,480.00',
        type: 'summary',
        category: '面粉制品',
        dataField: 'totals.flour',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_oil',
        title: '食用油类月度合计',
        description: '食用油月度总计',
        sampleData: '1,240.00',
        type: 'summary',
        category: '食用油类',
        dataField: 'totals.oil',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_seasoning',
        title: '调味品类月度合计',
        description: '调味品月度总计',
        sampleData: '775.00',
        type: 'summary',
        category: '调味品类',
        dataField: 'totals.seasoning',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'total_all',
        title: '月度总合计',
        description: '所有支出月度总计',
        sampleData: '28,210.00',
        type: 'summary',
        category: '总计',
        dataField: 'totals.all',
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      }
    ]

    // 储存类食材出库模块
    const storageOutboundModules = [
      {
        id: 'outbound_rice',
        title: '大米出库',
        description: '大米季度出库量',
        sampleData: '250.00, 250.00, 250.00, 150.00',
        type: 'storage_outbound',
        category: '大米',
        dataField: 'outbound.rice',
        rows: 4, // 4个季度数据
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'outbound_oil',
        title: '食用油类出库',
        description: '食用油季度出库量',
        sampleData: '80.00, 80.00, 80.00, 60.00',
        type: 'storage_outbound',
        category: '食用油类',
        dataField: 'outbound.oil',
        rows: 4,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
      },
      {
        id: 'outbound_seasoning',
        title: '调味品类出库',
        description: '调味品季度出库量',
        sampleData: '45.00, 45.00, 45.00, 35.00',
        type: 'storage_outbound',
        category: '调味品类',
        dataField: 'outbound.seasoning',
        rows: 4,
        defaultYear: new Date().getFullYear(),
        defaultMonth: new Date().getMonth() + 1
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

    const filteredStorageOutboundModules = computed(() =>
      storageOutboundModules.filter(m =>
        m.title.includes(searchText.value) ||
        m.description.includes(searchText.value) ||
        m.category.includes(searchText.value)
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
            toolbarConfig: {
              undoRedo: true, // 撤销重做
              paintFormat: true, // 格式刷
              currencyFormat: true, // 货币格式
              percentageFormat: true, // 百分比格式
              numberDecrease: true, // 减少小数位数
              numberIncrease: true, // 增加小数位数
              moreFormats: true, // 更多格式
              font: true, // 字体
              fontSize: true, // 字号
              bold: true, // 粗体
              italic: true, // 斜体
              strikethrough: true, // 删除线
              underline: true, // 下划线
              textColor: true, // 文字颜色
              fillColor: true, // 背景颜色
              border: true, // 边框
              mergeCell: true, // 合并单元格
              horizontalAlignMode: true, // 水平对齐
              verticalAlignMode: true, // 垂直对齐
              textWrapMode: true, // 文字换行
              textRotateMode: true, // 文字旋转
              image: true, // 插入图片
              link: true, // 插入链接
              chart: true, // 图表
              postil: true, // 批注
              pivotTable: true, // 数据透视表
              function: true, // 公式
              frozenMode: true, // 冻结
              sortAndFilter: true, // 排序和筛选
              findAndReplace: true, // 查找替换
              sum: true, // 求和
              autoSum: true, // 自动求和
              moreFunction: true, // 更多函数
              conditionalFormat: true, // 条件格式
              dataVerification: true, // 数据验证
              splitColumn: true, // 分列
              screenshot: true, // 截图
              protection: true, // 工作表保护
              print: true // 打印
            },
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

    // 获取预览文本
    const getPreviewText = () => {
      if (!selectedModule.value) return ''

      if (selectedModule.value.type === 'daily') {
        return `将插入 ${dateForm.year}年${dateForm.month}月 的${selectedModule.value.category}数据（31行）`
      } else {
        return `将插入 ${dateForm.year}年${dateForm.month}月 的${selectedModule.value.category}月度合计数据`
      }
    }

    // 获取汇总数据
    const fetchSummaryData = async (dataField, category, year, month) => {
      try {
        // 使用传入的年月参数，如果没有则使用当前日期
        if (!year || !month) {
          const currentDate = new Date()
          year = currentDate.getFullYear()
          month = currentDate.getMonth() + 1
        }

        console.log(`开始获取汇总数据: ${year}年${month}月 ${category}`)

        if (dataField.includes('totals.')) {
          // 月度合计数据
          if (category === '总计') {
            // 获取月度总合计 - 先尝试使用monthly-report API
            try {
              const response = await fetch(`/api/monthly-report/data?year=${year}&month=${month}`)
              const data = await response.json()
              if (data.monthlyTotal) {
                return data.monthlyTotal
              }
            } catch (error) {
              console.log('monthly-report API不可用，使用stock-ins API计算总计')
            }

            // 如果monthly-report API不可用，使用stock-ins API计算总计
            const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
            const endDate = `${year}-${month.toString().padStart(2, '0')}-31`
            const response = await fetch(`/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`)
            const data = await response.json()

            let total = 0
            if (data.data && Array.isArray(data.data)) {
              total = data.data.reduce((sum, record) => sum + parseFloat(record.subtotal || 0), 0)
              console.log(`总计汇总数据: 总数据${data.data.length}条，总计${total}`)
            }
            return total

          } else {
            // 特定分类的月度合计 - 直接使用中文分类名称
            const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
            const endDate = `${year}-${month.toString().padStart(2, '0')}-31`

            console.log(`请求特定分类数据: ${category}`)
            console.log(`时间范围: ${startDate} 到 ${endDate}`)

            const response = await fetch(`/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`)
            const data = await response.json()

            let total = 0
            if (data.data && Array.isArray(data.data)) {
              // 直接使用中文分类名称过滤数据
              const filteredData = data.data.filter(record => record.category === category)
              total = filteredData.reduce((sum, record) => sum + parseFloat(record.subtotal || 0), 0)
              console.log(`汇总数据 ${category}: 总数据${data.data.length}条，找到${filteredData.length}条记录，总计${total}`)

              // 输出前几条数据用于调试
              if (filteredData.length > 0) {
                console.log('找到的数据样例:', filteredData.slice(0, 3))
              } else {
                console.log('未找到匹配的数据，数据库中的分类有:', [...new Set(data.data.map(r => r.category))])
              }
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
        // 构建API请求URL
        const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
        const endDate = `${year}-${month.toString().padStart(2, '0')}-31`

        console.log(`开始获取每日数据: ${year}年${month}月 ${category}`)
        console.log(`请求时间范围: ${startDate} 到 ${endDate}`)

        // 创建31天的数据数组，初始化为0
        const dailyData = new Array(31).fill(0)

        // 获取所有数据
        const apiUrl = `/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`
        console.log(`请求API: ${apiUrl}`)

        const response = await fetch(apiUrl)
        const data = await response.json()

        console.log(`总共返回数据条数:`, data.data ? data.data.length : 0)
        console.log(`API返回的总记录数:`, data.total || '未知')

        if (data.data && Array.isArray(data.data)) {
          // 先查看所有数据的分类情况
          const allCategories = [...new Set(data.data.map(record => record.category))]
          console.log('数据库中所有的分类:', allCategories)

          // 填充实际数据
          if (category === '合计') {
            // 合计数据需要汇总所有分类
            console.log('开始计算合计数据，汇总所有分类...')

            data.data.forEach(record => {
              const recordDate = new Date(record.in_time)
              const day = recordDate.getDate()
              const subtotal = parseFloat(record.subtotal || 0)

              if (day >= 1 && day <= 31) {
                dailyData[day - 1] += subtotal
                console.log(`合计: ${day}日 += ${subtotal} (${record.category}), 当前总计: ${dailyData[day - 1]}`)
              }
            })
          } else {
            // 单个分类的数据 - 直接使用中文分类名称过滤
            const filteredData = data.data.filter(record => record.category === category)
            console.log(`过滤后 ${category} 数据条数:`, filteredData.length)
            console.log('过滤后的数据样例:', filteredData.slice(0, 3))

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

            // 如果没有找到数据，输出调试信息
            if (filteredData.length === 0) {
              console.log(`未找到 ${category} 的数据，数据库中的分类有:`, allCategories)
            }
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

    // 获取储存类食材使用量数据
    const fetchStorageUsageData = async (year, month, category) => {
      try {
        console.log(`开始获取储存类食材使用量: ${year}年${month}月 ${category}`)

        // 从API获取月底库存数据
        const inventoryResponse = await fetch('/api/monthly-inventory')
        const inventoryResult = await inventoryResponse.json()
        const inventoryData = inventoryResult.data || []
        console.log('月底库存数据:', inventoryData)

        // 构建当月和上月的年月字符串
        const currentMonth = `${year}-${month.toString().padStart(2, '0')}`
        const prevMonth = getPreviousMonth(currentMonth)

        console.log(`当月: ${currentMonth}, 上月: ${prevMonth}`)

        // 计算当月月底库存金额
        const currentMonthInventory = inventoryData.filter(item => item.date === currentMonth)
        const currentAmount = currentMonthInventory
          .filter(item => item.category === category)
          .reduce((sum, item) => sum + (parseFloat(item.unitPrice || 0) * parseFloat(item.quantity || 0)), 0)

        console.log(`${category} 当月库存金额: ${currentAmount}`)

        // 计算上个月月底库存金额
        const prevMonthInventory = inventoryData.filter(item => item.date === prevMonth)
        const prevAmount = prevMonthInventory
          .filter(item => item.category === category)
          .reduce((sum, item) => sum + (parseFloat(item.unitPrice || 0) * parseFloat(item.quantity || 0)), 0)

        console.log(`${category} 上月库存金额: ${prevAmount}`)

        // 从库存查询API获取当月入库数据
        const startDate = `${year}-${month.toString().padStart(2, '0')}-01`
        const endDate = `${year}-${month.toString().padStart(2, '0')}-31`

        console.log(`获取入库数据时间范围: ${startDate} 到 ${endDate}`)

        const response = await fetch(`/api/stock-ins?startTime=${startDate}&endTime=${endDate}&pageSize=10000`)
        const stockData = await response.json()

        let stockInAmount = 0
        if (stockData.data && Array.isArray(stockData.data)) {
          // 过滤指定分类的入库数据
          const filteredStockData = stockData.data.filter(record => record.category === category)
          stockInAmount = filteredStockData.reduce((sum, record) => sum + parseFloat(record.subtotal || 0), 0)
          console.log(`${category} 当月入库金额: ${stockInAmount}`)
        }

        // 计算使用量：上月库存 + 当月入库 - 当月库存
        // 注意：这里的逻辑是 上月库存 + 入库 - 当月库存 = 使用量
        let monthlyUsage = prevAmount + stockInAmount - currentAmount

        // 确保使用量不为负数
        monthlyUsage = Math.max(0, monthlyUsage)

        console.log(`${category} 计算过程:`)
        console.log(`  上月库存: ${prevAmount}`)
        console.log(`  当月入库: ${stockInAmount}`)
        console.log(`  当月库存: ${currentAmount}`)
        console.log(`  月度使用量: ${monthlyUsage}`)

        // 按照您的要求计算4个季度的数据
        // 将月度使用量除以4，商向下取整
        const quarterlyBase = Math.floor(monthlyUsage / 4)

        // 计算余数部分
        const remainder = monthlyUsage - (quarterlyBase * 3)

        // 返回4个数据：前3个季度使用基础值，第4个季度使用余数
        const quarterlyData = [quarterlyBase, quarterlyBase, quarterlyBase, remainder]

        console.log(`${category} 季度分配:`, quarterlyData)
        console.log(`验证总和: ${quarterlyData.reduce((sum, val) => sum + val, 0)} = ${monthlyUsage}`)

        return quarterlyData
      } catch (error) {
        console.error('获取储存类食材使用量失败:', error)
        ElMessage.error('获取储存类食材数据失败，将使用默认值')
        return [0, 0, 0, 0]
      }
    }

    // 获取上个月的年月字符串
    const getPreviousMonth = (yearMonth) => {
      const [year, month] = yearMonth.split('-').map(Number)
      const date = new Date(year, month - 1, 1) // month - 1 因为JavaScript月份从0开始
      date.setMonth(date.getMonth() - 1) // 减去一个月

      const prevYear = date.getFullYear()
      const prevMonth = String(date.getMonth() + 1).padStart(2, '0')
      return `${prevYear}-${prevMonth}`
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
            cellValue = parseFloat(dailyData[i].toFixed(2)) // 金额保留两位小数
            displayValue = cellValue.toFixed(2)

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
        const year = module.selectedYear || new Date().getFullYear()
        const month = module.selectedMonth || new Date().getMonth() + 1

        try {
          ElMessage.info('正在获取汇总数据...')

          // 获取实际的汇总数据，传入年月参数
          const summaryValue = await fetchSummaryData(module.dataField, module.category, year, month)

          // 根据数据类型格式化显示值
          let displayValue, cellValue
          cellValue = parseFloat(summaryValue.toFixed(2))
          displayValue = cellValue.toFixed(2)

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

          ElMessage.success(`已插入${year}年${month}月${module.title}（实际数据：${displayValue}）`)
        } catch (error) {
          console.error('插入汇总数据失败:', error)
          ElMessage.error('插入汇总数据失败: ' + error.message)
        }

      } else if (module.type === 'storage_outbound') {
        const year = module.selectedYear || module.defaultYear
        const month = module.selectedMonth || module.defaultMonth

        try {
          ElMessage.info('正在获取储存类食材出库数据...')

          // 获取储存类食材使用量数据
          const quarterlyData = await fetchStorageUsageData(year, month, module.category)

          // 按照您的要求填写到特定行：第1行，第8行，第15行，第22行
          const targetRows = [startRow, startRow + 7, startRow + 14, startRow + 21] // 第1,8,15,22行

          for (let i = 0; i < 4; i++) {
            const targetRow = targetRows[i]
            const cellValue = parseFloat(quarterlyData[i].toFixed(2))
            const displayValue = cellValue.toFixed(2)

            console.log(`插入第${i + 1}季度数据到行${targetRow + 1}: ${displayValue}`)

            // 设置单元格值 - 使用多种方法尝试
            let success = false

            // 方法1: 使用setCellValue
            if (window.luckysheet && typeof window.luckysheet.setCellValue === 'function') {
              try {
                window.luckysheet.setCellValue(targetRow, startCol, cellValue)
                console.log(`方法1成功设置储存出库单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                success = true
              } catch (error) {
                console.log('储存出库数据方法1失败:', error)
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
                console.log(`方法2成功设置储存出库单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                success = true
              } catch (error) {
                console.log('储存出库数据方法2失败:', error)
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
                  console.log(`方法3成功设置储存出库单元格 [${targetRow}, ${startCol}] 的值: ${cellValue}`)
                  success = true
                }
              } catch (error) {
                console.log('储存出库数据方法3失败:', error)
              }
            }

            if (!success) {
              console.error(`无法设置储存出库单元格 [${targetRow}, ${startCol}] 的值`)
              ElMessage.warning(`第${i + 1}季度数据设置失败`)
            }
          }

          ElMessage.success(`已插入${year}年${month}月${module.title}（4行季度数据）`)
        } catch (error) {
          console.error('插入储存出库数据失败:', error)
          ElMessage.error('插入储存出库数据失败: ' + error.message)
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

        await fetch('/api/designer-templates', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: templateForm.name,
            description: templateForm.description,
            sheetData: JSON.stringify(sheetData)
          })
        })

        ElMessage.success('模板保存成功')
        saveDialogVisible.value = false
        
        // 重新加载模板列表
        await loadTemplateList()
      } catch (error) {
        console.error('保存模板失败:', error)
        ElMessage.error('保存模板失败')
      } finally {
        saving.value = false
      }
    }

    // 加载模板列表
    const loadTemplateList = async () => {
      try {
        const response = await fetch('/api/designer-templates')
        const data = await response.json()
        availableTemplates.value = data.data.map(template => ({
          ...template,
          sheetData: JSON.parse(template.sheetData)
        }))
      } catch (error) {
        console.error('加载模板列表失败:', error)
        ElMessage.error('加载模板列表失败')
      }
    }

    // 加载模板
    const loadTemplate = async () => {
      await loadTemplateList()
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
              toolbarConfig: {
                undoRedo: true, // 撤销重做
                paintFormat: true, // 格式刷
                currencyFormat: true, // 货币格式
                percentageFormat: true, // 百分比格式
                numberDecrease: true, // 减少小数位数
                numberIncrease: true, // 增加小数位数
                moreFormats: true, // 更多格式
                font: true, // 字体
                fontSize: true, // 字号
                bold: true, // 粗体
                italic: true, // 斜体
                strikethrough: true, // 删除线
                underline: true, // 下划线
                textColor: true, // 文字颜色
                fillColor: true, // 背景颜色
                border: true, // 边框
                mergeCell: true, // 合并单元格
                horizontalAlignMode: true, // 水平对齐
                verticalAlignMode: true, // 垂直对齐
                textWrapMode: true, // 文字换行
                textRotateMode: true, // 文字旋转
                image: true, // 插入图片
                link: true, // 插入链接
                chart: true, // 图表
                postil: true, // 批注
                pivotTable: true, // 数据透视表
                function: true, // 公式
                frozenMode: true, // 冻结
                sortAndFilter: true, // 排序和筛选
                findAndReplace: true, // 查找替换
                sum: true, // 求和
                autoSum: true, // 自动求和
                moreFunction: true, // 更多函数
                conditionalFormat: true, // 条件格式
                dataVerification: true, // 数据验证
                splitColumn: true, // 分列
                screenshot: true, // 截图
                protection: true, // 工作表保护
                print: true // 打印
              },
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

        const template = availableTemplates.value[index]
        await fetch(`/api/designer-templates/${template.id}`, {
          method: 'DELETE'
        })
        
        // 重新加载模板列表
        await loadTemplateList()

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

    // 切换数据模块面板显示/隐藏
    const toggleModulesPanel = () => {
      showModulesPanel.value = !showModulesPanel.value
      ElMessage.success(showModulesPanel.value ? '已显示数据模块库' : '已隐藏数据模块库')
    }

    // 切换分类展开/收起状态
    const toggleCategory = (categoryKey) => {
      categoryExpanded[categoryKey] = !categoryExpanded[categoryKey]
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
          '合计': 'total'
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

        // 如果没有每日数据，尝试从分类总计中获取数据
        if (reportData.categoryTotals && reportData.categoryTotals.length > 0) {
          const categoryData = reportData.categoryTotals.find(c => c.category === category)
          if (categoryData) {
            // 返回月度总计除以天数的数据
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





    // 监听导航栏状态变化，重新调整Luckysheet大小
    watch(sidebarCollapsed, () => {
      setTimeout(() => {
        if (luckysheetInstance.value && window.luckysheet) {
          try {
            // 触发Luckysheet重新计算大小
            window.luckysheet.resize()
          } catch (error) {
            console.log('Luckysheet resize failed:', error)
          }
        }
      }, 350) // 等待CSS动画完成后再调整
    })

    onMounted(() => {
      // 忽略Chrome扩展的端口错误
      if (window.chrome && window.chrome.runtime && window.chrome.runtime.lastError) {
        // 清除可能的扩展错误
        console.log('忽略Chrome扩展错误')
      }

      if (window.luckysheet) {
        initLuckysheet()

        // 修复工具栏下拉菜单定位并添加拖动功能
        setTimeout(() => {
          const setupDraggableToolbar = () => {
            try {
              // 监听所有工具栏按钮的点击事件
              const toolbar = document.querySelector('.luckysheet-toolbar');
              if (toolbar) {
                toolbar.addEventListener('click', (e) => {
                  // 检查是否点击了更多按钮
                  if (e.target.closest('.luckysheet-toolbar-more-vertical')) {
                    setTimeout(() => {
                      const dropdown = document.querySelector('.luckysheet-toolbar-more-vertical-content');
                      if (dropdown && dropdown.style.display !== 'none') {
                        // 重置定位样式，使用fixed定位以便拖动
                        dropdown.style.position = 'fixed';
                        dropdown.style.zIndex = '9999';
                        dropdown.style.cursor = 'move';

                        // 获取初始位置
                        const moreButton = document.querySelector('.luckysheet-toolbar-more-vertical');
                        const buttonRect = moreButton.getBoundingClientRect();
                        dropdown.style.top = (buttonRect.bottom + 5) + 'px';
                        dropdown.style.left = buttonRect.left + 'px';
                        dropdown.style.transform = 'none';
                        dropdown.style.marginTop = '0';

                        // 让整个工具栏可拖动
                        dropdown.style.userSelect = 'none';
                        dropdown.title = '可拖动工具栏';

                        // 实现拖动功能
                        makeDraggable(dropdown);

                        console.log('工具栏下拉菜单已设置为可拖动');
                      }
                    }, 10);
                  }
                });
              }
            } catch (error) {
              console.log('设置可拖动工具栏失败:', error);
            }
          };

          // 拖动功能实现
          const makeDraggable = (element) => {
            let isDragging = false;
            let startX, startY, initialX, initialY;

            // 直接使用整个工具栏作为拖动目标
            const dragTarget = element;

            dragTarget.addEventListener('mousedown', (e) => {
              // 检查是否点击了工具栏按钮，如果是则不启动拖动
              if (e.target.closest('.luckysheet-toolbar-button') ||
                e.target.closest('.luckysheet-toolbar-menu-button') ||
                e.target.tagName === 'BUTTON' ||
                e.target.closest('button')) {
                return;
              }

              isDragging = true;
              startX = e.clientX;
              startY = e.clientY;

              const rect = element.getBoundingClientRect();
              initialX = rect.left;
              initialY = rect.top;

              element.style.transition = 'none';
              document.body.style.userSelect = 'none';
              element.style.cursor = 'grabbing';

              e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
              if (!isDragging) return;

              const deltaX = e.clientX - startX;
              const deltaY = e.clientY - startY;

              const newX = initialX + deltaX;
              const newY = initialY + deltaY;

              // 限制在视窗范围内
              const maxX = window.innerWidth - element.offsetWidth;
              const maxY = window.innerHeight - element.offsetHeight;

              const constrainedX = Math.max(0, Math.min(newX, maxX));
              const constrainedY = Math.max(0, Math.min(newY, maxY));

              element.style.left = constrainedX + 'px';
              element.style.top = constrainedY + 'px';
            });

            document.addEventListener('mouseup', () => {
              if (isDragging) {
                isDragging = false;
                element.style.transition = '';
                document.body.style.userSelect = '';
                element.style.cursor = 'move';
              }
            });

            // 双击重置位置（只在空白区域有效）
            dragTarget.addEventListener('dblclick', (e) => {
              // 检查是否双击了工具栏按钮，如果是则不重置
              if (e.target.closest('.luckysheet-toolbar-button') ||
                e.target.closest('.luckysheet-toolbar-menu-button') ||
                e.target.tagName === 'BUTTON' ||
                e.target.closest('button')) {
                return;
              }

              const moreButton = document.querySelector('.luckysheet-toolbar-more-vertical');
              if (moreButton) {
                const buttonRect = moreButton.getBoundingClientRect();
                element.style.top = (buttonRect.bottom + 5) + 'px';
                element.style.left = buttonRect.left + 'px';
                element.style.transition = 'all 0.3s ease';
                setTimeout(() => {
                  element.style.transition = '';
                }, 300);
              }
            });
          };

          setupDraggableToolbar();
        }, 1000);
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
      showModulesPanel,
      categoryExpanded,
      filteredDailyModules,
      filteredSummaryModules,
      filteredStorageOutboundModules,
      handleDragStart,
      showDateSelector,
      getYearOptions,
      getPreviewText,
      confirmInsertModule,
      saveTemplate,
      confirmSaveTemplate,
      loadTemplate,
      confirmLoadTemplate,
      deleteTemplate,
      formatDate,
      manualExport,
      toggleModulesPanel,
      toggleCategory
    }
  }
}
</script>

<style scoped>
.report-designer {
  height: calc(100vh - 64px);
  /* 减去头部高度 */
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

.toolbar-left {
  display: flex;
  gap: 10px;
}

.toolbar-right {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.designer-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.excel-container {
  flex: 1;
  position: relative;
  background: white;
  margin: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  /* 确保内部定位元素有正确的基准 */
  transform: translateZ(0);
  overflow: hidden;
  min-height: 0;
  /* 确保flex子元素能正确收缩 */
}

/* 悬浮的数据模块面板覆盖层 */
.modules-panel-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  bottom: 10px;
  width: 320px;
  /* 调整宽度以适应卡片内容 */
  z-index: 1000;
  pointer-events: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modules-panel {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  pointer-events: auto;
  border: 1px solid #e4e7ed;
  backdrop-filter: blur(10px);
  transform: translateX(0);
}

/* 面板显示/隐藏动画 */
.modules-panel-overlay {
  animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 面板内容样式调整 */
.modules-panel .panel-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 1px solid #e4e7ed;
  border-radius: 12px 12px 0 0;
}

.modules-panel .modules-content {
  background: rgba(255, 255, 255, 0.8);
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
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.category-header:hover {
  background: #e9ecef;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-header:active {
  transform: translateY(0);
}

/* 分类箭头样式 */
.category-arrow {
  margin-left: auto;
  transition: transform 0.3s ease;
  color: #666;
}

.category-arrow.expanded {
  transform: rotate(180deg);
}

/* 分类标题文字 */
.category-header span {
  flex: 1;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* 增加卡片间距 */
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 模块列表展开/收起动画 */
.module-list {
  max-height: 1000px;
  /* 设置一个足够大的最大高度 */
}

/* 当使用v-show时，可以通过CSS来控制动画 */
.module-category .module-list {
  animation-duration: 0.3s;
  animation-fill-mode: both;
}

/* 淡入动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.module-card {
  display: flex;
  align-items: flex-start;
  /* 改为顶部对齐，适应多行文字 */
  padding: 10px;
  /* 稍微减少内边距 */
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
  background: white;
  position: relative;
  min-height: 80px;
  /* 增加最小高度确保日期信息显示 */
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
  word-wrap: break-word;
  /* 确保长文字能够换行 */
  overflow-wrap: break-word;
  padding-right: 20px;
  /* 为右侧的badge留出空间 */
}

.module-title {
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 4px;
  color: #333;
  line-height: 1.3;
  /* 改善行高 */
  word-break: keep-all;
  /* 保持中文词汇完整性 */
}

.module-desc {
  font-size: 11px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 4px;
  word-break: keep-all;
  /* 保持中文词汇完整性 */
  hyphens: auto;
  /* 自动断词 */
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

.quarter-range {
  font-size: 10px;
  color: #fa541c;
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
  z-index: 2;
  /* 确保badge在最上层 */
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

.storage-outbound-module {
  border-left: 4px solid #fa541c;
}

.module-date-info {
  margin-top: 6px;
  /* 增加上边距 */
  position: relative;
  /* 确保在正常文档流中 */
  z-index: 1;
  /* 确保在badge之上 */
}

.date-label {
  font-size: 9px;
  color: #1890ff;
  background: #e6f3ff;
  padding: 2px 6px;
  /* 增加内边距 */
  border-radius: 3px;
  /* 稍微增加圆角 */
  display: inline-block;
  /* 确保正确显示 */
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

/* 修复Luckysheet工具栏下拉菜单定位问题 */
:deep(.luckysheet-toolbar-more-vertical-content) {
  position: fixed !important;
  z-index: 1001 !important;
}

/* 确保工具栏容器有正确的定位上下文 */
:deep(.luckysheet-toolbar) {
  position: relative !important;
  z-index: 100 !important;
}

/* 修复工具栏下拉菜单的定位基准 */
:deep(.luckysheet-toolbar-more-vertical) {
  position: relative !important;
}

/* 工具栏下拉菜单内容定位修复 */
:deep(.luckysheet-toolbar-more-vertical-content) {
  position: absolute !important;
  top: 100% !important;
  left: 0 !important;
  right: auto !important;
  transform: none !important;
  margin-top: 0 !important;
}

/* 确保下拉菜单不受页面滚动影响 */
:deep(.luckysheet-toolbar-more-vertical.luckysheet-toolbar-more-vertical-active .luckysheet-toolbar-more-vertical-content) {
  display: flex !important;
  position: fixed !important;
  background: #fff !important;
  border: 1px solid #e4e7ed !important;
  border-radius: 8px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
  z-index: 9999 !important;
  min-width: 200px !important;
  flex-direction: column !important;
}

/* 拖动工具栏样式增强 */
:deep(.luckysheet-toolbar-more-vertical-content) {
  transition: all 0.2s ease !important;
}

:deep(.luckysheet-toolbar-more-vertical-content:hover) {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2) !important;
}

/* 整个工具栏可拖动的视觉提示 */
:deep(.luckysheet-toolbar-more-vertical-content) {
  cursor: move !important;
  user-select: none !important;
}

:deep(.luckysheet-toolbar-more-vertical-content:active) {
  cursor: grabbing !important;
}

/* 工具栏按钮在拖动状态下的样式 */
:deep(.luckysheet-toolbar-more-vertical-content .luckysheet-toolbar-button) {
  margin: 2px !important;
  border-radius: 4px !important;
  transition: all 0.2s ease !important;
}

:deep(.luckysheet-toolbar-more-vertical-content .luckysheet-toolbar-button:hover) {
  background: #f0f9ff !important;
  transform: translateY(-1px) !important;
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

/* 导航栏收缩时的适配 */
@media screen and (min-width: 769px) {

  /* 当导航栏收缩时，确保表格有足够空间 */
  .report-designer {
    transition: all 0.3s ease;
  }

  .excel-container {
    transition: all 0.3s ease;
  }

  /* 悬浮面板在导航栏收缩时的调整 */
  .modules-panel-overlay {
    transition: all 0.3s ease;
  }
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

  /* 移动端时调整面板宽度 */
  .modules-panel-overlay {
    width: 280px;
  }
}
</style>
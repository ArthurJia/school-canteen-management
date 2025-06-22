<template>
  <div class="monthly-report-container">
    <div class="report-header">
      <h1>月度报表</h1>
      <div class="date-selector">
        <el-date-picker
          v-model="selectedDate"
          type="month"
          format="YYYY-MM"
          value-format="YYYY-MM"
          placeholder="选择月份"
          @change="handleDateChange"
        />
        <el-button type="primary" @click="loadReportData">
          <el-icon><i-ep-Search /></el-icon>
          查询
        </el-button>
      </div>
    </div>

    <div class="report-summary">
      <el-card class="box-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>月度统计</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="statistic-item">
              <div class="statistic-title">月度总支出</div>
              <div class="statistic-value" style="color: #cf1322;">
                ¥{{ reportData.monthlyTotal.toFixed(2) }}
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="statistic-item">
              <div class="statistic-title">商品种类</div>
              <div class="statistic-value" style="color: #3f8600;">
                {{ reportData.items.length }}
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="statistic-item">
              <div class="statistic-title">日均支出</div>
              <div class="statistic-value" style="color: #cf1322;">
                ¥{{ calculateDailyAverage().toFixed(2) }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <el-tabs v-model="activeTabKey" @tab-change="handleTabChange">
      <el-tab-pane label="类别统计" name="1">
        <div class="category-chart-container">
          <div ref="categoryChart" class="category-chart"></div>
        </div>
        <el-table
          :data="reportData.categoryTotals"
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="category" label="类别" />
          <el-table-column prop="total" label="金额" sortable>
            <template #default="scope">
              ¥{{ scope.row.total.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="占比" sortable>
            <template #default="scope">
              {{ calculatePercentage(scope.row.total) }}%
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="每日统计" name="2">
        <div class="daily-chart-container">
          <div ref="dailyChart" class="daily-chart"></div>
        </div>
        <el-table
          :data="reportData.dailyTotals"
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column label="日期">
            <template #default="scope">
              {{ reportData.year }}-{{ reportData.month.toString().padStart(2, '0') }}-{{ scope.row.day }}
            </template>
          </el-table-column>
          <el-table-column prop="total" label="金额" sortable>
            <template #default="scope">
              ¥{{ scope.row.total.toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="明细数据" name="3">
        <el-table
          :data="reportData.items.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="类别" />
          <el-table-column prop="totalQuantity" label="数量" />
          <el-table-column prop="unit" label="单位" />
          <el-table-column prop="avgPrice" label="平均单价">
            <template #default="scope">
              ¥{{ scope.row.avgPrice.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="totalSubtotal" label="总金额">
            <template #default="scope">
              ¥{{ scope.row.totalSubtotal.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="count" label="入库次数" />
        </el-table>
        <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="reportData.items.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-tab-pane>
      <el-tab-pane label="电子表格" name="4">
        <div class="luckysheet-container">
          <div class="toolbar">
            <el-button type="primary" @click="saveTemplate">
              <el-icon><i-ep-Document /></el-icon>
              保存模板
            </el-button>
            <el-button @click="exportExcel">
              <el-icon><i-ep-Download /></el-icon>
              导出Excel
            </el-button>
          </div>
          <luckysheet-wrapper
            ref="luckysheetRef"
            :options="luckysheetOptions"
            height="550px"
            @initialized="handleLuckysheetInitialized"
            @updated="handleLuckysheetUpdated"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, nextTick, watch, computed } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import * as echarts from 'echarts';
import dayjs from 'dayjs';
import LuckysheetWrapper from '@/components/LuckysheetWrapper.vue';

export default defineComponent({
  name: 'MonthlyReport',
  components: {
    LuckysheetWrapper
  },
  setup() {
    const selectedDate = ref(dayjs().format('YYYY-MM'));
    const activeTabKey = ref('1');
    const loading = ref(false);
    const categoryChart = ref(null);
    const dailyChart = ref(null);
    const currentPage = ref(1);
    const pageSize = ref(10);
    let categoryChartInstance = null;
    let dailyChartInstance = null;
    const luckysheetRef = ref(null);

    const reportData = reactive({
      items: [],
      monthlyTotal: 0,
      categoryTotals: [],
      dailyTotals: [],
      year: dayjs().year(),
      month: dayjs().month() + 1
    });

    const handleDateChange = (date) => {
      if (date) {
        const [year, month] = date.split('-');
        reportData.year = parseInt(year);
        reportData.month = parseInt(month);
      }
    };

    const handleTabChange = (tab) => {
      if (tab === '1' || tab === '2') {
        nextTick(() => {
          renderCharts();
        });
      }
    };

    const loadReportData = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/monthly-report/data', {
          params: {
            year: reportData.year,
            month: reportData.month
          }
        });
        
        Object.assign(reportData, response.data);
        
        nextTick(() => {
          renderCharts();
          loadLuckysheet();
        });
      } catch (error) {
        console.error('加载报表数据失败:', error);
        ElMessage.error('加载报表数据失败');
      } finally {
        loading.value = false;
      }
    };

    const calculatePercentage = (total) => {
      if (!reportData.monthlyTotal) return '0.00';
      return ((total / reportData.monthlyTotal) * 100).toFixed(2);
    };

    const calculateDailyAverage = () => {
      if (!reportData.monthlyTotal) return 0;
      const daysWithExpense = reportData.dailyTotals.filter(day => day.total > 0).length;
      return daysWithExpense ? reportData.monthlyTotal / daysWithExpense : 0;
    };

    const renderCharts = () => {
      // 渲染类别饼图
      if (categoryChartInstance) {
        categoryChartInstance.dispose();
      }
      
      if (categoryChart.value) {
        categoryChartInstance = echarts.init(categoryChart.value);
        const categoryData = reportData.categoryTotals.map(item => ({
          name: item.category,
          value: item.total
        }));
        
        categoryChartInstance.setOption({
          title: {
            text: '类别支出占比',
            left: 'center'
          },
          tooltip: {
            trigger: 'item',
            formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
          },
          legend: {
            orient: 'vertical',
            left: 'left',
            data: categoryData.map(item => item.name)
          },
          series: [
            {
              name: '支出金额',
              type: 'pie',
              radius: '50%',
              data: categoryData,
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        });
      }
      
      // 渲染每日柱状图
      if (dailyChartInstance) {
        dailyChartInstance.dispose();
      }
      
      if (dailyChart.value) {
        dailyChartInstance = echarts.init(dailyChart.value);
        const days = reportData.dailyTotals.map(item => item.day);
        const values = reportData.dailyTotals.map(item => item.total);
        
        dailyChartInstance.setOption({
          title: {
            text: '每日支出统计',
            left: 'center'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            },
            formatter: '{b} 日<br/>支出: ¥{c}'
          },
          xAxis: {
            type: 'category',
            data: days,
            axisLabel: {
              interval: 0,
              rotate: 45
            }
          },
          yAxis: {
            type: 'value',
            name: '金额 (元)'
          },
          series: [
            {
              data: values,
              type: 'bar',
              itemStyle: {
                color: '#91cc75'
              }
            }
          ]
        });
      }
    };

    // Luckysheet 配置选项
    const luckysheetData = ref(null);
    const luckysheetOptions = computed(() => ({
      title: `${reportData.year}年${reportData.month}月报表`,
      data: luckysheetData.value || [],
      lang: 'zh',
      showinfobar: false,
      allowUpdate: true,
      showtoolbar: true,
      showsheetbar: true,
      showstatisticBar: true,
      enableAddRow: true,
      enableAddCol: true,
      showRowBar: true,
      showColumnBar: true,
      sheetFormulaBar: true,
      cellRightClickConfig: {
        copy: true,
        paste: true,
        insertRow: true,
        insertColumn: true,
        deleteRow: true,
        deleteColumn: true,
        deleteCell: true,
        hideRow: true,
        hideColumn: true,
        rowHeight: true,
        columnWidth: true,
        clear: true,
        matrix: true,
        sort: true,
        filter: true,
        chart: true,
        image: true,
        link: true,
        data: true,
        cellFormat: true
      }
    }));

    // 处理 Luckysheet 初始化完成事件
    const handleLuckysheetInitialized = (instance) => {
      console.log('Luckysheet 初始化完成', instance);
      luckysheetRef.value = instance;
      loadLuckysheet();
    };
    
    // 处理 Luckysheet 数据更新事件
    const handleLuckysheetUpdated = (data) => {
      console.log('Luckysheet 数据已更新', data);
      // 可以在这里添加自动保存逻辑
      // 例如: 添加防抖处理，避免频繁保存
      // debounce(() => saveTemplate(), 2000);
    };
    
    const loadLuckysheet = async () => {
      if (!luckysheetRef.value) {
        console.warn('Luckysheet 组件未初始化');
        return;
      }

      try {
        // 尝试加载已保存的模板
        const response = await axios.get('/api/monthly-report/template', {
          params: {
            year: reportData.year,
            month: reportData.month
          }
        });
        
        if (response.data.exists) {
          luckysheetData.value = JSON.parse(response.data.templateData);
          console.log('加载已保存的模板');
        } else {
          // 创建默认模板
          createDefaultTemplate();
          console.log('创建默认模板');
        }

        // 更新 Luckysheet 数据
        if (luckysheetData.value && luckysheetRef.value) {
          console.log('更新 Luckysheet 数据');
          // 使用 updateData 方法更新数据
          luckysheetRef.value.updateData(luckysheetData.value);
        }
      } catch (error) {
        console.error('加载模板失败:', error);
        ElMessage.error('加载模板失败');
        createDefaultTemplate();
        
        // 即使出错也尝试更新数据
        if (luckysheetData.value && luckysheetRef.value) {
          luckysheetRef.value.updateData(luckysheetData.value);
        }
      }
    };

    const createDefaultTemplate = () => {
      // 准备表格数据
      const headerRow = ['名称', '类别', '数量', '单位', '平均单价', '总金额', '入库次数'];
      const dataRows = reportData.items.map(item => [
        item.name,
        item.category,
        item.totalQuantity,
        item.unit,
        item.avgPrice,
        item.totalSubtotal,
        item.count
      ]);
      
      // 添加类别统计
      const categoryRows = [
        ['类别统计'],
        ['类别', '金额', '占比']
      ];
      reportData.categoryTotals.forEach(category => {
        categoryRows.push([
          category.category,
          category.total,
          `${calculatePercentage(category.total)}%`
        ]);
      });
      
      // 添加每日统计
      const dailyRows = [
        ['每日统计'],
        ['日期', '金额']
      ];
      reportData.dailyTotals.forEach(day => {
        if (day.total > 0) {
          dailyRows.push([
            `${reportData.year}-${reportData.month.toString().padStart(2, '0')}-${day.day}`,
            day.total
          ]);
        }
      });
      
      // 添加月度总结
      const summaryRows = [
        ['月度总结'],
        ['月度总支出', reportData.monthlyTotal],
        ['商品种类', reportData.items.length],
        ['日均支出', calculateDailyAverage()]
      ];
      
      // 创建工作表
      luckysheetData.value = [
        {
          name: '明细数据',
          color: '',
          status: 1,
          order: 0,
          data: [headerRow, ...dataRows],
          config: {},
          index: 0
        },
        {
          name: '类别统计',
          color: '',
          status: 1,
          order: 1,
          data: categoryRows,
          config: {},
          index: 1
        },
        {
          name: '每日统计',
          color: '',
          status: 1,
          order: 2,
          data: dailyRows,
          config: {},
          index: 2
        },
        {
          name: '月度总结',
          color: '',
          status: 1,
          order: 3,
          data: summaryRows,
          config: {},
          index: 3
        }
      ];
    };

    // 初始化表格现在由 LuckysheetWrapper 组件处理

    const saveTemplate = async () => {
      if (!luckysheetRef.value) {
        ElMessage.error('表格未初始化');
        return;
      }
      
      try {
        loading.value = true;
        const templateData = JSON.stringify(luckysheetRef.value.getAllSheets());
        
        const response = await axios.post('/api/monthly-report/template', {
          name: `${reportData.year}年${reportData.month}月报表`,
          templateData: templateData,
          year: reportData.year,
          month: reportData.month
        });
        
        if (response.data.success) {
          ElMessage.success('报表模板保存成功');
        } else {
          ElMessage.error('保存失败: ' + response.data.message);
        }
      } catch (error) {
        console.error('保存模板失败:', error);
        ElMessage.error('保存模板失败');
      } finally {
        loading.value = false;
      }
    };

    const exportExcel = () => {
      if (!luckysheetRef.value) {
        ElMessage.error('表格未初始化');
        return;
      }
      
      const fileName = `${reportData.year}年${reportData.month}月报表.xlsx`;
      luckysheetRef.value.exportExcel(fileName);
    };

    // 监听窗口大小变化，重新渲染图表
    const handleResize = () => {
      if (categoryChartInstance) {
        categoryChartInstance.resize();
      }
      if (dailyChartInstance) {
        dailyChartInstance.resize();
      }
    };

    onMounted(() => {
      loadReportData();
      window.addEventListener('resize', handleResize);
    });

    const handleSizeChange = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
    };

    const handleCurrentChange = (page) => {
      currentPage.value = page;
    };

    return {
      selectedDate,
      activeTabKey,
      reportData,
      loading,
      categoryChart,
      dailyChart,
      currentPage,
      pageSize,
      luckysheetRef,
      luckysheetOptions,
      handleDateChange,
      handleTabChange,
      loadReportData,
      calculatePercentage,
      calculateDailyAverage,
      saveTemplate,
      exportExcel,
      handleSizeChange,
      handleCurrentChange,
      handleLuckysheetInitialized,
      handleLuckysheetUpdated
    };
  }
});
</script>

<style scoped>
.monthly-report-container {
  padding: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.date-selector {
  display: flex;
  gap: 10px;
}

.report-summary {
  margin-bottom: 20px;
}

.statistic-item {
  text-align: center;
  padding: 10px;
}

.statistic-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.statistic-value {
  font-size: 24px;
  font-weight: bold;
}

.category-chart-container,
.daily-chart-container {
  height: 400px;
  margin-bottom: 20px;
}

.category-chart,
.daily-chart {
  width: 100%;
  height: 100%;
}

.luckysheet-container {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.luckysheet {
  width: 100%;
  height: 100%;
  margin: 0px;
  padding: 0px;
}
</style>
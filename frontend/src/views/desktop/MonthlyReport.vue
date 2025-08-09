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
      </div>
    </div>

    <div class="report-summary">
      <el-card class="box-card card-hover card-glow" shadow="hover">
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
        <div class="category-chart-container card-hover">
          <div ref="categoryChart" class="category-chart"></div>
        </div>
        <el-table
          :data="reportData.categoryTotals"
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="category" label="类别">
            <template #default="scope">
              {{ getCategoryLabel(scope.row.category) }}
            </template>
          </el-table-column>
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
        <div class="daily-chart-container card-hover">
          <div ref="dailyChart" class="daily-chart"></div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="明细数据" name="3">
        <el-table
          :data="reportData.items.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
          style="width: 100%"
          v-loading="loading"
        >
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="类别">
            <template #default="scope">
              {{ getCategoryLabel(scope.row.category) }}
            </template>
          </el-table-column>
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
    </el-tabs>
  </div>
</template>

<script>
import { defineComponent, ref, reactive, onMounted, nextTick, watch } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import * as echarts from 'echarts';
import dayjs from 'dayjs';

export default defineComponent({
  name: 'MonthlyReport',
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

    // 类别映射表 - 与库存查询页面保持一致
    const categoryMapping = [
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
    ];

    // 获取类别的中文名称
    const getCategoryLabel = (categoryValue) => {
      if (!categoryValue || categoryValue === '未分类') {
        return '未分类';
      }
      const category = categoryMapping.find(item => item.value === categoryValue);
      return category ? category.label : categoryValue;
    };

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
        // 自动加载报表数据
        loadReportData();
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
          name: getCategoryLabel(item.category), // 使用中文名称
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
      handleDateChange,
      handleTabChange,
      loadReportData,
      calculatePercentage,
      calculateDailyAverage,
      handleSizeChange,
      handleCurrentChange,
      getCategoryLabel
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


</style>
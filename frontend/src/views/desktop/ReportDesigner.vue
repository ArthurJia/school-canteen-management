<template>
  <div class="report-designer">
    <el-container>
      <el-header style="height: auto; padding: 16px;">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-button-group>
              <el-button type="primary" @click="saveReport">
                <el-icon><Download /></el-icon>
                保存报表
              </el-button>
              <el-button @click="loadTemplate">
                <el-icon><Upload /></el-icon>
                加载模板
              </el-button>
            </el-button-group>
          </el-col>
        </el-row>
      </el-header>
      <el-main>
        <div id="luckysheet" style="margin: 0px; padding: 0px; position: absolute; width: 100%; height: calc(100% - 80px);"></div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Upload } from '@element-plus/icons-vue'

// Luckysheet配置
const options = {
  container: 'luckysheet',
  showinfobar: false,
  lang: 'zh',
  data: [{
    name: "工作表1",
    color: "",
    status: 1,
    order: 0,
    data: [],
    config: {},
    index: 0
  }],
  // 其他配置项...
}

// 保存报表
const saveReport = async () => {
  try {
    const data = window.luckysheet.getAllSheets()
    // TODO: 调用后端API保存报表数据
    ElMessage.success('报表保存成功')
  } catch (error) {
    console.error('保存报表失败:', error)
    ElMessage.error('保存报表失败')
  }
}

// 加载模板
const loadTemplate = async () => {
  try {
    // TODO: 实现模板加载逻辑
    ElMessage.success('模板加载成功')
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  }
}

onMounted(() => {
  // 动态加载Luckysheet资源
  const loadLuckysheet = async () => {
    try {
      // 加载CSS
      const linkElement = document.createElement('link')
      linkElement.rel = 'stylesheet'
      linkElement.href = '/libs/luckysheet/css/luckysheet.css'
      document.head.appendChild(linkElement)

      // 加载依赖的插件
      await Promise.all([
        loadScript('/libs/luckysheet/plugins/js/plugin.js'),
        loadScript('/libs/luckysheet/plugins/js/spectrum.min.js'),
      ])
      
      // 加载中文语言包
      await loadScript('/libs/luckysheet/plugins/js/locale/zh.js')

      // 加载主要JS文件
      await loadScript('/libs/luckysheet/js/luckysheet.umd.js')

      // 初始化Luckysheet
      window.luckysheet.create(options)
    } catch (error) {
      console.error('加载Luckysheet失败:', error)
      ElMessage.error('加载报表组件失败')
    }
  }

  loadLuckysheet()
})

onUnmounted(() => {
  // 清理Luckysheet实例
  if (window.luckysheet) {
    window.luckysheet.destroy()
  }
})

// 辅助函数：加载脚本
const loadScript = (src) => {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = src
    script.onload = resolve
    script.onerror = reject
    document.head.appendChild(script)
  })
}
</script>

<style scoped>
.report-designer {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

:deep(.el-main) {
  padding: 0;
  position: relative;
  flex: 1;
  overflow: hidden;
}
</style>
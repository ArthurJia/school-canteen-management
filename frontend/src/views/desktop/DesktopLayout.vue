<template>
  <el-container class="desktop-layout">
    <el-aside :width="sidebarCollapsed ? '60px' : '220px'" class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <!-- 折叠按钮 -->
      <div class="collapse-button" @click="toggleSidebar">
        <el-icon>
          <ArrowLeft v-if="!sidebarCollapsed" />
          <ArrowRight v-if="sidebarCollapsed" />
        </el-icon>
      </div>
      
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">
            <el-icon size="24"><Menu /></el-icon>
          </div>
          <div class="logo-text" v-show="!sidebarCollapsed">操作目录</div>
        </div>
      </div>
      <div class="menu-container">
        <el-menu
          router
          :default-active="$route.path"
          class="side-menu"
          :collapse="sidebarCollapsed"
          background-color="transparent"
          text-color="#606266"
          active-text-color="#409eff">
          <el-menu-item index="/desktop/inbound" class="menu-item">
            <el-icon><Goods /></el-icon>
            <span>入库管理</span>
          </el-menu-item>
          <el-menu-item index="/desktop/stock" class="menu-item">
            <el-icon><PieChart /></el-icon>
            <span>库存查询</span>
          </el-menu-item>
          <el-menu-item index="/desktop/supplier" class="menu-item">
            <el-icon><User /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="/desktop/monthly-inventory" class="menu-item">
            <el-icon><Document /></el-icon>
            <span>月底盘点明细</span>
          </el-menu-item>
          <el-menu-item index="/desktop/report" class="menu-item">
            <el-icon><Document /></el-icon>
            <span>月度报表</span>
          </el-menu-item>
          <el-menu-item index="/desktop/report-designer" class="menu-item">
            <el-icon><Edit /></el-icon>
            <span>报表设计及导出</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="system-title">中华路小学食堂管理系统</div>
          <div class="header-actions">
            <el-button type="text" class="user-info">
              <el-icon><User /></el-icon>
              <span>管理员</span>
            </el-button>
          </div>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, provide, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 提供导航栏状态给子组件
provide('sidebarCollapsed', sidebarCollapsed)

// 监听导航栏状态变化，触发窗口resize事件以便Luckysheet重新调整大小
watch(sidebarCollapsed, () => {
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'))
  }, 300) // 等待CSS动画完成
})
</script>

<style scoped>
.desktop-layout {
  height: 100vh;
  background-color: #f8f9fa;
}

/* 侧边栏样式 */
.sidebar {
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  transition: width 0.3s ease;
  position: relative;
  overflow: visible; /* 允许折叠按钮超出边界 */
}

/* 为了防止内容滚动，只对内容区域设置overflow */
.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  pointer-events: none;
}

/* 折叠按钮 */
.collapse-button {
  position: absolute;
  top: 50%;
  right: -15px;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1001; /* 提高层级确保显示在最上层 */
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
  color: white;
  border: none;
  outline: none;
  overflow: visible; /* 确保按钮内容不被裁切 */
}

/* 确保折叠按钮内的图标完全显示 */
.collapse-button .el-icon {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.collapse-button:hover {
  background: #337ecc;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 侧边栏收缩状态 */
.sidebar.collapsed .sidebar-header {
  padding: 0 8px;
}

.sidebar.collapsed .logo-container {
  justify-content: center;
  gap: 0;
  width: 100%;
}

.sidebar.collapsed .side-menu {
  padding: 16px 4px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  position: relative;
  overflow: hidden;
  z-index: 1; /* 确保不会覆盖折叠按钮 */
}

.sidebar-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.menu-container {
  height: calc(100vh - 64px);
  overflow: hidden; /* 防止菜单容器出现滚动条 */
  display: flex;
  flex-direction: column;
  z-index: 1; /* 确保不会覆盖折叠按钮 */
}

.side-menu {
  border: none;
  background: transparent;
  flex: 1;
  padding: 16px 8px;
  overflow: hidden; /* 防止菜单出现滚动条 */
  min-height: 0; /* 确保flex子元素能正确收缩 */
}

.menu-item {
  margin: 4px 0;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.menu-item:hover {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.menu-item.is-active {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.menu-item.is-active .el-icon,
.menu-item.is-active span {
  color: #fff !important;
}

.menu-item .el-icon {
  margin-right: 8px;
  font-size: 18px;
  transition: all 0.3s ease;
}

.menu-item span {
  font-weight: 500;
  transition: all 0.3s ease;
}

/* 确保Element Plus菜单组件不出现滚动条 */
:deep(.el-menu) {
  overflow: hidden !important;
}

:deep(.el-menu-item) {
  overflow: hidden !important;
}

/* 防止菜单项文字溢出 */
:deep(.el-menu-item span) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 收缩状态下菜单图标居中显示 */
.sidebar.collapsed :deep(.el-menu-item) {
  justify-content: center !important;
  padding: 0 !important;
}

.sidebar.collapsed :deep(.el-menu-item .el-icon) {
  margin-right: 0 !important;
}

/* 收缩状态下的菜单项样式调整 */
.sidebar.collapsed .menu-item {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 4px 2px;
}

.sidebar.collapsed .menu-item .el-icon {
  margin-right: 0;
}

/* 头部样式 */
.header {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 24px;
  height: 64px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
}

.system-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
  font-weight: 500;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}

/* 主内容区域 */
.main-content {
  background-color: #f8f9fa;
  padding: 24px;
  min-height: calc(100vh - 64px);
}



/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .sidebar {
    width: 180px !important;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .system-title {
    font-size: 20px;
  }
}

@media screen and (max-width: 768px) {
  .sidebar {
    width: 160px !important;
  }
  
  .sidebar-header {
    padding: 0 12px;
  }
  
  .logo-text {
    display: none;
  }
  
  .system-title {
    font-size: 18px;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style>
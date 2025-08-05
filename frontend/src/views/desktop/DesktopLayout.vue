<template>
  <el-container class="desktop-layout">
    <el-aside width="220px" class="sidebar">
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">
            <el-icon size="24"><i-ep-Menu /></el-icon>
          </div>
          <div class="logo-text">操作目录</div>
        </div>
      </div>
      <div class="menu-container">
        <el-menu
          router
          :default-active="$route.path"
          class="side-menu"
          background-color="transparent"
          text-color="#606266"
          active-text-color="#409eff">
          <el-menu-item index="/desktop/inbound" class="menu-item">
            <el-icon><i-ep-Goods /></el-icon>
            <span>入库管理</span>
          </el-menu-item>
          <el-menu-item index="/desktop/stock" class="menu-item">
            <el-icon><i-ep-PieChart /></el-icon>
            <span>库存查询</span>
          </el-menu-item>
          <el-menu-item index="/desktop/supplier" class="menu-item">
            <el-icon><i-ep-User /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="/desktop/report" class="menu-item">
            <el-icon><i-ep-Document /></el-icon>
            <span>月度报表</span>
          </el-menu-item>
          <el-menu-item index="/desktop/report-designer" class="menu-item">
            <el-icon><i-ep-Edit /></el-icon>
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
              <el-icon><i-ep-User /></el-icon>
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
import { ref } from 'vue'
const userAvatar = ref('https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png')
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
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  position: relative;
  overflow: hidden;
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
  overflow: hidden;
}

.side-menu {
  border: none;
  background: transparent;
  height: 100%;
  padding: 16px 8px;
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
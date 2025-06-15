<template>
  <div class="mobile-layout">
    <div class="header">
      <h1 class="title">中华路小学食堂管理系统</h1>
    </div>
    
    <div class="content">
      <router-view />
    </div>
    
    <div class="bottom-nav">
      <router-link to="/mobile/inbound" class="nav-item">
        <el-icon class="nav-icon"><i-ep-Goods /></el-icon>
        <span class="nav-text">入库</span>
      </router-link>
      <router-link to="/mobile/stock" class="nav-item">
        <el-icon class="nav-icon"><i-ep-PieChart /></el-icon>
        <span class="nav-text">库存</span>
      </router-link>
      <router-link to="/mobile/supplier" class="nav-item">
        <el-icon class="nav-icon"><i-ep-User /></el-icon>
        <span class="nav-text">供应商</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
// 移动端布局逻辑
</script>

<style scoped>
.mobile-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.header {
  padding: 12px;
  background-color: #409EFF;
  color: white;
}
.title {
  margin: 0;
  font-size: 22px;
  text-align: center;
}
.content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: #f5f7fa;
}
.bottom-nav {
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  background-color: white;
  border-top: 1px solid #eee;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #666;
}
.nav-item.router-link-active {
  color: #409EFF;
}
.nav-icon {
  font-size: 24px;
}
.nav-text {
  font-size: 12px;
  margin-top: 4px;
}
</style>
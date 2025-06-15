<template>
  <el-container class="desktop-layout">
    <el-aside width="200px">
      <div class="logo">操作目录</div>
      <el-menu
        router
        :default-active="$route.path"
        class="side-menu"
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b">
        <el-menu-item index="/desktop/inbound">
          <el-icon><i-ep-Goods /></el-icon>
          <span>入库管理</span>
        </el-menu-item>
        <el-menu-item index="/desktop/stock">
          <el-icon><i-ep-PieChart /></el-icon>
          <span>库存查询</span>
        </el-menu-item>
        <el-menu-item index="/desktop/supplier">
          <el-icon><i-ep-User /></el-icon>
          <span>供应商管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="system-title">中华路小学食堂管理系统</div>
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
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #434a50;
  font-size: 18px;
  font-weight: bold;
}
.side-menu {
  height: calc(100vh - 60px);
}
.header {
  background-color: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: center;
}
.system-title {
  font-size: 22px;
  font-weight: bold;
  color: #333;
  text-align: center;
  width: 100%;
}
.main-content {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
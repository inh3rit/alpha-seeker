<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="logo">Alpha Seeker</div>
      <el-menu mode="horizontal" :router="true" :default-active="$route.path">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/recommendations">推荐</el-menu-item>
        <el-menu-item index="/rankings">排行榜</el-menu-item>
        <el-menu-item index="/positions">持仓</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.app-container {
  min-height: 100vh;
}
.app-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #eee;
}
.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 40px;
  color: #409eff;
}
</style>

<script>
export default {
  name: 'App'
}
</script>

<template>
  <el-container class="app-container">
    <el-header class="header">
      <div class="header-content">
        <h1>AI面试官</h1>
        <el-menu mode="horizontal" router :default-active="$route.path" class="nav-menu">
          <el-menu-item index="/">
            <i class="el-icon-microphone"></i>
            面试
          </el-menu-item>
          <el-menu-item index="/history">
            <i class="el-icon-time"></i>
            历史记录
          </el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: fixed;
  left: 0;
  top: 0;
}

.app-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #6B2B63;
  position: relative;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: rgba(107, 43, 99, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  height: 60px !important;
  width: 100%;
}

.header-content {
  width: 100%;
  height: 100%;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.header h1 {
  margin: 0;
  font-size: 1.8em;
  color: white;
  font-weight: 600;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 1px;
  white-space: nowrap;
}

.nav-menu {
  background-color: transparent !important;
  border-bottom: none !important;
  display: flex;
  align-items: center;
  height: 100%;
}

.el-menu-item {
  color: rgba(255, 255, 255, 0.9) !important;
  font-size: 1.1em;
  height: 100% !important;
  line-height: 60px !important;
  padding: 0 25px !important;
  transition: all 0.3s ease;
}

.el-menu-item i {
  margin-right: 5px;
  font-size: 1.2em;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.15) !important;
  color: white !important;
  transform: translateY(-2px);
}

.el-main {
  padding: 0 !important;
  margin: 0 !important;
  height: 100vh !important;
  width: 100vw !important;
  overflow: hidden;
  position: relative;
}

/* Global styles for Element Plus components */
:root {
  --el-color-primary: #409EFF;
  --el-color-success: #67C23A;
  --el-color-warning: #E6A23C;
  --el-color-danger: #F56C6C;
  --el-color-info: #909399;
}

.el-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.el-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 45px rgba(0, 0, 0, 0.2);
}

.el-button {
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* Responsive design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: row;
    padding: 5px 10px;
  }

  .header h1 {
    font-size: 1.4em;
    margin: 0;
  }

  .nav-menu {
    padding: 0;
  }

  .el-menu-item {
    padding: 0 15px !important;
  }

  .el-main {
    margin-top: 50px;
  }
}
</style>

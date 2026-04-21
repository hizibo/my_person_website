<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  background-color: #f5f7fa;
}

#app {
  min-height: 100vh;
}

/* ========== 响应式基础 ========== */
/* 平板/大手机横屏 */
@media screen and (max-width: 1024px) {
  body {
    font-size: 14px;
  }
}

/* 手机 */
@media screen and (max-width: 768px) {
  body {
    font-size: 13px;
  }
}
</style>

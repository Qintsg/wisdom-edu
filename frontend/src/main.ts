/**
 * 应用入口文件
 * 初始化Vue应用，注册插件和全局组件
 */
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import { pinia } from './stores'
import router from './router'
import App from './App.vue'
import './styles/index.css'
import './styles/glassmorphism.css'
import { createLogger, installConsoleFormat } from './utils/logger'

installConsoleFormat()
const appLogger = createLogger('应用')

// 创建Vue应用实例
const app = createApp(App)

// 注册所有Element Plus图标为全局组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册插件
app.use(pinia)        // Pinia状态管理
app.use(router)       // Vue Router路由
app.use(ElementPlus, {
  locale: zhCn,       // Element Plus中文语言包
  size: 'default'     // 默认组件尺寸
})

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  appLogger.error('全局错误', err)
  appLogger.error('错误信息', info)
}

// 挂载应用
app.mount('#app')

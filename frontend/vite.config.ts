import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { copyFileSync, writeFileSync } from 'node:fs'

/**
 * 统一清洗代理目标地址，避免拼接时出现尾部斜杠或空值。
 */
function normalizeProxyTarget(rawTarget: string | undefined, fallbackTarget: string): string {
  return (rawTarget?.trim() || fallbackTarget).replace(/\/+$/, '')
}

/**
 * Vite 配置文件
 * 自适应学习系统前端构建配置
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const developmentBackendTarget = normalizeProxyTarget(
    env.VITE_DEV_BACKEND_ORIGIN,
    'http://127.0.0.1:8000'
  )
  const developmentWebSocketTarget = developmentBackendTarget
    .replace(/^http:/, 'ws:')
    .replace(/^https:/, 'wss:')

  return {
    plugins: [
      vue(),
      /* 构建结束后生成 SPA fallback 文件，解决静态部署刷新 404 问题 */
      {
        name: 'spa-fallback',
        closeBundle() {
          // GitHub Pages 等服务：把 404 页面指向 SPA 入口
          copyFileSync('dist/index.html', 'dist/404.html')
          // Netlify / Cloudflare Pages：重写所有路径到 index.html
          writeFileSync('dist/_redirects', '/* /index.html 200\n')
        }
      }
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true,
      proxy: {
        // 仅开发模式使用 Vite 代理；生产静态部署默认走同域反向代理。
        '/api': {
          target: developmentBackendTarget,
          changeOrigin: true
        },
        '/media': {
          target: developmentBackendTarget,
          changeOrigin: true
        },
        '/static': {
          target: developmentBackendTarget,
          changeOrigin: true
        },
        '/ws': {
          target: developmentWebSocketTarget,
          changeOrigin: true,
          ws: true
        }
      }
    },
    preview: {
      host: '0.0.0.0',
      port: 3000,
      strictPort: true
    },
    build: {
      // 代码分割优化
      rollupOptions: {
        output: {
          manualChunks(moduleId) {
            if (!moduleId.includes('node_modules')) {
              return
            }

            // 核心框架
            if (
              moduleId.includes('/vue/')
              || moduleId.includes('vue-router')
              || moduleId.includes('/pinia/')
            ) {
              return 'vue-core'
            }

            // UI组件库
            if (
              moduleId.includes('element-plus')
              || moduleId.includes('@element-plus/icons-vue')
            ) {
              return 'element-plus'
            }

            // 可视化库
            if (moduleId.includes('/echarts/')) {
              return 'echarts'
            }
          }
        }
      },
      // 增加警告阈值
      chunkSizeWarningLimit: 600
    }
  }
})

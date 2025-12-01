<template>
  <div class="radar-chart-wrapper">
    <div ref="chartRef" class="chart-container" :style="{ height: height }"></div>

    <!-- 空状态 -->
    <div v-if="!hasData" class="empty-overlay">
      <el-icon :size="48" color="#c0c4cc">
        <PieChart />
      </el-icon>
      <p>暂无数据</p>
    </div>
  </div>
</template>

<script setup>
/**
 * 雷达图组件
 * 用于展示能力评估、知识掌握度等多维数据
 * 基于 ECharts 实现
 */
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { PieChart } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  max: {
    type: Number,
    default: 100
  },
  height: {
    type: String,
    default: '300px'
  },
  color: {
    type: String,
    default: '#409eff'
  },
  title: {
    type: String,
    default: ''
  },
  showValue: {
    type: Boolean,
    default: true
  },
  animation: {
    type: Boolean,
    default: true
  }
})

const chartRef = ref(null)
let chartInstance = null

const hasData = computed(() => props.data && props.data.length > 0)

const indicators = computed(() =>
  props.data.map(item => ({
    name: item.name,
    min: item.min ?? 0,
    max: item.max || props.max
  }))
)

const values = computed(() => props.data.map(item => item.value))

const getOption = () => ({
  title: props.title ? {
    text: props.title,
    left: 'center',
    top: 10,
    textStyle: {
      fontSize: 16,
      fontWeight: 500,
      color: '#303133'
    }
  } : undefined,
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: '#e4e7ed',
    borderWidth: 1,
    textStyle: {
      color: '#606266'
    },
    formatter: (params) => {
      const data = props.data
      let html = `<div style="padding: 4px 8px;">`
      data.forEach((item, index) => {
        const max = item.max || props.max
        const percent = ((item.value / max) * 100).toFixed(1)
        html += `
          <div style="margin: 4px 0;">
            <span style="display: inline-block; width: 8px; height: 8px; 
                   background: ${props.color}; border-radius: 50%; margin-right: 8px;">
            </span>
            ${item.name}: ${item.value} / ${max} (${percent}%)
          </div>
        `
      })
      html += '</div>'
      return html
    }
  },
  radar: {
    indicator: indicators.value,
    shape: 'polygon',
    splitNumber: 5,
    center: ['50%', '55%'],
    radius: '65%',
    axisName: {
      color: '#606266',
      fontSize: 12,
      padding: [3, 5]
    },
    axisLabel: {
      show: false
    },
    axisTick: {
      show: false
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(0, 0, 0, 0.1)',
        type: 'dashed'
      }
    },
    splitArea: {
      show: true,
      areaStyle: {
        color: ['rgba(64, 158, 255, 0.02)', 'rgba(64, 158, 255, 0.04)']
      }
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    }
  },
  series: [{
    type: 'radar',
    data: [{
      value: values.value,
      name: '能力值',
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2,
        color: props.color
      },
      areaStyle: {
        color: {
          type: 'radial',
          x: 0.5,
          y: 0.5,
          r: 0.5,
          colorStops: [
            { offset: 0, color: `${props.color}40` },
            { offset: 1, color: `${props.color}10` }
          ]
        }
      },
      itemStyle: {
        color: props.color,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: props.showValue ? {
        show: true,
        formatter: '{c}',
        color: '#606266',
        fontSize: 11
      } : undefined
    }],
    animationDuration: props.animation ? 1000 : 0,
    animationEasing: 'elasticOut'
  }]
})

const initChart = () => {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  if (hasData.value) {
    chartInstance.setOption(getOption())
  }
}

const updateChart = () => {
  if (chartInstance && hasData.value) {
    chartInstance.setOption(getOption(), true)
  }
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.data, () => {
  nextTick(updateChart)
}, { deep: true })

watch(() => props.color, updateChart)

onMounted(() => {
  nextTick(initChart)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

defineExpose({
  refresh: updateChart,
  resize: handleResize
})
</script>

<style scoped>
.radar-chart-wrapper {
  position: relative;
  width: 100%;
  background: var(--bg-card);
  border-radius: var(--radius-base);
  padding: 16px;
  animation: fadeIn 0.5s ease-out;
}

.chart-container {
  width: 100%;
}

.empty-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-base);
}

.empty-overlay p {
  margin-top: 12px;
  color: var(--text-placeholder);
  font-size: var(--font-size-sm);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>

/**
 * AI 异步任务伪加载进度 composable
 *
 * 提供平滑递增的虚拟进度条 + 阶段性文字动画，
 * 适用于所有需要等待 AI 后端处理的场景（路径生成、学习建议生成等）。
 *
 * 用法：
 *   const { progress, stageText, start, complete, reset, isRunning } = useAIProgress(options)
 *
 * --- DEMO_EMBED: 答辩演示专用，后续可删除本文件中标记行 ---
 */
import { ref, computed, onUnmounted } from 'vue'

/* ---- 类型定义 ---- */

/** 单条阶段描述 */
export interface ProgressStage {
  /** 进入该阶段的最低进度百分比 (0-100) */
  at: number
  /** 阶段提示文字 */
  text: string
}

/** composable 配置项 */
export interface AIProgressOptions {
  /** 最大虚拟等待时长(ms)，到达后进度停在 maxPercent，默认 120000 (2min) */
  maxDuration?: number
  /** 进度上限百分比，真正完成前不会超过此值，默认 95 */
  maxPercent?: number
  /** 进度递增的定时器间隔(ms)，默认 400 */
  tickInterval?: number
  /** 阶段文字列表，按 at 升序排列 */
  stages?: ProgressStage[]
}

/* ---- 默认阶段（通用 AI 任务） ---- */
const DEFAULT_STAGES: ProgressStage[] = [
  { at: 0, text: '正在连接 AI 服务…' },
  { at: 10, text: '正在分析你的学习数据…' },
  { at: 25, text: '知识追踪模型推理中…' },
  { at: 40, text: '正在查询知识图谱关联…' },
  { at: 55, text: '生成个性化方案中…' },
  { at: 70, text: '优化学习路径排序…' },
  { at: 85, text: '即将完成，请稍候…' },
]

/* ---- composable 主体 ---- */
export function useAIProgress(options: AIProgressOptions = {}) {
  const {
    maxDuration = 120_000,
    maxPercent = 95,
    tickInterval = 400,
    stages = DEFAULT_STAGES,
  } = options

  /* 响应式状态 */
  const progress = ref(0)
  const isRunning = ref(false)

  /* 内部变量 */
  let timer: ReturnType<typeof setInterval> | null = null
  let startTs = 0

  const stageText = computed(() => {
    // 找到 at <= progress 的最后一条
    let text = stages[0]?.text ?? '处理中…'
    for (const s of stages) {
      if (s.at <= progress.value) text = s.text
      else break
    }
    return text
  })

  /**
   * 每 tick 递增进度
   * 采用"快—慢—极慢"三段速率，模拟真实 AI 处理体感
   */
  const tick = () => {
    const elapsed = Date.now() - startTs
    const ratio = Math.min(elapsed / maxDuration, 1)

    // 非线性衰减：前半快、后半慢
    // p = maxPercent * (1 - e^(-3*ratio))  → 初速快、渐近 maxPercent
    const target = maxPercent * (1 - Math.exp(-3 * ratio))

    // 平滑追赶，每次最多跳 1.5
    if (progress.value < target) {
      progress.value = Math.min(
        Math.round(progress.value + Math.max(0.3, (target - progress.value) * 0.15)),
        maxPercent,
      )
    }

    // 超时保护
    if (elapsed >= maxDuration) {
      progress.value = maxPercent
      stop()
    }
  }

  /** 启动伪进度 */
  const start = () => {
    stop() // 幂等：先清旧定时器
    progress.value = 0
    isRunning.value = true
    startTs = Date.now()
    timer = setInterval(tick, tickInterval)
    tick() // 立即执行一次，避免首帧空白
  }

  /** 标记完成：进度跳到 100 并停止 */
  const complete = () => {
    stop()
    progress.value = 100
  }

  /** 重置到初始状态 */
  const reset = () => {
    stop()
    progress.value = 0
  }

  /** 内部停止定时器 */
  const stop = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    isRunning.value = false
  }

  /* 组件卸载时自动清理 */
  onUnmounted(stop)

  return {
    /** 当前进度 0-100 */
    progress,
    /** 当前阶段提示文字 */
    stageText,
    /** 是否正在递增中 */
    isRunning,
    /** 开始伪进度 */
    start,
    /** 标记真正完成（跳到100） */
    complete,
    /** 重置归零 */
    reset,
  }
}

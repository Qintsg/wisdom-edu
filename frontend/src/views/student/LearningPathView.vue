<template>
  <div class="learning-path-view">
    <el-alert v-if="needAssessment" type="warning" :title="assessmentHint" show-icon :closable="false"
      class="assessment-alert">
      <template #default>
        <el-button type="warning" link @click="goToAssessment">
          前往初始测评
        </el-button>
      </template>
    </el-alert>

    <!-- 头部统计卡片 -->
    <el-card class="path-header" shadow="hover">
      <div class="header-top">
        <div class="header-title-row">
          <h2>学习路径</h2>
          <el-button type="primary" plain @click="refreshPath" :disabled="needAssessment" :loading="refreshingPath"
            class="refresh-btn">
            主动刷新路径
          </el-button>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-value">{{ completedNodes }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalNodes }}</div>
            <div class="stat-label">总任务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ progressPercent }}%</div>
            <div class="stat-label">完成度</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 路径主内容区 -->
    <el-card class="path-content" shadow="hover">
      <!-- 路径生成中 —— DEMO_EMBED: 答辩演示伪进度条 -->
      <div v-if="showRefreshingAnimation" class="generating-container">
        <el-icon class="is-loading" :size="48" color="#667eea">
          <Loading />
        </el-icon>
        <h3>{{ aiProgressStageText }}</h3>
        <el-progress :percentage="aiProgressPercentage" :stroke-width="10" :show-text="true"
          style="width: 320px; margin: 12px 0;" />
        <p style="color: #909399;">{{ refreshingDescription }}</p>
        <el-button v-if="!refreshingPath && !isAiProgressRunning" type="primary" style="margin-top: 16px;"
          @click="loadLearningPath">刷新查看</el-button>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="loadError" :description="loadError">
        <el-button type="primary" @click="loadLearningPath">重新加载</el-button>
      </el-empty>
      <el-empty v-else-if="!courseStore.courseId" description="请先在顶部选择课程" />
      <el-empty v-else-if="!pathNodes.length && needAssessment" description="请先完成初始测评以生成个性化学习路径">
        <el-button type="primary" @click="goToAssessment">前往初始测评</el-button>
      </el-empty>
      <el-empty v-else-if="!pathNodes.length" description="暂无学习路径数据" />

      <!-- 横向步骤条（地铁线路图风格） -->
      <template v-else>
        <div class="subway-track-wrapper" ref="trackWrapperRef">
          <div class="subway-track" ref="trackRef">
            <div v-for="(pathNode, idx) in pathNodes" :key="pathNode.nodeId" class="subway-station"
              :class="{ active: selectedNode?.nodeId === pathNode.nodeId }" @click="selectNode(pathNode)">
              <!-- 连接线（第一个节点前不加） -->
              <div v-if="idx > 0" class="station-line"
                :class="{ done: pathNodes[idx - 1].learningStatus === 'completed' }" />
              <!-- 站点圆圈 -->
              <div class="station-dot" :class="[pathNode.learningStatus, pathNode.nodeTypeText]">
                <el-icon v-if="pathNode.learningStatus === 'completed'" :size="14">
                  <Check />
                </el-icon>
                <el-icon v-else-if="pathNode.nodeTypeText === 'test'" :size="14">
                  <Edit />
                </el-icon>
                <span v-else class="dot-index">{{ idx + 1 }}</span>
              </div>
              <!-- 站点名称 -->
              <div class="station-label" :class="pathNode.learningStatus">
                {{ pathNode.titleText }}
              </div>
            </div>
          </div>
        </div>

        <!-- 选中节点的详情面板 -->
        <transition name="detail-fade">
          <div v-if="selectedNode" class="node-detail-panel">
            <div class="detail-header">
              <div class="detail-title-row">
                <el-icon v-if="selectedNode.nodeTypeText === 'test'" style="color: #e6a23c; font-size: 20px;">
                  <Edit />
                </el-icon>
                <h3>{{ selectedNode.titleText }}</h3>
                <el-tag v-if="selectedNode.nodeTypeText === 'test'" type="warning" size="small">测试</el-tag>
                <el-tag :type="getNodeTagType(selectedNode.learningStatus)" size="small">
                  {{ getNodeStatusText(selectedNode.learningStatus) }}
                </el-tag>
              </div>
              <div class="detail-meta">
                <span><el-icon>
                    <Clock />
                  </el-icon> 预计 {{ selectedNode.durationMinutes }} 分钟</span>
              </div>
            </div>

            <div class="detail-body">
              <p class="detail-desc">{{ selectedNode.descriptionText }}</p>
              <div v-if="selectedNode.suggestionText" class="detail-suggestion">
                <el-icon>
                  <MagicStick />
                </el-icon>
                <span>{{ selectedNode.suggestionText }}</span>
              </div>
            </div>

            <div class="detail-actions">
              <!-- 当前节点 - 测试类型 -->
              <template v-if="selectedNode.learningStatus === 'current' && selectedNode.nodeTypeText === 'test'">
                <el-button type="warning" @click="startLearning(selectedNode)">
                  <el-icon style="margin-right: 4px;">
                    <Edit />
                  </el-icon> 开始测试
                </el-button>
                <el-button plain @click="handleSkipNode(selectedNode)">跳过</el-button>
              </template>
              <!-- 当前节点 - 学习类型 -->
              <template v-else-if="selectedNode.learningStatus === 'current'">
                <el-button type="primary" @click="startLearning(selectedNode)">开始学习</el-button>
                <el-button type="success" plain @click="handleCompleteNode(selectedNode)">标记完成</el-button>
                <el-button plain @click="handleSkipNode(selectedNode)">跳过</el-button>
              </template>
              <!-- 已完成 - 测试类型 -->
              <template v-else-if="selectedNode.learningStatus === 'completed' && selectedNode.nodeTypeText === 'test'">
                <el-button type="primary" plain @click="viewTestReport(selectedNode)">查看报告</el-button>
                <el-button type="warning" plain @click="startLearning(selectedNode)">再做一次</el-button>
              </template>
              <!-- 已完成 - 学习类型 -->
              <el-button v-else-if="selectedNode.learningStatus === 'completed'" @click="reviewNode(selectedNode)">
                复习巩固
              </el-button>
              <el-button v-else-if="selectedNode.learningStatus === 'skipped'" type="warning" plain
                @click="startLearning(selectedNode)">
                返回学习
              </el-button>
              <el-button v-else disabled>待解锁</el-button>
            </div>
          </div>
        </transition>

        <!-- 未选中节点时的提示 -->
        <div v-if="!selectedNode" class="select-hint">
          <el-icon :size="32" color="#c0c4cc">
            <Pointer />
          </el-icon>
          <p>点击上方节点查看详情和操作</p>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 学习路径视图
 * 横向步骤条（地铁线路图）+ 下方详情面板
 */
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import {
  getLearningPath,
  startLearningNode,
  completePathNode,
  skipPathNode,
  refreshLearningPathWithAI
} from '@/api/student/learning'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Edit, Check, Pointer } from '@element-plus/icons-vue'
import { MagicStick, Loading } from '@element-plus/icons-vue'
import { useAIProgress } from '@/composables/useAIProgress'

/**
 * 统一收敛文本字段，避免模板直接读取动态 payload。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return String(rawValue)
  }
  return ''
}

/**
 * 统一收敛标识符，页面层只消费稳定字符串 ID。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  const normalizedText = normalizeText(rawValue)
  return normalizedText ? normalizedText : ''
}

/**
 * 统一收敛数值字段，避免 NaN 进入页面统计或文案。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将任意 payload 收敛为数组。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 收敛学习节点状态，统一映射到页面展示语义。
 * @param {unknown} rawStatus
 * @returns {'completed' | 'current' | 'skipped' | 'pending'}
 */
const normalizeLearningStatus = (rawStatus) => {
  const statusText = normalizeText(rawStatus)

  if (statusText === 'completed') {
    return 'completed'
  }
  if (statusText === 'active' || statusText === 'in_progress' || statusText === 'failed') {
    return 'current'
  }
  if (statusText === 'skipped') {
    return 'skipped'
  }
  return 'pending'
}

/**
 * 收敛节点时长字段，优先 estimated_minutes，其次 estimated_time。
 * @param {unknown} rawValue
 * @returns {number}
 */
const normalizeDurationMinutes = (rawValue) => {
  const durationMinutes = normalizeNumber(rawValue, 30)
  return durationMinutes > 0 ? durationMinutes : 30
}

/**
 * @typedef {Object} LearningPathNodeModel
 * @property {string} nodeId
 * @property {string} titleText
 * @property {string} descriptionText
 * @property {string} suggestionText
 * @property {'completed' | 'current' | 'skipped' | 'pending'} learningStatus
 * @property {number} durationMinutes
 * @property {number} resourceCount
 * @property {string} pointId
 * @property {string} nodeTypeText
 * @property {boolean} isInserted
 */

/**
 * 构造默认路径节点模型。
 * @returns {LearningPathNodeModel}
 */
const buildDefaultLearningPathNode = () => ({
  nodeId: '',
  titleText: '',
  descriptionText: '',
  suggestionText: '',
  learningStatus: 'pending',
  durationMinutes: 30,
  resourceCount: 0,
  pointId: '',
  nodeTypeText: 'study',
  isInserted: false
})

/**
 * 将学习路径节点统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawNode
 * @returns {LearningPathNodeModel}
 */
const normalizeLearningPathNode = (rawNode) => ({
  ...buildDefaultLearningPathNode(),
  nodeId: normalizeIdentifier(rawNode?.node_id ?? rawNode?.id),
  titleText: normalizeText(rawNode?.title) || '未命名节点',
  descriptionText: normalizeText(rawNode?.goal ?? rawNode?.description) || '暂无描述',
  suggestionText: normalizeText(rawNode?.suggestion),
  learningStatus: normalizeLearningStatus(rawNode?.status),
  durationMinutes: normalizeDurationMinutes(rawNode?.estimated_minutes ?? rawNode?.estimated_time),
  resourceCount: normalizeNumber(rawNode?.tasks_count ?? rawNode?.resource_count),
  pointId: normalizeIdentifier(rawNode?.knowledge_point_id ?? rawNode?.pointId),
  nodeTypeText: normalizeText(rawNode?.node_type ?? rawNode?.nodeType) || 'study',
  isInserted: Boolean(rawNode?.is_inserted)
})

/**
 * 收敛学习路径主接口响应。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ needAssessment: boolean, assessmentHint: string, generating: boolean, nodes: LearningPathNodeModel[] }}
 */
const normalizeLearningPathPayload = (rawPayload) => ({
  needAssessment: Boolean(rawPayload?.need_assessment),
  assessmentHint: normalizeText(rawPayload?.next_step_msg) || '请先完成初始评测后再进入学习路径',
  generating: Boolean(rawPayload?.generating),
  nodes: normalizeListFromPayload(rawPayload?.nodes)
    .map((pathNode) => normalizeLearningPathNode(pathNode))
})

/**
 * 收敛刷新路径后的摘要响应。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ preservedCount: number, newCount: number, changeSummary: { preservedContext: number, removedCount: number }, ktInfo: { answerCount: number }, profile: { summaryText: string } }}
 */
const normalizeLearningPathRefreshSummary = (rawPayload) => ({
  preservedCount: normalizeNumber(rawPayload?.preserved_count),
  newCount: normalizeNumber(rawPayload?.new_count),
  changeSummary: {
    preservedContext: normalizeNumber(rawPayload?.change_summary?.preserved_context),
    removedCount: normalizeNumber(rawPayload?.change_summary?.removed_count)
  },
  ktInfo: {
    answerCount: normalizeNumber(rawPayload?.kt_info?.answer_count)
  },
  profile: {
    summaryText: normalizeText(rawPayload?.profile?.summary)
  }
})

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

// --- DEMO_EMBED: 答辩演示伪进度 ---
const aiProgress = useAIProgress({
  stages: [
    { at: 0, text: '正在分析知识图谱结构...' },
    { at: 15, text: '学习画像匹配中...' },
    { at: 35, text: '知识追踪模型推理中...' },
    { at: 55, text: '规划最优学习路径...' },
    { at: 75, text: '渲染学习节点...' },
    { at: 90, text: '即将完成...' }
  ]
})
// --- /DEMO_EMBED ---

// 加载状态
const loading = ref(true)
const loadError = ref('')
const needAssessment = ref(false)
const assessmentHint = ref('请先完成初始评测')
const refreshingPath = ref(false)
const generating = ref(false)
const refreshingMessage = ref('正在为您刷新个性化学习路径...')

// 路径节点数据
const pathNodes = ref([])
const selectedNode = ref(null)

// 横向滚动
const trackWrapperRef = ref(null)
const trackRef = ref(null)

// 统计数据
const totalNodes = computed(() => pathNodes.value.length)
const completedNodes = computed(() => pathNodes.value.filter((pathNode) => pathNode.learningStatus === 'completed').length)
const progressPercent = computed(() => {
  if (totalNodes.value === 0) return 0
  return Math.round((completedNodes.value / totalNodes.value) * 100)
})

// --- DEMO_EMBED: 伪进度条运行时也显示动画 ---
const aiProgressStageText = computed(() => normalizeText(aiProgress.stageText.value) || '正在准备学习路径...')
const aiProgressPercentage = computed(() => normalizeNumber(aiProgress.progress.value))
const isAiProgressRunning = computed(() => Boolean(aiProgress.isRunning.value))
const isRefreshingRoute = computed(() => normalizeText(route.query['refreshing']) === '1')
const showRefreshingAnimation = computed(() => generating.value || refreshingPath.value || isAiProgressRunning.value)
// --- /DEMO_EMBED ---
const refreshingDescription = computed(() => refreshingMessage.value)

/**
 * 加载学习路径数据
 */
const loadLearningPath = async () => {
  // 缺少课程ID时不发起请求，避免白屏
  if (!courseStore.courseId) {
    pathNodes.value = []
    selectedNode.value = null
    loading.value = false
    return
  }

  loading.value = true
  loadError.value = ''
  selectedNode.value = null
  try {
    const learningPathPayload = normalizeLearningPathPayload(
      await getLearningPath(courseStore.courseId)
    )

    if (learningPathPayload.needAssessment) {
      needAssessment.value = true
      assessmentHint.value = learningPathPayload.assessmentHint
      generating.value = false
      aiProgress.complete()
      pathNodes.value = []
      return
    }

    needAssessment.value = false

    if (learningPathPayload.generating) {
      generating.value = true
      aiProgress.start() // DEMO_EMBED: 生成中启动伪进度
      pathNodes.value = []
      // DEMO_EMBED: 自动轮询，生成完成后自动刷新，无需手动点击
      window.setTimeout(() => {
        if (generating.value) {
          void loadLearningPath()
        }
      }, 2000)
      return
    }

    generating.value = false
    aiProgress.complete() // DEMO_EMBED: 生成完成，伪进度跳到100%
    pathNodes.value = learningPathPayload.nodes

    // 自动选中当前节点或第一个节点
    await nextTick()
    const currentNode = pathNodes.value.find((pathNode) => pathNode.learningStatus === 'current')
    if (currentNode) {
      selectNode(currentNode)
    } else if (pathNodes.value.length) {
      selectNode(pathNodes.value[0])
    }
  } catch (error) {
    console.error('获取学习路径失败:', error)
    loadError.value = '加载学习路径失败，请点击重试'
  } finally {
    loading.value = false
    if (isRefreshingRoute.value) {
      refreshingPath.value = false
      await router.replace({ path: '/student/learning-path' })
    }
  }
}

/**
 * 选中节点
 */
const selectNode = (node) => {
  selectedNode.value = node
  // 将选中的站点滚动到视口中央
  nextTick(() => {
    const trackWrapperElement = trackWrapperRef.value
    const trackElement = trackRef.value
    if (!trackWrapperElement || !trackElement) return
    const nodeIndex = pathNodes.value.findIndex((pathNode) => pathNode.nodeId === node.nodeId)
    const stationElements = trackElement.querySelectorAll('.subway-station')
    if (stationElements[nodeIndex]) {
      const stationElement = stationElements[nodeIndex]
      const wrapperRect = trackWrapperElement.getBoundingClientRect()
      const stationRect = stationElement.getBoundingClientRect()
      const scrollLeft = trackWrapperElement.scrollLeft + stationRect.left - wrapperRect.left - wrapperRect.width / 2 + stationRect.width / 2
      trackWrapperElement.scrollTo({ left: Math.max(0, scrollLeft), behavior: 'smooth' })
    }
  })
}

const resolveLiveNode = (node) => {
  if (!node?.nodeId) return null
  return pathNodes.value.find((pathNode) => pathNode.nodeId === node.nodeId) || null
}

/**
 * 获取节点标签类型
 */
const getNodeTagType = (status) => {
  const types = {
    completed: 'success',
    current: 'primary',
    skipped: 'warning',
    pending: 'info'
  }
  return types[status] || 'info'
}

/**
 * 获取节点状态文本
 */
const getNodeStatusText = (status) => {
  const texts = {
    completed: '已完成',
    current: '学习中',
    skipped: '已跳过',
    pending: '待解锁'
  }
  return texts[status] || '待解锁'
}

/**
 * 开始学习
 */
const startLearning = async (node) => {
  try {
    const liveNode = resolveLiveNode(node)
    if (!liveNode) {
      await loadLearningPath()
      ElMessage.warning('当前节点已刷新，请重新选择后再操作')
      return
    }
    // 调用开始学习API
    await startLearningNode(liveNode.nodeId, courseStore.courseId)
    // 跳转到任务学习页面
    await router.push({
      path: `/student/task/${liveNode.nodeId}`,
      query: { pointId: liveNode.pointId, nodeType: liveNode.nodeTypeText || 'study' }
    })
  } catch (error) {
    console.error('开始学习失败:', error)
    ElMessage.error('开始学习失败，请稍后重试')
  }
}

/**
 * 标记节点完成
 */
const handleCompleteNode = async (node) => {
  try {
    await ElMessageBox.confirm(
      '确定要标记此节点为已完成吗？',
      '完成学习',
      { confirmButtonText: '确认完成', cancelButtonText: '取消', type: 'success' }
    )
    const liveNode = resolveLiveNode(node)
    if (!liveNode) {
      await loadLearningPath()
      ElMessage.warning('当前节点已刷新，请重新选择后再操作')
      return
    }
    const wasLastVisibleNode = totalNodes.value > 0 && completedNodes.value + 1 >= totalNodes.value
    if (wasLastVisibleNode) {
      refreshingMessage.value = '当前路径已学习完成，系统正在为你规划下一阶段内容，请稍候。'
      refreshingPath.value = true
      aiProgress.start() // DEMO_EMBED: 最后节点完成时启动伪进度
    }
    await completePathNode(liveNode.nodeId, courseStore.courseId)
    ElMessage.success('恭喜完成学习！')
    await loadLearningPath()
  } catch (error) {
    if (error !== 'cancel') console.error('标记完成失败:', error)
  } finally {
    aiProgress.complete() // DEMO_EMBED: 完成伪进度
    refreshingPath.value = false
    refreshingMessage.value = '正在为您刷新个性化学习路径...'
  }
}

/**
 * 复习节点
 */
const reviewNode = (node) => {
  const liveNode = resolveLiveNode(node)
  if (!liveNode) {
    ElMessage.warning('当前节点已刷新，请重新选择')
    return
  }
  void router.push({
    path: `/student/task/${liveNode.nodeId}`,
    query: { pointId: liveNode.pointId, review: 'true', nodeType: liveNode.nodeTypeText || 'study' }
  })
}

/**
 * 查看测试报告
 */
const viewTestReport = (node) => {
  const liveNode = resolveLiveNode(node)
  if (!liveNode) {
    ElMessage.warning('当前节点已刷新，请重新选择')
    return
  }
  void router.push({
    path: `/student/task/${liveNode.nodeId}`,
    query: { pointId: liveNode.pointId, nodeType: 'test', viewReport: 'true' }
  })
}

/**
 * 跳过节点
 */
const handleSkipNode = async (node) => {
  try {
    await ElMessageBox.confirm(
      '确定要跳过此学习节点吗？跳过后可以稍后返回学习。',
      '提示',
      {
        confirmButtonText: '确定跳过',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    const liveNode = resolveLiveNode(node)
    if (!liveNode) {
      await loadLearningPath()
      ElMessage.warning('当前节点已刷新，请重新选择后再操作')
      return
    }

    // 注意：响应拦截器已自动提取data字段
    await skipPathNode(liveNode.nodeId, '', courseStore.courseId)
    ElMessage.success('已跳过该节点')
    await loadLearningPath()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('跳过节点失败:', error)
    }
  }
}

const goToAssessment = () => {
  void router.push('/student/assessment')
}

const refreshPath = async () => {
  if (!courseStore.courseId) return
  refreshingMessage.value = '系统正在根据你最新的掌握度与学习进度重规划路径，请稍候。'
  refreshingPath.value = true
  aiProgress.start() // DEMO_EMBED: 刷新路径时启动伪进度
  try {
    const refreshSummary = normalizeLearningPathRefreshSummary(
      await refreshLearningPathWithAI(courseStore.courseId)
    )

    const summaryParts = [`保留节点 ${refreshSummary.preservedCount} 个，新规划节点 ${refreshSummary.newCount} 个。`]
    if (refreshSummary.changeSummary.preservedContext > 0) {
      summaryParts.push(`已保留当前节点上下文，避免学习进度被重置。`)
    }
    if (refreshSummary.changeSummary.removedCount > 0) {
      summaryParts.push(`替换未来节点 ${refreshSummary.changeSummary.removedCount} 个。`)
    }
    if (refreshSummary.ktInfo.answerCount > 0) {
      summaryParts.push(`基于 ${refreshSummary.ktInfo.answerCount} 条答题记录的知识追踪分析。`)
    }
    if (refreshSummary.profile.summaryText) {
      summaryParts.push(`画像：${refreshSummary.profile.summaryText.slice(0, 80)}`)
    }

    ElMessage.success({
      message: `学习路径已刷新：${summaryParts.join(' ')}`,
      duration: 5000
    })

  } catch (error) {
    console.error('刷新学习路径失败:', error)
    ElMessage.error('刷新失败，请稍后重试')
  } finally {
    // 无论成功失败都重新加载路径数据（后端可能已删除旧节点）
    aiProgress.complete() // DEMO_EMBED: 完成伪进度
    await loadLearningPath()
    refreshingPath.value = false
    refreshingMessage.value = '正在为您刷新个性化学习路径...'
  }
}

onMounted(() => {
  if (isRefreshingRoute.value) {
    refreshingMessage.value = '当前路径已刷新，正在同步最新节点状态，请稍候。'
    refreshingPath.value = true
  }
  void loadLearningPath()
})

// 课程切换时重新加载
watch(() => courseStore.courseId, () => {
  void loadLearningPath()
})
</script>

<style scoped>
.learning-path-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.assessment-alert {
  margin-bottom: 4px;
}

/* === 头部卡片 === */
.path-header {
  background: var(--brand-gradient);
  border: none;
  color: var(--hero-text);
  box-shadow: 0 20px 40px rgba(66, 92, 77, 0.14) !important;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.header-title-row h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.88) !important;
  border-color: rgba(109, 146, 125, 0.18) !important;
  color: var(--primary-dark) !important;
}

.refresh-btn:hover {
  background: #fff !important;
}

.header-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

/* === 路径内容区 === */
.loading-container {
  padding: 40px;
}

.generating-container {
  padding: 60px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.generating-container h3 {
  margin: 0;
  color: #303133;
}

/* === 横向地铁线路图 === */
.subway-track-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 28px 18px 20px;
  scrollbar-width: thin;
  scrollbar-color: #c0c4cc transparent;
  background: var(--bg-soft);
  border-radius: 18px;
}

.subway-track-wrapper::-webkit-scrollbar {
  height: 6px;
}

.subway-track-wrapper::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.subway-track {
  display: flex;
  align-items: flex-start;
  min-width: max-content;
  position: relative;
}

/* === 站点 === */
.subway-station {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  cursor: pointer;
  min-width: 100px;
  max-width: 120px;
  padding: 0 8px;
  transition: transform 0.2s;
}

.subway-station:hover {
  transform: translateY(-2px);
}

.subway-station.active .station-dot {
  box-shadow: 0 0 0 5px rgba(18, 154, 116, 0.18);
  transform: scale(1.15);
}

.subway-station.active {
  z-index: 2;
}

/* === 连接线 === */
.station-line {
  position: absolute;
  top: 18px;
  left: calc(-50% + 18px);
  width: calc(100% - 18px);
  height: 3px;
  background: rgba(108, 133, 125, 0.28);
  z-index: 0;
  pointer-events: none;
  border-radius: 999px;
}

.station-line.done {
  background: var(--primary-color);
}

/* === 站点圆点 === */
.station-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  position: relative;
  z-index: 3;
  transition: all 0.3s;
  border: 3px solid #fff;
  box-shadow: 0 10px 20px rgba(9, 58, 45, 0.12);
}

.station-dot.completed {
  background: var(--success-color);
}

.station-dot.current {
  background: var(--primary-color);
  animation: pulse-dot 2s infinite;
}

.station-dot.skipped {
  background: var(--warning-color);
}

.station-dot.pending {
  background: #b7c7bf;
}

/* 测试节点用不同边框 */
.station-dot.test {
  border-color: #fdf6ec;
}

.dot-index {
  font-size: 12px;
}

@keyframes pulse-dot {

  0%,
  100% {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  50% {
    box-shadow: 0 0 0 6px rgba(64, 158, 255, 0.2);
  }
}

/* === 站点标签 === */
.station-label {
  margin-top: 10px;
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
  color: var(--text-regular);
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-all;
  position: relative;
  z-index: 3;
}

.station-label.completed {
  color: var(--success-color);
  font-weight: 500;
}

.station-label.current {
  color: var(--primary-color);
  font-weight: 600;
}

.station-label.skipped {
  color: var(--warning-color);
}

/* === 详情面板 === */
.node-detail-panel {
  margin-top: 20px;
  padding: 24px;
  background: var(--bg-soft);
  border-radius: 18px;
  border: 1px solid rgba(18, 154, 116, 0.12);
}

.detail-header {
  margin-bottom: 16px;
}

.detail-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-title-row h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  flex: 1;
  min-width: 0;
}

.detail-meta {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
  display: flex;
  gap: 20px;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.detail-body {
  margin-bottom: 20px;
}

.detail-desc {
  margin: 0 0 12px;
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

.detail-suggestion {
  padding: 10px 14px;
  font-size: 13px;
  color: var(--primary-color);
  background: rgba(20, 184, 166, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.6;
}

.detail-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* === 未选中提示 === */
.select-hint {
  margin-top: 32px;
  text-align: center;
  color: #c0c4cc;
  padding: 24px 0;
}

.select-hint p {
  margin: 8px 0 0;
  font-size: 14px;
}

/* === 过渡动画 === */
.detail-fade-enter-active,
.detail-fade-leave-active {
  transition: all 0.3s ease;
}

.detail-fade-enter-from,
.detail-fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* === 响应式 === */
@media (max-width: 768px) {
  .header-top {
    flex-direction: column;
    gap: 16px;
  }

  .header-stats {
    justify-content: flex-start;
  }

  .stat-value {
    font-size: 24px;
  }

  .subway-station {
    min-width: 80px;
  }

  .node-detail-panel {
    padding: 16px;
  }
}
</style>

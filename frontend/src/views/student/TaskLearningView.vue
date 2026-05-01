<template>
  <div class="task-learning-view fade-in-up" v-loading="loading">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span>{{ currentTask.titleText || '任务学习' }}</span>
      </template>
      <template #extra>
        <el-button :icon="ChatDotRound" type="primary" plain @click="chatDrawerVisible = true">
          AI助手
        </el-button>
      </template>
    </el-page-header>

    <!-- AI 知识点介绍 -->
    <el-card v-if="hasNodeIntro && !isTestNode" class="intro-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon>
              <MagicStick />
            </el-icon> 知识点介绍</span>
          <el-tag :type="difficultyTagType" size="small">{{ difficultyLabel }}</el-tag>
        </div>
      </template>
      <div class="intro-text markdown-body" v-html="renderMarkdown(nodeIntro.introductionText)"></div>
      <div v-if="nodeIntro.keyConceptList.length" class="key-concepts">
        <el-tag v-for="concept in nodeIntro.keyConceptList" :key="concept" type="info" effect="plain"
          class="concept-tag">{{
            concept }}</el-tag>
      </div>
      <p v-if="nodeIntro.learningTipsText" class="learning-tip">
        <el-icon>
          <InfoFilled />
        </el-icon> {{ nodeIntro.learningTipsText }}
      </p>
    </el-card>
    <el-skeleton v-else-if="introLoading && !isTestNode" :rows="2" animated style="margin-bottom: 20px;" />

    <el-row :gutter="20" class="content-row">
      <!-- 学习资源列表 -->
      <el-col v-if="!isTestNode" :xs="24" :lg="16">
        <el-card class="resources-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>学习资源</span>
              <span v-if="resourceRecords.length" class="resource-count">{{ completedResourceCount }} / {{
                resourceRecords.length }}
                已完成</span>
            </div>
          </template>

          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <el-empty v-else-if="!resourceRecords.length" description="暂无学习资源">
            <template #description>
              <div class="empty-ai-searching">
                <el-icon :class="{ 'is-loading': aiResourcesLoading }">
                  <MagicStick />
                </el-icon>
                <span>{{ aiResourcesLoading ? 'AI 正在联网查找适合你的学习资源，请稍候…' : 'AI 暂未找到合适资源，稍后会继续补充推荐。' }}</span>
              </div>
            </template>
          </el-empty>

          <div v-else class="resources-list">
            <div v-for="resourceRecord in resourceRecords" :key="resourceRecord.resourceId" class="resource-item"
              :class="{ completed: resourceRecord.isCompleted, active: currentResourceRecord.resourceId === resourceRecord.resourceId }"
              @click="selectResource(resourceRecord)">
              <div class="resource-icon">
                <el-icon v-if="resourceRecord.isCompleted">
                  <CircleCheck />
                </el-icon>
                <el-icon v-else-if="resourceRecord.resourceType === 'video'">
                  <VideoPlay />
                </el-icon>
                <el-icon v-else-if="resourceRecord.resourceType === 'document'">
                  <Document />
                </el-icon>
                <el-icon v-else>
                  <Reading />
                </el-icon>
              </div>
              <div class="resource-info">
                <h4>{{ resourceRecord.titleText }}</h4>
                <p>{{ resourceRecord.descriptionText || resourceRecord.durationText }}</p>
              </div>
              <el-tag v-if="!resourceRecord.isRequired" size="small" type="warning" effect="plain">选修</el-tag>
              <el-tag v-if="resourceRecord.isServerHosted" size="small" type="success" effect="plain">本地</el-tag>
              <el-tag v-else size="small" type="info" effect="plain">外部</el-tag>
              <el-tag v-if="resourceRecord.sourceText" size="small" type="info" effect="plain">
                {{ resourceRecord.sourceText }}
              </el-tag>
              <el-icon class="resource-arrow">
                <ArrowRight />
              </el-icon>
            </div>
            <!-- AI资源加载中提示 -->
            <div v-if="aiResourcesLoading" class="ai-loading-hint">
              <el-icon class="is-loading">
                <MagicStick />
              </el-icon>
              <span>AI 正在联网查找并筛选适合你的学习资源...</span>
            </div>
          </div>
        </el-card>

        <!-- 节点目标 -->
        <el-card v-if="currentTask.descriptionText && !isTestNode" class="goal-card" shadow="hover"
          style="margin-top: 20px;">
          <template #header><span>学习目标</span></template>
          <div class="goal-content">
            <p style="margin: 0; color: #606266; line-height: 1.8;">{{ currentTask.descriptionText }}</p>
            <div v-if="masteryBeforeRate !== null || masteryAfterRate !== null" class="goal-mastery-card">
              <div class="goal-mastery-title">知识掌握度</div>
              <div class="goal-mastery-grid">
                <div class="goal-mastery-item">
                  <span>学习前</span>
                  <strong>{{ Math.round((masteryBeforeRate || 0) * 100) }}%</strong>
                </div>
                <div v-if="masteryAfterRate !== null" class="goal-mastery-item success">
                  <span>学习后</span>
                  <strong>{{ Math.round((masteryAfterRate || 0) * 100) }}%</strong>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧面板 / 测试节点全宽面板 -->
      <el-col :xs="24" :lg="isTestNode ? 24 : 8">
        <!-- 学习进度 -->
        <el-card v-if="!isTestNode" class="progress-card" shadow="hover">
          <template #header><span>学习进度</span></template>
          <div class="progress-content">
            <el-progress type="circle" :percentage="progressPercent" :width="150" :stroke-width="12" />
            <div class="progress-stats">
              <p>已完成 <strong>{{ completedResourceCount }}</strong> / {{ resourceRecords.length }} 个资源</p>
            </div>
          </div>
          <el-divider />
          <div class="action-buttons">
            <el-button type="success" size="large" @click="completeTask">
              完成学习
            </el-button>
          </div>
        </el-card>

        <!-- 节点练习测验 -->
        <el-card v-if="hasNodeExam && !isTestNode" class="quiz-card" shadow="hover" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>节点作业</span>
              <el-tag v-if="hasNodeQuizResult" :type="nodeQuizResult.isPassed ? 'success' : 'danger'" size="small">
                {{ nodeQuizResult.isPassed ? '已通过' : '未通过' }}
              </el-tag>
            </div>
          </template>
          <div v-if="hasNodeQuizResult" class="quiz-result">
            <p>得分：<strong :style="{ color: nodeQuizResult.isPassed ? '#67c23a' : '#f56c6c' }">{{
              nodeQuizResult.scoreValue
            }}分</strong>
            </p>
            <p v-if="!nodeQuizResult.isPassed" style="color: #909399; font-size: 13px;">未达到及格线，建议复习后重新作答</p>
            <el-button v-if="!nodeQuizResult.isPassed" type="warning" size="small"
              @click="resetNodeQuizResult">重新作答</el-button>
          </div>
          <div v-else>
            <p style="color: #606266; margin: 0 0 12px;">{{ currentNodeExam.titleText }} · 及格线 {{
              currentNodeExam.passScore
            }}分</p>
            <el-button type="primary" size="small" @click="startQuiz" :disabled="!allCompleted">
              {{ allCompleted ? '开始作业' : '完成所有资源后可作答' }}
            </el-button>
          </div>
        </el-card>

        <!-- 嵌入式阶段测试 -->
        <el-card v-if="isTestNode" ref="stageTestCardRef" class="stage-test-card" shadow="hover"
          style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>{{ stageTestTitle }}</span>
              <el-tag v-if="hasStageTestResult" :type="stageTestResult.isPassed ? 'success' : 'danger'" size="small">
                {{ stageTestResult.isPassed ? '已通过' : '未通过' }}
              </el-tag>
              <el-tag v-else type="warning" size="small">{{ stageTestQuestions.length }} 题</el-tag>
            </div>
          </template>

          <div v-if="stageTestLoading" style="padding: 20px; text-align: center;">
            <el-skeleton :rows="5" animated />
          </div>

          <!-- 测试结果展示 -->
          <div v-else-if="hasStageTestResult" class="stage-test-result">
            <div class="stage-result-summary">
              <div class="result-score" :style="{ color: stageTestResult.isPassed ? '#22a06b' : '#d45050' }">
                {{ stageTestResult.scoreValue }} <span class="result-score-unit">/ {{ stageTestResult.totalScoreValue ||
                  100
                }}</span>
              </div>
              <div class="stage-result-metrics">
                <div class="metric-card">
                  <span class="metric-label">答对题数</span>
                  <strong>{{ stageTestResult.correctCount }} / {{ stageTestResult.totalCount }}</strong>
                </div>
                <div class="metric-card">
                  <span class="metric-label">通过线</span>
                  <strong>{{ stageTestPassScore }} 分</strong>
                </div>
              </div>
            </div>
            <p v-if="!stageTestResult.isPassed" style="color: #909399; font-size: 13px;">
              未达到及格线 {{ stageTestPassScore }} 分，建议复习后重试
            </p>
            <div v-if="hasStageFeedbackReport" class="stage-report-card">
              <h4>AI 分析报告</h4>
              <p v-if="stageTestResult.feedbackReport.summaryText" class="stage-report-summary">
                {{ stageTestResult.feedbackReport.summaryText }}
              </p>
              <p v-if="stageTestResult.feedbackReport.analysisText" class="stage-report-analysis">
                {{ stageTestResult.feedbackReport.analysisText }}
              </p>
              <div v-if="stageTestResult.feedbackReport.knowledgeGapList.length" class="stage-report-section">
                <h5>薄弱知识点</h5>
                <div class="stage-gap-tags">
                  <el-tag v-for="(item, idx) in stageTestResult.feedbackReport.knowledgeGapList" :key="`gap-${idx}`"
                    type="warning" effect="plain">
                    {{ item }}
                  </el-tag>
                </div>
              </div>
              <div v-if="stageTestResult.feedbackReport.recommendationList.length" class="stage-report-section">
                <h5>改进建议</h5>
                <ul>
                  <li v-for="(item, idx) in stageTestResult.feedbackReport.recommendationList" :key="`rec-${idx}`">{{
                    item
                  }}</li>
                </ul>
              </div>
              <div v-if="stageTestResult.feedbackReport.nextTaskList.length" class="stage-report-section">
                <h5>下一步任务</h5>
                <ul>
                  <li v-for="(item, idx) in stageTestResult.feedbackReport.nextTaskList" :key="`task-${idx}`">{{ item }}
                  </li>
                </ul>
              </div>
              <div v-if="stageTestResult.masteryChangeList.length" class="stage-report-section">
                <h5>知识掌握度变化</h5>
                <div class="stage-mastery-list">
                  <div v-for="item in stageTestResult.masteryChangeList" :key="item.pointId || item.pointName"
                    class="stage-mastery-item">
                    <span>{{ item.pointName }}</span>
                    <strong>{{ item.masteryBeforePercent }}% -> {{ item.masteryAfterPercent }}%</strong>
                  </div>
                </div>
              </div>
              <p v-if="displayStageConclusion" class="stage-report-encouragement">
                {{ displayStageConclusion }}
              </p>
            </div>
            <div v-if="stageTestResult.mistakeList.length" class="stage-mistake-list">
              <h4>错题回顾</h4>
              <div v-for="mistake in stageTestResult.mistakeList" :key="mistake.questionId" class="stage-mistake-item">
                <p class="stage-mistake-title">{{ mistake.questionText || `题目 ${mistake.questionId}` }}</p>
                <p><span class="mistake-label">你的答案：</span>{{ mistake.studentAnswerDisplayText ||
                  formatStageAnswer(mistake.studentAnswer) }}</p>
                <p><span class="mistake-label">正确答案：</span>{{ mistake.correctAnswerDisplayText ||
                  formatStageAnswer(mistake.correctAnswer) }}</p>
                <p v-if="mistake.analysisText"><span class="mistake-label">解析：</span>{{ mistake.analysisText }}</p>
              </div>
            </div>
            <el-button v-if="!stageTestResult.isPassed" type="warning" @click="retryStageTest"
              style="margin-top: 12px;">
              重新作答
            </el-button>
            <el-button v-else type="success" @click="goBack" style="margin-top: 12px;">
              返回学习路径
            </el-button>
          </div>

          <!-- 做题界面 -->
          <div v-else-if="stageTestQuestions.length" class="stage-test-questions">
            <div class="stage-test-intro">
              <div class="stage-test-intro-text">
                <h4>{{ stageTestTitle }}</h4>
                <p>按作业方式完成本轮诊断，题目统一计分，提交后将生成 AI 分析报告。</p>
              </div>
              <div class="stage-test-intro-meta">
                <el-tag type="warning" effect="plain">共 {{ stageTestQuestions.length }} 题</el-tag>
                <el-tag type="success" effect="plain">总分 100</el-tag>
              </div>
            </div>
            <div v-for="(question, idx) in stageTestQuestions" :key="question.questionId" class="question-item">
              <div class="question-head">
                <span class="question-order">第 {{ idx + 1 }} 题</span>
                <span class="question-score">{{ question.scoreValue }} 分</span>
              </div>
              <p class="question-title">{{ question.contentText }}</p>
              <el-checkbox-group v-if="question.questionType === 'multiple_choice'"
                v-model="stageTestAnswers[question.questionId]" class="question-options">
                <el-checkbox v-for="option in question.optionList" :key="option.optionKey" :value="option.answerValue"
                  class="question-option">
                  {{ option.optionKey }}. {{ option.optionLabel }}
                </el-checkbox>
              </el-checkbox-group>
              <el-radio-group v-else v-model="stageTestAnswers[question.questionId]" class="question-options">
                <el-radio v-for="option in question.optionList" :key="option.optionKey" :value="option.answerValue"
                  class="question-option">
                  {{ option.optionKey }}. {{ option.optionLabel }}
                </el-radio>
              </el-radio-group>
            </div>
            <el-button type="primary" @click="submitStageTestAnswers" :loading="stageTestLoading"
              style="width: 100%; margin-top: 16px;">
              提交答案
            </el-button>
          </div>

          <el-empty v-else description="暂无测试题目">
            <template #description>
              <p>当前暂无匹配的测试题目</p>
              <p style="font-size: 12px; color: #909399;">请联系教师补充题库或稍后重试</p>
            </template>
            <el-button type="primary" size="small" @click="loadStageTest">重新加载</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 聊天抽屉 -->
    <el-drawer v-model="chatDrawerVisible" title="AI 学习助手" direction="rtl" size="400px">
      <template #header>
        <div class="assistant-drawer-header">
          <span>AI 学习助手</span>
          <el-button link type="primary" @click="openFullAssistant">打开完整 AI助手</el-button>
        </div>
      </template>
      <div class="chat-container">
        <div ref="chatMessagesRef" class="chat-messages">
          <div class="chat-welcome">
            <el-icon>
              <MagicStick />
            </el-icon>
            <p>我是你的AI学习助手，有关于 <strong>{{ currentTask.titleText || '本节' }}</strong> 的问题都可以问我。</p>
          </div>
          <div v-for="(msg, idx) in chatMessages" :key="idx" :class="['chat-msg', msg.role]">
            <div class="msg-bubble" v-html="formatMessage(msg.content)"></div>
          </div>
          <div v-if="chatLoading" class="chat-msg assistant">
            <div class="msg-bubble typing"><span></span><span></span><span></span></div>
          </div>
        </div>
        <div class="chat-input">
          <el-input v-model="chatInput" placeholder="输入你的问题..." @keyup.enter="sendChat" :disabled="chatLoading">
            <template #append>
              <el-button :icon="Promotion" @click="sendChat" :loading="chatLoading" />
            </template>
          </el-input>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
/**
 * 任务学习视图
 * 展示学习节点详情、学习资源、阶段测试以及 AI 学习助手。
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCourseStore } from '@/stores/course'
import {
  getPathNodeDetail,
  getAIResources,
  completeResource,
  completePathNode,
  getNodeExams,
  getStageTest,
  submitStageTest
} from '@/api/student/learning'
import { aiChat, getAINodeIntro } from '@/api/student/ai'
import { ElMessage, ElMessageBox } from 'element-plus'
import { toBackendAbsoluteUrl } from '@/api/backend'
import {
  CircleCheck, VideoPlay, Document, Reading, ArrowRight,
  ChatDotRound, MagicStick, InfoFilled, Promotion
} from '@element-plus/icons-vue'
import { renderMarkdown } from '@/utils/markdown'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

/**
 * 收敛文本值，避免模板直接消费不稳定 payload。
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
 * 收敛标识符文本。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  return normalizeText(rawValue).trim()
}

/**
 * 收敛数值。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 收敛可空数值。
 * @param {unknown} rawValue
 * @returns {number | null}
 */
const normalizeNullableNumber = (rawValue) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : null
}

/**
 * 收敛布尔值，兼容字符串和数字输入。
 * @param {unknown} rawValue
 * @param {boolean} fallbackValue
 * @returns {boolean}
 */
const normalizeBoolean = (rawValue, fallbackValue = false) => {
  if (typeof rawValue === 'boolean') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return rawValue !== 0
  }
  if (typeof rawValue === 'string') {
    const loweredValue = rawValue.trim().toLowerCase()
    if (['true', '1', 'yes'].includes(loweredValue)) {
      return true
    }
    if (['false', '0', 'no'].includes(loweredValue)) {
      return false
    }
  }
  return fallbackValue
}

/**
 * 将任意 payload 收敛为普通对象。
 * @param {unknown} rawValue
 * @returns {Record<string, unknown>}
 */
const normalizeObjectFromPayload = (rawValue) => {
  return rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)
    ? rawValue
    : {}
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
 * 将任意列表收敛为干净的字符串数组。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const normalizeStringList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((item) => normalizeText(item).trim())
    .filter(Boolean)
}

/**
 * 将 0-1 或 0-100 的值统一换算为百分比。
 * @param {unknown} rawValue
 * @returns {number}
 */
const normalizePercentValue = (rawValue) => {
  const numericValue = normalizeNumber(rawValue)
  return Math.round((numericValue <= 1 ? numericValue * 100 : numericValue) || 0)
}

/**
 * 格式化学习时长。
 * @param {unknown} rawSeconds
 * @returns {string}
 */
const formatDuration = (rawSeconds) => {
  const totalSeconds = normalizeNumber(rawSeconds)
  if (totalSeconds <= 0) {
    return '未知时长'
  }
  const minutes = Math.round(totalSeconds / 60)
  if (minutes < 1) {
    return `${totalSeconds}秒`
  }
  if (minutes < 60) {
    return `${minutes}分钟`
  }
  const hours = Math.floor(minutes / 60)
  const remainMinutes = minutes % 60
  return remainMinutes > 0 ? `${hours}小时${remainMinutes}分钟` : `${hours}小时`
}

/**
 * 统一阶段测试答案空值判断。
 * @param {unknown} answerValue
 * @returns {boolean}
 */
const isEmptyStageAnswer = (answerValue) => {
  if (Array.isArray(answerValue)) {
    return answerValue.length === 0
  }
  return normalizeText(answerValue).trim().length === 0
}

/**
 * 从模板 ref 中解析真实 DOM 元素。
 * @param {{ value: unknown }} templateRef
 * @returns {HTMLElement | null}
 */
const resolveTemplateElement = (templateRef) => {
  const currentValue = templateRef.value
  if (!currentValue) {
    return null
  }
  if (currentValue instanceof HTMLElement) {
    return currentValue
  }
  if (typeof currentValue === 'object' && currentValue.$el instanceof HTMLElement) {
    return currentValue.$el
  }
  return null
}

const currentNodeId = computed(() => normalizeNumber(route.params.nodeId, 0))
const currentPointId = computed(() => normalizeNullableNumber(route.query.pointId))
const currentNodeType = computed(() => normalizeText(route.query.nodeType) || 'study')
const shouldViewStageReport = computed(() => normalizeText(route.query.viewReport) === 'true')
const isTestNode = computed(() => currentNodeType.value === 'test')

const buildDefaultTaskModel = () => ({
  taskId: '',
  titleText: '',
  descriptionText: '',
  pointNameText: '',
  knowledgePointId: null
})

const buildDefaultResourceModel = () => ({
  resourceId: '',
  titleText: '',
  resourceType: 'document',
  descriptionText: '',
  durationText: '未知时长',
  isCompleted: false,
  isRequired: true,
  resourceUrl: '',
  isServerHosted: false
})

const buildDefaultNodeIntroModel = () => ({
  introductionText: '',
  keyConceptList: [],
  learningTipsText: '',
  difficultyLevel: ''
})

const buildDefaultNodeExamModel = () => ({
  hasExam: false,
  examId: '',
  titleText: '',
  passScore: 60
})

const buildDefaultNodeQuizResultModel = () => ({
  hasResult: false,
  isPassed: false,
  scoreValue: 0
})

const buildDefaultStageQuestionOptionModel = () => ({
  optionKey: '',
  optionLabel: '',
  answerValue: ''
})

const buildDefaultStageQuestionModel = () => ({
  questionId: '',
  contentText: '',
  questionType: 'single_choice',
  difficultyLevel: '',
  scoreValue: 0,
  optionList: []
})

const buildDefaultStageFeedbackReportModel = () => ({
  summaryText: '',
  analysisText: '',
  knowledgeGapList: [],
  recommendationList: [],
  nextTaskList: [],
  conclusionText: ''
})

const buildDefaultStageMasteryChangeModel = () => ({
  pointId: '',
  pointName: '',
  masteryBeforePercent: 0,
  masteryAfterPercent: 0
})

const buildDefaultStageMistakeModel = () => ({
  questionId: '',
  questionText: '',
  studentAnswer: null,
  correctAnswer: null,
  studentAnswerDisplayText: '',
  correctAnswerDisplayText: '',
  analysisText: ''
})

const buildDefaultStageTestResultModel = () => ({
  hasResult: false,
  scoreValue: 0,
  totalScoreValue: 100,
  isPassed: false,
  passThresholdValue: 60,
  correctCount: 0,
  totalCount: 0,
  accuracyPercent: 0,
  mistakeList: [],
  masteryChangeList: [],
  feedbackReport: buildDefaultStageFeedbackReportModel(),
  isPathRefreshed: false
})

/**
 * 收敛题目难度标记。
 * @param {unknown} rawDifficulty
 * @returns {string}
 */
const normalizeDifficultyLevel = (rawDifficulty) => {
  const difficultyText = normalizeText(rawDifficulty).trim()
  return ['easy', 'medium', 'hard'].includes(difficultyText) ? difficultyText : ''
}

/**
 * 收敛节点详情数据。
 * @param {unknown} rawPayload
 * @returns {{taskId: string, titleText: string, descriptionText: string, pointNameText: string, knowledgePointId: number | null}}
 */
const normalizeTaskPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    taskId: normalizeIdentifier(payload.node_id ?? payload.id ?? currentNodeId.value),
    titleText: normalizeText(payload.node_title ?? payload.title) || '学习任务',
    descriptionText: normalizeText(payload.goal ?? payload.description),
    pointNameText: normalizeText(payload.knowledge_point_name ?? payload.node_title ?? payload.title),
    knowledgePointId: normalizeNullableNumber(payload.knowledge_point_id ?? currentPointId.value)
  }
}

/**
 * 收敛 AI 知识点介绍数据。
 * @param {unknown} rawPayload
 * @returns {{introductionText: string, keyConceptList: string[], learningTipsText: string, difficultyLevel: string}}
 */
const normalizeNodeIntroPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    introductionText: normalizeText(payload.introduction),
    keyConceptList: normalizeStringList(payload.key_concepts),
    learningTipsText: normalizeText(payload.learning_tips),
    difficultyLevel: normalizeDifficultyLevel(payload.difficulty)
  }
}

/**
 * 收敛资源类型。
 * @param {unknown} rawType
 * @returns {string}
 */
const normalizeResourceType = (rawType) => {
  const resourceType = normalizeText(rawType).trim().toLowerCase()
  return resourceType || 'document'
}

/**
 * 收敛学习资源数据。
 * @param {unknown} rawPayload
 * @returns {{resourceId: string, titleText: string, resourceType: string, descriptionText: string, durationText: string, isCompleted: boolean, isRequired: boolean, resourceUrl: string, isServerHosted: boolean, sourceText: string, providerText: string}}
 */
const normalizeResourcePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const rawResourceUrl = normalizeText(payload.url)
  const resourceUrl = toBackendAbsoluteUrl(rawResourceUrl)
  const explicitServerFlag = payload.is_internal
  const isServerHosted = explicitServerFlag !== undefined
    ? normalizeBoolean(explicitServerFlag)
    : Boolean(rawResourceUrl) && (rawResourceUrl.startsWith('/media') || rawResourceUrl.startsWith('/api'))

  return {
    resourceId: normalizeIdentifier(payload.resource_id ?? payload.id),
    titleText: normalizeText(payload.title) || '未命名资源',
    resourceType: normalizeResourceType(payload.type ?? payload.resource_type),
    descriptionText: normalizeText(payload.description) || (!isServerHosted ? '外部扩展学习资源' : ''),
    durationText: formatDuration(payload.duration),
    isCompleted: normalizeBoolean(payload.completed),
    isRequired: payload.required === undefined ? true : normalizeBoolean(payload.required, true),
    resourceUrl,
    isServerHosted,
    sourceText: normalizeText(payload.source),
    providerText: normalizeText(payload.provider)
  }
}

/**
 * 收敛节点作业信息。
 * @param {unknown} rawPayload
 * @returns {{hasExam: boolean, examId: string, titleText: string, passScore: number}}
 */
const normalizeNodeExamPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const examId = normalizeIdentifier(payload.exam_id ?? payload.id)
  return {
    hasExam: Boolean(examId),
    examId,
    titleText: normalizeText(payload.title),
    passScore: normalizeNumber(payload.pass_score, 60)
  }
}

/**
 * 收敛阶段测试选项。
 * @param {unknown} rawPayload
 * @param {number} optionIndex
 * @returns {{optionKey: string, optionLabel: string, answerValue: string}}
 */
const normalizeStageQuestionOptionPayload = (rawPayload, optionIndex) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  const fallbackKey = String.fromCharCode(65 + optionIndex)
  const optionKey = normalizeText(payload.key ?? payload.label ?? payload.value) || fallbackKey
  return {
    optionKey,
    optionLabel: normalizeText(payload.value ?? payload.text ?? payload.label ?? payload.content) || optionKey,
    answerValue: normalizeText(payload.answer_value ?? payload.value ?? optionKey)
  }
}

/**
 * 收敛阶段测试题目。
 * @param {unknown} rawPayload
 * @returns {{questionId: string, contentText: string, questionType: string, difficultyLevel: string, scoreValue: number, optionList: Array<{optionKey: string, optionLabel: string, answerValue: string}>}}
 */
const normalizeStageQuestionPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    questionId: normalizeIdentifier(payload.id),
    contentText: normalizeText(payload.content ?? payload.question_text),
    questionType: normalizeText(payload.question_type) || 'single_choice',
    difficultyLevel: normalizeDifficultyLevel(payload.difficulty),
    scoreValue: normalizeNumber(payload.score),
    optionList: normalizeListFromPayload(payload.options).map((item, optionIndex) => normalizeStageQuestionOptionPayload(item, optionIndex))
  }
}

/**
 * 收敛阶段测试反馈报告。
 * @param {unknown} rawPayload
 * @returns {{summaryText: string, analysisText: string, knowledgeGapList: string[], recommendationList: string[], nextTaskList: string[], conclusionText: string}}
 */
const normalizeStageFeedbackReportPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    summaryText: normalizeText(payload.summary),
    analysisText: normalizeText(payload.analysis),
    knowledgeGapList: normalizeStringList(payload.knowledge_gaps),
    recommendationList: normalizeStringList(payload.recommendations),
    nextTaskList: normalizeStringList(payload.next_tasks),
    conclusionText: normalizeText(payload.conclusion ?? payload.encouragement)
  }
}

/**
 * 收敛掌握度变化列表项。
 * @param {unknown} rawPayload
 * @returns {{pointId: string, pointName: string, masteryBeforePercent: number, masteryAfterPercent: number}}
 */
const normalizeStageMasteryChangePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    pointId: normalizeIdentifier(payload.knowledge_point_id ?? payload.point_id ?? payload.id),
    pointName: normalizeText(payload.knowledge_point_name ?? payload.point_name ?? payload.name) || '未知知识点',
    masteryBeforePercent: normalizePercentValue(payload.mastery_before),
    masteryAfterPercent: normalizePercentValue(payload.mastery_after)
  }
}

/**
 * 收敛错题回顾项。
 * @param {unknown} rawPayload
 * @returns {{questionId: string, questionText: string, studentAnswer: unknown, correctAnswer: unknown, studentAnswerDisplayText: string, correctAnswerDisplayText: string, analysisText: string}}
 */
const normalizeStageMistakePayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  return {
    questionId: normalizeIdentifier(payload.question_id),
    questionText: normalizeText(payload.question_text),
    studentAnswer: payload.student_answer,
    correctAnswer: payload.correct_answer,
    studentAnswerDisplayText: normalizeText(payload.student_answer_display),
    correctAnswerDisplayText: normalizeText(payload.correct_answer_display),
    analysisText: normalizeText(payload.analysis)
  }
}

/**
 * 收敛阶段测试结果。
 * @param {unknown} rawPayload
 * @returns {{hasResult: boolean, scoreValue: number, totalScoreValue: number, isPassed: boolean, passThresholdValue: number, correctCount: number, totalCount: number, accuracyPercent: number, mistakeList: Array, masteryChangeList: Array, feedbackReport: object, isPathRefreshed: boolean}}
 */
const normalizeStageTestResultPayload = (rawPayload) => {
  const payload = normalizeObjectFromPayload(rawPayload)
  if (!Object.keys(payload).length) {
    return buildDefaultStageTestResultModel()
  }

  return {
    hasResult: true,
    scoreValue: normalizeNumber(payload.score),
    totalScoreValue: normalizeNumber(payload.total_score, 100),
    isPassed: normalizeBoolean(payload.passed),
    passThresholdValue: normalizeNumber(payload.pass_threshold, 60),
    correctCount: normalizeNumber(payload.correct_count ?? payload.correct),
    totalCount: normalizeNumber(payload.total_count ?? payload.total),
    accuracyPercent: normalizeNumber(payload.accuracy),
    mistakeList: normalizeListFromPayload(payload.mistakes).map(normalizeStageMistakePayload),
    masteryChangeList: normalizeListFromPayload(payload.mastery_changes).map(normalizeStageMasteryChangePayload),
    feedbackReport: normalizeStageFeedbackReportPayload(payload.feedback_report),
    isPathRefreshed: normalizeBoolean(payload.path_refreshed)
  }
}

/**
 * 初始化阶段测试答案字典。
 * @param {Array<{questionId: string, questionType: string}>} questionList
 * @returns {Record<string, string | string[]>}
 */
const buildStageTestAnswers = (questionList) => {
  return questionList.reduce((answerMap, questionItem) => {
    answerMap[questionItem.questionId] = questionItem.questionType === 'multiple_choice' ? [] : ''
    return answerMap
  }, {})
}

/**
 * 获取能力标签的展示颜色。
 */
const getDifficultyTagType = (difficultyLevel) => {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' }
  return map[difficultyLevel] || 'info'
}

/**
 * 获取能力标签的展示文本。
 */
const getDifficultyLabel = (difficultyLevel) => {
  const map = { easy: '基础', medium: '中等', hard: '进阶' }
  return map[difficultyLevel] || '未知'
}

// 加载状态
const loading = ref(true)
const introLoading = ref(false)
const aiResourcesLoading = ref(false)

// 当前任务和资源
const currentTask = ref(buildDefaultTaskModel())
const currentResourceRecord = ref(buildDefaultResourceModel())
const resourceRecords = ref([])
const nodeIntro = ref(buildDefaultNodeIntroModel())
const masteryBeforeRate = ref(null)
const masteryAfterRate = ref(null)

// AI聊天
const chatDrawerVisible = ref(false)
const chatMessages = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessagesRef = ref(null)

// 节点作业
const currentNodeExam = ref(buildDefaultNodeExamModel())
const nodeQuizResult = ref(buildDefaultNodeQuizResultModel())

// 阶段测试（嵌入式做题）
const stageTestQuestions = ref([])
const stageTestAnswers = ref({})
const stageTestResult = ref(buildDefaultStageTestResultModel())
const stageTestLoading = ref(false)
const stageTestTitle = ref('')
const stageTestPassScore = ref(60)
const stageTestCardRef = ref(null)

const hasNodeIntro = computed(() => {
  return Boolean(
    nodeIntro.value.introductionText
    || nodeIntro.value.learningTipsText
    || nodeIntro.value.keyConceptList.length
  )
})

const hasNodeExam = computed(() => currentNodeExam.value.hasExam)
const hasNodeQuizResult = computed(() => nodeQuizResult.value.hasResult)
const hasStageTestResult = computed(() => stageTestResult.value.hasResult)
const hasStageFeedbackReport = computed(() => {
  const feedbackReport = stageTestResult.value.feedbackReport
  return Boolean(
    feedbackReport.summaryText
    || feedbackReport.analysisText
    || feedbackReport.knowledgeGapList.length
    || feedbackReport.recommendationList.length
    || feedbackReport.nextTaskList.length
    || feedbackReport.conclusionText
  )
})

// 难度标签
const difficultyTagType = computed(() => getDifficultyTagType(nodeIntro.value.difficultyLevel))
const difficultyLabel = computed(() => getDifficultyLabel(nodeIntro.value.difficultyLevel))

const completedResourceCount = computed(() => resourceRecords.value.filter((item) => item.isCompleted).length)
const requiredResources = computed(() => resourceRecords.value.filter((item) => item.isRequired))
const requiredCompletedCount = computed(() => requiredResources.value.filter((item) => item.isCompleted).length)
const progressPercent = computed(() => {
  if (resourceRecords.value.length === 0) {
    return 0
  }
  return Math.round((completedResourceCount.value / resourceRecords.value.length) * 100)
})
const allCompleted = computed(() => {
  return requiredResources.value.length > 0 && requiredCompletedCount.value >= requiredResources.value.length
})
const displayStageConclusion = computed(() => {
  const feedbackReport = stageTestResult.value.feedbackReport
  const conclusionText = feedbackReport.conclusionText.trim()
  const summaryText = feedbackReport.summaryText.trim()
  const analysisText = feedbackReport.analysisText.trim()
  if (!conclusionText || conclusionText === summaryText || conclusionText === analysisText) {
    return ''
  }
  return conclusionText
})

/**
 * 加载节点详情。
 */
const loadNodeData = async () => {
  if (!currentNodeId.value) {
    ElMessage.warning('缺少任务节点ID')
    return
  }

  loading.value = true
  try {
    const nodePayload = normalizeObjectFromPayload(
      await getPathNodeDetail(currentNodeId.value, courseStore.courseId)
    )

    currentTask.value = normalizeTaskPayload(nodePayload)
    masteryBeforeRate.value = normalizeNullableNumber(nodePayload.mastery_before)
    masteryAfterRate.value = normalizeNullableNumber(nodePayload.mastery_after)
  } catch (error) {
    console.error('加载节点数据失败:', error)
    ElMessage.error('加载学习资源失败')
  } finally {
    loading.value = false
  }

  if (!isTestNode.value) {
    void loadAIResources()
  }
}

/**
 * 异步加载 AI 推荐的内部资源和外部资源。
 */
const loadAIResources = async () => {
  aiResourcesLoading.value = true
  try {
    const recommendationPayload = normalizeObjectFromPayload(await getAIResources(currentNodeId.value))
    const internalResourceList = normalizeListFromPayload(recommendationPayload.internal_resources).map(normalizeResourcePayload)
    const externalResourceList = normalizeListFromPayload(recommendationPayload.external_resources).map(normalizeResourcePayload)
    resourceRecords.value = [...internalResourceList, ...externalResourceList]
  } catch (error) {
    console.warn('AI资源推荐加载失败:', error)
  } finally {
    aiResourcesLoading.value = false
  }
}

/**
 * 加载 AI 知识点介绍。
 */
const loadNodeIntro = async () => {
  if (!currentTask.value.pointNameText) {
    return
  }

  introLoading.value = true
  try {
    const introPayload = await getAINodeIntro({
      point_name: currentTask.value.pointNameText,
      point_id: currentTask.value.knowledgePointId,
      course_id: courseStore.courseId || null,
      course_name: courseStore.courseName || ''
    })
    nodeIntro.value = normalizeNodeIntroPayload(introPayload)
  } catch (error) {
    console.error('加载知识点介绍失败:', error)
  } finally {
    introLoading.value = false
  }
}

const goBack = () => {
  const shouldShowRefreshing = stageTestResult.value.isPassed && stageTestResult.value.isPathRefreshed
  void router.push(shouldShowRefreshing ? '/student/learning-path?refreshing=1' : '/student/learning-path')
}

const selectResource = async (resourceRecord) => {
  currentResourceRecord.value = resourceRecord
  if (resourceRecord.resourceUrl) {
    window.open(resourceRecord.resourceUrl, '_blank')
  }
  if (!resourceRecord.isCompleted) {
    try {
      await completeResource(currentNodeId.value, resourceRecord.resourceId, courseStore.courseId)
      resourceRecord.isCompleted = true
      ElMessage.success('资源学习完成！')
    } catch (error) {
      console.error('标记资源完成失败:', error)
      ElMessage.error('标记资源完成失败，请稍后重试')
    }
  }
}

const completeTask = async () => {
  try {
    await completePathNode(currentNodeId.value, courseStore.courseId)
    ElMessage.success('恭喜！任务学习完成！')
    await router.push('/student/learning-path?refreshing=1')
  } catch (error) {
    console.error('完成任务失败:', error)
    ElMessage.error('完成任务失败，请稍后重试')
  }
}

/**
 * 加载节点作业。
 */
const loadNodeExam = async () => {
  try {
    const examPayload = normalizeObjectFromPayload(await getNodeExams(currentNodeId.value, courseStore.courseId))
    const examList = normalizeListFromPayload(examPayload.exams).map(normalizeNodeExamPayload)
    currentNodeExam.value = examList[0] || buildDefaultNodeExamModel()
  } catch (error) {
    console.error('加载节点测验失败:', error)
  }
}

/**
 * 加载阶段测试（test类型节点专用）。
 */
const loadStageTest = async () => {
  stageTestLoading.value = true
  try {
    const stageTestPayload = normalizeObjectFromPayload(await getStageTest(currentNodeId.value))
    const questionList = normalizeListFromPayload(stageTestPayload.questions).map(normalizeStageQuestionPayload)

    stageTestTitle.value = normalizeText(stageTestPayload.node_title ?? stageTestPayload.title) || '阶段测试'
    stageTestPassScore.value = normalizeNumber(stageTestPayload.pass_score, 60)
    stageTestQuestions.value = questionList
    stageTestAnswers.value = buildStageTestAnswers(questionList)

    const normalizedResult = normalizeStageTestResultPayload(stageTestPayload.result)
    stageTestResult.value = normalizedResult
    if (normalizedResult.hasResult) {
      stageTestPassScore.value = normalizedResult.passThresholdValue
    }
  } catch (error) {
    if (error?.response?.status !== 404 && error?.status !== 404) {
      console.error('加载阶段测试失败:', error)
    }
  } finally {
    stageTestLoading.value = false
  }
}

/**
 * 提交阶段测试答案。
 */
const submitStageTestAnswers = async () => {
  const unansweredQuestions = stageTestQuestions.value.filter((questionItem) => {
    return isEmptyStageAnswer(stageTestAnswers.value[questionItem.questionId])
  })
  if (unansweredQuestions.length > 0) {
    ElMessage.warning(`还有 ${unansweredQuestions.length} 题未作答`)
    return
  }

  stageTestLoading.value = true
  try {
    const answerPayload = {}
    stageTestQuestions.value.forEach((questionItem) => {
      answerPayload[questionItem.questionId] = stageTestAnswers.value[questionItem.questionId]
    })

    const submissionResult = normalizeStageTestResultPayload(
      await submitStageTest(currentNodeId.value, { answers: answerPayload })
    )
    stageTestResult.value = submissionResult
    stageTestPassScore.value = submissionResult.passThresholdValue || stageTestPassScore.value

    if (submissionResult.isPassed) {
      ElMessage.success(`测试通过！得分：${submissionResult.scoreValue}分`)
    } else {
      ElMessage.warning(`未通过，得分：${submissionResult.scoreValue}分，需要${stageTestPassScore.value}分`)
    }
  } catch (error) {
    console.error('提交阶段测试失败:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    stageTestLoading.value = false
  }
}

/**
 * 重新做阶段测试。
 */
const retryStageTest = () => {
  stageTestResult.value = buildDefaultStageTestResultModel()
  stageTestAnswers.value = buildStageTestAnswers(stageTestQuestions.value)
}

/**
 * 重置节点作业结果。
 */
const resetNodeQuizResult = () => {
  nodeQuizResult.value = buildDefaultNodeQuizResultModel()
}

const formatStageAnswer = (answerValue) => {
  if (answerValue === null || answerValue === undefined || answerValue === '') {
    return '未作答'
  }
  if (typeof answerValue === 'boolean') {
    return answerValue ? '正确' : '错误'
  }
  if (Array.isArray(answerValue)) {
    return answerValue.map((item) => normalizeText(item)).filter(Boolean).join('、')
  }

  const answerPayload = normalizeObjectFromPayload(answerValue)
  if (Object.keys(answerPayload).length) {
    if (Array.isArray(answerPayload.answers)) {
      return answerPayload.answers.map((item) => normalizeText(item)).filter(Boolean).join('、')
    }
    if (typeof answerPayload.answer === 'boolean') {
      return answerPayload.answer ? '正确' : '错误'
    }
    if (answerPayload.answer !== undefined) {
      return normalizeText(answerPayload.answer)
    }
  }
  return normalizeText(answerValue)
}

/**
 * 开始节点作业。
 */
const startQuiz = async () => {
  if (!currentNodeExam.value.examId) {
    return
  }
  try {
    await ElMessageBox.confirm(
      `即将开始「${currentNodeExam.value.titleText}」作业，准备好了吗？`,
      '节点作业',
      { confirmButtonText: '开始', cancelButtonText: '稍后', type: 'info' }
    )
    await router.push({
      path: `/student/exam/${currentNodeExam.value.examId}`,
      query: { nodeId: currentNodeId.value }
    })
  } catch {
    // 用户主动取消时不提示错误
  }
}

/**
 * 发送聊天消息。
 */
const sendChat = async () => {
  const questionText = chatInput.value.trim()
  if (!questionText || chatLoading.value) {
    return
  }

  const recentHistory = chatMessages.value.slice(-12)
  chatMessages.value.push({ role: 'user', content: questionText })
  chatInput.value = ''
  chatLoading.value = true
  await scrollChat()

  try {
    const chatReplyPayload = normalizeObjectFromPayload(
      await aiChat({
        question: questionText,
        message: questionText,
        course_id: courseStore.courseId || null,
        point_id: currentTask.value.knowledgePointId || null,
        knowledge_point: currentTask.value.pointNameText || '',
        course_name: courseStore.courseName || '',
        history: recentHistory
      })
    )
    chatMessages.value.push({
      role: 'assistant',
      content: normalizeText(chatReplyPayload.reply) || '暂无回复'
    })
  } catch {
    chatMessages.value.push({ role: 'assistant', content: '抱歉，AI助手暂时无法回复，请稍后重试。' })
  } finally {
    chatLoading.value = false
    await scrollChat()
  }
}

const scrollChat = async () => {
  await nextTick()
  const chatContainerElement = resolveTemplateElement(chatMessagesRef)
  if (chatContainerElement) {
    chatContainerElement.scrollTop = chatContainerElement.scrollHeight
  }
}

const scrollStageTestCardIntoView = () => {
  const stageTestElement = resolveTemplateElement(stageTestCardRef)
  if (stageTestElement && typeof stageTestElement.scrollIntoView === 'function') {
    stageTestElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const openFullAssistant = () => {
  chatDrawerVisible.value = false
  void router.push({
    path: '/student/ai-assistant',
    query: {
      pointId: currentTask.value.knowledgePointId || '',
      keyword: currentTask.value.pointNameText || ''
    }
  })
}

const formatMessage = (content) => {
  return renderMarkdown(content)
}

onMounted(async () => {
  if (isTestNode.value) {
    stageTestLoading.value = true
  }

  await loadNodeData()

  if (isTestNode.value) {
    void loadStageTest()
  } else {
    void loadNodeIntro()
    void loadNodeExam()
  }

  if (shouldViewStageReport.value) {
    await nextTick()
    window.setTimeout(() => {
      scrollStageTestCardIntoView()
    }, 500)
  }
})
</script>

<style scoped>
.task-learning-view {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.content-row {
  margin-top: 0;
  align-items: stretch;
}

.content-row>.el-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 知识点介绍卡片 */
.intro-card {
  margin-bottom: 20px;
  border-left: 3px solid var(--primary-color);
  animation: fadeInUp 0.42s ease-out;
}

.resources-card,
.goal-card,
.progress-card,
.quiz-card,
.stage-test-card {
  width: 100%;
  margin-top: 0 !important;
}

.resources-card :deep(.el-card__body),
.goal-card :deep(.el-card__body),
.progress-card :deep(.el-card__body),
.quiz-card :deep(.el-card__body) {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.intro-text {
  margin: 0 0 12px;
  color: #606266;
  line-height: 1.8;
}

.key-concepts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.concept-tag {
  border-radius: 12px;
}

.learning-tip {
  margin: 0;
  color: #909399;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 资源计数 */
.resource-count {
  font-size: 13px;
  color: #909399;
}

/* 资源列表 */
.loading-container {
  padding: 20px;
}

.resources-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-loading-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: #909399;
  font-size: 13px;
  background: rgba(20, 184, 166, 0.08);
  border-radius: 8px;
  border: 1px dashed rgba(20, 184, 166, 0.2);
}

.ai-loading-hint .is-loading {
  animation: rotating 2s linear infinite;
  color: var(--primary-color);
}

.empty-ai-searching {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #909399;
  line-height: 1.6;
  padding: 0 12px;
}

.empty-ai-searching .is-loading {
  animation: rotating 2s linear infinite;
  color: var(--primary-color);
}

.resource-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid transparent;
  border-radius: 18px;
  cursor: pointer;
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
}

.resource-item:hover {
  background: rgba(20, 184, 166, 0.08);
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.14);
  box-shadow: 0 18px 34px rgba(15, 23, 42, 0.08);
}

.resource-item.active {
  background: rgba(20, 184, 166, 0.08);
  border-left: 3px solid var(--primary-color);
}

.resource-item.completed {
  background: rgba(34, 160, 107, 0.08);
}

.resource-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 12px;
  font-size: 20px;
  color: var(--primary-color);
}

.resource-item.completed .resource-icon {
  color: #67c23a;
}

.resource-info {
  flex: 1;
  margin-left: 16px;
}

.resource-info h4 {
  margin: 0 0 4px;
  font-size: 15px;
  color: #303133;
}

.resource-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.resource-arrow {
  color: #c0c4cc;
  margin-left: 8px;
}

/* 进度卡片 */
.progress-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.progress-stats {
  margin-top: 20px;
  text-align: center;
}

.progress-stats p {
  margin: 0;
  color: #606266;
}

.progress-stats strong {
  color: var(--primary-color);
  font-size: 18px;
}

.action-buttons {
  display: flex;
  justify-content: center;
}

.action-buttons .el-button {
  width: 100%;
}

/* 掌握度对比 */
.mastery-compare {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mastery-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mastery-label {
  font-size: 13px;
  color: #606266;
  width: 50px;
  flex-shrink: 0;
}

/* AI 聊天 */
.assistant-drawer-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-welcome {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.chat-welcome .el-icon {
  font-size: 32px;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.chat-welcome p {
  margin: 8px 0 0;
  font-size: 14px;
}

.chat-msg {
  display: flex;
}

.chat-msg.user {
  justify-content: flex-end;
}

.chat-msg.assistant {
  justify-content: flex-start;
}

.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.chat-msg.user .msg-bubble {
  background: var(--primary-color);
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.2);
}

.chat-msg.assistant .msg-bubble {
  background: rgba(248, 250, 252, 0.92);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--border-light);
}

.msg-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 13px;
}

.msg-bubble :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.msg-bubble :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

/* 打字动画 */
.msg-bubble.typing {
  display: flex;
  gap: 4px;
  padding: 14px 18px;
}

.msg-bubble.typing span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typing 1.4s infinite both;
}

.msg-bubble.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.msg-bubble.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {

  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.4;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #ebeef5;
}

/* 测验卡片 */
.quiz-card .quiz-result p {
  margin: 4px 0;
  color: #606266;
}

.quiz-card .quiz-result strong {
  font-size: 24px;
}

/* 嵌入式阶段测试 */
.stage-test-card {
  border: 1px solid rgba(18, 154, 116, 0.12);
  background: var(--bg-soft);
}

.stage-test-result {
  padding: 8px 0 20px;
}

.stage-result-summary {
  display: grid;
  grid-template-columns: minmax(0, 220px) minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  margin-bottom: 18px;
}

.stage-result-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(18, 154, 116, 0.08);
  text-align: center;
}

.metric-label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.metric-card strong {
  font-size: 18px;
  color: var(--text-primary);
}

.result-score {
  font-size: 48px;
  font-weight: 700;
  text-align: center;
  padding: 22px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(18, 154, 116, 0.08);
}

.result-score-unit {
  font-size: 18px;
  color: var(--text-secondary);
}

.stage-test-result p {
  margin: 4px 0;
  color: var(--text-regular);
}

.stage-report-card {
  margin-top: 20px;
  padding: 18px;
  text-align: left;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(18, 154, 116, 0.08);
  border-radius: 16px;
}

.stage-report-card h4,
.stage-mistake-list h4,
.stage-report-section h5 {
  margin: 0 0 10px;
  color: #303133;
}

.stage-report-summary,
.stage-report-analysis,
.stage-report-encouragement {
  line-height: 1.8;
  color: #606266;
}

.stage-report-summary {
  margin-bottom: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(14, 165, 164, 0.08);
}

.stage-report-encouragement {
  margin-top: 12px;
  padding: 10px 12px;
  background: rgba(34, 160, 107, 0.08);
  border-radius: 8px;
  color: var(--success-color);
}

.stage-gap-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.goal-content {
  display: grid;
  gap: 16px;
}

.goal-mastery-card {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(14, 165, 164, 0.08);
  border: 1px solid rgba(18, 154, 116, 0.12);
}

.goal-mastery-title {
  margin-bottom: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}

.goal-mastery-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.goal-mastery-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.goal-mastery-item span {
  font-size: 12px;
  color: var(--text-secondary);
}

.goal-mastery-item strong {
  font-size: 22px;
  color: var(--text-primary);
}

.goal-mastery-item.success strong {
  color: var(--success-color);
}

.stage-report-section ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
}

.stage-mastery-list {
  display: grid;
  gap: 10px;
}

.stage-mastery-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(17, 88, 69, 0.06);
  color: var(--text-regular);
}

.stage-mastery-item strong {
  color: var(--text-primary);
}

.stage-mistake-list {
  margin-top: 20px;
  text-align: left;
}

.stage-mistake-item {
  margin-bottom: 12px;
  padding: 12px 14px;
  background: rgba(212, 80, 80, 0.08);
  border-radius: 12px;
  border-left: 3px solid var(--danger-color);
}

.stage-mistake-item p {
  margin: 6px 0;
}

.stage-mistake-title {
  font-weight: 600;
  color: #303133;
}

.mistake-label {
  color: #909399;
  margin-right: 6px;
}

.stage-test-questions {
  max-height: 720px;
  overflow-y: auto;
  padding-right: 8px;
}

.stage-test-intro {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 18px;
  margin-bottom: 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(18, 154, 116, 0.08);
}

.stage-test-intro-text h4 {
  margin: 0 0 8px;
  font-size: 18px;
  color: var(--text-primary);
}

.stage-test-intro-text p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.stage-test-intro-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.question-item {
  margin-bottom: 18px;
  padding: 20px 18px;
  border: 1px solid rgba(18, 154, 116, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
}

.question-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.question-order,
.question-score {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.question-order {
  color: var(--primary-color);
  background: rgba(18, 154, 116, 0.08);
}

.question-score {
  color: var(--warning-color);
  background: rgba(221, 143, 29, 0.12);
}

.question-title {
  margin: 0 0 18px;
  font-size: 17px;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.7;
  text-align: center;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-option {
  margin-right: 0 !important;
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(244, 251, 248, 0.96);
  border: 1px solid rgba(18, 154, 116, 0.08);
}

.question-option:hover {
  background: rgba(20, 184, 166, 0.08);
}

@media (max-width: 768px) {
  .stage-result-summary {
    grid-template-columns: 1fr;
  }

  .stage-result-metrics {
    grid-template-columns: 1fr;
  }

  .stage-test-intro {
    flex-direction: column;
  }
}
</style>

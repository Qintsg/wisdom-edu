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
import {
  ArrowRight,
  ChatDotRound,
  CircleCheck,
  Document,
  InfoFilled,
  MagicStick,
  Promotion,
  Reading,
  VideoPlay
} from '@element-plus/icons-vue'
import { useTaskLearning } from './useTaskLearning'

const {
  allCompleted,
  aiResourcesLoading,
  chatDrawerVisible,
  chatInput,
  chatLoading,
  chatMessages,
  chatMessagesRef,
  completeTask,
  completedResourceCount,
  currentNodeExam,
  currentResourceRecord,
  currentTask,
  difficultyLabel,
  difficultyTagType,
  displayStageConclusion,
  formatMessage,
  formatStageAnswer,
  goBack,
  hasNodeExam,
  hasNodeIntro,
  hasNodeQuizResult,
  hasStageFeedbackReport,
  hasStageTestResult,
  introLoading,
  isTestNode,
  loadStageTest,
  loading,
  masteryAfterRate,
  masteryBeforeRate,
  nodeIntro,
  nodeQuizResult,
  openFullAssistant,
  progressPercent,
  renderMarkdown,
  resetNodeQuizResult,
  resourceRecords,
  retryStageTest,
  selectResource,
  sendChat,
  stageTestAnswers,
  stageTestCardRef,
  stageTestLoading,
  stageTestPassScore,
  stageTestQuestions,
  stageTestResult,
  stageTestTitle,
  startQuiz,
  submitStageTestAnswers
} = useTaskLearning()
</script>

<style scoped src="./TaskLearningView.css"></style>
<style scoped src="./TaskLearningStageTest.css"></style>

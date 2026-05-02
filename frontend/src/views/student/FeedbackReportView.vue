<template>
  <div class="feedback-report-view">
    <!-- Page-level navigation keeps the report in the homework flow. -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span>作业反馈报告</span>
      </template>
    </el-page-header>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="15" animated />
    </div>

    <template v-else>
      <!-- Score overview stays visible even while the AI report is still polling. -->
      <el-card class="score-card" shadow="hover">
        <div class="score-content">
          <div class="score-circle">
            <el-progress type="circle" :percentage="scorePercent" :width="152" :stroke-width="12" :color="scoreColor">
              <template #default>
                <div class="score-text">
                  <span class="score-value">{{ examResult.score }}</span>
                  <span class="score-unit">/ {{ examResult.totalScore }}</span>
                </div>
              </template>
            </el-progress>
          </div>
          <div class="score-info">
            <h2>{{ examResult.titleText }}</h2>
            <div class="score-stats">
              <div class="stat-item">
                <span class="stat-label">答对题数</span>
                <span class="stat-value correct">{{ examResult.correctCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">错误题数</span>
                <span class="stat-value wrong">{{ examResult.wrongCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">正确率</span>
                <span class="stat-value">{{ examResult.accuracy }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">结果</span>
                <span class="stat-value" :class="examResult.passed ? 'correct' : 'wrong'">
                  {{ examResult.passed ? '通过' : '未通过' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="analysis-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon>
                <MagicStick />
              </el-icon> AI 智能分析</span>
            <el-tag :type="statusTagType" effect="plain">{{ statusLabel }}</el-tag>
          </div>
        </template>

        <div class="analysis-content">
          <!-- Status alert changes first so the student immediately knows whether to wait or retry. -->
          <el-alert v-if="feedbackStatus === 'pending'" :title="aiAnalysis.summary || '成绩已生成，AI 报告正在生成中...'" type="info"
            :closable="false" show-icon />
          <el-alert v-else-if="feedbackStatus === 'failed'" title="AI 报告生成失败，可以重新获取" type="warning" :closable="false"
            show-icon />
          <el-alert v-else :title="aiAnalysis.summary || '暂无分析摘要'" type="info" :closable="false" show-icon />

          <!-- Pending state keeps the page useful while background generation finishes. -->
          <div v-if="feedbackStatus === 'pending'" class="ai-pending">
            <el-progress :percentage="aiProgressPercent" :stroke-width="10" :show-text="true" status="" />
            <p class="ai-progress-stage">{{ aiProgressStageText }}</p>
          </div>

          <!-- Failed state exposes a single retry action instead of stale partial content. -->
          <div v-else-if="feedbackStatus === 'failed'" class="ai-retry">
            <el-button type="primary" size="small" :loading="aiRetrying" @click="retryAIFeedback">
              重新获取 AI 分析
            </el-button>
          </div>

          <template v-else>
            <!-- Each section is rendered independently because the backend may omit some fields. -->
            <div v-if="aiAnalysis.analysis" class="feedback-section">
              <h4>综合分析</h4>
              <p>{{ aiAnalysis.analysis }}</p>
            </div>

            <div v-if="aiAnalysis.knowledgeGaps.length" class="feedback-section">
              <h4>薄弱知识点</h4>
              <div class="tag-group">
                <el-tag v-for="(gap, index) in aiAnalysis.knowledgeGaps" :key="`gap-${index}`" type="warning"
                  effect="plain">
                  {{ gap }}
                </el-tag>
              </div>
            </div>

            <div v-if="aiAnalysis.suggestions.length" class="feedback-section">
              <h4>改进建议</h4>
              <ul>
                <li v-for="(suggestion, index) in aiAnalysis.suggestions" :key="`suggestion-${index}`">
                  {{ suggestion }}
                </li>
              </ul>
            </div>

            <!-- Task items may arrive as plain strings or richer objects, so the template normalizes both. -->
            <div v-if="aiAnalysis.nextTasks.length" class="feedback-section">
              <h4>下一步学习任务</h4>
              <ul>
                <li v-for="(task, index) in aiAnalysis.nextTasks" :key="`task-${index}`">
                  {{ typeof task === 'string' ? task : task.description || task.title || JSON.stringify(task) }}
                </li>
              </ul>
            </div>

            <!-- Mastery change cards expose before/after percentages without forcing chart reading. -->
            <div v-if="masteryChanges.length" class="feedback-section">
              <h4>知识掌握度变化</h4>
              <div class="mastery-change-list">
                <div v-for="item in masteryChanges" :key="item.knowledgePointId" class="mastery-change-item">
                  <span>{{ item.knowledgePointName }}</span>
                  <strong>{{ Math.round((item.masteryBefore || 0) * 100) }}% -> {{ Math.round((item.masteryAfter || 0) *
                    100) }}%</strong>
                </div>
              </div>
            </div>

            <!-- Duplicate conclusion text is hidden in script to avoid repeating the same sentence. -->
            <div v-if="displayConclusion" class="conclusion-section">
              <p>{{ displayConclusion }}</p>
            </div>
          </template>
        </div>
      </el-card>

      <el-card class="detail-card" shadow="hover">
        <template #header>
          <span>答题详情</span>
        </template>

        <el-collapse>
          <!-- Question review stays expanded per item so the student can inspect mistakes selectively. -->
          <el-collapse-item v-for="(question, index) in questionDetails" :key="question.questionId" :name="index">
            <template #title>
              <span>第 {{ index + 1 }} 题</span>
              <el-tag :type="question.isCorrect ? 'success' : 'danger'" size="small" class="title-tag">
                {{ question.isCorrect ? '正确' : '错误' }}
              </el-tag>
            </template>

            <p class="question-content">{{ question.contentText }}</p>

            <!-- Option styling highlights both correctness and the student's own selection path. -->
            <div v-if="question.optionList.length" class="option-review">
              <div v-for="option in question.optionList" :key="`${question.questionId}-${option.optionKey}`"
                class="option-row" :class="{ correct: option.isCorrectOption, selected: option.isStudentSelected }">
                <span class="option-prefix">{{ option.optionPrefix }}</span>
                <span class="option-text">{{ option.optionText }}</span>
                <el-tag v-if="option.isCorrectOption" size="small" type="success" effect="plain">正确选项</el-tag>
                <el-tag v-if="option.isStudentSelected" size="small" :type="question.isCorrect ? 'success' : 'warning'"
                  effect="plain">
                  你的选择
                </el-tag>
              </div>
            </div>

            <p>
              <span class="label">你的答案：</span>
              <span :class="question.isCorrect ? 'correct-answer' : 'wrong-answer'">
                {{ question.studentAnswerText || formatAnswer(question.studentAnswer) }}
              </span>
            </p>
            <p>
              <span class="label">正确答案：</span>
              <span class="correct-answer">
                {{ question.correctAnswerText || formatAnswer(question.correctAnswer) }}
              </span>
            </p>
            <p v-if="question.analysisText" class="analysis-note">
              <span class="label">解析：</span>{{ question.analysisText }}
            </p>
          </el-collapse-item>
        </el-collapse>

        <el-empty v-if="!questionDetails.length" description="暂无答题详情" />
      </el-card>

      <!-- Action bar keeps the likely next decisions grouped at the bottom of the report. -->
      <div class="action-bar">
        <el-button @click="goBack" size="large">返回作业列表</el-button>
        <el-button v-if="!examResult.passed" type="warning" size="large" @click="retryExam">
          再做一次
        </el-button>
        <el-button type="primary" size="large" @click="goToLearningPath">
          继续学习
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { MagicStick } from '@element-plus/icons-vue'
import { useFeedbackReport } from './useFeedbackReport'

const {
  aiAnalysis,
  aiProgressPercent,
  aiProgressStageText,
  aiRetrying,
  displayConclusion,
  examResult,
  feedbackStatus,
  formatAnswer,
  goBack,
  goToLearningPath,
  loading,
  masteryChanges,
  questionDetails,
  retryAIFeedback,
  retryExam,
  scoreColor,
  scorePercent,
  statusLabel,
  statusTagType
} = useFeedbackReport()
</script>

<style scoped src="./FeedbackReportView.css"></style>

<template>
  <div class="exam-taking-view" v-loading.fullscreen.lock="loading || submitting"
    :element-loading-text="submitting ? '正在提交作业，成绩已同步计算，AI 报告将稍后补齐...' : '正在加载作业...'">
    <!-- 作业信息栏 (吸顶) -->
    <div class="exam-header-wrapper">
      <el-card class="exam-header" shadow="always" :body-style="{ padding: '15px 20px' }">
        <div class="header-content">
          <div class="exam-title">
            <el-icon class="icon">
              <Document />
            </el-icon>
            <h2>{{ examInfo.titleText }}</h2>
          </div>
          <div class="timer-wrapper" :class="{ 'urgent': remainingTime < 300 }">
            <el-icon>
              <Timer />
            </el-icon>
            <span class="timer-text">{{ formatTime(remainingTime) }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="exam-container">
      <el-row :gutter="24">
        <!-- 题目区域 -->
        <el-col :xs="24" :lg="18">
          <el-card class="question-card" shadow="never" v-if="currentQuestion">
            <template #header>
              <div class="card-header">
                <span class="question-index">
                  Question {{ currentIndex + 1 }}
                  <span class="total">/ {{ questions.length }}</span>
                </span>
                <el-tag :type="currentQuestion?.questionTagType" effect="dark">
                  {{ currentQuestion?.questionTypeText }}
                </el-tag>
                <div class="score-tag">
                  分值: {{ currentQuestion?.score }}分
                </div>
              </div>
            </template>

            <div class="question-content">
              <div class="question-stem">
                {{ currentQuestion?.stem }}
              </div>

              <div class="answer-area">
                <!-- 单选题 -->
                <el-radio-group v-if="currentQuestion?.answerMode === 'singleChoice'" v-model="answers[currentIndex]"
                  class="options-group">
                  <el-radio v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    <span class="option-label">{{ option.optionLabel }}.</span>
                    <span class="option-content">{{ option.optionContent }}</span>
                  </el-radio>
                </el-radio-group>

                <!-- 多选题 -->
                <el-checkbox-group v-else-if="currentQuestion?.answerMode === 'multipleChoice'"
                  v-model="answers[currentIndex]" class="options-group">
                  <el-checkbox v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    <span class="option-label">{{ option.optionLabel }}.</span>
                    <span class="option-content">{{ option.optionContent }}</span>
                  </el-checkbox>
                </el-checkbox-group>

                <!-- 判断题 -->
                <el-radio-group v-else-if="currentQuestion?.answerMode === 'trueFalse'" v-model="answers[currentIndex]"
                  class="options-group">
                  <el-radio value="true" class="option-item" border>正确</el-radio>
                  <el-radio value="false" class="option-item" border>错误</el-radio>
                </el-radio-group>

                <!-- 填空题 -->
                <el-input v-else-if="currentQuestion?.answerMode === 'fillBlank'" v-model="answers[currentIndex]"
                  placeholder="请输入答案" class="fill-input" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />

                <!-- 简答题 -->
                <el-input v-else-if="currentQuestion?.answerMode === 'shortAnswer'" v-model="answers[currentIndex]"
                  type="textarea" :rows="6" placeholder="请输入答案解析" class="fill-input" />

                <!-- 默认按单选容错处理 -->
                <el-radio-group v-else v-model="answers[currentIndex]" class="options-group">
                  <el-radio v-for="option in currentQuestion?.optionList" :key="option.optionValue"
                    :value="option.optionValue" class="option-item" border>
                    {{ option.optionContent }}
                  </el-radio>
                </el-radio-group>
              </div>
            </div>

            <div class="question-footer">
              <el-button-group>
                <el-button :disabled="currentIndex === 0" @click="prevQuestion" :icon="ArrowLeft">
                  上一道题
                </el-button>
                <el-button type="primary" @click="nextQuestion">
                  {{ isLastQuestion ? '交卷' : '下一道题' }}
                  <el-icon v-if="!isLastQuestion" class="el-icon--right">
                    <ArrowRight />
                  </el-icon>
                </el-button>
              </el-button-group>

              <div class="progress-info">
                已答: {{ respondedCount }} / {{ questions.length }}
              </div>
            </div>
          </el-card>

          <el-empty v-else-if="loadError" :description="loadError">
            <el-button type="primary" @click="loadExamData">重新加载</el-button>
          </el-empty>

          <el-empty v-else description="暂无题目" />
        </el-col>

        <!-- 答题卡 (侧边固定) -->
        <el-col :xs="24" :lg="6" class="sidebar-col">
          <div class="sidebar-wrapper">
            <el-card class="answer-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span>答题卡</span>
                  <el-button type="primary" link :loading="submitting" :disabled="submitting" @click="submitExam">
                    提交作业
                  </el-button>
                </div>
              </template>

              <div class="answer-grid">
                <div v-for="(q, index) in questions" :key="q.questionId" class="answer-cell" :class="{
                  'is-answered': isAnswered(index),
                  'is-current': index === currentIndex
                }" @click="goToQuestion(index)">
                  {{ index + 1 }}
                </div>
              </div>

              <div class="answer-legend">
                <div class="legend-item"><span class="dot is-current"></span>当前</div>
                <div class="legend-item"><span class="dot is-answered"></span>已答</div>
                <div class="legend-item"><span class="dot"></span>未答</div>
              </div>
            </el-card>

            <!-- 作业说明或其他信息 -->
            <el-card class="info-card" shadow="never" style="margin-top: 15px;">
              <div class="info-text">
                <el-icon>
                  <InfoFilled />
                </el-icon>
                作答期间请勿切换页面或刷新，系统会自动保存您的答题进度。
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { Timer, Document, ArrowLeft, ArrowRight, InfoFilled } from '@element-plus/icons-vue'
import { useExamTaking } from './useExamTaking'

const {
  answers,
  currentIndex,
  currentQuestion,
  examInfo,
  formatTime,
  goToQuestion,
  isAnswered,
  isLastQuestion,
  loadError,
  loadExamData,
  loading,
  nextQuestion,
  prevQuestion,
  questions,
  remainingTime,
  respondedCount,
  submitExam,
  submitting
} = useExamTaking()
</script>

<style scoped src="./ExamTakingView.css"></style>

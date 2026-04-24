<template>
  <div class="ai-assistant-view">
    <div class="assistant-layout">
      <el-card class="search-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span>知识图谱检索</span>
            <div class="panel-header-tags">
              <el-tag v-if="courseStore.courseName" size="small" effect="plain">{{ courseStore.courseName }}</el-tag>
              <el-tag size="small" type="info">GraphRAG</el-tag>
            </div>
          </div>
        </template>

        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="输入知识点名称、概念或问题关键词"
            clearable
            @keyup.enter="runSearch"
          >
            <template #append>
              <el-button :loading="searchLoading" @click="runSearch">检索</el-button>
            </template>
          </el-input>
        </div>

        <div v-if="searchResults.length" class="search-results">
          <button
            v-for="pointItem in searchResults"
            :key="pointItem.point_id"
            class="search-result-item"
            :class="{ active: selectedPoint?.point_id === pointItem.point_id }"
            @click="selectPoint(pointItem)"
          >
            <span class="search-result-main">
              <strong>{{ pointItem.point_name }}</strong>
              <span>{{ pointItem.chapter || '未分章' }}</span>
            </span>
            <span class="search-result-meta">
              <el-tag size="small" type="success">掌握度 {{ Math.round((pointItem.mastery_rate || 0) * 100) }}%</el-tag>
            </span>
            <span class="search-result-summary">{{ pointItem.description || '暂无摘要' }}</span>
          </button>
        </div>
        <el-empty v-else description="输入关键词后检索课程知识图谱" />

        <div v-if="selectedPointDetail" class="point-detail-card">
          <div class="detail-header">
            <h3>{{ selectedPointDetail.point_name }}</h3>
            <el-button link type="primary" @click="goToKnowledgeMap">查看图谱</el-button>
          </div>
          <p class="point-description">{{ selectedPointDetail.description || '暂无描述' }}</p>
          <div class="point-mastery">
            <span>当前掌握度</span>
            <el-progress :percentage="Math.round((selectedPointDetail.mastery_rate || 0) * 100)" :stroke-width="10" />
          </div>
          <div class="relation-groups">
            <div>
              <span class="relation-label">前置知识</span>
              <div class="relation-tags">
                <el-tag
                  v-for="item in selectedPointDetail.prerequisites || []"
                  :key="item.point_id || item"
                  size="small"
                  type="info"
                >
                  {{ item.point_name || item }}
                </el-tag>
                <span v-if="!(selectedPointDetail.prerequisites || []).length" class="empty-text">暂无</span>
              </div>
            </div>
            <div>
              <span class="relation-label">后续知识</span>
              <div class="relation-tags">
                <el-tag
                  v-for="item in selectedPointDetail.postrequisites || []"
                  :key="item.point_id || item"
                  size="small"
                  type="warning"
                >
                  {{ item.point_name || item }}
                </el-tag>
                <span v-if="!(selectedPointDetail.postrequisites || []).length" class="empty-text">暂无</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="chat-panel" shadow="hover">
        <template #header>
          <div class="panel-header">
            <span>图谱增强问答</span>
            <el-tag :type="isGraphEnhancedMode(lastMode) ? 'success' : 'warning'" size="small">
              {{ isGraphEnhancedMode(lastMode) ? '图谱增强回答' : '课程级回答' }}
            </el-tag>
          </div>
        </template>

        <div ref="chatScrollRef" class="chat-history">
          <div v-for="(messageItem, index) in chatMessages" :key="index" :class="['chat-message', messageItem.role]">
            <div class="message-bubble">
              <div class="message-content" v-html="renderMarkdown(messageItem.content)" />
              <div v-if="messageItem.sources?.length" class="message-sources">
                <span>来源：</span>
                <el-tag v-for="sourceItem in messageItem.sources" :key="formatSourceKey(sourceItem)" size="small" type="success">
                  {{ formatSourceLabel(sourceItem) }}
                </el-tag>
              </div>
              <div v-if="messageItem.matchedPoint" class="message-context">
                <span>命中知识点：{{ messageItem.matchedPoint.point_name }}</span>
              </div>
            </div>
          </div>

          <div v-if="chatLoading" class="chat-message assistant">
            <div class="message-bubble typing">
              <span class="typing-stage-text">{{ chatStageText }}</span>
              <span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>
            </div>
          </div>
        </div>

        <div class="chat-composer">
          <el-input
            v-model="questionInput"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="输入你的问题，可以先检索知识点再追问，也可以直接围绕当前课程提问。"
            @keydown="handleComposerKeydown"
            @keyup.ctrl.enter="askQuestion"
          />
          <div class="composer-actions">
            <div class="composer-context">
              <el-tag v-if="selectedPoint" size="small" type="info">当前知识点：{{ selectedPoint.point_name }}</el-tag>
              <span v-else>当前未指定知识点，将按课程上下文检索。</span>
              <span class="composer-shortcut">Enter 发送 · Shift + Enter 换行</span>
            </div>
            <el-button type="primary" :loading="chatLoading" @click="askQuestion">发送问题</el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { extractApiErrorMessage, isApiErrorHandled } from '@/api'
import { askGraphRAG, createStudentAIChatSocket, searchGraphRAG } from '@/api/student/ai'
import { getKnowledgePointDetail } from '@/api/student/knowledge'
import { useCourseStore } from '@/stores/course'
import { renderMarkdown } from '@/utils/markdown'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()

const searchKeyword = ref('')
const searchLoading = ref(false)
const searchResults = ref([])
const selectedPoint = ref(null)
const selectedPointDetail = ref(null)
const questionInput = ref('')
const chatLoading = ref(false)
const chatScrollRef = ref(null)
const activeSocket = ref(null)
const chatMessages = ref([
  {
    role: 'assistant',
    content: '你好，我是系统中的 GraphRAG AI助手。你可以先检索知识点，再围绕该知识点继续追问；也可以直接针对当前课程提问。',
    sources: [],
    matchedPoint: null
  }
])
const lastMode = ref('graph_rag')

const isGraphEnhancedMode = (mode) => {
  const normalizedMode = String(mode || '').trim()
  return normalizedMode !== '' && normalizedMode !== 'llm_fallback' && normalizedMode !== 'error'
}

// ---- AI 对话阶段动画 (DEFENSE_DEMO_PROGRESS) ----
const chatStageText = ref('AI助手正在检索知识图谱')
let chatStageTimer = null
let chatStageIdx = 0
const CHAT_STAGES = [
  'AI助手正在检索知识图谱',
  '正在匹配相关知识点',
  '正在整理图谱证据',
  '正在生成回答内容'
]

function startChatStageAnimation() {
  stopChatStageAnimation()
  chatStageIdx = 0
  chatStageText.value = CHAT_STAGES[0]
  chatStageTimer = window.setInterval(() => {
    chatStageIdx = (chatStageIdx + 1) % CHAT_STAGES.length
    chatStageText.value = CHAT_STAGES[chatStageIdx]
  }, 2500)
}

function stopChatStageAnimation() {
  if (chatStageTimer) {
    window.clearInterval(chatStageTimer)
    chatStageTimer = null
  }
}
// ---- END DEFENSE_DEMO_PROGRESS ----

const ensureCourseSelected = () => {
  if (!courseStore.courseId) {
    ElMessage.warning('请先选择课程后再使用 AI助手')
    router.push('/student/course-select')
    return false
  }
  return true
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  }
}

const handleComposerKeydown = (event) => {
  if (
    event.key !== 'Enter'
    || event.shiftKey
    || event.ctrlKey
    || event.altKey
    || event.metaKey
    || event.isComposing
  ) {
    return
  }

  event.preventDefault()
  void askQuestion()
}

const runSearch = async () => {
  if (!ensureCourseSelected()) return
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    ElMessage.warning('请输入检索关键词')
    return
  }
  searchLoading.value = true
  try {
    const data = await searchGraphRAG({
      course_id: courseStore.courseId,
      query: keyword,
      limit: 8
    })
    searchResults.value = data.matched_points || []
    if (searchResults.value.length) {
      await selectPoint(searchResults.value[0])
    } else {
      selectedPoint.value = null
      selectedPointDetail.value = null
    }
  } catch (error) {
    console.error('GraphRAG检索失败:', error)
    if (!isApiErrorHandled(error)) {
      ElMessage.error(extractApiErrorMessage(error, '知识图谱检索失败'))
    }
  } finally {
    searchLoading.value = false
  }
}

const selectPoint = async (pointItem) => {
  selectedPoint.value = pointItem
  try {
    selectedPointDetail.value = await getKnowledgePointDetail(pointItem.point_id, courseStore.courseId)
  } catch (error) {
    console.error('加载知识点详情失败:', error)
    selectedPointDetail.value = {
      point_id: pointItem.point_id,
      point_name: pointItem.point_name,
      description: pointItem.description || '',
      mastery_rate: pointItem.mastery_rate || 0,
      prerequisites: (pointItem.prerequisites || []).map(name => ({ point_name: name })),
      postrequisites: (pointItem.postrequisites || []).map(name => ({ point_name: name }))
    }
  }
}

const askQuestion = async () => {
  if (!ensureCourseSelected()) return
  const question = questionInput.value.trim()
  if (!question || chatLoading.value) {
    return
  }

  chatMessages.value.push({ role: 'user', content: question, sources: [], matchedPoint: null })
  questionInput.value = ''
  chatLoading.value = true
  startChatStageAnimation()
  const assistantMessage = {
    role: 'assistant',
    content: '',
    sources: [],
    matchedPoint: null
  }
  chatMessages.value.push(assistantMessage)
  await scrollToBottom()

  try {
    const websocketSucceeded = await askQuestionByWebSocket(question, assistantMessage)
    if (!websocketSucceeded) {
      const result = await askGraphRAG({
        course_id: courseStore.courseId,
        point_id: selectedPoint.value?.point_id || null,
        question
      })
      assistantMessage.content = result.reply || '暂无回复'
      assistantMessage.sources = result.sources || []
      assistantMessage.matchedPoint = result.matched_point || null
      lastMode.value = result.mode || 'llm_fallback'
      if (result.matched_point && (!selectedPoint.value || selectedPoint.value.point_id !== result.matched_point.point_id)) {
        await selectPoint(result.matched_point)
      }
    }
  } catch (error) {
    console.error('GraphRAG问答失败:', error)
    assistantMessage.content = `抱歉，AI助手暂时无法回复：${extractApiErrorMessage(error, '请稍后重试')}`
  } finally {
    stopChatStageAnimation()
    chatLoading.value = false
    await scrollToBottom()
  }
}

const askQuestionByWebSocket = (question, assistantMessage) => {
  return new Promise((resolve) => {
    let resolved = false
    let receivedChunk = false
    const timeoutId = window.setTimeout(() => {
      try {
        socket.close()
      } catch {
        // noop
      }
      finalize(false)
    }, 12000)

    if (activeSocket.value) {
      activeSocket.value.close()
      activeSocket.value = null
    }

    const socket = createStudentAIChatSocket()
    activeSocket.value = socket

    const finalize = (success) => {
      if (resolved) return
      resolved = true
      window.clearTimeout(timeoutId)
      if (activeSocket.value === socket) {
        activeSocket.value = null
      }
      resolve(success)
    }

    socket.onopen = () => {
      socket.send(JSON.stringify({
        question,
        course_id: courseStore.courseId,
        point_id: selectedPoint.value?.point_id || null
      }))
    }

    socket.onmessage = async (event) => {
      const payload = JSON.parse(event.data || '{}')
      if (payload.type === 'chunk') {
        receivedChunk = true
        assistantMessage.content += payload.content || ''
        await scrollToBottom()
        return
      }
      if (payload.type === 'done') {
        assistantMessage.sources = payload.sources || []
        assistantMessage.matchedPoint = payload.matched_point || null
        lastMode.value = payload.mode || 'graph_rag'
        if (payload.matched_point && (!selectedPoint.value || selectedPoint.value.point_id !== payload.matched_point.point_id)) {
          await selectPoint(payload.matched_point)
        }
        socket.close()
        finalize(receivedChunk || !!assistantMessage.content)
        return
      }
      if (payload.type === 'error') {
        assistantMessage.content = payload.message || ''
        socket.close()
        finalize(false)
      }
    }

    socket.onerror = () => {
      finalize(false)
    }

    socket.onclose = () => {
      finalize(receivedChunk || !!assistantMessage.content)
    }
  })
}

const goToKnowledgeMap = () => {
  if (!selectedPoint.value) {
    return
  }
  router.push('/student/knowledge-map')
}

const formatSourceLabel = (sourceItem) => {
  if (!sourceItem) return '未知来源'
  if (typeof sourceItem === 'string') return sourceItem
  return sourceItem.title || sourceItem.kind || '未知来源'
}

const formatSourceKey = (sourceItem) => {
  if (typeof sourceItem === 'string') return sourceItem
  return `${sourceItem?.title || 'source'}-${sourceItem?.kind || 'unknown'}-${sourceItem?.score || 0}`
}

onMounted(async () => {
  if (!ensureCourseSelected()) return
  const keyword = String(route.query.keyword || '').trim()
  const pointId = Number(route.query.pointId || 0)
  if (pointId) {
    selectedPoint.value = {
      point_id: pointId,
      point_name: keyword || '当前知识点'
    }
    await selectPoint(selectedPoint.value)
  }
  if (keyword) {
    searchKeyword.value = keyword
    await runSearch()
  }
})

onUnmounted(() => {
  stopChatStageAnimation()
  if (activeSocket.value) {
    activeSocket.value.close()
    activeSocket.value = null
  }
})
</script>

<style scoped>
.ai-assistant-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 142px);
}

.assistant-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.95fr) minmax(0, 1.35fr);
  gap: 20px;
  flex: 1;
  min-height: 0;
}

.panel-header,
.detail-header,
.search-result-main,
.search-result-meta,
.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-header-tags {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.search-panel,
.chat-panel {
  min-height: 0;
  height: 100%;
}

.search-panel :deep(.el-card__body),
.chat-panel :deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-panel :deep(.el-card__body) {
  gap: 16px;
}

.search-box {
  margin-bottom: 0;
}

.search-results {
  display: grid;
  gap: 10px;
  max-height: min(34vh, 280px);
  overflow: auto;
  padding-right: 4px;
  flex: 0 0 auto;
}

.search-result-item {
  display: grid;
  gap: 10px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(15, 108, 189, 0.08);
  border-radius: 14px;
  background: var(--bg-elevated);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.search-result-item.active,
.search-result-item:hover {
  border-color: rgba(15, 108, 189, 0.28);
  transform: translateY(-1px);
}

.search-result-summary,
.point-description {
  display: block;
  margin: 0;
  line-height: 1.7;
  color: #606266;
}

.point-detail-card {
  display: grid;
  gap: 16px;
  padding: 18px;
  border: 1px solid rgba(15, 108, 189, 0.12);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(244, 248, 252, 0.96));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.point-detail-card h3 {
  margin: 0;
  color: #303133;
}

.point-mastery {
  display: grid;
  gap: 8px;
}

.relation-groups {
  display: grid;
  gap: 14px;
}

.relation-label {
  display: block;
  margin-bottom: 8px;
  color: #909399;
  font-size: 13px;
}

.relation-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-text {
  color: #909399;
  font-size: 13px;
}

.chat-history {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  gap: 14px;
  padding-right: 6px;
}

.chat-message {
  display: flex;
}

.chat-message.user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 88%;
  padding: 14px 16px;
  border-radius: 16px;
  background: var(--bg-elevated);
  border: 1px solid rgba(15, 108, 189, 0.08);
}

.chat-message.user .message-bubble {
  background: linear-gradient(135deg, rgba(15, 108, 189, 0.92), rgba(91, 157, 237, 0.82));
  color: #fff;
}

.message-content :deep(p) {
  margin: 0;
  line-height: 1.8;
}

.message-sources,
.message-context {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.typing {
  color: #606266;
  display: flex;
  align-items: center;
  gap: 2px;
}

.typing-stage-text {
  animation: stage-fade 0.5s ease;
}

.typing-dots span {
  animation: dot-blink 1.4s infinite;
  opacity: 0;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dot-blink {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes stage-fade {
  from { opacity: 0.4; }
  to { opacity: 1; }
}

.chat-composer {
  margin-top: 18px;
  display: grid;
  gap: 10px;
}

.composer-context {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: #909399;
  font-size: 13px;
}

.composer-shortcut {
  color: #606266;
}

@media (max-width: 960px) {
  .ai-assistant-view {
    min-height: auto;
  }

  .assistant-layout {
    grid-template-columns: 1fr;
  }

  .chat-history {
    height: 420px;
    min-height: 420px;
  }
}
</style>

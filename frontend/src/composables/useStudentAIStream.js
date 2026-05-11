import { nextTick, onUnmounted, ref } from 'vue'
import { createStudentAIChatSocket } from '@/api/student/ai'

const DEFAULT_STAGE_TEXT = '正在连接 AI 助手'
const FALLBACK_ERROR_TEXT = '抱歉，AI助手暂时无法回复，请稍后重试。'

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeChunkText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value)
}

const createAssistantMessage = () => ({
  role: 'assistant',
  content: '',
  sources: [],
  matchedPoint: null,
  mode: '',
  queryModes: [],
  keyPoints: [],
  streamed: false
})

const normalizeSourceList = (value) => Array.isArray(value) ? value : []

/**
 * 学生端 AI WebSocket 流式问答状态机。
 * 维护意图：AI助手页和学习节点抽屉共享连接、chunk 拼接、降级和清理逻辑。
 */
export function useStudentAIStream(options = {}) {
  const messages = options.messages || ref([])
  const loading = ref(false)
  const stageText = ref(DEFAULT_STAGE_TEXT)
  const activeSocket = ref(null)
  const lastMode = ref('graph_rag')
  const shouldInlineErrorFallback = options.inlineErrorFallback !== false

  const applyErrorFallback = (assistantMessage, message = FALLBACK_ERROR_TEXT) => {
    if (shouldInlineErrorFallback) {
      assistantMessage.content = normalizeText(message) || FALLBACK_ERROR_TEXT
    }
  }

  const scrollToBottom = async () => {
    await nextTick()
    if (typeof options.scrollToBottom === 'function') {
      await options.scrollToBottom()
    }
  }

  const closeSocket = () => {
    if (!activeSocket.value) return
    try {
      activeSocket.value.close()
    } catch {
      // 关闭失败不影响页面卸载。
    }
    activeSocket.value = null
  }

  const sendStreamMessage = async ({
    question,
    payload = {},
    history = [],
    assistantMessage = createAssistantMessage(),
    onDone,
    onError
  }) => {
    const questionText = normalizeText(question)
    if (!questionText || loading.value) return null

    closeSocket()
    loading.value = true
    stageText.value = DEFAULT_STAGE_TEXT

    let socket = null
    try {
      socket = createStudentAIChatSocket()
    } catch {
      applyErrorFallback(assistantMessage)
      loading.value = false
      if (typeof onError === 'function') onError({ type: 'error', message: assistantMessage.content || FALLBACK_ERROR_TEXT })
      await scrollToBottom()
      return assistantMessage
    }

    activeSocket.value = socket
    let settled = false
    let receivedChunk = false

    return new Promise((resolve) => {
      const finish = async () => {
        if (settled) return
        settled = true
        loading.value = false
        if (activeSocket.value === socket) activeSocket.value = null
        await scrollToBottom()
        resolve(assistantMessage)
      }

      socket.onopen = () => {
        socket.send(JSON.stringify({
          ...payload,
          question: questionText,
          message: questionText,
          history
        }))
      }

      socket.onmessage = async (event) => {
        let streamPayload = {}
        try {
          streamPayload = JSON.parse(event.data || '{}')
        } catch {
          return
        }

        if (streamPayload.type === 'stage') {
          stageText.value = normalizeText(streamPayload.message) || DEFAULT_STAGE_TEXT
          return
        }

        if (streamPayload.type === 'chunk') {
          const chunkText = normalizeChunkText(streamPayload.content)
          if (!chunkText) return
          receivedChunk = true
          assistantMessage.content += chunkText
          await scrollToBottom()
          return
        }

        if (streamPayload.type === 'done') {
          const finalReply = normalizeText(streamPayload.reply)
          if (finalReply && finalReply !== normalizeText(assistantMessage.content)) {
            assistantMessage.content = finalReply
          }
          assistantMessage.sources = normalizeSourceList(streamPayload.sources)
          assistantMessage.matchedPoint = streamPayload.matched_point || null
          assistantMessage.mode = normalizeText(streamPayload.mode) || 'graph_rag'
          assistantMessage.queryModes = normalizeSourceList(streamPayload.query_modes)
          assistantMessage.keyPoints = normalizeSourceList(streamPayload.key_points)
          assistantMessage.streamed = Boolean(streamPayload.streamed)
          lastMode.value = assistantMessage.mode
          if (typeof onDone === 'function') await onDone(streamPayload, assistantMessage)
          socket.close()
          await finish()
          return
        }

        if (streamPayload.type === 'error') {
          applyErrorFallback(assistantMessage, streamPayload.message)
          if (typeof onError === 'function') onError(streamPayload)
          socket.close()
          await finish()
        }
      }

      socket.onerror = async () => {
        if (!receivedChunk && !assistantMessage.content) {
          applyErrorFallback(assistantMessage)
        }
        if (typeof onError === 'function') onError({ type: 'error', message: assistantMessage.content || FALLBACK_ERROR_TEXT })
        await finish()
      }

      socket.onclose = async () => {
        if (!settled) {
          if (!receivedChunk && !assistantMessage.content) applyErrorFallback(assistantMessage)
          await finish()
        }
      }
    })
  }

  onUnmounted(() => {
    closeSocket()
  })

  return {
    closeSocket,
    createAssistantMessage,
    lastMode,
    loading,
    messages,
    sendStreamMessage,
    stageText
  }
}

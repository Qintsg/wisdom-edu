import { nextTick, onUnmounted, ref } from 'vue'
import { aiChat, createStudentAIChatSocket } from '@/api/student/ai'

const DEFAULT_STAGE_TEXT = '正在连接 AI 助手'
const HTTP_FALLBACK_STAGE_TEXT = '正在切换 HTTP 问答链路'
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

const hasMeaningfulReply = (assistantMessage) => normalizeText(assistantMessage.content) !== ''

/**
 * 学生端 AI WebSocket 流式问答状态机。
 */
export function useStudentAIStream(options = {}) {
  const messages = options.messages || ref([])
  const loading = ref(false)
  const stageText = ref(DEFAULT_STAGE_TEXT)
  const activeSocket = ref(null)
  const lastMode = ref('graph_rag')
  const shouldInlineErrorFallback = options.inlineErrorFallback !== false
  const httpFallback = options.httpFallback || aiChat

  const applyErrorFallback = (assistantMessage, message = FALLBACK_ERROR_TEXT) => {
    if (shouldInlineErrorFallback) {
      assistantMessage.content = normalizeText(message) || FALLBACK_ERROR_TEXT
    }
  }

  const applyFinalErrorFallback = (assistantMessage, message = FALLBACK_ERROR_TEXT) => {
    assistantMessage.content = normalizeText(message) || FALLBACK_ERROR_TEXT
  }

  const applyChatResult = async (assistantMessage, resultPayload, onDone) => {
    const streamPayload = {
      type: 'done',
      reply: normalizeText(resultPayload?.reply ?? resultPayload?.answer) || '暂无回复',
      sources: normalizeSourceList(resultPayload?.sources),
      matched_point: resultPayload?.matched_point || null,
      mode: normalizeText(resultPayload?.mode) || 'llm_fallback',
      query_modes: normalizeSourceList(resultPayload?.query_modes),
      key_points: normalizeSourceList(resultPayload?.key_points),
      streamed: false
    }
    assistantMessage.content = streamPayload.reply
    assistantMessage.sources = streamPayload.sources
    assistantMessage.matchedPoint = streamPayload.matched_point
    assistantMessage.mode = streamPayload.mode
    assistantMessage.queryModes = streamPayload.query_modes
    assistantMessage.keyPoints = streamPayload.key_points
    assistantMessage.streamed = false
    lastMode.value = assistantMessage.mode
    if (typeof onDone === 'function') await onDone(streamPayload, assistantMessage)
  }

  const runHttpFallback = async ({
    questionText,
    payload,
    history,
    assistantMessage,
    onDone
  }) => {
    if (!httpFallback || hasMeaningfulReply(assistantMessage)) return false
    stageText.value = HTTP_FALLBACK_STAGE_TEXT
    const resultPayload = await httpFallback({
      ...payload,
      question: questionText,
      message: questionText,
      history
    })
    await applyChatResult(assistantMessage, resultPayload, onDone)
    return true
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
    } catch (error) {
      try {
        await runHttpFallback({ questionText, payload, history, assistantMessage, onDone })
      } catch (fallbackError) {
        applyFinalErrorFallback(assistantMessage)
        if (typeof onError === 'function') {
          onError({
            type: 'error',
            message: assistantMessage.content,
            error: fallbackError || error
          })
        }
      }
      loading.value = false
      await scrollToBottom()
      return assistantMessage
    }

    activeSocket.value = socket
    let settled = false
    let receivedChunk = false
    let handlingTransportFailure = false

    return new Promise((resolve) => {
      const finish = async () => {
        if (settled) return
        settled = true
        loading.value = false
        if (activeSocket.value === socket) activeSocket.value = null
        await scrollToBottom()
        resolve(assistantMessage)
      }

      const finishWithTransportFallback = async (fallbackMessage = FALLBACK_ERROR_TEXT, error = null) => {
        if (settled || handlingTransportFailure) return
        handlingTransportFailure = true
        try {
          if (activeSocket.value === socket) activeSocket.value = null
          try {
            socket.close()
          } catch {
            // WebSocket 已处于关闭态时无需额外处理。
          }
          if (!receivedChunk && !hasMeaningfulReply(assistantMessage)) {
            try {
              await runHttpFallback({ questionText, payload, history, assistantMessage, onDone })
            } catch (fallbackError) {
              applyFinalErrorFallback(assistantMessage, fallbackMessage)
              if (typeof onError === 'function') {
                onError({
                  type: 'error',
                  message: assistantMessage.content,
                  error: fallbackError || error
                })
              }
            }
          } else if (!hasMeaningfulReply(assistantMessage)) {
            applyErrorFallback(assistantMessage, fallbackMessage)
            if (typeof onError === 'function') onError({ type: 'error', message: assistantMessage.content || fallbackMessage, error })
          }
        } finally {
          await finish()
        }
      }

      socket.onopen = async () => {
        try {
          socket.send(JSON.stringify({
            ...payload,
            question: questionText,
            message: questionText,
            history
          }))
        } catch (error) {
          await finishWithTransportFallback(FALLBACK_ERROR_TEXT, error)
        }
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
          await finishWithTransportFallback(normalizeText(streamPayload.message) || FALLBACK_ERROR_TEXT, streamPayload)
        }
      }

      socket.onerror = async (event) => {
        await finishWithTransportFallback(FALLBACK_ERROR_TEXT, event)
      }

      socket.onclose = async (event) => {
        if (settled || handlingTransportFailure) return
        if (!receivedChunk && !hasMeaningfulReply(assistantMessage)) {
          await finishWithTransportFallback(normalizeText(event?.reason) || FALLBACK_ERROR_TEXT, event)
          return
        }
        await finish()
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

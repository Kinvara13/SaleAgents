import { ref, computed, nextTick, onMounted, onUnmounted, type Ref } from 'vue'
import { getChatHistory, sendChatStream, readChatStream, type ChatMessage, type SendChatOptions } from '../services/chat'

export type ChatState = 'idle' | 'waiting' | 'streaming' | 'confirmed' | 'done'

export interface UseLLMChatOptions {
  /** 项目 ID，有值时会自动加载历史并挂载项目上下文 */
  projectId?: string
  /** 自定义 API endpoint，默认使用项目聊天接口 */
  apiEndpoint?: string
  /** 额外请求头 */
  headers?: Record<string, string>
  /** 额外请求体 */
  body?: Record<string, unknown>
  /** 是否自动加载历史 */
  autoLoadHistory?: boolean
  /** 发生错误时回调 */
  onError?: (error: Error, lastUserMessage?: string) => void
  /** 流式输出完成时回调 */
  onComplete?: (assistantMsg: ChatMessage) => void
}

export interface UseLLMChatReturn {
  /** 消息列表 */
  messages: Ref<ChatMessage[]>
  /** 当前状态 */
  state: Ref<ChatState>
  /** 是否正在等待/流式输出中 */
  isLoading: Ref<boolean>
  /** 是否正在流式输出 */
  isStreaming: Ref<boolean>
  /** 状态文字标签 */
  stateLabel: Ref<string>
  /** 发送消息 */
  sendMessage: (text: string, override?: Partial<SendChatOptions>) => Promise<void>
  /** 重试上一条用户消息 */
  retryLastMessage: () => Promise<void>
  /** 清空消息 */
  clearMessages: () => void
  /** 加载历史记录 */
  loadHistory: () => Promise<void>
  /** 滚动到消息底部（调用方需传入容器元素） */
  scrollToBottom: (el?: HTMLElement | null) => Promise<void>
}

/** 自增 ID 计数器（模块级闭包，高并发安全） */
let _idSeq = 0
function makeId(prefix = 'msg'): string {
  return `${prefix}_${Date.now()}_${++_idSeq}`
}

/** 构建请求体 */
function buildRequestBody(
  baseBody: Record<string, unknown> | undefined,
  overrideBody: Record<string, unknown> | undefined,
  content: string
): Record<string, unknown> | undefined {
  if (baseBody && overrideBody) {
    return { ...baseBody, content, ...overrideBody }
  }
  if (baseBody) {
    return { ...baseBody, content }
  }
  if (overrideBody) {
    return { content, ...overrideBody }
  }
  return undefined
}

/**
 * 大模型对话 Composable
 *
 * 封装消息状态、SSE 流式请求、重试机制。
 * 支持项目聊天、通用对话、自定义 endpoint 三种模式。
 */
export function useLLMChat(options: UseLLMChatOptions = {}): UseLLMChatReturn {
  const messages = ref<ChatMessage[]>([])
  const state = ref<ChatState>('idle')
  const isLoading = ref(false)
  const isStreaming = ref(false)
  let _unmounted = false

  const stateLabel = computed(() => {
    switch (state.value) {
      case 'idle': return '就绪'
      case 'waiting': return '等待回复...'
      case 'streaming': return '流式输出中'
      case 'confirmed': return '已确认'
      case 'done': return '已完成'
      default: return ''
    }
  })

  /**
   * 发送消息
   * @param text 用户输入文本
   * @param override 临时覆盖选项（如 projectId、model 等）
   */
  async function sendMessage(text: string, override?: Partial<SendChatOptions>) {
    const trimmed = text.trim().slice(0, 2000)
    if (!trimmed || isLoading.value) return

    console.log('[useLLMChat] 发送消息:', trimmed)

    // 添加用户消息
    const userMsg: ChatMessage = {
      id: makeId('user'),
      role: 'user',
      content: trimmed,
      status: 'waiting',
    }
    messages.value.push(userMsg)
    state.value = 'waiting'
    isLoading.value = true
    isStreaming.value = false

    try {
      const streamOptions: SendChatOptions = {
        projectId: override?.projectId ?? options.projectId,
        endpoint: override?.endpoint ?? options.apiEndpoint,
        headers: { ...options.headers, ...override?.headers },
        body: buildRequestBody(options.body, override?.body, trimmed),
      }

      const { reader } = await sendChatStream(trimmed, streamOptions)

      // 创建助手消息
      const assistantMsg: ChatMessage = {
        id: makeId('assistant'),
        role: 'assistant',
        content: '',
        status: 'streaming',
      }
      messages.value.push(assistantMsg)
      
      // 更新用户消息状态 - 使用替换的方式确保响应式
      const userIndex = messages.value.findIndex(m => m.id === userMsg.id)
      if (userIndex !== -1) {
        messages.value[userIndex] = { ...userMsg, status: 'confirmed' }
      }
      
      state.value = 'streaming'
      isStreaming.value = true

      // 逐段读取
      await readChatStream(
        reader,
        (chunk) => {
          // 使用替换方式确保响应式更新
          const assistantIndex = messages.value.findIndex(m => m.id === assistantMsg.id)
          if (assistantIndex !== -1) {
            const currentMsg = messages.value[assistantIndex]
            messages.value[assistantIndex] = {
              ...currentMsg,
              content: currentMsg.content + chunk
            }
          }
        },
        () => {
          // 完成时更新状态
          const assistantIndex = messages.value.findIndex(m => m.id === assistantMsg.id)
          if (assistantIndex !== -1) {
            const currentMsg = messages.value[assistantIndex]
            messages.value[assistantIndex] = {
              ...currentMsg,
              status: 'confirmed'
            }
          }
          state.value = 'confirmed'
          isStreaming.value = false
        }
      )

      // 最终修整
      const finalIndex = messages.value.findIndex(m => m.id === assistantMsg.id)
      if (finalIndex !== -1) {
        const currentMsg = messages.value[finalIndex]
        const finalMsg = {
          ...currentMsg,
          content: currentMsg.content.trim()
        }
        messages.value[finalIndex] = finalMsg
        options.onComplete?.(finalMsg)
      }

      // 完成后重置状态为 idle
      console.log('[useLLMChat] 消息完成，重置状态为 idle')
      state.value = 'idle'
    } catch (e: any) {
      console.error('[useLLMChat] 发送失败:', e)
      messages.value.push({
        id: makeId('error'),
        role: 'assistant',
        content: '发送失败，请检查网络连接后重试',
        status: 'error',
      })
      state.value = 'idle'
      options.onError?.(e instanceof Error ? e : new Error(String(e)), userMsg.content)
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }

  /**
   * 重试上一条用户消息
   */
  async function retryLastMessage() {
    const lastUserIndex = messages.value.map(m => m.role).lastIndexOf('user')
    if (lastUserIndex === -1) return

    const userMsg = messages.value[lastUserIndex]
    // 删除该用户消息之后的所有消息（包含错误回复）
    messages.value = messages.value.slice(0, lastUserIndex + 1)
    await sendMessage(userMsg.content)
  }

  /**
   * 清空消息
   */
  function clearMessages() {
    messages.value = []
    state.value = 'idle'
    isLoading.value = false
    isStreaming.value = false
  }

  /**
   * 加载历史记录
   */
  async function loadHistory() {
    if (!options.projectId) return
    try {
      const history = await getChatHistory(options.projectId)
      if (_unmounted) return
      messages.value = history
      state.value = 'done'
    } catch (e) {
      if (_unmounted) return
      console.error('[useLLMChat] 加载历史失败:', e)
      messages.value = []
    }
  }

  /**
   * 滚动到底部
   */
  async function scrollToBottom(el?: HTMLElement | null) {
    await nextTick()
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  }

  // 在组件挂载时自动加载历史
  onMounted(() => {
    if (options.autoLoadHistory !== false && options.projectId) {
      loadHistory()
    }
  })

  onUnmounted(() => {
    _unmounted = true
  })

  return {
    messages,
    state,
    isLoading,
    isStreaming,
    stateLabel,
    sendMessage,
    retryLastMessage,
    clearMessages,
    loadHistory,
    scrollToBottom,
  }
}

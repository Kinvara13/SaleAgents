import { ref, computed, nextTick, type Ref } from 'vue'
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

  function makeId(prefix = 'msg'): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
  }

  /**
   * 发送消息
   * @param text 用户输入文本
   * @param override 临时覆盖选项（如 projectId、model 等）
   */
  async function sendMessage(text: string, override?: Partial<SendChatOptions>) {
    const trimmed = text.trim().slice(0, 2000)
    if (!trimmed || isLoading.value) return

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
        body: options.body
          ? { ...options.body, content: trimmed, ...override?.body }
          : override?.body
            ? { content: trimmed, ...override.body }
            : undefined,
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
      userMsg.status = 'confirmed'
      state.value = 'streaming'
      isStreaming.value = true

      // 逐段读取
      await readChatStream(
        reader,
        (chunk) => {
          assistantMsg.content += chunk
        },
        () => {
          assistantMsg.status = 'confirmed'
          state.value = 'confirmed'
          isStreaming.value = false
        }
      )

      assistantMsg.content = assistantMsg.content.trim()
      options.onComplete?.(assistantMsg)
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
      messages.value = history
      state.value = 'done'
    } catch (e) {
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

  // 自动加载历史
  if (options.autoLoadHistory !== false && options.projectId) {
    loadHistory()
  }

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

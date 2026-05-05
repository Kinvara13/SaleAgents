import api from './api'

/** 聊天消息 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  status?: 'idle' | 'waiting' | 'streaming' | 'confirmed' | 'done' | 'error'
  createdAt?: string
}

/** 发送聊天消息的选项 */
export interface SendChatOptions {
  projectId?: string
  endpoint?: string
  headers?: Record<string, string>
  body?: Record<string, unknown>
}

/**
 * 获取聊天历史记录
 * @param projectId 项目 ID
 * @returns 消息列表
 */
export async function getChatHistory(projectId: string): Promise<ChatMessage[]> {
  const res = await api.get(`/chat/${projectId}/history`)
  const history = res.data || []
  return history.map((m: any) => ({
    id: m.id || `hist_${Math.random().toString(36).slice(2, 9)}`,
    role: m.role,
    content: m.content || '',
    status: 'confirmed' as const,
    createdAt: m.created_at,
  }))
}

/**
 * 发送 SSE 流式聊天请求，返回 ReadableStream 的 reader
 *
 * @param content 用户输入内容
 * @param options 选项
 * @returns reader + response，供调用方逐段读取
 */
export async function sendChatStream(
  content: string,
  options: SendChatOptions = {}
): Promise<{ reader: ReadableStreamDefaultReader<Uint8Array>; response: Response }> {
  const baseUrl = import.meta.env.VITE_API_BASE || ''
  const token = localStorage.getItem('sa_token')

  const projectId = options.projectId
  const endpoint = options.endpoint || (projectId ? `/api/v1/chat/${projectId}/message` : '/api/v1/chat/message')
  const url = `${baseUrl}${endpoint}`

  const body = options.body || { content }

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers,
    },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: 发送失败`)
  }

  const reader = res.body?.getReader()
  if (!reader) {
    throw new Error('无法读取流')
  }

  return { reader, response: res }
}

/**
 * 逐段解析 SSE 流数据
 *
 * @param reader fetch 返回的 reader
 * @param onChunk 每收到一段内容时的回调
 * @param onDone 流结束时的回调
 */
export async function readChatStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onChunk?: (text: string) => void,
  onDone?: () => void
): Promise<string> {
  const decoder = new TextDecoder()
  let buffer = ''
  let fullText = ''
  let isDone = false

  console.log('[readChatStream] 开始读取流')

  while (!isDone) {
    const { done, value } = await reader.read()
    
    if (done) {
      console.log('[readChatStream] 流完成')
      isDone = true
      break
    }

    const decoded = decoder.decode(value, { stream: true })
    buffer += decoded
    console.log('[readChatStream] 收到数据:', decoded)

    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      const data = line.replace(/^data: /, '').trim()
      
      if (data === '[DONE]') {
        console.log('[readChatStream] 收到 DONE 标记')
        isDone = true
        continue
      }
      
      if (data) {
        try {
          const parsed = JSON.parse(data)
          const text = parsed.content || ''
          if (text) {
            console.log('[readChatStream] 解析到内容:', text)
            fullText += text
            onChunk?.(text)
          }
        } catch (e) {
          console.error('[readChatStream] 解析失败:', e, data)
          // 如果不是 JSON，可能是纯文本
          if (data && !data.startsWith('{') && !data.startsWith('[')) {
            fullText += data
            onChunk?.(data)
          }
        }
      }
    }
  }

  console.log('[readChatStream] 完成，总文本:', fullText)
  onDone?.()
  return fullText.trim()
}

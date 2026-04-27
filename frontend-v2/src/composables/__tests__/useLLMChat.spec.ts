import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent, h, nextTick } from 'vue'
import { useLLMChat } from '../useLLMChat'
import { getChatHistory, sendChatStream, readChatStream } from '../../services/chat'

vi.mock('../../services/chat', () => ({
  getChatHistory: vi.fn(),
  sendChatStream: vi.fn(),
  readChatStream: vi.fn(),
}))

function withComposable(options: Parameters<typeof useLLMChat>[0] = {}) {
  let result!: ReturnType<typeof useLLMChat>
  const Comp = defineComponent({
    setup() {
      result = useLLMChat(options)
      return {}
    },
    render() {
      return h('div')
    },
  })
  const wrapper = mount(Comp)
  return { result, wrapper }
}

describe('useLLMChat', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('sendMessage', () => {
    it('adds user message and assistant response on success', async () => {
      const onComplete = vi.fn()
      const { result } = withComposable({ onComplete })

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockImplementation(async (_reader, onChunk, onDone) => {
        onChunk?.('Hi')
        onChunk?.(' there')
        onDone?.()
        return 'Hi there'
      })

      await result.sendMessage('hello')

      expect(result.messages.value).toHaveLength(2)
      expect(result.messages.value[0]).toMatchObject({
        role: 'user',
        content: 'hello',
        status: 'confirmed',
      })
      expect(result.messages.value[1]).toMatchObject({
        role: 'assistant',
        content: 'Hi there',
        status: 'confirmed',
      })
      expect(result.state.value).toBe('confirmed')
      expect(result.isLoading.value).toBe(false)
      expect(result.isStreaming.value).toBe(false)
      expect(onComplete).toHaveBeenCalledWith(
        expect.objectContaining({ role: 'assistant', content: 'Hi there' })
      )
    })

    it('adds error message on failure', async () => {
      const onError = vi.fn()
      const { result } = withComposable({ onError })

      vi.mocked(sendChatStream).mockRejectedValue(new Error('Network down'))

      await result.sendMessage('hello')

      expect(result.messages.value).toHaveLength(2)
      expect(result.messages.value[1]).toMatchObject({
        role: 'assistant',
        content: '\u53d1\u9001\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u8fde\u63a5\u540e\u91cd\u8bd5',
        status: 'error',
      })
      expect(result.state.value).toBe('idle')
      expect(result.isLoading.value).toBe(false)
      expect(onError).toHaveBeenCalledWith(expect.any(Error), 'hello')
    })

    it('does nothing when text is empty', async () => {
      const { result } = withComposable()
      await result.sendMessage('   ')
      expect(result.messages.value).toHaveLength(0)
    })

    it('does nothing when already loading', async () => {
      const { result } = withComposable()

      vi.mocked(sendChatStream).mockImplementation(() => new Promise(() => {}))

      result.sendMessage('first')
      await nextTick()

      expect(result.isLoading.value).toBe(true)
      expect(result.messages.value).toHaveLength(1)

      await result.sendMessage('second')
      expect(result.messages.value).toHaveLength(1)
    })

    it('trims text to 2000 chars', async () => {
      const longText = 'a'.repeat(3000)
      const { result } = withComposable()

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockResolvedValue('ok')

      await result.sendMessage(longText)

      expect(result.messages.value[0].content).toHaveLength(2000)
      expect(sendChatStream).toHaveBeenCalledWith('a'.repeat(2000), expect.any(Object))
    })

    it('passes override options to sendChatStream', async () => {
      const { result } = withComposable({
        apiEndpoint: '/base',
        headers: { 'X-Base': '1' },
        body: { model: 'gpt-4' },
      })

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockImplementation(async (_reader, _onChunk, onDone) => {
        onDone?.()
        return 'ok'
      })

      await result.sendMessage('hello', {
        projectId: 'override-proj',
        endpoint: '/override',
        headers: { 'X-Override': '2' },
        body: { temperature: 0.5 },
      })

      expect(sendChatStream).toHaveBeenCalledWith(
        'hello',
        expect.objectContaining({
          projectId: 'override-proj',
          endpoint: '/override',
          headers: expect.objectContaining({ 'X-Base': '1', 'X-Override': '2' }),
          body: expect.objectContaining({ model: 'gpt-4', temperature: 0.5, content: 'hello' }),
        })
      )
    })
  })

  describe('retryLastMessage', () => {
    it('truncates after last user message and retries', async () => {
      const { result } = withComposable()

      vi.mocked(sendChatStream).mockRejectedValue(new Error('fail'))
      await result.sendMessage('hello')
      expect(result.messages.value).toHaveLength(2)
      expect(result.messages.value[1].status).toBe('error')

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockImplementation(async (_reader, onChunk, onDone) => {
        onChunk?.('Retry ok')
        onDone?.()
        return 'Retry ok'
      })

      await result.retryLastMessage()

      expect(result.messages.value).toHaveLength(3)
      expect(result.messages.value[2]).toMatchObject({
        content: 'Retry ok',
        status: 'confirmed',
      })
    })

    it('does nothing when no user message exists', async () => {
      const { result } = withComposable()
      await result.retryLastMessage()
      expect(result.messages.value).toHaveLength(0)
    })
  })

  describe('clearMessages', () => {
    it('resets everything', async () => {
      const { result } = withComposable()

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockResolvedValue('ok')

      await result.sendMessage('hello')
      expect(result.messages.value.length).toBeGreaterThan(0)

      result.clearMessages()
      expect(result.messages.value).toHaveLength(0)
      expect(result.state.value).toBe('idle')
      expect(result.isLoading.value).toBe(false)
      expect(result.isStreaming.value).toBe(false)
    })
  })

  describe('loadHistory', () => {
    it('loads history on mount when projectId is provided', async () => {
      vi.mocked(getChatHistory).mockResolvedValue([
        { id: '1', role: 'user', content: 'Hist', status: 'confirmed' },
      ])

      const { result } = withComposable({ projectId: 'proj-1' })
      await flushPromises()

      expect(getChatHistory).toHaveBeenCalledWith('proj-1')
      expect(result.messages.value).toHaveLength(1)
      expect(result.state.value).toBe('done')
    })

    it('does not auto-load when autoLoadHistory is false', async () => {
      vi.mocked(getChatHistory).mockResolvedValue([])

      withComposable({ projectId: 'proj-1', autoLoadHistory: false })
      await flushPromises()

      expect(getChatHistory).not.toHaveBeenCalled()
    })

    it('does not update messages after unmount', async () => {
      vi.mocked(getChatHistory).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve([]), 50))
      )

      const { wrapper, result } = withComposable({ projectId: 'proj-1' })
      wrapper.unmount()

      await flushPromises()

      expect(result.messages.value).toHaveLength(0)
    })

    it('handles loadHistory error gracefully', async () => {
      vi.mocked(getChatHistory).mockRejectedValue(new Error('fail'))

      const { result } = withComposable({ projectId: 'proj-1' })
      await flushPromises()

      expect(result.messages.value).toHaveLength(0)
    })
  })

  describe('scrollToBottom', () => {
    it('scrolls element to bottom', async () => {
      const { result } = withComposable()
      const el = document.createElement('div')
      Object.defineProperty(el, 'scrollHeight', { value: 200, writable: true })
      await result.scrollToBottom(el)
      expect(el.scrollTop).toBe(200)
    })
  })

  describe('stateLabel', () => {
    it('reflects current state', async () => {
      const { result } = withComposable()

      expect(result.stateLabel.value).toBe('\u5c31\u7eea')

      vi.mocked(sendChatStream).mockRejectedValue(new Error('err'))
      await result.sendMessage('test')
      expect(result.stateLabel.value).toBe('\u5c31\u7eea')

      vi.mocked(sendChatStream).mockResolvedValue({
        reader: {} as ReadableStreamDefaultReader<Uint8Array>,
        response: {} as Response,
      })
      vi.mocked(readChatStream).mockImplementation(async (_reader, _onChunk, onDone) => {
        onDone?.()
        return 'ok'
      })

      await result.sendMessage('test2')
      expect(result.stateLabel.value).toBe('\u5df2\u786e\u8ba4')
    })
  })
})

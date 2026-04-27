import { describe, it, expect, vi, beforeEach, afterEach, type MockedFunction } from 'vitest'
import { getChatHistory, sendChatStream, readChatStream } from '../chat'
import api from '../api'

vi.mock('../api', () => ({
  default: {
    get: vi.fn(),
  },
}))

function encode(text: string): Uint8Array {
  return new TextEncoder().encode(text)
}

function createMockReader(chunks: Uint8Array[]) {
  let i = 0
  return {
    read: vi.fn(async () => {
      if (i < chunks.length) {
        return { done: false, value: chunks[i++] }
      }
      return { done: true, value: undefined }
    }),
    releaseLock: vi.fn(),
    cancel: vi.fn(),
  } as unknown as ReadableStreamDefaultReader<Uint8Array>
}

describe('getChatHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns mapped messages on success', async () => {
    const mockGet = api.get as MockedFunction<typeof api.get>
    mockGet.mockResolvedValue({
      data: [
        { id: '1', role: 'user', content: 'Hello', created_at: '2024-01-01' },
        { id: '2', role: 'assistant', content: 'Hi', created_at: '2024-01-02' },
      ],
    })

    const result = await getChatHistory('proj-123')
    expect(mockGet).toHaveBeenCalledWith('/chat/proj-123/history')
    expect(result).toHaveLength(2)
    expect(result[0]).toMatchObject({
      id: '1',
      role: 'user',
      content: 'Hello',
      status: 'confirmed',
      createdAt: '2024-01-01',
    })
    expect(result[1]).toMatchObject({
      id: '2',
      role: 'assistant',
      content: 'Hi',
      status: 'confirmed',
      createdAt: '2024-01-02',
    })
  })

  it('generates fallback ids when missing', async () => {
    const mockGet = api.get as MockedFunction<typeof api.get>
    mockGet.mockResolvedValue({
      data: [{ role: 'user', content: 'Test' }],
    })

    const result = await getChatHistory('proj-456')
    expect(result[0].id).toMatch(/^hist_/)
    expect(result[0].content).toBe('Test')
  })

  it('throws when api fails', async () => {
    const mockGet = api.get as MockedFunction<typeof api.get>
    mockGet.mockRejectedValue(new Error('Network error'))

    await expect(getChatHistory('proj-789')).rejects.toThrow('Network error')
  })
})

describe('sendChatStream', () => {
  const originalFetch = globalThis.fetch
  let fetchMock: MockedFunction<typeof fetch>

  beforeEach(() => {
    fetchMock = vi.fn()
    globalThis.fetch = fetchMock
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => 'test-token'),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    })
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
    vi.unstubAllGlobals()
  })

  it('returns reader and response on success', async () => {
    const mockReader = createMockReader([])
    const mockResponse = {
      ok: true,
      status: 200,
      body: {
        getReader: () => mockReader,
      },
    } as unknown as Response

    fetchMock.mockResolvedValue(mockResponse)

    const result = await sendChatStream('hello', { projectId: 'proj-1' })
    expect(result.reader).toBe(mockReader)
    expect(result.response).toBe(mockResponse)

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/chat/proj-1/message',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        }),
        body: expect.any(String),
      })
    )
  })

  it('uses default endpoint without projectId', async () => {
    const mockReader = createMockReader([])
    const mockResponse = {
      ok: true,
      status: 200,
      body: {
        getReader: () => mockReader,
      },
    } as unknown as Response

    fetchMock.mockResolvedValue(mockResponse)

    await sendChatStream('hello')
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/chat/message',
      expect.any(Object)
    )
  })

  it('uses custom endpoint and headers', async () => {
    const mockReader = createMockReader([])
    const mockResponse = {
      ok: true,
      status: 200,
      body: {
        getReader: () => mockReader,
      },
    } as unknown as Response

    fetchMock.mockResolvedValue(mockResponse)

    await sendChatStream('hello', {
      endpoint: '/custom/chat',
      headers: { 'X-Custom': 'value' },
    })

    const callArgs = fetchMock.mock.calls[0][1] as RequestInit
    expect(callArgs.headers).toMatchObject({
      'X-Custom': 'value',
    })
    expect(fetchMock).toHaveBeenCalledWith(
      '/custom/chat',
      expect.any(Object)
    )
  })

  it('throws on non-ok response', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
    } as Response)

    await expect(sendChatStream('hello')).rejects.toThrow('HTTP 500: 发送失败')
  })

  it('throws when body is missing', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      body: null,
    } as unknown as Response)

    await expect(sendChatStream('hello')).rejects.toThrow('无法读取流')
  })
})

describe('readChatStream', () => {
  it('parses SSE chunks and calls callbacks', async () => {
    const chunks = [
      encode('data: Hello\n\ndata: World\n\n'),
      encode('data: !\n\n'),
    ]
    const reader = createMockReader(chunks)
    const onChunk = vi.fn()
    const onDone = vi.fn()

    const result = await readChatStream(reader, onChunk, onDone)
    expect(result).toBe('HelloWorld!')
    expect(onChunk).toHaveBeenCalledTimes(3)
    expect(onChunk).toHaveBeenNthCalledWith(1, 'Hello')
    expect(onChunk).toHaveBeenNthCalledWith(2, 'World')
    expect(onChunk).toHaveBeenNthCalledWith(3, '!')
    expect(onDone).toHaveBeenCalled()
  })

  it('ignores [DONE] markers', async () => {
    const chunks = [
      encode('data: partial\n\ndata: [DONE]\n\n'),
    ]
    const reader = createMockReader(chunks)
    const onChunk = vi.fn()

    const result = await readChatStream(reader, onChunk)
    expect(result).toBe('partial')
    expect(onChunk).toHaveBeenCalledTimes(1)
    expect(onChunk).toHaveBeenCalledWith('partial')
  })

  it('handles empty stream', async () => {
    const reader = createMockReader([])
    const onChunk = vi.fn()
    const onDone = vi.fn()

    const result = await readChatStream(reader, onChunk, onDone)
    expect(result).toBe('')
    expect(onChunk).not.toHaveBeenCalled()
    expect(onDone).toHaveBeenCalled()
  })

  it('handles split across multiple chunks with leftover buffer', async () => {
    const chunks = [
      encode('data: Hel'),
      encode('lo\n\ndata: Wor'),
      encode('ld\n\n'),
    ]
    const reader = createMockReader(chunks)
    const onChunk = vi.fn()

    const result = await readChatStream(reader, onChunk)
    expect(result).toBe('HelloWorld')
    expect(onChunk).toHaveBeenCalledTimes(2)
  })
})

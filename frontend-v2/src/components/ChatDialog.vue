<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="flex-shrink-0 flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <span class="text-lg">💬</span>
        <span class="font-medium text-gray-700 text-sm">AI 助手</span>
        <span v-if="projectId" class="text-xs text-gray-400">项目对话</span>
      </div>
      <div class="flex items-center space-x-2">
        <button
          v-if="messages.length > 0"
          class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          @click="clearHistory"
        >
          清空记录
        </button>
        <button
          class="text-gray-400 hover:text-gray-500 transition-colors text-xs"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>
    </div>

    <!-- Messages area -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center text-gray-400">
          <div class="text-3xl mb-2">🤖</div>
          <p class="text-sm">发送消息开始对话</p>
        </div>
      </div>

      <!-- Message bubbles -->
      <div
        v-for="msg in messages"
        :key="msg.id"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap leading-relaxed"
          :class="msg.role === 'user'
            ? 'bg-primary text-white rounded-br-sm'
            : 'bg-gray-100 text-gray-800 rounded-bl-sm'"
          style="font-family: system-ui, sans-serif;"
        >
          <span v-if="msg.role === 'assistant' && msg.status === 'streaming'" class="streaming-dots">...</span>
          <template v-else>{{ msg.content }}</template>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isStreaming" class="flex justify-start">
        <div class="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-2.5">
          <div class="flex space-x-1">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input area -->
    <div class="flex-shrink-0 flex items-end space-x-2">
      <textarea
        ref="inputEl"
        v-model="inputText"
        @keydown.enter.exact.prevent="sendMessage"
        @keydown.enter.shift="inputText += '\n'"
        :disabled="isStreaming"
        placeholder="输入问题，按 Enter 发送..."
        rows="2"
        class="flex-1 resize-none px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all disabled:bg-gray-50"
        style="font-family: system-ui, sans-serif;"
      ></textarea>
      <button
        @click="sendMessage"
        :disabled="!inputText.trim() || isStreaming"
        class="mb-0.5 px-3 py-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-sm"
      >
        发送
      </button>
    </div>

    <!-- State indicator -->
    <div class="flex-shrink-0 flex items-center justify-between mt-1.5 text-xs text-gray-400">
      <span>{{ stateLabel }}</span>
      <span v-if="isStreaming" class="text-primary">流式输出中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  status?: 'idle' | 'waiting' | 'streaming' | 'confirmed' | 'done'
  created_at?: string
}

const props = defineProps<{
  projectId: string
}>()

const emit = defineEmits<{
  close: []
}>()

const messagesEl = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLTextAreaElement | null>(null)
const inputText = ref('')
const isStreaming = ref(false)
const currentStreamText = ref('')
const state = ref<'idle' | 'waiting' | 'streaming' | 'confirmed' | 'done'>('idle')

const messages = ref<ChatMessage[]>([])

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

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  const userMsg: ChatMessage = {
    id: `temp_${Date.now()}`,
    role: 'user',
    content: text,
    status: 'idle',
  }
  messages.value.push(userMsg)
  inputText.value = ''
  state.value = 'waiting'
  isStreaming.value = true
  currentStreamText.value = ''

  await scrollToBottom()

  try {
    const res = await fetch(
      `http://localhost:8000/api/v1/chat/${props.projectId}/message`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text }),
      }
    )

    if (!res.ok) throw new Error('发送失败')

    const reader = res.body?.getReader()
    const decoder = new TextDecoder()

    const assistantMsg: ChatMessage = {
      id: `temp_${Date.now()}_a`,
      role: 'assistant',
      content: '',
      status: 'streaming',
    }
    messages.value.push(assistantMsg)
    state.value = 'streaming'

    if (reader) {
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          const data = line.replace(/^data: /, '').trim()
          if (data && data !== '[DONE]') {
            assistantMsg.content += data
            await nextTick()
            await scrollToBottom()
          }
        }
      }
      assistantMsg.content = assistantMsg.content.trim()
      assistantMsg.status = 'confirmed'
      state.value = 'confirmed'
    }
  } catch (e) {
    console.error('Chat error:', e)
    // Remove the last user msg on error
    messages.value.pop()
    state.value = 'idle'
  } finally {
    isStreaming.value = false
    await nextTick()
    await scrollToBottom()
    inputEl.value?.focus()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function loadHistory() {
  try {
    const res = await fetch(
      `http://localhost:8000/api/v1/chat/${props.projectId}/history`
    )
    if (res.ok) {
      const history = await res.json()
      messages.value = history.map((m: any) => ({
        ...m,
        status: 'confirmed',
      }))
    }
  } catch (e) {
    console.error('Load history failed:', e)
  }
}

function clearHistory() {
  messages.value = []
  state.value = 'idle'
}

onMounted(() => {
  loadHistory()
  inputEl.value?.focus()
})
</script>

<style scoped>
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-4px); }
}
.animate-bounce {
  animation: bounce 1s infinite;
}
.streaming-dots {
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
</style>

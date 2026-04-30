<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div v-if="showHeader" class="flex-shrink-0 flex items-center justify-between mb-3">
      <div class="flex items-center space-x-2">
        <slot name="header-icon">
          <span class="text-lg">💬</span>
        </slot>
        <span class="font-medium text-gray-700 text-sm">{{ title }}</span>
        <span v-if="projectId" class="text-xs text-gray-400">项目对话</span>
      </div>
      <div class="flex items-center space-x-2">
        <button
          v-if="messages.length > 0 && showClear"
          class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          @click="clearMessages"
        >
          清空记录
        </button>
        <slot name="header-extra" />
      </div>
    </div>

    <!-- Messages area -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center text-gray-400">
          <div class="text-3xl mb-2">{{ emptyIcon }}</div>
          <p class="text-sm">{{ emptyText }}</p>
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
            : msg.status === 'error'
              ? 'bg-red-50 text-red-700 border border-red-100 rounded-bl-sm'
              : 'bg-gray-100 text-gray-800 rounded-bl-sm'"
          style="font-family: system-ui, sans-serif;"
        >
          <template v-if="msg.role === 'assistant' && msg.status === 'streaming' && !msg.content">
            <span class="streaming-dots">...</span>
          </template>
          <template v-else-if="msg.status === 'error'">
            <div class="flex items-center flex-wrap gap-2">
              <span>⚠️ {{ msg.content }}</span>
              <button
                class="text-xs underline hover:text-red-800 transition-colors"
                @click="retryLastMessage"
              >
                重试
              </button>
            </div>
          </template>
          <template v-else-if="msg.role === 'user'">
            {{ msg.content }}
            <span
              v-if="msg.status === 'waiting'"
              class="ml-1 inline-block w-1.5 h-1.5 bg-white/70 rounded-full animate-pulse"
            />
          </template>
          <template v-else>
            {{ msg.content }}
          </template>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="state === 'waiting'" class="flex justify-start">
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
      <slot name="input-prefix" />
      <textarea
        ref="inputEl"
        v-model="inputText"
        @keydown.enter.exact.prevent="handleSend"
        @keydown.enter.shift="inputText += '\n'"
        :disabled="isLoading"
        :placeholder="placeholder"
        :rows="inputRows"
        class="flex-1 resize-none px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all disabled:bg-gray-50"
        style="font-family: system-ui, sans-serif;"
      ></textarea>
      <button
        @click="handleSend"
        :disabled="!inputText.trim() || isLoading"
        class="mb-0.5 px-3 py-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-sm"
      >
        {{ sendText }}
      </button>
    </div>

    <slot name="input-suffix" />

    <!-- State indicator -->
    <div v-if="showState" class="flex-shrink-0 flex items-center justify-between mt-1.5 text-xs text-gray-400">
      <span>{{ stateLabel }}</span>
      <span v-if="state === 'waiting' || state === 'streaming'" class="text-primary">AI 正在输入...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useLLMChat, type UseLLMChatOptions } from '../composables/useLLMChat'

interface Props extends /* @vue-ignore */ UseLLMChatOptions {
  title?: string
  emptyText?: string
  emptyIcon?: string
  placeholder?: string
  sendText?: string
  showHeader?: boolean
  showClear?: boolean
  showState?: boolean
  inputRows?: number
  autoFocus?: boolean
  /** @vue-ignore 显式声明避免模板访问警告 */
  projectId?: string
  apiEndpoint?: string
  headers?: Record<string, string>
  body?: Record<string, unknown>
  autoLoadHistory?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'AI 助手',
  emptyText: '发送消息开始对话',
  emptyIcon: '🤖',
  placeholder: '输入问题，按 Enter 发送...',
  sendText: '发送',
  showHeader: true,
  showClear: true,
  showState: true,
  inputRows: 2,
  autoFocus: true,
  autoLoadHistory: true,
})

const emit = defineEmits<{
  send: [text: string]
  complete: [message: string]
  error: [error: Error]
}>()

const messagesEl = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLTextAreaElement | null>(null)
const inputText = ref('')

const {
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
} = useLLMChat({
  projectId: props.projectId,
  apiEndpoint: props.apiEndpoint,
  headers: props.headers,
  body: props.body,
  autoLoadHistory: props.autoLoadHistory,
  onError: (err) => {
    emit('error', err)
  },
  onComplete: (msg) => {
    emit('complete', msg.content)
  },
})

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isLoading.value) return

  emit('send', text)
  inputText.value = ''
  await sendMessage(text, { body: props.body })
  await scrollToBottom(messagesEl.value)
}

// 发送/流式输出时自动滚动
watch(
  () => messages.value.length,
  async () => {
    await scrollToBottom(messagesEl.value)
  }
)

watch(isStreaming, async () => {
  await scrollToBottom(messagesEl.value)
})

onMounted(() => {
  if (props.autoFocus) {
    inputEl.value?.focus()
  }
})

// 暴露方法供父组件调用
defineExpose({
  messages,
  sendMessage,
  clearMessages,
  loadHistory,
  isLoading,
  setInputText: (text: string) => { inputText.value = text },
  focusInput: () => { inputEl.value?.focus() },
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

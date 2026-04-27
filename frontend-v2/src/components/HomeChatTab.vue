<template>
  <div class="space-y-4">
    <!-- 消息展示区 -->
    <div
      v-if="chat.messages.length > 0"
      ref="msgBox"
      class="bg-white rounded-lg border border-gray-200 p-4 max-h-[420px] overflow-y-auto space-y-3"
    >
      <div
        v-for="msg in chat.messages"
        :key="msg.id"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div
          class="max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed break-words"
          :class="msg.role === 'user'
            ? 'bg-primary text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'"
        >
          {{ msg.content }}
        </div>
      </div>
      <div v-if="chat.isLoading && !chat.isStreaming" class="flex justify-start">
        <div class="bg-gray-100 text-gray-500 rounded-lg rounded-bl-none px-4 py-2 text-sm flex items-center gap-2">
          <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
          <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
          <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
        </div>
      </div>
    </div>

    <div class="bg-gray-50 rounded-lg p-4">
      <!-- 输入区域 -->
      <div class="border border-gray-200 rounded-lg p-4 bg-white">
        <textarea
          :value="input"
          class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
          rows="4"
          :placeholder="placeholder"
          @input="onInput"
          @keydown.enter.prevent="handleEnter"
        ></textarea>

        <!-- 上传文件回显 -->
        <div v-if="uploadedFiles.length > 0" class="mt-3">
          <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
            <span class="text-sm text-gray-700">{{ file.name }}</span>
            <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
          </div>
        </div>

        <input
          type="file"
          ref="fileInput"
          class="hidden"
          multiple
          @change="handleFileUpload"
        />

        <!-- 底部控制栏 -->
        <div class="flex flex-wrap gap-3 mt-3 justify-end items-center">
          <select
            :value="projectId"
            class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
            style="width: 200px"
            @change="onProjectChange"
          >
            <option value="">请选择项目</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>

          <select
            :value="model"
            class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
            style="width: 100px"
            @change="onModelChange"
          >
            <option value="gpt-4">GPT-4</option>
            <option value="claude-3">Claude-3</option>
            <option value="gpt-3.5">GPT-3.5</option>
            <option value="custom">自定义</option>
          </select>

          <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 32px" @click="openFileUpload">
            上传文件
          </button>

          <button
            class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            style="height: 32px"
            :disabled="chat.isLoading || !input.trim()"
            @click="handleSend"
          >
            {{ chat.isLoading ? chat.stateLabel : '发送' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { UseLLMChatReturn } from '../composables/useLLMChat'
import type { Project } from '../types'

const props = defineProps<{
  chat: UseLLMChatReturn
  input: string
  projectId: string
  model: string
  projects: Project[]
  uploadedFiles: Array<{ name: string; size: number; type: string }>
  placeholder: string
}>()

const emit = defineEmits<{
  'update:input': [value: string]
  'update:projectId': [value: string]
  'update:model': [value: string]
  'send': []
  'file-upload': [event: Event]
  'open-file-upload': []
  'remove-file': [index: number]
}>()

const msgBox = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const onInput = (e: Event) => {
  emit('update:input', (e.target as HTMLTextAreaElement).value)
}

const onProjectChange = (e: Event) => {
  emit('update:projectId', (e.target as HTMLSelectElement).value)
}

const onModelChange = (e: Event) => {
  emit('update:model', (e.target as HTMLSelectElement).value)
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    handleSend()
  }
}

const handleSend = () => {
  emit('send')
}

const openFileUpload = () => {
  fileInput.value?.click()
  emit('open-file-upload')
}

const handleFileUpload = (event: Event) => {
  emit('file-upload', event)
}

const removeFile = (index: number) => {
  emit('remove-file', index)
}

// 消息数量变化时自动滚动到底部
watch(() => props.chat.messages.value.length, () => {
  nextTick(() => {
    if (msgBox.value) {
      msgBox.value.scrollTop = msgBox.value.scrollHeight
    }
  })
})
</script>

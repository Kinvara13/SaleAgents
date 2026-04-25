<template>
  <LLMChatPanel
    v-bind="$props"
    title="AI 助手"
    @send="$emit('send', $event)"
    @complete="$emit('complete', $event)"
    @error="$emit('error', $event)"
  >
    <template #header-extra>
      <button
        class="text-gray-400 hover:text-gray-500 transition-colors text-xs"
        @click="$emit('close')"
      >
        ✕
      </button>
    </template>
  </LLMChatPanel>
</template>

<script setup lang="ts">
import LLMChatPanel from './LLMChatPanel.vue'
import type { UseLLMChatOptions } from '../composables/useLLMChat'

interface Props extends UseLLMChatOptions {}

defineProps<Props>()

defineEmits<{
  close: []
  send: [text: string]
  complete: [message: string]
  error: [error: Error]
}>()
</script>

<template>
  <div class="fade-in">
    <!-- Page header -->
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-800">系统日志</h2>
      <button
        class="flex items-center space-x-2 px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50"
        :disabled="loading"
        @click="refreshLogs"
      >
        <svg v-if="loading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span v-else>刷新</span>
      </button>
    </div>

    <!-- Log type tabs -->
    <div class="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
      <button
        v-for="tab in logTabs"
        :key="tab.value"
        class="px-4 py-1.5 text-sm rounded-md transition-all"
        :class="activeTab === tab.value ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = tab.value; loadLogs()"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Log display area -->
    <div
      class="bg-gray-900 rounded-xl p-4 max-h-[600px] overflow-auto font-mono text-sm"
      ref="logContainer"
    >
      <div v-if="loading && !backendLog && !frontendLog" class="text-gray-400 text-center py-8">
        <span class="inline-flex items-center space-x-2">
          <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>加载中...</span>
        </span>
      </div>
      <pre v-else class="text-green-400 whitespace-pre-wrap">{{ currentLog }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '../services/api'

const activeTab = ref('all')
const backendLog = ref('')
const frontendLog = ref('')
const loading = ref(false)
const logContainer = ref<HTMLElement | null>(null)

const logTabs = [
  { label: '全部', value: 'all' },
  { label: '后端日志', value: 'backend' },
  { label: '前端日志', value: 'frontend' },
]

const currentLog = computed(() => {
  if (activeTab.value === 'backend') return backendLog.value
  if (activeTab.value === 'frontend') return frontendLog.value
  return `=== 后端日志 ===\n${backendLog.value}\n\n=== 前端日志 ===\n${frontendLog.value}`
})

async function loadLogs() {
  loading.value = true
  try {
    const params = { log_type: activeTab.value, lines: 500 }
    const res = await api.get('/system/logs', { params })
    backendLog.value = res.data?.backend || '暂无后端日志'
    frontendLog.value = res.data?.frontend || '暂无前端日志'
  } catch (e) {
    console.error('Failed to load logs:', e)
    backendLog.value = '加载后端日志失败'
    frontendLog.value = '加载前端日志失败'
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function refreshLogs() {
  loadLogs()
}

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

onMounted(loadLogs)
</script>

<style scoped>
.fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>
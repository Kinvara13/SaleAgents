<template>
  <div class="fade-in">
    <!-- 通知提示 -->
    <div v-if="showToast" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg text-sm font-medium transition-all duration-300" :class="uploadStatus === 'failed' ? 'bg-red-500 text-white' : uploadStatus === 'completed' ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'">
      {{ toastMessage }}
    </div>

    <!-- 页面标题 -->
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-800">标前评估</h2>
      <p v-if="currentJob" class="text-sm text-gray-500">
        当前文件：{{ currentJob.file_name }}
      </p>
    </div>

    <!-- 上传区域 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">上传标书要求文件</h2>

      <!-- 未上传状态 -->
      <div v-if="uploadStatus === 'idle'" class="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center bg-primary/5 transition-all duration-300 hover:border-primary/50">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">📄</span>
          <p class="text-gray-600 mb-2">点击或拖拽文件到此处上传</p>
          <p class="text-sm text-gray-400 mb-6">支持 PDF、Word（.docx）、Excel（.xlsx）、ZIP 格式</p>
          <input type="file" class="hidden" id="file-upload" accept=".pdf,.docx,.xlsx,.xls,.zip,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/zip" @change="handleFileUpload" />
          <label for="file-upload" class="px-6 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 cursor-pointer">
            选择文件
          </label>
        </div>
      </div>

      <!-- 上传/解析中状态 -->
      <div v-else-if="uploadStatus === 'uploading' || uploadStatus === 'analyzing'" class="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center bg-primary/5">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">{{ uploadStatus === 'uploading' ? '⏳' : '🔍' }}</span>
          <p class="text-gray-600 mb-2">{{ uploadStatus === 'uploading' ? '正在上传文件...' : '正在解析并分析文件...' }}</p>
          <p class="text-sm text-gray-400 mt-2">{{ uploadStatus === 'analyzing' ? '正在提取评审办法、技术评审表和星标项...' : '' }}</p>
          <div class="w-full max-w-md mt-4">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-2 bg-primary rounded-full animate-pulse" :style="{ width: uploadStatus === 'uploading' ? '60%' : '90%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 失败状态 -->
      <div v-else-if="uploadStatus === 'failed'" class="border-2 border-dashed border-red-300 rounded-lg p-8 text-center bg-red-50">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">❌</span>
          <p class="text-red-600 mb-2">处理失败</p>
          <p class="text-sm text-red-400 mb-6">{{ errorMessage }}</p>
          <button class="px-6 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" @click="resetUpload">
            重新上传
          </button>
        </div>
      </div>

      <!-- 完成状态 -->
      <div v-else-if="uploadStatus === 'completed' && currentJob" class="border-2 border-dashed border-green-300 rounded-lg p-6 bg-green-50">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-2xl mr-4">📄</span>
            <div>
              <h3 class="font-medium text-gray-900">{{ currentJob.file_name }}</h3>
              <p class="text-sm text-gray-500">分析完成</p>
            </div>
          </div>
          <button class="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm" @click="resetUpload">
            重新上传
          </button>
        </div>
      </div>
    </div>

    <!-- 评估结果 TAB -->
    <div v-if="currentJob && uploadStatus === 'completed'" class="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
      <!-- TAB导航 -->
      <div class="border-b border-gray-100 flex justify-between items-center">
        <div class="flex">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="px-6 py-4 text-sm font-medium transition-colors"
            :class="activeTab === tab.id ? 'text-primary border-b-2 border-primary' : 'text-gray-600 hover:text-primary'"
            @click="activeTab = tab.id"
          >
            {{ tab.name }}
          </button>
        </div>
      </div>

      <!-- TAB内容 -->
      <div class="p-6">
        <!-- 评审办法 -->
        <div v-if="activeTab === 1" class="space-y-6">
          <!-- 摘要 -->
          <div v-if="currentJob.summary" class="bg-blue-50 p-4 rounded-lg border border-blue-100">
            <h3 class="text-lg font-semibold text-blue-800 mb-2">评估摘要</h3>
            <p class="text-sm text-blue-700 leading-relaxed">{{ currentJob.summary }}</p>
          </div>

          <!-- 评审办法概述 -->
          <div v-if="currentJob.review_method && currentJob.review_method.method">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">评审办法</h3>
            <div class="bg-gray-50 p-4 rounded-lg">
              <div class="mb-3">
                <span class="text-sm font-medium text-gray-500">评审方法：</span>
                <span class="text-sm text-gray-900">{{ currentJob.review_method.method }}</span>
              </div>
              <div v-if="currentJob.review_method.description" class="mb-3">
                <span class="text-sm font-medium text-gray-500">说明：</span>
                <span class="text-sm text-gray-900">{{ currentJob.review_method.description }}</span>
              </div>
              <div v-if="currentJob.review_method.key_points && currentJob.review_method.key_points.length">
                <span class="text-sm font-medium text-gray-500">关键要点：</span>
                <ul class="mt-1 space-y-1">
                  <li v-for="(point, idx) in currentJob.review_method.key_points" :key="idx" class="text-sm text-gray-700 flex items-start">
                    <span class="mr-2">•</span>{{ point }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 技术评审表 -->
          <div v-if="currentJob.tech_review_table && currentJob.tech_review_table.length">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">技术评审表</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full border border-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">评审项</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-32">分值</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">评分标准</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="(item, idx) in currentJob.tech_review_table" :key="idx" class="hover:bg-gray-50">
                    <td class="px-4 py-3 text-sm text-gray-900">{{ item.item }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 font-medium">{{ item.score }}</td>
                    <td class="px-4 py-3 text-sm text-gray-600">{{ item.criteria }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="!currentJob.review_method?.method && (!currentJob.tech_review_table || currentJob.tech_review_table.length === 0)" class="text-center py-8 text-gray-400">
            未解析到评审办法和技术评审表信息
          </div>
        </div>

        <!-- 星标项 -->
        <div v-if="activeTab === 2" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">关键注意事项（星标项）</h3>
          <div v-if="currentJob.starred_items && currentJob.starred_items.length" class="space-y-4">
            <div v-for="(item, idx) in currentJob.starred_items" :key="idx" class="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
              <div class="flex items-start">
                <span class="text-yellow-500 font-bold text-lg mr-3">★</span>
                <div class="flex-1">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium text-gray-900">{{ item.item }}</h4>
                    <span :class="importanceBadgeClass(item.importance)" class="px-2 py-0.5 text-xs rounded-full">
                      {{ importanceLabel(item.importance) }}
                    </span>
                  </div>
                  <p v-if="item.suggestion" class="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    <span class="font-medium text-gray-700">建议：</span>{{ item.suggestion }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-400">
            未解析到星标项信息
          </div>
        </div>
      </div>
    </div>

    <!-- 历史评估记录 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="p-6 border-b border-gray-100 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-800">历史评估记录</h2>
        <button class="text-sm text-primary hover:text-primary/80" @click="loadHistory">
          刷新
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">文件名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">上传时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">客观分</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="record in evaluationRecords" :key="record.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ record.file_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ formatDate(record.created_at) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ record.objective_score ?? '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="statusBadgeClass(record.status)" class="px-2 py-1 text-xs rounded-full">
                  {{ statusLabel(record.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  class="mr-3 transition-colors"
                  :class="viewingRecordId === record.id ? 'text-gray-400 cursor-not-allowed' : 'text-primary hover:text-primary/80'"
                  :disabled="viewingRecordId === record.id"
                  @click="viewRecord(record.id)"
                >
                  <span v-if="viewingRecordId === record.id" class="inline-flex items-center">
                    <span class="spinner-sm mr-1"></span>加载中...
                  </span>
                  <span v-else>查看</span>
                </button>
                <button class="text-gray-600 hover:text-gray-900 mr-3" @click="downloadReport(record.id)">下载报告</button>
                <button class="text-red-500 hover:text-red-700" :disabled="viewingRecordId === record.id" @click="deleteRecord(record.id)">删除</button>
              </td>
            </tr>
            <tr v-if="evaluationRecords.length === 0">
              <td colspan="5" class="px-6 py-8 text-center text-sm text-gray-400">
                暂无历史记录
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  uploadPreEvaluation,
  listPreEvaluations,
  getPreEvaluation,
  deletePreEvaluation,
  type PreEvaluationJob,
  type PreEvaluationJobDetail,
} from '../services/preEvaluation'

const route = useRoute()

// 上传相关状态
const uploadStatus = ref<'idle' | 'uploading' | 'analyzing' | 'completed' | 'failed'>('idle')
const errorMessage = ref('')
const currentJob = ref<PreEvaluationJobDetail | null>(null)

// Toast 通知
const showToast = ref(false)
const toastMessage = ref('')
let toastTimer: ReturnType<typeof setTimeout> | null = null

// 查看按钮loading状态
const viewingRecordId = ref<string | null>(null)

const showNotification = (message: string, duration: number = 5000) => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = message
  showToast.value = true
  toastTimer = setTimeout(() => {
    showToast.value = false
    toastTimer = null
  }, duration)
}

// TAB
const activeTab = ref(1)
const tabs = [
  { id: 1, name: '评审办法' },
  { id: 2, name: '星标项' },
]

// 历史记录
const evaluationRecords = ref<PreEvaluationJob[]>([])

// 重要性标签
const importanceBadgeClass = (importance: string) => {
  switch (importance) {
    case 'high': return 'bg-red-100 text-red-700'
    case 'medium': return 'bg-yellow-100 text-yellow-700'
    case 'low': return 'bg-green-100 text-green-700'
    default: return 'bg-gray-100 text-gray-700'
  }
}
const importanceLabel = (importance: string) => {
  switch (importance) {
    case 'high': return '高'
    case 'medium': return '中'
    case 'low': return '低'
    default: return importance || '一般'
  }
}

// 状态标签
const statusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-green-100 text-green-800'
    case 'failed': return 'bg-red-100 text-red-800'
    case 'analyzing': return 'bg-blue-100 text-blue-800'
    case 'parsing': return 'bg-yellow-100 text-yellow-800'
    case 'pending': return 'bg-gray-100 text-gray-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}
const statusLabel = (status: string) => {
  switch (status) {
    case 'completed': return '已完成'
    case 'failed': return '失败'
    case 'analyzing': return '分析中'
    case 'parsing': return '解析中'
    case 'pending': return '待处理'
    default: return status
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN')
}

// 处理文件上传
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploadStatus.value = 'uploading'
  errorMessage.value = ''
  showNotification('文件正在上传解析中，请稍后查看结果')

  try {
    const projectId = typeof route.query.projectId === 'string' ? route.query.projectId : undefined
    const result = await uploadPreEvaluation(file, projectId)
    currentJob.value = result
    uploadStatus.value = 'completed'
    await loadHistory()
  } catch (e: any) {
    uploadStatus.value = 'failed'
    errorMessage.value = e.response?.data?.detail || e.message || '上传或分析失败'
    showNotification('上传失败：' + (e.response?.data?.detail || e.message || '上传或分析失败'), 5000)
  }
}

// 重置上传
const resetUpload = () => {
  uploadStatus.value = 'idle'
  currentJob.value = null
  errorMessage.value = ''
  activeTab.value = 1
  const input = document.getElementById('file-upload') as HTMLInputElement
  if (input) input.value = ''
}

// 加载历史记录
const loadHistory = async () => {
  try {
    const projectId = typeof route.query.projectId === 'string' ? route.query.projectId : undefined
    evaluationRecords.value = await listPreEvaluations(projectId)
  } catch (e: any) {
    console.error('加载历史记录失败:', e)
  }
}

// 查看记录详情
const viewRecord = async (jobId: string) => {
  viewingRecordId.value = jobId
  try {
    const result = await getPreEvaluation(jobId)
    currentJob.value = result
    uploadStatus.value = 'completed'
    activeTab.value = 1
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e: any) {
    alert('加载详情失败: ' + (e.message || '未知错误'))
  } finally {
    viewingRecordId.value = null
  }
}

// 删除记录
const deleteRecord = async (jobId: string) => {
  if (!confirm('确定要删除这条评估记录吗？')) return
  try {
    await deletePreEvaluation(jobId)
    if (currentJob.value?.id === jobId) {
      resetUpload()
    }
    await loadHistory()
  } catch (e: any) {
    alert('删除失败: ' + (e.message || '未知错误'))
  }
}

// 下载报告
const downloadReport = async (jobId: string) => {
  try {
    // 获取详情数据
    const result = await getPreEvaluation(jobId)
    // 生成报告内容
    const reportContent = generateReportContent(result)
    // 创建下载
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `标前评估报告_${result.file_name || jobId}.txt`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (e: any) {
    alert('下载报告失败: ' + (e.message || '未知错误'))
  }
}

// 生成报告内容
const generateReportContent = (job: PreEvaluationJobDetail): string => {
  let content = `标前评估报告\n`
  content += `================\n\n`
  content += `文件名称: ${job.file_name}\n`
  content += `评估时间: ${formatDate(job.created_at)}\n`
  content += `评估状态: ${statusLabel(job.status)}\n\n`

  if (job.summary) {
    content += `评估摘要\n`
    content += `--------\n`
    content += `${job.summary}\n\n`
  }

  if (job.review_method?.method) {
    content += `评审办法\n`
    content += `--------\n`
    content += `评审方法: ${job.review_method.method}\n`
    if (job.review_method.description) {
      content += `说明: ${job.review_method.description}\n`
    }
    if (job.review_method.key_points?.length) {
      content += `关键要点:\n`
      job.review_method.key_points.forEach((point, idx) => {
        content += `  ${idx + 1}. ${point}\n`
      })
    }
    content += `\n`
  }

  if (job.tech_review_table?.length) {
    content += `技术评审表\n`
    content += `----------\n`
    job.tech_review_table.forEach(item => {
      content += `评审项: ${item.item}\n`
      content += `分值: ${item.score}\n`
      content += `评分标准: ${item.criteria}\n\n`
    })
  }

  if (job.starred_items?.length) {
    content += `星标项\n`
    content += `------\n`
    job.starred_items.forEach((item, idx) => {
      content += `${idx + 1}. ${item.item}\n`
      content += `   重要性: ${importanceLabel(item.importance)}\n`
      if (item.suggestion) {
        content += `   建议: ${item.suggestion}\n`
      }
      content += `\n`
    })
  }

  return content
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-sm {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: #999;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
</style>

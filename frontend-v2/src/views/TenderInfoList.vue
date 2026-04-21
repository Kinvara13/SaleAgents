<template>
  <div class="fade-in">
    <!-- Header -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold text-gray-800">招标信息</h2>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-1.5 text-xs rounded-lg border transition-all"
          :class="mineFilter ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:border-primary hover:text-primary'"
          @click="toggleMineFilter"
        >
          {{ mineFilter ? '✓ 我的招标' : '全部招标' }}
        </button>
      </div>
    </div>

    <!-- Filter & Search -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- Status Filter -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">状态:</span>
          <button
            v-for="s in statusOptions"
            :key="s.value"
            class="px-3 py-1.5 rounded-lg text-sm transition-all"
            :class="activeStatus === s.value
              ? 'bg-primary text-white'
              : 'text-gray-600 hover:bg-gray-100'"
            @click="activeStatus = s.value; loadTenders()"
          >
            {{ s.label }}
          </button>
        </div>

        <!-- Search -->
        <div class="flex-1 max-w-md">
          <div class="relative">
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索招标标题或类型"
              class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
              @keyup.enter="loadTenders"
            />
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <!-- List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="tender in filteredTenders"
        :key="tender.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300 cursor-pointer"
        @click="handleTenderClick(tender)"
      >
        <div class="mb-3">
          <h3 class="text-base font-semibold text-gray-800 mb-2 line-clamp-2">{{ tender.title }}</h3>
          <p class="text-xs text-gray-500">{{ tender.project_type }}</p>
        </div>

        <div class="space-y-2 mb-4 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">预算金额</span>
            <span class="font-semibold text-gray-800">{{ tender.amount || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">截止时间</span>
            <span class="font-semibold text-gray-800">{{ tender.deadline || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">发布日期</span>
            <span class="font-semibold text-gray-800">{{ tender.publish_date || '-' }}</span>
          </div>
        </div>

        <div class="flex justify-between items-center">
          <span
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium',
              tender.decision === 'pending' ? 'bg-gray-100 text-gray-600' :
              tender.decision === 'bid' ? 'bg-success/10 text-success' :
              'bg-danger/10 text-danger'
            ]"
          >
            {{ decisionLabel(tender.decision) }}
          </span>
          <span v-if="tender.deadline" class="flex items-center text-xs text-gray-400">
            <span class="mr-1">⏰</span>
            {{ formatCountdown(tender.deadline) }}
          </span>
        </div>
      </div>

      <!-- Empty -->
      <div v-if="filteredTenders.length === 0" class="col-span-full text-center py-12 text-gray-400">
        <div class="text-5xl mb-4">📋</div>
        <p>暂无招标信息</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listTenders, type Tender } from '../services/tender'

const router = useRouter()

const tenders = ref<Tender[]>([])
const loading = ref(false)
const error = ref('')
const mineFilter = ref(false)
const searchKeyword = ref('')
const activeStatus = ref('all')

const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'pending' },
  { label: '已投标', value: 'bid' },
  { label: '不投标', value: 'reject' },
]

const filteredTenders = computed(() => {
  let list = tenders.value
  if (activeStatus.value !== 'all') {
    list = list.filter(t => t.decision === activeStatus.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter(t =>
      t.title.toLowerCase().includes(kw) ||
      t.project_type.toLowerCase().includes(kw)
    )
  }
  return list
})

function toggleMineFilter() {
  mineFilter.value = !mineFilter.value
  loadTenders()
}

async function loadTenders() {
  loading.value = true
  error.value = ''
  try {
    tenders.value = await listTenders()
  } catch (e: any) {
    error.value = e.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function handleTenderClick(tender: Tender) {
  router.push(`/tender-info/${tender.id}`)
}

function decisionLabel(decision: string) {
  return { pending: '待处理', bid: '已投标', reject: '不投标' }[decision] || decision
}

function formatCountdown(deadline: string) {
  if (!deadline) return ''
  const end = new Date(deadline)
  const now = new Date()
  const diff = end.getTime() - now.getTime()
  if (diff <= 0) return '已截止'
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  return `${days}天${hours}小时`
}

onMounted(loadTenders)
</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

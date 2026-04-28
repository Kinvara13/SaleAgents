<template>
  <div class="fade-in">
    <!-- 标题和操作按钮 -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold text-gray-800">招标项目</h2>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-1.5 text-xs rounded-lg border transition-all"
          :class="mineFilter ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-200 hover:border-primary hover:text-primary'"
          @click="toggleMineFilter"
        >
          {{ mineFilter ? '✓ 我的项目' : '全部项目' }}
        </button>
        <button class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300" @click="handleCreateProject">
          + 新增项目
        </button>
      </div>
    </div>

    <!-- 筛选和搜索区域 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <!-- 状态筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">状态:</span>
          <button class="px-3 py-1.5 rounded-lg bg-primary text-white text-sm">全部</button>
          <button class="px-3 py-1.5 rounded-lg text-gray-600 text-sm hover:bg-gray-100 transition-all">进行中</button>
          <button class="px-3 py-1.5 rounded-lg text-gray-600 text-sm hover:bg-gray-100 transition-all">即将截止</button>
          <button class="px-3 py-1.5 rounded-lg text-gray-600 text-sm hover:bg-gray-100 transition-all">已截止</button>
          <button class="px-3 py-1.5 rounded-lg text-gray-600 text-sm hover:bg-gray-100 transition-all">草稿</button>
        </div>

        <!-- 日期筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">发布日期:</span>
          <input type="date" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
          <span class="text-gray-400">至</span>
          <input type="date" class="px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
        </div>

        <!-- 搜索框 -->
        <div class="flex-1 max-w-md">
          <div class="relative">
            <input
              type="text"
              placeholder="搜索项目名称或招标方"
              class="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
            >
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <!-- 项目列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in projects"
        :key="project.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300 cursor-pointer relative"
        @click="handleProjectClick(project.id)"
      >
        <button
          class="absolute top-3 right-3 w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:text-danger hover:bg-danger/10 transition-all"
          @click.stop="showDeleteConfirm = project.id"
          title="删除项目"
        >
          ✕
        </button>

        <div v-if="showDeleteConfirm === project.id" class="absolute inset-0 bg-white/95 rounded-xl flex flex-col items-center justify-center z-10 p-4">
          <p class="text-sm text-gray-700 mb-3">确定删除此项目？</p>
          <div class="flex space-x-2">
            <button
              class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50"
              @click.stop="showDeleteConfirm = null"
            >
              取消
            </button>
            <button
              class="px-3 py-1.5 text-xs bg-danger text-white rounded-lg hover:bg-danger/90"
              @click.stop="handleDeleteProject(project.id)"
            >
              删除
            </button>
          </div>
        </div>

        <div class="mb-4">
          <h3 class="text-lg font-semibold text-gray-800 mb-2 line-clamp-2 pr-6">{{ project.name }}</h3>
          <p class="text-sm text-gray-500 mb-2">招标方：{{ project.client || '-' }}</p>
          <p class="text-sm text-gray-600">应标方：{{ project.owner || '-' }}</p>
        </div>

        <div class="space-y-3 mb-4">
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">预算金额</span>
            <span class="text-sm font-semibold text-gray-800">{{ formatAmount(project.amount) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">截止时间</span>
            <span class="text-sm font-semibold text-gray-800">{{ project.deadline || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">创建时间</span>
            <span class="text-xs text-gray-500">{{ formatDate(project.created_at) }}</span>
          </div>
        </div>

        <div class="flex justify-between items-center">
          <span
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium',
              project.status === '进行中' ? 'bg-success/10 text-success' :
              project.status === '即将截止' ? 'bg-warning/10 text-warning' :
              project.status === '已截止' ? 'bg-gray-100 text-gray-500' :
              'bg-info/10 text-info'
            ]"
          >
            {{ project.status }}
          </span>
          <div class="flex items-center text-sm text-danger">
            <span class="mr-1">⏰</span>
            {{ formatCountdown(project.deadline) }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="projects.length === 0" class="col-span-full text-center py-12 text-gray-400">
        <div class="text-5xl mb-4">📋</div>
        <p>暂无项目{{ mineFilter ? '（我的项目）' : '' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listProjects, deleteProject } from '../services/project'
import type { Project } from '../types'

const router = useRouter()

const projects = ref<Project[]>([])
const loading = ref(false)
const error = ref('')
const mineFilter = ref(false)
const showDeleteConfirm = ref<string | null>(null)

function toggleMineFilter() {
  mineFilter.value = !mineFilter.value
  loadProjects()
}

async function loadProjects() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await listProjects(undefined, mineFilter.value)
  } catch (e: any) {
    error.value = e.message || '加载项目失败'
  } finally {
    loading.value = false
  }
}

const handleCreateProject = () => {
  router.push('/project-create')
}

const handleProjectClick = (id: string) => {
  const project = projects.value.find(p => p.id === id)
  if (project && (project.status === '草稿' || project.status === '解析中' || project.status === '解析失败')) {
    router.push(`/project-create/${id}`)
  } else {
    router.push(`/tender-detail/${id}`)
  }
}

const handleDeleteProject = async (id: string) => {
  try {
    await deleteProject(id)
    projects.value = projects.value.filter(p => p.id !== id)
    showDeleteConfirm.value = null
  } catch (e: any) {
    error.value = e.message || '删除失败'
  }
}

const formatAmount = (amount: string) => {
  if (!amount) return '-'
  return amount.startsWith('¥') ? amount : `¥ ${amount}`
}

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return '-'
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch {
    return '-'
  }
}

const formatCountdown = (deadline: string) => {
  if (!deadline) return '未设置'
  const end = new Date(deadline)
  const now = new Date()
  const diff = end.getTime() - now.getTime()
  if (diff <= 0) return '已结束'
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  return `${days}天${hours}小时`
}

onMounted(loadProjects)
</script>

<style scoped>
</style>

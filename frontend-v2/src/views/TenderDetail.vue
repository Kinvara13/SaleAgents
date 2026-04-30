<template>
  <div class="fade-in">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
      {{ error }}
    </div>

    <template v-else-if="displayProject">
      <!-- 标题 -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">{{ displayProject.name }}</h2>
      </div>

      <!-- 项目基本信息 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">项目基本信息</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <p class="text-sm text-gray-500 mb-1">招标方</p>
            <p class="font-medium text-gray-800">{{ displayProject.client || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">应标方</p>
            <p class="font-medium text-gray-800">{{ displayProject.bidder }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">预算金额</p>
            <p class="font-medium text-gray-800">{{ displayProject.budget }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">截止时间</p>
            <p class="font-medium text-gray-800">{{ displayProject.deadline || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">项目状态</p>
            <span
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium',
                displayProject.status === '进行中' ? 'bg-success/10 text-success' :
                displayProject.status === '即将截止' ? 'bg-warning/10 text-warning' :
                'bg-gray-100 text-gray-500'
              ]"
            >
              {{ displayProject.status }}
            </span>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">倒计时</p>
            <span class="text-sm text-danger">{{ displayProject.countdown }}</span>
          </div>
          <div class="md:col-span-2">
            <p class="text-sm text-gray-500 mb-1">项目描述</p>
            <p class="text-gray-700">{{ displayProject.description || '暂无描述' }}</p>
          </div>
        </div>
      </div>

    <!-- 回标文件完成情况 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-800">回标文件完成情况</h3>
        <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all text-sm flex items-center" @click="downloadAllFiles">
          <span class="mr-2">📥</span>
          一键下载
        </button>
      </div>
      <div class="space-y-6" v-if="bidSections && bidSections.length">
        <div v-for="section in bidSections" :key="section.id">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <span class="mr-3">{{ section.icon }}</span>
              <h4 class="font-medium text-gray-800">{{ section.name }}</h4>
            </div>
            <span class="text-sm font-medium text-gray-600">
              {{ section.completed }}/{{ section.total }} 完成
            </span>
          </div>
          <div class="h-2 bg-gray-200 rounded-full overflow-hidden mb-3">
            <div
              class="h-full rounded-full transition-all duration-1000"
              :class="section.completed === section.total ? 'bg-success' : 'bg-primary'"
              :style="{ width: (section.completed / section.total * 100) + '%' }"
            ></div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div
              v-for="file in section.files"
              :key="file.id"
              class="flex items-center p-3 border border-gray-100 rounded-lg hover:border-primary/30 transition-all"
            >
              <span class="mr-3 text-gray-400">{{ file.icon }}</span>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-800">{{ file.name }}</p>
                <div v-if="file.responsible" class="text-xs text-gray-500">
                  负责人：{{ file.responsible }}
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  v-if="file.status === '已完成'"
                  class="text-xs text-primary hover:underline transition-all"
                  @click="openPreview(file)"
                >
                  预览
                </button>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    file.status === '已完成' ? 'bg-success/10 text-success' :
                    file.status === '进行中' ? 'bg-primary/10 text-primary' :
                    'bg-gray-100 text-gray-500'
                  ]"
                >
                  {{ file.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预估得分 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6" v-if="scoringCriteria && scoringCriteria.length">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">预估得分</h3>
      <div class="overflow-x-auto">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-gray-50 text-left">
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700">一级指标</th>
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700">二级指标</th>
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700">评分标准原文</th>
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700 text-center">分值</th>
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700 text-center">类型</th>
              <th class="px-4 py-3 border-b border-gray-200 text-sm font-semibold text-gray-700 text-center">预估得分</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="(item, index) in scoringCriteria" :key="index" class="hover:bg-gray-50 transition-colors">
              <td class="px-4 py-3 text-sm text-gray-800 font-medium" v-if="item.isFirstInGroup" :rowspan="item.groupSpan">
                {{ item.primary }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-700">{{ item.secondary }}</td>
              <td class="px-4 py-3 text-xs text-gray-500 max-w-md">
                <div class="line-clamp-3 hover:line-clamp-none cursor-pointer transition-all duration-300">
                  {{ item.standard }}
                </div>
              </td>
              <td class="px-4 py-3 text-sm text-gray-700 text-center">{{ item.maxScore }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="[
                  'px-2 py-0.5 rounded text-xs font-medium',
                  item.type === '客观' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'
                ]">
                  {{ item.type }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm font-bold text-center" :class="item.type === '客观' ? 'text-primary' : 'text-gray-400'">
                {{ item.type === '客观' ? item.estimatedScore : '/' }}
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="bg-primary/5 font-bold">
              <td colspan="5" class="px-4 py-4 text-right text-gray-800">客观分总得分合计：</td>
              <td class="px-4 py-4 text-center text-xl text-primary">{{ totalObjectiveScore }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- 操作历史 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h3 class="text-lg font-semibold text-gray-800 mb-4">操作历史</h3>
      <div v-if="activities && activities.length" class="space-y-3">
        <div v-for="(activity, index) in activities" :key="index" class="flex items-start space-x-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" :class="activity.iconBg">
            <span :class="activity.iconColor">{{ activity.icon }}</span>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-800">{{ activity.title }}</p>
            <p v-if="activity.time" class="text-xs text-gray-500">{{ activity.time }}</p>
          </div>
        </div>
      </div>
      <div v-else class="text-sm text-gray-400 text-center py-4">暂无操作记录</div>
    </div>

    <!-- 文件预览窗口 -->
    <div v-if="previewModalVisible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[80vh] flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">文件预览 - {{ previewFile?.name }}</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="previewModalVisible = false">
            ✕
          </button>
        </div>
        <div class="flex-1 overflow-auto mb-4">
          <div class="border border-gray-200 rounded-lg p-6 bg-gray-50">
            <div class="text-4xl text-center mb-4">{{ previewFile?.icon }}</div>
            <div class="prose max-w-none">
              <p class="text-gray-700">这是{{ previewFile?.name }}的预览内容。</p>
              <p class="text-gray-600 mt-4">文件状态：{{ previewFile?.status }}</p>
              <p class="text-gray-600">负责人：{{ previewFile?.responsible || '未分配' }}</p>
              <div class="mt-6 p-4 bg-gray-100 rounded-lg">
                <h4 class="font-medium text-gray-800 mb-2">文件内容预览</h4>
                <p class="text-gray-600">这里展示文件的实际内容预览。实际项目中应从服务器获取文件内容。</p>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-end space-x-3">
          <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all" @click="previewModalVisible = false">
            关闭
          </button>
          <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all flex items-center">
            <span class="mr-2">📥</span>
            下载文件
          </button>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getProject,
  getProjectBidProgress,
  getProjectScoringCriteria,
  getProjectActivities,
  type Project,
  type BidSection,
  type ScoringCriteriaItem,
  type ProjectActivity,
} from '../services/project'
import {
  getLatestJobByProject,
  exportGenerationJobDocx,
} from '../services/generation'

const route = useRoute()
const projectId = route.params.id as string

const loading = ref(false)
const error = ref('')

const project = ref<Project | null>(null)
const bidSections = ref<BidSection[]>([])
const scoringCriteria = ref<ScoringCriteriaItem[]>([])
const activities = ref<ProjectActivity[]>([])

const displayProject = computed(() => {
  if (!project.value) return null
  const p = project.value
  const end = p.deadline ? new Date(p.deadline) : null
  const now = new Date()
  let countdown = '未设置'
  if (end) {
    const diff = end.getTime() - now.getTime()
    if (diff <= 0) countdown = '已结束'
    else {
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      countdown = `${days}天${hours}小时`
    }
  }
  return {
    ...p,
    bidder: p.bidding_company || p.owner || '-',
    budget: p.amount ? (p.amount.startsWith('¥') ? p.amount : `¥ ${p.amount}`) : '-',
    countdown,
  }
})

const totalObjectiveScore = computed(() => {
  if (!scoringCriteria.value) return 0
  return scoringCriteria.value
    .filter(item => item.type === '客观')
    .reduce((sum, item) => sum + item.estimatedScore, 0)
})

const previewModalVisible = ref(false)
const previewFile = ref<BidSection['files'][0] | null>(null)

const openPreview = (file: BidSection['files'][0]) => {
  previewFile.value = file
  previewModalVisible.value = true
}

const downloadAllFiles = async () => {
  error.value = ''
  try {
    const job = await getLatestJobByProject(projectId)
    const blob = await exportGenerationJobDocx(job.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `回标文件_${displayProject.value?.name || projectId}.docx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (e: any) {
    error.value = e.message || '未找到可下载的回标文件，请先在标书制作页生成'
  }
}

async function loadDetail() {
  loading.value = true
  error.value = ''
  try {
    const [p, bidProgress, criteria, acts] = await Promise.all([
      getProject(projectId),
      getProjectBidProgress(projectId),
      getProjectScoringCriteria(projectId),
      getProjectActivities(projectId),
    ])
    project.value = p
    bidSections.value = bidProgress
    scoringCriteria.value = criteria
    activities.value = acts
  } catch (e: any) {
    error.value = e.message || '加载项目详情失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
</script>

<style scoped>
</style>

<template>
  <div class="fade-in flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div>
        <h2 class="text-xl font-bold text-gray-800">技术建议书编辑器</h2>
        <p class="text-sm text-gray-500 mt-0.5">{{ project?.name || '加载中...' }}</p>
      </div>
      <div class="flex items-center space-x-2">
        <button
          class="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm transition-all"
          @click="showScoringRules = true"
        >
          📋 评分规则
        </button>
        <button
          class="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm transition-all"
          @click="goBack"
        >
          ← 返回列表
        </button>
      </div>
    </div>

    <!-- 项目信息摘要 -->
    <div v-if="project" class="flex-shrink-0 flex items-center space-x-6 mb-3 text-sm">
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">客户:</span> {{ project.client || '-' }}
      </div>
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">投标:</span> {{ project.bidding_company || '-' }}
      </div>
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">截止:</span> {{ project.deadline || '-' }}
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div class="flex items-center space-x-3">
        <!-- 生成按钮 -->
        <button
          v-if="!hasGenerated"
          class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm font-medium transition-all flex items-center"
          :disabled="generating"
          @click="handleGenerate"
        >
          <span v-if="generating" class="mr-2">
            <span class="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full"></span>
          </span>
          <span v-else class="mr-1">✨</span>
          {{ generating ? '生成中...' : 'AI 生成建议书' }}
        </button>

        <!-- 重新生成 -->
        <button
          v-if="hasGenerated"
          class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm font-medium transition-all"
          :disabled="generating"
          @click="handleRegenerate"
        >
          🔄 重新生成
        </button>

        <!-- 预打分按钮 -->
        <button
          v-if="hasGenerated"
          class="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 text-sm font-medium transition-all"
          :disabled="scoring"
          @click="handleScore"
        >
          📊 {{ scoring ? '评分中...' : '预打分' }}
        </button>

        <!-- 再次打分（人工修改后） -->
        <button
          v-if="hasGenerated && hasEdited"
          class="px-4 py-2 bg-warning text-white rounded-lg hover:bg-warning/90 text-sm font-medium transition-all"
          :disabled="scoring"
          @click="handleRescore"
        >
          🔄 再次打分
        </button>

        <!-- 确认完成 -->
        <button
          v-if="hasGenerated && allConfirmed"
          class="px-4 py-2 bg-success text-white rounded-lg hover:bg-success/90 text-sm font-medium transition-all"
          @click="handleConfirm"
        >
          ✅ 确认完成
        </button>
      </div>

      <!-- 总分展示 -->
      <div v-if="totalScore > 0" class="flex items-center space-x-3">
        <div class="text-sm">
          <span class="text-gray-500">总分：</span>
          <span class="text-2xl font-bold text-primary ml-1">{{ totalScore }}</span>
          <span class="text-gray-400 text-xs">/ 100</span>
        </div>
        <div class="text-xs text-gray-400">
          <span class="px-2 py-0.5 bg-gray-100 rounded">已生成</span>
        </div>
      </div>
    </div>

    <!-- 生成进度条 -->
    <div v-if="generating" class="mb-4 flex-shrink-0">
      <div class="flex items-center space-x-3">
        <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full bg-primary rounded-full transition-all duration-500 animate-pulse" :style="{ width: generateProgress + '%' }"></div>
        </div>
        <span class="text-xs text-gray-500 whitespace-nowrap">AI 正在生成章节内容...</span>
      </div>
      <div class="mt-1 text-xs text-gray-400 flex items-center space-x-4">
        <span>📝 整体解决方案</span>
        <span>🏗️ 软件架构</span>
        <span>⚙️ 功能实现</span>
        <span>🔌 接口方案</span>
        <span>🚀 部署方案</span>
      </div>
    </div>

    <!-- 章节列表 -->
    <div v-if="hasGenerated || sections.length > 0" class="flex-1 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100">
        <!-- 表头 -->
        <div class="flex items-center px-4 py-3 bg-gray-50 border-b border-gray-100 text-xs uppercase text-gray-500 font-medium">
          <div class="flex-1">章节名称</div>
          <div class="w-20 text-center">得分</div>
          <div class="w-16 text-center">权重</div>
          <div class="w-24 text-center">状态</div>
          <div class="w-36 text-center">操作</div>
        </div>

        <!-- 章节行 -->
        <div
          v-for="section in sections"
          :key="section.id"
          class="flex items-center px-4 py-3 border-b border-gray-50 hover:bg-gray-50/50 transition-all"
          :class="selectedSection?.id === section.id ? 'bg-primary/5' : ''"
        >
          <div class="flex-1 flex items-center space-x-2">
            <span class="text-sm font-medium text-gray-800">{{ section.section_name }}</span>
          </div>
          <div class="w-20 text-center">
            <span
              v-if="section.score > 0"
              class="px-2 py-1 rounded text-sm font-bold"
              :class="section.score >= 80 ? 'text-success' : section.score >= 60 ? 'text-warning' : 'text-danger'"
            >
              {{ section.score }}
            </span>
            <span v-else class="text-gray-300 text-xs">-</span>
          </div>
          <div class="w-16 text-center">
            <span class="text-xs text-gray-400">{{ getSectionWeight(section.section_name) }}</span>
          </div>
          <div class="w-24 text-center">
            <span
              v-if="section.is_confirmed"
              class="px-2 py-1 bg-success/10 text-success text-xs rounded-full"
            >
              ✓ 已确认
            </span>
            <span
              v-else-if="section.is_generated"
              class="px-2 py-1 bg-warning/10 text-warning text-xs rounded-full"
            >
              待确认
            </span>
            <span v-else class="px-2 py-1 bg-gray-100 text-gray-400 text-xs rounded-full">
              未生成
            </span>
          </div>
          <div class="w-36 text-center flex items-center justify-center space-x-1">
            <button
              class="px-2 py-1 text-xs text-primary hover:underline"
              @click="selectSection(section)"
            >
              查看
            </button>
            <button
              class="px-2 py-1 text-xs text-blue-500 hover:underline"
              @click="openEditSection(section)"
            >
              编辑
            </button>
            <button
              v-if="section.is_generated && !section.is_confirmed"
              class="px-2 py-1 text-xs text-success hover:underline"
              @click="confirmSection(section)"
            >
              确认
            </button>
          </div>
        </div>

        <!-- 全部确认提示 -->
        <div v-if="allConfirmed && hasGenerated" class="px-4 py-3 bg-success/5 border-t border-gray-100">
          <p class="text-sm text-success font-medium text-center">
            ✅ 所有章节已确认，技术建议书已完成
          </p>
        </div>
      </div>
    </div>

    <!-- 章节详情（选中时） -->
    <div v-if="selectedSection && selectedSection.content" class="flex-shrink-0 mt-3 bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-medium text-gray-800">{{ selectedSection.section_name }}</h3>
        <div class="flex items-center space-x-2">
          <span
            v-if="selectedSection.score > 0"
            class="px-2 py-1 rounded text-xs font-bold"
            :class="selectedSection.score >= 80 ? 'bg-success/10 text-success' : selectedSection.score >= 60 ? 'bg-warning/10 text-warning' : 'bg-danger/10 text-danger'"
          >
            得分: {{ selectedSection.score }}
          </span>
          <button
            class="px-3 py-1 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
            @click="openEditSection(selectedSection)"
          >
            编辑内容
          </button>
        </div>
      </div>
      <pre class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed font-sans max-h-48 overflow-auto">{{ selectedSection.content }}</pre>
    </div>

    <!-- 未生成状态 -->
    <div v-if="!hasGenerated && sections.length === 0" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="text-5xl mb-4">📝</div>
        <p class="text-gray-600 mb-2">点击上方按钮，AI 将生成完整的技术建议书</p>
        <p class="text-xs text-gray-400">包含 10 个标准章节，结合客户背景、公司背景、技术打分表要求</p>
        <div class="mt-4 text-xs text-gray-400 space-y-1">
          <p>✨ AI 生成内容包含：</p>
          <p>• 结合客户背景和公司背景的专业方案</p>
          <p>• 响应技术打分表的评分要点</p>
          <p>• 支持人工编辑确认</p>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showEditModal = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-2xl p-6 max-h-[80vh] flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800">编辑章节内容 - {{ editingSection?.section_name }}</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="showEditModal = false">✕</button>
        </div>
        <div class="mb-3 text-xs text-gray-500 bg-blue-50 px-3 py-2 rounded">
          💡 编辑后请点击"再次打分"重新计算得分
        </div>
        <textarea
          v-model="editContent"
          class="flex-1 w-full min-h-[300px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          placeholder="请输入章节内容..."
        ></textarea>
        <div class="flex justify-end space-x-3 mt-4">
          <button
            class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
            @click="showEditModal = false"
          >
            取消
          </button>
          <button
            class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-all"
            :disabled="savingSection"
            @click="saveSection"
          >
            {{ savingSection ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 评分规则弹窗 -->
    <div v-if="showScoringRules" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showScoringRules = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-lg p-6 max-h-[80vh] overflow-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800">📋 技术建议书评分规则</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="showScoringRules = false">✕</button>
        </div>
        <div class="text-sm text-gray-500 mb-4">
          根据技术打分表和技术规范书要求，各章节评分标准如下：
        </div>
        <div class="space-y-2">
          <div v-for="rule in scoringRules" :key="rule.section_name" class="border border-gray-100 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <span class="font-medium text-gray-800">{{ rule.section_name }}</span>
              <span class="text-xs text-gray-500">满分 {{ rule.max_score }} 分 · 权重 {{ (rule.weight * 100).toFixed(0) }}%</span>
            </div>
            <div class="text-xs text-gray-400 mt-1">{{ rule.criteria }}</div>
          </div>
        </div>
        <div class="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-500">
          提示：总分 100 分，各章节得分 × 权重求和为最终得分。人工编辑后建议再次打分。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import api from '../services/api'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getProject } from '../services/project'
import type { Project } from '../types'

interface ProposalSection {
  id: string
  section_name: string
  content: string
  score: number
  is_confirmed: boolean
  is_generated: boolean
}

interface ScoringRule {
  section_name: string
  max_score: number
  weight: number
  criteria: string
}

const router = useRouter()
const route = useRoute()

const project = ref<Project | null>(null)
const sections = ref<ProposalSection[]>([])
const loading = ref(false)
const generating = ref(false)
const scoring = ref(false)
const savingSection = ref(false)
const selectedSection = ref<ProposalSection | null>(null)
const editingSection = ref<ProposalSection | null>(null)
const showEditModal = ref(false)
const editContent = ref('')
const totalScore = ref(0)
const generateProgress = ref(0)
const hasEdited = ref(false)
const showScoringRules = ref(false)
const scoringRules = ref<ScoringRule[]>([])

// 评分规则权重映射
const weightMap: Record<string, string> = {
  '整体解决方案': '15%',
  '软件架构': '12%',
  '功能实现方案': '18%',
  '系统接口方案': '10%',
  '部署方案': '8%',
  '兼容性': '5%',
  '系统安全': '10%',
  '项目经理能力': '8%',
  '人员能力': '7%',
  '维保期限': '7%',
}

function getSectionWeight(name: string): string {
  return weightMap[name] || '-'
}

const hasGenerated = computed(() => sections.value.some(s => s.is_generated))
const allConfirmed = computed(() => sections.value.length > 0 && sections.value.every(s => s.is_confirmed))

async function fetchSections() {
  const projectId = route.params.projectId as string
  if (!projectId) return
  try {
    const res = await api.get(`/proposal-editor/${projectId}/sections`)
    sections.value = res.data
  } catch (e) {
    console.error('Failed to fetch sections:', e)
  }
}

async function fetchScoringRules() {
  const projectId = route.params.projectId as string
  if (!projectId) return
  try {
    const res = await api.get(`/proposal-editor/${projectId}/scoring-rules`)
    scoringRules.value = res.data.sections
  } catch (e) {
    console.error('Failed to fetch scoring rules:', e)
  }
}

let pollTimer: ReturnType<typeof setInterval> | null = null
let pollCount = 0
const MAX_POLL_COUNT = 60 // 最多轮询5分钟

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollCount = 0
  pollTimer = setInterval(async () => {
    pollCount++
    if (pollCount > MAX_POLL_COUNT) {
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
      generating.value = false
      generateProgress.value = 0
      console.warn('生成任务超时，请刷新页面检查结果')
      return
    }
    await fetchSections()
    const hasGen = sections.value.some(s => s.is_generated)
    if (hasGen) {
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
      generating.value = false
      generateProgress.value = 0
      // 自动计算总分
      totalScore.value = sections.value.reduce((sum, s) => sum + (s.score || 0), 0)
    }
  }, 2000)
}

async function handleGenerate() {
  const projectId = route.params.projectId as string
  if (!projectId) return

  generating.value = true
  generateProgress.value = 0

  // 模拟进度
  const progressInterval = setInterval(() => {
    if (generateProgress.value < 85) {
      generateProgress.value += Math.random() * 15
    }
  }, 500)

  try {
    const res = await api.post(`/proposal-editor/${projectId}/generate`, {
      include_client_bg: true,
      include_company_bg: true,
      reference_scoring: true,
    })

    // 后端返回 processing 状态，启动轮询
    if (res.data && res.data.status === 'processing') {
      startPolling()
    } else {
      // 后端直接返回结果（同步模式）
      clearInterval(progressInterval)
      generateProgress.value = 100
      sections.value = res.data
      generating.value = false
      totalScore.value = sections.value.reduce((sum, s) => sum + (s.score || 0), 0)
    }
  } catch (e) {
    clearInterval(progressInterval)
    console.error('Generate failed:', e)
    generating.value = false
    generateProgress.value = 0
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }
}

async function handleRegenerate() {
  if (confirm('重新生成将覆盖所有现有章节，确定继续？')) {
    await handleGenerate()
  }
}

async function handleScore() {
  const projectId = route.params.projectId as string
  if (!projectId) return
  scoring.value = true
  try {
    const res = await api.post(`/proposal-editor/${projectId}/score`)
    sections.value = res.data.sections
    totalScore.value = res.data.total_score
  } catch (e) {
    console.error('Score failed:', e)
  } finally {
    scoring.value = false
  }
}

async function handleRescore() {
  const projectId = route.params.projectId as string
  if (!projectId) return
  scoring.value = true
  try {
    const res = await api.post(`/proposal-editor/${projectId}/rescore`)
    sections.value = res.data.sections
    totalScore.value = res.data.total_score
    hasEdited.value = false
  } catch (e) {
    console.error('Rescore failed:', e)
  } finally {
    scoring.value = false
  }
}

async function confirmSection(section: ProposalSection) {
  const projectId = route.params.projectId as string
  if (!projectId) return
  try {
    const updated = await api.patch(`/proposal-editor/${projectId}/sections/${section.id}`, {
      is_confirmed: true,
    })
    const idx = sections.value.findIndex(s => s.id === section.id)
    if (idx >= 0) sections.value[idx] = { ...sections.value[idx], ...updated.data }
  } catch (e) {
    console.error('Confirm failed:', e)
  }
}

async function handleConfirm() {
  const projectId = route.params.projectId as string
  if (!projectId) return
  try {
    const res = await api.post(`/proposal-editor/${projectId}/confirm`)
    sections.value = res.data
  } catch (e) {
    console.error('Confirm all failed:', e)
  }
}

function selectSection(section: ProposalSection) {
  // 获取完整内容
  const projectId = route.params.projectId as string
  api.get(`/proposal-editor/${projectId}/sections/${section.id}`)
    .then(res => {
      selectedSection.value = res.data
    })
    .catch(e => console.error('Fetch detail failed:', e))
}

function openEditSection(section: ProposalSection) {
  editingSection.value = section
  // 获取最新内容
  const projectId = route.params.projectId as string
  api.get(`/proposal-editor/${projectId}/sections/${section.id}`)
    .then(res => {
      editContent.value = res.data.content
      showEditModal.value = true
    })
    .catch(e => console.error('Fetch detail failed:', e))
}

async function saveSection() {
  if (!editingSection.value) return
  savingSection.value = true
  const projectId = route.params.projectId as string
  try {
    const { data: updated } = await api.patch(
      `/proposal-editor/${projectId}/sections/${editingSection.value.id}`,
      { content: editContent.value }
    )
    const idx = sections.value.findIndex(s => s.id === editingSection.value!.id)
    if (idx >= 0) sections.value[idx] = { ...sections.value[idx], ...updated }
    editingSection.value = null
    showEditModal.value = false
    hasEdited.value = true
  } catch (e) {
    console.error('Save failed:', e)
  } finally {
    savingSection.value = false
  }
}

function goBack() {
  router.push({ name: 'BidList' })
}

onMounted(async () => {
  const projectId = route.params.projectId as string
  if (!projectId) return
  loading.value = true
  try {
    project.value = await getProject(projectId)
    await Promise.all([fetchSections(), fetchScoringRules()])
  } catch (e) {
    console.error('Load failed:', e)
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})
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
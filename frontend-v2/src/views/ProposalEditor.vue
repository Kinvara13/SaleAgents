<template>
  <div class="fade-in h-full flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <div class="flex items-center space-x-3">
        <h2 class="text-xl font-bold text-gray-800">技术建议书编辑器</h2>
        <div class="relative">
          <input
            type="text"
            v-model="selectedProjectSearch"
            placeholder="搜索项目..."
            class="w-56 px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
            @focus="showProjectDropdown = true"
            @blur="hideProjectDropdown"
          />
          <div v-if="showProjectDropdown" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-md z-10 max-h-48 overflow-y-auto">
            <div
              v-for="project in filteredProjects"
              :key="project.id"
              class="px-3 py-1.5 hover:bg-gray-100 cursor-pointer transition-all text-sm"
              @click="selectProject(project)"
            >
              {{ project.name }}
            </div>
            <div v-if="filteredProjects.length === 0" class="px-3 py-2 text-sm text-gray-400 text-center">
              无匹配项目
            </div>
          </div>
        </div>
        <span v-if="selectedProjectName" class="text-sm text-gray-500">{{ selectedProjectName }}</span>
        <span v-if="loadingProjects || loadingSections" class="text-xs text-gray-400">加载中...</span>
      </div>
      <div class="flex space-x-2">
        <button
          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all"
          @click="handleGenerate"
          :disabled="isGenerating || !selectedProjectId"
        >
          {{ isGenerating ? generationTaskStatus || '生成中...' : 'AI生成' }}
        </button>
        <button
          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all"
          @click="handleSave"
          :disabled="isSaving || !selectedSectionId"
        >
          {{ isSaving ? '保存中...' : '保存草稿' }}
        </button>
        <button
          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all"
          @click="handleRescore"
          :disabled="isScoring || !selectedProjectId || sections.length === 0"
        >
          {{ isScoring ? '评分中...' : '重新打分' }}
        </button>
        <button
          class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50"
          @click="handleConfirm"
          :disabled="isConfirming || !selectedProjectId || sections.length === 0"
        >
          {{ isConfirming ? '确认中...' : '一键完成' }}
        </button>
        <button
          class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50"
          @click="handleExport"
          :disabled="isExporting || !selectedProjectId || sections.length === 0"
        >
          {{ isExporting ? '导出中...' : '导出文档' }}
        </button>
      </div>
    </div>

    <div v-if="pageError" class="mb-4 rounded-lg border border-danger/20 bg-danger/10 px-4 py-3 text-sm text-danger">
      {{ pageError }}
    </div>
    <div v-if="pageMessage" class="mb-4 rounded-lg border border-success/20 bg-success/10 px-4 py-3 text-sm text-success">
      {{ pageMessage }}
    </div>

    <!-- Tab 切换 -->
    <div class="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
      <button
        class="px-6 py-2 text-sm font-medium rounded-md transition-all duration-200"
        :class="activeTab === 'editor' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = 'editor'"
      >
        技术建议书编写
      </button>
      <button
        class="px-6 py-2 text-sm font-medium rounded-md transition-all duration-200"
        :class="activeTab === 'star' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = 'star'"
      >
        星标项确认
      </button>
    </div>

    <!-- 技术建议书编写 Tab 内容 -->
    <div v-if="activeTab === 'editor'" class="flex-1 flex flex-col min-h-0">
      <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex">
        <!-- 左侧目录 -->
        <div :class="['border-r border-gray-100 bg-gray-50 p-4 transition-all duration-300', isLeftSidebarHidden ? 'w-0 hidden' : 'w-72']">
          <h3 class="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">目录导航</h3>
          <div v-if="loadingSections" class="text-sm text-gray-400 text-center py-4">加载章节...</div>
          <div v-else-if="sections.length === 0" class="text-sm text-gray-400 text-center py-4">
            {{ selectedProjectId ? '暂无章节，请先生成技术建议书' : '请选择一个项目' }}
          </div>
          <div v-else class="space-y-1 max-h-[200px] overflow-y-auto">
            <div
              v-for="(section, index) in sections"
              :key="section.id"
              class="flex items-center px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 transition-all text-sm"
              :class="{ 'bg-primary/10 text-primary font-medium': selectedSectionId === section.id }"
              @click="selectSection(section.id)"
            >
              <span class="mr-2 text-gray-400">{{ index + 1 }}.</span>
              <span class="flex-1">{{ section.section_name }}</span>
              <span v-if="section.is_confirmed" class="text-success text-xs">✓</span>
            </div>
          </div>

          <!-- AI智能建议 -->
          <div class="mt-6">
            <h3 class="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide flex items-center">
              <span class="mr-2">🤖</span>
              AI智能建议
            </h3>
            <div v-if="selectedSectionDetail" class="space-y-3">
              <div class="bg-white rounded-lg p-3 border border-gray-100">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="w-5 h-5 bg-success/10 text-success rounded-full flex items-center justify-center text-xs">✓</span>
                  <span class="text-sm font-medium text-gray-700">章节得分</span>
                </div>
                <p class="text-sm text-gray-500">{{ selectedSectionDetail.score }} 分</p>
              </div>
              <div class="bg-white rounded-lg p-3 border border-gray-100">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="w-5 h-5 bg-primary/10 text-primary rounded-full flex items-center justify-center text-xs">💡</span>
                  <span class="text-sm font-medium text-gray-700">状态</span>
                </div>
                <p class="text-sm text-gray-500">
                  {{ selectedSectionDetail.is_generated ? 'AI已生成' : '未生成' }}
                  {{ selectedSectionDetail.is_confirmed ? '· 已确认' : '' }}
                </p>
              </div>
            </div>
            <div v-else class="text-sm text-gray-400 text-center py-4">请选择章节查看详情</div>
          </div>
        </div>

        <!-- 中间编辑区 -->
        <div class="flex-1 flex flex-col">
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-medium text-gray-800">
              {{ selectedSectionDetail?.section_name || '技术建议书编辑' }}
            </h3>
            <button
              class="text-gray-400 hover:text-gray-600 transition-all"
              @click="toggleLeftSidebar"
            >
              {{ isLeftSidebarHidden ? '☰' : '✕' }}
            </button>
          </div>
          <div class="flex-1 p-6 overflow-auto">
            <div class="max-w-4xl mx-auto">
              <div v-if="loadingDetail" class="flex items-center justify-center h-full text-gray-400">
                <div class="text-center">
                  <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                  <p>加载中...</p>
                </div>
              </div>
              <div v-else-if="selectedSectionDetail" class="space-y-4">
                <div class="mb-6">
                  <input
                    type="text"
                    v-model="sectionTitle"
                    class="w-full text-3xl font-bold text-gray-800 border-none outline-none placeholder-gray-300 bg-transparent"
                    placeholder="请输入章节标题"
                    readonly
                  />
                </div>
                <div class="prose max-w-none">
                  <textarea
                    v-model="sectionContent"
                    class="w-full min-h-[500px] text-gray-700 border-none outline-none resize-none leading-relaxed bg-transparent"
                    placeholder="在此处开始编辑内容..."
                  ></textarea>
                </div>
              </div>
              <div v-else class="flex items-center justify-center h-full text-gray-400">
                <div class="text-center">
                  <div class="text-4xl mb-2">📝</div>
                  <p>请选择章节开始编辑</p>
                </div>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-100 bg-gray-50 p-4">
            <div v-if="scoreInfo" class="flex items-center space-x-4 text-sm">
              <span class="text-gray-600">总得分: <span class="font-bold text-primary">{{ scoreInfo.total_score }}</span></span>
              <span class="text-gray-400">|</span>
              <span class="text-gray-600">已确认: {{ scoreInfo.sections.filter(s => s.is_confirmed).length }}/{{ scoreInfo.sections.length }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧 AI 助手 -->
        <div class="w-96 border-l border-gray-100 bg-gray-50 flex flex-col">
          <!-- 选择元素按钮 -->
          <div class="p-4 border-b border-gray-100 bg-white">
            <button
              v-if="!isSelectingElement"
              class="w-full px-3 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all text-sm"
              @click="startSelectElement"
            >
              选择元素
            </button>
            <button
              v-else
              class="w-full px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-sm"
              @click="cancelSelect"
            >
              取消选择
            </button>
          </div>

          <LLMChatPanel
            ref="llmChatPanelRef"
            class="flex-1 min-h-0"
            title="AI助手"
            :projectId="selectedProjectId || undefined"
            :body="chatBody"
            placeholder="输入修改需求..."
            emptyText="发送消息开始对话，我可以帮你优化技术建议书"
            :showClear="true"
            :inputRows="3"
            :autoFocus="false"
          >
            <template #input-suffix>
              <div class="flex items-center justify-end px-3 py-2 border-t border-gray-100 space-x-2">
                <select
                  v-model="selectedAIModel"
                  class="px-2 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm text-gray-700"
                >
                  <option v-for="cfg in aiConfigs" :key="cfg.id" :value="cfg.model">
                    {{ cfg.name }}
                  </option>
                </select>
              </div>
            </template>
          </LLMChatPanel>
        </div>
      </div>
    </div>

    <!-- 星标项确认 Tab 内容 -->
    <div v-else class="flex-1 flex space-x-6 min-h-0">
      <!-- 左侧：星标项列表 -->
      <div class="w-1/3 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div class="p-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
          <h3 class="font-medium text-gray-800">星标项列表</h3>
          <div class="flex items-center space-x-2">
            <span v-if="areAllStarItemsConfirmed && !hasUnsatisfiedItems" class="text-success text-xs font-medium">全部满足 ✅</span>
            <span v-else-if="areAllStarItemsConfirmed && hasUnsatisfiedItems" class="text-danger text-xs font-medium">存在不满足 ❌</span>
          </div>
        </div>
        <div class="flex-1 overflow-auto p-3 space-y-2">
          <div v-if="starItems.length === 0" class="text-sm text-gray-400 text-center py-4">
            {{ selectedProjectId ? '该项目暂无星标项' : '请选择一个项目' }}
          </div>
          <div
            v-for="(item, index) in starItems"
            :key="index"
            class="p-4 border rounded-lg transition-all cursor-pointer group"
            :class="[
              selectedStarItem?.name === item.name ? 'border-primary bg-primary/5' : 'border-gray-100 hover:border-primary/30',
            ]"
            @click="selectStarItem(item)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium transition-colors" :class="selectedStarItem?.name === item.name ? 'text-primary' : 'text-gray-800'">{{ item.name }}</p>
                <p class="text-xs text-gray-500 mt-1 flex items-center">
                  <span class="mr-1">📄</span> {{ item.source }}
                </p>
              </div>
              <div class="flex flex-col items-end space-y-2">
                <div class="flex space-x-1">
                  <button
                    class="w-6 h-6 flex items-center justify-center rounded-full border transition-all text-xs"
                    :class="item.satisfied === true ? 'bg-success text-white border-success' : 'border-gray-200 text-gray-400 hover:bg-success/10'"
                    @click.stop="item.satisfied = true"
                    title="满足"
                  >
                    ✓
                  </button>
                  <button
                    class="w-6 h-6 flex items-center justify-center rounded-full border transition-all text-xs"
                    :class="item.satisfied === false ? 'bg-danger text-white border-danger' : 'border-gray-200 text-gray-400 hover:bg-danger/10'"
                    @click.stop="item.satisfied = false"
                    title="不满足"
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对应应答文字 -->
      <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div class="p-4 border-b border-gray-100 bg-gray-50">
          <h3 class="font-medium text-gray-800">标书应答内容</h3>
        </div>
        <div class="flex-1 overflow-auto p-8">
          <div v-if="selectedStarItem" class="max-w-3xl mx-auto space-y-6">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-1 bg-primary/10 text-primary text-xs font-bold rounded">应答章节</span>
              <span class="text-gray-800 font-bold">{{ selectedStarItem.name }}</span>
            </div>

            <div class="bg-gray-50 rounded-xl p-6 border border-gray-100 relative">
              <div class="absolute -top-3 left-6 px-3 py-1 bg-white border border-gray-100 rounded-full text-xs text-gray-400 font-medium">
                应答详情
              </div>
              <pre class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed font-sans">{{ starItemDetail?.content || '暂无对应应答文字内容，请在编辑器中编写。' }}</pre>
            </div>

            <div class="flex justify-end space-x-3">
              <button
                class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                @click="activeTab = 'editor'"
              >
                前往编辑
              </button>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            <div class="text-center">
              <div class="text-5xl mb-4">🔍</div>
              <p>请点击左侧星标项查看对应应答文字</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  listProjects,
  getTenderSections,
  getTenderSectionDetail,
  type Project,
  type TenderSection,
} from '../services/project'
import {
  listProposalSections,
  getProposalSectionDetail,
  updateProposalSection,
  generateProposal,
  scoreProposal,
  rescoreProposal,
  confirmProposal,
  exportProposalDocx,
  getTaskStatus,
  type ProposalSectionSummary,
  type ProposalSectionDetail,
} from '../services/proposal'
import { listAIConfigs, type AIConfig } from '../services/settings'
import LLMChatPanel from '../components/LLMChatPanel.vue'

// ============ 项目选择 ============
const route = useRoute()
const selectedProjectSearch = ref('')
const selectedProjectId = ref('')
const selectedProjectName = ref('')
const showProjectDropdown = ref(false)
const projects = ref<Project[]>([])
const loadingProjects = ref(false)
const pageError = ref('')
const pageMessage = ref('')

const filteredProjects = computed(() => {
  if (!selectedProjectSearch.value) return projects.value
  return projects.value.filter(p =>
    p.name.toLowerCase().includes(selectedProjectSearch.value.toLowerCase())
  )
})

async function loadProjects() {
  loadingProjects.value = true
  pageError.value = ''
  try {
    projects.value = await listProjects()
    const routeProjectId = route.params.projectId as string | undefined
    if (routeProjectId && !selectedProjectId.value) {
      const matched = projects.value.find(p => p.id === routeProjectId)
      if (matched) {
        selectProject(matched)
      }
    }
  } catch (e: any) {
    console.error('加载项目列表失败:', e)
    pageError.value = e.message || '加载项目列表失败'
  } finally {
    loadingProjects.value = false
  }
}

function selectProject(project: Project) {
  selectedProjectSearch.value = project.name
  selectedProjectName.value = project.name
  selectedProjectId.value = project.id
  showProjectDropdown.value = false
  loadProposalSections(project.id)
  loadStarItems(project.id)
}

const hideProjectDropdown = () => {
  setTimeout(() => {
    showProjectDropdown.value = false
  }, 200)
}

// ============ 技术建议书章节 ============
const sections = ref<ProposalSectionSummary[]>([])
const selectedSectionId = ref('')
const sectionDetail = ref<ProposalSectionDetail | null>(null)
const loadingSections = ref(false)
const loadingDetail = ref(false)
const isSaving = ref(false)
const isGenerating = ref(false)
const isScoring = ref(false)
const isConfirming = ref(false)
const isExporting = ref(false)
const generationTaskStatus = ref('')
const scoreInfo = ref<{ sections: ProposalSectionSummary[]; total_score: number } | null>(null)

const sectionTitle = computed(() => sectionDetail.value?.section_name || '')
const sectionContent = ref('')

const selectedSectionDetail = computed(() => {
  if (!selectedSectionId.value) return null
  return sections.value.find(s => s.id === selectedSectionId.value) || null
})

async function loadProposalSections(projectId: string) {
  loadingSections.value = true
  sections.value = []
  selectedSectionId.value = ''
  sectionDetail.value = null
  sectionContent.value = ''
  scoreInfo.value = null
  try {
    sections.value = await listProposalSections(projectId)
    if (sections.value.length > 0) {
      await selectSection(sections.value[0].id)
    }
    // 同时加载评分
    try {
      scoreInfo.value = await scoreProposal(projectId)
    } catch (e) {
      console.error('加载评分失败:', e)
    }
  } catch (e: any) {
    console.error('加载章节列表失败:', e)
    pageError.value = e.message || '加载章节列表失败'
  } finally {
    loadingSections.value = false
  }
}

async function selectSection(sectionId: string) {
  selectedSectionId.value = sectionId
  if (!selectedProjectId.value) return
  loadingDetail.value = true
  try {
    sectionDetail.value = await getProposalSectionDetail(selectedProjectId.value, sectionId)
    sectionContent.value = sectionDetail.value.content || ''
  } catch (e: any) {
    console.error('加载章节详情失败:', e)
    pageError.value = e.message || '加载章节详情失败'
  } finally {
    loadingDetail.value = false
  }
}

async function handleSave() {
  if (!selectedProjectId.value || !selectedSectionId.value) return
  isSaving.value = true
  pageError.value = ''
  pageMessage.value = ''
  try {
    const updated = await updateProposalSection(
      selectedProjectId.value,
      selectedSectionId.value,
      { content: sectionContent.value }
    )
    sectionDetail.value = updated
    // 更新列表中的章节信息
    const idx = sections.value.findIndex(s => s.id === selectedSectionId.value)
    if (idx >= 0) {
      sections.value[idx] = { ...sections.value[idx], is_confirmed: updated.is_confirmed, score: updated.score }
    }
    pageMessage.value = '草稿已保存'
  } catch (e: any) {
    console.error('保存失败:', e)
    pageError.value = '保存失败: ' + (e.message || '未知错误')
  } finally {
    isSaving.value = false
  }
}

async function saveCurrentSection(): Promise<boolean> {
  if (!selectedProjectId.value || !selectedSectionId.value) return true
  isSaving.value = true
  try {
    const updated = await updateProposalSection(
      selectedProjectId.value,
      selectedSectionId.value,
      { content: sectionContent.value }
    )
    sectionDetail.value = updated
    const idx = sections.value.findIndex(s => s.id === selectedSectionId.value)
    if (idx >= 0) {
      sections.value[idx] = { ...sections.value[idx], is_confirmed: updated.is_confirmed, score: updated.score }
    }
    return true
  } catch (e: any) {
    pageError.value = '保存失败: ' + (e.message || '未知错误')
    return false
  } finally {
    isSaving.value = false
  }
}

async function handleGenerate() {
  if (!selectedProjectId.value) return
  if (!window.confirm('生成会覆盖当前 AI 已生成章节，确认继续？')) return
  isGenerating.value = true
  pageError.value = ''
  pageMessage.value = ''
  generationTaskStatus.value = '提交中...'
  try {
    const result = await generateProposal(selectedProjectId.value)
    generationTaskStatus.value = result.message || '处理中...'
    let completed = false
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 2000))
      const task = await getTaskStatus(result.task_id)
      if (task.status === 'completed') {
        completed = true
        break
      }
      if (task.status === 'failed') {
        throw new Error(task.error_message || '生成任务失败')
      }
      generationTaskStatus.value = `生成中 ${i + 1}/60`
    }
    if (!completed) {
      throw new Error('生成任务超时，请稍后刷新查看结果')
    }
    await loadProposalSections(selectedProjectId.value)
    pageMessage.value = '技术建议书已生成'
  } catch (e: any) {
    console.error('生成失败:', e)
    pageError.value = '生成失败: ' + (e.message || '未知错误')
  } finally {
    isGenerating.value = false
    generationTaskStatus.value = ''
  }
}

async function handleRescore() {
  if (!selectedProjectId.value) return
  isScoring.value = true
  pageError.value = ''
  pageMessage.value = ''
  try {
    if (selectedSectionId.value) {
      const saved = await saveCurrentSection()
      if (!saved) return
    }
    scoreInfo.value = await rescoreProposal(selectedProjectId.value)
    sections.value = scoreInfo.value.sections
    if (selectedSectionId.value) {
      await selectSection(selectedSectionId.value)
    }
    pageMessage.value = '已完成重新打分'
  } catch (e: any) {
    pageError.value = '重新打分失败: ' + (e.message || '未知错误')
  } finally {
    isScoring.value = false
  }
}

async function handleConfirm() {
  if (!selectedProjectId.value) return
  if (!window.confirm('确认后将把全部章节标记为已完成，是否继续？')) return
  isConfirming.value = true
  pageError.value = ''
  pageMessage.value = ''
  try {
    if (selectedSectionId.value) {
      const saved = await saveCurrentSection()
      if (!saved) return
    }
    sections.value = await confirmProposal(selectedProjectId.value)
    scoreInfo.value = await scoreProposal(selectedProjectId.value)
    pageMessage.value = '全部章节已确认'
  } catch (e: any) {
    pageError.value = '确认失败: ' + (e.message || '未知错误')
  } finally {
    isConfirming.value = false
  }
}

async function handleExport() {
  if (!selectedProjectId.value) return
  isExporting.value = true
  pageError.value = ''
  pageMessage.value = ''
  try {
    if (selectedSectionId.value) {
      const saved = await saveCurrentSection()
      if (!saved) return
    }
    const blob = await exportProposalDocx(selectedProjectId.value)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedProjectName.value || '项目'}_技术建议书.docx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    pageMessage.value = '技术建议书已导出'
  } catch (e: any) {
    pageError.value = '导出失败: ' + (e.message || '未知错误')
  } finally {
    isExporting.value = false
  }
}

// ============ 左侧边栏 ============
const isLeftSidebarHidden = ref(false)
const toggleLeftSidebar = () => {
  isLeftSidebarHidden.value = !isLeftSidebarHidden.value
}

// ============ 选择元素 ============
const isSelectingElement = ref(false)
const selectedElement = ref<{ element: string; text: string } | null>(null)

const startSelectElement = () => {
  isSelectingElement.value = true
  selectedElement.value = null
}

const cancelSelect = () => {
  isSelectingElement.value = false
  selectedElement.value = null
}

// ============ AI 助手 ============
const aiConfigs = ref<AIConfig[]>([])
const selectedAIModel = ref('')
const llmChatPanelRef = ref<InstanceType<typeof LLMChatPanel> | null>(null)

const chatBody = computed(() => {
  if (selectedAIModel.value) {
    return { model: selectedAIModel.value }
  }
  return undefined
})

async function loadAIConfigs() {
  try {
    aiConfigs.value = await listAIConfigs()
    const active = aiConfigs.value.find(c => c.is_active)
    if (active) {
      selectedAIModel.value = active.model
    } else if (aiConfigs.value.length > 0) {
      selectedAIModel.value = aiConfigs.value[0].model
    }
  } catch (e) {
    console.error('加载AI配置失败:', e)
  }
}

// ============ 星标项 ============
const tenderSections = ref<TenderSection[]>([])
const selectedStarItem = ref<{ name: string; source: string; satisfied: boolean | null; sectionId: string } | null>(null)
const starItemDetail = ref<any>(null)

const starItems = computed(() => {
  return tenderSections.value
    .filter(s => s.is_star_item)
    .map(s => ({
      name: s.section_name,
      source: s.source_file || '招标文件',
      satisfied: null as boolean | null,
      sectionId: s.id,
    }))
})

const areAllStarItemsConfirmed = computed(() => {
  return starItems.value.length > 0 && starItems.value.every(item => item.satisfied !== null)
})

const hasUnsatisfiedItems = computed(() => {
  return starItems.value.some(item => item.satisfied === false)
})

async function loadStarItems(projectId: string) {
  try {
    const data = await getTenderSections(projectId)
    tenderSections.value = data || []
  } catch (e) {
    console.error('加载星标项失败:', e)
    tenderSections.value = []
  }
}

const selectStarItem = async (item: { name: string; source: string; satisfied: boolean | null; sectionId: string }) => {
  selectedStarItem.value = item
  if (item.sectionId && selectedProjectId.value) {
    try {
      starItemDetail.value = await getTenderSectionDetail(selectedProjectId.value, item.sectionId)
    } catch (e) {
      console.error('加载星标项详情失败:', e)
    }
  }
}

// ============ Tab ============
const activeTab = ref('editor')

// ============ 初始化 ============
onMounted(() => {
  loadProjects()
  loadAIConfigs()
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

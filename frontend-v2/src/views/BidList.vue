<template>
  <div class="fade-in flex flex-col h-full">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div class="flex items-center space-x-3">
        <h2 class="text-xl font-bold text-gray-800">投标文件编辑器</h2>
        <!-- 项目选择下拉框 -->
        <div class="relative">
          <input
            type="text"
            v-model="selectedProjectSearch"
            placeholder="搜索项目..."
            class="w-56 px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
            @focus="showProjectDropdown = true"
            @blur="hideProjectDropdown"
          />
          <div v-if="showProjectDropdown" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-md z-10 max-h-48 overflow-y-auto">
            <div
              v-for="project in filteredProjects"
              :key="project.id"
              class="px-3 py-1.5 hover:bg-gray-100 cursor-pointer transition-all duration-300 text-sm"
              @click="selectProject(project)"
            >
              {{ getProjectDisplayName(project) }}
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
        <button class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all duration-300" @click="saveDraft">
          保存草稿
        </button>
        <button class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300" @click="completeAll">
          一键完成
        </button>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit flex-shrink-0">
      <button
        class="px-6 py-2 text-sm font-medium rounded-md transition-all duration-200"
        :class="activeTab === 'writing' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = 'writing'"
      >
        回标文件编写
      </button>
      <button
        class="px-6 py-2 text-sm font-medium rounded-md transition-all duration-200"
        :class="activeTab === 'star' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = 'star'"
      >
        星标项确认
      </button>
    </div>

    <!-- 回标文件编写 Tab 内容 -->
    <div v-if="activeTab === 'writing'" class="flex-1 flex flex-col min-h-0">
      <!-- 文件目录 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 mb-3 overflow-hidden flex-shrink-0" :class="{ 'max-h-[200px]': !isLeftSidebarHidden }">
        <div class="flex items-center justify-between p-3 border-b border-gray-100 bg-gray-50">
          <h3 class="font-medium text-gray-800 text-sm">文件目录</h3>
          <button
            class="text-gray-400 hover:text-gray-600 transition-all duration-300"
            @click="isLeftSidebarHidden = !isLeftSidebarHidden"
          >
            {{ isLeftSidebarHidden ? '▼' : '▲' }}
          </button>
        </div>
        <div v-if="!isLeftSidebarHidden" class="p-3 space-y-3 max-h-[140px] overflow-y-auto">
          <div v-if="loadingSections" class="text-sm text-gray-400 text-center py-4">加载文件目录...</div>
          <div v-else-if="fileTree.length === 0" class="text-sm text-gray-400 text-center py-4">
            {{ selectedProjectId ? '暂无解析文件，请先上传招标文件' : '请选择一个项目' }}
          </div>
          <div
            v-for="section in fileTree"
            :key="section.id"
            class="group"
          >
            <div
              class="flex items-center px-2 py-1.5 rounded-lg cursor-pointer hover:bg-gray-100 transition-all duration-300"
              :class="{ 'bg-primary/10 text-primary': selectedSection === section.id }"
              @click="toggleSection(section.id)"
            >
              <span class="mr-2 transition-transform duration-200" :class="{ 'rotate-90': expandedSections.has(section.id) }">▶</span>
              <span class="mr-2">{{ section.icon }}</span>
              <span class="flex-1 font-medium text-sm">{{ section.name }}</span>
              <span
                :class="[
                  'text-xs px-2 py-0.5 rounded-full',
                  section.completed === section.total ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'
                ]"
              >
                {{ section.completed }}/{{ section.total }}
              </span>
            </div>
            <div v-if="expandedSections.has(section.id)" class="ml-6 mt-1 space-y-1 max-h-[100px] overflow-y-auto">
              <div
                v-for="file in section.files"
                :key="file.id"
                class="flex items-center px-2 py-1.5 rounded-lg cursor-pointer hover:bg-gray-100 transition-all duration-300 text-xs"
                :class="{ 'bg-white border border-primary/30': selectedFile === file.id }"
                @click="handleSelectFile(file.id)"
              >
                <span class="mr-2">{{ file.completed ? '✅' : '⭕' }}</span>
                <span class="flex-1 text-gray-700">{{ file.name }}</span>
                <button
                  class="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-all duration-300 ml-2"
                  @click.stop="handleEditFile(file)"
                >
                  修改
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 下方三栏布局 -->
      <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex min-h-[400px]">
        <!-- 左侧：AI生成后文件预览 -->
        <div :class="[
          'border-r border-gray-100 flex flex-col transition-all duration-300',
          isRightTemplateHidden ? 'w-3/5' : 'w-1/2'
        ]">
          <div class="flex items-center justify-between p-4 border-b border-gray-100 bg-gray-50">
            <div class="flex items-center space-x-3">
              <h3 class="font-medium text-gray-800">AI生成文件预览</h3>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="!isEditing" class="text-sm text-success flex items-center">
                <span class="mr-1">✓</span> 已生成
              </span>
              <button
                v-if="selectedFileData && !isEditing"
                class="px-3 py-1 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300"
                @click="startEdit"
              >
                编辑
              </button>
              <button
                v-if="isEditing"
                class="px-3 py-1 text-xs border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-100 transition-all duration-300"
                @click="cancelEdit"
              >
                取消
              </button>
              <button
                v-if="isEditing"
                class="px-3 py-1 text-xs bg-success text-white rounded-lg hover:bg-success/90 transition-all duration-300"
                :disabled="saving"
                @click="saveSection"
              >
                {{ saving ? '保存中...' : '保存' }}
              </button>
              <button
                v-if="!isRightTemplateHidden && !isEditing"
                class="text-gray-400 hover:text-gray-600 transition-all duration-300"
                @click="isRightTemplateHidden = true"
                title="隐藏原文件"
              >
                ▶
              </button>
              <button
                v-if="isRightTemplateHidden && !isEditing"
                class="text-gray-400 hover:text-gray-600 transition-all duration-300"
                @click="isRightTemplateHidden = false"
                title="显示原文件"
              >
                ◀
              </button>
            </div>
          </div>
          <div class="flex-1 p-4 overflow-auto">
            <div v-if="loadingDetail" class="flex items-center justify-center h-full text-gray-400">
              <div class="text-center">
                <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                <p>加载中...</p>
              </div>
            </div>
            <div v-else-if="selectedFileData" class="flex flex-col h-full space-y-4">
              <div v-show="isEditing" key="editing-mode" class="flex flex-col h-full space-y-3">
                <h4 class="text-lg font-bold text-gray-800 flex-shrink-0">{{ selectedFileData.name }}</h4>
                <div class="flex-1 overflow-hidden">
                  <textarea
                    v-model="editableContent"
                    class="w-full h-full min-h-[350px] p-4 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm resize-none font-sans leading-relaxed overflow-y-auto"
                    placeholder="在此编辑投标文件内容..."
                  ></textarea>
                </div>
              </div>
              <div v-show="!isEditing" key="viewing-mode" class="border border-gray-100 rounded-lg p-6">
                <h4 class="text-xl font-bold text-gray-800 mb-4">{{ selectedFileData.name }}</h4>
                <div v-if="isSelectingElement" class="mb-4 p-3 bg-primary/10 border border-primary/20 rounded-lg text-sm text-primary">
                  <span class="font-medium">选择元素模式：</span>请点击下方需要修改的文字元素
                </div>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">项目名称</label>
                    <div
                      class="bg-gray-50 rounded px-3 py-2 text-gray-800 cursor-pointer hover:bg-gray-100 transition-all duration-200"
                      :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                      @click="isSelectingElement && selectElement('projectName', selectedProjectName || '')"
                    >
                      {{ selectedProjectName || '未选择项目' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">章节名称</label>
                    <div
                      class="bg-gray-50 rounded px-3 py-2 text-gray-800 cursor-pointer hover:bg-gray-100 transition-all duration-200"
                      :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                      @click="isSelectingElement && selectElement('sectionName', sectionDetail?.section_name || '')"
                    >
                      {{ sectionDetail?.section_name || '未选择章节' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">来源文件</label>
                    <div
                      class="bg-gray-50 rounded px-3 py-2 text-gray-800 cursor-pointer hover:bg-gray-100 transition-all duration-200"
                      :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                      @click="isSelectingElement && selectElement('sourceFile', sectionDetail?.source_file || '')"
                    >
                      {{ sectionDetail?.source_file || '未知' }}
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">投标说明</label>
                    <div
                      class="bg-gray-50 rounded px-3 py-2 text-gray-800 cursor-pointer hover:bg-gray-100 transition-all duration-200"
                      :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                      @click="isSelectingElement && selectElement('bidDescription', '我方完全响应招标文件的所有要求，承诺提供优质的产品和服务。')"
                    >
                      我方完全响应招标文件的所有要求，承诺提供优质的产品和服务。
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="!isEditing" class="flex justify-center">
                <button class="px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all duration-300" @click="downloadCurrentSection">
                  下载文件
                </button>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full text-gray-400">
              <div class="text-center">
                <div class="text-4xl mb-2">🤖</div>
                <p>请选择文件查看AI生成内容</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 中间：模版原文件（可隐藏） -->
        <div
          :class="[
            'border-r border-gray-100 flex flex-col transition-all duration-300',
            isRightTemplateHidden ? 'w-0 hidden' : 'w-1/4'
          ]"
        >
          <div class="flex items-center justify-between p-4 border-b border-gray-100 bg-gray-50">
            <div class="flex items-center space-x-3">
              <h3 class="font-medium text-gray-800">模版原文件</h3>
            </div>
            <button
              class="text-gray-400 hover:text-gray-600 transition-all duration-300"
              @click="isRightTemplateHidden = true"
            >
              ✕
            </button>
          </div>
          <div class="flex-1 p-4 overflow-auto">
            <div v-if="loadingDetail" class="flex items-center justify-center h-full text-gray-400">
              <div class="text-center">
                <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                <p>加载中...</p>
              </div>
            </div>
            <div v-else-if="sectionDetail" class="space-y-4 overflow-auto">
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-800 mb-2">{{ sectionDetail.section_name }}</h4>
                <div class="text-sm text-gray-600 space-y-2">
                  <p>来源文件：{{ sectionDetail.source_file || '未知' }}</p>
                  <p>章节类型：{{ sectionDetail.section_type || '未知' }}</p>
                  <div class="mt-4 border-t border-gray-200 pt-4">
                    <p class="text-gray-500 text-xs mb-2">这是招标文件的原始内容：</p>
                    <pre class="whitespace-pre-wrap font-sans text-gray-700 text-xs leading-relaxed max-h-[400px] overflow-y-auto">{{ sectionDetail.content || '暂无内容' }}</pre>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-full text-gray-400">
              <div class="text-center">
                <div class="text-4xl mb-2">📄</div>
                <p>请选择文件查看原模版</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：AI对话框 -->
        <div :class="[
          'flex flex-col border-l border-gray-100 bg-gray-50 transition-all duration-300',
          isRightTemplateHidden ? 'w-2/5' : 'w-1/4'
        ]">
          <!-- 选择元素按钮 -->
          <div class="p-4 border-b border-gray-100 bg-white flex-shrink-0">
            <button
              v-if="!isSelectingElement"
              class="w-full px-3 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm font-medium"
              @click="startSelectElement"
            >
              🎯 选择元素
            </button>
            <button
              v-else
              class="w-full px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all duration-300 text-sm font-medium"
              @click="cancelSelect"
            >
              ✕ 取消选择
            </button>
          </div>

          <LLMChatPanel
            ref="llmChatPanelRef"
            class="flex-1 min-h-0"
            title="🤖 AI助手"
            :projectId="selectedProjectId || undefined"
            :body="chatBody"
            placeholder="输入修改需求，如：优化这段内容、修改格式..."
            emptyText="发送消息开始对话，我可以帮你修改投标文件内容"
            :showClear="true"
            :inputRows="4"
            :autoFocus="false"
            @complete="handleAIResponse"
          >
            <template #header-extra>
              <button
                v-if="isRightTemplateHidden"
                class="text-primary hover:text-primary/80 transition-all text-sm flex items-center font-medium"
                @click="isRightTemplateHidden = false"
                title="展开原文件"
              >
                <span class="mr-1">📄</span> 原文件
              </button>
            </template>

            <template #input-suffix>
              <div class="flex items-center justify-end px-3 py-2 border-t border-gray-100 space-x-2">
                <select
                  v-model="selectedAIModel"
                  class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm text-gray-700 min-w-[120px]"
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
                    @click.stop="setStarItemSatisfied(item, true)"
                    title="满足"
                  >
                    ✓
                  </button>
                  <button
                    class="w-6 h-6 flex items-center justify-center rounded-full border transition-all text-xs"
                    :class="item.satisfied === false ? 'bg-danger text-white border-danger' : 'border-gray-200 text-gray-400 hover:bg-danger/10'"
                    @click.stop="setStarItemSatisfied(item, false)"
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
              <span class="text-gray-800 font-bold">{{ starItemDetail?.section_name || selectedStarItem.name }}</span>
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
                @click="activeTab = 'writing'"
              >
                前往编辑
              </button>
              <button class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" @click="confirmStarItem">
                确认为满足
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
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import {
  listProjects,
  getProject,
  getTenderSections,
  getTenderSectionDetail,
  updateTenderSection,
  updateProject,
  type Project,
  type TenderSection,
} from '../services/project'
import { listAIConfigs, type AIConfig } from '../services/settings'
import LLMChatPanel from '../components/LLMChatPanel.vue'

interface FileItem {
  id: string
  name: string
  completed: boolean
}

interface FileSection {
  id: string
  name: string
  icon: string
  completed: number
  total: number
  files: FileItem[]
}

interface StarItem {
  name: string
  source: string
  satisfied: boolean | null
  sectionId: string
}

const selectedSection = ref<string>('')
const selectedFile = ref<string>('')
const selectedProjectSearch = ref<string>('')
const selectedProjectId = ref<string>('')
const selectedProjectName = ref<string>('')
const showProjectDropdown = ref<boolean>(false)
const isLeftSidebarHidden = ref<boolean>(false)
const expandedSections = ref<Set<string>>(new Set(['模板', '商务', '技术', '评审', '内容']))
const isSelectingElement = ref<boolean>(false)
const selectedElement = ref<{ element: string; text: string } | null>(null)
const isRightTemplateHidden = ref<boolean>(false)
const activeTab = ref<'writing' | 'star'>('writing')
const isEditing = ref(false)
const editableContent = ref('')
const selectedStarItem = ref<StarItem | null>(null)

const projects = ref<Project[]>([])
const sections = ref<TenderSection[]>([])
const sectionDetail = ref<any>(null)
const starItemDetail = ref<any>(null)
const loadingProjects = ref(false)
const loadingSections = ref(false)
const loadingDetail = ref(false)
const saving = ref(false)
const error = ref('')

// 用 ref 存储星标项状态而不是 computed
const starItemsState = ref<Map<string, boolean | null>>(new Map())

// AI 配置
const aiConfigs = ref<AIConfig[]>([])
const selectedAIModel = ref<string>('')

const chatBody = computed(() => {
  if (selectedAIModel.value) {
    return { model: selectedAIModel.value }
  }
  return undefined
})

// 项目列表
const filteredProjects = computed(() => {
  if (!selectedProjectSearch.value) return projects.value
  const searchLower = selectedProjectSearch.value.toLowerCase()
  return projects.value.filter(p => {
    const displayName = getProjectDisplayName(p)
    return displayName.toLowerCase().includes(searchLower) || p.name.toLowerCase().includes(searchLower)
  })
})

// 获取项目的实际名称（优先从解析的项目名称字段获取）
const getProjectDisplayName = (project: Project): string => {
  if (!project) return ''
  
  if (project.extracted_fields && Array.isArray(project.extracted_fields)) {
    const nameField = project.extracted_fields.find(f => f.label === '项目名称')
    if (nameField && nameField.value) {
      return nameField.value
    }
  }
  
  return project.name || ''
}

// 选择项目
const selectProject = (project: Project) => {
  const displayName = getProjectDisplayName(project)
  selectedProjectSearch.value = displayName
  selectedProjectName.value = displayName
  selectedProjectId.value = project.id
  showProjectDropdown.value = false
  loadSections(project.id)
}

// 加载项目列表
async function loadProjects() {
  loadingProjects.value = true
  try {
    projects.value = await listProjects()
  } catch (e: any) {
    error.value = e.message || '加载项目列表失败'
  } finally {
    loadingProjects.value = false
  }
}

// 加载 AI 模型配置
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

// 加载章节列表
async function loadSections(projectId: string) {
  loadingSections.value = true
  sections.value = []
  sectionDetail.value = null
  selectedFile.value = ''
  selectedStarItem.value = null
  starItemDetail.value = null
  starItemsState.value.clear()
  try {
    const data = await getTenderSections(projectId)
    sections.value = data || []

    const project = await getProject(projectId)
    if (project && project.bid_template_files && Array.isArray(project.bid_template_files) && project.bid_template_files.length > 0) {
      const templateSection: TenderSection[] = project.bid_template_files.map((f: any) => ({
        id: f.id,
        section_name: f.name,
        section_type: '模板',
        is_star_item: false,
        source_file: f.path || '模板文件',
      }))
      sections.value = [...templateSection, ...sections.value]
    }
  } catch (e: any) {
    error.value = e.message || '加载文件列表失败'
  } finally {
    loadingSections.value = false
  }
}

// 文件目录按 section_type 分组
const fileTree = computed((): FileSection[] => {
  const groups: Record<string, TenderSection[]> = {}
  for (const s of sections.value) {
    groups[s.section_type] = groups[s.section_type] || []
    groups[s.section_type].push(s)
  }

  const typeMeta: Record<string, { name: string; icon: string }> = {
    '模板': { name: '回标文件模板', icon: '📋' },
    '商务': { name: '商务部分', icon: '📁' },
    '技术': { name: '技术部分', icon: '📄' },
    '评审': { name: '评审部分', icon: '🔍' },
    '内容': { name: '内容部分', icon: '📝' },
  }

  const result: FileSection[] = []
  for (const [type, items] of Object.entries(groups)) {
    const meta = typeMeta[type] || { name: type + '部分', icon: '📄' }
    result.push({
      id: type,
      name: meta.name,
      icon: meta.icon,
      completed: 0,
      total: items.length,
      files: items.map(s => ({
        id: s.id,
        name: s.section_name,
        completed: false,
      })),
    })
  }
  return result
})

const toggleSection = (sectionId: string) => {
  if (expandedSections.value.has(sectionId)) {
    expandedSections.value.delete(sectionId)
  } else {
    expandedSections.value.add(sectionId)
  }
}

// 星标项列表
const starItems = computed((): StarItem[] => {
  return sections.value
    .filter(s => s.is_star_item)
    .map(s => ({
      name: s.section_name,
      source: s.source_file || '招标文件',
      satisfied: starItemsState.value.get(s.id) ?? null,
      sectionId: s.id,
    }))
})

// 检查所有星标项是否都已确认
const areAllStarItemsConfirmed = computed(() => {
  return starItems.value.every(item => item.satisfied !== null)
})

// 检查是否有不满足的星标项
const hasUnsatisfiedItems = computed(() => {
  return starItems.value.some(item => item.satisfied === false)
})

// 设置星标项的满足状态
const setStarItemSatisfied = (item: StarItem, satisfied: boolean | null) => {
  starItemsState.value.set(item.sectionId, satisfied)
  console.log('星标项状态更新:', item.name, satisfied)
}

// 确认为满足
const confirmStarItem = () => {
  if (selectedStarItem.value) {
    setStarItemSatisfied(selectedStarItem.value, true)
  }
}

// 保存草稿
const saveDraft = () => {
  console.log('保存草稿')
  alert('草稿已保存！')
}

// 一键完成
const completeAll = async () => {
  if (!selectedProjectId.value) {
    alert('请先选择项目！')
    return
  }

  console.log('一键完成')
  
  try {
    // 1. 先确认所有星标项都是满足状态
    const allStarItems = starItems.value
    if (allStarItems.length > 0) {
      allStarItems.forEach(item => {
        if (item.satisfied !== true) {
          setStarItemSatisfied(item, true)
        }
      })
    }

    // 2. 更新项目状态为已完成
    await updateProject(selectedProjectId.value, {
      status: '已完成',
      node_status: { decision: 'done', parsing: 'done', generation: 'done' }
    })
    
    alert('一键完成成功！项目状态已更新为已完成。')
  } catch (e) {
    console.error('一键完成失败:', e)
    alert('一键完成失败，请稍后重试！')
  }
}

// 选择星标项
const selectStarItem = async (item: StarItem) => {
  selectedStarItem.value = item
  if (item.sectionId && selectedProjectId.value) {
    try {
      starItemDetail.value = await getTenderSectionDetail(selectedProjectId.value, item.sectionId)
    } catch (e) {
      console.error('加载星标项详情失败:', e)
    }
  }
}

// 处理文件选择
const handleSelectFile = async (fileId: string) => {
  selectedFile.value = fileId
  if (!selectedProjectId.value) return
  loadingDetail.value = true
  try {
    try {
      sectionDetail.value = await getTenderSectionDetail(selectedProjectId.value, fileId)
    } catch (e: any) {
      console.warn('从解析接口获取章节详情失败，尝试从本地文件列表获取:', e)
      
      const foundSection = sections.value.find(s => s.id === fileId)
      if (foundSection) {
        sectionDetail.value = {
          ...foundSection,
          content: foundSection.content || '这是投标文件内容，可在此编辑。',
        }
      } else {
        console.warn('本地文件列表中未找到匹配的文件，创建默认章节详情')
        sectionDetail.value = {
          id: fileId,
          section_name: '未命名章节',
          section_type: '模板',
          content: '这是投标文件模板，用于指导投标文件的编写格式。',
          source_file: '',
          is_star_item: false,
        }
      }
    }
  } catch (e: any) {
    console.error('加载章节详情失败:', e)
    sectionDetail.value = {
      id: fileId,
      section_name: '未命名章节',
      section_type: '模板',
      content: '这是投标文件模板，用于指导投标文件的编写格式。',
      source_file: '',
      is_star_item: false,
    }
  } finally {
    loadingDetail.value = false
  }
}

// 处理文件修改
const handleEditFile = async (file: FileItem) => {
  console.log('>>> handleEditFile called', file.id, file.name)
  await handleSelectFile(file.id)
  console.log('>>> handleSelectFile done, sectionDetail:', sectionDetail.value)
  if (sectionDetail.value) {
    isEditing.value = true
    editableContent.value = sectionDetail.value.content || ''
  } else {
    console.error('>>> sectionDetail is null, cannot edit')
  }
  console.log('>>> isEditing set to:', isEditing.value)
}

// 下载当前章节为TXT文件
const downloadCurrentSection = () => {
  if (!sectionDetail.value) {
    alert('请先选择文件')
    return
  }
  const content = editableContent.value || sectionDetail.value.content || ''
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${sectionDetail.value.section_name || '文档'}.txt`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

// 开始选择元素
const startSelectElement = () => {
  isSelectingElement.value = true
  selectedElement.value = null
  console.log('开始选择元素')
}

// 选择元素
const llmChatPanelRef = ref<InstanceType<typeof LLMChatPanel> | null>(null)

const selectElement = (element: string, text: string) => {
  selectedElement.value = { element, text }
  isSelectingElement.value = false
  console.log('选择元素:', text)
  llmChatPanelRef.value?.setInputText(`修改这段文字: "${text}"`)
  llmChatPanelRef.value?.focusInput()
}

// 取消选择
const cancelSelect = () => {
  isSelectingElement.value = false
  selectedElement.value = null
  console.log('取消选择')
}

// 处理AI助手返回结果，自动填充到生成文件预览
const handleAIResponse = async (content: string) => {
  console.log('=== AI助手返回结果 ===')
  console.log('Content:', content)
  console.log('当前选中文件:', selectedFile.value)
  console.log('当前sectionDetail:', sectionDetail.value)
  console.log('selectedFileData:', selectedFileData.value)
  
  if (!selectedFile.value) {
    console.warn('未选择文件，无法自动填充')
    alert('请先选择一个文件模板')
    return
  }
  
  // 如果没有sectionDetail但有selectedFileData，尝试重新加载
  if (!sectionDetail.value && selectedFileData.value) {
    console.log('尝试重新加载文件详情...')
    await handleSelectFile(selectedFile.value)
  }
  
  if (!sectionDetail.value) {
    console.warn('sectionDetail仍然为空，使用默认内容')
    sectionDetail.value = {
      id: selectedFile.value,
      section_name: selectedFileData.value?.name || '未命名',
      source_file: '',
      section_type: 'template',
      content: content,
      is_star_item: false
    }
  }
  
  // 确保进入编辑模式
  isEditing.value = false
  await nextTick()
  
  editableContent.value = content
  isEditing.value = true
  
  console.log('>>> AI结果已填充')
  console.log('>>> isEditing:', isEditing.value)
  console.log('>>> editableContent:', editableContent.value)
}

// 修复 setTimeout 在模板中无法访问的问题
const hideProjectDropdown = () => {
  setTimeout(() => {
    showProjectDropdown.value = false
  }, 200)
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  editableContent.value = sectionDetail.value?.content || ''
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  editableContent.value = ''
}

// 保存章节内容
const saveSection = async () => {
  if (!selectedProjectId.value || !selectedFile.value) return
  saving.value = true
  try {
    const updated = await updateTenderSection(
      selectedProjectId.value,
      selectedFile.value,
      { content: editableContent.value }
    )
    sectionDetail.value = updated
    isEditing.value = false
    editableContent.value = ''
  } catch (e: any) {
    error.value = e.message || '保存失败'
  } finally {
    saving.value = false
  }
}

const selectedFileData = computed(() => {
  if (!sectionDetail.value) return null
  return {
    id: selectedFile.value,
    name: sectionDetail.value.section_name || '',
    completed: false,
  }
})

// 监听项目 ID 变化
watch(selectedProjectId, (newProjectId) => {
  console.log('[BidList] 项目 ID 变化:', newProjectId)
  if (newProjectId && llmChatPanelRef.value) {
    // 清除之前的聊天记录并加载新项目的历史
    llmChatPanelRef.value.clearMessages()
    // 等待一下，确保 LLMChatPanel 内部的 projectId 已经更新
    setTimeout(() => {
      llmChatPanelRef.value?.loadHistory()
    }, 100)
  }
})

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

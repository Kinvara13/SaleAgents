<template>
  <div class="fade-in h-full flex flex-col">
    <div class="flex justify-between items-center mb-4">
      <div class="flex items-center space-x-3">
        <h2 class="text-xl font-bold text-gray-800">技术建议书编辑器</h2>
        <div class="w-56">
          <select class="w-full px-2 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm">
            <option>某城市智能交通系统建设项目</option>
            <option>企业数字化转型平台采购</option>
            <option>智慧城市安防系统升级</option>
            <option>医院信息系统(HIS)建设</option>
          </select>
        </div>
      </div>
      <div class="flex space-x-2">
        <button class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all duration-300">
          查看原模版
        </button>
        <button class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all duration-300">
          保存草稿
        </button>
        <button class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300">
          一键完成
        </button>
        <button class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300">
          导出文档
        </button>
      </div>
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
        <div :class="['border-r border-gray-100 bg-gray-50 p-4 transition-all duration-300', isLeftSidebarHidden ? 'w-0 hidden' : 'w-72']">
          <h3 class="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">目录导航</h3>
          <div class="space-y-1 max-h-[200px] overflow-y-auto">
            <div
              v-for="(item, index) in tableOfContents"
              :key="index"
              class="flex items-center px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-100 transition-all duration-300 text-sm"
              :class="{ 'bg-primary/10 text-primary font-medium': selectedSection === index, 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
              @click="isSelectingElement ? selectElement('toc', item) : (selectedSection = index)"
            >
              <span class="mr-2 text-gray-400">{{ index + 1 }}.</span>
              <span>{{ item }}</span>
            </div>
          </div>

          <!-- AI智能建议 -->
          <div class="mt-6">
            <h3 class="text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide flex items-center">
              <span class="mr-2">🤖</span>
              AI智能建议
            </h3>
            <div class="space-y-4 max-h-[400px] overflow-y-auto">
              <div class="bg-white rounded-lg p-4 border border-gray-100">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="w-6 h-6 bg-success/10 text-success rounded-full flex items-center justify-center text-sm">✓</span>
                  <span class="text-sm font-medium text-gray-700">内容优化</span>
                </div>
                <p class="text-sm text-gray-500 mb-3">{{ aiSuggestions.optimization }}</p>
                <button class="text-sm text-primary hover:underline">应用建议</button>
              </div>

              <div class="bg-white rounded-lg p-4 border border-gray-100">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="w-6 h-6 bg-warning/10 text-warning rounded-full flex items-center justify-center text-sm">⚠</span>
                  <span class="text-sm font-medium text-gray-700">风险提示</span>
                </div>
                <p class="text-sm text-gray-500 mb-3">{{ aiSuggestions.warning }}</p>
                <button class="text-sm text-primary hover:underline">查看详情</button>
              </div>

              <div class="bg-white rounded-lg p-4 border border-gray-100">
                <div class="flex items-center space-x-2 mb-2">
                  <span class="w-6 h-6 bg-primary/10 text-primary rounded-full flex items-center justify-center text-sm">💡</span>
                  <span class="text-sm font-medium text-gray-700">灵感补充</span>
                </div>
                <div class="typing-animation text-sm text-gray-600 inline-block">
                  {{ aiSuggestions.inspiration }}
                </div>
                <button class="text-sm text-primary hover:underline mt-2 block">插入内容</button>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-1 flex flex-col">
          <div class="flex items-center justify-between p-4 border-b border-gray-100">
            <h3 class="font-medium text-gray-800">技术建议书编辑</h3>
            <button 
              class="text-gray-400 hover:text-gray-600 transition-all duration-300"
              @click="toggleLeftSidebar"
            >
              {{ isLeftSidebarHidden ? '☰' : '✕' }}
            </button>
          </div>
          <div class="flex-1 p-6 overflow-auto">
            <div class="max-w-4xl mx-auto">
              <div v-if="isSelectingElement" class="mb-4 p-3 bg-primary/10 border border-primary/20 rounded-lg text-sm text-primary">
                <span class="font-medium">选择元素模式：</span>请点击下方需要修改的文字元素
              </div>
              <div class="mb-6">
                <input
                  type="text"
                  v-model="documentTitle"
                  class="w-full text-3xl font-bold text-gray-800 border-none outline-none placeholder-gray-300"
                  :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                  @click="isSelectingElement && selectElement('title', documentTitle)"
                  placeholder="请输入文档标题"
                />
              </div>
              <div class="prose max-w-none">
                <textarea
                  v-model="documentContent"
                  class="w-full min-h-[500px] text-gray-700 border-none outline-none resize-none leading-relaxed"
                  :class="{ 'ring-2 ring-primary ring-offset-1': isSelectingElement }"
                  @click="isSelectingElement && selectElement('content', documentContent)"
                  placeholder="在此处开始编辑内容..."
                ></textarea>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-100 bg-gray-50 p-4">
          </div>
        </div>

        <div class="w-96 border-l border-gray-100 bg-gray-50 flex flex-col">
          <!-- 智能生成 -->
          <div class="p-4 border-b border-gray-100">
            <h3 class="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wide flex items-center">
              <span class="mr-2">✨</span>
              智能生成
            </h3>
            <div class="bg-gradient-to-r from-primary/5 to-success/5 rounded-lg p-3 border border-primary/20">
              <div class="space-y-1">
                <button class="w-full text-left px-2 py-1.5 bg-white rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-all duration-300 border border-gray-100">
                  🎯 优化当前段落
                </button>
                <button class="w-full text-left px-2 py-1.5 bg-white rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-all duration-300 border border-gray-100">
                  📝 扩写当前段落
                </button>
                <button class="w-full text-left px-2 py-1.5 bg-white rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-all duration-300 border border-gray-100">
                  📚 引用知识库文件
                </button>
              </div>
            </div>
          </div>

          <!-- 选择元素按钮 -->
          <div class="p-4 border-b border-gray-100">
            <button 
              v-if="!isSelectingElement"
              class="w-full px-3 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm"
              @click="startSelectElement"
            >
              选择元素
            </button>
            <button 
              v-else
              class="w-full px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all duration-300 text-sm"
              @click="cancelSelect"
            >
              取消选择
            </button>
          </div>

          <!-- 对话历史 -->
          <div class="flex flex-col flex-1 min-h-0">
            <div class="p-4 overflow-auto space-y-4" style="height: 300px;">
              <div class="flex space-x-2">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  🤖
                </div>
                <div class="bg-gray-100 rounded-lg px-3 py-2 text-sm text-gray-800">
                  你好！我可以帮你修改技术建议书。你可以点击"选择元素"来选择需要修改的内容，然后告诉我你的修改需求。
                </div>
              </div>
              <div class="flex space-x-2">
                <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <span class="text-white text-xs">我</span>
                </div>
                <div class="bg-primary/10 rounded-lg px-3 py-2 text-sm text-gray-800">
                  帮我优化一下技术方案部分
                </div>
              </div>
              <div class="flex space-x-2">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  🤖
                </div>
                <div class="bg-gray-100 rounded-lg px-3 py-2 text-sm text-gray-800">
                  好的，我已经帮你优化了技术方案部分，增加了更多关于系统安全性的描述和大数据分析平台的技术实现细节。
                </div>
              </div>
            </div>
            
            <!-- 填充区域 -->
            <div class="flex-1 bg-gray-50 border-t border-gray-100"></div>
          </div>

          <textarea 
            v-model="aiMessage"
            placeholder="输入修改需求..."
            class="mx-3 mb-2 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm resize-none"
            style="height: 115px;"
            @keyup.enter="sendAiMessage"
          ></textarea>

          <!-- 操作按钮 -->
          <div class="p-3 border-t border-gray-100">
            <div class="flex items-center justify-end space-x-2">
              <input 
                type="file" 
                accept="image/*" 
                class="hidden" 
                ref="fileInput"
                @change="handleImageUpload"
              />
              <select class="px-2 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm text-gray-700">
                <option>GPT-4</option>
                <option>Claude-3</option>
                <option>GPT-3.5</option>
                <option>自定义模型</option>
              </select>
              <button 
              class="p-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-300 text-gray-600"
              @click="$refs.fileInput.click()"
              title="上传图片"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
            </button>
            <button 
              class="px-4 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm"
              @click="sendAiMessage"
            >
              发送
            </button>
            </div>
          </div>
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
                    @click.stop="handleStarItemConfirm(item, true)"
                    title="满足"
                  >
                    ✓
                  </button>
                  <button 
                    class="w-6 h-6 flex items-center justify-center rounded-full border transition-all text-xs"
                    :class="item.satisfied === false ? 'bg-danger text-white border-danger' : 'border-gray-200 text-gray-400 hover:bg-danger/10'"
                    @click.stop="handleStarItemConfirm(item, false)"
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
              <span class="text-gray-800 font-bold">{{ starItemResponses[selectedStarItem.name]?.section || '待编写' }}</span>
            </div>
            
            <div class="bg-gray-50 rounded-xl p-6 border border-gray-100 relative">
              <div class="absolute -top-3 left-6 px-3 py-1 bg-white border border-gray-100 rounded-full text-xs text-gray-400 font-medium">
                应答详情
              </div>
              <pre class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed font-sans">{{ starItemResponses[selectedStarItem.name]?.content || '暂无对应应答文字内容，请在编辑器中编写。' }}</pre>
            </div>

            <div class="flex justify-end space-x-3">
              <button 
                class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                @click="activeTab = 'editor'"
              >
                前往编辑
              </button>
              <button class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" @click="confirmCurrentStarItem">
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getProposal, updateProposal, confirmStarItem } from '../services/proposal'
import type { Proposal, StarItem, StarResponse } from '../services/proposal'
import { listProjects } from '../services/project'

const route = useRoute()

// 状态
const loading = ref(false)
const currentProposalId = ref<string>('')
const selectedSection = ref(0)
const documentTitle = ref('')
const documentContent = ref('')
const isLeftSidebarHidden = ref(false)
const isSelectingElement = ref(false)
const selectedElement = ref<{element: string, text: string} | null>(null)
const aiMessage = ref('')
const isStarItemsExpanded = ref(false)

const starItems = ref<StarItem[]>([])
const starItemResponses = ref<Record<string, StarResponse>>({})

// 检查所有星标项是否都已确认
const areAllStarItemsConfirmed = computed(() => {
  return starItems.value.length > 0 && starItems.value.every(item => item.satisfied !== null)
})

// 检查是否有不满足的星标项
const hasUnsatisfiedItems = computed(() => {
  return starItems.value.some(item => item.satisfied === false)
})

// 切换左侧边栏
const toggleLeftSidebar = () => {
  isLeftSidebarHidden.value = !isLeftSidebarHidden.value
}

// 开始选择元素
const startSelectElement = () => {
  isSelectingElement.value = true
  selectedElement.value = null
}

// 选择元素
const selectElement = (element: string, text: string) => {
  selectedElement.value = { element, text }
  isSelectingElement.value = false
  // 将选中的文本添加到AI输入框
  aiMessage.value = `修改这段文字: "${text}"`
}

// 取消选择
const cancelSelect = () => {
  isSelectingElement.value = false
  selectedElement.value = null
}

// 发送AI消息
const sendAiMessage = () => {
  if (aiMessage.value.trim()) {
    console.log('发送消息:', aiMessage.value)
    aiMessage.value = ''
  }
}

// 处理图片上传
const fileInput = ref<HTMLInputElement | null>(null)
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    alert('图片上传功能已触发，实际项目中会上传到服务器')
  }
}

const tableOfContents = [
  '项目概述',
  '技术方案',
  '项目实施计划',
  '质量保证措施',
  '售后服务承诺',
  '人员配置方案',
  '设备配置清单',
  '培训计划'
]

const aiSuggestions = ref({
  optimization: '建议在技术方案中增加更多关于系统安全性的描述，这是招标方关注的重点。',
  warning: '注意：当前内容中缺少对"大数据分析平台"的具体技术实现细节描述。',
  inspiration: '正在思考如何更好地展示我们的技术优势...'
})

const activeTab = ref('editor') // 'editor' or 'star'
const selectedStarItem = ref<StarItem | null>(null)

const selectStarItem = (item: StarItem) => {
  selectedStarItem.value = item
}

// 保存逻辑
let saveTimer: ReturnType<typeof setTimeout> | null = null
const triggerSave = () => {
  if (!currentProposalId.value) return
  if (saveTimer) clearTimeout(saveTimer)
  saveTimer = setTimeout(async () => {
    try {
      await updateProposal(currentProposalId.value, {
        title: documentTitle.value,
        content: documentContent.value
      })
    } catch (e) {
      console.error('Auto save failed', e)
    }
  }, 1500)
}

watch([documentTitle, documentContent], () => {
  triggerSave()
}, { deep: false })

const handleStarItemConfirm = async (item: StarItem, satisfied: boolean) => {
  if (!currentProposalId.value) return
  try {
    const updated = await confirmStarItem(currentProposalId.value, item.name, satisfied)
    item.satisfied = updated.satisfied
  } catch (e) {
    console.error('Failed to confirm star item', e)
    // fallback
    item.satisfied = satisfied
  }
}

const confirmCurrentStarItem = () => {
  if (selectedStarItem.value) {
    handleStarItemConfirm(selectedStarItem.value, true)
  }
}

// 加载数据
onMounted(async () => {
  loading.value = true
  try {
    let pid = route.params.projectId as string
    if (!pid) {
      const projects = await listProjects()
      if (projects.length > 0) {
        pid = projects[0].id
      }
    }
    if (pid) {
      currentProposalId.value = pid
      const data = await getProposal(pid)
      documentTitle.value = data.title || ''
      documentContent.value = data.content || ''
      starItems.value = data.star_items || []
      starItemResponses.value = data.star_responses || {}
    }
  } catch (e) {
    console.error('Failed to load proposal:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.typing-animation {
  overflow: hidden;
  border-right: 2px solid transparent;
  white-space: normal;
  animation: typing 2s steps(40, end);
}
@keyframes typing {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

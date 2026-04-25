<template>
  <div class="fade-in min-h-screen bg-gradient-to-br from-white to-gray-50">

    <!-- 主要内容 -->
    <main class="container mx-auto px-4 py-8">
      <!-- 标题部分 -->
      <div class="text-center mb-12">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-800 mb-4">标书助手，你的AI投标伙伴已就位</h1>
        <p class="text-gray-600 max-w-2xl mx-auto">
          利用人工智能技术，快速制作高质量标书，提高中标率，为您的企业赢得更多商机
        </p>
      </div>

      <!-- 中间对话框 -->
      <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-md border border-gray-100 mb-16">
        <!-- TAP导航 -->
        <div class="border-b border-gray-100">
          <div class="flex">
            <button
              v-for="tap in taps"
              :key="tap.id"
              class="px-6 py-4 text-sm font-medium transition-colors"
              :class="activeTap === tap.id ? 'text-primary border-b-2 border-primary' : 'text-gray-600 hover:text-primary'"
              @click="activeTap = tap.id"
            >
              {{ tap.name }}
            </button>
          </div>
        </div>

        <!-- TAP内容 -->
        <div class="p-6">
          <template v-for="(tap, index) in taps" :key="tap.id">
            <HomeChatTab
              v-if="activeTap === tap.id"
              :chat="tapChats[index]"
              v-model:input="tapInputs[index]"
              v-model:projectId="tapProjectIds[index]"
              v-model:model="tapModels[index]"
              :projects="projects"
              :uploadedFiles="uploadedFiles"
              :placeholder="tapPlaceholders[index]"
              @send="handleSend(tap.id)"
              @file-upload="handleFileUpload"
              @remove-file="removeFile($event)"
            />
          </template>
        </div>
      </div>

      <!-- 平台案例 -->
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-800 mb-2">成功案例</h2>
          <p class="text-gray-600">查看我们帮助客户完成的优质项目</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="caseItem in cases" :key="caseItem.id" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
            <div class="h-48 bg-gray-200 flex items-center justify-center">
              <span class="text-4xl">{{ caseItem.icon }}</span>
            </div>
            <div class="p-4">
              <h3 class="font-semibold text-gray-800 mb-2">{{ caseItem.title }}</h3>
              <p class="text-sm text-gray-600 mb-4">{{ caseItem.description }}</p>
              <button class="text-sm text-primary hover:underline">查看详情</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-100 mt-16 py-8">
      <div class="container mx-auto px-4">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
            <div class="text-lg font-bold text-primary">AI标书智能平台</div>
            <p class="text-sm text-gray-600 mt-1">© 2026 AI标书智能平台. 保留所有权利</p>
          </div>
          <div class="flex space-x-6">
            <a href="#" class="text-sm text-gray-600 hover:text-primary">关于我们</a>
            <a href="#" class="text-sm text-gray-600 hover:text-primary">服务条款</a>
            <a href="#" class="text-sm text-gray-600 hover:text-primary">隐私政策</a>
            <a href="#" class="text-sm text-gray-600 hover:text-primary">联系我们</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listProjects } from '../services/project'
import type { Project } from '../types'
import { useLLMChat } from '../composables/useLLMChat'
import HomeChatTab from '../components/HomeChatTab.vue'

// TAP切换
const activeTap = ref(1)
const taps = [
  { id: 1, name: '投标前评估' },
  { id: 2, name: '标书制作' },
  { id: 3, name: 'DEMO制作' }
]

const tapPlaceholders = [
  '请选择您要进行前评估的项目，描述你的需求',
  '请选择您要进行标书制作的项目，描述你的需求',
  '请选择您要进行DEMO制作的项目，描述你的需求'
]

// 各 TAP 独立状态
const tapInputs = ref(['', '', ''])
const tapProjectIds = ref(['', '', ''])
const tapModels = ref(['gpt-4', 'gpt-4', 'gpt-4'])

// 各 TAP 独立聊天实例
const chat1 = useLLMChat()
const chat2 = useLLMChat()
const chat3 = useLLMChat()

const tapChats = [chat1, chat2, chat3]

// 上传文件相关
const uploadedFiles = ref<Array<{ name: string; size: number; type: string }>>([])

// 项目列表
const projects = ref<Project[]>([])

// 处理文件上传
const handleFileUpload = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files && files.length > 0) {
    for (let i = 0; i < files.length; i++) {
      uploadedFiles.value.push({
        name: files[i].name,
        size: files[i].size,
        type: files[i].type
      })
    }
  }
}

// 移除上传的文件
const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

// 发送消息
const handleSend = async (tapId: number) => {
  const idx = tapId - 1
  const text = tapInputs.value[idx].trim()
  if (!text) return

  const chat = tapChats[idx]
  if (chat.isLoading.value) return

  await chat.sendMessage(text, {
    projectId: tapProjectIds.value[idx] || undefined,
    body: { model: tapModels.value[idx] }
  })

  tapInputs.value[idx] = ''
}

// 案例数据（待后端接口完善后对接）
const cases = ref<any[]>([])

onMounted(async () => {
  try {
    projects.value = await listProjects()
  } catch (e) {
    console.error('加载项目失败', e)
  }
})
</script>

<style scoped>
</style>

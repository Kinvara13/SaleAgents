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
          <!-- ===== 投标前评估 ===== -->
          <div v-if="activeTap === 1" class="space-y-4">
            <!-- 消息展示区 -->
            <div
              v-if="chat1.messages.length > 0"
              ref="msgBox1"
              class="bg-white rounded-lg border border-gray-200 p-4 max-h-[420px] overflow-y-auto space-y-3"
            >
              <div
                v-for="msg in chat1.messages"
                :key="msg.id"
                :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
              >
                <div
                  class="max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed break-words"
                  :class="msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'"
                >
                  {{ msg.content }}
                </div>
              </div>
              <div v-if="chat1.isLoading && !chat1.isStreaming" class="flex justify-start">
                <div class="bg-gray-100 text-gray-500 rounded-lg rounded-bl-none px-4 py-2 text-sm flex items-center gap-2">
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-4">
              <!-- 输入区域 -->
              <div class="border border-gray-200 rounded-lg p-4 bg-white">
                <textarea
                  v-model="tapInputs[0]"
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行前评估的项目，描述你的需求"
                  @keydown.enter.prevent="handleEnter(1, $event)"
                ></textarea>

                <!-- 上传文件回显 -->
                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>

                <input
                  type="file"
                  ref="fileInput"
                  class="hidden"
                  multiple
                  @change="handleFileUpload"
                />

                <!-- 底部控制栏 -->
                <div class="flex flex-wrap gap-3 mt-3 justify-end items-center">
                  <select
                    v-model="tapProjectIds[0]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 200px"
                  >
                    <option value="">请选择项目</option>
                    <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>

                  <select
                    v-model="tapModels[0]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 100px"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义</option>
                  </select>

                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 32px" @click="openFileUpload">
                    上传文件
                  </button>

                  <button
                    class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    style="height: 32px"
                    :disabled="chat1.isLoading || !tapInputs[0].trim()"
                    @click="handleSend(1)"
                  >
                    {{ chat1.isLoading ? chat1.stateLabel : '发送' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ===== 标书制作 ===== -->
          <div v-if="activeTap === 2" class="space-y-4">
            <!-- 消息展示区 -->
            <div
              v-if="chat2.messages.length > 0"
              ref="msgBox2"
              class="bg-white rounded-lg border border-gray-200 p-4 max-h-[420px] overflow-y-auto space-y-3"
            >
              <div
                v-for="msg in chat2.messages"
                :key="msg.id"
                :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
              >
                <div
                  class="max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed break-words"
                  :class="msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'"
                >
                  {{ msg.content }}
                </div>
              </div>
              <div v-if="chat2.isLoading && !chat2.isStreaming" class="flex justify-start">
                <div class="bg-gray-100 text-gray-500 rounded-lg rounded-bl-none px-4 py-2 text-sm flex items-center gap-2">
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-4">
              <div class="border border-gray-200 rounded-lg p-4 bg-white">
                <textarea
                  v-model="tapInputs[1]"
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行标书制作的项目，描述你的需求"
                  @keydown.enter.prevent="handleEnter(2, $event)"
                ></textarea>

                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>

                <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileUpload" />

                <div class="flex flex-wrap gap-3 mt-3 justify-end items-center">
                  <select
                    v-model="tapProjectIds[1]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 200px"
                  >
                    <option value="">请选择项目</option>
                    <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>

                  <select
                    v-model="tapModels[1]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 100px"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义</option>
                  </select>

                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 32px" @click="openFileUpload">
                    上传文件
                  </button>

                  <button
                    class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    style="height: 32px"
                    :disabled="chat2.isLoading || !tapInputs[1].trim()"
                    @click="handleSend(2)"
                  >
                    {{ chat2.isLoading ? chat2.stateLabel : '发送' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ===== DEMO制作 ===== -->
          <div v-if="activeTap === 3" class="space-y-4">
            <!-- 消息展示区 -->
            <div
              v-if="chat3.messages.length > 0"
              ref="msgBox3"
              class="bg-white rounded-lg border border-gray-200 p-4 max-h-[420px] overflow-y-auto space-y-3"
            >
              <div
                v-for="msg in chat3.messages"
                :key="msg.id"
                :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
              >
                <div
                  class="max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed break-words"
                  :class="msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'"
                >
                  {{ msg.content }}
                </div>
              </div>
              <div v-if="chat3.isLoading && !chat3.isStreaming" class="flex justify-start">
                <div class="bg-gray-100 text-gray-500 rounded-lg rounded-bl-none px-4 py-2 text-sm flex items-center gap-2">
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                  <span class="inline-block w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-4">
              <div class="border border-gray-200 rounded-lg p-4 bg-white">
                <textarea
                  v-model="tapInputs[2]"
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行DEMO制作的项目，描述你的需求"
                  @keydown.enter.prevent="handleEnter(3, $event)"
                ></textarea>

                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>

                <input type="file" ref="fileInput" class="hidden" multiple @change="handleFileUpload" />

                <div class="flex flex-wrap gap-3 mt-3 justify-end items-center">
                  <select
                    v-model="tapProjectIds[2]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 200px"
                  >
                    <option value="">请选择项目</option>
                    <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>

                  <select
                    v-model="tapModels[2]"
                    class="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
                    style="width: 100px"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义</option>
                  </select>

                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 32px" @click="openFileUpload">
                    上传文件
                  </button>

                  <button
                    class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    style="height: 32px"
                    :disabled="chat3.isLoading || !tapInputs[2].trim()"
                    @click="handleSend(3)"
                  >
                    {{ chat3.isLoading ? chat3.stateLabel : '发送' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
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
import { ref, onMounted, watch, nextTick } from 'vue'
import { listProjects } from '../services/project'
import type { Project } from '../types'
import { useLLMChat } from '../composables/useLLMChat'

// TAP切换
const activeTap = ref(1)
const taps = [
  { id: 1, name: '投标前评估' },
  { id: 2, name: '标书制作' },
  { id: 3, name: 'DEMO制作' }
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

// 消息容器引用（用于自动滚动）
const msgBox1 = ref<HTMLElement | null>(null)
const msgBox2 = ref<HTMLElement | null>(null)
const msgBox3 = ref<HTMLElement | null>(null)
const msgBoxes = [msgBox1, msgBox2, msgBox3] as const

// 上传文件相关
const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFiles = ref<Array<{ name: string; size: number; type: string }>>([])

// 项目列表
const projects = ref<Project[]>([])

// 打开文件上传窗口
const openFileUpload = () => {
  fileInput.value?.click()
}

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

// Enter 发送（Shift+Enter 换行）
const handleEnter = (tapId: number, e: KeyboardEvent) => {
  if (!e.shiftKey) {
    handleSend(tapId)
  }
}

// 各 TAP 消息变化时自动滚动到底部
watch(chat1.messages, () => nextTick(() => {
  if (msgBox1.value) msgBox1.value.scrollTop = msgBox1.value.scrollHeight
}), { deep: true })
watch(chat2.messages, () => nextTick(() => {
  if (msgBox2.value) msgBox2.value.scrollTop = msgBox2.value.scrollHeight
}), { deep: true })
watch(chat3.messages, () => nextTick(() => {
  if (msgBox3.value) msgBox3.value.scrollTop = msgBox3.value.scrollHeight
}), { deep: true })

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

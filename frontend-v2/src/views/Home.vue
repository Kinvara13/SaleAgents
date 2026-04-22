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
          <!-- 投标前评估 -->
          <div v-if="activeTap === 1" class="space-y-6">
            
            <div class="bg-gray-50 rounded-lg p-4">
              <!-- 输入区域 -->
              <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                <!-- 文本输入区域 -->
                <textarea 
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行前评估的项目，描述你的需求"
                ></textarea>
                
                <!-- 上传文件回显 -->
                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>
                
                <!-- 隐藏的文件输入框 -->
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="hidden" 
                  multiple 
                  @change="handleFileUpload"
                />
                
                <!-- 底部控制栏 -->
                <div class="flex space-x-4 mt-3 justify-end">
                  <!-- 选择项目下拉框 -->
                  <select class="w-50 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 200px">
                    <option value="">请选择项目</option>
                    <option value="1">某城市智能交通系统建设项目</option>
                    <option value="2">企业数字化转型平台采购</option>
                    <option value="3">智慧城市安防系统升级</option>
                    <option value="4">医院信息系统(HIS)建设</option>
                  </select>
                  
                  <!-- 模型选择下拉框 -->
                  <select class="w-24 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 100px">
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义模型</option>
                  </select>
                  
                  <!-- 上传文件按钮 -->
                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 30px" @click="openFileUpload">
                    上传文件
                  </button>
                  
                  <!-- 发送按钮 -->
                  <button class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center" style="height: 30px" @click="handleSend(activeTap)">
                    发送
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 标书制作 -->
          <div v-if="activeTap === 2" class="space-y-6">
            
            <div class="bg-gray-50 rounded-lg p-4">
              <!-- 输入区域 -->
              <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                <!-- 文本输入区域 -->
                <textarea 
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行标书制作的项目，描述你的需求"
                ></textarea>
                
                <!-- 上传文件回显 -->
                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>
                
                <!-- 隐藏的文件输入框 -->
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="hidden" 
                  multiple 
                  @change="handleFileUpload"
                />
                
                <!-- 底部控制栏 -->
                <div class="flex space-x-4 mt-3 justify-end">
                  <!-- 选择项目下拉框 -->
                  <select class="w-50 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 200px">
                    <option value="">请选择项目</option>
                    <option value="1">某城市智能交通系统建设项目</option>
                    <option value="2">企业数字化转型平台采购</option>
                    <option value="3">智慧城市安防系统升级</option>
                    <option value="4">医院信息系统(HIS)建设</option>
                  </select>
                  
                  <!-- 模型选择下拉框 -->
                  <select class="w-24 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 100px">
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义模型</option>
                  </select>
                  
                  <!-- 上传文件按钮 -->
                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 30px" @click="openFileUpload">
                    上传文件
                  </button>
                  
                  <!-- 发送按钮 -->
                  <button class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center" style="height: 30px" @click="handleSend(activeTap)">
                    发送
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- DEMO制作 -->
          <div v-if="activeTap === 3" class="space-y-6">
            
            <div class="bg-gray-50 rounded-lg p-4">
              <!-- 输入区域 -->
              <div class="border border-gray-200 rounded-lg p-4 bg-white mb-4">
                <!-- 文本输入区域 -->
                <textarea 
                  class="w-full px-3 py-2 border-0 focus:outline-none text-sm resize-none"
                  rows="4"
                  placeholder="请选择您要进行DEMO制作的项目，描述你的需求"
                ></textarea>
                
                <!-- 上传文件回显 -->
                <div v-if="uploadedFiles.length > 0" class="mt-3">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="flex items-center justify-between p-2 bg-gray-50 rounded mb-1">
                    <span class="text-sm text-gray-700">{{ file.name }}</span>
                    <button class="text-sm text-red-500 hover:text-red-700" @click="removeFile(index)">删除</button>
                  </div>
                </div>
                
                <!-- 隐藏的文件输入框 -->
                <input 
                  type="file" 
                  ref="fileInput" 
                  class="hidden" 
                  multiple 
                  @change="handleFileUpload"
                />
                
                <!-- 底部控制栏 -->
                <div class="flex space-x-4 mt-3 justify-end">
                  <!-- 选择项目下拉框 -->
                  <select class="w-50 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 200px">
                    <option value="">请选择项目</option>
                    <option value="1">某城市智能交通系统建设项目</option>
                    <option value="2">企业数字化转型平台采购</option>
                    <option value="3">智慧城市安防系统升级</option>
                    <option value="4">医院信息系统(HIS)建设</option>
                  </select>
                  
                  <!-- 模型选择下拉框 -->
                  <select class="w-24 px-3 py-1 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm" style="width: 100px">
                    <option value="gpt-4">GPT-4</option>
                    <option value="claude-3">Claude-3</option>
                    <option value="gpt-3.5">GPT-3.5</option>
                    <option value="custom">自定义模型</option>
                  </select>
                  
                  <!-- 上传文件按钮 -->
                  <button class="px-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center text-sm" style="height: 30px" @click="openFileUpload">
                    上传文件
                  </button>
                  
                  <!-- 发送按钮 -->
                  <button class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors flex items-center" style="height: 30px" @click="handleSend(activeTap)">
                    发送
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listProjects } from '../services/project'
import type { Project } from '../types'

// TAP切换
const activeTap = ref(1)
const taps = [
  { id: 1, name: '投标前评估' },
  { id: 2, name: '标书制作' },
  { id: 3, name: 'DEMO制作' }
]

// 上传文件相关
const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFiles = ref<Array<{ name: string; size: number; type: string }>>([])

// 路由
const router = useRouter()

// 项目列表
const projects = ref<Project[]>([])

// 打开文件上传窗口
const openFileUpload = () => {
  fileInput.value?.click()
}

// 处理文件上传
const handleFileUpload = (event: any) => {
  const files = event.target.files
  if (files.length > 0) {
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

// 发送按钮点击事件
const handleSend = (tapId: number) => {
  switch(tapId) {
    case 1:
      // 投标前评估转跳至「已上传文件后的编辑页」
      {
        const firstUploadedFile = uploadedFiles.value[0] || {
          name: '标签评估文件.rar',
          size: 0,
          type: ''
        }
        router.push({
          path: '/pre-evaluation',
          query: {
            uploaded: '1',
            fileName: firstUploadedFile.name,
            fileSize: String(firstUploadedFile.size || 0),
            fileType: firstUploadedFile.type || ''
          }
        })
      }
      break
    case 2:
      // 标书制作转跳至回标文件菜单
      router.push('/bid-list')
      break
    case 3:
      // DEMO制作转跳至DEMO制作菜单
      router.push('/demo-workflow')
      break
    default:
      break
  }
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

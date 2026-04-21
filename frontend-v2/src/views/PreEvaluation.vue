<template>
  <div class="fade-in">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-gray-800">标前评估</h2>
    </div>
    
    <!-- 文件预览模态框 -->
    <div v-if="showPreview" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-800">{{ previewFile.name }}</h3>
          <button class="text-gray-500 hover:text-gray-700" @click="showPreview = false">
            <span class="text-xl">×</span>
          </button>
        </div>
        <div class="p-6 overflow-auto max-h-[calc(80vh-80px)]">
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900 mb-2">文件内容预览</h4>
            <div class="text-sm text-gray-600 whitespace-pre-wrap">
              {{ previewFile.content }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">上传标书要求文件</h2>
      
      <!-- 未上传状态 -->
      <div v-if="!uploadedFile" class="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center bg-primary/5 transition-all duration-300 hover:border-primary/50">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">📄</span>
          <p class="text-gray-600 mb-2">点击或拖拽文件到此处上传</p>
          <p class="text-sm text-gray-400 mb-6">支持 Word、PDF、ZIP 等格式</p>
          <input type="file" class="hidden" id="file-upload" multiple @change="handleFileUpload" />
          <label for="file-upload" class="px-6 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 cursor-pointer">
            选择文件
          </label>
        </div>
      </div>
      
      <!-- 上传中状态 -->
      <div v-else-if="uploadStatus === 'uploading'" class="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center bg-primary/5">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">⏳</span>
          <p class="text-gray-600 mb-2">正在上传文件...</p>
          <div class="w-full max-w-md mt-4">
            <div class="h-2 bg-gray-200 rounded-full">
              <div class="h-2 bg-primary rounded-full" style="width: 60%"></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 解析中状态 -->
      <div v-else-if="uploadStatus === 'analyzing'" class="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center bg-primary/5">
        <div class="flex flex-col items-center">
          <span class="text-4xl mb-4">🔍</span>
          <p class="text-gray-600 mb-2">正在解析文件...</p>
          <p class="text-sm text-gray-400 mt-2">正在分析评审办法和技术评审表...</p>
        </div>
      </div>
      
      <!-- 上传完成状态 -->
      <div v-else-if="uploadStatus === 'completed'" class="border-2 border-dashed border-primary/30 rounded-lg p-8 bg-primary/5">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <span class="text-2xl mr-4">📄</span>
            <div>
              <h3 class="font-medium text-gray-900">{{ uploadedFile.name }}</h3>
              <p class="text-sm text-gray-500">{{ formatFileSize(uploadedFile.size) }}</p>
            </div>
          </div>
          <button class="px-4 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm">
            重新上传
          </button>
        </div>
      </div>
    </div>

    <!-- 评估结果 TAP -->
    <div v-if="uploadStatus === 'completed'" class="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
      <!-- TAP导航 -->
      <div class="border-b border-gray-100 flex justify-between items-center">
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
        <div class="px-6 py-4">
          <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm">
            生成报告
          </button>
        </div>
      </div>
      
      <!-- TAP内容 -->
      <div class="p-6">
        <!-- 评审办法 -->
        <div v-if="activeTap === 1" class="space-y-6">
          <!-- 评审办法前附表 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">评审办法前附表</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full border border-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">条款号</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">条款名称</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">评审内容</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">评审因素</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">权重占比(%)</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">评分标准</th>
                  </tr>
                </thead>
                <tbody class="bg-white">
                  <tr class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" rowspan="4">3.2.2</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" rowspan="4">详细评审标准</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">综合实力</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">综合实力标准</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">0</td>
                    <td class="px-4 py-3 text-sm text-gray-900"></td>
                  </tr>
                  <tr class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">技术后评估</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">技术标准</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">50</td>
                    <td class="px-4 py-3 text-sm text-gray-900">详见第三章附件：《技术评分标准》</td>
                  </tr>
                  <tr class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">技术后评估</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">评审标准</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">0</td>
                    <td class="px-4 py-3 text-sm text-gray-900">/</td>
                  </tr>
                  <tr class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">价格</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">价格评审</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">50</td>
                    <td class="px-4 py-3 text-sm text-gray-900">1、按照应答文件格式中"应答一览表"要求进行报价。<br>2、详见第三章附件：《价格评分标准》。</td>
                  </tr>
                  <tr class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">3.3.2.2</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">评分计算原则</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" colspan="2">综合得分计算</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r"></td>
                    <td class="px-4 py-3 text-sm text-gray-900">综合得分=技术评审部分得分*技术评审部分权重+价格评审部分得分*价格评审部分权重<br>最终综合得分四舍五入保留至小数点后两位。</td>
                  </tr>
                  <tr>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">3.3.4</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">中选候选人推荐原则</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" colspan="2">推荐原则</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r"></td>
                    <td class="px-4 py-3 text-sm text-gray-900">1、中选候选人个数详见应答人须知前附表。<br>2、当评审综合得分出现并列时，以价格部分得分高者优先，如仍相同，则按照技术部分中"技术能力、项目经验、服务团队"部分分项得分排名次序依次确定。<br>3、异常低价澄清要求详见第三章附件《异常低价澄清启动规则》。</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- 技术评审表 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">技术评审表</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full border border-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-24">评分标准-一级</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-48">评分标准-二级</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-96">评分内容</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-32">主观/客观/扣分</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-24">满分分值</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-24">预估得分</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b w-64">得分说明</th>
                  </tr>
                </thead>
                <tbody class="bg-white">
                  <tr v-for="item in technicalEvaluationTable" :key="item.id" class="border-b">
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" :rowspan="item.rowspan || 1">
                      {{ item.category }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" :rowspan="item.rowspan || 1">
                      {{ item.subCategory }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r" :rowspan="item.rowspan || 1">
                      {{ item.content }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">{{ item.type }}</td>
                    <td class="px-4 py-3 text-sm text-gray-900 border-r">{{ item.fullScore }}</td>
                    <td class="px-4 py-3 text-sm font-medium text-primary border-r">
                      {{ item.type === '主观' ? '/' : item.estimatedScore }}
                    </td>
                    <td class="px-4 py-3 text-sm text-gray-500">
                      {{ item.explanation }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- 客观分预估 -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h3 class="text-lg font-semibold text-gray-800 mb-2">客观分预估</h3>
            <div class="flex items-center">
              <div class="text-3xl font-bold text-primary mr-4">{{ totalScore }}</div>
              <div class="text-gray-600">/ 100</div>
            </div>
            <p class="text-gray-600 mt-2">根据评审办法和技术评审表分析，预计可以获得的客观分</p>
          </div>
        </div>
        
        <!-- 星标项 -->
        <div v-if="activeTap === 2" class="space-y-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">标书中的星标项</h3>
          <div class="space-y-4">
            <div v-for="item in starItems" :key="item.id" class="border border-gray-200 rounded-lg p-4">
              <div class="flex items-start">
                <span class="text-yellow-500 font-bold text-lg mr-3">★</span>
                <div class="flex-1">
                  <h4 class="font-medium text-gray-900 mb-2">{{ item.title }}</h4>
                  <p class="text-sm text-gray-600 mb-3">{{ item.content }}</p>
                  <div class="flex items-center">
                    <span class="text-sm text-gray-500">关联文件：</span>
                    <a href="#" class="text-sm text-primary hover:underline ml-2 cursor-pointer" @click.stop="previewFileContent(item.relatedFile)">{{ item.relatedFile }}</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史评估记录 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="p-6 border-b border-gray-100">
        <h2 class="text-lg font-semibold text-gray-800">历史评估记录</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">项目名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">上传时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">客观分</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="record in evaluationRecords" :key="record.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ record.projectName }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ record.uploadTime }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ record.score }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 py-1 text-xs rounded-full', record.status === '已完成' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800']">
                  {{ record.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="#" class="text-primary hover:text-primary/80 mr-3">查看详情</a>
                <a href="#" class="text-gray-600 hover:text-gray-900">下载报告</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="p-6 border-t border-gray-100">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-600">
            显示 <span class="font-medium">{{ evaluationRecords.length }}</span> 条记录
          </div>
          <div class="flex space-x-2">
            <button class="px-3 py-1 border border-gray-200 rounded-md text-sm text-gray-600 hover:bg-gray-50 transition-colors">
              上一页
            </button>
            <button class="px-3 py-1 border border-gray-200 rounded-md text-sm text-gray-600 hover:bg-gray-50 transition-colors">
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getReviewSummary, getReviewIssues, getReviewActions, getLatestReviewJob } from '../services/review'
import type { MetricItem, ReviewIssue } from '../types'

// 文件上传相关状态
const uploadedFile = ref<any>(null)
const uploadStatus = ref('') // '', 'uploading', 'analyzing', 'completed'
const route = useRoute()
const loading = ref(false)
const error = ref('')

// 支持从首页携带「已上传文件」状态，直达编辑页
const initUploadedStateFromRoute = () => {
  if (route.query.uploaded !== '1') return

  const fileName = typeof route.query.fileName === 'string' && route.query.fileName.trim()
    ? route.query.fileName
    : '标签评估文件.rar'
  const fileSize = Number(route.query.fileSize) || 0
  const fileType = typeof route.query.fileType === 'string' ? route.query.fileType : ''

  uploadedFile.value = {
    name: fileName,
    size: fileSize,
    type: fileType
  }
  uploadStatus.value = 'completed'
}

initUploadedStateFromRoute()

// TAP切换
const activeTap = ref(1)
const taps = [
  { id: 1, name: '评审办法' },
  { id: 2, name: '星标项' }
]

// 评审办法前附表数据（待后端接口完善后对接）
const preEvaluationTable = ref<any[]>([])

// 技术评审表数据（待后端接口完善后对接）
const technicalEvaluationTable = ref<any[]>([])

// 星标项数据（从 review issues 映射）
const starItems = ref<any[]>([])

// 客观分预估
const totalScore = ref('0')

// 计算客观分总分
const calculateTotalScore = () => {
  let score = 0
  technicalEvaluationTable.value.forEach((item: any) => {
    if (item.type === '客观' && item.estimatedScore) {
      score += parseFloat(item.estimatedScore)
    }
  })
  totalScore.value = score.toFixed(1)
}

// 文件预览相关状态
const showPreview = ref(false)
const previewFile = ref<{ name: string; content: string }>({ name: '', content: '' })

// 预览文件内容
const previewFileContent = (fileName: string) => {
  previewFile.value = {
    name: fileName,
    content: '文件内容暂不可用，待后端接口完善后对接。'
  }
  showPreview.value = true
}

// 历史评估记录数据
const evaluationRecords = ref<any[]>([])

// 处理文件上传
const handleFileUpload = (event: any) => {
  const file = event.target.files[0]
  if (file) {
    uploadedFile.value = file
    uploadStatus.value = 'uploading'

    // 模拟上传过程
    setTimeout(() => {
      uploadStatus.value = 'analyzing'

      // 模拟解析过程
      setTimeout(() => {
        uploadStatus.value = 'completed'
      }, 2000)
    }, 1500)
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [summary, issues, actions, latestJob] = await Promise.all([
      getReviewSummary(),
      getReviewIssues(),
      getReviewActions(),
      getLatestReviewJob().catch(() => null),
    ])
    // 将 review issues 映射为星标项
    starItems.value = issues.map((issue: ReviewIssue, index: number) => ({
      id: index + 1,
      title: issue.title,
      content: issue.detail,
      relatedFile: issue.document || '评审文件'
    }))
    // 将 review summary 映射为历史评估记录
    if (latestJob) {
      evaluationRecords.value = [{
        id: latestJob.id,
        projectName: latestJob.contract_name || '未命名项目',
        uploadTime: latestJob.created_at,
        score: summary.find((s: MetricItem) => s.label.includes('得分'))?.value || '-',
        status: latestJob.status === 'completed' ? '已完成' : '进行中'
      }]
    }
  } catch (e: any) {
    error.value = e.message || '加载评审数据失败'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
</style>

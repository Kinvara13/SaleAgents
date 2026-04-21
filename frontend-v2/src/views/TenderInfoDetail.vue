<template>
  <div class="fade-in flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div>
        <h2 class="text-xl font-bold text-gray-800">{{ tender?.title || '加载中...' }}</h2>
        <p class="text-sm text-gray-500 mt-0.5">招标信息详情</p>
      </div>
      <button
        class="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 text-sm transition-all"
        @click="router.push({ name: 'TenderInfoList' })"
      >
        ← 返回列表
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
    </div>

    <!-- Detail -->
    <div v-else-if="tender" class="flex-1 flex flex-col min-h-0 gap-6">
      <!-- Info Card -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="grid grid-cols-2 gap-y-3 gap-x-8 text-sm">
          <div>
            <span class="text-gray-500">项目类型：</span>
            <span class="text-gray-800">{{ tender.project_type || '-' }}</span>
          </div>
          <div>
            <span class="text-gray-500">预算金额：</span>
            <span class="text-gray-800 font-semibold">{{ tender.amount || '-' }}</span>
          </div>
          <div>
            <span class="text-gray-500">发布日期：</span>
            <span class="text-gray-800">{{ tender.publish_date || '-' }}</span>
          </div>
          <div>
            <span class="text-gray-500">报名截止：</span>
            <span class="text-gray-800">{{ tender.deadline || '-' }}</span>
          </div>
          <div class="col-span-2">
            <span class="text-gray-500">招标链接：</span>
            <a
              :href="tender.source_url"
              target="_blank"
              class="text-primary hover:underline break-all"
            >{{ tender.source_url }}</a>
          </div>
          <div>
            <span class="text-gray-500">当前状态：</span>
            <span
              :class="[
                'px-2 py-0.5 rounded-full text-xs font-medium',
                tender.decision === 'pending' ? 'bg-gray-100 text-gray-600' :
                tender.decision === 'bid' ? 'bg-success/10 text-success' :
                'bg-danger/10 text-danger'
              ]"
            >
              {{ decisionLabel(tender.decision) }}
            </span>
          </div>
        </div>

        <!-- Description -->
        <div v-if="tender.description" class="mt-4 pt-4 border-t border-gray-100">
          <h4 class="text-sm font-medium text-gray-700 mb-2">项目描述</h4>
          <p class="text-sm text-gray-600 leading-relaxed">{{ tender.description }}</p>
        </div>

        <!-- Reject Reason -->
        <div v-if="tender.decision === 'reject' && tender.reject_reason" class="mt-4 pt-4 border-t border-gray-100">
          <h4 class="text-sm font-medium text-gray-700 mb-2">不投标原因</h4>
          <p class="text-sm text-danger">{{ tender.reject_reason }}</p>
        </div>
      </div>

      <!-- Action Area -->
      <div v-if="tender.decision === 'pending'" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h4 class="text-base font-semibold text-gray-800 mb-4">投标决策</h4>

        <!-- Tabs -->
        <div class="flex space-x-3 mb-4">
          <button
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            :class="actionTab === 'bid'
              ? 'bg-primary text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            @click="actionTab = 'bid'"
          >
            💰 投标
          </button>
          <button
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            :class="actionTab === 'reject'
              ? 'bg-danger text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            @click="actionTab = 'reject'"
          >
            ✖ 不投标
          </button>
        </div>

        <!-- Bid Action -->
        <div v-if="actionTab === 'bid'">
          <p class="text-sm text-gray-600 mb-3">上传招标文件，系统将自动创建投标项目并进入标书制作流程。</p>
          <label class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 cursor-pointer text-sm inline-block transition-all">
            选择标书文件上传
            <input type="file" accept=".pdf,.doc,.docx" class="hidden" @change="handleBidUpload" />
          </label>
          <p v-if="uploading" class="text-sm text-gray-500 mt-2">正在上传并创建投标项目...</p>
        </div>

        <!-- Reject Action -->
        <div v-if="actionTab === 'reject'">
          <p class="text-sm text-gray-600 mb-3">请填写不投标的原因（选填）：</p>
          <textarea
            v-model="rejectReason"
            class="w-full min-h-[100px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-danger/50 focus:border-danger"
            placeholder="例如：预算过低、项目周期太短、技术要求超出能力范围..."
          ></textarea>
          <button
            class="mt-3 px-4 py-2 bg-danger text-white rounded-lg hover:bg-danger/90 text-sm transition-all"
            :disabled="submitting"
            @click="handleReject"
          >
            {{ submitting ? '提交中...' : '确认不投标' }}
          </button>
        </div>
      </div>

      <!-- Already Decided -->
      <div v-else class="bg-gray-50 rounded-xl border border-gray-200 p-6 text-center">
        <p class="text-gray-500 text-sm">
          已完成决策：
          <span
            :class="tender.decision === 'bid' ? 'text-success' : 'text-danger'"
          >{{ decisionLabel(tender.decision) }}</span>
        </p>
        <button
          v-if="tender.decision === 'bid' && tender.project_id"
          class="mt-3 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm transition-all"
          @click="router.push(`/tender-detail/${tender.project_id}`)"
        >
          查看投标项目 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getTender, uploadBidDocument, submitDecision, type Tender } from '../services/tender'

const router = useRouter()
const route = useRoute()
const tenderId = route.params.id as string

const tender = ref<Tender | null>(null)
const loading = ref(false)
const actionTab = ref<'bid' | 'reject'>('bid')
const rejectReason = ref('')
const submitting = ref(false)
const uploading = ref(false)

async function loadTender() {
  loading.value = true
  try {
    tender.value = await getTender(tenderId)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleBidUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    tender.value = await uploadBidDocument(tenderId, file)
  } catch (e) {
    console.error(e)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function handleReject() {
  submitting.value = true
  try {
    tender.value = await submitDecision(tenderId, {
      decision: 'reject',
      reason: rejectReason.value,
    })
  } catch (e) {
    console.error(e)
  } finally {
    submitting.value = false
  }
}

function decisionLabel(decision: string) {
  return { pending: '待处理', bid: '已投标', reject: '不投标' }[decision] || decision
}

onMounted(loadTender)
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

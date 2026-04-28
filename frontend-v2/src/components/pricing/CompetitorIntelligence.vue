<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
    <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
      <span class="mr-2">🔍</span>
      AI 竞商情报
    </h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">竞商信息录入</label>
          <div v-for="(comp, idx) in competitors" :key="idx" class="mb-3 p-3 bg-gray-50 rounded">
            <div class="grid grid-cols-2 gap-2 mb-2">
              <input
                v-model="comp.name"
                class="px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="公司名称"
              />
              <select
                v-model="comp.size"
                class="px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="">选择规模</option>
                <option value="大型">大型</option>
                <option value="中型">中型</option>
                <option value="小型">小型</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <input
                v-model="comp.industry"
                class="px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="行业(如IT服务)"
              />
              <input
                v-model.number="comp.historical_discount"
                type="number"
                step="0.01"
                min="0"
                max="1"
                class="px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="历史折扣率(0-1)"
              />
            </div>
            <button class="mt-2 text-xs text-danger hover:underline" @click="removeCompetitor(idx)">删除</button>
          </div>
          <button class="text-xs text-primary hover:underline" @click="addCompetitor">+ 添加竞商</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <button
            class="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 transition-all duration-300 text-sm"
            :disabled="predicting"
            @click="runPrediction"
          >
            {{ predicting ? 'AI预测中...' : '🔍 AI预测折扣率' }}
          </button>
          <button
            class="px-4 py-2 border border-gray-200 text-gray-700 rounded hover:bg-gray-50 transition-all duration-300 text-sm"
            :disabled="historyLoading"
            @click="learnFromHistory"
          >
            {{ historyLoading ? '学习中...' : '历史学习参数' }}
          </button>
        </div>
        <div v-if="historyMessage" class="text-xs text-gray-500">{{ historyMessage }}</div>
      </div>

      <div v-if="predictions.length" class="space-y-3">
        <div v-if="accompliceGroups.length" class="p-3 rounded border" :class="'bg-danger/5 border-danger/20'">
          <p class="text-sm font-medium text-danger mb-2 flex items-center">
            <span class="mr-1">⚠️</span>关联公司预警
          </p>
          <div v-for="(group, gi) in accompliceGroups" :key="gi" class="mb-1 text-xs text-gray-700">
            <span class="font-medium">第{{ gi + 1 }}组：</span>{{ group.join('、') }}
            <span class="text-danger ml-1">（同系公司同时参与投标，存在陪标风险）</span>
          </div>
        </div>

        <div v-for="pred in predictions" :key="pred.name" class="p-3 bg-gray-50 rounded border border-gray-100">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-800">{{ pred.name }}</span>
            <div class="flex items-center space-x-2">
              <span class="text-xs px-1.5 py-0.5 rounded" :class="positionClass(pred.market_position)">
                {{ positionLabel(pred.market_position) }}
              </span>
              <span v-if="pred.accomplice_alert && pred.accomplice_alert.risk_level !== 'low'" class="text-xs px-1.5 py-0.5 rounded" :class="alertLevelClass(pred.accomplice_alert.risk_level)">
                {{ alertLevelLabel(pred.accomplice_alert.risk_level) }}风险 {{ (pred.accomplice_probability * 100).toFixed(0) }}%
              </span>
              <span v-else-if="pred.accomplice_probability > 0.3" class="text-xs px-1.5 py-0.5 rounded bg-danger/20 text-danger">
                陪标风险 {{ (pred.accomplice_probability * 100).toFixed(0) }}%
              </span>
            </div>
          </div>

          <div class="flex items-center justify-between mb-2">
            <span class="text-lg font-bold text-primary">{{ (pred.point_estimate * 100).toFixed(1) }}%</span>
            <span class="text-xs text-gray-500">预测折扣率</span>
          </div>

          <div class="mb-2">
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>P10: {{ (pred.distribution.p10 * 100).toFixed(1) }}%</span>
              <span>P50: {{ (pred.distribution.p50 * 100).toFixed(1) }}%</span>
              <span>P90: {{ (pred.distribution.p90 * 100).toFixed(1) }}%</span>
            </div>
            <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="absolute h-full bg-primary/30 rounded-full"
                :style="{
                  left: ((pred.distribution.p10 * 100) / 100) + '%',
                  width: ((pred.distribution.p90 - pred.distribution.p10) * 100) + '%'
                }"
              ></div>
              <div
                class="absolute h-full w-0.5 bg-primary"
                :style="{ left: (pred.point_estimate * 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="flex items-center space-x-2 text-xs text-gray-500 mb-2">
            <span>置信度: {{ (pred.confidence * 100).toFixed(0) }}%</span>
            <div class="flex-1 h-1 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full rounded-full" :class="pred.confidence >= 0.7 ? 'bg-success' : 'bg-warning'" :style="{ width: (pred.confidence * 100) + '%' }"></div>
            </div>
          </div>

          <div v-if="pred.accomplice_alert && pred.accomplice_alert.reasons.length" class="mb-2 p-2 rounded text-xs" :class="pred.accomplice_alert.risk_level === 'high' ? 'bg-danger/5 border border-danger/10' : pred.accomplice_alert.risk_level === 'medium' ? 'bg-warning/5 border border-warning/10' : 'bg-gray-50 border border-gray-100'">
            <p class="font-medium mb-1" :class="pred.accomplice_alert.risk_level === 'high' ? 'text-danger' : pred.accomplice_alert.risk_level === 'medium' ? 'text-warning' : 'text-gray-600'">陪标分析</p>
            <div v-for="(reason, ri) in pred.accomplice_alert.reasons" :key="ri" class="flex items-start space-x-1 mb-0.5">
              <span class="text-gray-400 mt-0.5">•</span>
              <span class="text-gray-600">{{ reason }}</span>
            </div>
            <div v-if="pred.accomplice_alert.related_companies.length" class="mt-1 text-gray-500">
              关联公司: {{ pred.accomplice_alert.related_companies.join('、') }}
            </div>
            <div class="mt-1 text-gray-400">
              异常评分: {{ (pred.accomplice_alert.anomaly_score * 100).toFixed(0) }}%
            </div>
          </div>

          <div v-if="pred.evidence.length" class="text-xs text-gray-400">
            <span v-for="(ev, i) in pred.evidence" :key="i" class="inline-block mr-2">
              <span class="px-1 py-0.5 rounded" :class="reliabilityClass(ev.reliability)">{{ ev.source }}</span>
            </span>
          </div>
        </div>

        <div class="flex items-center justify-between p-3 border border-primary/20 bg-primary/5 rounded">
          <span class="text-sm text-gray-700">应用到博弈沙盘</span>
          <button class="px-3 py-1.5 text-xs bg-primary text-white rounded hover:bg-primary/90" @click="applyPredictions">
            应用预测结果
          </button>
        </div>
      </div>

      <div v-else-if="historyProfiles.length" class="space-y-3">
        <div v-for="profile in historyProfiles" :key="profile.name" class="p-3 bg-gray-50 rounded border border-gray-100">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-gray-800">{{ profile.name }}</span>
            <span class="text-xs text-gray-500">样本 {{ profile.sample_count }}</span>
          </div>
          <div class="grid grid-cols-2 gap-3 mb-2">
            <div>
              <p class="text-[11px] text-gray-500 mb-1">折扣均值</p>
              <p class="text-base font-semibold text-primary">{{ (profile.discount_belief_mean * 100).toFixed(1) }}%</p>
            </div>
            <div>
              <p class="text-[11px] text-gray-500 mb-1">折扣标准差</p>
              <p class="text-base font-semibold text-gray-800">{{ (profile.discount_belief_std * 100).toFixed(1) }}%</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2 text-[11px] text-gray-500">
            <span
              v-for="(count, source) in profile.source_breakdown"
              :key="source"
              class="px-1.5 py-0.5 border border-gray-200 rounded"
            >
              {{ historySourceLabel(source) }} {{ count }}
            </span>
          </div>
        </div>

        <div class="flex items-center justify-between p-3 border border-primary/20 bg-primary/5 rounded">
          <span class="text-sm text-gray-700">应用到博弈沙盘</span>
          <button class="px-3 py-1.5 text-xs bg-primary text-white rounded hover:bg-primary/90" @click="applyHistoryProfiles">
            应用历史参数
          </button>
        </div>
      </div>

      <div v-else class="flex items-center justify-center text-gray-400 text-sm">
        录入竞商信息后点击"AI预测折扣率"或"历史学习参数"
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { predictCompetitorIntel } from '../../services/competitorIntel'
import type { CompetitorPrediction } from '../../services/competitorIntel'
import { learnBiddingGameHistory } from '../../services/biddingGame'
import type { CompetitorHistoryProfile } from '../../services/biddingGame'

const props = withDefaults(defineProps<{
  projectId?: string
}>(), {
  projectId: undefined,
})

const emit = defineEmits<{
  (e: 'apply-predictions', predictions: CompetitorPrediction[]): void
  (e: 'apply-history-learning', profiles: CompetitorHistoryProfile[]): void
}>()

interface CompetitorInput {
  name: string
  industry: string
  region: string
  size: string
  historical_discount: number | null
}

const competitors = ref<CompetitorInput[]>([
  { name: '亚信', industry: 'IT服务', region: '全国', size: '大型', historical_discount: null },
  { name: '中软', industry: 'IT服务', region: '全国', size: '大型', historical_discount: null },
  { name: '浪潮', industry: '系统集成', region: '全国', size: '大型', historical_discount: null },
])

const predicting = ref(false)
const predictions = ref<CompetitorPrediction[]>([])
const accompliceGroups = ref<string[][]>([])
const historyLoading = ref(false)
const historyProfiles = ref<CompetitorHistoryProfile[]>([])
const historyMessage = ref('')

const addCompetitor = () => {
  competitors.value.push({ name: '', industry: '', region: '', size: '', historical_discount: null })
}

const removeCompetitor = (idx: number) => {
  competitors.value.splice(idx, 1)
}

const positionLabel = (pos: string) => {
  const map: Record<string, string> = { price_killer: '低价型', tech_oriented: '技术型', balanced: '均衡型' }
  return map[pos] || pos
}

const positionClass = (pos: string) => {
  const map: Record<string, string> = { price_killer: 'bg-danger/20 text-danger', tech_oriented: 'bg-success/20 text-success', balanced: 'bg-primary/20 text-primary' }
  return map[pos] || 'bg-gray-200 text-gray-600'
}

const alertLevelLabel = (level: string) => {
  const map: Record<string, string> = { high: '高', medium: '中', low: '低' }
  return map[level] || level
}

const alertLevelClass = (level: string) => {
  const map: Record<string, string> = { high: 'bg-danger/20 text-danger', medium: 'bg-warning/20 text-warning', low: 'bg-gray-200 text-gray-600' }
  return map[level] || 'bg-gray-200 text-gray-600'
}

const reliabilityClass = (r: string) => {
  const map: Record<string, string> = { A: 'bg-success/10 text-success', B: 'bg-primary/10 text-primary', C: 'bg-warning/10 text-warning', D: 'bg-danger/10 text-danger' }
  return map[r] || 'bg-gray-100 text-gray-500'
}

const historySourceLabel = (source: string) => {
  const map: Record<string, string> = {
    manual_historical_input: '手工历史',
    intel_prediction: '情报预测',
    agent_prior_mean: '沙盘先验',
    iterative_round: '迭代轮次',
  }
  return map[source] || source
}

const runPrediction = async () => {
  predicting.value = true
  try {
    console.info('[CompetitorIntelligence] Starting competitor prediction', {
      competitorCount: competitors.value.filter(c => c.name).length,
      projectId: props.projectId || 'ALL',
    })
    const payload = {
      project_id: props.projectId,
      competitors: competitors.value.filter(c => c.name).map(c => ({
        name: c.name,
        industry: c.industry,
        region: c.region,
        size: c.size,
        historical_discount: c.historical_discount ?? undefined,
      })),
    }
    const res = await predictCompetitorIntel(payload)
    predictions.value = res.predictions
    accompliceGroups.value = res.accomplice_groups || []
    historyProfiles.value = []
    historyMessage.value = ''
  } catch (e: any) {
    console.error('[CompetitorIntelligence] Prediction failed', e)
    alert(e.message || '竞商情报预测失败')
  } finally {
    predicting.value = false
  }
}

const applyPredictions = () => {
  emit('apply-predictions', predictions.value)
}

const learnFromHistory = async () => {
  const competitorNames = competitors.value
    .map(item => item.name.trim())
    .filter(Boolean)

  if (!competitorNames.length) {
    alert('请先录入至少一个竞商名称')
    return
  }

  historyLoading.value = true
  historyMessage.value = ''
  try {
    console.info('[CompetitorIntelligence] Starting history learning', {
      competitorCount: competitorNames.length,
      projectId: props.projectId || 'ALL',
    })
    const response = await learnBiddingGameHistory({
      project_id: props.projectId,
      competitor_names: competitorNames,
      limit: 50,
    })
    historyProfiles.value = response.profiles
    predictions.value = []
    accompliceGroups.value = []
    historyMessage.value = response.message
  } catch (e: any) {
    console.error('[CompetitorIntelligence] History learning failed', e)
    alert(e.message || '历史学习失败')
  } finally {
    historyLoading.value = false
  }
}

const applyHistoryProfiles = () => {
  emit('apply-history-learning', historyProfiles.value)
}
</script>

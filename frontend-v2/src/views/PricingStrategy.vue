<template>
  <div class="fade-in h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-3">
        <h2 class="text-2xl font-bold text-gray-800">报价策略</h2>
        <div class="relative">
          <input
            type="text"
            v-model="selectedProject"
            placeholder="搜索项目..."
            class="w-56 px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
            @focus="showProjectDropdown = true"
            @blur="onProjectInputBlur"
          />
          <div v-if="showProjectDropdown" class="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-md z-10 max-h-48 overflow-y-auto">
            <div
              v-for="project in filteredProjects"
              :key="project.id"
              class="px-3 py-1.5 hover:bg-gray-100 cursor-pointer transition-all duration-300 text-sm"
              @click="selectProject(project)"
            >
              {{ project.name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex border-b border-gray-200 mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-2 text-sm font-medium transition-all duration-200 border-b-2"
        :class="activeTab === tab.key
          ? 'text-primary border-primary'
          : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-show="activeTab === 'calculator'">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div class="lg:col-span-2 flex flex-col gap-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
                <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
                  <span class="mr-2">💰</span>报价参数
                </h3>
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">预算上限</label>
                    <div class="relative">
                      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">¥</span>
                      <input v-model.number="pricingParams.budget" type="number" class="w-full pl-8 pr-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300" />
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">价格评分方法</label>
                    <select v-model="pricingParams.pricingMethod" class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300">
                      <option value="vertexRandomK">顶点中间值法（K值随机）</option>
                      <option value="vertexFixedK">顶点中间值法（K值固定）</option>
                      <option value="linear">线性评分法</option>
                    </select>
                  </div>
                  <div v-if="pricingParams.pricingMethod.includes('vertex')" class="space-y-3 pl-4 border-l-2 border-primary/20">
                    <div v-if="pricingParams.pricingMethod === 'vertexRandomK'">
                      <label class="block text-sm font-medium text-gray-700 mb-1">K值范围</label>
                      <div class="flex items-center space-x-2">
                        <span class="text-sm text-gray-500">90%</span>
                        <input v-model.number="pricingParams.kValue" type="range" min="90" max="100" class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" />
                        <span class="text-sm text-gray-500">100%</span>
                      </div>
                      <div class="text-right text-sm font-medium text-gray-800 mt-1">{{ pricingParams.kValue }}%</div>
                    </div>
                    <div v-else>
                      <label class="block text-sm font-medium text-gray-700 mb-1">固定K值</label>
                      <div class="text-sm font-medium text-gray-800">90%</div>
                    </div>
                  </div>
                  <div v-if="pricingParams.pricingMethod === 'linear'" class="space-y-3 pl-4 border-l-2 border-primary/20">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">敏感系数 (λ)</label>
                      <div class="flex items-center space-x-2">
                        <input v-model.number="pricingParams.sensitivity" type="range" min="0.5" max="5" step="0.1" class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" />
                        <span class="w-14 text-right text-sm font-medium text-gray-800">{{ pricingParams.sensitivity.toFixed(1) }}%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">目标利润率</label>
                    <div class="flex items-center space-x-2">
                      <input v-model.number="pricingParams.profitMargin" type="range" min="5" max="30" class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary" />
                      <span class="w-12 text-right text-sm font-medium text-gray-800">{{ pricingParams.profitMargin }}%</span>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">风险系数</label>
                    <div class="flex items-center space-x-2">
                      <input v-model.number="pricingParams.riskFactor" type="range" min="1" max="5" class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-warning" />
                      <span class="w-12 text-right text-sm font-medium text-gray-800">{{ pricingParams.riskFactor }}级</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
                <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
                  <span class="mr-2">📊</span>报价金额
                </h3>
                <div class="space-y-4">
                  <div class="p-4 bg-gray-50 rounded-lg space-y-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">不含税报价</label>
                      <div class="relative">
                        <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                        <input v-model.number="exTaxPrice" type="number" class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">含税报价</label>
                      <div class="relative">
                        <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                        <input v-model.number="incTaxPrice" type="number" class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
                      </div>
                    </div>
                    <div class="flex items-center justify-between py-1 border-t border-b border-gray-100 my-1">
                      <label class="text-sm font-medium text-gray-700">折扣率</label>
                      <span class="text-sm font-semibold text-primary">{{ discountRateDisplay }}</span>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">不含税成本</label>
                      <div class="relative">
                        <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                        <input v-model.number="exTaxCost" type="number" readonly class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-gray-100" />
                      </div>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">含税成本</label>
                      <div class="relative">
                        <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                        <input v-model.number="incTaxCost" type="number" readonly class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-gray-100" />
                      </div>
                    </div>
                  </div>
                  <div class="flex items-center justify-between">
                    <label class="text-sm font-medium text-gray-700">税率</label>
                    <select v-model="taxRate" class="px-3 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                      <option value="0.06">6%</option>
                      <option value="0.09">9%</option>
                      <option value="0.13">13%</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <div class="flex flex-col md:flex-row items-start md:items-center justify-between mb-6">
                <h3 class="font-semibold text-gray-800 flex items-center mb-4 md:mb-0">
                  <span class="mr-2">🎯</span>得分预览
                </h3>
                <div class="flex items-center bg-gray-50 rounded-lg p-3 border border-gray-100 relative">
                  <div class="mr-6 pr-6 border-r border-gray-200">
                    <label class="block text-xs font-medium text-gray-500 mb-1">技术分</label>
                    <div class="flex items-center">
                      <input v-model.number="pricingParams.techScore" type="number" min="0" max="100" class="w-20 px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
                      <span class="ml-2 text-sm text-gray-600">分</span>
                    </div>
                  </div>
                  <div class="flex flex-col items-end">
                    <span class="text-xs font-medium text-gray-500 mb-1">预估总得分</span>
                    <div class="flex items-end">
                      <span class="text-3xl font-bold text-primary leading-none">{{ score }}</span>
                      <span class="text-sm text-gray-400 ml-1 mb-0.5">/100</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm text-gray-500">价格竞争力</span>
                    <span class="text-sm font-medium text-primary">{{ scores.priceCompetitiveness }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-primary rounded-full" :style="{ width: scores.priceCompetitiveness + '%' }"></div>
                  </div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm text-gray-500">利润合理性</span>
                    <span class="text-sm font-medium text-success">{{ scores.profitReasonability }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-success rounded-full" :style="{ width: scores.profitReasonability + '%' }"></div>
                  </div>
                </div>
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm text-gray-500">风险可控性</span>
                    <span class="text-sm font-medium text-warning">{{ scores.riskControllability }}</span>
                  </div>
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div class="h-full bg-warning rounded-full" :style="{ width: scores.riskControllability + '%' }"></div>
                  </div>
                </div>
              </div>

              <div class="bg-gradient-to-r from-primary/5 to-success/5 rounded-lg p-4 border border-primary/20">
                <div class="flex items-start space-x-3">
                  <span class="text-2xl">🤖</span>
                  <div>
                    <p class="text-sm font-medium text-gray-800 mb-1">AI建议</p>
                    <p class="text-sm text-gray-600">{{ aiAdvice }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="lg:col-span-2 flex flex-col gap-6">
            <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
                <span class="mr-2">📈</span>竞商报价模拟器
              </h3>
              <div class="border border-gray-100 rounded-lg p-4 mb-4">
                <div class="flex items-center justify-between mb-3">
                  <p class="text-sm font-medium text-gray-700">竞品折扣率设置（%）</p>
                  <div class="flex items-center space-x-2">
                    <button class="px-3 py-1.5 text-xs bg-primary/10 text-primary border border-primary/20 rounded-lg hover:bg-primary/20 transition-all duration-300" @click="autoAdjustToFirst">🎯 智能调价争取第一</button>
                    <button class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="addCompetitor">+ 新增公司</button>
                  </div>
                </div>
                <div class="space-y-2">
                  <div class="grid grid-cols-12 gap-2 text-xs text-gray-500">
                    <div class="col-span-5">公司名称</div>
                    <div class="col-span-4">折扣率</div>
                    <div class="col-span-3 text-right">操作</div>
                  </div>
                  <div v-for="item in competitorCompanies" :key="item.id" class="grid grid-cols-12 gap-2 items-center">
                    <input v-model="item.name" class="col-span-5 px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" placeholder="公司名称" />
                    <div class="col-span-4 relative">
                      <input v-model.number="item.discountRate" type="number" min="0" max="100" step="0.01" class="w-full px-2 py-1.5 pr-7 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
                      <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">%</span>
                    </div>
                    <div class="col-span-3 text-right">
                      <button class="px-2 py-1 text-xs text-danger hover:bg-red-50 rounded" @click="removeCompetitor(item.id)">删除</button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="overflow-x-auto border border-gray-100 rounded-lg">
                <table class="w-full text-sm">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">排名</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">公司</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">报价</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">折扣率</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">价格得分</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in rankedSimulationRows" :key="row.id" :class="row.isOur ? 'bg-primary/5' : 'bg-white'" class="border-t border-gray-100">
                      <td class="px-3 py-2">#{{ row.rank }}</td>
                      <td class="px-3 py-2"><span class="font-medium" :class="row.isOur ? 'text-primary' : 'text-gray-800'">{{ row.name }}</span></td>
                      <td class="px-3 py-2">¥{{ formatNumber(row.quotePrice) }}</td>
                      <td class="px-3 py-2">{{ formatPercent(row.discountRate) }}</td>
                      <td class="px-3 py-2 font-medium">{{ row.priceScore.toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="mt-4 text-xs text-gray-500">
                参与公司数：{{ rankedSimulationRows.length }}（含我方），我方排名：第 {{ ourRank }} 名
              </div>
              <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="border border-gray-100 rounded-lg p-4">
                  <p class="text-xs text-gray-500 mb-1">评审基准价 D</p>
                  <p class="text-base font-semibold text-gray-800">{{ benchmarkDisplay }}</p>
                </div>
                <div class="border border-gray-100 rounded-lg p-4">
                  <p class="text-xs text-gray-500 mb-1">最低评审价 D2</p>
                  <p class="text-base font-semibold text-gray-800">{{ minReviewPriceDisplay }}</p>
                </div>
              </div>
              <div class="mt-6 flex justify-end space-x-3">
                <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="resetStrategy">重置参数</button>
                <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300" :disabled="pricingParams.techScore < 60 || apiLoading" :class="{ 'opacity-50 cursor-not-allowed': pricingParams.techScore < 60 || apiLoading }" @click="callPricingApi">
                  {{ apiLoading ? '计算中...' : '应用报价策略' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'tech-score'">
        <TechScoreEvaluator @apply-tech-score="onApplyTechScore" />
      </div>

      <div v-show="activeTab === 'competitor-intel'">
        <CompetitorIntelligence
          :project-id="selectedProjectId"
          @apply-predictions="onApplyPredictions"
          @apply-history-learning="onApplyHistoryLearning"
        />
      </div>

      <div v-show="activeTab === 'bidding-game'">
        <BiddingGameSimulator
          ref="gameSimulatorRef"
          :project-id="selectedProjectId"
          @apply-optimal-bid="onApplyOptimalBid"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { listProjects } from '../services/project'
import { calculatePricing } from '../services/pricing'
import type { Project } from '../types'
import type { CompetitorPrediction } from '../services/competitorIntel'
import type { BiddingGameSimulateResponse, CompetitorHistoryProfile } from '../services/biddingGame'
import TechScoreEvaluator from '../components/pricing/TechScoreEvaluator.vue'
import CompetitorIntelligence from '../components/pricing/CompetitorIntelligence.vue'
import BiddingGameSimulator from '../components/pricing/BiddingGameSimulator.vue'

const tabs = [
  { key: 'calculator', label: '💰 报价计算器' },
  { key: 'tech-score', label: '🧠 AI技术分评估' },
  { key: 'competitor-intel', label: '🔍 竞商情报' },
  { key: 'bidding-game', label: '🎮 博弈沙盘' },
]

type GameSimulatorExpose = {
  ourAgent: { tech_score: number }
  applyHistoryProfiles: (profiles: CompetitorHistoryProfile[]) => void
}

const activeTab = ref('calculator')
const gameSimulatorRef = ref<GameSimulatorExpose | null>(null)

const pricingParams = ref({
  budget: 0,
  profitMargin: 15,
  riskFactor: 3,
  techScore: 75,
  pricingMethod: 'linear',
  kValue: 95,
  sensitivity: 2,
})

const exTaxPrice = ref(0)
const incTaxPrice = ref(0)
const taxRate = ref(0.06)
const exTaxCost = ref(0)
const incTaxCost = ref(0)
const selectedProject = ref('')
const showProjectDropdown = ref(false)
const apiLoading = ref(false)

const competitorCompanies = ref<Array<{ id: number; name: string; discountRate: number }>>([
  { id: 1, name: '竞品A', discountRate: 10 },
])
const nextCompetitorId = ref(2)
const projects = ref<Array<{ id: string; name: string; amount: string }>>([])

const filteredProjects = computed(() => {
  if (!selectedProject.value) return projects.value
  return projects.value.filter(p => p.name.toLowerCase().includes(selectedProject.value.toLowerCase()))
})
const selectedProjectRecord = computed(() => projects.value.find(project => project.name === selectedProject.value) || null)
const selectedProjectId = computed(() => selectedProjectRecord.value?.id)

const selectProject = (project: { id: string; name: string }) => {
  selectedProject.value = project.name
  showProjectDropdown.value = false
}

const onProjectInputBlur = () => {
  setTimeout(() => {
    showProjectDropdown.value = false
  }, 200)
}

const safeBudget = computed(() => Math.max(pricingParams.value.budget || 0, 0))
const totalPrice = computed(() => incTaxPrice.value || 0)

const ourDiscountRate = computed(() => {
  if (!safeBudget.value) return 0
  return ((safeBudget.value - totalPrice.value) / safeBudget.value) * 100
})

const discountRateDisplay = computed(() => `${ourDiscountRate.value.toFixed(2)}%`)

const clampDiscountRate = (value: number) => {
  const n = Number(value)
  if (Number.isNaN(n)) return 0
  if (n < 0) return 0
  if (n > 100) return 100
  return n
}

const addCompetitor = () => {
  competitorCompanies.value.push({ id: nextCompetitorId.value++, name: `新公司${nextCompetitorId.value - 1}`, discountRate: 5 })
}

const removeCompetitor = (id: number) => {
  if (competitorCompanies.value.length <= 1) return
  competitorCompanies.value = competitorCompanies.value.filter(item => item.id !== id)
}

const calcAverage = (values: number[]) => values.reduce((sum, v) => sum + v, 0) / values.length

const calcVertexBenchmark = (reviewPrices: number[], kValue: number) => {
  if (!reviewPrices.length) return 0
  if (reviewPrices.length <= 5) return calcAverage(reviewPrices) * kValue
  const sorted = [...reviewPrices].sort((a, b) => a - b)
  const trimmed = sorted.slice(1, -1)
  if (!trimmed.length) return calcAverage(sorted) * kValue
  const avg = calcAverage(trimmed)
  if (avg === 0) return 0
  const filtered = trimmed.filter(price => Math.abs(price - avg) / avg <= 0.2)
  const finalList = filtered.length > 0 ? filtered : trimmed
  return calcAverage(finalList) * kValue
}

const calcVertexScore = (d1: number, d: number, e = 1) => {
  if (!d) return 0
  if (d1 === d) return 100
  if (d1 > d) return 100 - (Math.abs(d1 - d) / d) * 100 * e
  return 100 - (Math.abs(d1 - d) / d) * 100 * (e / 2)
}

const calcLinearScore = (d1: number, d2: number, d: number, lambda: number) => {
  if (!d || !lambda) return 0
  return 100 - (d1 - d2) / (d * lambda)
}

const runSimulationWithOurDiscount = (ourDiscount: number) => {
  const ourQuote = safeBudget.value * (1 - ourDiscount / 100)
  const rows = [
    { id: 'our', name: '我方报价', isOur: true, quotePrice: Math.max(ourQuote, 0), discountRate: clampDiscountRate(ourDiscount) },
    ...competitorCompanies.value.map(item => {
      const discountRate = clampDiscountRate(item.discountRate)
      const quotePrice = safeBudget.value * (1 - discountRate / 100)
      return { id: item.id, name: item.name || `公司${item.id}`, isOur: false, quotePrice: Math.max(quotePrice, 0), discountRate }
    }),
  ]

  const method = pricingParams.value.pricingMethod
  const reviewPrices = rows.map(row => method === 'vertexRandomK' ? 1 - row.discountRate / 100 : row.quotePrice)
  let benchmark = 0
  let minReviewPrice = Math.min(...reviewPrices)
  const lambda = (pricingParams.value.sensitivity || 2) / 100

  if (method === 'vertexRandomK') benchmark = calcVertexBenchmark(reviewPrices, (pricingParams.value.kValue || 95) / 100)
  else if (method === 'vertexFixedK') benchmark = calcVertexBenchmark(reviewPrices, 0.9)
  else benchmark = calcAverage(reviewPrices)

  const scoredRows = rows.map((row, idx) => {
    const d1 = reviewPrices[idx]
    let rawScore = 0
    if (method === 'vertexRandomK' || method === 'vertexFixedK') rawScore = calcVertexScore(d1, benchmark, 1)
    else rawScore = calcLinearScore(d1, minReviewPrice, benchmark, lambda)
    const priceScore = Math.max(0, Math.round(rawScore * 100) / 100)
    return { ...row, reviewPrice: d1, priceScore }
  })

  return [...scoredRows].sort((a, b) => b.priceScore - a.priceScore || a.quotePrice - b.quotePrice).map((row, index) => ({ ...row, rank: index + 1 }))
}

const simulationResult = computed(() => {
  const ranked = runSimulationWithOurDiscount(ourDiscountRate.value)
  const method = pricingParams.value.pricingMethod
  const reviewPrices = ranked.map((r: any) => r.reviewPrice)
  let benchmark = 0
  const lambda = (pricingParams.value.sensitivity || 2) / 100
  if (method === 'vertexRandomK') benchmark = calcVertexBenchmark(reviewPrices, (pricingParams.value.kValue || 95) / 100)
  else if (method === 'vertexFixedK') benchmark = calcVertexBenchmark(reviewPrices, 0.9)
  else benchmark = calcAverage(reviewPrices)
  return { ranked, benchmark, minReviewPrice: Math.min(...reviewPrices), lambda }
})

const autoAdjustToFirst = () => {
  let bestDiscount = -1
  for (let d = 0; d <= 100; d += 0.1) {
    const ranked = runSimulationWithOurDiscount(d)
    const ourResult = ranked.find((r: any) => r.isOur)
    if (ourResult && ourResult.rank === 1) { bestDiscount = d; break }
  }
  if (bestDiscount !== -1) {
    incTaxPrice.value = Math.round(safeBudget.value * (1 - bestDiscount / 100) * 100) / 100
  } else {
    alert('当前参数下无法找到排名第一的报价组合')
  }
}

const rankedSimulationRows = computed(() => simulationResult.value.ranked)
const ourSimulationRow = computed(() => rankedSimulationRows.value.find((row: any) => row.isOur) || null)
const ourRank = computed(() => ourSimulationRow.value?.rank || '-')

const benchmarkDisplay = computed(() => {
  if (pricingParams.value.pricingMethod === 'vertexRandomK') return simulationResult.value.benchmark.toFixed(4)
  return `¥${formatNumber(simulationResult.value.benchmark)}`
})

const minReviewPriceDisplay = computed(() => {
  if (pricingParams.value.pricingMethod === 'linear') return `¥${formatNumber(simulationResult.value.minReviewPrice)}`
  return '-'
})

const calculatePriceScore = () => ourSimulationRow.value?.priceScore || 0

const scores = computed(() => {
  let budgetRatio = safeBudget.value > 0 ? totalPrice.value / safeBudget.value : 0
  let priceCompetitiveness = budgetRatio < 0.9 ? 90 : budgetRatio < 0.95 ? 80 : budgetRatio < 1 ? 70 : 50
  let profitReasonability = (pricingParams.value.profitMargin >= 15 && pricingParams.value.profitMargin <= 22) ? 90 : (pricingParams.value.profitMargin < 10 || pricingParams.value.profitMargin > 25) ? 60 : 75
  let riskControllability = pricingParams.value.riskFactor <= 2 ? 90 : pricingParams.value.riskFactor >= 4 ? 65 : 80
  return {
    priceCompetitiveness: Math.round(priceCompetitiveness * 100) / 100,
    profitReasonability: Math.round(profitReasonability * 100) / 100,
    riskControllability: Math.round(riskControllability * 100) / 100,
  }
})

const score = computed(() => {
  if (pricingParams.value.techScore < 60) return 0
  return Math.round((pricingParams.value.techScore * 0.5 + calculatePriceScore() * 0.5) * 100) / 100
})

const aiAdvice = computed(() => {
  if (pricingParams.value.techScore < 60) return '技术分低于60分，不得参与报价分评审。请先提高技术方案质量。'
  const priceScore = calculatePriceScore()
  if (ourRank.value === 1 && priceScore >= 90) return '当前报价在模拟对手中排名靠前且价格得分高，建议保持并关注利润空间。'
  if (ourRank.value !== '-' && ourRank.value <= 3) return '当前报价具备竞争力，可微调折扣率并复算，观察排名变化后再定稿。'
  return '当前模拟排名偏后，建议适当提高折扣率或优化成本结构后再次测算。'
})

const formatNumber = (value: number) => Number(value || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const formatPercent = (value: number) => `${Number(value || 0).toFixed(2)}%`

const callPricingApi = async () => {
  if (!safeBudget.value) { alert('请先选择项目并设置预算'); return }
  apiLoading.value = true
  try {
    const payload = {
      budget: safeBudget.value,
      inc_tax_price: incTaxPrice.value || undefined,
      ex_tax_price: exTaxPrice.value || undefined,
      tax_rate: taxRate.value,
      profit_margin: pricingParams.value.profitMargin,
      risk_factor: pricingParams.value.riskFactor,
      pricing_method: pricingParams.value.pricingMethod,
      k_value: pricingParams.value.kValue,
      sensitivity: pricingParams.value.sensitivity,
      effective_bidder_count: rankedSimulationRows.value.length,
      tech_score: pricingParams.value.techScore,
      competitors: competitorCompanies.value.map(c => ({ name: c.name, discount_rate: c.discountRate })),
    }
    const res = await calculatePricing(payload)
    alert(res.message || '报价计算成功')
  } catch (e: any) {
    alert(e.message || '报价计算失败')
  } finally {
    apiLoading.value = false
  }
}

const resetStrategy = () => {
  pricingParams.value = { budget: 0, profitMargin: 15, riskFactor: 3, techScore: 75, pricingMethod: 'linear', kValue: 95, sensitivity: 2 }
  exTaxPrice.value = 0; incTaxPrice.value = 0; taxRate.value = 0.06
  competitorCompanies.value = [{ id: 1, name: '竞品A', discountRate: 10 }]
  nextCompetitorId.value = 2
}

const onApplyTechScore = (score: number) => {
  pricingParams.value.techScore = Math.round(score)
  activeTab.value = 'calculator'
}

const onApplyPredictions = (predictions: CompetitorPrediction[]) => {
  console.info('[PricingStrategy] Applying competitor predictions', {
    predictionCount: predictions.length,
    projectId: selectedProjectId.value || 'ALL',
  })
  competitorCompanies.value = predictions.map((p, i) => ({
    id: i + 1,
    name: p.name,
    discountRate: Math.round(p.point_estimate * 10000) / 100,
  }))
  nextCompetitorId.value = predictions.length + 1
  activeTab.value = 'calculator'
}

const onApplyHistoryLearning = (profiles: CompetitorHistoryProfile[]) => {
  console.info('[PricingStrategy] Applying history learning profiles', {
    profileCount: profiles.length,
    projectId: selectedProjectId.value || 'ALL',
  })
  if (!profiles.length) {
    alert('暂无可应用的历史参数')
    return
  }
  gameSimulatorRef.value?.applyHistoryProfiles(profiles)
  activeTab.value = 'bidding-game'
}

const onApplyOptimalBid = (result: BiddingGameSimulateResponse) => {
  const optimalPrice = result.optimal_bid.recommended_price
  incTaxPrice.value = Math.round(optimalPrice * 100) / 100
  pricingParams.value.techScore = Math.round(gameSimulatorRef.value?.ourAgent.tech_score || pricingParams.value.techScore)
  activeTab.value = 'calculator'
}

watch(exTaxPrice, (newValue) => { if (newValue != null) incTaxPrice.value = Math.round(newValue * (1 + taxRate.value) * 100) / 100 })
watch(incTaxPrice, (newValue) => { if (newValue != null) exTaxPrice.value = Math.round(newValue / (1 + taxRate.value) * 100) / 100 })
watch([exTaxPrice, () => pricingParams.value.profitMargin], ([newExTaxPrice, newProfitMargin]) => {
  if (newExTaxPrice != null && newProfitMargin != null) {
    exTaxCost.value = Math.round(newExTaxPrice / (1 + newProfitMargin / 100) * 100) / 100
    incTaxCost.value = Math.round(exTaxCost.value * (1 + taxRate.value) * 100) / 100
  }
}, { immediate: true })
watch(taxRate, (newValue) => {
  if (newValue != null) {
    incTaxPrice.value = Math.round(exTaxPrice.value * (1 + newValue) * 100) / 100
    incTaxCost.value = Math.round(exTaxCost.value * (1 + newValue) * 100) / 100
  }
})

onMounted(async () => {
  try {
    const projList = await listProjects()
    projects.value = projList.map((p: Project) => ({ id: p.id, name: p.name, amount: p.amount }))
    if (projList.length > 0) {
      selectedProject.value = projList[0].name
      const amount = parseFloat(projList[0].amount.replace(/[^\d.]/g, ''))
      if (!isNaN(amount)) pricingParams.value.budget = amount
    }
  } catch (e) {
    console.error('[PricingStrategy] Load projects failed', e)
  }
})
</script>

<style scoped>
</style>

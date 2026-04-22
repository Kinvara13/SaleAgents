<template>
  <div class="fade-in h-full flex flex-col">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-3">
        <h2 class="text-2xl font-bold text-gray-800">报价策略计算器</h2>
        <!-- 项目选择下拉框 -->
        <div class="relative">
          <input 
            type="text" 
            v-model="selectedProject" 
            placeholder="搜索项目..." 
            class="w-56 px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
            @focus="showProjectDropdown = true"
            @blur="window.setTimeout(() => showProjectDropdown = false, 200)"
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
      <button
        class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 transition-all duration-300"
        @click="generateOffer"
      >
        生成报价方案
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
      <!-- 左侧：参数、金额、得分预览 -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 报价参数 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
              <span class="mr-2">💰</span>
              报价参数
            </h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">预算上限</label>
                <div class="relative">
                  <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">¥</span>
                  <input
                    v-model.number="pricingParams.budget"
                    type="number"
                    class="w-full pl-8 pr-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">价格评分方法</label>
                <select 
                  v-model="pricingParams.pricingMethod"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                >
                  <option value="vertexRandomK">顶点中间值法（K值随机）</option>
                  <option value="vertexFixedK">顶点中间值法（K值固定）</option>
                  <option value="linear">线性评分法</option>
                </select>
              </div>
              
              <!-- 顶点中间值法参数 -->
              <div v-if="pricingParams.pricingMethod.includes('vertex')" class="space-y-3 pl-4 border-l-2 border-primary/20">
                <div v-if="pricingParams.pricingMethod === 'vertexRandomK'">
                  <label class="block text-sm font-medium text-gray-700 mb-1">K值范围</label>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">90%</span>
                    <input
                      v-model.number="pricingParams.kValue"
                      type="range"
                      min="90"
                      max="100"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
                    />
                    <span class="text-sm text-gray-500">100%</span>
                  </div>
                  <div class="text-right text-sm font-medium text-gray-800 mt-1">{{ pricingParams.kValue }}%</div>
                </div>
                <div v-else>
                  <label class="block text-sm font-medium text-gray-700 mb-1">固定K值</label>
                  <div class="text-sm font-medium text-gray-800">90%</div>
                </div>
                <p class="text-xs text-gray-500">
                  有效应答人数量用于决定基准价计算分支（≤5 或 >5）。
                </p>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">有效应答人数量</label>
                  <input
                    v-model.number="pricingParams.effectiveBidderCount"
                    type="number"
                    min="1"
                    class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300"
                  />
                  <p class="mt-1 text-xs text-gray-500">
                    当前录入公司数（含我方）为 {{ rankedSimulationRows.length }}。
                  </p>
                </div>
              </div>
              
              <!-- 线性评分法参数 -->
              <div v-if="pricingParams.pricingMethod === 'linear'" class="space-y-3 pl-4 border-l-2 border-primary/20">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">敏感系数 (λ)</label>
                  <div class="flex items-center space-x-2">
                    <input
                      v-model.number="pricingParams.sensitivity"
                      type="range"
                      min="0.5"
                      max="5"
                      step="0.1"
                      class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
                    />
                    <span class="w-14 text-right text-sm font-medium text-gray-800">{{ pricingParams.sensitivity.toFixed(1) }}%</span>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">线性评分法下与有效应答人数量无关，λ默认2%。</p>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">目标利润率</label>
                <div class="flex items-center space-x-2">
                  <input
                    v-model.number="pricingParams.profitMargin"
                    type="range"
                    min="5"
                    max="30"
                    class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                  <span class="w-12 text-right text-sm font-medium text-gray-800">{{ pricingParams.profitMargin }}%</span>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">风险系数</label>
                <div class="flex items-center space-x-2">
                  <input
                    v-model.number="pricingParams.riskFactor"
                    type="range"
                    min="1"
                    max="5"
                    class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-warning"
                  />
                  <span class="w-12 text-right text-sm font-medium text-gray-800">{{ pricingParams.riskFactor }}级</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 报价金额 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
              <span class="mr-2">📊</span>
              报价金额
            </h3>
            <div class="space-y-4">
              <div class="p-4 bg-gray-50 rounded-lg space-y-3">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">不含税报价</label>
                  <div class="relative">
                    <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                    <input
                      v-model.number="exTaxPrice"
                      type="number"
                      class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">含税报价</label>
                  <div class="relative">
                    <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                    <input
                      v-model.number="incTaxPrice"
                      type="number"
                      class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>
                <div class="flex items-center justify-between py-1 border-t border-b border-gray-100 my-1">
                  <label class="text-sm font-medium text-gray-700">折扣率（相对预算）</label>
                  <span class="text-sm font-semibold text-primary">{{ discountRateDisplay }}</span>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">不含税成本</label>
                  <div class="relative">
                    <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                    <input
                      v-model.number="exTaxCost"
                      type="number"
                      class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-gray-100"
                      readonly
                    />
                  </div>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">含税成本</label>
                  <div class="relative">
                    <span class="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">¥</span>
                    <input
                      v-model.number="incTaxCost"
                      type="number"
                      class="w-full pl-6 pr-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary bg-gray-100"
                      readonly
                    />
                  </div>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium text-gray-700">税率</label>
                <select 
                  v-model="taxRate"
                  class="px-3 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="0.06">6%</option>
                  <option value="0.09">9%</option>
                  <option value="0.13">13%</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- 实际得分预览 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between mb-6">
            <h3 class="font-semibold text-gray-800 flex items-center mb-4 md:mb-0">
              <span class="mr-2">🎯</span>
              实际得分预览
            </h3>
            <div class="flex items-center bg-gray-50 rounded-lg p-3 border border-gray-100 relative">
              <div class="mr-6 pr-6 border-r border-gray-200">
                <label class="block text-xs font-medium text-gray-500 mb-1">技术分</label>
                <div class="flex items-center">
                  <input
                    v-model.number="pricingParams.techScore"
                    type="number"
                    min="0"
                    max="100"
                    class="w-20 px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  <span class="ml-2 text-sm text-gray-600">分</span>
                </div>
                <p v-if="pricingParams.techScore < 60" class="absolute -bottom-5 left-3 text-[10px] text-danger whitespace-nowrap">技术分需≥60分</p>
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

          <div class="mb-6 rounded-lg border border-gray-100 bg-gray-50 p-4">
            <p class="text-sm font-medium text-gray-800 mb-1">当前价格规则说明</p>
            <p class="text-sm text-gray-600">{{ currentRuleDescription }}</p>
          </div>

          <div class="bg-gradient-to-r from-primary/5 to-success/5 rounded-lg p-4 border border-primary/20">
            <div class="flex items-start space-x-3">
              <span class="text-2xl">🤖</span>
              <div>
                <p class="text-sm font-medium text-gray-800 mb-1">AI建议</p>
                <p class="text-sm text-gray-600 typing-animation">
                  {{ aiAdvice }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：竞商报价模拟器 -->
      <div class="lg:col-span-2 flex flex-col gap-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
            <span class="mr-2">📈</span>
            竞商报价模拟器
          </h3>

          <div class="border border-gray-100 rounded-lg p-4 mb-4">
            <div class="flex items-center justify-between mb-3">
              <p class="text-sm font-medium text-gray-700">竞品折扣率设置（%）</p>
              <div class="flex items-center space-x-2">
                <button
                  class="px-3 py-1.5 text-xs bg-primary/10 text-primary border border-primary/20 rounded-lg hover:bg-primary/20 transition-all duration-300"
                  @click="autoAdjustToFirst"
                  title="自动调整我司报价，争取价格得分第一"
                >
                  🎯 智能调价争取第一
                </button>
                <button
                  class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-300"
                  @click="addCompetitor"
                >
                  + 新增公司
                </button>
              </div>
            </div>
            <div class="space-y-2">
              <div class="grid grid-cols-12 gap-2 text-xs text-gray-500">
                <div class="col-span-5">公司名称</div>
                <div class="col-span-4">折扣率</div>
                <div class="col-span-3 text-right">操作</div>
              </div>
              <div
                v-for="item in competitorCompanies"
                :key="item.id"
                class="grid grid-cols-12 gap-2 items-center"
              >
                <input
                  v-model="item.name"
                  class="col-span-5 px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="公司名称"
                />
                <div class="col-span-4 relative">
                  <input
                    v-model.number="item.discountRate"
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    class="w-full px-2 py-1.5 pr-7 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  <span class="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500">%</span>
                </div>
                <div class="col-span-3 text-right">
                  <button
                    class="px-2 py-1 text-xs text-danger hover:bg-red-50 rounded"
                    @click="removeCompetitor(item.id)"
                  >
                    删除
                  </button>
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
                <tr
                  v-for="row in rankedSimulationRows"
                  :key="row.id"
                  :class="row.isOur ? 'bg-primary/5' : 'bg-white'"
                  class="border-t border-gray-100"
                >
                  <td class="px-3 py-2">#{{ row.rank }}</td>
                  <td class="px-3 py-2">
                    <span class="font-medium" :class="row.isOur ? 'text-primary' : 'text-gray-800'">{{ row.name }}</span>
                  </td>
                  <td class="px-3 py-2">¥{{ formatNumber(row.quotePrice) }}</td>
                  <td class="px-3 py-2">{{ formatPercent(row.discountRate) }}</td>
                  <td class="px-3 py-2 font-medium">{{ row.priceScore.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-4 text-xs text-gray-500">
            当前参与公司数：{{ rankedSimulationRows.length }}（含我方），我方当前排名：第 {{ ourRank }} 名
          </div>

          <div class="mt-2 text-xs text-gray-500">
            规则细节：{{ simulatorRuleNote }}
          </div>

          <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="border border-gray-100 rounded-lg p-4">
              <p class="text-xs text-gray-500 mb-1">评审基准价 D</p>
              <p class="text-base font-semibold text-gray-800">{{ benchmarkDisplay }}</p>
            </div>
            <div class="border border-gray-100 rounded-lg p-4">
              <p class="text-xs text-gray-500 mb-1">最低评审价 D2（线性法）</p>
              <p class="text-base font-semibold text-gray-800">{{ minReviewPriceDisplay }}</p>
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button
              class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300"
              @click="resetStrategy"
            >
              重置参数
            </button>
            <button
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300"
              :disabled="pricingParams.techScore < 60 || apiLoading"
              :class="{ 'opacity-50 cursor-not-allowed': pricingParams.techScore < 60 || apiLoading }"
              @click="callPricingApi"
            >
              {{ apiLoading ? '计算中...' : '应用报价策略' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { listProjects } from '../services/project'
import { calculatePricing } from '../services/pricing'
import type { Project } from '../types'

const pricingParams = ref({
  budget: 0,
  profitMargin: 15,
  riskFactor: 3,
  techScore: 75,
  pricingMethod: 'linear',
  kValue: 95,
  sensitivity: 2
})

const exTaxPrice = ref(0)
const incTaxPrice = ref(0)
const taxRate = ref(0.06)

const exTaxCost = ref(0)
const incTaxCost = ref(0)

const selectedProject = ref('')
const showProjectDropdown = ref(false)

const competitorCompanies = ref<Array<{ id: number; name: string; discountRate: number }>>([
  { id: 1, name: '竞品A', discountRate: 10 }
])
const nextCompetitorId = ref(2)

const projects = ref<Array<{ id: string; name: string }>>([])

const filteredProjects = computed(() => {
  if (!selectedProject.value) return projects.value
  return projects.value.filter(project =>
    project.name.toLowerCase().includes(selectedProject.value.toLowerCase())
  )
})

const selectProject = (project) => {
  selectedProject.value = project.name
  showProjectDropdown.value = false
}

const selectedProjectId = ref<string>('')
const apiLoading = ref(false)

const callPricingApi = async () => {
  if (!safeBudget.value) {
    alert('请先选择项目并设置预算')
    return
  }
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
      competitors: competitorCompanies.value.map(c => ({
        name: c.name,
        discount_rate: c.discountRate
      }))
    }
    const res = await calculatePricing(payload)
    if (res.competitors && res.competitors.length > 0) {
      console.log('API计算结果:', res)
    }
    alert(res.message || '报价计算成功')
  } catch (e: any) {
    alert(e.message || '报价计算失败')
  } finally {
    apiLoading.value = false
  }
}



watch(exTaxPrice, (newValue) => {
  if (newValue !== null && newValue !== undefined) {
    incTaxPrice.value = Math.round(newValue * (1 + taxRate.value) * 100) / 100
  }
})

watch(incTaxPrice, (newValue) => {
  if (newValue !== null && newValue !== undefined) {
    exTaxPrice.value = Math.round(newValue / (1 + taxRate.value) * 100) / 100
  }
})

watch([exTaxPrice, () => pricingParams.value.profitMargin], ([newExTaxPrice, newProfitMargin]) => {
  if (newExTaxPrice !== null && newExTaxPrice !== undefined && newProfitMargin !== null && newProfitMargin !== undefined) {
    exTaxCost.value = Math.round(newExTaxPrice / (1 + newProfitMargin / 100) * 100) / 100
    incTaxCost.value = Math.round(exTaxCost.value * (1 + taxRate.value) * 100) / 100
  }
}, { immediate: true })

watch(taxRate, (newValue) => {
  if (newValue !== null && newValue !== undefined) {
    incTaxPrice.value = Math.round(exTaxPrice.value * (1 + newValue) * 100) / 100
    incTaxCost.value = Math.round(exTaxCost.value * (1 + newValue) * 100) / 100
  }
})

const totalPrice = computed(() => incTaxPrice.value || 0)
const safeBudget = computed(() => Math.max(pricingParams.value.budget || 0, 0))

const ourDiscountRate = computed(() => {
  if (!safeBudget.value) return 0
  return ((safeBudget.value - totalPrice.value) / safeBudget.value) * 100
})

const discountRateDisplay = computed(() => `${ourDiscountRate.value.toFixed(2)}%`)

const clampDiscountRate = (value) => {
  const n = Number(value)
  if (Number.isNaN(n)) return 0
  if (n < 0) return 0
  if (n > 100) return 100
  return n
}

const addCompetitor = () => {
  competitorCompanies.value.push({
    id: nextCompetitorId.value++,
    name: `新公司${nextCompetitorId.value - 1}`,
    discountRate: 5
  })
}

const removeCompetitor = (id) => {
  if (competitorCompanies.value.length <= 1) return
  competitorCompanies.value = competitorCompanies.value.filter(item => item.id !== id)
}



const calcAverage = (values) => values.reduce((sum, v) => sum + v, 0) / values.length

const calcVertexBenchmark = (reviewPrices, kValue) => {
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

const calcVertexScore = (d1, d, e = 1) => {
  if (!d) return 0
  if (d1 === d) return 100
  if (d1 > d) return 100 - (Math.abs(d1 - d) / d) * 100 * e
  return 100 - (Math.abs(d1 - d) / d) * 100 * (e / 2)
}

const calcLinearScore = (d1, d2, d, lambda) => {
  if (!d || !lambda) return 0
  return 100 - (d1 - d2) / (d * lambda)
}

const runSimulationWithOurDiscount = (ourDiscount) => {
  const ourQuote = safeBudget.value * (1 - ourDiscount / 100)
  const rows = [
    {
      id: 'our',
      name: '我方报价',
      isOur: true,
      quotePrice: Math.max(ourQuote, 0),
      discountRate: clampDiscountRate(ourDiscount)
    },
    ...competitorCompanies.value.map(item => {
      const discountRate = clampDiscountRate(item.discountRate)
      const quotePrice = safeBudget.value * (1 - discountRate / 100)
      return {
        id: item.id,
        name: item.name || `公司${item.id}`,
        isOur: false,
        quotePrice: Math.max(quotePrice, 0),
        discountRate
      }
    })
  ]

  const method = pricingParams.value.pricingMethod
  const reviewPrices = rows.map(row => {
    if (method === 'vertexRandomK') {
      return 1 - row.discountRate / 100
    }
    return row.quotePrice
  })

  let benchmark = 0
  let minReviewPrice = Math.min(...reviewPrices)
  const lambda = (pricingParams.value.sensitivity || 2) / 100

  if (method === 'vertexRandomK') {
    benchmark = calcVertexBenchmark(reviewPrices, (pricingParams.value.kValue || 95) / 100)
  } else if (method === 'vertexFixedK') {
    benchmark = calcVertexBenchmark(reviewPrices, 0.9)
  } else {
    benchmark = calcAverage(reviewPrices)
  }

  const scoredRows = rows.map((row, idx) => {
    const d1 = reviewPrices[idx]
    let rawScore = 0
    if (method === 'vertexRandomK' || method === 'vertexFixedK') {
      rawScore = calcVertexScore(d1, benchmark, 1)
    } else {
      rawScore = calcLinearScore(d1, minReviewPrice, benchmark, lambda)
    }
    const priceScore = Math.max(0, Math.round(rawScore * 100) / 100)
    return { ...row, reviewPrice: d1, priceScore }
  })

  return [...scoredRows]
    .sort((a, b) => b.priceScore - a.priceScore || a.quotePrice - b.quotePrice)
    .map((row, index) => ({ ...row, rank: index + 1 }))
}

const simulationResult = computed(() => {
  const ranked = runSimulationWithOurDiscount(ourDiscountRate.value)
  const method = pricingParams.value.pricingMethod
  
  const reviewPrices = ranked.map(r => r.reviewPrice)
  let benchmark = 0
  let minReviewPrice = Math.min(...reviewPrices)
  const lambda = (pricingParams.value.sensitivity || 2) / 100

  if (method === 'vertexRandomK') {
    benchmark = calcVertexBenchmark(reviewPrices, (pricingParams.value.kValue || 95) / 100)
  } else if (method === 'vertexFixedK') {
    benchmark = calcVertexBenchmark(reviewPrices, 0.9)
  } else {
    benchmark = calcAverage(reviewPrices)
  }

  return {
    ranked,
    benchmark,
    minReviewPrice,
    lambda
  }
})

const autoAdjustToFirst = () => {
  // 遍历 0% 到 100%，步长 0.1%，找到能排名第一的最小折扣率（即最高报价）
  let bestDiscount = -1
  for (let d = 0; d <= 100; d += 0.1) {
    const ranked = runSimulationWithOurDiscount(d)
    const ourResult = ranked.find(r => r.isOur)
    // 排名第一且与其他公司得分不完全相同（严格大于或同分但报价更低，由于这里同分看报价，我们要确保rank=1）
    if (ourResult && ourResult.rank === 1) {
      bestDiscount = d
      break
    }
  }

  if (bestDiscount !== -1) {
    const newIncTaxPrice = safeBudget.value * (1 - bestDiscount / 100)
    incTaxPrice.value = Math.round(newIncTaxPrice * 100) / 100
  } else {
    alert('当前参数下无法找到排名第一的报价组合，请尝试调整利润率或修改竞品折扣率。')
  }
}

const rankedSimulationRows = computed(() => simulationResult.value.ranked)

const ourSimulationRow = computed(() => {
  return rankedSimulationRows.value.find(row => row.isOur) || null
})

const ourRank = computed(() => ourSimulationRow.value?.rank || '-')

const benchmarkDisplay = computed(() => {
  if (pricingParams.value.pricingMethod === 'vertexRandomK') {
    return simulationResult.value.benchmark.toFixed(4)
  }
  return `¥${formatNumber(simulationResult.value.benchmark)}`
})

const minReviewPriceDisplay = computed(() => {
  if (pricingParams.value.pricingMethod === 'linear') {
    return `¥${formatNumber(simulationResult.value.minReviewPrice)}`
  }
  return '-'
})

const simulatorRuleNote = computed(() => {
  if (pricingParams.value.pricingMethod === 'vertexRandomK') {
    return '折扣报价：评审价 D1 = 1 - 折扣率；按顶点中间值法计算价格得分。'
  }
  if (pricingParams.value.pricingMethod === 'vertexFixedK') {
    return '评审价为报价金额，顶点中间值法固定 K=90%。'
  }
  return `线性评分法：F=100-(D1-D2)/(D*λ)，λ默认2%，当前${pricingParams.value.sensitivity.toFixed(1)}%，不设置有效应答人数量参数。`
})

const currentRuleDescription = computed(() => {
  if (pricingParams.value.pricingMethod === 'vertexRandomK') {
    return '规则1：折扣报价 + 顶点中间值法（K随机90%-100%，步长1%）。'
  }
  if (pricingParams.value.pricingMethod === 'vertexFixedK') {
    return '规则2：顶点中间值法（K固定90%）。'
  }
  return `规则3：线性评分法（λ默认2%，当前${pricingParams.value.sensitivity.toFixed(1)}%），价格得分与有效应答人数量参数无关。`
})

const calculatePriceScore = () => ourSimulationRow.value?.priceScore || 0

const scores = computed(() => {
  let budgetRatio = 0
  if (safeBudget.value > 0) {
    budgetRatio = totalPrice.value / safeBudget.value
  }
  let priceCompetitiveness = 70
  if (budgetRatio < 0.9) priceCompetitiveness = 90
  else if (budgetRatio < 0.95) priceCompetitiveness = 80
  else if (budgetRatio < 1) priceCompetitiveness = 70
  else priceCompetitiveness = 50

  let profitReasonability = 75
  if (pricingParams.value.profitMargin >= 15 && pricingParams.value.profitMargin <= 22) {
    profitReasonability = 90
  } else if (pricingParams.value.profitMargin < 10 || pricingParams.value.profitMargin > 25) {
    profitReasonability = 60
  }

  let riskControllability = 80
  if (pricingParams.value.riskFactor <= 2) riskControllability = 90
  else if (pricingParams.value.riskFactor >= 4) riskControllability = 65

  return {
    priceCompetitiveness: Math.round(priceCompetitiveness * 100) / 100,
    profitReasonability: Math.round(profitReasonability * 100) / 100,
    riskControllability: Math.round(riskControllability * 100) / 100
  }
})

const score = computed(() => {
  if (pricingParams.value.techScore < 60) return 0
  const total = pricingParams.value.techScore * 0.5 + calculatePriceScore() * 0.5
  return Math.round(total * 100) / 100
})

const aiAdvice = computed(() => {
  if (pricingParams.value.techScore < 60) {
    return '技术分低于60分，不得参与报价分评审。请先提高技术方案质量。'
  }
  const priceScore = calculatePriceScore()
  if (ourRank.value === 1 && priceScore >= 90) {
    return '当前报价在模拟对手中排名靠前且价格得分高，建议保持并关注利润空间。'
  }
  if (ourRank.value !== '-' && ourRank.value <= 3) {
    return '当前报价具备竞争力，可微调折扣率并复算，观察排名变化后再定稿。'
  }
  return '当前模拟排名偏后，建议适当提高折扣率或优化成本结构后再次测算。'
})

const formatNumber = (value) => {
  const n = Number(value || 0)
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatPercent = (value) => `${Number(value || 0).toFixed(2)}%`

const generateOffer = async () => {
  await callPricingApi()
  alert('报价方案已生成，可导出或进一步编辑')
}

const resetStrategy = () => {
  pricingParams.value = {
    budget: 0,
    profitMargin: 15,
    riskFactor: 3,
    techScore: 75,
    pricingMethod: 'linear',
    kValue: 95,
    sensitivity: 2
  }
  exTaxPrice.value = 0
  incTaxPrice.value = 0
  taxRate.value = 0.06
  competitorCompanies.value = [
    { id: 1, name: '竞品A', discountRate: 10 }
  ]
  nextCompetitorId.value = 2
}

onMounted(async () => {
  try {
    const projList = await listProjects()
    projects.value = projList.map((p: Project) => ({ id: p.id, name: p.name }))
    if (projList.length > 0) {
      selectedProject.value = projList[0].name
      const amount = parseFloat(projList[0].amount.replace(/[^\d.]/g, ''))
      if (!isNaN(amount)) {
        pricingParams.value.budget = amount
      }
    }
  } catch (e) {
    console.error('加载项目失败', e)
  }
})
</script>

<style scoped>
</style>

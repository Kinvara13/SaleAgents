<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
    <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
      <span class="mr-2">🧠</span>
      AI 技术分评估
    </h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">客观分（手动输入）</label>
          <div class="flex items-center space-x-2">
            <input
              v-model.number="objectiveScore"
              type="number"
              min="0"
              max="100"
              class="w-24 px-2 py-1.5 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <span class="text-sm text-gray-500">/ 100</span>
          </div>
          <p class="text-xs text-gray-400 mt-1">资质匹配、业绩案例、参数响应等可量化评分项</p>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">主观评分项配置</label>
          <div v-for="(item, idx) in subjectiveItems" :key="idx" class="mb-3 p-3 bg-gray-50 rounded">
            <div class="flex items-center justify-between mb-1">
              <input
                v-model="item.name"
                class="flex-1 px-2 py-1 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="评分项名称"
              />
              <button class="ml-2 text-xs text-danger hover:text-red-600" @click="removeSubjectiveItem(idx)">删除</button>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-500">满分</span>
              <input
                v-model.number="item.max_score"
                type="number"
                min="1"
                max="100"
                class="w-16 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
          </div>
          <button class="text-xs text-primary hover:underline" @click="addSubjectiveItem">+ 添加主观评分项</button>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">方案内容（用于AI评估主观分）</label>
          <textarea
            v-model="proposalText"
            rows="4"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary resize-y"
            placeholder="粘贴运营方案、命题方案等内容，AI将据此评估主观分档位..."
          ></textarea>
        </div>

        <div class="border-t border-gray-100 pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">企业资质（每行一项）</label>
          <textarea
            v-model="qualificationsText"
            rows="3"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary resize-y"
            placeholder="ISO9001认证&#10;CMMI5认证&#10;..."
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">历史案例（每行一项）</label>
          <textarea
            v-model="casesText"
            rows="3"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary resize-y"
            placeholder="XX省智慧城市项目&#10;XX市政务云平台..."
          ></textarea>
        </div>

        <button
          class="w-full px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 transition-all duration-300 text-sm"
          :disabled="evaluating"
          @click="runEvaluation"
        >
          {{ evaluating ? 'AI评估中...' : '🧠 AI评估技术分' }}
        </button>
      </div>

      <div v-if="evalResult" class="space-y-4">
        <div class="p-4 bg-gray-50 rounded">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-medium text-gray-700">综合技术分</span>
            <div class="flex items-end">
              <span class="text-2xl font-bold text-primary">{{ evalResult.total_tech_score }}</span>
              <span class="text-sm text-gray-400 ml-1">分</span>
            </div>
          </div>
          <div class="text-xs text-gray-500">
            置信区间: [{{ evalResult.confidence_range[0] }}, {{ evalResult.confidence_range[1] }}]
          </div>
          <div v-if="evalResult.needs_manual_review" class="mt-2 text-xs text-warning flex items-center">
            <span class="mr-1">⚠️</span> 建议人工确认
          </div>
        </div>

        <div class="p-4 bg-gray-50 rounded">
          <p class="text-sm font-medium text-gray-700 mb-2">客观分: {{ evalResult.objective_score.total }}</p>
          <div v-for="item in evalResult.objective_score.items" :key="item.name" class="mb-2 p-2 bg-white rounded border border-gray-100">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-800">{{ item.name }}</span>
              <div class="flex items-center space-x-2">
                <span v-if="item.ai_verified" class="text-xs px-1.5 py-0.5 rounded bg-success/20 text-success">AI已校验</span>
                <span class="text-sm font-semibold text-primary">{{ item.score }}</span>
                <span class="text-xs text-gray-400">/ {{ item.max_score }}</span>
              </div>
            </div>
            <p class="text-xs text-gray-500">{{ item.detail }}</p>
            <p v-if="item.ai_verification_detail" class="text-xs text-primary/70 mt-1">{{ item.ai_verification_detail }}</p>
            <div v-if="item.missing_items && item.missing_items.length" class="mt-1">
              <span class="text-xs text-warning">缺失项:</span>
              <span v-for="mi in item.missing_items" :key="mi" class="inline-block text-xs px-1.5 py-0.5 ml-1 rounded bg-warning/10 text-warning">{{ mi }}</span>
            </div>
          </div>
        </div>

        <div class="p-4 bg-gray-50 rounded">
          <p class="text-sm font-medium text-gray-700 mb-2">主观分: {{ evalResult.subjective_score.total }}</p>
          <div v-for="item in evalResult.subjective_score.items" :key="item.name" class="mb-3 p-2 bg-white rounded border border-gray-100">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-800">{{ item.name }}</span>
              <div class="flex items-center space-x-2">
                <span class="text-xs px-1.5 py-0.5 rounded" :class="tierClass(item.ai_tier)">
                  第{{ item.ai_tier }}档
                </span>
                <span class="text-sm font-semibold text-primary">{{ item.ai_score }}</span>
                <span class="text-xs text-gray-400">/ {{ item.max_score }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-2 text-xs text-gray-500 mb-1">
              <span>置信度: {{ (item.confidence * 100).toFixed(0) }}%</span>
              <div class="flex-1 h-1 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full rounded-full" :class="item.confidence >= 0.7 ? 'bg-success' : 'bg-warning'" :style="{ width: (item.confidence * 100) + '%' }"></div>
              </div>
            </div>
            <p class="text-xs text-gray-600">{{ item.reasoning }}</p>
            <div v-if="item.references.length" class="mt-1 text-xs text-gray-400">
              依据: {{ item.references.join('; ') }}
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between p-3 border border-primary/20 bg-primary/5 rounded">
          <span class="text-sm text-gray-700">应用到报价策略</span>
          <button class="px-3 py-1.5 text-xs bg-primary text-white rounded hover:bg-primary/90" @click="applyTechScore">
            应用技术分
          </button>
        </div>
      </div>

      <div v-else class="flex items-center justify-center text-gray-400 text-sm">
        配置评分标准后点击"AI评估技术分"
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { evaluateTechScore } from '../../services/techScore'
import type { TechScoreEvaluateResponse, SubjectiveItem } from '../../services/techScore'

const emit = defineEmits<{
  (e: 'apply-tech-score', score: number): void
}>()

const objectiveScore = ref(70)
const subjectiveItems = ref<Array<SubjectiveItem & { _key?: number }>>([
  { name: '运营方案', max_score: 20, tiers: [
    { tier: 1, min_score: 15, max_score: 20, description: '方案完整、创新、可行' },
    { tier: 2, min_score: 10, max_score: 15, description: '方案较完整' },
    { tier: 3, min_score: 5, max_score: 10, description: '方案基本覆盖' },
    { tier: 4, min_score: 0, max_score: 5, description: '方案不完整' },
  ]},
  { name: '命题方案', max_score: 10, tiers: [
    { tier: 1, min_score: 7, max_score: 10, description: '创新性强' },
    { tier: 2, min_score: 4, max_score: 7, description: '有一定创新' },
    { tier: 3, min_score: 0, max_score: 4, description: '缺乏创新' },
    { tier: 4, min_score: 0, max_score: 0, description: '不得分' },
  ]},
])

const proposalText = ref('')
const qualificationsText = ref('')
const casesText = ref('')
const evaluating = ref(false)
const evalResult = ref<TechScoreEvaluateResponse | null>(null)

const addSubjectiveItem = () => {
  subjectiveItems.value.push({
    name: '',
    max_score: 10,
    tiers: [
      { tier: 1, min_score: 7, max_score: 10, description: '' },
      { tier: 2, min_score: 4, max_score: 7, description: '' },
      { tier: 3, min_score: 0, max_score: 4, description: '' },
      { tier: 4, min_score: 0, max_score: 0, description: '' },
    ],
  })
}

const removeSubjectiveItem = (idx: number) => {
  subjectiveItems.value.splice(idx, 1)
}

const tierClass = (tier: number) => {
  const map: Record<number, string> = {
    1: 'bg-success/20 text-success',
    2: 'bg-primary/20 text-primary',
    3: 'bg-warning/20 text-warning',
    4: 'bg-danger/20 text-danger',
  }
  return map[tier] || 'bg-gray-200 text-gray-600'
}

const runEvaluation = async () => {
  evaluating.value = true
  try {
    const payload = {
      scoring_criteria: {
        objective_items: [{ name: '客观分', max_score: 100, weight: 1.0 }],
        subjective_items: subjectiveItems.value.filter(i => i.name),
      },
      company_materials: {
        qualifications: qualificationsText.value.split('\n').filter(s => s.trim()),
        cases: casesText.value.split('\n').filter(s => s.trim()),
        proposal_text: proposalText.value,
        technical_params: [],
      },
      manual_objective_score: objectiveScore.value,
      tech_weight: 0.5,
    }
    evalResult.value = await evaluateTechScore(payload)
  } catch (e: any) {
    alert(e.message || '技术分评估失败')
  } finally {
    evaluating.value = false
  }
}

const applyTechScore = () => {
  if (evalResult.value) {
    emit('apply-tech-score', evalResult.value.total_tech_score)
  }
}
</script>

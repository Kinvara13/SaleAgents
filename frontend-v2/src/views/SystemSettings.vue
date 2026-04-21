<template>
  <div class="fade-in flex flex-col h-full">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <h2 class="text-xl font-bold text-gray-800">系统设置</h2>
    </div>

    <!-- Tab -->
    <div class="flex space-x-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit flex-shrink-0">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-1.5 text-sm rounded-md transition-all"
        :class="activeTab === tab.key ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- AI 配置 -->
    <div v-if="activeTab === 'ai'" class="flex-1 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-w-2xl">
        <h3 class="font-semibold text-gray-800 mb-4">AI 模型配置</h3>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">供应商</label>
              <select v-model="aiForm.provider" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
                <option value="zhipu">智谱 AI</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="ollama">Ollama (本地)</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">模型名称</label>
              <input v-model="aiForm.model" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="glm-4" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">API Base URL</label>
            <input v-model="aiForm.base_url" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="https://open.bigmodel.cn/api/paas/v4" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input v-model="aiForm.api_key" type="password" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="输入 API Key" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
              <input v-model.number="aiForm.temperature" type="number" step="0.1" min="0" max="2" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
              <input v-model.number="aiForm.max_tokens" type="number" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
            </div>
          </div>
          <button
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm font-medium"
            :disabled="savingAI"
            @click="saveAIConfig"
          >
            {{ savingAI ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 素材库 -->
    <div v-else-if="activeTab === 'materials'" class="flex-1 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="flex items-center justify-between p-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">素材库</h3>
          <label class="px-3 py-1.5 bg-primary text-white text-xs rounded-lg hover:bg-primary/90 cursor-pointer">
            上传素材
            <input type="file" class="hidden" @change="handleMaterialUpload" />
          </label>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="mat in materials" :key="mat.id" class="flex items-center justify-between px-4 py-3 hover:bg-gray-50/50 transition-all">
            <div class="flex items-center space-x-3">
              <span class="text-xl">📄</span>
              <div>
                <p class="text-sm font-medium text-gray-800">{{ mat.name }}</p>
                <p class="text-xs text-gray-400">{{ mat.material_type }} · {{ mat.description || '无描述' }}</p>
              </div>
            </div>
            <button class="text-danger hover:text-danger/80 text-xs" @click="deleteMaterial(mat.id)">删除</button>
          </div>
          <div v-if="materials.length === 0" class="py-8 text-center text-gray-400 text-sm">暂无素材</div>
        </div>
      </div>
    </div>

    <!-- 规则中心 -->
    <div v-else-if="activeTab === 'rules'" class="flex-1 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="flex items-center justify-between p-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">规则中心</h3>
          <button class="px-3 py-1.5 bg-primary text-white text-xs rounded-lg hover:bg-primary/90" @click="showRuleModal = true">
            + 新建规则
          </button>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="rule in rules" :key="rule.id" class="px-4 py-3 hover:bg-gray-50/50 transition-all">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <span class="px-2 py-0.5 bg-blue-50 text-blue-600 text-xs rounded">{{ rule.rule_type }}</span>
                <span class="text-sm font-medium text-gray-800">{{ rule.name }}</span>
              </div>
              <button class="text-danger hover:text-danger/80 text-xs" @click="deleteRule(rule.id)">删除</button>
            </div>
            <p class="text-xs text-gray-400 mt-1 ml-14 line-clamp-2">{{ rule.content || '(无内容)' }}</p>
          </div>
          <div v-if="rules.length === 0" class="py-8 text-center text-gray-400 text-sm">暂无规则</div>
        </div>
      </div>
    </div>

    <!-- 新建规则弹窗 -->
    <div v-if="showRuleModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showRuleModal = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">新建规则</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">规则名称</label>
            <input v-model="ruleForm.name" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder="规则名称" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">类型</label>
            <select v-model="ruleForm.rule_type" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option value="general">通用</option>
              <option value="tender">投标规则</option>
              <option value="compliance">合规规则</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">规则内容</label>
            <textarea v-model="ruleForm.content" rows="4" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" placeholder="规则内容..."></textarea>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="showRuleModal = false">取消</button>
          <button class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90" @click="handleCreateRule">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import api from '@/services/api'
import { ref, onMounted } from 'vue'

const tabs = [
  { key: 'ai', label: 'AI 模型配置' },
  { key: 'materials', label: '素材库管理' },
  { key: 'rules', label: '规则中心' },
]
const activeTab = ref('ai')
const aiForm = ref({ provider: 'zhipu', api_key: '', base_url: '', model: 'glm-4', temperature: 0.7, max_tokens: 4096 })
const materials = ref<any[]>([])
const rules = ref<any[]>([])
const savingAI = ref(false)
const showRuleModal = ref(false)
const ruleForm = ref({ name: '', rule_type: 'general', content: '' })


async function loadAIConfig() {
  try {
    const res = await api.get('/settings/ai-config')
    const cfg = res.data
    aiForm.value = { ...aiForm.value, ...cfg }
  } catch (e) { console.error(e) }
}

async function saveAIConfig() {
  savingAI.value = true
  try {
    await api.patch('/settings/ai-config', aiForm.value)
  } catch (e) { console.error(e) }
  finally { savingAI.value = false }
}

async function loadMaterials() {
  try {
    const res = await api.get('/settings/materials')
    materials.value = res.data
  } catch (e) { console.error(e) }
}

async function handleMaterialUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', file.name)
  formData.append('material_type', 'general')
  try {
    await api.post('/settings/materials/upload', formData)
    await loadMaterials()
  } catch (e) { console.error(e) }
  finally { input.value = '' }
}

async function deleteMaterial(id: string) {
  await api.delete(`/settings/materials/${id}`).catch(() => {})
  await loadMaterials()
}

async function loadRules() {
  try {
    const res = await api.get('/settings/rules')
    rules.value = res.data
  } catch (e) { console.error(e) }
}

async function handleCreateRule() {
  try {
    await api.post('/settings/rules', ruleForm.value)
    showRuleModal.value = false
    ruleForm.value = { name: '', rule_type: 'general', content: '' }
    await loadRules()
  } catch (e) { console.error(e) }
}

async function deleteRule(id: string) {
  await api.delete(`/settings/rules/${id}`).catch(() => {})
  await loadRules()
}

onMounted(async () => {
  await loadAIConfig()
  await loadMaterials()
  await loadRules()
})
</script>

<style scoped>
.fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

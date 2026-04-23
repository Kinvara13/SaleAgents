<template>
  <div class="fade-in flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <h2 class="text-xl font-bold text-gray-800">投标项目清单</h2>
      <button
        class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-sm font-medium"
        @click="showCreateModal = true"
      >
        + 新建项目
      </button>
    </div>

    <!-- 状态筛选 -->
    <div class="flex space-x-2 mb-4 flex-shrink-0">
      <button
        v-for="tab in statusTabs"
        :key="tab.value"
        class="px-4 py-1.5 text-sm rounded-lg transition-all duration-300"
        :class="activeStatus === tab.value
          ? 'bg-primary text-white shadow-sm'
          : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'"
        @click="activeStatus = tab.value; fetchProjects()"
      >
        {{ tab.label }}
        <span
          v-if="tab.count !== undefined"
          class="ml-1 px-1.5 py-0.5 text-xs rounded-full"
          :class="activeStatus === tab.value ? 'bg-white/20' : 'bg-gray-100'"
        >
          {{ tab.count }}
        </span>
      </button>
    </div>

    <!-- 列表 -->
    <div class="flex-1 overflow-auto">
      <div v-if="loading" class="flex items-center justify-center h-40">
        <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
      </div>

      <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center h-40 text-gray-400">
        <div class="text-4xl mb-2">📋</div>
        <p>暂无项目，点击上方按钮创建</p>
      </div>

      <table v-else class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr class="text-left text-gray-500 text-xs uppercase tracking-wider">
            <th class="pb-3 pl-4 font-medium">项目名称</th>
            <th class="pb-3 font-medium">客户</th>
            <th class="pb-3 font-medium">截止时间</th>
            <th class="pb-3 font-medium">金额</th>
            <th class="pb-3 font-medium">解析状态</th>
            <th class="pb-3 font-medium">节点进度</th>
            <th class="pb-3 font-medium">状态</th>
            <th class="pb-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="project in projects"
            :key="project.id"
            class="hover:bg-gray-50/50 transition-all duration-200"
          >
            <td class="py-3 pl-4 font-medium text-gray-800">{{ project.name }}</td>
            <td class="py-3 text-gray-600">{{ project.client || '-' }}</td>
            <td class="py-3 text-gray-600">{{ project.deadline || '-' }}</td>
            <td class="py-3 text-gray-600">{{ project.amount || '-' }}</td>
            <td class="py-3">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="parseStatusClass(project.parse_status)"
              >
                {{ project.parse_status || '未上传' }}
              </span>
            </td>
            <td class="py-3">
              <div class="flex items-center space-x-1">
                <span
                  v-for="(val, key) in project.node_status || {}"
                  :key="key"
                  class="px-1.5 py-0.5 text-xs rounded"
                  :class="nodeStatusClass(val)"
                  :title="key"
                >
                  {{ nodeStatusLabel(key) }}
                </span>
              </div>
            </td>
            <td class="py-3">
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="statusClass(project.status)"
              >
                {{ project.status }}
              </span>
            </td>
            <td class="py-3">
              <div class="flex items-center space-x-3">
                <button
                  class="text-primary hover:text-primary/80 text-xs font-medium transition-colors"
                  @click="goToTenderDetail(project)"
                >
                  标书详情
                </button>
                <button
                  class="text-gray-400 hover:text-gray-600 text-xs transition-colors"
                  @click="goToProposalEditor(project)"
                >
                  建议书
                </button>
                <button
                  class="text-gray-400 hover:text-gray-600 text-xs transition-colors"
                  @click="openUpdateModal(project)"
                >
                  编辑
                </button>
                <button
                  class="text-danger hover:text-danger/80 text-xs transition-colors"
                  @click="confirmDelete(project)"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新建项目弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">新建项目</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">项目名称 <span class="text-danger">*</span></label>
            <input
              v-model="createForm.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
              placeholder="请输入项目名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">客户</label>
            <input
              v-model="createForm.client"
              type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
              placeholder="请输入客户名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">截止时间</label>
            <input
              v-model="createForm.deadline"
              type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
              placeholder="如：2026-06-01"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">预算金额</label>
            <input
              v-model="createForm.amount"
              type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
              placeholder="如：500万"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">风险等级</label>
            <select
              v-model="createForm.risk"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
            >
              <option value="P1">P1 - 高风险</option>
              <option value="P2">P2 - 中风险</option>
              <option value="P3">P3 - 低风险</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
            @click="showCreateModal = false"
          >
            取消
          </button>
          <button
            class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-all"
            :disabled="!createForm.name || creating"
            @click="handleCreate"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑状态弹窗 -->
    <div v-if="isUpdateModalVisible" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="isUpdateModalVisible = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">更新项目状态</h3>
        <div class="space-y-4">
          <p class="text-sm text-gray-600">项目：<span class="font-medium text-gray-800">{{ updateForm.name }}</span></p>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
            <select
              v-model="updateForm.status"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm"
            >
              <option value="待决策">待决策</option>
              <option value="已投标">已投标</option>
              <option value="未中标">未中标</option>
              <option value="已中标">已中标</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
            @click="isUpdateModalVisible = false"
          >
            取消
          </button>
          <button
            class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-all"
            :disabled="updating"
            @click="handleUpdate"
          >
            {{ updating ? '更新中...' : '更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-sm p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-2">确认删除</h3>
        <p class="text-sm text-gray-600 mb-6">
          确定要删除项目「<span class="font-medium text-gray-800">{{ deleteTarget?.name }}</span>」吗？此操作不可恢复。
        </p>
        <div class="flex justify-end space-x-3">
          <button
            class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
            @click="showDeleteConfirm = false"
          >
            取消
          </button>
          <button
            class="px-4 py-2 text-sm bg-danger text-white rounded-lg hover:bg-danger/90 transition-all"
            :disabled="deleting"
            @click="handleDelete"
          >
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listProjects, createProject, updateProject, deleteProject } from '../services/project'
import type { Project } from '../types'

const router = useRouter()

const projects = ref<Project[]>([])
const loading = ref(false)
const activeStatus = ref('全部')

const statusTabs = computed(() => {
  const counts: Record<string, number> = {}
  for (const p of projects.value) {
    counts[p.status] = (counts[p.status] || 0) + 1
  }
  return [
    { label: '全部', value: '全部', count: projects.value.length },
    { label: '待决策', value: '待决策', count: counts['待决策'] || 0 },
    { label: '已投标', value: '已投标', count: counts['已投标'] || 0 },
    { label: '未中标', value: '未中标', count: counts['未中标'] || 0 },
    { label: '已中标', value: '已中标', count: counts['已中标'] || 0 },
  ]
})

// Create modal
const showCreateModal = ref(false)
const creating = ref(false)
const createForm = ref({ name: '', client: '', deadline: '', amount: '', risk: 'P2' })

// Update modal
const isUpdateModalVisible = ref(false)
const updating = ref(false)
const updateForm = ref({ id: '', name: '', status: '待决策' })

// Delete confirm
const showDeleteConfirm = ref(false)
const deleteTarget = ref<Project | null>(null)
const deleting = ref(false)

function statusClass(status: string) {
  switch (status) {
    case '待决策': return 'bg-gray-100 text-gray-600'
    case '已投标': return 'bg-blue-100 text-blue-600'
    case '未中标': return 'bg-red-100 text-red-600'
    case '已中标': return 'bg-green-100 text-green-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

function parseStatusClass(parseStatus: string | undefined) {
  switch (parseStatus) {
    case '已解析': return 'bg-green-100 text-green-600'
    case '解析中': return 'bg-yellow-100 text-yellow-600'
    case '解析失败': return 'bg-red-100 text-red-600'
    default: return 'bg-gray-100 text-gray-400'
  }
}

function nodeStatusClass(val: string) {
  switch (val) {
    case 'done': return 'bg-green-100 text-green-600'
    case 'in_progress': return 'bg-blue-100 text-blue-600'
    case 'pending': return 'bg-gray-100 text-gray-400'
    default: return 'bg-gray-100 text-gray-400'
  }
}

function nodeStatusLabel(key: string) {
  const map: Record<string, string> = {
    decision: '决策',
    parsing: '解析',
    generation: '生成',
    review: '审查',
  }
  return map[key] || key
}

async function fetchProjects() {
  loading.value = true
  try {
    const status = activeStatus.value === '全部' ? undefined : activeStatus.value
    projects.value = await listProjects(status as any)
  } catch (e) {
    console.error('Failed to fetch projects:', e)
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!createForm.value.name) return
  creating.value = true
  try {
    await createProject({
      name: createForm.value.name,
      client: createForm.value.client,
      deadline: createForm.value.deadline,
      amount: createForm.value.amount,
      risk: createForm.value.risk,
    } as any)
    createForm.value = { name: '', client: '', deadline: '', amount: '', risk: 'P2' }
    showCreateModal.value = false
    await fetchProjects()
  } catch (e) {
    console.error('Failed to create project:', e)
  } finally {
    creating.value = false
  }
}

function openUpdateModal(project: Project) {
  updateForm.value = { id: project.id, name: project.name, status: project.status }
  isUpdateModalVisible.value = true
}

async function handleUpdate() {
  updating.value = true
  try {
    await updateProject(updateForm.value.id, { status: updateForm.value.status } as any)
    isUpdateModalVisible.value = false
    await fetchProjects()
  } catch (e) {
    console.error('Failed to update project:', e)
  } finally {
    updating.value = false
  }
}

function confirmDelete(project: Project) {
  deleteTarget.value = project
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await deleteProject(deleteTarget.value.id)
    showDeleteConfirm.value = false
    deleteTarget.value = null
    await fetchProjects()
  } catch (e) {
    console.error('Failed to delete project:', e)
  } finally {
    deleting.value = false
  }
}

function goToTenderDetail(project: Project) {
  router.push({ name: 'TenderDetailProject', params: { projectId: project.id } })
}

function goToProposalEditor(project: Project) {
  router.push({ name: 'ProposalEditor', params: { projectId: project.id } })
}

onMounted(fetchProjects)
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

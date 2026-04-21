<template>
  <div class="fade-in flex flex-col h-full">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <h2 class="text-xl font-bold text-gray-800">用户管理</h2>
      <button
        class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm font-medium"
        @click="showCreateModal = true"
      >
        + 新建用户
      </button>
    </div>

    <!-- 用户列表 -->
    <div class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-white border-b border-gray-100">
          <tr class="text-left text-gray-500 text-xs uppercase tracking-wider">
            <th class="pb-3 pl-4 font-medium">用户名</th>
            <th class="pb-3 font-medium">姓名</th>
            <th class="pb-3 font-medium">角色</th>
            <th class="pb-3 font-medium">状态</th>
            <th class="pb-3 font-medium">创建时间</th>
            <th class="pb-3 font-medium">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50/50 transition-all">
            <td class="py-3 pl-4 font-medium text-gray-800">{{ user.username }}</td>
            <td class="py-3 text-gray-600">{{ user.name || '-' }}</td>
            <td class="py-3">
              <span class="px-2 py-1 text-xs rounded-full" :class="roleClass(user.role)">
                {{ roleName(user.role) }}
              </span>
            </td>
            <td class="py-3">
              <span
                class="px-2 py-1 text-xs rounded-full"
                :class="user.is_active ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-400'"
              >
                {{ user.is_active ? '启用' : '禁用' }}
              </span>
            </td>
            <td class="py-3 text-gray-400 text-xs">{{ user.created_at || '-' }}</td>
            <td class="py-3">
              <div class="flex items-center space-x-3">
                <button class="text-primary hover:text-primary/80 text-xs font-medium" @click="openEditModal(user)">
                  编辑
                </button>
                <button
                  v-if="user.is_active"
                  class="text-warning hover:text-warning/80 text-xs"
                  @click="toggleActive(user)"
                >
                  禁用
                </button>
                <button
                  v-else
                  class="text-success hover:text-success/80 text-xs"
                  @click="toggleActive(user)"
                >
                  启用
                </button>
                <button
                  class="text-danger hover:text-danger/80 text-xs"
                  @click="confirmDelete(user)"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="py-8 text-center text-gray-400">暂无用户</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新建用户弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">新建用户</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名 <span class="text-danger">*</span></label>
            <input v-model="createForm.username" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" placeholder="登录用户名" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码 <span class="text-danger">*</span></label>
            <input v-model="createForm.password" type="password" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" placeholder="初始密码" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input v-model="createForm.name" type="text" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary" placeholder="显示名称" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色</label>
            <select v-model="createForm.role" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
              <option value="admin">管理员</option>
              <option value="project_owner">项目负责人</option>
              <option value="executor">执行人员</option>
              <option value="reviewer">审核人员</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="showCreateModal = false">取消</button>
          <button class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90" :disabled="creating" @click="handleCreate">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <div v-if="isEditModalVisible" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="isEditModalVisible = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">编辑用户</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色</label>
            <select v-model="editForm.role" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
              <option value="admin">管理员</option>
              <option value="project_owner">项目负责人</option>
              <option value="executor">执行人员</option>
              <option value="reviewer">审核人员</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="isEditModalVisible = false">取消</button>
          <button class="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90" :disabled="updating" @click="handleUpdate">
            {{ updating ? '更新中...' : '更新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-xl shadow-lg w-full max-w-sm p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-2">确认删除</h3>
        <p class="text-sm text-gray-600 mb-6">确定删除用户「<span class="font-medium">{{ deleteTarget?.username }}</span>」？</p>
        <div class="flex justify-end space-x-3">
          <button class="px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50" @click="showDeleteConfirm = false">取消</button>
          <button class="px-4 py-2 text-sm bg-danger text-white rounded-lg hover:bg-danger/90" :disabled="deleting" @click="handleDelete">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import api from '@/services/api'
import { ref, onMounted } from 'vue'

interface User {
  id: string
  username: string
  name: string
  role: string
  is_active: boolean
  created_at?: string
}

const users = ref<User[]>([])
const showCreateModal = ref(false)
const isEditModalVisible = ref(false)
const showDeleteConfirm = ref(false)
const creating = ref(false)
const updating = ref(false)
const deleting = ref(false)
const deleteTarget = ref<User | null>(null)
const editTarget = ref<User | null>(null)

const createForm = ref({ username: '', password: '', name: '', role: 'executor' })
const editForm = ref({ role: '' })

function roleName(role: string) {
  const map: Record<string, string> = {
    admin: '管理员', project_owner: '项目负责人', executor: '执行人员', reviewer: '审核人员'
  }
  return map[role] || role
}

function roleClass(role: string) {
  switch (role) {
    case 'admin': return 'bg-purple-100 text-purple-600'
    case 'project_owner': return 'bg-blue-100 text-blue-600'
    case 'executor': return 'bg-gray-100 text-gray-600'
    case 'reviewer': return 'bg-warning/10 text-warning'
    default: return 'bg-gray-100 text-gray-600'
  }
}

async function fetchUsers() {
  try {
    const res = await api.get('/users')
    if (res.ok) users.value = await res.json()
  } catch (e) { console.error('Fetch users failed:', e) }
}

async function handleCreate() {
  creating.value = true
  try {
    await api.post('/users', createForm.value)
    showCreateModal.value = false
    createForm.value = { username: '', password: '', name: '', role: 'executor' }
    await fetchUsers()
  } catch (e) { console.error('Create failed:', e) }
  finally { creating.value = false }
}

function openEditModal(user: User) {
  editTarget.value = user
  editForm.value = { role: user.role }
  isEditModalVisible.value = true
}

async function handleUpdate() {
  if (!editTarget.value) return
  updating.value = true
  try {
    await api.patch('/users/${editTarget.value.id}', { role: editForm.value.role })
    isEditModalVisible.value = false
    await fetchUsers()
  } catch (e) { console.error('Update failed:', e) }
  finally { updating.value = false }
}

function confirmDelete(user: User) {
  deleteTarget.value = user
  showDeleteConfirm.value = true
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete('/users/${deleteTarget.value.id}')
    showDeleteConfirm.value = false
    deleteTarget.value = null
    await fetchUsers()
  } catch (e) { console.error('Delete failed:', e) }
  finally { deleting.value = false }
}

async function toggleActive(user: User) {
  try {
    await api.patch('/users/${user.id}', { is_active: !user.is_active })
    await fetchUsers()
  } catch (e) { console.error('Toggle failed:', e) }
}

onMounted(fetchUsers)
</script>

<style scoped>
.fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>

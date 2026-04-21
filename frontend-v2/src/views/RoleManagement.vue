<template>
  <div class="fade-in flex flex-col h-full">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <h2 class="text-xl font-bold text-gray-800">角色管理</h2>
    </div>

    <!-- 角色卡片 -->
    <div class="flex-1 overflow-auto space-y-4">
      <div
        v-for="role in roles"
        :key="role.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-3">
            <span class="px-3 py-1 rounded-full text-sm font-bold" :class="roleClass(role.id)">
              {{ role.name }}
            </span>
            <span class="text-xs text-gray-400 font-mono">{{ role.id }}</span>
          </div>
          <span class="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded">
            {{ role.permissions.length }} 项权限
          </span>
        </div>

        <!-- 权限列表 -->
        <div class="flex flex-wrap gap-2 mt-3">
          <span
            v-for="perm in role.permissions"
            :key="perm"
            class="px-2 py-1 bg-gray-50 text-gray-600 text-xs rounded border border-gray-100 font-mono"
          >
            {{ perm }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import api from '@/services/api'
import { ref, onMounted } from 'vue'

const roles = ref<any[]>([])

function roleClass(id: string) {
  switch (id) {
    case 'admin': return 'bg-purple-100 text-purple-700'
    case 'project_owner': return 'bg-blue-100 text-blue-700'
    case 'executor': return 'bg-gray-100 text-gray-700'
    case 'reviewer': return 'bg-warning/10 text-warning'
    default: return 'bg-gray-100 text-gray-700'
  }
}

onMounted(async () => {
  try {
    const res = await fetch('/api/v1/users/roles/list')
    if (res.ok) roles.value = await res.json()
  } catch (e) { console.error('Load roles failed:', e) }
})
</script>

<style scoped>
.fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
</style>

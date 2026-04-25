<template>
  <div class="flex h-screen bg-background">
    <aside :class="['bg-sidebar flex-shrink-0 flex flex-col transition-all duration-300', isSidebarCollapsed ? 'w-20' : 'w-[200px]']">
      <div class="h-16 flex items-center justify-between border-b border-gray-700 px-4">
        <h1 :class="['text-white font-bold text-lg transition-all duration-300', isSidebarCollapsed ? 'hidden' : 'block']">AI标书助手</h1>
        <button 
          class="text-white hover:bg-white/10 p-2 rounded transition-all duration-300"
          @click="isSidebarCollapsed = !isSidebarCollapsed"
        >
          <span>{{ isSidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
      </div>
      <nav class="flex-1 py-4">
        <div v-for="item in menuItems" :key="item.path" class="group">
          <div v-if="!item.children" class="group">
            <router-link
              :to="item.path"
              class="flex items-center px-4 py-3 text-gray-300 hover:bg-primary/20 hover:text-white transition-all duration-300 block"
              :class="{ 'bg-primary/30 text-white': isActive(item.path) }"
            >
              <span v-if="isSidebarCollapsed" class="mr-3">{{ item.icon }}</span>
              <span v-else class="mr-3 opacity-0">{{ item.icon }}</span>
              <span :class="['transition-all duration-300', isSidebarCollapsed ? 'hidden' : 'block']">{{ item.name }}</span>
            </router-link>
          </div>
          <div v-else class="group">
            <div class="flex items-center justify-between px-4 py-3 hover:bg-primary/20 transition-all duration-300 cursor-pointer">
              <router-link
                :to="item.path"
                class="flex-1 flex items-center text-gray-300 hover:text-white transition-all duration-300"
                :class="{ 'text-white': isActive(item.path) }"
              >
                <span v-if="isSidebarCollapsed" class="mr-3">{{ item.icon }}</span>
                <span v-else class="mr-3 opacity-0">{{ item.icon }}</span>
                <span :class="['transition-all duration-300', isSidebarCollapsed ? 'hidden' : 'block']">{{ item.name }}</span>
              </router-link>
              <button
                class="text-gray-300 hover:text-white transition-all duration-300"
                @click.stop="toggleSubMenu(item)"
                :class="['transition-all duration-300', isSidebarCollapsed ? 'hidden' : 'block']"
              >
                <span class="text-xs">▼</span>
              </button>
            </div>
          </div>
          <div v-if="item.children && item.expanded && !isSidebarCollapsed" class="pl-10 py-2 space-y-1">
            <router-link
              v-for="child in item.children"
              :key="child.path"
              :to="child.path"
              class="flex items-center px-4 py-2 text-gray-300 hover:bg-primary/20 hover:text-white transition-all duration-300 text-sm block"
              :class="{ 'bg-primary/30 text-white': isActive(child.path) }"
            >
              <span v-if="isSidebarCollapsed" class="mr-2">{{ child.icon }}</span>
              <span v-else class="mr-2 opacity-0">{{ child.icon }}</span>
              <span>{{ child.name }}</span>
            </router-link>
          </div>
        </div>
      </nav>
    </aside>

    <div class="flex-1 flex flex-col">
      <main class="flex-1 overflow-auto p-6 bg-background">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isSidebarCollapsed = ref(false)

interface MenuItem {
  name: string
  path: string
  icon: string
  children?: MenuItem[]
  expanded?: boolean
}

const menuItems = ref<MenuItem[]>([
  { name: '首页', path: '/home', icon: '🏠' },
  { name: '标前评估', path: '/pre-evaluation', icon: '📊' },
  { name: '招标项目', path: '/tender-list', icon: '📋' },
  { name: '招标信息', path: '/tender-info-list', icon: '🔔' },
  { name: '回标文件', path: '/bid-list', icon: '📁' },
  { name: '技术建议书', path: '/bid-list', icon: '✍️' },
  { name: 'DEMO制作', path: '/demo-workflow', icon: '🎬' },
  { name: '报价策略', path: '/pricing-strategy', icon: '💰' },
  {
    name: '系统管理',
    path: '/system-settings',
    icon: '⚙️',
    expanded: false,
    children: [
      { name: '系统设置', path: '/system-settings', icon: '⚙️' },
      { name: '用户管理', path: '/user-management', icon: '👥' },
      { name: '角色管理', path: '/role-management', icon: '🔐' },
    ]
  }
])

const currentPageName = computed(() => {
  const currentPath = route.path
  for (const item of menuItems.value) {
    if (item.path === currentPath) {
      return item.name
    }
    if (item.children) {
      const child = item.children.find(c => c.path === currentPath)
      if (child) {
        return child.name
      }
    }
  }
  return ''
})

const breadcrumbItems = computed(() => {
  const currentPath = route.path
  const items = [{ name: '首页', path: '/' }]

  for (const item of menuItems.value) {
    if (item.path === currentPath) {
      items.push({ name: item.name, path: item.path })
      break
    }
    if (item.children) {
      const child = item.children.find(c => c.path === currentPath)
      if (child) {
        items.push({ name: item.name, path: item.path })
        items.push({ name: child.name, path: child.path })
        break
      }
    }
  }
  return items
})

const isActive = (path: string) => {
  return route.path === path
}

const toggleSubMenu = (item: MenuItem) => {
  if (item.children) {
    item.expanded = !item.expanded
  }
}
</script>

<style scoped>
</style>

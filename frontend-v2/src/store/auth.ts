import { reactive, readonly } from 'vue'
import { login as loginApi, getMe, logout as logoutApi, type UserInfo } from '../services/auth'

interface AuthState {
  user: UserInfo | null
  isLoggedIn: boolean
  loading: boolean
}

const state = reactive<AuthState>({
  user: null,
  isLoggedIn: false,
  loading: false,
})

export function useAuth() {
  return readonly(state)
}

export async function loadUser(): Promise<void> {
  const token = localStorage.getItem('sa_token')
  if (!token) {
    state.isLoggedIn = false
    state.user = null
    return
  }
  try {
    const user = await getMe()
    state.user = user
    state.isLoggedIn = true
  } catch (e) {
    state.user = null
    state.isLoggedIn = false
  }
}

export async function login(username: string, password: string): Promise<UserInfo> {
  state.loading = true
  try {
    await loginApi(username, password)
    const user = await getMe()
    state.user = user
    state.isLoggedIn = true
    return user
  } finally {
    state.loading = false
  }
}

export function logout(): void {
  logoutApi()
  state.user = null
  state.isLoggedIn = false
}

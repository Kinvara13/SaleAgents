import { reactive, readonly } from 'vue'
import { login as loginApi, getMe, logout as logoutApi, refreshToken as refreshTokenApi, type UserInfo } from '../services/auth'

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
    const refreshToken = localStorage.getItem('sa_refresh_token')
    if (refreshToken) {
      try {
        await refreshTokenApi(refreshToken)
        const user = await getMe()
        state.user = user
        state.isLoggedIn = true
        return
      } catch {
        // refresh 也失败，清除状态
      }
    }
    state.user = null
    state.isLoggedIn = false
    logoutApi()
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

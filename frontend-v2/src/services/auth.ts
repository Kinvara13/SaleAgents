import api from './api'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserInfo {
  id: string
  username: string
  name: string
  role: string
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>('/auth/login', { username, password })
  const { access_token, refresh_token } = res.data
  localStorage.setItem('sa_token', access_token)
  localStorage.setItem('sa_refresh_token', refresh_token)
  return res.data
}

export async function refreshToken(refresh_token: string): Promise<LoginResponse> {
  const res = await api.post<LoginResponse>('/auth/refresh', { refresh_token })
  const { access_token } = res.data
  localStorage.setItem('sa_token', access_token)
  if (res.data.refresh_token) {
    localStorage.setItem('sa_refresh_token', res.data.refresh_token)
  }
  return res.data
}

export async function getMe(): Promise<UserInfo> {
  const res = await api.get<UserInfo>('/auth/me')
  return res.data
}

export function logout(): void {
  localStorage.removeItem('sa_token')
  localStorage.removeItem('sa_refresh_token')
}

export function isLoggedIn(): boolean {
  return !!localStorage.getItem('sa_token')
}

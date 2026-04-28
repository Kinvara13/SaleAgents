import axios from 'axios'

const baseURL = (import.meta.env.VITE_API_BASE || '') + '/api/v1'

const api = axios.create({
  baseURL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// 请求拦截器：自动注入 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sa_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb)
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach(cb => cb(newToken))
  refreshSubscribers = []
}

// 响应拦截器：统一错误处理 + Token 刷新
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      // 避免循环刷新：如果 refresh 请求本身返回 401，直接跳转到登录页
      if (originalRequest.url === '/auth/refresh') {
        localStorage.removeItem('sa_token')
        localStorage.removeItem('sa_refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      isRefreshing = true
      ;(originalRequest as any)._retry = true
      const refreshToken = localStorage.getItem('sa_refresh_token')
      if (refreshToken) {
        try {
          const res = await axios.post(`${baseURL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          const { access_token, refresh_token: newRefresh } = res.data
          localStorage.setItem('sa_token', access_token)
          if (newRefresh) {
            localStorage.setItem('sa_refresh_token', newRefresh)
          }
          onTokenRefreshed(access_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem('sa_token')
          localStorage.removeItem('sa_refresh_token')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      } else {
        localStorage.removeItem('sa_token')
        localStorage.removeItem('sa_refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    // 统一错误提示
    const msg = error.response?.data?.detail || error.message || '请求失败'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  }
)

export default api

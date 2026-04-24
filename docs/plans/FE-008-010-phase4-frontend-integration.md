# FE-008~FE-010 阶段四前端对接开发计划

> **For Hermes:** 使用 subagent-driven-development skill 逐任务实现。

**目标:** 完成前端与后端接口的完整对接
- **FE-008**: TenderDetail.vue 打分反馈与重算交互
- **FE-009**: 登录鉴权 token 刷新（用户无感知）
- **FE-010**: 聊天页面级回归（流式消息、上下文保持、错误态）

**前端技术栈**: Vue 3 + TypeScript + Vite + Tailwind CSS + Axios
**前端服务层约定**: 使用相对路径 `../services/api`，不支持 `@/` 别名。

---

## 任务 1: FE-008 打分反馈与重算交互 (TenderDetail.vue)

**修改文件**: `frontend-v2/src/views/TenderDetail.vue`

### 当前状态
- 已有 `handleScoreBusinessDoc` 和 `handleScoreTechDoc` 方法
- 已有 `scoreResult` modal 显示分数
- 商务文档和技术文档的卡片上有"评分"按钮
- 但缺少："重新打分"功能、分数差异展示、保存后自动重算

### 需要实现
1. **卡片头部分数徽章**：在商务文档和技术文档卡片上显示当前得分（如有）
2. **保存后自动重算**：`saveDoc` 和 `saveTechDoc` 成功后，如果该文档之前已打分，自动调用 score 接口重新计算
3. **重算差异展示**：在 score modal 中显示上次得分和本次得分的差异
4. **手动重新打分按钮**：在文档详情展开区域添加"重新打分"按钮
5. **保持打分历史**：在 TenderDetail.vue 的 data 中维护一个 `scoreHistory` 映射 `docId -> {score, max_score, timestamp}`

### API 接口
- `GET /api/v1/projects/{pid}/business-documents/{docId}/score` → DocumentScoreResult
- `GET /api/v1/projects/{pid}/technical-documents/{docId}/score` → DocumentScoreResult

```typescript
interface DocumentScoreResult {
  score: number
  max_score: number
  is_scored: boolean
  breakdown: Record<string, unknown>
  message?: string
}
```

### 实现结构
- 添加 `scoreHistory: Map<string, { score: number; max_score: number; timestamp: number }>`
- 在 `saveDoc` 和 `saveTechDoc` 成功后，如果 `scoreHistory.has(doc.id)` 则自动调用 score 并更新
- 在 score modal 中显示 `scoreHistory` 中的上次记录
- 在文档卡片头部显示当前分数徽章（小型绿色/红色圆点 + 分数）

---

## 任务 2: FE-009 登录鉴权 Token 刷新

**修改文件**: `frontend-v2/src/services/api.ts`, `frontend-v2/src/store/auth.ts`

### 当前状态
- `api.ts` 已有 401 响应拦截器，会尝试刷新 token
- 但存在问题：
  1. 没有并发控制：多个请求同时 401 时，会发送多个 refresh 请求
  2. `store/auth.ts` 的 `loadUser` 在 getMe 失败时只是默默失败，没有触发 token 刷新
  3. 没有预测性刷新（在 token 即将过期前自动刷新）

### 需要实现
1. **并发控制**：在 `api.ts` 中添加 `isRefreshing` 标志和 `pendingQueue` 优化，确保同一时刻只有一个 refresh 请求
2. **loadUser 增强**：在 `store/auth.ts` 的 `loadUser` 中，getMe 失败时尝试先刷新 token，再重试
3. **无感知登录恢复**：在应用启动时（App.vue 或 main.ts）调用 `loadUser`，如果 token 有效则自动恢复登录状态

### 关键代码
```typescript
// api.ts 中添加
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb)
}

function onTokenRefreshed(newToken: string) {
  refreshSubscribers.forEach(cb => cb(newToken))
  refreshSubscribers = []
}
```

### 修改文件
- `frontend-v2/src/services/api.ts` - 添加并发控制和队列
- `frontend-v2/src/store/auth.ts` - 增强 loadUser 逻辑
- `frontend-v2/src/main.ts` - 启动时调用 loadUser

---

## 任务 3: FE-010 聊天页面级回归

**修改文件**: `frontend-v2/src/components/ChatDialog.vue`

### 当前状态
- 已有流式消息接收
- 已有历史记录加载
- 已有发送和清空功能

### 存在问题
1. **错误处理**：出错时只是移除了 user message，没有给出错误提示或重试按钮
2. **SSE 解析**：`adapter: 'fetch'` 和 `responseType: 'stream'` 在 axios 中可能不支持，需要检查
3. **上下文保持**：看起来正常，但需要确认页面刷新后能正确恢复历史

### 需要实现
1. **错误态处理**：
   - 发送失败时不删除 user message，而是添加一条 assistant 错误消息
   - 在错误消息旁显示"重试"按钮
2. **重试机制**：添加 `retryMessage` 方法，重发上一条用户消息
3. **SSE 稳定性修复**：确保流式解析正常工作
4. **空消息防护**：添加输入验证

### 实现结构
- 添加 `errorMessage: ChatMessage | null` 状态
- 修改 `sendMessage` 错误处理：不移除 user message，添加错误提示
- 添加 `retryLastMessage` 方法
- 添加错误消息的 UI 展示

---

## 完成标准

| 检查点 | 说明 |
|--------|------|
| ✅ FE-008 | 商务文档/技术文档保存后自动重新打分，显示分数变化差异 |
| ✅ FE-008 | 打分结果 modal 显示历史对比 |
| ✅ FE-009 | 多个请求同时 401 时只发送一次 refresh 请求 |
| ✅ FE-009 | 页面刷新后自动恢复登录状态（如 token 未过期） |
| ✅ FE-010 | 发送失败时显示错误提示 + 重试按钮 |
| ✅ FE-010 | 流式输出正常工作 |
| ✅ FE-010 | 历史记录加载正常 |
| ✅ Vite 构建 | `npm run build` 或 `npx vue-tsc --noEmit` 无错误 |
| ✅ Git 推送 | 所有提交推送到 GitHub |

# SaleAgents 前端开发与样式规范

## 1. 技术基线

- 框架：Vue 3
- 构建：Vite
- 样式：Tailwind CSS
- 路由：`vue-router`
- HTTP：axios，统一使用 `src/services/api.ts`

## 2. 页面开发规则

- 页面文件放在 `src/views/`
- 路由统一在 `src/router/index.ts`
- 页面级数据请求优先走 `src/services/*.ts`
- 复杂页面优先把 API 调用抽到 service，不直接散落在 view 中

## 3. axios 使用规范

`api.ts` 返回的是 axios response，不是 fetch `Response`。

正确写法：

```ts
const { data } = await api.get('/users')
users.value = data
```

禁止写法：

```ts
const res = await api.get('/users')
if (res.ok) {
  users.value = await res.json()
}
```

必须禁止：

- 读取 `res.ok`
- 调用 `res.json()`
- 把 axios 当 fetch 用

## 4. 动态路径规范

动态路径必须使用模板字符串：

```ts
await api.patch(`/users/${userId}`, payload)
```

禁止：

```ts
await api.patch('/users/${userId}', payload)
```

## 5. 页面状态规范

每个页面至少处理四种状态：

- `loading`
- `empty`
- `success`
- `error`

要求：

- 错误态对用户可见
- 正在保存/上传时要有禁用或进度反馈
- 删除、覆盖、重生成类操作要有二次确认

## 6. Tailwind 约束

沿用当前项目视觉语义：

- `primary`
- `success`
- `warning`
- `danger`
- `background`
- `sidebar`

要求：

- 复用已存在的颜色语义，不新增无来源的主题色
- 统一圆角、边框、阴影风格
- 不在同一页面混用多套按钮语义

## 7. 组件与复用

优先抽离以下重复模式：

- 列表加载态
- 空态
- 错误态
- 模态框表单
- 文件上传区
- 规则说明区

## 8. 当前已知前端高风险点

- `ProposalEditor.vue`：axios/fetch 混用
- `UserManagement.vue`：axios/fetch 混用 + 动态路径错误
- `RoleManagement.vue`：axios/fetch 混用
- `SystemSettings.vue`：需要与后端 AI 配置兼容口径对齐

这些问题修复前，不得把相关页面标记为“已完成”。

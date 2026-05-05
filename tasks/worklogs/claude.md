# Claude 工作日志

## 2026-05-05

### 认领任务
- BUG-001: 新增项目第二步生成回标文件按钮应跳转而非直接生成
- BUG-002: 第二步完成/保存按钮未实现功能
- BUG-003: 第三步结束后从卡片进入应查看项目整体情况

### 问题分析
1. **ProjectCreate.vue 步骤3** (`currentStep === 2`): `startGeneration()` 直接调用后端生成任务并下载 Word，用户期望改为跳转到 `/bid-list` 回标文件编辑页面。
2. **ProjectCreate.vue 顶部**: "保存项目"按钮无 `@click` 事件处理器。
3. **ProjectCreate.vue 步骤2**: 缺少"完成"按钮直接跳转 `/bid-list` 的功能。
4. **TenderList.vue**: `handleProjectClick` 中 `hasTemplate && !isGenerationDone` 条件会让已有模板但未生成的项目回到 `project-create`，用户期望直接到 `tender-detail`。

### 修复计划
- `ProjectCreate.vue`: 给"保存项目"按钮添加 `saveProject` 方法；步骤2添加"完成"按钮跳转 `/bid-list`；步骤3"开始生成回标文件"按钮改为跳转；步骤3"完成"按钮改为跳转并更新状态。
- `services/project.ts`: 扩展 `ProjectUpdateRequest` 接口支持更多字段。
- `TenderList.vue`: 简化卡片点击逻辑，有模板即去 `tender-detail`。

### 修复结果
- 前端构建通过（`npm run build` 无错误）。
- BUG-001: `startGeneration` 现在跳转 `/bid-list` 并更新 `node_status.generation = 'in_progress'`。
- BUG-002: 顶部"保存项目"可保存基础信息；步骤2"完成"按钮直接跳转 `/bid-list`。
- BUG-003: 卡片点击逻辑简化，有模板文件即跳转 `tender-detail`。

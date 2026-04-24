<template>
  <div class="fade-in flex flex-col h-full">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div>
        <h2 class="text-xl font-bold text-gray-800">{{ project?.name || '加载中...' }}</h2>
        <p class="text-sm text-gray-500 mt-0.5">标书拆分结果</p>
      </div>
      <button
        class="px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 text-sm transition-all"
        @click="router.push({ name: 'BidList' })"
      >
        ← 返回列表
      </button>
    </div>

    <!-- 项目信息摘要 -->
    <div v-if="project" class="flex-shrink-0 flex items-center space-x-6 mb-4 text-sm">
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">客户:</span> {{ project.client || '-' }}
      </div>
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">截止:</span> {{ project.deadline || '-' }}
      </div>
      <div class="flex items-center text-gray-600">
        <span class="text-gray-400 mr-1">金额:</span> {{ project.amount || '-' }}
      </div>
      <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="statusClass(project.status)">
        {{ project.status }}
      </span>
    </div>

    <!-- 上传区域（未解析时显示） -->
    <div v-if="!sections.length && !loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="text-5xl mb-4">📄</div>
        <p class="text-gray-600 mb-4">尚未上传招标文件</p>
        <label class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 cursor-pointer text-sm inline-block">
          选择招标文件上传
          <input type="file" accept=".pdf,.doc,.docx" class="hidden" @change="handleFileUpload" />
        </label>
      </div>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full"></div>
    </div>

    <!-- 已有章节时显示 -->
    <div v-else-if="sections.length > 0" class="flex-1 flex flex-col min-h-0">
      <!-- 商务/技术/文档 Tab -->
      <div class="flex items-center justify-between mb-3 flex-shrink-0">
        <div class="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '商务' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '商务'"
          >
            商务部分
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ businessSections.length }}
            </span>
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '技术' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '技术'"
          >
            技术部分
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ techSections.length }}
            </span>
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '商务文档' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '商务文档'"
          >
            商务文档
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ businessDocs.length }}
            </span>
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '技术文档' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '技术文档'"
          >
            技术文档
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ techDocs.length }}
            </span>
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '方案建议书' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '方案建议书'"
          >
            方案建议书
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ proposalPlans.length }}
            </span>
          </button>
          <button
            class="px-4 py-1.5 text-sm rounded-md transition-all"
            :class="activeTab === '技术案例' ? 'bg-white text-primary shadow-sm' : 'text-gray-500 hover:text-gray-700'"
            @click="activeTab = '技术案例'"
          >
            技术案例
            <span class="ml-1 px-1.5 py-0.5 text-xs bg-gray-200 rounded-full">
              {{ technicalCases.length }}
            </span>
          </button>
        </div>
        <label class="px-3 py-1.5 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 cursor-pointer text-xs transition-all">
          重新上传
          <input type="file" accept=".pdf,.doc,.docx" class="hidden" @change="handleFileUpload" />
        </label>
      </div>

      <!-- 章节列表（商务/技术） -->
      <div v-if="activeTab === '商务' || activeTab === '技术'" class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="p-4">
          <div
            v-for="section in filteredSections"
            :key="section.id"
            class="border border-gray-100 rounded-lg mb-2 overflow-hidden"
          >
            <div
              class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-all"
              :class="expandedSection === section.id ? 'bg-gray-50' : ''"
              @click="expandedSection = expandedSection === section.id ? null : section.id"
            >
              <div class="flex items-center space-x-3">
                <span class="text-gray-400 text-xs">
                  {{ expandedSection === section.id ? '▼' : '▶' }}
                </span>
                <span class="text-sm font-medium text-gray-800">
                  {{ section.section_name }}
                </span>
                <span
                  v-if="section.is_star_item"
                  class="px-1.5 py-0.5 bg-warning/10 text-warning text-xs rounded"
                >
                  ⭐ 星标项
                </span>
              </div>
              <span class="text-xs text-gray-400">{{ section.source_file }}</span>
            </div>

            <div v-if="expandedSection === section.id" class="border-t border-gray-100 p-4">
              <div v-if="editingSection === section.id" class="space-y-3">
                <textarea
                  v-model="editContent"
                  class="w-full min-h-[200px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  placeholder="请输入章节内容..."
                ></textarea>
                <div class="flex justify-end space-x-2">
                  <button
                    class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                    @click="cancelEdit"
                  >
                    取消
                  </button>
                  <button
                    class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all"
                    :disabled="saving"
                    @click="saveSection(section)"
                  >
                    {{ saving ? '保存中...' : '保存' }}
                  </button>
                </div>
              </div>
              <div v-else>
                <pre class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed font-sans mb-3">{{ section.content || '暂无内容' }}</pre>
                <div class="flex justify-end">
                  <button
                    class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                    @click="startEdit(section)"
                  >
                    编辑内容
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 商务文档列表 ========== -->
      <div v-else-if="activeTab === '商务文档'" class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="p-4">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-700">商务文档清单</h3>
              <p class="text-xs text-gray-400 mt-0.5">点击文档查看详情和可填写字段</p>
            </div>
            <div class="flex items-center space-x-2 text-xs">
              <span class="px-2 py-1 bg-green-50 text-green-600 rounded">星标项: {{ businessDocStarCount }}</span>
              <span class="px-2 py-1 bg-blue-50 text-blue-600 rounded">可编辑: {{ businessDocFillableCount }}</span>
            </div>
          </div>

          <!-- 文档列表 -->
          <div
            v-for="doc in businessDocs"
            :key="doc.id"
            class="border border-gray-100 rounded-lg mb-2 overflow-hidden"
          >
            <div
              class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-all"
              :class="expandedDocId === doc.id ? 'bg-gray-50' : ''"
              @click="toggleDoc(doc)"
            >
              <div class="flex items-center space-x-3">
                <span class="text-gray-400 text-xs">
                  {{ expandedDocId === doc.id ? '▼' : '▶' }}
                </span>
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-800">{{ doc.doc_name }}</span>
                  <span v-if="doc.is_star_item" class="px-1.5 py-0.5 bg-warning/10 text-warning text-xs rounded">⭐</span>
                  <span v-if="doc.has_fillable_fields" class="px-1.5 py-0.5 bg-green-50 text-green-600 text-xs rounded">可编辑</span>
                  <span
                    v-if="scoreHistory[doc.id]"
                    class="px-1.5 py-0.5 text-xs rounded font-medium"
                    :class="getScoreBadgeClass(scoreHistory[doc.id].score, scoreHistory[doc.id].max_score)"
                  >
                    {{ scoreHistory[doc.id].score }}/{{ scoreHistory[doc.id].max_score }} 分
                  </span>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-xs text-gray-400">{{ doc.score_point }}</span>
                <span
                  class="px-2 py-0.5 text-xs rounded-full"
                  :class="docStatusClass(doc.status)"
                >
                  {{ docStatusLabel(doc.status) }}
                </span>
                <button
                  class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                  :disabled="exportingDocId === doc.id"
                  @click.stop="openExportModal(doc, 'business')"
                >
                  {{ exportingDocId === doc.id ? '导出中...' : '导出' }}
                </button>
                <button
                  class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                  :disabled="scoringDocId === doc.id"
                  @click.stop="handleScoreBusinessDoc(doc)"
                >
                  {{ scoringDocId === doc.id ? '评分中...' : '评分' }}
                </button>
              </div>
            </div>

            <div v-if="expandedDocId === doc.id" class="border-t border-gray-100">
              <div v-if="loadingDocId === doc.id" class="p-8 text-center">
                <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
                <p class="text-xs text-gray-400 mt-2">加载中...</p>
              </div>

              <div v-else-if="currentDoc" class="p-4">
                <div v-if="currentDoc.rule_description" class="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div class="text-xs font-medium text-blue-600 mb-1">📋 规则说明</div>
                  <p class="text-xs text-gray-600">{{ currentDoc.rule_description }}</p>
                </div>

                <div v-if="currentDoc.return_file_list" class="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div class="text-xs font-medium text-gray-600 mb-1">📎 回标文件清单</div>
                  <div
                    v-for="(f, idx) in parseReturnFileList(currentDoc.return_file_list)"
                    :key="idx"
                    class="flex items-center space-x-2 text-xs text-gray-600 mt-1"
                  >
                    <span>•</span>
                    <span class="font-medium">{{ f.file_name }}</span>
                    <span class="text-gray-400">({{ f.file_type }})</span>
                    <span class="text-gray-400">- {{ f.description }}</span>
                  </div>
                </div>

                <div v-if="currentDoc.has_fillable_fields" class="mb-3 p-2 bg-green-50 rounded text-xs text-green-700">
                  💡 此文档包含可填写字段，请在下方编辑内容
                </div>

                <div class="space-y-3">
                  <div>
                    <div class="text-xs font-medium text-gray-500 mb-1">原始模板内容</div>
                    <pre class="text-xs text-gray-500 bg-gray-50 rounded p-3 whitespace-pre-wrap leading-relaxed max-h-48 overflow-auto border border-gray-100">{{ currentDoc.original_content }}</pre>
                  </div>

                  <div v-if="currentDoc.has_fillable_fields || editingDocId === doc.id">
                    <div class="flex items-center justify-between mb-1">
                      <div class="text-xs font-medium text-gray-500">✏️ 可编辑内容</div>
                      <div class="flex items-center space-x-3">
                        <button
                          v-if="editingDocId !== doc.id && currentDoc.has_fillable_fields"
                          class="text-xs text-primary hover:underline flex items-center"
                          @click="generateDoc(doc)"
                          :disabled="generatingDocId === doc.id"
                        >
                          <span v-if="generatingDocId === doc.id" class="mr-1 animate-spin inline-block w-3 h-3 border border-current border-t-transparent rounded-full"></span>
                          ✨ AI 自动填充
                        </button>
                        <button
                          v-if="editingDocId !== doc.id"
                          class="text-xs text-primary hover:underline"
                          @click="startEditDoc(doc)"
                        >
                          编辑
                        </button>
                      </div>
                    </div>
                    <div v-if="editingDocId === doc.id">
                      <textarea
                        v-model="editDocContent"
                        class="w-full min-h-[200px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                        placeholder="请填写文档内容..."
                      ></textarea>
                      <div class="flex justify-end space-x-2 mt-2">
                        <button
                          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50"
                          @click="cancelEditDoc"
                        >
                          取消
                        </button>
                        <button
                          class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90"
                          :disabled="savingDoc"
                          @click="saveDoc(doc)"
                        >
                          {{ savingDoc ? '保存中...' : '保存' }}
                        </button>
                      </div>
                    </div>
                    <div v-else>
                      <pre class="text-sm text-gray-700 bg-white rounded p-3 whitespace-pre-wrap leading-relaxed min-h-[80px] border border-gray-200">{{ currentDoc.editable_content || currentDoc.original_content }}</pre>
                    </div>
                  </div>
                </div>

                <!-- 重新打分按钮和保存后提示 -->
                <div class="mt-4 flex items-center justify-between">
                  <div
                    v-if="saveScoreToast && saveScoreToast.docId === doc.id"
                    class="px-3 py-2 rounded-lg text-xs"
                    :class="saveScoreToast.change >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'"
                  >
                    分数更新：{{ saveScoreToast.newScore }}/{{ saveScoreToast.maxScore }} 分
                    <span class="font-medium">{{ saveScoreToast.change >= 0 ? '+' : '' }}{{ saveScoreToast.change }} 分</span>
                  </div>
                  <div v-else></div>
                  <button
                    class="px-3 py-1.5 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                    :disabled="scoringDocId === doc.id"
                    @click="handleScoreBusinessDoc(doc)"
                  >
                    {{ scoringDocId === doc.id ? '评分中...' : '重新打分' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 方案建议书列表 ========== -->
      <div v-else-if="activeTab === '方案建议书'" class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="p-4">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-700">方案建议书</h3>
              <p class="text-xs text-gray-400 mt-0.5">维保期限 / 项目经理能力 / 人员能力 / 硬件资源占用</p>
            </div>
            <div class="flex items-center space-x-2 text-xs">
              <span class="px-2 py-1 bg-green-50 text-green-600 rounded">星标项: {{ proposalPlanStarCount }}</span>
              <span class="px-2 py-1 bg-blue-50 text-blue-600 rounded">可编辑: {{ proposalPlanFillableCount }}</span>
            </div>
          </div>

          <div
            v-for="doc in proposalPlans"
            :key="doc.id"
            class="border border-gray-100 rounded-lg mb-2 overflow-hidden"
          >
            <div
              class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-all"
              :class="expandedProposalPlanId === doc.id ? 'bg-gray-50' : ''"
              @click="toggleProposalPlan(doc)"
            >
              <div class="flex items-center space-x-3">
                <span class="text-gray-400 text-xs">
                  {{ expandedProposalPlanId === doc.id ? '▼' : '▶' }}
                </span>
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-800">{{ doc.doc_name }}</span>
                  <span v-if="doc.is_star_item" class="px-1.5 py-0.5 bg-warning/10 text-warning text-xs rounded">⭐</span>
                  <span v-if="doc.has_fillable_fields" class="px-1.5 py-0.5 bg-green-50 text-green-600 text-xs rounded">可编辑</span>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-xs text-gray-400">{{ doc.score_point }}</span>
                <span
                  class="px-2 py-0.5 text-xs rounded-full"
                  :class="docStatusClass(doc.status)"
                >
                  {{ docStatusLabel(doc.status) }}
                </span>
              </div>
            </div>

            <div v-if="expandedProposalPlanId === doc.id" class="border-t border-gray-100">
              <div v-if="loadingProposalPlanId === doc.id" class="p-8 text-center">
                <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
                <p class="text-xs text-gray-400 mt-2">加载中...</p>
              </div>

              <div v-else-if="currentProposalPlan" class="p-4">
                <div v-if="currentProposalPlan.rule_description" class="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div class="text-xs font-medium text-blue-600 mb-1">📋 规则说明</div>
                  <p class="text-xs text-gray-600">{{ currentProposalPlan.rule_description }}</p>
                </div>

                <div v-if="currentProposalPlan.return_file_list" class="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div class="text-xs font-medium text-gray-600 mb-1">📎 回标文件清单</div>
                  <div
                    v-for="(f, idx) in parseReturnFileList(currentProposalPlan.return_file_list)"
                    :key="idx"
                    class="flex items-center space-x-2 text-xs text-gray-600 mt-1"
                  >
                    <span>•</span>
                    <span class="font-medium">{{ f.file_name }}</span>
                    <span class="text-gray-400">({{ f.file_type }})</span>
                    <span class="text-gray-400">- {{ f.description }}</span>
                  </div>
                </div>

                <div v-if="currentProposalPlan.has_fillable_fields" class="mb-3 p-2 bg-green-50 rounded text-xs text-green-700">
                  💡 此文档包含可填写字段，请在下方编辑内容
                </div>

                <div class="space-y-3">
                  <div>
                    <div class="text-xs font-medium text-gray-500 mb-1">原始模板内容</div>
                    <pre class="text-xs text-gray-500 bg-gray-50 rounded p-3 whitespace-pre-wrap leading-relaxed max-h-48 overflow-auto border border-gray-100">{{ currentProposalPlan.original_content }}</pre>
                  </div>

                  <div v-if="currentProposalPlan.has_fillable_fields || editingProposalPlanId === doc.id">
                    <div class="flex items-center justify-between mb-1">
                      <div class="text-xs font-medium text-gray-500">✏️ 可编辑内容</div>
                      <div class="flex items-center space-x-3">
                        <button
                          v-if="editingProposalPlanId !== doc.id && currentProposalPlan.has_fillable_fields"
                          class="text-xs text-primary hover:underline flex items-center"
                          @click="doGenerateProposalPlan(doc)"
                          :disabled="generatingProposalPlanId === doc.id"
                        >
                          <span v-if="generatingProposalPlanId === doc.id" class="mr-1 animate-spin inline-block w-3 h-3 border border-current border-t-transparent rounded-full"></span>
                          ✨ AI 自动填充
                        </button>
                        <button
                          v-if="editingProposalPlanId !== doc.id"
                          class="text-xs text-primary hover:underline"
                          @click="startEditProposalPlan(doc)"
                        >
                          编辑
                        </button>
                      </div>
                    </div>
                    <div v-if="editingProposalPlanId === doc.id">
                      <textarea
                        v-model="editProposalPlanContent"
                        class="w-full min-h-[200px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                        placeholder="请填写文档内容..."
                      ></textarea>
                      <div class="flex justify-end space-x-2 mt-2">
                        <button
                          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50"
                          @click="cancelEditProposalPlan"
                        >
                          取消
                        </button>
                        <button
                          class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90"
                          :disabled="savingProposalPlan"
                          @click="saveProposalPlan(doc)"
                        >
                          {{ savingProposalPlan ? '保存中...' : '保存' }}
                        </button>
                      </div>
                    </div>
                    <div v-else>
                      <pre class="text-sm text-gray-700 bg-white rounded p-3 whitespace-pre-wrap leading-relaxed min-h-[80px] border border-gray-200">{{ currentProposalPlan.editable_content || currentProposalPlan.original_content }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 技术文档列表 ========== -->
      <div v-else-if="activeTab === '技术文档'" class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="p-4">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-700">技术文档清单</h3>
              <p class="text-xs text-gray-400 mt-0.5">点击文档查看详情和可填写字段</p>
            </div>
            <div class="flex items-center space-x-2 text-xs">
              <span class="px-2 py-1 bg-green-50 text-green-600 rounded">星标项: {{ techDocStarCount }}</span>
              <span class="px-2 py-1 bg-blue-50 text-blue-600 rounded">可编辑: {{ techDocFillableCount }}</span>
            </div>
          </div>

          <!-- 技术文档列表 -->
          <div
            v-for="doc in techDocs"
            :key="doc.id"
            class="border border-gray-100 rounded-lg mb-2 overflow-hidden"
          >
            <div
              class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-all"
              :class="expandedTechDocId === doc.id ? 'bg-gray-50' : ''"
              @click="toggleTechDoc(doc)"
            >
              <div class="flex items-center space-x-3">
                <span class="text-gray-400 text-xs">
                  {{ expandedTechDocId === doc.id ? '▼' : '▶' }}
                </span>
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-medium text-gray-800">{{ doc.doc_name }}</span>
                  <span v-if="doc.is_star_item" class="px-1.5 py-0.5 bg-warning/10 text-warning text-xs rounded">⭐</span>
                  <span v-if="doc.has_fillable_fields" class="px-1.5 py-0.5 bg-green-50 text-green-600 text-xs rounded">可编辑</span>
                  <span
                    v-if="scoreHistory[doc.id]"
                    class="px-1.5 py-0.5 text-xs rounded font-medium"
                    :class="getScoreBadgeClass(scoreHistory[doc.id].score, scoreHistory[doc.id].max_score)"
                  >
                    {{ scoreHistory[doc.id].score }}/{{ scoreHistory[doc.id].max_score }} 分
                  </span>
                </div>
              </div>
              <div class="flex items-center space-x-3">
                <span class="text-xs text-gray-400">{{ doc.score_point }}</span>
                <span
                  class="px-2 py-0.5 text-xs rounded-full"
                  :class="docStatusClass(doc.status)"
                >
                  {{ docStatusLabel(doc.status) }}
                </span>
                <button
                  class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                  :disabled="exportingTechDocId === doc.id"
                  @click.stop="openExportModal(doc, 'technical')"
                >
                  {{ exportingTechDocId === doc.id ? '导出中...' : '导出' }}
                </button>
                <button
                  class="px-2 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                  :disabled="scoringTechDocId === doc.id"
                  @click.stop="handleScoreTechDoc(doc)"
                >
                  {{ scoringTechDocId === doc.id ? '评分中...' : '评分' }}
                </button>
              </div>
            </div>

            <div v-if="expandedTechDocId === doc.id" class="border-t border-gray-100">
              <div v-if="loadingTechDocId === doc.id" class="p-8 text-center">
                <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
                <p class="text-xs text-gray-400 mt-2">加载中...</p>
              </div>

              <div v-else-if="currentTechDoc" class="p-4">
                <div v-if="currentTechDoc.rule_description" class="mb-4 p-3 bg-blue-50 rounded-lg">
                  <div class="text-xs font-medium text-blue-600 mb-1">📋 规则说明</div>
                  <p class="text-xs text-gray-600">{{ currentTechDoc.rule_description }}</p>
                </div>

                <div v-if="currentTechDoc.return_file_list" class="mb-4 p-3 bg-gray-50 rounded-lg">
                  <div class="text-xs font-medium text-gray-600 mb-1">📎 回标文件清单</div>
                  <div
                    v-for="(f, idx) in parseReturnFileList(currentTechDoc.return_file_list)"
                    :key="idx"
                    class="flex items-center space-x-2 text-xs text-gray-600 mt-1"
                  >
                    <span>•</span>
                    <span class="font-medium">{{ f.file_name }}</span>
                    <span class="text-gray-400">({{ f.file_type }})</span>
                    <span class="text-gray-400">- {{ f.description }}</span>
                  </div>
                </div>

                <div v-if="currentTechDoc.has_fillable_fields" class="mb-3 p-2 bg-green-50 rounded text-xs text-green-700">
                  💡 此文档包含可填写字段，请在下方编辑内容
                </div>

                <div class="space-y-3">
                  <div>
                    <div class="text-xs font-medium text-gray-500 mb-1">原始模板内容</div>
                    <pre class="text-xs text-gray-500 bg-gray-50 rounded p-3 whitespace-pre-wrap leading-relaxed max-h-48 overflow-auto border border-gray-100">{{ currentTechDoc.original_content }}</pre>
                  </div>

                  <div v-if="currentTechDoc.has_fillable_fields || editingTechDocId === doc.id">
                    <div class="flex items-center justify-between mb-1">
                      <div class="text-xs font-medium text-gray-500">✏️ 可编辑内容</div>
                      <div class="flex items-center space-x-3">
                        <button
                          v-if="editingTechDocId !== doc.id && currentTechDoc.has_fillable_fields"
                          class="text-xs text-primary hover:underline flex items-center"
                          @click="generateTechDoc(doc)"
                          :disabled="generatingTechDocId === doc.id"
                        >
                          <span v-if="generatingTechDocId === doc.id" class="mr-1 animate-spin inline-block w-3 h-3 border border-current border-t-transparent rounded-full"></span>
                          ✨ AI 自动填充
                        </button>
                        <button
                          v-if="editingTechDocId !== doc.id"
                          class="text-xs text-primary hover:underline"
                          @click="startEditTechDoc(doc)"
                        >
                          编辑
                        </button>
                      </div>
                    </div>
                    <div v-if="editingTechDocId === doc.id">
                      <textarea
                        v-model="editTechDocContent"
                        class="w-full min-h-[200px] px-3 py-2 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                        placeholder="请填写文档内容..."
                      ></textarea>
                      <div class="flex justify-end space-x-2 mt-2">
                        <button
                          class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50"
                          @click="cancelEditTechDoc"
                        >
                          取消
                        </button>
                        <button
                          class="px-3 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90"
                          :disabled="savingTechDoc"
                          @click="saveTechDoc(doc)"
                        >
                          {{ savingTechDoc ? '保存中...' : '保存' }}
                        </button>
                      </div>
                    </div>
                    <div v-else>
                      <pre class="text-sm text-gray-700 bg-white rounded p-3 whitespace-pre-wrap leading-relaxed min-h-[80px] border border-gray-200">{{ currentTechDoc.editable_content || currentTechDoc.original_content }}</pre>
                    </div>
                  </div>
                </div>

                <!-- 重新打分按钮和保存后提示 -->
                <div class="mt-4 flex items-center justify-between">
                  <div
                    v-if="saveScoreToast && saveScoreToast.docId === doc.id"
                    class="px-3 py-2 rounded-lg text-xs"
                    :class="saveScoreToast.change >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'"
                  >
                    分数更新：{{ saveScoreToast.newScore }}/{{ saveScoreToast.maxScore }} 分
                    <span class="font-medium">{{ saveScoreToast.change >= 0 ? '+' : '' }}{{ saveScoreToast.change }} 分</span>
                  </div>
                  <div v-else></div>
                  <button
                    class="px-3 py-1.5 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all"
                    :disabled="scoringTechDocId === doc.id"
                    @click="handleScoreTechDoc(doc)"
                  >
                    {{ scoringTechDocId === doc.id ? '评分中...' : '重新打分' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 技术案例列表 ========== -->
      <div v-else-if="activeTab === '技术案例'" class="flex-1 overflow-auto bg-white rounded-xl shadow-sm border border-gray-100">
        <div class="p-4">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h3 class="text-sm font-medium text-gray-700">技术案例素材库</h3>
              <p class="text-xs text-gray-400 mt-0.5">根据评审项检索并引用技术案例</p>
            </div>
            <div class="flex items-center space-x-2">
              <button
                class="px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 text-xs transition-all"
                @click="showCreateCaseModal = true"
              >
                + 新建案例
              </button>
            </div>
          </div>

          <!-- 检索区域 -->
          <div class="mb-4 p-3 bg-gray-50 rounded-lg space-y-2">
            <div class="text-xs font-medium text-gray-500 mb-2">🔍 素材检索</div>
            <div class="flex items-center space-x-2">
              <input
                v-model="searchPrimaryItem"
                class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="一级评审项（如：技术方案）"
              />
              <input
                v-model="searchSecondaryItem"
                class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="二级评审项（如：系统架构）"
              />
              <input
                v-model="searchKeyword"
                class="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-primary/50"
                placeholder="关键词"
              />
              <button
                class="px-3 py-1.5 bg-primary text-white rounded-lg hover:bg-primary/90 text-xs transition-all"
                @click="doSearch"
              >
                检索
              </button>
              <button
                class="px-3 py-1.5 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 text-xs transition-all"
                @click="clearSearch"
              >
                清空
              </button>
            </div>
          </div>

          <!-- 案例列表 -->
          <div v-if="loadingCases" class="p-8 text-center">
            <div class="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
            <p class="text-xs text-gray-400 mt-2">加载中...</p>
          </div>

          <div v-else-if="displayedCases.length === 0" class="p-8 text-center text-gray-400 text-sm">
            暂无技术案例，请点击"新建案例"添加
          </div>

          <div v-else>
            <div
              v-for="caseItem in displayedCases"
              :key="caseItem.id"
              class="border border-gray-100 rounded-lg mb-3 overflow-hidden"
            >
              <div
                class="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 transition-all"
                :class="expandedCaseId === caseItem.id ? 'bg-gray-50' : ''"
                @click="toggleCase(caseItem)"
              >
                <div class="flex items-center space-x-3">
                  <span class="text-gray-400 text-xs">
                    {{ expandedCaseId === caseItem.id ? '▼' : '▶' }}
                  </span>
                  <div class="flex items-center space-x-2">
                    <span class="text-sm font-medium text-gray-800">{{ caseItem.title }}</span>
                    <span class="px-1.5 py-0.5 bg-blue-50 text-blue-600 text-xs rounded">{{ caseItem.case_type }}</span>
                    <span class="px-1.5 py-0.5 bg-green-50 text-green-600 text-xs rounded">评分: {{ caseItem.score }}</span>
                  </div>
                </div>
                <div class="flex items-center space-x-3">
                  <span v-if="caseItem.primary_review_item" class="text-xs text-gray-400">{{ caseItem.primary_review_item }}</span>
                  <span v-if="caseItem.secondary_review_item" class="text-xs text-gray-400">/ {{ caseItem.secondary_review_item }}</span>
                </div>
              </div>

              <div v-if="expandedCaseId === caseItem.id" class="border-t border-gray-100 p-4">
                <div v-if="loadingCaseDetail === caseItem.id" class="text-center py-4">
                  <div class="animate-spin w-5 h-5 border-2 border-primary border-t-transparent rounded-full mx-auto"></div>
                </div>
                <div v-else-if="currentCase" class="space-y-3">
                  <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-50 rounded p-2">
                      <div class="text-xs text-gray-400">合同名称</div>
                      <div class="text-xs text-gray-700 font-medium mt-0.5">{{ currentCase.contract_name || '-' }}</div>
                    </div>
                    <div class="bg-gray-50 rounded p-2">
                      <div class="text-xs text-gray-400">合同金额</div>
                      <div class="text-xs text-gray-700 font-medium mt-0.5">{{ currentCase.contract_amount || '-' }}</div>
                    </div>
                    <div class="bg-gray-50 rounded p-2">
                      <div class="text-xs text-gray-400">甲方名称</div>
                      <div class="text-xs text-gray-700 font-medium mt-0.5">{{ currentCase.client_name || '-' }}</div>
                    </div>
                    <div class="bg-gray-50 rounded p-2">
                      <div class="text-xs text-gray-400">置信度</div>
                      <div class="text-xs text-gray-700 font-medium mt-0.5">{{ currentCase.score }}</div>
                    </div>
                  </div>
                  <div v-if="currentCase.summary" class="bg-blue-50 rounded p-2">
                    <div class="text-xs font-medium text-blue-600">📋 摘要</div>
                    <p class="text-xs text-gray-600 mt-1">{{ currentCase.summary }}</p>
                  </div>
                  <div v-if="currentCase.contract_overview" class="bg-gray-50 rounded p-2">
                    <div class="text-xs font-medium text-gray-600">📄 合同内容概述</div>
                    <p class="text-xs text-gray-600 mt-1">{{ currentCase.contract_overview }}</p>
                  </div>
                  <div v-if="currentCase.key_highlights" class="bg-green-50 rounded p-2">
                    <div class="text-xs font-medium text-green-600">✨ 关键技术亮点</div>
                    <p class="text-xs text-gray-600 mt-1">{{ currentCase.key_highlights }}</p>
                  </div>
                  <div v-if="currentCase.video_url" class="bg-purple-50 rounded p-2">
                    <div class="text-xs font-medium text-purple-600">🎬 视频</div>
                    <a :href="currentCase.video_url" target="_blank" class="text-xs text-primary hover:underline mt-1 block">查看视频</a>
                  </div>
                  <div class="flex justify-end space-x-2 pt-2">
                    <button
                      class="px-3 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                      @click="startEditCase(caseItem)"
                    >
                      编辑
                    </button>
                    <button
                      class="px-3 py-1.5 text-xs bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-all"
                      @click="confirmDeleteCase(caseItem)"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="uploading" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-64 text-center">
        <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-3"></div>
        <p class="text-sm text-gray-600">正在解析招标文件...</p>
      </div>
    </div>

    <!-- 新建/编辑案例 Modal -->
    <div v-if="showCreateCaseModal || editingCaseId" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="showCreateCaseModal = false; editingCaseId = null">
      <div class="bg-white rounded-xl p-6 w-[500px] max-h-[80vh] overflow-auto">
        <h3 class="text-base font-medium text-gray-800 mb-4">{{ editingCaseId ? '编辑案例' : '新建技术案例' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-500 block mb-1">案例标题 *</label>
            <input v-model="editCaseForm.title" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：XX智慧城市项目案例" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500 block mb-1">一级评审项</label>
              <input v-model="editCaseForm.primary_review_item" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：技术方案" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">二级评审项</label>
              <input v-model="editCaseForm.secondary_review_item" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：系统架构" />
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">案例类型</label>
            <select v-model="editCaseForm.case_type" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50">
              <option>项目案例</option>
              <option>产品介绍</option>
              <option>方案模板</option>
              <option>行业报告</option>
              <option>技术白皮书</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500 block mb-1">合同名称</label>
              <input v-model="editCaseForm.contract_name" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="XX系统采购合同" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">合同金额</label>
              <input v-model="editCaseForm.contract_amount" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：500万元" />
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">甲方名称</label>
            <input v-model="editCaseForm.client_name" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：某市政府/某企业" />
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">案例摘要</label>
            <textarea v-model="editCaseForm.summary" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50" :rows="2" placeholder="简要描述案例背景和亮点..."></textarea>
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">合同内容概述</label>
            <textarea v-model="editCaseForm.contract_overview" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50" :rows="3" placeholder="详细描述合同内容、项目范围、交付成果..."></textarea>
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">关键技术亮点</label>
            <textarea v-model="editCaseForm.key_highlights" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary/50" :rows="2" placeholder="列举关键技术亮点、创新点..."></textarea>
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">来源</label>
            <input v-model="editCaseForm.source" class="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="如：公司内部/外部引用" />
          </div>
        </div>
        <div class="flex justify-end space-x-2 mt-4">
          <button class="px-4 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all" @click="showCreateCaseModal = false; editingCaseId = null; resetEditForm()">取消</button>
          <button class="px-4 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" :disabled="savingCase || !editCaseForm.title" @click="saveCase">
            {{ savingCase ? '保存中...' : (editingCaseId ? '保存修改' : '创建案例') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 导出格式选择 Modal -->
    <div v-if="showExportModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="closeExportModal">
      <div class="bg-white rounded-xl p-6 w-80">
        <h3 class="text-base font-medium text-gray-800 mb-1">导出文档</h3>
        <p v-if="exportDocInfo" class="text-xs text-gray-400 mb-4">{{ exportDocInfo.docName }}</p>
        <div class="space-y-2">
          <button class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-all" @click="doExport('word')">Word (.docx)</button>
          <button class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-all" @click="doExport('excel')">Excel (.xlsx)</button>
          <button class="w-full px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-all" @click="doExport('pdf')">PDF (.pdf)</button>
        </div>
        <div class="flex justify-end mt-4">
          <button class="px-4 py-1.5 text-xs border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-all" @click="closeExportModal">取消</button>
        </div>
      </div>
    </div>

    <!-- 评分结果 Modal -->
    <div v-if="showScoreModal" class="fixed inset-0 bg-black/30 flex items-center justify-center z-50" @click.self="closeScoreModal">
      <div class="bg-white rounded-xl p-6 w-[420px] max-h-[70vh] overflow-auto">
        <h3 class="text-base font-medium text-gray-800 mb-4">📊 文档评分结果</h3>
        <div v-if="scoreResult" class="space-y-3">
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <span class="text-sm text-gray-600">完整度分数</span>
            <span class="text-lg font-bold text-blue-600">{{ scoreResult.score }} / {{ scoreResult.max_score }}</span>
          </div>
          <div v-if="scoredDocId && scoreHistory[scoredDocId]" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-sm text-gray-600">上次得分</span>
            <div class="text-sm">
              <span class="font-medium text-gray-700">{{ scoreHistory[scoredDocId].score }} / {{ scoreHistory[scoredDocId].max_score }}</span>
              <span
                class="ml-2 font-bold"
                :class="scoreResult.score - scoreHistory[scoredDocId].score >= 0 ? 'text-green-600' : 'text-red-600'"
              >
                {{ scoreResult.score - scoreHistory[scoredDocId].score >= 0 ? '↑' : '↓' }}{{ Math.abs(scoreResult.score - scoreHistory[scoredDocId].score) }}
              </span>
            </div>
          </div>
          <div v-if="scoreResult.message" class="text-xs text-gray-500">{{ scoreResult.message }}</div>
          <div v-if="scoreResult.breakdown && Object.keys(scoreResult.breakdown).length > 0">
            <div class="text-xs font-medium text-gray-500 mb-2">详细评分项</div>
            <div v-for="(value, key) in scoreResult.breakdown" :key="key" class="flex items-center justify-between py-1 border-b border-gray-50 text-xs">
              <span class="text-gray-600">{{ key }}</span>
              <span class="text-gray-800 font-medium">{{ typeof value === 'object' ? JSON.stringify(value) : String(value) }}</span>
            </div>
          </div>
          <div v-else class="text-xs text-gray-400">暂无详细评分项</div>
        </div>
        <div class="flex justify-end mt-4">
          <button class="px-4 py-1.5 text-xs bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" @click="closeScoreModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getProject } from '../services/project'
import { listParsingSections, updateParsingSection, uploadAndParse } from '../services/tender'
import {
  listBusinessDocuments,
  getBusinessDocumentDetail,
  updateBusinessDocument,
  generateBusinessDocument,
  exportBusinessDocument,
  scoreBusinessDocument,
  type DocumentExportResult,
  type DocumentScoreResult,
} from '../services/businessDocument'
import {
  listTechnicalDocuments,
  getTechnicalDocumentDetail,
  updateTechnicalDocument,
  generateTechnicalDocument,
  exportTechnicalDocument,
  scoreTechnicalDocument,
} from '../services/technicalDocument'
import {
  listProposalPlans,
  getProposalPlanDetail,
  updateProposalPlan,
  generateProposalPlan,
} from '../services/proposalPlan'
import {
  listTechnicalCases,
  getTechnicalCaseDetail,
  createTechnicalCase,
  updateTechnicalCase,
  deleteTechnicalCase,
  searchTechnicalCases,
} from '../services/technicalCase'
import type { TechnicalCaseDetail, TechnicalCaseSummary } from '../services/technicalCase'
import type { ProposalPlanSummary, ProposalPlanDetail } from '../services/proposalPlan'
import type { BusinessDocumentDetail, BusinessDocumentSummary } from '../services/businessDocument'
import type { TechnicalDocumentDetail, TechnicalDocumentSummary } from '../services/technicalDocument'
import type { Project } from '../types'

const router = useRouter()
const route = useRoute()

// Support both route params
const pid = computed(() => (route.params.projectId as string) || (route.params.id as string))

const project = ref<Project | null>(null)
const sections = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const activeTab = ref<'商务' | '技术' | '商务文档' | '技术文档' | '方案建议书' | '技术案例'>('商务')
const expandedSection = ref<string | null>(null)
const editingSection = ref<string | null>(null)
const editContent = ref('')

// Business documents
const businessDocs = ref<BusinessDocumentSummary[]>([])
const expandedDocId = ref<string | null>(null)
const loadingDocId = ref<string | null>(null)
const editingDocId = ref<string | null>(null)
const currentDoc = ref<BusinessDocumentDetail | null>(null)
const editDocContent = ref('')
const savingDoc = ref(false)
const generatingDocId = ref<string | null>(null)
const exportingDocId = ref<string | null>(null)
const scoringDocId = ref<string | null>(null)

// Technical documents
const techDocs = ref<TechnicalDocumentSummary[]>([])
const expandedTechDocId = ref<string | null>(null)
const loadingTechDocId = ref<string | null>(null)
const editingTechDocId = ref<string | null>(null)
const currentTechDoc = ref<TechnicalDocumentDetail | null>(null)
const editTechDocContent = ref('')
const savingTechDoc = ref(false)
const generatingTechDocId = ref<string | null>(null)
const exportingTechDocId = ref<string | null>(null)
const scoringTechDocId = ref<string | null>(null)

// Score modal
const showScoreModal = ref(false)
const scoreResult = ref<DocumentScoreResult | null>(null)

// Score history
const scoreHistory = ref<Record<string, { score: number; max_score: number; timestamp: number }>>({})
const scoredDocId = ref<string | null>(null)

// Save auto-recalc toast
const saveScoreToast = ref<{ docId: string; change: number; newScore: number; maxScore: number } | null>(null)

// Export modal
const showExportModal = ref(false)
const exportDocInfo = ref<{ type: 'business' | 'technical'; docId: string; docName: string } | null>(null)

const businessSections = computed(() => sections.value.filter(s => s.section_type === '商务'))
const techSections = computed(() => sections.value.filter(s => s.section_type === '技术'))
const filteredSections = computed(() => activeTab.value === '商务' ? businessSections.value : techSections.value)

const businessDocStarCount = computed(() => businessDocs.value.filter(d => d.is_star_item).length)
const businessDocFillableCount = computed(() => businessDocs.value.filter(d => d.has_fillable_fields).length)

const techDocStarCount = computed(() => techDocs.value.filter(d => d.is_star_item).length)
const techDocFillableCount = computed(() => techDocs.value.filter(d => d.has_fillable_fields).length)

// Proposal plans
const proposalPlans = ref<ProposalPlanSummary[]>([])
const expandedProposalPlanId = ref<string | null>(null)
const loadingProposalPlanId = ref<string | null>(null)
const editingProposalPlanId = ref<string | null>(null)
const currentProposalPlan = ref<ProposalPlanDetail | null>(null)
const editProposalPlanContent = ref('')
const savingProposalPlan = ref(false)
const generatingProposalPlanId = ref<string | null>(null)

const proposalPlanStarCount = computed(() => proposalPlans.value.filter(d => d.is_star_item).length)
const proposalPlanFillableCount = computed(() => proposalPlans.value.filter(d => d.has_fillable_fields).length)

// Technical cases
const technicalCases = ref<TechnicalCaseSummary[]>([])
const expandedCaseId = ref<string | null>(null)
const loadingCaseDetail = ref<string | null>(null)
const currentCase = ref<TechnicalCaseDetail | null>(null)
const editingCaseId = ref<string | null>(null)
const editCaseForm = ref({
  title: '',
  primary_review_item: '',
  secondary_review_item: '',
  case_type: '项目案例',
  summary: '',
  contract_name: '',
  contract_amount: '',
  client_name: '',
  contract_overview: '',
  key_highlights: '',
  source: '',
})
const loadingCases = ref(false)
const savingCase = ref(false)
const showCreateCaseModal = ref(false)
const deleteCaseId = ref<string | null>(null)

// Search
const searchPrimaryItem = ref('')
const searchSecondaryItem = ref('')
const searchKeyword = ref('')
const isSearchMode = ref(false)
const searchResults = ref<TechnicalCaseSummary[]>([])

const displayedCases = computed(() => isSearchMode.value ? searchResults.value : technicalCases.value)

function statusClass(status: string) {
  switch (status) {
    case '待决策': return 'bg-gray-100 text-gray-600'
    case '已投标': return 'bg-blue-100 text-blue-600'
    case '未中标': return 'bg-red-100 text-red-600'
    case '已中标': return 'bg-green-100 text-green-600'
    default: return 'bg-gray-100 text-gray-600'
  }
}

function docStatusClass(status: string) {
  switch (status) {
    case 'pending': return 'bg-gray-100 text-gray-500'
    case 'filled': return 'bg-blue-100 text-blue-600'
    case 'confirmed': return 'bg-green-100 text-green-600'
    default: return 'bg-gray-100 text-gray-500'
  }
}

function docStatusLabel(status: string) {
  switch (status) {
    case 'pending': return '待填写'
    case 'filled': return '已填写'
    case 'confirmed': return '已确认'
    default: return status
  }
}

function getScoreBadgeClass(score: number, maxScore: number) {
  const ratio = maxScore > 0 ? score / maxScore : 0
  if (ratio >= 0.8) return 'bg-green-100 text-green-700'
  if (ratio >= 0.6) return 'bg-blue-100 text-blue-700'
  return 'bg-red-100 text-red-700'
}

function showSaveScoreToast(docId: string, oldScore: number, newScore: number, maxScore: number) {
  saveScoreToast.value = { docId, change: newScore - oldScore, newScore, maxScore }
  setTimeout(() => {
    if (saveScoreToast.value?.docId === docId) {
      saveScoreToast.value = null
    }
  }, 3000)
}

function parseReturnFileList(jsonStr: string) {
  try {
    return JSON.parse(jsonStr || '[]')
  } catch {
    return []
  }
}

async function loadSections() {
  const id = pid.value
  if (!id) return
  try {
    sections.value = await listParsingSections(id)
    if (sections.value.length > 0) {
      expandedSection.value = sections.value[0].id
    }
  } catch (e) {
    console.error('Load sections failed:', e)
  }
}

async function loadBusinessDocs() {
  const id = pid.value
  if (!id) return
  try {
    businessDocs.value = await listBusinessDocuments(id)
  } catch (e) {
    console.error('Load business docs failed:', e)
  }
}

async function loadTechDocs() {
  const id = pid.value
  if (!id) return
  try {
    techDocs.value = await listTechnicalDocuments(id)
  } catch (e) {
    console.error('Load tech docs failed:', e)
  }
}

async function loadProposalPlans() {
  const id = pid.value
  if (!id) return
  try {
    proposalPlans.value = await listProposalPlans(id)
  } catch (e) {
    console.error('Load proposal plans failed:', e)
  }
}

async function loadTechnicalCases() {
  const id = pid.value
  if (!id) return
  try {
    technicalCases.value = await listTechnicalCases(id)
  } catch (e) {
    console.error('Load technical cases failed:', e)
  }
}

async function toggleProposalPlan(doc: ProposalPlanSummary) {
  if (expandedProposalPlanId.value === doc.id) {
    expandedProposalPlanId.value = null
    currentProposalPlan.value = null
    return
  }
  expandedProposalPlanId.value = doc.id
  loadingProposalPlanId.value = doc.id
  currentProposalPlan.value = null
  try {
    currentProposalPlan.value = await getProposalPlanDetail(pid.value!, doc.id)
  } catch (e) {
    console.error('Load proposal plan detail failed:', e)
  } finally {
    loadingProposalPlanId.value = null
  }
}

function startEditProposalPlan(doc: { id: string; editable_content?: string; original_content?: string }) {
  editingProposalPlanId.value = doc.id
  editProposalPlanContent.value = doc.editable_content || doc.original_content || ''
}

function cancelEditProposalPlan() {
  editingProposalPlanId.value = null
  editProposalPlanContent.value = ''
}

async function saveProposalPlan(doc: ProposalPlanSummary) {
  savingProposalPlan.value = true
  try {
    const updated = await updateProposalPlan(pid.value!, doc.id, {
      editable_content: editProposalPlanContent.value,
      status: 'filled',
    })
    currentProposalPlan.value = updated
    const idx = proposalPlans.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      proposalPlans.value[idx] = { ...proposalPlans.value[idx], status: updated.status }
    }
    editingProposalPlanId.value = null
  } catch (e) {
    console.error('Save proposal plan failed:', e)
  } finally {
    savingProposalPlan.value = false
  }
}

async function doGenerateProposalPlan(doc: ProposalPlanSummary) {
  generatingProposalPlanId.value = doc.id
  try {
    const updated = await generateProposalPlan(pid.value!, doc.id)
    currentProposalPlan.value = updated
    const idx = proposalPlans.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      proposalPlans.value[idx] = { ...proposalPlans.value[idx], status: updated.status }
    }
  } catch (e) {
    console.error('Generate proposal plan failed:', e)
    alert('生成失败，请重试')
  } finally {
    generatingProposalPlanId.value = null
  }
}

async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const id = pid.value
  if (!id) return

  uploading.value = true
  try {
    sections.value = await uploadAndParse(id, file)
    if (sections.value.length > 0) {
      expandedSection.value = sections.value[0].id
    }
  } catch (e) {
    console.error('Upload failed:', e)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function startEdit(section: any) {
  editingSection.value = section.id
  editContent.value = section.content || ''
}

function cancelEdit() {
  editingSection.value = null
  editContent.value = ''
}

async function saveSection(section: any) {
  saving.value = true
  try {
    const id = pid.value
    const updated = await updateParsingSection(id, section.id, editContent.value)
    const idx = sections.value.findIndex((s: any) => s.id === section.id)
    if (idx >= 0) {
      sections.value[idx] = { ...sections.value[idx], ...updated }
    }
    editingSection.value = null
  } catch (e) {
    console.error('Save failed:', e)
  } finally {
    saving.value = false
  }
}

// ---- Business Document handlers ----

async function toggleDoc(doc: BusinessDocumentSummary) {
  if (expandedDocId.value === doc.id) {
    expandedDocId.value = null
    currentDoc.value = null
    return
  }
  expandedDocId.value = doc.id
  loadingDocId.value = doc.id
  currentDoc.value = null
  try {
    currentDoc.value = await getBusinessDocumentDetail(pid.value!, doc.id)
  } catch (e) {
    console.error('Load doc detail failed:', e)
  } finally {
    loadingDocId.value = null
  }
}

function startEditDoc(doc: { id: string; editable_content?: string; original_content?: string }) {
  editingDocId.value = doc.id
  editDocContent.value = doc.editable_content || doc.original_content || ''
}

function cancelEditDoc() {
  editingDocId.value = null
  editDocContent.value = ''
}

async function saveDoc(doc: BusinessDocumentSummary) {
  savingDoc.value = true
  try {
    const updated = await updateBusinessDocument(pid.value!, doc.id, {
      editable_content: editDocContent.value,
      status: 'filled',
    })
    currentDoc.value = updated
    const idx = businessDocs.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      businessDocs.value[idx] = { ...businessDocs.value[idx], status: updated.status }
    }
    editingDocId.value = null

    // Auto-recalc if previously scored
    const previous = scoreHistory.value[doc.id]
    if (previous && pid.value) {
      try {
        const result = await scoreBusinessDocument(pid.value, doc.id)
        scoreHistory.value[doc.id] = {
          score: result.score,
          max_score: result.max_score,
          timestamp: Date.now(),
        }
        showSaveScoreToast(doc.id, previous.score, result.score, result.max_score)
      } catch (e) {
        console.error('Auto-recalc business doc score failed:', e)
      }
    }
  } catch (e) {
    console.error('Save doc failed:', e)
  } finally {
    savingDoc.value = false
  }
}

async function generateDoc(doc: BusinessDocumentSummary) {
  generatingDocId.value = doc.id
  try {
    const updated = await generateBusinessDocument(pid.value!, doc.id)
    currentDoc.value = updated
    const idx = businessDocs.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      businessDocs.value[idx] = { ...businessDocs.value[idx], status: updated.status }
    }
  } catch (e) {
    console.error('Generate doc failed:', e)
    alert('生成失败，请重试')
  } finally {
    generatingDocId.value = null
  }
}

// ---- Technical Document handlers ----

async function toggleTechDoc(doc: TechnicalDocumentSummary) {
  if (expandedTechDocId.value === doc.id) {
    expandedTechDocId.value = null
    currentTechDoc.value = null
    return
  }
  expandedTechDocId.value = doc.id
  loadingTechDocId.value = doc.id
  currentTechDoc.value = null
  try {
    currentTechDoc.value = await getTechnicalDocumentDetail(pid.value!, doc.id)
  } catch (e) {
    console.error('Load tech doc detail failed:', e)
  } finally {
    loadingTechDocId.value = null
  }
}

function startEditTechDoc(doc: { id: string; editable_content?: string; original_content?: string }) {
  editingTechDocId.value = doc.id
  editTechDocContent.value = doc.editable_content || doc.original_content || ''
}

function cancelEditTechDoc() {
  editingTechDocId.value = null
  editTechDocContent.value = ''
}

async function saveTechDoc(doc: TechnicalDocumentSummary) {
  savingTechDoc.value = true
  try {
    const updated = await updateTechnicalDocument(pid.value!, doc.id, {
      editable_content: editTechDocContent.value,
      status: 'filled',
    })
    currentTechDoc.value = updated
    const idx = techDocs.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      techDocs.value[idx] = { ...techDocs.value[idx], status: updated.status }
    }
    editingTechDocId.value = null

    // Auto-recalc if previously scored
    const previous = scoreHistory.value[doc.id]
    if (previous && pid.value) {
      try {
        const result = await scoreTechnicalDocument(pid.value, doc.id)
        scoreHistory.value[doc.id] = {
          score: result.score,
          max_score: result.max_score,
          timestamp: Date.now(),
        }
        showSaveScoreToast(doc.id, previous.score, result.score, result.max_score)
      } catch (e) {
        console.error('Auto-recalc tech doc score failed:', e)
      }
    }
  } catch (e) {
    console.error('Save tech doc failed:', e)
  } finally {
    savingTechDoc.value = false
  }
}

async function generateTechDoc(doc: TechnicalDocumentSummary) {
  generatingTechDocId.value = doc.id
  try {
    const updated = await generateTechnicalDocument(pid.value!, doc.id)
    currentTechDoc.value = updated
    const idx = techDocs.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) {
      techDocs.value[idx] = { ...techDocs.value[idx], status: updated.status }
    }
  } catch (e) {
    console.error('Generate tech doc failed:', e)
    alert('生成失败，请重试')
  } finally {
    generatingTechDocId.value = null
  }
}

// ---- Export / Score handlers ----

function openExportModal(doc: BusinessDocumentSummary | TechnicalDocumentSummary, type: 'business' | 'technical') {
  exportDocInfo.value = { type, docId: doc.id, docName: doc.doc_name }
  showExportModal.value = true
}

function closeExportModal() {
  showExportModal.value = false
  exportDocInfo.value = null
}

function triggerDownload(url: string, filename: string) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename || 'download'
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

async function doExport(fmt: string) {
  if (!exportDocInfo.value || !pid.value) return
  const { type, docId } = exportDocInfo.value
  if (type === 'business') {
    exportingDocId.value = docId
    try {
      const result = await exportBusinessDocument(pid.value, docId, fmt)
      triggerDownload(result.download_url, result.filename)
    } catch (e) {
      console.error('Export business doc failed:', e)
      alert('导出失败，请重试')
    } finally {
      exportingDocId.value = null
    }
  } else {
    exportingTechDocId.value = docId
    try {
      const result = await exportTechnicalDocument(pid.value, docId, fmt)
      triggerDownload(result.download_url, result.filename)
    } catch (e) {
      console.error('Export tech doc failed:', e)
      alert('导出失败，请重试')
    } finally {
      exportingTechDocId.value = null
    }
  }
  closeExportModal()
}

async function handleScoreBusinessDoc(doc: BusinessDocumentSummary) {
  if (!pid.value) return
  scoringDocId.value = doc.id
  scoredDocId.value = doc.id
  try {
    const result = await scoreBusinessDocument(pid.value, doc.id)
    scoreResult.value = result
    showScoreModal.value = true
    scoreHistory.value[doc.id] = {
      score: result.score,
      max_score: result.max_score,
      timestamp: Date.now(),
    }
  } catch (e) {
    console.error('Score business doc failed:', e)
    alert('评分失败，请重试')
  } finally {
    scoringDocId.value = null
  }
}

async function handleScoreTechDoc(doc: TechnicalDocumentSummary) {
  if (!pid.value) return
  scoringTechDocId.value = doc.id
  scoredDocId.value = doc.id
  try {
    const result = await scoreTechnicalDocument(pid.value, doc.id)
    scoreResult.value = result
    showScoreModal.value = true
    scoreHistory.value[doc.id] = {
      score: result.score,
      max_score: result.max_score,
      timestamp: Date.now(),
    }
  } catch (e) {
    console.error('Score tech doc failed:', e)
    alert('评分失败，请重试')
  } finally {
    scoringTechDocId.value = null
  }
}

function closeScoreModal() {
  showScoreModal.value = false
  scoreResult.value = null
  scoredDocId.value = null
}

onMounted(async () => {
  const id = pid.value
  if (!id) return
  loading.value = true
  try {
    project.value = await getProject(id)
    await Promise.all([loadSections(), loadBusinessDocs(), loadTechDocs(), loadProposalPlans(), loadTechnicalCases()])
  } catch (e) {
    console.error('Load failed:', e)
  } finally {
    loading.value = false
  }
})

async function toggleCase(item: TechnicalCaseSummary) {
  if (expandedCaseId.value === item.id) {
    expandedCaseId.value = null
    currentCase.value = null
    return
  }
  expandedCaseId.value = item.id
  loadingCaseDetail.value = item.id
  currentCase.value = null
  try {
    currentCase.value = await getTechnicalCaseDetail(pid.value!, item.id)
  } catch (e) {
    console.error('Load case detail failed:', e)
  } finally {
    loadingCaseDetail.value = null
  }
}

function startEditCase(item: TechnicalCaseSummary & Partial<Pick<TechnicalCaseDetail, 'contract_overview' | 'key_highlights' | 'source'>>) {
  editingCaseId.value = item.id
  editCaseForm.value = {
    title: item.title,
    primary_review_item: item.primary_review_item,
    secondary_review_item: item.secondary_review_item,
    case_type: item.case_type,
    summary: item.summary,
    contract_name: item.contract_name,
    contract_amount: item.contract_amount,
    client_name: item.client_name,
    contract_overview: item.contract_overview || '',
    key_highlights: item.key_highlights || '',
    source: item.source || '',
  }
  expandedCaseId.value = item.id
}

async function saveCase() {
  if (!editingCaseId.value) {
    // create new
    savingCase.value = true
    try {
      const created = await createTechnicalCase(pid.value!, editCaseForm.value)
      technicalCases.value.unshift(created)
      showCreateCaseModal.value = false
      resetEditForm()
    } catch (e) {
      console.error('Create case failed:', e)
    } finally {
      savingCase.value = false
    }
  } else {
    // update existing
    savingCase.value = true
    try {
      const updated = await updateTechnicalCase(pid.value!, editingCaseId.value, editCaseForm.value)
      const idx = technicalCases.value.findIndex(c => c.id === editingCaseId.value)
      if (idx >= 0) technicalCases.value[idx] = updated
      currentCase.value = updated
      editingCaseId.value = null
    } catch (e) {
      console.error('Update case failed:', e)
    } finally {
      savingCase.value = false
    }
  }
}

function resetEditForm() {
  editingCaseId.value = null
  editCaseForm.value = {
    title: '',
    primary_review_item: '',
    secondary_review_item: '',
    case_type: '项目案例',
    summary: '',
    contract_name: '',
    contract_amount: '',
    client_name: '',
    contract_overview: '',
    key_highlights: '',
    source: '',
  }
}

async function confirmDeleteCase(item: TechnicalCaseSummary) {
  if (!confirm(`确定删除案例"${item.title}"吗？`)) return
  try {
    await deleteTechnicalCase(pid.value!, item.id)
    technicalCases.value = technicalCases.value.filter(c => c.id !== item.id)
    if (expandedCaseId.value === item.id) {
      expandedCaseId.value = null
      currentCase.value = null
    }
  } catch (e) {
    console.error('Delete case failed:', e)
  }
}

async function doSearch() {
  if (!pid.value) return
  loadingCases.value = true
  isSearchMode.value = true
  try {
    searchResults.value = await searchTechnicalCases(pid.value!, {
      primary_item: searchPrimaryItem.value,
      secondary_item: searchSecondaryItem.value,
      keyword: searchKeyword.value,
    })
  } catch (e) {
    console.error('Search failed:', e)
  } finally {
    loadingCases.value = false
  }
}

function clearSearch() {
  searchPrimaryItem.value = ''
  searchSecondaryItem.value = ''
  searchKeyword.value = ''
  isSearchMode.value = false
  searchResults.value = []
}</script>

<style scoped>
.fade-in {
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
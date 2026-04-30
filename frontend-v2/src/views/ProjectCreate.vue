<template>
  <div class="fade-in h-full flex flex-col">
    <!-- 顶部状态栏 -->
    <div class="bg-white border-b border-gray-200 mb-6">
      <div class="flex justify-between items-center px-4 py-3">
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <span class="text-sm text-gray-500 mr-2">当前项目:</span>
            <span class="text-sm font-medium">{{ currentProjectName || '未选择项目' }}</span>
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <div class="flex items-center text-green-500 text-sm">
            <span class="mr-1">🟢</span>
            环境正常
          </div>
          <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            👤
          </div>
        </div>
      </div>
    </div>



    <!-- 标题和操作按钮 -->
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center space-x-4">
        <button 
          class="flex items-center px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300"
          @click="goBack"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          返回
        </button>
        <h2 class="text-2xl font-bold text-gray-800">新增项目</h2>
      </div>
      <button class="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90 transition-all duration-300">
        保存项目
      </button>
    </div>

    <!-- 进度条 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6" style="height: 130px;">
      <div class="flex items-center justify-between">
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="flex flex-col items-center"
        >
          <div class="flex items-center">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-white z-10"
              :class="[
                index < currentStep ? 'bg-success' :
                index === currentStep ? 'bg-primary' :
                'bg-gray-200 text-gray-500'
              ]"
            >
              {{ index < currentStep ? '✓' : index + 1 }}
            </div>
            <div
              v-if="index < steps.length - 1"
              class="flex-1 h-1 mx-4 z-0"
              :class="[
                index < currentStep ? 'bg-success' : 'bg-gray-200'
              ]"
            ></div>
          </div>
          <span
            class="mt-2 text-sm font-medium"
            :class="[
              index <= currentStep ? 'text-gray-800' : 'text-gray-400'
            ]"
          >
            {{ step.name }}
          </span>
          <span
            class="mt-1 text-xs"
            :class="[
              index <= currentStep ? 'text-gray-500' : 'text-gray-300'
            ]"
          >
            {{ step.description }}
          </span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 p-6 overflow-auto">
      <!-- 解析文件步骤 -->
      <div v-if="currentStep === 0" class="space-y-6">
        <!-- 文件上传区域 -->
        <div class="border-b border-gray-200 pb-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">招标文件解析</h3>
          
          <!-- 上传区域 -->
          <div v-if="!uploadedFile" class="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-primary transition-all duration-300">
            <div class="flex flex-col items-center">
              <svg class="w-8 h-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              <span class="text-sm text-gray-600">点击上传招标文件</span>
              <span class="text-xs text-gray-500 mt-1">支持上传 Word、Zip、Rar、PRD、Excel 格式文件</span>
              <input type="file" ref="tenderFileInput" class="hidden" @change="onFileSelected" accept=".doc,.docx,.pdf,.zip,.rar,.xlsx">
              <button class="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300" @click="tenderFileInput.click()">
                选择文件
              </button>
            </div>
          </div>
          
          <!-- 已上传文件展示 -->
          <div v-else class="border-2 border-dashed border-primary/30 rounded-lg p-4 text-center bg-primary/5 transition-all duration-300" style="height: 130px;">
            <div class="flex items-center justify-center space-x-4">
              <div class="text-4xl">📄</div>
              <div class="text-left">
                <p class="font-medium text-gray-800">{{ uploadedFile.name }}</p>
                <p class="text-sm text-gray-500">{{ formatFileSize(uploadedFile.size) }}</p>
                <div v-if="uploadStatus === '解析中'" class="mt-2 flex items-center">
                  <div class="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      class="h-full bg-primary rounded-full transition-all duration-300" 
                      :style="{ width: uploadProgress + '%' }"
                    ></div>
                  </div>
                  <span class="ml-2 text-sm text-gray-600">{{ uploadProgress }}%</span>
                </div>
              </div>
            </div>
            <button class="mt-3 px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="reuploadFile">
              重新选择文件
            </button>
          </div>
          
          <!-- 上传状态 -->
          <div v-if="uploadStatus" class="flex items-center justify-between p-3 border border-gray-100 rounded-lg" :class="{
            'bg-green-50 border-green-200': uploadStatus === '文件解析成功',
            'bg-yellow-50 border-yellow-200': uploadStatus === '解析中' || uploadStatus.includes('正在后台解析'),
            'bg-red-50 border-red-200': uploadStatus === 'error'
          }">
            <span class="text-sm" :class="{
              'text-green-700': uploadStatus === '文件解析成功',
              'text-yellow-700': uploadStatus === '解析中' || uploadStatus.includes('正在后台解析'),
              'text-red-700': uploadStatus === 'error'
            }">
              {{ uploadStatus === '文件解析成功' ? '文件解析成功，已提取关键信息' : (uploadStatus === 'error' ? formErrors.companyName || '解析失败' : uploadStatus) }}
            </span>
            <button v-if="uploadStatus === '文件解析成功'" class="text-xs text-primary" @click="reuploadFile">
              重新上传
            </button>
            <button v-if="uploadStatus === 'error'" class="text-xs text-primary ml-2" @click="reuploadFile">
              重新上传
            </button>
          </div>
        </div>

        <!-- 文件解析后显示的内容 -->
        <div v-if="uploadedFile && uploadStatus === '文件解析成功'" class="space-y-6">
          <!-- 基础信息填写 -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">基础信息</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">应标公司 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  v-model="basicInfo.companyName"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  :class="{ 'border-danger': formErrors.companyName }"
                >
                <p v-if="formErrors.companyName" class="mt-1 text-xs text-danger">{{ formErrors.companyName }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">代理人 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  v-model="basicInfo.agent"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  :class="{ 'border-danger': formErrors.agent }"
                >
                <p v-if="formErrors.agent" class="mt-1 text-xs text-danger">{{ formErrors.agent }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">电话 <span class="text-danger">*</span></label>
                <input 
                  type="tel" 
                  v-model="basicInfo.phone"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  :class="{ 'border-danger': formErrors.phone }"
                >
                <p v-if="formErrors.phone" class="mt-1 text-xs text-danger">{{ formErrors.phone }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">邮箱 <span class="text-danger">*</span></label>
                <input 
                  type="email" 
                  v-model="basicInfo.email"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  :class="{ 'border-danger': formErrors.email }"
                >
                <p v-if="formErrors.email" class="mt-1 text-xs text-danger">{{ formErrors.email }}</p>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">公司地址 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  v-model="basicInfo.address"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  :class="{ 'border-danger': formErrors.address }"
                >
                <p v-if="formErrors.address" class="mt-1 text-xs text-danger">{{ formErrors.address }}</p>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">开户银行信息 <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  v-model="basicInfo.bankInfo"
                  class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                  placeholder="银行名称、账号等信息"
                  :class="{ 'border-danger': formErrors.bankInfo }"
                >
                <p v-if="formErrors.bankInfo" class="mt-1 text-xs text-danger">{{ formErrors.bankInfo }}</p>
              </div>
            </div>
          </div>

          <!-- 招标原文和关键信息 -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- 招标原文 -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">招标原文</h3>
              <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="bg-gray-50 border-b border-gray-200 px-4 py-2">
                  <select v-model="selectedSourceFile" class="text-sm border-none bg-transparent focus:outline-none" @change="onSourceFileChange">
                    <option v-for="(file, idx) in projectFileList" :key="idx" :value="file.name">{{ file.name }}</option>
                  </select>
                </div>
                <div class="p-4 max-h-96 overflow-auto bg-gray-50">
                  <pre v-if="selectedFileContent" class="text-sm text-gray-700 whitespace-pre-wrap">{{ selectedFileContent }}</pre>
                  <div v-else class="text-sm text-gray-400 text-center py-8">
                    选择文件后显示内容
                  </div>
                </div>
              </div>

              <!-- 引用内容展示区域 -->
              <div v-if="currentReference.visible && uploadedFile" class="mt-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">引用原文</h3>
                <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-lg">
                  <div class="flex items-start justify-between mb-3">
                    <div>
                      <span class="text-sm font-medium text-blue-800">来源文件：</span>
                      <span class="text-sm text-blue-700">{{ currentReference.filename }}</span>
                    </div>
                    <button 
                      class="text-blue-500 hover:text-blue-700 text-sm"
                      @click="currentReference.visible = false"
                    >
                      关闭
                    </button>
                  </div>
                  <div class="bg-white p-4 rounded border border-blue-100">
                    <pre class="text-sm text-gray-800 whitespace-pre-wrap font-sans">{{ currentReference.originalText }}</pre>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关键信息 -->
            <div>
              <h3 class="text-lg font-semibold text-gray-800 mb-4">关键信息</h3>
              
              <!-- Tab切换 -->
              <div class="border-b border-gray-200 mb-4">
                <div class="flex space-x-4">
                  <button 
                    class="px-4 py-2 border-b-2 font-medium text-sm transition-all" 
                    :class="activeTab === 'info' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                    @click="activeTab = 'info'"
                  >
                    基本信息
                  </button>
                  <button 
                    class="px-4 py-2 border-b-2 font-medium text-sm transition-all" 
                    :class="activeTab === 'star' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                    @click="activeTab = 'star'"
                  >
                    星标项
                  </button>
                </div>
              </div>
              
              <!-- 基本信息Tab -->
              <div v-if="activeTab === 'info'" class="space-y-3">
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 项目名称</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.projectName.value }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('项目名称')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 标书类型</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.bidType.value }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('标书类型')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 项目预算</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.budget.value }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('项目预算')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 标书起止时间</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ formatDate(keyInfo.startTime.value) }} 至 {{ formatDate(keyInfo.endTime.value) }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('标书起止时间')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 投标截止时间</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ formatDate(keyInfo.bidDeadline.value) }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('投标截止时间')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 是否有保证金</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.hasSecurityDeposit.value ? '是' : '否' }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('是否有保证金')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <!-- 保证金金额和形式 -->
                <div v-if="keyInfo.hasSecurityDeposit.value" class="space-y-3 pl-8">
                  <div class="flex items-center space-x-3">
                    <span class="text-sm text-gray-700 w-32">• 保证金金额</span>
                    <div class="flex-1 flex items-center">
                      <span class="text-sm text-gray-800">{{ keyInfo.securityDepositAmount.value || '未提取' }}</span>
                      <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('保证金金额')">
                        【引】
                      </span>
                    </div>
                  </div>
                  
                  <div class="flex items-center space-x-3">
                    <span class="text-sm text-gray-700 w-32">• 保证金形式</span>
                    <div class="flex-1 flex items-center">
                      <span class="text-sm text-gray-800">{{ keyInfo.securityDepositType.value || '未提取' }}</span>
                      <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('保证金形式')">
                        【引】
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-start space-x-3">
                  <span class="text-sm text-gray-700 w-32 mt-1">• 引入说明</span>
                  <div class="flex-1 flex items-start">
                    <span class="text-sm text-gray-800">各采购包均拟引入 【1】家合作伙伴，中选份额 【100%】，如多家，则需分别列出中选份额</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all mt-0.5" @click="showTenderOriginal('引入说明')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 技术分限制</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">技术分低于60分，不得参与报价分评审</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('技术分限制')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 价格评分方法</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">线性评分法</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('价格评分方法')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 应答文件的盖章或签字</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.needSignature.value ? '是' : '否' }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('应答文件的盖章或签字')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-700 w-32">• 是否有项目澄清会</span>
                  <div class="flex-1 flex items-center">
                    <span class="text-sm text-gray-800">{{ keyInfo.hasClarificationMeeting.value ? '是' : '否' }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('是否有项目澄清会')">
                      【引】
                    </span>
                  </div>
                </div>
                
                <!-- 项目澄清会时间和链接 -->
                <div v-if="keyInfo.hasClarificationMeeting.value" class="space-y-3 pl-8">
                  <div class="flex items-center space-x-3">
                    <span class="text-sm text-gray-700 w-32">• 项目澄清会时间</span>
                    <div class="flex-1 flex items-center">
                      <span class="text-sm text-gray-800">{{ formatDate(keyInfo.clarificationTime.value) }}</span>
                      <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('项目澄清会时间')">
                        【引】
                      </span>
                    </div>
                  </div>
                  
                  <div class="flex items-center space-x-3">
                    <span class="text-sm text-gray-700 w-32">• 项目澄清会链接</span>
                    <div class="flex-1 flex items-center">
                      <span class="text-sm text-gray-800">{{ keyInfo.clarificationLink.value }}</span>
                      <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all" @click="showTenderOriginal('项目澄清会链接')">
                        【引】
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-start space-x-3">
                  <span class="text-sm text-gray-700 w-32 mt-1">• 评分标准</span>
                  <div class="flex-1 flex items-start">
                    <span class="text-sm text-gray-800">{{ keyInfo.evaluationCriteria.value }}</span>
                    <span class="ml-2 px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all mt-0.5" @click="showTenderOriginal('评分标准')">
                      【引】
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 星标项Tab -->
              <div v-if="activeTab === 'star'" class="space-y-4">
                <!-- 星标项二级Tab -->
                <div class="border-b border-gray-200 mb-4">
                  <div class="flex space-x-2 overflow-x-auto pb-2">
                    <button 
                      v-for="(item, index) in starItems" 
                      :key="index"
                      class="px-3 py-2 text-xs font-medium whitespace-nowrap transition-all rounded-t-lg"
                      :class="activeStarItem === index ? 'bg-white border border-gray-200 border-b-transparent text-primary' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'"
                      @click="activeStarItem = index"
                    >
                      星标项 {{ index + 1 }}
                    </button>
                  </div>
                </div>
                
                <!-- 当前选中的星标项 -->
                <div v-if="starItems[activeStarItem]" class="border border-gray-100 rounded-lg p-4 bg-white hover:shadow-sm transition-all">
                  <div class="flex items-start space-x-3">
                    <div class="flex-1">
                      <div class="flex items-start space-x-2">
                        <span class="text-sm text-gray-800">{{ starItems[activeStarItem].name }}</span>
                        <span class="px-2 py-0.5 text-xs bg-blue-50 text-primary rounded-full border border-blue-100 cursor-pointer hover:bg-blue-100 transition-all mt-0.5" @click="showTenderOriginal('星标项', activeStarItem)">
                          【引】
                        </span>
                      </div>
                    </div>
                    <div class="flex space-x-2">
                      <button class="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all" :class="{ 'bg-success text-white border-success': starItems[activeStarItem].satisfied === true }" @click="starItems[activeStarItem].satisfied = true">
                        满足
                      </button>
                      <button class="px-3 py-1 text-xs border border-gray-200 rounded hover:bg-gray-50 transition-all" :class="{ 'bg-danger text-white border-danger': starItems[activeStarItem].satisfied === false }" @click="starItems[activeStarItem].satisfied = false">
                        不满足
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 知识库引用 -->
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">知识库引用</h3>
            <div v-if="knowledgeAssets.length === 0" class="text-sm text-gray-400 py-4 text-center">
              暂无可用知识库素材
            </div>
            <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                v-for="asset in knowledgeAssets"
                :key="asset.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-800 text-sm">{{ asset.title }}</h4>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">{{ asset.asset_type }}</span>
                </div>
                <p class="text-xs text-gray-500 mb-3 line-clamp-2">{{ asset.summary || '暂无摘要' }}</p>
                <div class="flex items-center justify-between">
                  <span class="text-xs text-gray-400">匹配度: {{ asset.score }}</span>
                  <button class="text-xs text-primary hover:underline">选择</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" v-if="uploadedFile && uploadStatus === '文件解析成功'">
            上一步
          </button>
          <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300" @click="nextStep" :disabled="!uploadedFile || uploadStatus !== '文件解析成功'">
            下一步
          </button>
        </div>
      </div>

      <!-- 回标文件框架步骤 -->
      <div v-else-if="currentStep === 1" class="space-y-6">
        <h3 class="text-lg font-semibold text-gray-800">回标文件框架</h3>

        <!-- 回标文件模版上传 -->
        <div class="border border-gray-200 rounded-lg p-4 mb-6">
          <h4 class="font-medium text-gray-800 mb-3">回标文件模版上传</h4>
          <div class="space-y-3">
            <!-- 上传区域 -->
            <div v-if="!uploadedTemplateFile" class="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-primary transition-all duration-300">
              <input type="file" ref="templateFileInput" class="hidden" accept=".zip,.rar,.7z" @change="handleTemplateUpload">
              <button type="button" class="w-full py-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="$refs.templateFileInput.click()">
                <div class="flex flex-col items-center">
                  <svg class="w-8 h-8 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                  </svg>
                  <span class="text-sm text-gray-600">点击上传回标文件模版压缩包</span>
                  <span class="text-xs text-gray-500 mt-1">支持 .zip, .rar, .7z 格式</span>
                </div>
              </button>
            </div>
            
            <!-- 已上传文件展示 -->
            <div v-else class="border-2 border-dashed rounded-lg p-4 text-center transition-all duration-300" :class="{
              'border-primary/30 bg-primary/5': templateUploadStatus === 'success',
              'border-red-300 bg-red-50': templateUploadStatus === 'error',
              'border-gray-200': !templateUploadStatus || templateUploadStatus === 'processing'
            }">
              <div class="flex items-center justify-center space-x-4">
                <div class="text-4xl">{{ templateUploadStatus === 'error' ? '❌' : '📦' }}</div>
                <div class="text-left">
                  <p class="font-medium text-gray-800">{{ uploadedTemplateFile.name }}</p>
                  <p class="text-sm text-gray-500">{{ formatFileSize(uploadedTemplateFile.size) }}</p>
                </div>
              </div>
              <button class="mt-3 px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="$refs.templateFileInput.click()">
                重新选择文件
              </button>
            </div>
            
            <!-- 上传状态 -->
            <div v-if="templateUploadStatus" class="flex items-center justify-between p-3 border border-gray-100 rounded-lg" :class="{
              'bg-green-50 border-green-200': templateUploadStatus === 'success',
              'bg-yellow-50 border-yellow-200': templateUploadStatus === 'processing',
              'bg-red-50 border-red-200': templateUploadStatus === 'error'
            }">
              <span class="text-sm" :class="{
                'text-green-700': templateUploadStatus === 'success',
                'text-yellow-700': templateUploadStatus === 'processing',
                'text-red-700': templateUploadStatus === 'error'
              }">
                {{ templateUploadMessage }}
              </span>
              <button v-if="templateUploadStatus === 'success' || templateUploadStatus === 'error'" class="text-xs text-primary" @click="clearTemplateUpload">
                重新上传
              </button>
            </div>
          </div>
        </div>

        <!-- 回标文件清单和预览 -->
        <div v-if="templateUploadStatus === 'success'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 左侧：回标文件清单 -->
          <div class="lg:col-span-2">
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex items-center justify-between">
                <h4 class="font-medium text-gray-800">回标文件清单</h4>
                <button
                  v-if="bidFiles.some((f: any) => f.selected)"
                  class="text-xs px-3 py-1.5 bg-primary text-white rounded hover:bg-primary/90 transition-all"
                  @click="openAssignModal(null)"
                >
                  批量设置负责人
                </button>
              </div>
              <div class="p-4 space-y-3">
                <div 
                  v-for="file in bidFiles" 
                  :key="file.id"
                  class="flex items-center p-3 border border-gray-100 rounded-lg hover:border-primary/30 transition-all cursor-pointer"
                  :class="{ 'bg-primary/5': selectedFile === file.id }"
                  @click="selectFile(file.id)"
                >
                  <button 
                    class="w-5 h-5 rounded border border-gray-300 flex items-center justify-center hover:bg-primary/10 transition-all mr-3 flex-shrink-0"
                    :class="{ 'bg-primary text-white': file.selected }"
                    @click.stop="file.selected = !file.selected"
                  >
                    {{ file.selected ? '✓' : '' }}
                  </button>
                  <div class="flex-1">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-800">{{ file.name }}</span>
                      <div class="flex items-center space-x-2">
                        <span
                          class="text-xs px-2 py-1 rounded-full"
                          :class="file.status === '已分配' ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-500'"
                        >
                          {{ file.status }}
                        </span>
                        <button 
                          class="text-xs text-primary hover:underline"
                          @click.stop="openAssignModal(file.id)"
                        >
                          指派负责人
                        </button>
                      </div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ file.description }}</p>
                    <div v-if="file.responsible" class="text-xs text-gray-500">
                      负责人：{{ file.responsible }}
                    </div>
                  </div>
                  <span class="ml-2 text-gray-400">{{ file.icon }}</span>
                </div>
              </div>
            </div>

            <!-- 自定义补充文件模版 -->
            <div class="mt-6 border border-dashed border-gray-200 rounded-lg p-4">
              <h4 class="font-medium text-gray-800 mb-3">自定义补充文件</h4>
              <div class="flex items-center space-x-3">
                <input 
                  type="text" 
                  v-model="newFile.name"
                  placeholder="文件名称"
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                >
                <input 
                  type="text" 
                  v-model="newFile.description"
                  placeholder="描述"
                  class="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
                >
                <button 
                  class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all"
                  @click="addCustomFile"
                >
                  添加
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧：文件预览 -->
          <div>
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <div class="bg-gray-50 border-b border-gray-200 px-4 py-3">
                <h4 class="font-medium text-gray-800">文件预览</h4>
              </div>
              <div class="p-4">
                <div v-if="selectedFileData" class="space-y-4">
                  <div>
                    <h5 class="font-medium text-gray-800">{{ selectedFileData.name }}</h5>
                    <p class="text-sm text-gray-500">{{ selectedFileData.description }}</p>
                  </div>
                  <div class="border border-gray-100 rounded-lg p-4 bg-gray-50 min-h-64 overflow-auto">
                    <div v-if="loadingPreview" class="text-center py-8 text-gray-400">
                      正在加载文件内容...
                    </div>
                    <pre v-else-if="templateFilePreview" class="text-sm text-gray-700 whitespace-pre-wrap">{{ templateFilePreview }}</pre>
                    <div v-else class="text-center py-8 text-gray-400">
                      该文件暂无可预览内容
                    </div>
                  </div>
                  <div class="flex justify-between">
                    <button class="px-3 py-1.5 border border-gray-200 text-gray-600 rounded hover:bg-gray-50 transition-all text-sm">
                      下载模板
                    </button>
                    <button class="px-3 py-1.5 bg-primary text-white rounded hover:bg-primary/90 transition-all text-sm">
                      编辑文件
                    </button>
                  </div>
                </div>
                <div v-else class="flex items-center justify-center h-64 text-gray-400">
                  <p>请选择一个文件进行预览</p>
                </div>
              </div>
            </div>

            <!-- 上传回标文件模板 -->
            <div class="mt-6 border border-dashed border-gray-200 rounded-lg p-4">
              <h4 class="font-medium text-gray-800 mb-3">上传回标文件模板</h4>
              <div class="text-center py-6">
                <div class="text-3xl mb-2">📁</div>
                <p class="text-gray-600 mb-3">点击或拖拽文件至此处上传</p>
                <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all">
                  选择文件
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="prevStep">
            上一步
          </button>
          <button 
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300"
            :disabled="templateUploadStatus !== 'success'"
            @click="nextStep"
          >
            下一步
          </button>
        </div>
      </div>

      <!-- 全文编写步骤 -->
      <div v-else-if="currentStep === 2" class="space-y-6">
        <h3 class="text-lg font-semibold text-gray-800">全文编写</h3>
        <p class="text-gray-600">生成全文，可自由编辑</p>

        <!-- 生成状态 -->
        <div v-if="isGenerating" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between mb-4">
            <h4 class="font-medium text-gray-800">生成回标文件</h4>
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">进行中</span>
          </div>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-600">生成进度</span>
                <span class="font-medium">{{ generationProgress }}%</span>
              </div>
              <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-primary rounded-full transition-all duration-300"
                  :style="{ width: generationProgress + '%' }"
                ></div>
              </div>
            </div>
            <div class="border border-gray-100 rounded-lg p-4 bg-gray-50">
              <h5 class="text-sm font-medium text-gray-800 mb-2">生成日志</h5>
              <div class="text-sm text-gray-600 space-y-2">
                <div v-for="(log, index) in generationLogs" :key="index" class="flex items-start">
                  <span class="mr-2 text-primary">•</span>
                  <span>{{ log }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 生成完成状态 -->
        <div v-else-if="hasGenerated" class="flex flex-col items-center justify-center py-12 space-y-4">
          <div class="text-4xl">✅</div>
          <p class="text-gray-600 font-medium">回标文件已生成</p>
          <button
            class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-lg font-medium"
            @click="regenerateDocx"
          >
            重新下载 Word 文档
          </button>
        </div>

        <!-- 生成按钮 -->
        <div v-else class="flex justify-center py-12">
          <button
            class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300 text-lg font-medium"
            @click="startGeneration"
          >
            开始生成回标文件
          </button>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3 mt-6">
          <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all duration-300" @click="prevStep">
            上一步
          </button>
          <button 
            class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all duration-300"
            :disabled="isGenerating"
            @click="nextStep"
          >
            完成
          </button>
        </div>
      </div>
    </div>

    <!-- 指派负责人弹窗 -->
    <div v-if="assignModalVisible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">{{ isBatchAssignMode ? '批量设置负责人' : '指派负责人' }}</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="assignModalVisible = false">
            ✕
          </button>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">文件</label>
          <p v-if="isBatchAssignMode" class="text-sm text-gray-600">已选中 {{ bidFiles.filter((f: any) => f.selected).length }} 个文件</p>
          <p v-else class="text-sm text-gray-600">{{ selectedFileForAssign?.name }}</p>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">负责人姓名</label>
          <input
            type="text"
            v-model="assignResponsibleName"
            placeholder="请输入负责人姓名"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary"
          >
        </div>
        <div class="flex justify-end space-x-3">
          <button class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg hover:bg-gray-50 transition-all" @click="assignModalVisible = false">
            取消
          </button>
          <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-all" @click="assignResponsible">
            确认
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createProject, uploadAndParseTender, getProject, getTenderSections, getTenderSectionDetail, listKnowledgeAssets, uploadBidTemplate, updateBidTemplateFiles, previewBidTemplateFile } from '../services/project'
import { createGenerationJob, exportGenerationJobDocx, getLatestJobByProject } from '../services/generation'

const router = useRouter()
const route = useRoute()
const currentStep = ref(0)
const steps = [
  { name: '解析文件', description: '解析招标文件信息' },
  { name: '回标文件框架', description: '展示回标文件清单，支持选择和预览' },
  { name: '全文编写', description: '生成全文，可自由编辑' }
]

// 上传文件状态
const uploadedFile = ref<any>(null)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const activeTab = ref('info')
const activeStarItem = ref(0)
const tenderFileInput = ref<HTMLInputElement | null>(null)

// 回标文件模版上传状态
const templateUploadStatus = ref('') // '', 'processing', 'success', 'error'
const templateUploadMessage = ref('')
const templateFileInput = ref<HTMLInputElement | null>(null)
const uploadedTemplateFile = ref<any>(null)

// 招标原文文件列表
const projectFileList = ref<any[]>([])
const selectedSourceFile = ref('')
const selectedFileContent = ref('')
const fileContentMap = ref<Record<string, string>>({})

const loadSectionDetails = async (sections: any[]) => {
  if (!currentProjectId.value) return sections
  return Promise.all(sections.map(async (section: any) => {
    if (section.content !== undefined) return section
    try {
      const detail = await getTenderSectionDetail(currentProjectId.value, section.id)
      return { ...section, content: detail.content || '' }
    } catch (e) {
      console.error('Failed to load section detail:', section.id, e)
      return { ...section, content: '' }
    }
  }))
}

const onSourceFileChange = async () => {
  if (!currentProjectId.value || !selectedSourceFile.value) return
  
  // 先从缓存中查找
  if (fileContentMap.value[selectedSourceFile.value]) {
    selectedFileContent.value = fileContentMap.value[selectedSourceFile.value]
    return
  }
  
  try {
    // 从sections中查找对应文件的内容
    const sections = await getTenderSections(currentProjectId.value)
    const fileSections = await loadSectionDetails(sections.filter((s: any) => s.source_file === selectedSourceFile.value))
    if (fileSections.length > 0) {
      const content = fileSections.map((s: any) => `【${s.section_name}】\n${s.content || ''}`).join('\n\n')
      selectedFileContent.value = content
      fileContentMap.value[selectedSourceFile.value] = content
    } else {
      selectedFileContent.value = '该文件暂无解析内容'
    }
  } catch (e) {
    console.error('Failed to load file content:', e)
    selectedFileContent.value = '加载文件内容失败'
  }
}

// 基础信息表单
const basicInfo = ref({
  companyName: '',
  agent: '',
  phone: '',
  email: '',
  address: '',
  bankInfo: ''
})

// 表单验证错误
const formErrors = ref({
  companyName: '',
  agent: '',
  phone: '',
  email: '',
  address: '',
  bankInfo: ''
})

const currentProjectId = ref<string | null>(null)
const currentProjectName = ref<string>('')

// 关键信息
const keyInfo = ref<Record<string, { checked: boolean; value: any }>>({
  projectName: { checked: false, value: '' },
  bidType: { checked: false, value: '' },
  budget: { checked: false, value: '' },
  deadline: { checked: false, value: '' },
  startTime: { checked: false, value: '' },
  endTime: { checked: false, value: '' },
  bidDeadline: { checked: false, value: '' },
  hasSecurityDeposit: { checked: false, value: false },
  securityDepositAmount: { checked: false, value: '' },
  securityDepositType: { checked: false, value: '' },
  partnerIntroduction: { checked: false, value: '' },
  needSignature: { checked: false, value: false },
  clarificationTime: { checked: false, value: '' },
  clarificationLink: { checked: false, value: '' },
  hasClarificationMeeting: { checked: false, value: false },
  evaluationCriteria: { checked: false, value: '' },
  techScoreLimit: { checked: false, value: false },
  starItems: { checked: false, value: '' }
})

// 星标项列表
const starItems = ref<any[]>([])

// 知识库引用
const knowledgeAssets = ref<KnowledgeAsset[]>([])

// 回标文件清单
const bidFiles = ref<any[]>([])

// 当前选中的文件
const selectedFile = ref(1)

// 自定义文件
const newFile = ref({
  name: '',
  description: ''
})

// 当前显示的引用内容
const currentReference = ref({
  filename: '',
  originalText: '',
  visible: false
})

// 添加自定义文件
const addCustomFile = () => {
  if (newFile.value.name) {
    bidFiles.value.push({
      id: bidFiles.value.length + 1,
      name: newFile.value.name,
      description: newFile.value.description || '自定义文件',
      status: '自定义',
      selected: false,
      icon: '📄',
      preview: ''
    })
    newFile.value.name = ''
    newFile.value.description = ''
  }
}

// 指派负责人
const assignModalVisible = ref(false)
const selectedFileForAssign = ref<any>(null)
const assignResponsibleName = ref('')
const isBatchAssignMode = ref(false)

const openAssignModal = (fileId: number | null) => {
  isBatchAssignMode.value = fileId === null
  if (fileId !== null) {
    selectedFileForAssign.value = bidFiles.value.find((file: any) => file.id === fileId)
    assignResponsibleName.value = selectedFileForAssign.value?.responsible || ''
  } else {
    selectedFileForAssign.value = null
    assignResponsibleName.value = ''
  }
  assignModalVisible.value = true
}

const assignResponsible = async () => {
  if (!assignResponsibleName.value) return

  if (isBatchAssignMode.value) {
    bidFiles.value.forEach((file: any) => {
      if (file.selected) {
        file.responsible = assignResponsibleName.value
        file.status = '已分配'
      }
    })
  } else if (selectedFileForAssign.value) {
    const file = bidFiles.value.find((file: any) => file.id === selectedFileForAssign.value.id)
    if (file) {
      file.responsible = assignResponsibleName.value
      file.status = '已分配'
    }
  }

  // 保存到后端
  if (currentProjectId.value) {
    try {
      await updateBidTemplateFiles(currentProjectId.value, bidFiles.value)
    } catch (e) {
      console.error('Failed to save template files:', e)
    }
  }

  assignModalVisible.value = false
}

// 处理文件选择
const onFileSelected = async (event: any) => {
  const file = event.target.files[0]
  if (!file) return
  
  uploadedFile.value = {
    name: file.name,
    size: file.size
  }
  uploadProgress.value = 10
  uploadStatus.value = '解析中'

  try {
    // 1. 如果还没有项目，先创建一个基础项目
    if (!currentProjectId.value) {
      const projectName = file.name.split('.')[0] || '新项目'
      const proj = await createProject({
        name: projectName,
        owner: '当前用户',
        status: '解析中',
      })
      currentProjectId.value = proj.id
      currentProjectName.value = projectName
    }
    
    uploadProgress.value = 40
    
    // 2. 调用真实的解析接口
    const res = await uploadAndParseTender(currentProjectId.value, file)
    
    let sections: any[] = []
    
    if (res.status === 'processing') {
      uploadStatus.value = '正在后台解析（可能需要1-3分钟），请耐心等待...'
      
      const maxRetries = 120 // 最多等待6分钟
      let retries = 0
      
      while (retries < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        const proj = await getProject(currentProjectId.value)
        if (proj.status === '解析失败') {
          throw new Error('后台解析任务失败，请检查文件内容或重试')
        }
        
        if (proj.status === '解析完成') {
          sections = await getTenderSections(currentProjectId.value)
          // Populate projectFileList from the project's file_list
          if (proj.file_list && Array.isArray(proj.file_list)) {
            projectFileList.value = proj.file_list
            if (proj.file_list.length > 0) {
              selectedSourceFile.value = proj.file_list[0].name
              // Auto-load first file content
              const firstFileSections = await loadSectionDetails(sections.filter((s: any) => s.source_file === proj.file_list[0].name))
            if (firstFileSections.length > 0) {
              selectedFileContent.value = firstFileSections.map((s: any) => `【${s.section_name}】\n${s.content || ''}`).join('\n\n')
              fileContentMap.value[proj.file_list[0].name] = selectedFileContent.value
            }
            }
          }
          break
        }
        
        retries++
        uploadProgress.value = Math.min(40 + Math.floor(retries * 0.5), 95)
      }
      
      if (retries >= maxRetries) {
        throw new Error('解析超时，请稍后在项目列表中查看')
      }
    } else {
      // 兼容可能同步返回的旧逻辑
      sections = res
    }
    
    uploadProgress.value = 100
    uploadStatus.value = '文件解析成功'
    
    // 从后端返回的 extracted_fields 填充基本信息
    console.log('Parsed sections:', sections)
    
    // Fetch full project with extracted_fields
    const fullProject = await getProject(currentProjectId.value)
    if (fullProject.extracted_fields && Array.isArray(fullProject.extracted_fields)) {
      const fieldMap: Record<string, string> = {}
      for (const f of fullProject.extracted_fields) {
        fieldMap[f.label] = f.value
      }
      // 基本信息
      keyInfo.value.projectName.value = fieldMap['项目名称'] || ''
      keyInfo.value.projectName.checked = !!fieldMap['项目名称']
      keyInfo.value.bidType.value = fieldMap['标书类型'] || ''
      keyInfo.value.bidType.checked = !!fieldMap['标书类型']
      keyInfo.value.budget.value = fieldMap['预算金额'] || ''
      keyInfo.value.budget.checked = !!fieldMap['预算金额']
      keyInfo.value.startTime.value = fieldMap['标书起始时间'] || ''
      keyInfo.value.startTime.checked = !!fieldMap['标书起始时间']
      keyInfo.value.endTime.value = fieldMap['标书结束时间'] || ''
      keyInfo.value.endTime.checked = !!fieldMap['标书结束时间']
      keyInfo.value.bidDeadline.value = fieldMap['投标截止时间'] || ''
      keyInfo.value.bidDeadline.checked = !!fieldMap['投标截止时间']
      // 保证金信息
      const hasDeposit = fieldMap['是否有保证金']
      keyInfo.value.hasSecurityDeposit.value = hasDeposit === '是'
      keyInfo.value.hasSecurityDeposit.checked = !!hasDeposit
      keyInfo.value.securityDepositAmount.value = fieldMap['保证金金额'] || ''
      keyInfo.value.securityDepositAmount.checked = !!fieldMap['保证金金额']
      keyInfo.value.securityDepositType.value = fieldMap['保证金形式'] || ''
      keyInfo.value.securityDepositType.checked = !!fieldMap['保证金形式']
      // 其他信息
      keyInfo.value.needSignature.value = fieldMap['是否需要签字盖章'] === '是'
      keyInfo.value.needSignature.checked = !!fieldMap['是否需要签字盖章']
      const hasClarification = fieldMap['是否有项目澄清会']
      keyInfo.value.hasClarificationMeeting.value = hasClarification === '是'
      keyInfo.value.hasClarificationMeeting.checked = !!hasClarification
      keyInfo.value.clarificationTime.value = fieldMap['项目澄清会时间'] || ''
      keyInfo.value.clarificationTime.checked = !!fieldMap['项目澄清会时间']
      keyInfo.value.clarificationLink.value = fieldMap['项目澄清会链接'] || ''
      keyInfo.value.clarificationLink.checked = !!fieldMap['项目澄清会链接']
      keyInfo.value.evaluationCriteria.value = fieldMap['评分重点'] || ''
      keyInfo.value.evaluationCriteria.checked = !!fieldMap['评分重点']
      keyInfo.value.starItems.value = fieldMap['技术要求'] || ''
      keyInfo.value.starItems.checked = !!fieldMap['技术要求']
    }
    
    // Populate star items from sections with is_star_item=true
    starItems.value = []
    let starId = 1
    const starSections = await loadSectionDetails(sections.filter((s: any) => s.is_star_item))
    starSections.forEach((s: any) => {
      starItems.value.push({
        id: starId++,
        name: s.section_name,
        type: s.section_type === '评审' ? '评审规则' : '技术规范',
        source: s.source_file,
        status: '需关注',
        content: s.content || ''
      })
    })

  } catch (e: any) {
    console.error(e)
    uploadStatus.value = 'error'
    uploadProgress.value = 0
    formErrors.value.companyName = e.message || '解析失败，请检查文件后重试'
  }
}

// 上传回标文件模版
const handleTemplateUpload = async (event: any) => {
  const file = event.target.files[0]
  if (!file || !currentProjectId.value) return

  uploadedTemplateFile.value = file
  templateUploadStatus.value = 'processing'
  templateUploadMessage.value = '正在上传并解析回标文件模版...'

  try {
    const res = await uploadBidTemplate(currentProjectId.value, file)
    templateUploadStatus.value = 'success'
    templateUploadMessage.value = res.message

    if (res.files && res.files.length > 0) {
      const files: any[] = []
      let fileId = 1
      for (const f of res.files) {
        files.push({
          id: fileId++,
          name: f.name,
          description: f.path || '模板文件',
          status: '待分配',
          selected: true,
          icon: f.icon || '📄',
          preview: '',
          path: f.path,
        })
      }
      bidFiles.value = files
      // Auto-select first file and load preview
      if (files.length > 0) {
        selectedFile.value = files[0].id
        await loadFilePreview(files[0])
      }
    }
  } catch (e: any) {
    templateUploadStatus.value = 'error'
    templateUploadMessage.value = e.message || '上传失败'
  }
}

// 清除模板上传状态
const clearTemplateUpload = () => {
  templateUploadStatus.value = ''
  templateUploadMessage.value = ''
  uploadedTemplateFile.value = null
  if (templateFileInput.value) {
    templateFileInput.value.value = ''
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const normalized = String(dateString).trim()
  if (!normalized || normalized === '待补充') return ''
  const date = new Date(normalized.replace(/年|月/g, '-').replace(/日/g, '').replace(/时/g, ':').replace(/分/g, ''))
  if (Number.isNaN(date.getTime())) return normalized
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}年${month}月${day}日 ${hours}:${minutes}`
}

// 重新上传文件
const reuploadFile = () => {
  uploadedFile.value = null
  uploadProgress.value = 0
  uploadStatus.value = ''
}

// 展示对应招标原文
const showTenderOriginal = (key: string, index: number | null = null) => {
  console.log('展示招标原文:', key, index)
  if (uploadedFile.value) {
    let filename = '技术规格书.docx'
    let originalText = ''
    if (key === '星标项' && index !== null && starItems.value[index]) {
      filename = starItems.value[index].source
      originalText = starItems.value[index].name
    } else {
      originalText = `引用内容：${key}`
    }
    currentReference.value = {
      filename: filename,
      originalText: originalText,
      visible: true
    }
    setTimeout(() => {
      const referenceElement = document.querySelector('.bg-blue-50.border-l-4')
      if (referenceElement) {
        referenceElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }, 100)
  }
}

// 选中文件数据
const selectedFileData = computed(() => {
  return bidFiles.value.find((file: any) => file.id === selectedFile.value)
})

// 文件预览内容
const templateFilePreview = ref('')
const loadingPreview = ref(false)

// 加载文件预览
const loadFilePreview = async (file: any) => {
  if (!currentProjectId.value || !file?.path) {
    templateFilePreview.value = ''
    return
  }
  
  loadingPreview.value = true
  try {
    const data = await previewBidTemplateFile(currentProjectId.value, file.path)
    if (data.status === 'success') {
      templateFilePreview.value = data.content
    } else {
      templateFilePreview.value = '无法加载文件内容'
    }
  } catch (e) {
    console.error('Failed to load file preview:', e)
    templateFilePreview.value = '加载预览失败'
  } finally {
    loadingPreview.value = false
  }
}

// 重写selectFile以加载预览
const selectFile = async (id: number) => {
  selectedFile.value = id
  const file = bidFiles.value.find((f: any) => f.id === id)
  if (file) {
    await loadFilePreview(file)
  }
}

// 生成状态
const isGenerating = ref(false)
const hasGenerated = ref(false)
const generationProgress = ref(0)
const generationLogs = ref<string[]>([])

// 开始生成
const startGeneration = async () => {
  if (!currentProjectId.value) {
    alert('请先创建项目')
    return
  }
  isGenerating.value = true
  generationProgress.value = 0
  generationLogs.value = ['正在创建生成任务...']

  try {
    const job = await createGenerationJob(currentProjectId.value, currentProjectName.value || '未命名项目')
    generationLogs.value.push(`任务已创建: ${job.id}`)
    generationProgress.value = 30

    let targetJob = job
    // 如果返回的 job 已经是 completed，跳过轮询直接导出
    if (job.status === 'completed') {
      generationLogs.value.push('生成任务已完成')
      generationProgress.value = 60
    } else {
      generationLogs.value.push('正在生成回标文件内容...')
      generationProgress.value = 60

      let retries = 0
      while (retries < 60) {
        await new Promise(resolve => setTimeout(resolve, 3000))
        targetJob = await getLatestJobByProject(currentProjectId.value)
        if (targetJob && targetJob.status === 'completed') {
          break
        }
        if (targetJob && targetJob.status === 'failed') {
          throw new Error('生成任务失败')
        }
        retries++
        generationProgress.value = Math.min(60 + Math.floor(retries * 0.5), 95)
      }

      if (!targetJob || targetJob.status !== 'completed') {
        throw new Error('生成任务超时')
      }
    }

    generationProgress.value = 95
    generationLogs.value.push('正在导出Word文档...')

    const blob = await exportGenerationJobDocx(targetJob.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `回标文件_${currentProjectName.value || '项目'}.docx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)

    generationProgress.value = 100
    generationLogs.value.push('回标文件生成完成！Word文档已下载')
    hasGenerated.value = true

    setTimeout(() => {
      isGenerating.value = false
      alert('回标文件生成完成！Word文档已下载')
    }, 1000)
  } catch (e: any) {
    console.error(e)
    generationLogs.value.push(`错误: ${e.message}`)
    isGenerating.value = false
    alert(`生成失败: ${e.message}`)
  }
}

// 重新下载已生成的文档
const regenerateDocx = async () => {
  if (!currentProjectId.value) return
  try {
    const latestJob = await getLatestJobByProject(currentProjectId.value)
    if (!latestJob) {
      alert('未找到生成记录')
      return
    }
    const blob = await exportGenerationJobDocx(latestJob.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `回标文件_${currentProjectName.value || '项目'}.docx`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (e: any) {
    console.error(e)
    alert(`下载失败: ${e.message}`)
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 返回上一页
const goBack = () => {
  router.push('/tender-list')
}

// 验证基础信息表单
const validateBasicInfo = () => {
  let isValid = true
  formErrors.value = {
    companyName: '',
    agent: '',
    phone: '',
    email: '',
    address: '',
    bankInfo: ''
  }

  if (!basicInfo.value.companyName) {
    formErrors.value.companyName = '请输入应标公司'
    isValid = false
  }
  if (!basicInfo.value.agent) {
    formErrors.value.agent = '请输入代理人'
    isValid = false
  }
  if (!basicInfo.value.phone) {
    formErrors.value.phone = '请输入电话'
    isValid = false
  }
  if (!basicInfo.value.email) {
    formErrors.value.email = '请输入邮箱'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(basicInfo.value.email)) {
    formErrors.value.email = '请输入有效的邮箱地址'
    isValid = false
  }
  if (!basicInfo.value.address) {
    formErrors.value.address = '请输入公司地址'
    isValid = false
  }
  if (!basicInfo.value.bankInfo) {
    formErrors.value.bankInfo = '请输入开户银行信息'
    isValid = false
  }

  return isValid
}

// 验证所有问卷是否都已指派负责人
const validateResponsibleAssignments = () => {
  const selectedFiles = bidFiles.value.filter((file: any) => file.selected)
  return selectedFiles.every((file: any) => file.responsible)
}

// 下一步
const nextStep = () => {
  if (currentStep.value < steps.length - 1) {
    if (currentStep.value === 0) {
      if (!uploadedFile.value || uploadStatus.value !== '文件解析成功') {
        alert('请先上传文件并等待解析完成')
        return
      }
      const isBasicInfoValid = validateBasicInfo()
      if (!isBasicInfoValid) {
        alert('请填写所有必填的基础信息')
        return
      }
    } else if (currentStep.value === 1) {
      const isAllAssigned = validateResponsibleAssignments()
      if (!isAllAssigned) {
        alert('请为所有选中的文件指派负责人')
        return
      }
    }
    currentStep.value++
  }
}

onMounted(async () => {
  try {
    knowledgeAssets.value = await listKnowledgeAssets()
  } catch (e) {
    console.error('Failed to load knowledge assets:', e)
  }

  const projectId = route.params.projectId as string
  if (projectId) {
    try {
      const project = await getProject(projectId)
      if (project) {
        currentProjectId.value = project.id
        currentProjectName.value = project.name
        uploadedFile.value = { name: project.name, size: 0 }

        if (project.extracted_fields && Array.isArray(project.extracted_fields) && project.extracted_fields.length > 0) {
          const fieldMap: Record<string, string> = {}
          for (const f of project.extracted_fields) {
            fieldMap[f.label] = f.value
          }
          keyInfo.value.projectName.value = fieldMap['项目名称'] || project.name
          keyInfo.value.projectName.checked = true
          keyInfo.value.bidType.value = fieldMap['标书类型'] || ''
          keyInfo.value.bidType.checked = !!fieldMap['标书类型']
          keyInfo.value.budget.value = fieldMap['预算金额'] || ''
          keyInfo.value.budget.checked = !!fieldMap['预算金额']
          keyInfo.value.startTime.value = fieldMap['标书起始时间'] || ''
          keyInfo.value.startTime.checked = !!fieldMap['标书起始时间']
          keyInfo.value.endTime.value = fieldMap['标书结束时间'] || ''
          keyInfo.value.endTime.checked = !!fieldMap['标书结束时间']
          keyInfo.value.bidDeadline.value = fieldMap['投标截止时间'] || ''
          keyInfo.value.bidDeadline.checked = !!fieldMap['投标截止时间']
          const hasDeposit = fieldMap['是否有保证金']
          keyInfo.value.hasSecurityDeposit.value = hasDeposit === '是'
          keyInfo.value.hasSecurityDeposit.checked = !!hasDeposit
          keyInfo.value.securityDepositAmount.value = fieldMap['保证金金额'] || ''
          keyInfo.value.securityDepositAmount.checked = !!fieldMap['保证金金额']
          keyInfo.value.securityDepositType.value = fieldMap['保证金形式'] || ''
          keyInfo.value.securityDepositType.checked = !!fieldMap['保证金形式']
          keyInfo.value.needSignature.value = fieldMap['是否需要签字盖章'] === '是'
          keyInfo.value.needSignature.checked = !!fieldMap['是否需要签字盖章']
          const hasClarification = fieldMap['是否有项目澄清会']
          keyInfo.value.hasClarificationMeeting.value = hasClarification === '是'
          keyInfo.value.hasClarificationMeeting.checked = !!hasClarification
          keyInfo.value.clarificationTime.value = fieldMap['项目澄清会时间'] || ''
          keyInfo.value.clarificationTime.checked = !!fieldMap['项目澄清会时间']
          keyInfo.value.clarificationLink.value = fieldMap['项目澄清会链接'] || ''
          keyInfo.value.clarificationLink.checked = !!fieldMap['项目澄清会链接']
          keyInfo.value.evaluationCriteria.value = fieldMap['评分重点'] || ''
          keyInfo.value.evaluationCriteria.checked = !!fieldMap['评分重点']
          keyInfo.value.starItems.value = fieldMap['技术要求'] || ''
          keyInfo.value.starItems.checked = !!fieldMap['技术要求']
        } else {
          keyInfo.value.projectName.value = project.name || ''
          keyInfo.value.projectName.checked = !!project.name
          keyInfo.value.budget.value = project.amount || ''
          keyInfo.value.budget.checked = !!project.amount
          keyInfo.value.bidDeadline.value = project.deadline || ''
          keyInfo.value.bidDeadline.checked = !!project.deadline
        }

        if (project.bidding_company) basicInfo.value.companyName = project.bidding_company
        if (project.agent_name) basicInfo.value.agent = project.agent_name
        if (project.agent_phone) basicInfo.value.phone = project.agent_phone
        if (project.agent_email) basicInfo.value.email = project.agent_email
        if (project.company_address) basicInfo.value.address = project.company_address
        if (project.bank_name) basicInfo.value.bankInfo = project.bank_name

        if (project.node_status && project.node_status.generation === 'completed') {
          hasGenerated.value = true
          currentStep.value = 2
        } else if (project.status === '解析完成' || project.parse_status === '已解析') {
          uploadStatus.value = '文件解析成功'
          const sections = await getTenderSections(projectId)
          if (sections && sections.length > 0) {
            starItems.value = []
            let starId = 1
            const starSections = await loadSectionDetails(sections.filter((s: any) => s.is_star_item))
            starSections.forEach((s: any) => {
              starItems.value.push({
                id: starId++,
                name: s.section_name,
                type: s.section_type === '评审' ? '评审规则' : '技术规范',
                source: s.source_file,
                status: '需关注',
                content: s.content || ''
              })
            })
          }
          if (project.file_list && Array.isArray(project.file_list) && project.file_list.length > 0) {
            projectFileList.value = project.file_list
            selectedSourceFile.value = project.file_list[0].name
            const firstFileSections = await loadSectionDetails(sections.filter((s: any) => s.source_file === project.file_list[0].name))
            if (firstFileSections.length > 0) {
              selectedFileContent.value = firstFileSections.map((s: any) => `【${s.section_name}】\n${s.content || ''}`).join('\n\n')
              fileContentMap.value[project.file_list[0].name] = selectedFileContent.value
            }
          }
          currentStep.value = project.bid_template_files?.length > 0 ? 1 : 0
        } else if (project.status === '解析失败' || project.parse_status === '解析失败') {
          uploadStatus.value = 'error'
          formErrors.value.companyName = '解析失败，请重新上传招标文件'
          currentStep.value = 0
        } else if (project.status === '解析中' || project.parse_status === '解析中') {
          uploadStatus.value = '解析中'
          currentStep.value = 0
        } else {
          currentStep.value = 0
        }

        if (project.bid_template_files && Array.isArray(project.bid_template_files) && project.bid_template_files.length > 0) {
          templateUploadStatus.value = 'success'
          templateUploadMessage.value = '模板已上传'
          bidFiles.value = project.bid_template_files.map((f: any, i: number) => ({
            id: i + 1,
            name: f.name,
            description: f.path || '模板文件',
            status: '待分配',
            selected: true,
            icon: f.icon || '📄',
            preview: '',
          }))
          if (currentStep.value < 1) currentStep.value = 1
        }
      }
    } catch (e) {
      console.error('Failed to load project:', e)
    }
  }
})
</script>

<style scoped>
</style>

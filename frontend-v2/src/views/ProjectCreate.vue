<template>
  <div class="fade-in h-full flex flex-col">
    <!-- 顶部状态栏 -->
    <div class="bg-white border-b border-gray-200 mb-6">
      <div class="flex justify-between items-center px-4 py-3">
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <span class="text-sm text-gray-500 mr-2">当前项目:</span>
            <span class="text-sm font-medium">智能城市项目</span>
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
      <h2 class="text-2xl font-bold text-gray-800">新增项目</h2>
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
            'bg-yellow-50 border-yellow-200': uploadStatus === '解析中',
            'bg-red-50 border-red-200': uploadStatus === 'error'
          }">
            <span class="text-sm" :class="{
              'text-green-700': uploadStatus === '文件解析成功',
              'text-yellow-700': uploadStatus === '解析中',
              'text-red-700': uploadStatus === 'error'
            }">
              {{ uploadStatus === '文件解析成功' ? '文件解析成功，已提取关键信息' : uploadStatus }}
            </span>
            <button v-if="uploadStatus === '文件解析成功'" class="text-xs text-primary" @click="reuploadFile">
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
                  <select class="text-sm border-none bg-transparent focus:outline-none">
                    <option>技术规格书.docx</option>
                    <option>商务要求.docx</option>
                    <option>附件.zip</option>
                  </select>
                </div>
                <div class="p-4 max-h-96 overflow-auto bg-gray-50">
                  <pre class="text-sm text-gray-700 whitespace-pre-wrap">
3.3 接口日志
接口日志应结合所有与外部系统的交互日志，包括平台内部编排各环节接口日志。接口日志具备信息完整、可追溯、可分析。

4.4 系统安全要求
系统应具有较高的可靠性，防病毒软件应具备全面查杀病毒、查杀准确度高无误、管理方便、病毒特征码自动更新、安装简单的特点。
系统具有入侵检测的功能，监控可疑的连接、非法访问等，采取的措施包括实时报警、自动阻断通信连接或执行用户自定义的安全策略。
                  </pre>
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
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="border border-gray-200 rounded-lg p-4">
                <h4 class="font-medium text-gray-800 mb-3">历史标书</h4>
                <div class="space-y-2">
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">城市交通系统标书</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">企业数字化转型标书</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">智慧城市安防标书</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                </div>
              </div>
              
              <div class="border border-gray-200 rounded-lg p-4">
                <h4 class="font-medium text-gray-800 mb-3">人员信息</h4>
                <div class="space-y-2">
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">张三 - 技术总监</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">李四 - 项目经理</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">王五 - 商务经理</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                </div>
              </div>
              
              <div class="border border-gray-200 rounded-lg p-4">
                <h4 class="font-medium text-gray-800 mb-3">公司资质</h4>
                <div class="space-y-2">
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">ISO9001认证</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">软件企业认证</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
                  <div class="flex items-center justify-between p-2 hover:bg-gray-50 rounded cursor-pointer transition-all">
                    <span class="text-sm text-gray-700">系统集成资质</span>
                    <button class="text-xs text-primary">选择</button>
                  </div>
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
            <div v-else class="border-2 border-dashed border-primary/30 rounded-lg p-4 text-center bg-primary/5 transition-all duration-300">
              <div class="flex items-center justify-center space-x-4">
                <div class="text-4xl">📦</div>
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
              <button v-if="templateUploadStatus === 'success'" class="text-xs text-primary" @click="clearTemplateUpload">
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
              <div class="bg-gray-50 border-b border-gray-200 px-4 py-3">
                <h4 class="font-medium text-gray-800">回标文件清单</h4>
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
                          :class="file.status === '解析完成' ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-500'"
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
                  <div class="border border-gray-100 rounded-lg p-4 bg-gray-50 min-h-64 flex items-center justify-center">
                    <div class="text-center">
                      <div class="text-4xl mb-2">{{ selectedFileData.icon }}</div>
                      <p class="text-gray-500">{{ selectedFileData.preview }}</p>
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
          <h3 class="text-lg font-semibold text-gray-800">指派负责人</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="assignModalVisible = false">
            ✕
          </button>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">文件</label>
          <p class="text-sm text-gray-600">{{ selectedFileForAssign?.name }}</p>
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
import { useRouter } from 'vue-router'
import { createProject, uploadAndParseTender, getProject, getTenderSections } from '../services/project'
import type { Project } from '../types'

const router = useRouter()
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

// 选择文件
const selectFile = (id: number) => {
  selectedFile.value = id
}

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

const openAssignModal = (fileId: number) => {
  selectedFileForAssign.value = bidFiles.value.find((file: any) => file.id === fileId)
  assignResponsibleName.value = selectedFileForAssign.value?.responsible || ''
  assignModalVisible.value = true
}

const assignResponsible = () => {
  if (selectedFileForAssign.value && assignResponsibleName.value) {
    const file = bidFiles.value.find((file: any) => file.id === selectedFileForAssign.value.id)
    if (file) {
      file.responsible = assignResponsibleName.value
    }
    assignModalVisible.value = false
  }
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
      const proj = await createProject({
        name: file.name.split('.')[0] || '新项目',
        owner: '当前用户',
        status: '解析中',
      })
      currentProjectId.value = proj.id
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
    
    // 把后端返回的内容塞到基本信息里，暂时放在待确认状态
    console.log('Parsed sections:', sections)
    
    // 假设后端返回了 sections，我们从中找出特定的内容填充表单
    // (这部分也可以通过后端再提供一个项目基本信息的聚合接口)
    const bizSections = sections.filter((s: any) => s.section_type === '商务' || s.section_type === '评审')
    
    // 我们把解析到的 "评分重点" 塞到 starItems 里用于展示
    const evalRule = sections.find((s: any) => s.section_name === '评分规则解析')
    if (evalRule) {
      starItems.value.push({
        id: 1,
        name: '评分重点',
        type: '评审规则',
        source: evalRule.source_file,
        status: '需关注',
        content: evalRule.content
      })
    }
    
    // 技术要求
    const techReq = sections.find((s: any) => s.section_name === '技术要求')
    if (techReq) {
      starItems.value.push({
        id: 2,
        name: '核心技术要求',
        type: '技术规范',
        source: techReq.source_file,
        status: '需关注',
        content: techReq.content
      })
    }

    // 初始化回标文件清单
    const files: any[] = []
    let fileId = 1
    sections.forEach((s: any) => {
      // 如果 section_type 存在，我们把它当成一个需要编制的文件（简单模拟）
      if (s.section_type === '商务' || s.section_type === '技术') {
        files.push({
          id: fileId++,
          name: s.section_name,
          description: `来源: ${s.source_file}`,
          status: '待分配',
          selected: true,
          icon: s.section_type === '商务' ? '📄' : '💻',
          preview: (s.content || '').substring(0, 100) + '...',
          original: s
        })
      }
    })
    
    // 去重文件
    const uniqueFiles: any[] = []
    const seenNames = new Set()
    for (const f of files) {
      if (!seenNames.has(f.name)) {
        seenNames.add(f.name)
        uniqueFiles.push(f)
      }
    }
    bidFiles.value = uniqueFiles

  } catch (e: any) {
    console.error(e)
    uploadStatus.value = 'error'
    uploadProgress.value = 0
    formErrors.value.companyName = e.message || '解析失败'
  }
}

// 上传回标文件模版
const handleTemplateUpload = (event: any) => {
  const file = event.target.files[0]
  if (file) {
    uploadedTemplateFile.value = file
    templateUploadStatus.value = 'processing'
    templateUploadMessage.value = '正在上传并解析回标文件模版...'

    // 模拟文件上传和AI识别
    setTimeout(() => {
      templateUploadStatus.value = 'success'
      templateUploadMessage.value = '回标文件模版上传成功，AI已识别并生成回标文件清单'
    }, 3000)
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
  const date = new Date(dateString)
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

// 生成状态
const isGenerating = ref(false)
const generationProgress = ref(0)
const generationLogs = ref<string[]>([])

// 开始生成
const startGeneration = () => {
  isGenerating.value = true
  generationProgress.value = 0

  // 模拟生成过程
  const interval = setInterval(() => {
    generationProgress.value += 5
    if (generationProgress.value >= 100) {
      clearInterval(interval)
      setTimeout(() => {
        isGenerating.value = false
        alert('回标文件生成完成！项目状态已更新为进行中')
        router.push('/bid-list')
      }, 1000)
    }
  }, 200)
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
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
  // 如果需要加载已有项目列表
})
</script>

<style scoped>
</style>

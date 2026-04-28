<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
    <h3 class="font-semibold text-gray-800 mb-4 flex items-center">
      <span class="mr-2">🎮</span>
      博弈沙盘
      <span class="ml-2 text-xs text-gray-400 font-normal">多智能体招投标博弈模拟</span>
    </h3>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div class="space-y-4">
        <div class="p-3 bg-gray-50 rounded">
          <p class="text-sm font-medium text-gray-700 mb-2">场景参数</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">预算(元)</span>
              <input v-model.number="scenario.budget" type="number" class="w-32 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">评分方法</span>
              <select v-model="scenario.scoring_method" class="px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="linear">线性评分法</option>
                <option value="vertexRandomK">顶点中间值法(K随机)</option>
                <option value="vertexFixedK">顶点中间值法(K固定)</option>
              </select>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">技术分权重</span>
              <input v-model.number="scenario.tech_weight" type="number" min="0" max="1" step="0.1" class="w-16 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">模拟次数</span>
              <input v-model.number="simConfig.n_simulations" type="number" min="100" max="10000" step="100" class="w-20 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">模拟模式</span>
              <select v-model="simConfig.method" class="px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="monte_carlo">蒙特卡洛</option>
                <option value="bayesian">贝叶斯更新</option>
                <option value="iterative">多轮迭代</option>
                <option value="ab_test">A/B测试</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="isIterativeMode" class="p-3 bg-gray-50 rounded border border-gray-100">
          <p class="text-sm font-medium text-gray-700 mb-2">迭代参数</p>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <span class="text-[10px] text-gray-400">轮次数</span>
              <input v-model.number="simConfig.iterative_rounds" type="number" min="5" max="100" class="w-full px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <span class="text-[10px] text-gray-400">学习率</span>
              <input v-model.number="simConfig.learning_rate" type="number" min="0.01" max="1" step="0.01" class="w-full px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <span class="text-[10px] text-gray-400">探索率</span>
              <input v-model.number="simConfig.exploration_rate" type="number" min="0" max="0.5" step="0.01" class="w-full px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <span class="text-[10px] text-gray-400">收敛阈值</span>
              <input v-model.number="simConfig.convergence_threshold" type="number" min="0.001" max="0.1" step="0.001" class="w-full px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
          </div>
        </div>

        <div v-if="isABTestMode" class="p-3 bg-indigo-50 rounded border border-indigo-200">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-indigo-700">策略组配置</p>
            <button v-if="abTestGroups.length < 5" class="text-xs text-indigo-600 hover:underline" @click="addABTestGroup">+ 添加策略组</button>
          </div>
          <div v-for="(group, gi) in abTestGroups" :key="gi" class="mb-2 p-2 bg-white rounded border border-indigo-100">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center space-x-2">
                <span class="w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold text-white" :class="gi === 0 ? 'bg-indigo-500' : gi === 1 ? 'bg-emerald-500' : gi === 2 ? 'bg-amber-500' : gi === 3 ? 'bg-rose-500' : 'bg-gray-500'">{{ group.label }}</span>
                <input v-model="group.label" class="w-12 px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400" />
              </div>
              <button v-if="abTestGroups.length > 2" class="text-[10px] text-danger" @click="removeABTestGroup(gi)">✕</button>
            </div>
            <div class="grid grid-cols-3 gap-1">
              <div>
                <span class="text-[10px] text-gray-400">利润率%</span>
                <input v-model.number="group.our_agent.profit_target" type="number" min="0" max="50" class="w-full px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400" />
              </div>
              <div>
                <span class="text-[10px] text-gray-400">风险偏好</span>
                <input v-model.number="group.our_agent.risk_preference" type="number" min="-1" max="1" step="0.1" class="w-full px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400" />
              </div>
              <div>
                <span class="text-[10px] text-gray-400">策略类型</span>
                <select v-model="group.our_agent.strategy" class="w-full px-1 py-0.5 text-[10px] border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400">
                  <option value="aggressive">激进</option>
                  <option value="conservative">保守</option>
                  <option value="balanced">均衡</option>
                </select>
              </div>
            </div>
          </div>
          <p class="text-[10px] text-indigo-400 mt-1">各策略组共享场景参数和竞商配置，仅我方Agent参数不同</p>
        </div>

        <div v-if="!isABTestMode" class="p-3 bg-primary/5 rounded border border-primary/20">
          <p class="text-sm font-medium text-primary mb-2">我方 Agent</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">技术分</span>
              <input v-model.number="ourAgent.tech_score" type="number" min="0" max="100" class="w-16 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">成本基数</span>
              <input v-model.number="ourAgent.cost_base" type="number" class="w-28 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">目标利润率%</span>
              <input v-model.number="ourAgent.profit_target" type="number" min="0" max="50" class="w-16 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">风险偏好</span>
              <input v-model.number="ourAgent.risk_preference" type="range" min="-1" max="1" step="0.1" class="flex-1 mx-2 h-1.5 bg-gray-200 rounded appearance-none cursor-pointer accent-primary" />
              <span class="text-xs text-gray-600 w-8 text-right">{{ ourAgent.risk_preference.toFixed(1) }}</span>
            </div>
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-gray-700">竞商 Agent</p>
            <button class="text-xs text-primary hover:underline" @click="addAgent">+ 添加</button>
          </div>
          <div v-for="(agent, idx) in competitorAgents" :key="idx" class="mb-2 p-2 bg-gray-50 rounded border border-gray-100">
            <div class="flex items-center justify-between mb-1">
              <input v-model="agent.name" class="flex-1 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" placeholder="公司名" />
              <select v-model="agent.strategy" class="ml-2 px-1 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="aggressive">激进型</option>
                <option value="conservative">保守型</option>
                <option value="balanced">均衡型</option>
                <option value="accomplice">陪标型</option>
              </select>
              <button class="ml-2 text-xs text-danger" @click="removeAgent(idx)">✕</button>
            </div>
            <div class="grid grid-cols-3 gap-1">
              <div>
                <span class="text-[10px] text-gray-400">技术分</span>
                <input v-model.number="agent.tech_score" type="number" min="0" max="100" class="w-full px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
              </div>
              <div>
                <span class="text-[10px] text-gray-400">折扣均值</span>
                <input v-model.number="agent.discount_belief_mean" type="number" min="0" max="1" step="0.01" class="w-full px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
              </div>
              <div>
                <span class="text-[10px] text-gray-400">折扣标准差</span>
                <input v-model.number="agent.discount_belief_std" type="number" min="0" max="0.5" step="0.01" class="w-full px-1 py-0.5 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
              </div>
            </div>
          </div>
        </div>

        <div class="border-t border-gray-100 pt-3 mt-3">
          <button
            class="flex items-center space-x-1 text-xs w-full justify-between"
            :class="showCoalitionPanel ? 'text-primary' : 'text-gray-500 hover:text-gray-700'"
            @click="showCoalitionPanel = !showCoalitionPanel"
          >
            <span class="flex items-center">
              <span class="mr-1">🤝</span>
              协同博弈配置
            </span>
            <span :class="showCoalitionPanel ? 'rotate-180' : ''" class="transition-transform duration-200 text-[10px]">▼</span>
          </button>

          <div v-if="showCoalitionPanel" class="mt-2 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">启用联盟模式</span>
              <input v-model="coalitionConfig.enabled" type="checkbox" class="h-4 w-4 text-primary rounded border-gray-200" />
            </div>

            <div v-if="coalitionConfig.enabled" class="space-y-3">
              <div v-for="(alliance, ai) in coalitionConfig.alliances" :key="ai" class="p-2 bg-amber-50 rounded border border-amber-200">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-medium text-amber-700">联盟 {{ ai + 1 }}</span>
                  <button class="text-[10px] text-danger" @click="removeAlliance(ai)">✕ 移除</button>
                </div>

                <div class="space-y-2">
                  <div>
                    <span class="text-[10px] text-gray-400">主攻方</span>
                    <select v-model="alliance.leader" class="w-full mt-0.5 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                      <option value="" disabled>选择主攻方</option>
                      <option v-for="name in availableCompetitorNames" :key="name" :value="name">{{ name }}</option>
                    </select>
                  </div>

                  <div>
                    <span class="text-[10px] text-gray-400">陪标方（多选）</span>
                    <div class="flex flex-wrap gap-1 mt-0.5">
                      <button
                        v-for="name in availableCompetitorNames.filter(n => n !== alliance.leader)"
                        :key="name"
                        class="px-2 py-0.5 text-[10px] rounded border transition-colors duration-150"
                        :class="alliance.supporters.includes(name)
                          ? 'bg-amber-200 border-amber-400 text-amber-800'
                          : 'bg-white border-gray-200 text-gray-500 hover:border-amber-300'"
                        @click="toggleAllianceSupporter(ai, name)"
                      >
                        {{ name }}
                      </button>
                    </div>
                    <p v-if="!availableCompetitorNames.filter(n => n !== alliance.leader).length" class="text-[10px] text-gray-400 mt-1">
                      请先添加竞商后选择
                    </p>
                  </div>

                  <div class="grid grid-cols-2 gap-2">
                    <div>
                      <span class="text-[10px] text-gray-400">协同策略</span>
                      <select v-model="alliance.coordination_type" class="w-full mt-0.5 px-1 py-0.5 text-[10px] border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary">
                        <option value="high_bid_escort">高报价陪标</option>
                        <option value="price_padding">价格垫策略</option>
                        <option value="bracket">区间包裹</option>
                      </select>
                    </div>
                    <div>
                      <span class="text-[10px] text-gray-400">折扣间距</span>
                      <input v-model.number="alliance.discount_spread" type="number" min="0.01" max="0.5" step="0.01" class="w-full mt-0.5 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary" />
                    </div>
                  </div>
                </div>
              </div>

              <button
                class="w-full px-3 py-1.5 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded hover:bg-amber-100 transition-all duration-200"
                @click="addAlliance"
              >
                + 添加联盟
              </button>
            </div>
          </div>
        </div>

        <button
          class="w-full px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 transition-all duration-300 text-sm"
          :disabled="simulating"
          @click="runSimulation"
        >
          {{ simulating ? '模拟运行中...' : '🎮 启动博弈模拟' }}
        </button>
      </div>

      <div v-if="simResult" class="lg:col-span-2 space-y-4">
        <div class="p-4 bg-gradient-to-r from-primary/5 to-success/5 rounded border border-primary/20">
          <p class="text-sm font-medium text-gray-700 mb-3">最优报价建议</p>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">推荐报价</p>
              <p class="text-lg font-bold text-primary">¥{{ formatNum(simResult.optimal_bid.recommended_price) }}</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">推荐折扣率</p>
              <p class="text-lg font-bold text-primary">{{ (simResult.optimal_bid.recommended_discount * 100).toFixed(1) }}%</p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">中标概率</p>
              <p class="text-lg font-bold" :class="simResult.optimal_bid.win_probability >= 0.5 ? 'text-success' : 'text-warning'">
                {{ (simResult.optimal_bid.win_probability * 100).toFixed(1) }}%
              </p>
            </div>
            <div class="text-center">
              <p class="text-xs text-gray-500 mb-1">期望利润</p>
              <p class="text-lg font-bold text-success">¥{{ formatNum(simResult.optimal_bid.expected_profit) }}</p>
            </div>
          </div>
          <div class="mt-3 text-xs text-gray-500">
            折扣率置信区间: [{{ (simResult.optimal_bid.confidence_interval[0] * 100).toFixed(1) }}%, {{ (simResult.optimal_bid.confidence_interval[1] * 100).toFixed(1) }}%]
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="p-4 bg-gray-50 rounded">
            <p class="text-sm font-medium text-gray-700 mb-2">模拟统计</p>
            <div class="space-y-1 text-xs text-gray-600">
              <div class="flex justify-between"><span>模拟次数</span><span>{{ simResult.simulation_stats.n_simulations }}</span></div>
              <div class="flex justify-between"><span>最优折扣下中标率</span><span>{{ (simResult.simulation_stats.win_rate_at_optimal * 100).toFixed(1) }}%</span></div>
              <div class="flex justify-between"><span>平均利润</span><span>¥{{ formatNum(simResult.simulation_stats.avg_profit_at_optimal) }}</span></div>
              <div class="flex justify-between"><span>中位数排名</span><span>第{{ simResult.simulation_stats.median_rank }}名</span></div>
              <div class="flex justify-between"><span>P10排名</span><span>第{{ simResult.simulation_stats.p10_rank }}名</span></div>
              <div class="flex justify-between"><span>P90排名</span><span>第{{ simResult.simulation_stats.p90_rank }}名</span></div>
            </div>
          </div>

          <div class="p-4 bg-gray-50 rounded">
            <p class="text-sm font-medium text-gray-700 mb-2">纳什均衡 & 敏感性</p>
            <div class="space-y-1 text-xs text-gray-600">
              <div class="flex justify-between">
                <span>纳什均衡</span>
                <span :class="simResult.nash_equilibrium.found ? 'text-success' : 'text-gray-400'">
                  {{ simResult.nash_equilibrium.found ? '已找到' : '未找到' }}
                </span>
              </div>
              <div v-if="simResult.nash_equilibrium.found" class="flex justify-between">
                <span>均衡折扣率</span>
                <span>{{ (simResult.nash_equilibrium.our_optimal_discount * 100).toFixed(1) }}%</span>
              </div>
              <div v-if="simResult.nash_equilibrium.found" class="flex justify-between">
                <span>均衡类型</span>
                <span>{{ simResult.nash_equilibrium.equilibrium_type }}</span>
              </div>
              <div class="flex justify-between">
                <span>最敏感参数</span>
                <span>{{ simResult.sensitivity.most_sensitive_param }}</span>
              </div>
              <div class="flex justify-between">
                <span>价格弹性</span>
                <span>{{ simResult.sensitivity.price_elasticity.toFixed(4) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="simResult.game_insights.length" class="p-4 bg-gray-50 rounded">
          <p class="text-sm font-medium text-gray-700 mb-2">博弈洞察</p>
          <div class="space-y-2">
            <div v-for="(insight, i) in simResult.game_insights" :key="i" class="flex items-start space-x-2 text-xs text-gray-600">
              <span class="text-primary mt-0.5">●</span>
              <span>{{ insight }}</span>
            </div>
          </div>
        </div>

        <div v-if="simResult.coalition_result" class="p-4 bg-amber-50 rounded border border-amber-200">
          <p class="text-sm font-medium text-amber-800 mb-2">🤝 协同博弈结果</p>
          <div class="grid grid-cols-2 md:grid-cols-3 gap-2 mb-2">
            <div class="bg-white rounded p-2 border border-amber-100">
              <p class="text-[10px] text-gray-400">联盟数量</p>
              <p class="text-sm font-semibold text-amber-700">{{ simResult.coalition_result.alliance_count }}</p>
            </div>
            <div v-for="(count, ct) in simResult.coalition_result.coordination_type_breakdown" :key="ct" class="bg-white rounded p-2 border border-amber-100">
              <p class="text-[10px] text-gray-400">{{ ct === 'high_bid_escort' ? '高报价陪标' : ct === 'price_padding' ? '价格垫' : ct === 'bracket' ? '区间包裹' : ct }}</p>
              <p class="text-sm font-semibold text-amber-700">{{ count }}组</p>
            </div>
          </div>
          <div v-if="simResult.coalition_result.agent_effects.length" class="overflow-x-auto">
            <table class="w-full text-[11px]">
              <thead>
                <tr class="border-b border-amber-200">
                  <th class="px-2 py-1 text-left text-amber-600">Agent</th>
                  <th class="px-2 py-1 text-left text-amber-600">角色</th>
                  <th class="px-2 py-1 text-right text-amber-600">联盟</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="effect in simResult.coalition_result.agent_effects" :key="effect.agent_name" class="border-b border-amber-100">
                  <td class="px-2 py-1 text-gray-700">{{ effect.agent_name }}</td>
                  <td class="px-2 py-1">
                    <span class="px-1.5 py-0.5 rounded text-[10px]" :class="effect.role === 'leader' ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-500'">
                      {{ effect.role === 'leader' ? '主攻方' : '陪标方' }}
                    </span>
                  </td>
                  <td class="px-2 py-1 text-right text-gray-500">联盟{{ effect.alliance_id + 1 }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="simResult.iterative_result" class="space-y-4">
          <div class="p-4 bg-gray-50 rounded border border-gray-100">
            <p class="text-sm font-medium text-gray-700 mb-3">多轮迭代结果</p>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div class="bg-white border border-gray-100 rounded p-3">
                <p class="text-[11px] text-gray-500 mb-1">收敛轮次</p>
                <p class="text-base font-semibold text-gray-800">
                  {{ simResult.iterative_result.convergence_round ? `第${simResult.iterative_result.convergence_round}轮` : '未收敛' }}
                </p>
              </div>
              <div class="bg-white border border-gray-100 rounded p-3">
                <p class="text-[11px] text-gray-500 mb-1">最终最优折扣</p>
                <p class="text-base font-semibold text-primary">
                  {{ (simResult.iterative_result.final_optimal_discount * 100).toFixed(1) }}%
                </p>
              </div>
              <div class="bg-white border border-gray-100 rounded p-3">
                <p class="text-[11px] text-gray-500 mb-1">最终胜率</p>
                <p class="text-base font-semibold text-success">
                  {{ (simResult.iterative_result.final_win_probability * 100).toFixed(1) }}%
                </p>
              </div>
              <div class="bg-white border border-gray-100 rounded p-3">
                <p class="text-[11px] text-gray-500 mb-1">最终期望利润</p>
                <p class="text-base font-semibold text-gray-800">¥{{ formatNum(simResult.iterative_result.final_expected_profit) }}</p>
              </div>
            </div>
          </div>

          <div class="p-4 bg-gray-50 rounded border border-gray-100">
            <p class="text-sm font-medium text-gray-700 mb-2">策略演化</p>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead class="bg-white">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-500">Agent</th>
                    <th class="px-3 py-2 text-right text-gray-500">初始均值</th>
                    <th class="px-3 py-2 text-right text-gray-500">最终均值</th>
                    <th class="px-3 py-2 text-right text-gray-500">偏移</th>
                    <th class="px-3 py-2 text-right text-gray-500">胜场</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in simResult.iterative_result.strategy_evolutions" :key="item.agent_name" class="border-t border-gray-100">
                    <td class="px-3 py-2 font-medium text-gray-700">{{ item.agent_name }}</td>
                    <td class="px-3 py-2 text-right">{{ (item.initial_discount_mean * 100).toFixed(1) }}%</td>
                    <td class="px-3 py-2 text-right">{{ (item.final_discount_mean * 100).toFixed(1) }}%</td>
                    <td class="px-3 py-2 text-right" :class="item.strategy_shift > 0 ? 'text-danger' : item.strategy_shift < 0 ? 'text-success' : 'text-gray-500'">
                      {{ item.strategy_shift > 0 ? '+' : '' }}{{ (item.strategy_shift * 100).toFixed(1) }}%
                    </td>
                    <td class="px-3 py-2 text-right">{{ item.wins }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="p-4 bg-gray-50 rounded border border-gray-100">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-medium text-gray-700">轮次明细</p>
              <span class="text-[11px] text-gray-400">展示最近 {{ iterativeRoundsToShow.length }} 轮</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead class="bg-white">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-500">轮次</th>
                    <th class="px-3 py-2 text-right text-gray-500">我方折扣</th>
                    <th class="px-3 py-2 text-right text-gray-500">总分</th>
                    <th class="px-3 py-2 text-right text-gray-500">排名</th>
                    <th class="px-3 py-2 text-right text-gray-500">利润</th>
                    <th class="px-3 py-2 text-right text-gray-500">结果</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="round in iterativeRoundsToShow" :key="round.round_no" class="border-t border-gray-100">
                    <td class="px-3 py-2 text-gray-700">第{{ round.round_no }}轮</td>
                    <td class="px-3 py-2 text-right">{{ (round.our_discount * 100).toFixed(1) }}%</td>
                    <td class="px-3 py-2 text-right">{{ round.our_total_score.toFixed(2) }}</td>
                    <td class="px-3 py-2 text-right">第{{ round.our_rank }}名</td>
                    <td class="px-3 py-2 text-right">¥{{ formatNum(round.profit) }}</td>
                    <td class="px-3 py-2 text-right" :class="round.won ? 'text-success' : 'text-gray-500'">
                      {{ round.won ? '中标' : '未中标' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-if="abTestResult" class="space-y-4">
          <div class="p-4 bg-gradient-to-r from-indigo-50 to-emerald-50 rounded border border-indigo-200">
            <p class="text-sm font-medium text-indigo-800 mb-3">📊 A/B 测试对比结果</p>
            <div v-if="abTestResult.comparison.recommendation" class="mb-3 p-3 bg-white rounded border border-indigo-100">
              <p class="text-xs text-gray-700">{{ abTestResult.comparison.recommendation }}</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="bg-white rounded p-3 border border-gray-100">
                <p class="text-xs font-medium text-gray-600 mb-2">胜率排名</p>
                <div v-for="(item, ri) in abTestResult.comparison.win_rate_ranking" :key="ri" class="flex items-center justify-between py-1 border-b border-gray-50 last:border-0">
                  <span class="text-xs font-medium" :class="item.label === abTestResult.comparison.best_strategy ? 'text-indigo-700' : 'text-gray-600'">
                    {{ ri === 0 ? '🥇' : ri === 1 ? '🥈' : '🥉' }} 策略{{ item.label }}
                  </span>
                  <span class="text-xs font-bold" :class="item.win_probability >= 0.5 ? 'text-success' : 'text-warning'">
                    {{ (item.win_probability * 100).toFixed(1) }}%
                  </span>
                </div>
              </div>
              <div class="bg-white rounded p-3 border border-gray-100">
                <p class="text-xs font-medium text-gray-600 mb-2">利润排名</p>
                <div v-for="(item, ri) in abTestResult.comparison.profit_ranking" :key="ri" class="flex items-center justify-between py-1 border-b border-gray-50 last:border-0">
                  <span class="text-xs font-medium text-gray-600">
                    {{ ri === 0 ? '🥇' : ri === 1 ? '🥈' : '🥉' }} 策略{{ item.label }}
                  </span>
                  <span class="text-xs font-bold text-success">¥{{ formatNum(item.expected_profit) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="p-4 bg-gray-50 rounded border border-gray-100">
            <p class="text-sm font-medium text-gray-700 mb-3">策略组详情</p>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead class="bg-white">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-500">策略</th>
                    <th class="px-3 py-2 text-right text-gray-500">最优折扣</th>
                    <th class="px-3 py-2 text-right text-gray-500">推荐报价</th>
                    <th class="px-3 py-2 text-right text-gray-500">胜率</th>
                    <th class="px-3 py-2 text-right text-gray-500">期望利润</th>
                    <th class="px-3 py-2 text-right text-gray-500">中位排名</th>
                    <th class="px-3 py-2 text-right text-gray-500">置信区间</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="r in abTestResult.strategy_results" :key="r.label" class="border-t border-gray-100" :class="r.label === abTestResult.comparison.best_strategy ? 'bg-indigo-50' : ''">
                    <td class="px-3 py-2 font-medium" :class="r.label === abTestResult.comparison.best_strategy ? 'text-indigo-700' : 'text-gray-700'">
                      {{ r.label }}{{ r.label === abTestResult.comparison.best_strategy ? ' ★' : '' }}
                    </td>
                    <td class="px-3 py-2 text-right">{{ (r.optimal_discount * 100).toFixed(1) }}%</td>
                    <td class="px-3 py-2 text-right">¥{{ formatNum(r.recommended_price) }}</td>
                    <td class="px-3 py-2 text-right font-bold" :class="r.win_probability >= 0.5 ? 'text-success' : 'text-warning'">
                      {{ (r.win_probability * 100).toFixed(1) }}%
                    </td>
                    <td class="px-3 py-2 text-right text-success">¥{{ formatNum(r.expected_profit) }}</td>
                    <td class="px-3 py-2 text-right">第{{ r.median_rank }}名</td>
                    <td class="px-3 py-2 text-right text-gray-400">[{{ (r.confidence_interval[0] * 100).toFixed(1) }}%, {{ (r.confidence_interval[1] * 100).toFixed(1) }}%]</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="abTestResult.comparison.significance_tests.length" class="p-4 bg-gray-50 rounded border border-gray-100">
            <p class="text-sm font-medium text-gray-700 mb-2">统计显著性检验</p>
            <div class="overflow-x-auto">
              <table class="w-full text-xs">
                <thead class="bg-white">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-500">对比</th>
                    <th class="px-3 py-2 text-right text-gray-500">胜率差</th>
                    <th class="px-3 py-2 text-right text-gray-500">Z值</th>
                    <th class="px-3 py-2 text-right text-gray-500">p值</th>
                    <th class="px-3 py-2 text-center text-gray-500">显著?</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="test in abTestResult.comparison.significance_tests" :key="test.comparison" class="border-t border-gray-100">
                    <td class="px-3 py-2 text-gray-700">{{ test.comparison }}</td>
                    <td class="px-3 py-2 text-right" :class="test.win_rate_diff > 0 ? 'text-success' : test.win_rate_diff < 0 ? 'text-danger' : 'text-gray-500'">
                      {{ test.win_rate_diff > 0 ? '+' : '' }}{{ (test.win_rate_diff * 100).toFixed(1) }}%
                    </td>
                    <td class="px-3 py-2 text-right">{{ test.z_score.toFixed(4) }}</td>
                    <td class="px-3 py-2 text-right">{{ test.p_value.toFixed(4) }}</td>
                    <td class="px-3 py-2 text-center">
                      <span class="px-1.5 py-0.5 rounded text-[10px]" :class="test.significant_at_005 ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-400'">
                        {{ test.significant_at_005 ? '显著' : '不显著' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="abTestResult.insights.length" class="p-4 bg-gray-50 rounded">
            <p class="text-sm font-medium text-gray-700 mb-2">A/B 测试洞察</p>
            <div class="space-y-2">
              <div v-for="(insight, i) in abTestResult.insights" :key="i" class="flex items-start space-x-2 text-xs text-gray-600">
                <span class="text-indigo-500 mt-0.5">●</span>
                <span>{{ insight }}</span>
              </div>
            </div>
          </div>
        </div>

        <GameReplayCharts
          v-if="simResult.raw_simulation_data"
          :raw-data="simResult.raw_simulation_data"
          :bayesian-updates="simResult.bayesian_updates || []"
          :optimal-discount="simResult.optimal_bid.recommended_discount"
        />

        <div class="flex items-center justify-between p-3 border border-primary/20 bg-primary/5 rounded">
          <span class="text-sm text-gray-700">应用到报价策略</span>
          <button class="px-3 py-1.5 text-xs bg-primary text-white rounded hover:bg-primary/90" @click="applyResult">
            应用最优报价
          </button>
        </div>
      </div>

      <div v-else class="lg:col-span-2 flex items-center justify-center text-gray-400 text-sm">
        配置场景和Agent后点击"启动博弈模拟"
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { simulateBiddingGame, runABTest } from '../../services/biddingGame'
import type {
  BiddingGameSimulateResponse,
  AgentConfig,
  CompetitorHistoryProfile,
  SimulationConfig,
  CoalitionConfig,
  AllianceConfig,
  CoalitionResult,
  ABTestStrategyGroup,
  ABTestResponse,
} from '../../services/biddingGame'
import GameReplayCharts from './GameReplayCharts.vue'

const props = withDefaults(defineProps<{
  projectId?: string
}>(), {
  projectId: undefined,
})

const emit = defineEmits<{
  (e: 'apply-optimal-bid', result: BiddingGameSimulateResponse): void
}>()

const scenario = ref({
  budget: 2500000,
  scoring_method: 'linear',
  tech_weight: 0.5,
  price_weight: 0.5,
  k_value: 95,
  sensitivity: 2,
  tax_rate: 0.06,
})

const ourAgent = ref<AgentConfig>({
  name: '我方',
  strategy: 'balanced',
  tech_score: 85,
  cost_base: 1800000,
  profit_target: 18,
  risk_preference: 0.0,
  discount_belief_mean: 0.5,
  discount_belief_std: 0.1,
})

const competitorAgents = ref<AgentConfig[]>([
  { name: '亚信', strategy: 'balanced', tech_score: 80, cost_base: 0, profit_target: 15, risk_preference: 0.0, discount_belief_mean: 0.21, discount_belief_std: 0.12 },
  { name: '中软', strategy: 'aggressive', tech_score: 75, cost_base: 0, profit_target: 12, risk_preference: 0.3, discount_belief_mean: 0.26, discount_belief_std: 0.10 },
  { name: '浪潮', strategy: 'conservative', tech_score: 82, cost_base: 0, profit_target: 20, risk_preference: -0.2, discount_belief_mean: 0.15, discount_belief_std: 0.09 },
])

const simConfig = ref<SimulationConfig>({
  n_simulations: 500,
  method: 'monte_carlo',
  iterative_rounds: 16,
  learning_rate: 0.18,
  exploration_rate: 0.12,
  convergence_threshold: 0.01,
})
const simulating = ref(false)
const simResult = ref<BiddingGameSimulateResponse | null>(null)
const isIterativeMode = computed(() => simConfig.value.method === 'iterative')
const isABTestMode = computed(() => simConfig.value.method === 'ab_test')
const iterativeRoundsToShow = computed(() => simResult.value?.iterative_result?.rounds.slice(-8) ?? [])
const showCoalitionPanel = ref(false)

const abTestGroups = ref<ABTestStrategyGroup[]>([
  { label: 'A', our_agent: { name: '我方A', strategy: 'balanced', tech_score: 85, cost_base: 1800000, profit_target: 18, risk_preference: 0.0, discount_belief_mean: 0.5, discount_belief_std: 0.1 } },
  { label: 'B', our_agent: { name: '我方B', strategy: 'aggressive', tech_score: 85, cost_base: 1800000, profit_target: 12, risk_preference: 0.5, discount_belief_mean: 0.5, discount_belief_std: 0.1 } },
])
const abTestResult = ref<ABTestResponse | null>(null)

const addABTestGroup = () => {
  const labels = ['A', 'B', 'C', 'D', 'E']
  const nextLabel = labels[abTestGroups.value.length] || String(abTestGroups.value.length + 1)
  abTestGroups.value.push({
    label: nextLabel,
    our_agent: { name: `我方${nextLabel}`, strategy: 'balanced', tech_score: 85, cost_base: 1800000, profit_target: 15, risk_preference: 0.0, discount_belief_mean: 0.5, discount_belief_std: 0.1 },
  })
}

const removeABTestGroup = (idx: number) => {
  abTestGroups.value.splice(idx, 1)
}

const coalitionConfig = ref<CoalitionConfig>({
  alliances: [],
  enabled: false,
  profit_redistribution: false,
})

const addAlliance = () => {
  coalitionConfig.value.alliances.push({
    leader: '',
    supporters: [],
    coordination_type: 'high_bid_escort',
    leader_bonus: 0,
    discount_spread: 0.06,
  })
  coalitionConfig.value.enabled = true
}

const removeAlliance = (idx: number) => {
  coalitionConfig.value.alliances.splice(idx, 1)
  if (!coalitionConfig.value.alliances.length) {
    coalitionConfig.value.enabled = false
  }
}

const toggleAllianceSupporter = (allianceIdx: number, agentName: string) => {
  const alliance = coalitionConfig.value.alliances[allianceIdx]
  if (!alliance) return
  const idx = alliance.supporters.indexOf(agentName)
  if (idx >= 0) {
    alliance.supporters.splice(idx, 1)
  } else {
    alliance.supporters.push(agentName)
  }
}

const availableCompetitorNames = computed(() =>
  competitorAgents.value.map(a => a.name).filter(Boolean)
)

const addAgent = () => {
  competitorAgents.value.push({
    name: '', strategy: 'balanced', tech_score: 75, cost_base: 0,
    profit_target: 15, risk_preference: 0.0,
    discount_belief_mean: 0.18, discount_belief_std: 0.10,
  })
}

const removeAgent = (idx: number) => {
  competitorAgents.value.splice(idx, 1)
}

const formatNum = (v: number) => {
  return Number(v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const applyHistoryProfiles = (profiles: CompetitorHistoryProfile[]) => {
  console.info('[BiddingGameSimulator] Applying history profiles', {
    profileCount: profiles.length,
    names: profiles.map(profile => profile.name),
  })

  const existingAgents = new Map(
    competitorAgents.value.map(agent => [agent.name.trim().toLowerCase(), agent]),
  )

  profiles.forEach((profile) => {
    const key = profile.name.trim().toLowerCase()
    if (!key) return
    const existingAgent = existingAgents.get(key)
    if (existingAgent) {
      existingAgent.discount_belief_mean = profile.discount_belief_mean
      existingAgent.discount_belief_std = profile.discount_belief_std
      return
    }
    competitorAgents.value.push({
      name: profile.name,
      strategy: 'balanced',
      tech_score: 75,
      cost_base: 0,
      profit_target: 15,
      risk_preference: 0.0,
      discount_belief_mean: profile.discount_belief_mean,
      discount_belief_std: profile.discount_belief_std,
    })
  })
}

const runSimulation = async () => {
  simulating.value = true
  try {
    if (isABTestMode.value) {
      console.info('[BiddingGameSimulator] Starting A/B test', {
        groupCount: abTestGroups.value.length,
        competitorCount: competitorAgents.value.filter(a => a.name).length,
      })
      abTestResult.value = await runABTest({
        project_id: props.projectId,
        scenario: scenario.value,
        strategy_groups: abTestGroups.value,
        competitor_agents: competitorAgents.value.filter(a => a.name),
        n_simulations: simConfig.value.n_simulations,
        coalition_config: coalitionConfig.value.enabled ? coalitionConfig.value : undefined,
      })
      simResult.value = null
    } else {
      const simulationConfig: SimulationConfig = {
        n_simulations: simConfig.value.n_simulations,
        method: simConfig.value.method,
      }
      if (isIterativeMode.value) {
        simulationConfig.iterative_rounds = simConfig.value.iterative_rounds
        simulationConfig.learning_rate = simConfig.value.learning_rate
        simulationConfig.exploration_rate = simConfig.value.exploration_rate
        simulationConfig.convergence_threshold = simConfig.value.convergence_threshold
      }
      const payload = {
        project_id: props.projectId,
        scenario: scenario.value,
        our_agent: ourAgent.value,
        competitor_agents: competitorAgents.value.filter(a => a.name),
        simulation_config: simulationConfig,
        coalition_config: coalitionConfig.value.enabled ? coalitionConfig.value : undefined,
      }
      console.info('[BiddingGameSimulator] Starting simulation', {
        competitorCount: payload.competitor_agents.length,
        method: simulationConfig.method,
        nSimulations: simulationConfig.n_simulations,
      })
      simResult.value = await simulateBiddingGame(payload)
      abTestResult.value = null
    }
  } catch (e: any) {
    console.error('[BiddingGameSimulator] Simulation failed', e)
    alert(e.message || '博弈模拟失败')
  } finally {
    simulating.value = false
  }
}

const applyResult = () => {
  if (isABTestMode.value && abTestResult.value) {
    const best = abTestResult.value.strategy_results.find(
      r => r.label === abTestResult.value!.comparison.best_strategy,
    )
    if (best) {
      emit('apply-optimal-bid', {
        optimal_bid: {
          recommended_price: best.recommended_price,
          recommended_discount: best.optimal_discount,
          win_probability: best.win_probability,
          expected_profit: best.expected_profit,
          confidence_interval: best.confidence_interval,
        },
      } as BiddingGameSimulateResponse)
    }
    return
  }
  if (simResult.value) {
    emit('apply-optimal-bid', simResult.value)
  }
}

defineExpose({ scenario, ourAgent, competitorAgents, applyHistoryProfiles })
</script>

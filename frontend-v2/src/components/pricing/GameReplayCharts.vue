<template>
  <div class="space-y-4">
    <div v-if="rawData?.discount_winrate_curve" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">中标概率 vs 折扣率</p>
      <div ref="winrateChartRef" style="height: 280px;"></div>
    </div>

    <div v-if="rawData?.discount_profit_curve" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">期望利润 vs 折扣率</p>
      <div ref="profitChartRef" style="height: 280px;"></div>
    </div>

    <div v-if="rawData?.bayesian_details && rawData.bayesian_details.length" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">贝叶斯信念更新</p>
      <div ref="bayesianChartRef" style="height: 260px;"></div>
    </div>

    <div v-if="bayesianUpdates && bayesianUpdates.length" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">信念偏移详情</p>
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-gray-500">Agent</th>
              <th class="px-3 py-2 text-right text-gray-500">先验均值</th>
              <th class="px-3 py-2 text-right text-gray-500">后验均值</th>
              <th class="px-3 py-2 text-right text-gray-500">偏移量</th>
              <th class="px-3 py-2 text-right text-gray-500">先验σ</th>
              <th class="px-3 py-2 text-right text-gray-500">后验σ</th>
              <th class="px-3 py-2 text-right text-gray-500">观察数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in bayesianUpdates" :key="u.agent_name" class="border-t border-gray-50">
              <td class="px-3 py-2 font-medium text-gray-800">{{ u.agent_name }}</td>
              <td class="px-3 py-2 text-right">{{ (u.prior_mean * 100).toFixed(1) }}%</td>
              <td class="px-3 py-2 text-right">{{ (u.posterior_mean * 100).toFixed(1) }}%</td>
              <td class="px-3 py-2 text-right" :class="u.belief_shift > 0 ? 'text-danger' : u.belief_shift < 0 ? 'text-success' : 'text-gray-500'">
                {{ u.belief_shift > 0 ? '+' : '' }}{{ (u.belief_shift * 100).toFixed(1) }}%
              </td>
              <td class="px-3 py-2 text-right">{{ (u.prior_std * 100).toFixed(1) }}%</td>
              <td class="px-3 py-2 text-right">{{ (u.posterior_std * 100).toFixed(1) }}%</td>
              <td class="px-3 py-2 text-right">{{ u.n_observations }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="rawData?.iterative_rounds && rawData.iterative_rounds.length" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">多轮迭代趋势</p>
      <div ref="iterativeTrendChartRef" style="height: 300px;"></div>
    </div>

    <div v-if="rawData?.strategy_evolutions && rawData.strategy_evolutions.length" class="bg-white rounded-lg border border-gray-100 p-4">
      <p class="text-sm font-medium text-gray-700 mb-3">策略演化轨迹</p>
      <div ref="strategyEvolutionChartRef" style="height: 300px;"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { RawSimulationData, BayesianBeliefUpdate } from '../../services/biddingGame'

const props = defineProps<{
  rawData: RawSimulationData | undefined
  bayesianUpdates: BayesianBeliefUpdate[]
  optimalDiscount: number
}>()

const winrateChartRef = ref<HTMLElement>()
const profitChartRef = ref<HTMLElement>()
const bayesianChartRef = ref<HTMLElement>()
const iterativeTrendChartRef = ref<HTMLElement>()
const strategyEvolutionChartRef = ref<HTMLElement>()

let winrateChart: echarts.ECharts | null = null
let profitChart: echarts.ECharts | null = null
let bayesianChart: echarts.ECharts | null = null
let iterativeTrendChart: echarts.ECharts | null = null
let strategyEvolutionChart: echarts.ECharts | null = null

const renderWinrateChart = () => {
  if (!winrateChartRef.value || !props.rawData?.discount_winrate_curve) return
  if (!winrateChart) {
    winrateChart = echarts.init(winrateChartRef.value)
  }
  const data = props.rawData.discount_winrate_curve
  winrateChart.setOption({
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => (d.discount * 100).toFixed(1) + '%'),
      axisLabel: { fontSize: 10, interval: Math.floor(data.length / 8) },
      name: '折扣率',
      nameTextStyle: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 10, formatter: (v: number) => (v * 100).toFixed(0) + '%' },
      name: '中标概率',
      nameTextStyle: { fontSize: 11 },
    },
    series: [{
      type: 'line',
      data: data.map(d => d.win_rate),
      smooth: true,
      lineStyle: { width: 2, color: '#4F46E5' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(79,70,229,0.2)' },
        { offset: 1, color: 'rgba(79,70,229,0.02)' },
      ]) },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#EF4444', type: 'dashed', width: 1 },
        data: [{ xAxis: (props.optimalDiscount * 100).toFixed(1) + '%', label: { formatter: '最优', fontSize: 10 } }],
      },
    }],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        return `折扣率: ${p.axisValue}<br/>中标概率: ${(p.value * 100).toFixed(1)}%`
      },
    },
  })
}

const renderProfitChart = () => {
  if (!profitChartRef.value || !props.rawData?.discount_profit_curve) return
  if (!profitChart) {
    profitChart = echarts.init(profitChartRef.value)
  }
  const data = props.rawData.discount_profit_curve
  profitChart.setOption({
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: data.map(d => (d.discount * 100).toFixed(1) + '%'),
      axisLabel: { fontSize: 10, interval: Math.floor(data.length / 8) },
      name: '折扣率',
      nameTextStyle: { fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      axisLabel: { fontSize: 10, formatter: (v: number) => '¥' + (v / 10000).toFixed(0) + '万' },
      name: '期望利润',
      nameTextStyle: { fontSize: 11 },
    },
    series: [{
      type: 'line',
      data: data.map(d => d.avg_profit),
      smooth: true,
      lineStyle: { width: 2, color: '#10B981' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(16,185,129,0.2)' },
        { offset: 1, color: 'rgba(16,185,129,0.02)' },
      ]) },
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#EF4444', type: 'dashed', width: 1 },
        data: [{ xAxis: (props.optimalDiscount * 100).toFixed(1) + '%', label: { formatter: '最优', fontSize: 10 } }],
      },
    }],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        return `折扣率: ${p.axisValue}<br/>期望利润: ¥${Number(p.value).toLocaleString()}`
      },
    },
  })
}

const renderBayesianChart = () => {
  if (!bayesianChartRef.value || !props.rawData?.bayesian_details) return
  if (!bayesianChart) {
    bayesianChart = echarts.init(bayesianChartRef.value)
  }
  const details = props.rawData.bayesian_details
  const names = details.map(d => d.agent_name)
  bayesianChart.setOption({
    grid: { left: 80, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'value',
      axisLabel: { fontSize: 10, formatter: (v: number) => (v * 100).toFixed(0) + '%' },
      name: '折扣率信念',
      nameTextStyle: { fontSize: 11 },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 10 },
    },
    series: [
      {
        name: '先验',
        type: 'scatter',
        data: details.map(d => [d.prior_mean, d.agent_name]),
        symbolSize: 12,
        itemStyle: { color: '#94A3B8' },
      },
      {
        name: '后验',
        type: 'scatter',
        data: details.map(d => [d.posterior_mean, d.agent_name]),
        symbolSize: 14,
        itemStyle: { color: '#4F46E5' },
      },
      {
        name: '偏移',
        type: 'custom',
        renderItem: (_params: any, api: any) => {
          const priorX = api.coord([api.value(0), api.value(1)])
          const posteriorX = api.coord([api.value(2), api.value(1)])
          return {
            type: 'line',
            shape: { x1: priorX[0], y1: priorX[1], x2: posteriorX[0], y2: posteriorX[1] },
            style: { stroke: '#F59E0B', lineWidth: 2, lineDash: [4, 2] },
          }
        },
        data: details.map(d => [d.prior_mean, d.agent_name, d.posterior_mean]),
        z: 1,
      },
    ],
    legend: { top: 0, right: 0, textStyle: { fontSize: 10 } },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const d = details[params.dataIndex]
        if (!d) return ''
        return `${d.agent_name}<br/>先验: ${(d.prior_mean * 100).toFixed(1)}% → 后验: ${(d.posterior_mean * 100).toFixed(1)}%<br/>偏移: ${d.belief_shift > 0 ? '+' : ''}${(d.belief_shift * 100).toFixed(1)}%`
      },
    },
  })
}

const renderIterativeTrendChart = () => {
  if (!iterativeTrendChartRef.value || !props.rawData?.iterative_rounds?.length) return
  if (!iterativeTrendChart) {
    iterativeTrendChart = echarts.init(iterativeTrendChartRef.value)
  }

  const rounds = props.rawData.iterative_rounds
  iterativeTrendChart.setOption({
    grid: { left: 48, right: 56, top: 24, bottom: 34 },
    legend: { top: 0, right: 0, textStyle: { fontSize: 10 } },
    xAxis: {
      type: 'category',
      data: rounds.map(item => `R${item.round_no}`),
      axisLabel: { fontSize: 10 },
    },
    yAxis: [
      {
        type: 'value',
        name: '折扣率',
        axisLabel: { fontSize: 10, formatter: (v: number) => `${(v * 100).toFixed(0)}%` },
        nameTextStyle: { fontSize: 11 },
      },
      {
        type: 'value',
        name: '利润',
        axisLabel: { fontSize: 10, formatter: (v: number) => `¥${(v / 10000).toFixed(0)}万` },
        nameTextStyle: { fontSize: 11 },
      },
    ],
    series: [
      {
        name: '我方折扣',
        type: 'line',
        smooth: true,
        data: rounds.map(item => item.our_discount),
        lineStyle: { width: 2, color: '#2563EB' },
      },
      {
        name: '轮次利润',
        type: 'bar',
        yAxisIndex: 1,
        barMaxWidth: 14,
        data: rounds.map(item => item.profit),
        itemStyle: {
          color: (params: any) => rounds[params.dataIndex]?.won ? '#16A34A' : '#DC2626',
        },
      },
    ],
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const index = params?.[0]?.dataIndex ?? 0
        const round = rounds[index]
        if (!round) return ''
        return [
          `第${round.round_no}轮`,
          `折扣率: ${(round.our_discount * 100).toFixed(1)}%`,
          `排名: 第${round.our_rank}名`,
          `利润: ¥${Number(round.profit).toLocaleString()}`,
          `结果: ${round.won ? '中标' : '未中标'}`,
        ].join('<br/>')
      },
    },
  })
}

const renderStrategyEvolutionChart = () => {
  if (!strategyEvolutionChartRef.value || !props.rawData?.strategy_evolutions?.length) return
  if (!strategyEvolutionChart) {
    strategyEvolutionChart = echarts.init(strategyEvolutionChartRef.value)
  }

  const evolutions = props.rawData.strategy_evolutions
  const roundLength = Math.max(...evolutions.map(item => item.learning_curve.length))
  strategyEvolutionChart.setOption({
    grid: { left: 50, right: 20, top: 28, bottom: 34 },
    legend: { top: 0, left: 0, textStyle: { fontSize: 10 } },
    xAxis: {
      type: 'category',
      data: Array.from({ length: roundLength }, (_, idx) => idx === 0 ? 'Init' : `R${idx}`),
      axisLabel: { fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: '折扣均值',
      axisLabel: { fontSize: 10, formatter: (v: number) => `${(v * 100).toFixed(0)}%` },
      nameTextStyle: { fontSize: 11 },
    },
    series: evolutions.map((item, idx) => ({
      name: item.agent_name,
      type: 'line',
      smooth: true,
      symbolSize: 6,
      data: item.learning_curve,
      lineStyle: { width: idx === 0 ? 2.5 : 1.8 },
    })),
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const rows = (params || []).map((entry: any) => (
          `${entry.seriesName}: ${(Number(entry.value) * 100).toFixed(1)}%`
        ))
        return rows.join('<br/>')
      },
    },
  })
}

const renderAll = () => {
  nextTick(() => {
    renderWinrateChart()
    renderProfitChart()
    renderBayesianChart()
    renderIterativeTrendChart()
    renderStrategyEvolutionChart()
  })
}

watch(() => props.rawData, () => {
  renderAll()
}, { deep: true })

onMounted(() => {
  renderAll()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  winrateChart?.dispose()
  profitChart?.dispose()
  bayesianChart?.dispose()
  iterativeTrendChart?.dispose()
  strategyEvolutionChart?.dispose()
})

const handleResize = () => {
  winrateChart?.resize()
  profitChart?.resize()
  bayesianChart?.resize()
  iterativeTrendChart?.resize()
  strategyEvolutionChart?.resize()
}
</script>

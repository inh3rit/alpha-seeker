<template>
  <div class="stock-detail">
    <h2>{{ code }} 详情</h2>

    <el-card class="chart-card">
      <template #header>K 线图</template>
      <div ref="chartRef" style="height: 400px;"></div>
    </el-card>

    <el-empty v-if="!chartData.length" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import api from '../api'

const route = useRoute()
const code = ref(route.params.code)
const chartRef = ref(null)
const chartData = ref([])

const fetchChart = async () => {
  try {
    const { data } = await api.get(`/api/stocks/${code.value}/chart`, { params: { days: 60 } })
    chartData.value = data.data || []
    renderChart()
  } catch (e) {
    console.error('获取图表数据失败:', e)
  }
}

const renderChart = () => {
  if (!chartRef.value || !chartData.value.length) return

  const chart = echarts.init(chartRef.value)
  const dates = chartData.value.map(d => d.date)
  const ohlc = chartData.value.map(d => [d.open, d.close, d.low, d.high])
  const volumes = chartData.value.map(d => d.volume)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates },
    yAxis: [
      { type: 'value', name: '价格' },
      { type: 'value', name: '成交量', splitLine: { show: false } },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: ohlc,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a',
        },
      },
      {
        name: '成交量',
        type: 'bar',
        yAxisIndex: 1,
        data: volumes,
        itemStyle: { color: '#ccc', opacity: 0.5 },
      },
    ],
  })
}

onMounted(fetchChart)
watch(() => route.params.code, (newCode) => {
  code.value = newCode
  fetchChart()
})
</script>

<style scoped>
.stock-detail { padding: 20px; }
.chart-card { margin-bottom: 20px; }
</style>

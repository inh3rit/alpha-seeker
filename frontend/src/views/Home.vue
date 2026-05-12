<template>
  <div class="home">
    <el-row :gutter="20" class="section">
      <el-col :span="24">
        <h2>今日推荐</h2>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="8" v-for="rec in recommendations" :key="rec.code">
        <el-card shadow="hover" class="rec-card" @click="$router.push(`/stock/${rec.code}`)">
          <template #header>
            <div class="card-header">
              <span class="stock-code">{{ rec.code }}</span>
              <el-tag :type="actionTag(rec.suggested_action)" size="small">
                {{ actionText(rec.suggested_action) }}
              </el-tag>
            </div>
          </template>
          <div class="card-body">
            <div class="score">评分: <strong>{{ rec.score }}</strong></div>
            <div class="reason">{{ rec.reason }}</div>
            <div class="risk">
              风险: <el-tag :type="riskTag(rec.risk_level)" size="small">{{ riskText(rec.risk_level) }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="recommendations.length === 0" description="暂无推荐数据，请先运行策略" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const recommendations = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/api/recommendations/daily')
    recommendations.value = data.recommendations || []
  } catch (e) {
    console.error('获取推荐失败:', e)
  }
})

const actionText = (action) => ({ buy: '买入', hold: '观察', sell: '卖出' }[action] || action)
const actionTag = (action) => ({ buy: 'success', hold: 'warning', sell: 'danger' }[action] || '')
const riskText = (level) => ({ low: '低', medium: '中', high: '高' }[level] || level)
const riskTag = (level) => ({ low: 'success', medium: 'warning', high: 'danger' }[level] || '')
</script>

<style scoped>
.home { padding: 20px; }
.section { margin-bottom: 20px; }
.rec-card { margin-bottom: 16px; cursor: pointer; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.stock-code { font-weight: bold; font-size: 16px; }
.score { font-size: 18px; margin-bottom: 8px; }
.reason { color: #666; margin-bottom: 8px; }
</style>

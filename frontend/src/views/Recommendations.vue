<template>
  <div class="recommendations">
    <h2>每日推荐清单</h2>
    <el-table :data="recommendations" stripe style="width: 100%">
      <el-table-column prop="code" label="代码" width="100" />
      <el-table-column prop="score" label="评分" width="80" sortable />
      <el-table-column prop="suggested_action" label="建议" width="80">
        <template #default="{ row }">
          <el-tag :type="actionTag(row.suggested_action)" size="small">
            {{ actionText(row.suggested_action) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="risk_level" label="风险" width="80">
        <template #default="{ row }">
          <el-tag :type="riskTag(row.risk_level)" size="small">
            {{ riskText(row.risk_level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="理由" />
      <el-table-column label="操作" width="80">
        <template #default="{ row }">
          <el-button size="small" @click="$router.push(`/stock/${row.code}`)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="recommendations.length === 0" description="暂无推荐" />
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

const actionText = (a) => ({ buy: '买入', hold: '观察', sell: '卖出' }[a] || a)
const actionTag = (a) => ({ buy: 'success', hold: 'warning', sell: 'danger' }[a] || '')
const riskText = (l) => ({ low: '低', medium: '中', high: '高' }[l] || l)
const riskTag = (l) => ({ low: 'success', medium: 'warning', high: 'danger' }[l] || '')
</script>

<style scoped>
.recommendations { padding: 20px; }
</style>

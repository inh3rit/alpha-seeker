<template>
  <div class="rankings">
    <h2>综合评分排行榜</h2>
    <el-table :data="items" stripe style="width: 100%" v-loading="loading">
      <el-table-column type="index" label="排名" width="60" />
      <el-table-column prop="code" label="代码" width="100">
        <template #default="{ row }">
          <el-link @click="$router.push(`/stock/${row.code}`)">{{ row.code }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="score" label="综合分" width="100" sortable />
      <el-table-column prop="dual_ma" label="双均线" width="100" />
      <el-table-column prop="macd" label="MACD" width="100" />
      <el-table-column prop="rsi" label="RSI" width="100" />
    </el-table>
    <el-empty v-if="!loading && items.length === 0" description="暂无排行数据" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const items = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/rankings/score', { params: { top: 20 } })
    items.value = data.items || []
  } catch (e) {
    console.error('获取排行榜失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.rankings { padding: 20px; }
</style>

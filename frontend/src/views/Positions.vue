<template>
  <div class="positions">
    <div class="header">
      <h2>我的持仓</h2>
      <el-button type="primary" @click="showAddDialog = true">添加持仓</el-button>
    </div>

    <el-table :data="positions" stripe style="width: 100%">
      <el-table-column prop="code" label="代码" width="100" />
      <el-table-column prop="buy_date" label="买入日期" width="120" />
      <el-table-column prop="buy_price" label="买入价" width="100" />
      <el-table-column prop="quantity" label="数量" width="80" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'holding' ? 'success' : 'info'" size="small">
            {{ row.status === 'holding' ? '持有' : '已卖' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="deletePosition(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="positions.length === 0" description="暂无持仓" />

    <el-dialog v-model="showAddDialog" title="添加持仓" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="代码">
          <el-input v-model="form.code" placeholder="如 600519" />
        </el-form-item>
        <el-form-item label="买入日期">
          <el-date-picker v-model="form.buy_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="买入价">
          <el-input-number v-model="form.buy_price" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="form.quantity" :min="1" :step="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addPosition">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const positions = ref([])
const showAddDialog = ref(false)
const form = ref({ code: '', buy_date: '', buy_price: 0, quantity: 100 })

const fetchPositions = async () => {
  try {
    const { data } = await api.get('/api/positions')
    positions.value = data
  } catch (e) {
    console.error('获取持仓失败:', e)
  }
}

const addPosition = async () => {
  try {
    await api.post('/api/positions', form.value)
    ElMessage.success('添加成功')
    showAddDialog.value = false
    form.value = { code: '', buy_date: '', buy_price: 0, quantity: 100 }
    await fetchPositions()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const deletePosition = async (id) => {
  try {
    await api.delete(`/api/positions/${id}`)
    ElMessage.success('删除成功')
    await fetchPositions()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchPositions)
</script>

<style scoped>
.positions { padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>

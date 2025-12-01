<template>
  <div class="activation-code-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>激活码管理</h2>
        <el-button type="primary" @click="showGenerateDialog = true">
          <el-icon>
            <Plus />
          </el-icon> 批量生成
        </el-button>
      </div>
    </el-card>

    <el-card shadow="hover">
      <div class="filter-bar">
        <el-select v-model="filter.role" placeholder="适用角色" clearable style="width: 120px;" @change="loadCodes">
          <el-option label="教师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
        <el-select v-model="filter.status" placeholder="使用状态" clearable style="width: 120px;" @change="loadCodes">
          <el-option label="未使用" value="unused" />
          <el-option label="已使用" value="used" />
          <el-option label="已过期" value="expired" />
        </el-select>
      </div>

      <el-table :data="codes" v-loading="loading" style="width: 100%;">
        <el-table-column prop="code" label="激活码" width="280">
          <template #default="{ row }">
            <code>{{ row.code }}</code>
            <el-button type="primary" link size="small" @click="copyCode(row.code)">复制</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="适用角色" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.role === 'teacher' ? '教师' : '管理员' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usedBy" label="使用者" width="120" />
        <el-table-column prop="expiresAt" label="过期时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" link :disabled="row.status === 'used'" @click="deleteCode(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无激活码" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="total"
        :page-sizes="[10, 20, 50]" v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        @size-change="loadCodes" @current-change="loadCodes" />
    </el-card>

    <!-- 批量生成对话框 -->
    <el-dialog v-model="showGenerateDialog" title="批量生成激活码" width="400px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="适用角色" required>
          <el-select v-model="generateForm.role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成数量" required>
          <el-input-number v-model="generateForm.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker v-model="generateForm.expiresAt" type="date" placeholder="选择过期日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="generateForm.remark" placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" :loading="generateLoading" @click="generateCodes">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 管理端 - 激活码管理视图
 * 管理激活码、批量生成、删除等功能
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getActivationCodes,
  generateActivationCodes,
  deleteActivationCode
} from '@/api/admin/activation'

// 加载状态
const loading = ref(true)
const generateLoading = ref(false)

// 筛选条件
const filter = reactive({ role: '', status: '' })

// 分页
const pagination = reactive({ page: 1, pageSize: 10 })
const total = ref(0)

// 激活码列表
const codes = ref([])

// 生成对话框
const showGenerateDialog = ref(false)
const generateForm = reactive({
  role: 'teacher',
  count: 10,
  expiresAt: null,
  remark: ''
})

/**
 * 加载激活码列表
 */
const loadCodes = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filter.role) params.code_type = filter.role
    if (filter.status === 'used') params.is_used = true
    if (filter.status === 'unused') params.is_used = false
    if (filter.status === 'expired') params.expired = true

    const res = await getActivationCodes(params)
    // 拦截器已提取data字段
    const now = new Date()
    const codeList = res.codes || []
    codes.value = (Array.isArray(codeList) ? codeList : []).map(c => ({
      id: c.code_id || c.id,
      code: c.code,
      role: c.code_type || c.role,
      status: getCodeStatus(c, now),
      usedBy: c.used_by_username || c.used_by || '-',
      expiresAt: formatDate(c.expires_at)
    }))
    total.value = res.total || codes.value.length
  } catch (error) {
    console.error('获取激活码列表失败:', error)
    ElMessage.error('获取激活码列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 获取激活码状态
 */
const getCodeStatus = (code, now = new Date()) => {
  if (code.used || code.used_at) return 'used'
  if (code.expires_at && new Date(code.expires_at) < now) return 'expired'
  return 'unused'
}

/**
 * 格式化日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

/**
 * 获取状态类型
 */
const getStatusType = (status) => ({ unused: 'success', used: 'info', expired: 'danger' }[status])

/**
 * 获取状态文本
 */
const getStatusText = (status) => ({ unused: '未使用', used: '已使用', expired: '已过期' }[status])

/**
 * 生成激活码
 */
const generateCodes = async () => {
  if (!generateForm.role) {
    ElMessage.warning('请选择适用角色')
    return
  }

  generateLoading.value = true
  try {
    const data = {
      code_type: generateForm.role,
      count: generateForm.count
    }
    if (generateForm.expiresAt) {
      // 后端接受 expires_days（整数天数）
      const now = new Date()
      const expires = new Date(generateForm.expiresAt)
      const diffDays = Math.ceil((expires - now) / (1000 * 60 * 60 * 24))
      if (diffDays > 0) data.expires_days = diffDays
    }
    if (generateForm.remark) {
      data.remark = generateForm.remark
    }

    const res = await generateActivationCodes(data)
    // 注意：响应拦截器已自动提取data字段
    ElMessage.success(`成功生成 ${generateForm.count} 个激活码`)
    showGenerateDialog.value = false
    Object.assign(generateForm, { role: 'teacher', count: 10, expiresAt: null, remark: '' })
    await loadCodes()
  } catch (error) {
    console.error('生成激活码失败:', error)
    ElMessage.error('生成激活码失败')
  } finally {
    generateLoading.value = false
  }
}

/**
 * 复制激活码
 */
const copyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    ElMessage.success('激活码已复制')
  } catch {
    ElMessage.warning(`当前环境不支持自动复制，请手动复制激活码：${code}`)
  }
}

/**
 * 删除激活码
 */
const deleteCode = async (code) => {
  try {
    await ElMessageBox.confirm('确定删除该激活码吗？', '删除确认', { type: 'warning' })
    await deleteActivationCode(code.id)
    ElMessage.success('删除成功')
    await loadCodes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除激活码失败:', error)
      ElMessage.error('删除激活码失败')
    }
  }
}

onMounted(() => {
  loadCodes()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

code {
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
}
</style>

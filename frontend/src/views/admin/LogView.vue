<template>
  <div class="log-view">
    <el-card class="page-header" shadow="never">
      <h2>系统日志</h2>
    </el-card>

    <el-card v-loading="loading" shadow="hover">
      <div class="filter-bar">
        <el-select v-model="filter.level" placeholder="日志状态" clearable style="width: 120px;" @change="search">
          <el-option label="成功 (INFO)" value="info" />
          <el-option label="失败 (ERROR)" value="error" />
        </el-select>
        <el-date-picker v-model="filter.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
          end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="search" />
        <el-input v-model="filter.keyword" placeholder="搜索描述/用户/路径" clearable style="width: 250px;"
          @keyup.enter="search" />
        <el-button type="primary" @click="search">搜索</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <el-table :data="operationLogs" style="width: 100%;" border stripe>
        <el-table-column prop="createdAt" label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.isSuccess ? 'success' : 'danger'">
              {{ row.isSuccess ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usernameText" label="操作用户" width="120">
          <template #default="{ row }">{{ row.usernameText || '匿名' }}</template>
        </el-table-column>
        <el-table-column prop="moduleDisplayText" label="模块" width="120">
          <template #default="{ row }">{{ row.moduleDisplayText }}</template>
        </el-table-column>
        <el-table-column prop="actionTypeDisplayText" label="操作" width="120">
          <template #default="{ row }">{{ row.actionTypeDisplayText }}</template>
        </el-table-column>
        <el-table-column prop="descriptionText" label="描述" show-overflow-tooltip min-width="200">
          <template #default="{ row }">
            <span>{{ row.descriptionText || '-' }}</span>
            <span v-if="!row.isSuccess && row.errorMessageText" class="error-inline-text">
              (错误: {{ row.errorMessageText }})
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ipAddressText" label="IP地址" width="140">
          <template #default="{ row }">{{ row.ipAddressText || '-' }}</template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无日志数据" />
        </template>
      </el-table>

      <div class="pagination-container">
        <el-pagination layout="total, sizes, prev, pager, next, jumper" :total="totalLogCount"
          v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange" @current-change="handlePageChange" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getLogs } from '@/api/admin/log'

/**
 * 统一收敛文本字段，避免模板直接消费不稳定 payload。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return String(rawValue)
  }
  return ''
}

/**
 * 统一收敛数值字段，避免分页统计出现 NaN。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 统一收敛布尔字段，避免状态展示受后端脏值影响。
 * @param {unknown} rawValue
 * @param {boolean} fallbackValue
 * @returns {boolean}
 */
const normalizeBoolean = (rawValue, fallbackValue = false) => {
  if (typeof rawValue === 'boolean') {
    return rawValue
  }
  if (typeof rawValue === 'number') {
    return rawValue !== 0
  }
  if (typeof rawValue === 'string') {
    if (rawValue === 'true' || rawValue === '1') {
      return true
    }
    if (rawValue === 'false' || rawValue === '0') {
      return false
    }
  }
  return fallbackValue
}

/**
 * 将任意 payload 收敛为对象数组。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * @typedef {Object} OperationLogModel
 * @property {string} logId
 * @property {string} createdAt
 * @property {boolean} isSuccess
 * @property {string} usernameText
 * @property {string} moduleText
 * @property {string} moduleDisplayText
 * @property {string} actionTypeText
 * @property {string} actionTypeDisplayText
 * @property {string} descriptionText
 * @property {string} errorMessageText
 * @property {string} ipAddressText
 */

/**
 * 构造默认日志模型，确保模板只读取稳定字段。
 * @returns {OperationLogModel}
 */
const buildDefaultOperationLog = () => ({
  logId: '',
  createdAt: '',
  isSuccess: true,
  usernameText: '',
  moduleText: '',
  moduleDisplayText: '',
  actionTypeText: '',
  actionTypeDisplayText: '',
  descriptionText: '',
  errorMessageText: '',
  ipAddressText: ''
})

/**
 * 将单条日志统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawLog
 * @returns {OperationLogModel}
 */
const normalizeOperationLog = (rawLog) => {
  const moduleText = normalizeText(rawLog?.module)
  const actionTypeText = normalizeText(rawLog?.action_type)

  return {
    ...buildDefaultOperationLog(),
    logId: normalizeText(rawLog?.id),
    createdAt: normalizeText(rawLog?.created_at),
    isSuccess: normalizeBoolean(rawLog?.is_success, true),
    usernameText: normalizeText(rawLog?.username),
    moduleText,
    moduleDisplayText: normalizeText(rawLog?.module_display) || moduleText,
    actionTypeText,
    actionTypeDisplayText: normalizeText(rawLog?.action_type_display) || actionTypeText,
    descriptionText: normalizeText(rawLog?.description),
    errorMessageText: normalizeText(rawLog?.error_message),
    ipAddressText: normalizeText(rawLog?.ip_address)
  }
}

/**
 * 收敛日志列表响应，隔离 results/count 等后端字段。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ records: OperationLogModel[], totalCount: number }}
 */
const normalizeOperationLogListPayload = (rawPayload) => ({
  records: normalizeListFromPayload(rawPayload?.results).map((rawLog) => normalizeOperationLog(rawLog)),
  totalCount: normalizeNumber(rawPayload?.count)
})

const loading = ref(false)
const filter = reactive({ level: '', dateRange: null, keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20 })
const totalLogCount = ref(0)
const operationLogs = ref([])

/**
 * 加载日志列表
 */
const loadLogs = async () => {
  loading.value = true
  try {
    const queryParams = {
      page: pagination.page,
      size: pagination.pageSize
    }

    // 只有当有值时才添加参数
    if (filter.level) queryParams.level = filter.level
    if (filter.keyword) queryParams.keyword = filter.keyword

    if (filter.dateRange && filter.dateRange.length === 2) {
      // dateRange 已经是 YYYY-MM-DD 格式 (value-format)
      queryParams.start_date = filter.dateRange[0]
      queryParams.end_date = filter.dateRange[1]
    }

    const logListPayload = normalizeOperationLogListPayload(
      await getLogs(queryParams)
    )

    operationLogs.value = logListPayload.records
    totalLogCount.value = logListPayload.totalCount

  } catch (error) {
    console.error('获取日志失败:', error)
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

const search = () => {
  pagination.page = 1
  void loadLogs()
}

const resetFilter = () => {
  filter.level = ''
  filter.dateRange = null
  filter.keyword = ''
  search()
}

const handleSizeChange = (val) => {
  pagination.page = 1
  pagination.pageSize = val
  void loadLogs()
}

const handlePageChange = (val) => {
  pagination.page = val
  void loadLogs()
}

/**
 * 格式化时间
 */
const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  void loadLogs()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.error-inline-text {
  color: var(--danger-color, #f56c6c);
  margin-left: 5px;
}
</style>

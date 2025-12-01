<template>
  <div class="resource-list-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>课程资源</h2>
      </div>
    </el-card>

    <el-card shadow="hover">
      <div class="filter-bar">
        <el-select v-model="resourceFilter.resourceType" placeholder="资源类型" clearable style="width: 130px;"
          @change="handleResourceSearch">
          <el-option v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.optionValue"
            :label="resourceTypeOption.optionLabel" :value="resourceTypeOption.optionValue" />
        </el-select>
        <el-select v-model="resourceFilter.pointId" placeholder="按知识点筛选" clearable filterable style="width: 180px;"
          @change="handleResourceSearch">
          <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
            :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
        </el-select>
        <el-input v-model="resourceFilter.keyword" placeholder="搜索资源" clearable style="width: 200px;"
          @keyup.enter="handleResourceSearch" />
        <el-select v-model="resourceFilter.sortType" placeholder="排序方式" style="width: 140px;"
          @change="handleResourceSearch">
          <el-option label="默认排序" value="default" />
          <el-option label="按名称" value="title" />
          <el-option label="按类型" value="type" />
          <el-option label="最新创建" value="newest" />
        </el-select>
        <el-button type="primary" @click="handleResourceSearch">搜索</el-button>
      </div>

      <div v-loading="loading" class="resource-grid">
        <div v-for="resourceRecord in resourceRecords" :key="resourceRecord.resourceId" class="resource-card"
          @click="openResource(resourceRecord)">
          <div class="resource-icon">
            <el-icon :size="32">
              <VideoPlay v-if="resourceRecord.resourceTypeText === 'video'" />
              <Document v-else-if="resourceRecord.resourceTypeText === 'document'" />
              <Link v-else-if="resourceRecord.resourceTypeText === 'link'" />
              <EditPen v-else />
            </el-icon>
          </div>
          <div class="resource-info">
            <div class="resource-title">{{ resourceRecord.titleText }}</div>
            <div class="resource-meta">
              <el-tag size="small" :type="resourceRecord.typeTagType">{{ resourceRecord.typeLabel }}</el-tag>
              <el-tag v-if="resourceRecord.isServerHosted" size="small" type="success">本地资源</el-tag>
              <el-tag v-else-if="resourceRecord.hasExternalUrl" size="small" type="warning">外部链接</el-tag>
              <span v-if="resourceRecord.chapterLabel" class="chapter">{{ resourceRecord.chapterLabel }}</span>
              <span v-if="resourceRecord.durationSeconds" class="duration">{{
                formatDuration(resourceRecord.durationSeconds) }}</span>
            </div>
            <div v-if="resourceRecord.descriptionText" class="resource-desc">{{ resourceRecord.descriptionText }}</div>
            <div v-if="resourceRecord.knowledgePointList.length" class="resource-kps">
              <el-tag v-for="knowledgePoint in resourceRecord.knowledgePointList" :key="knowledgePoint.pointId"
                size="small" type="info" class="knowledge-point-tag">{{ knowledgePoint.pointName }}</el-tag>
            </div>
          </div>
        </div>
        <el-empty v-if="!loading && !resourceRecords.length" description="暂无学习资源" />
      </div>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="totalResourceCount"
        :page-sizes="[12, 24, 48]" v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        @size-change="handleResourcePageSizeChange" @current-change="handleResourcePageChange" />
    </el-card>
  </div>
</template>

<script setup>
/**
 * 学生端课程资源页
 * 对资源列表与知识点筛选做内部模型收敛，避免模板直接消费后端 snake_case 字段。
 */
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, Document, Link, EditPen } from '@element-plus/icons-vue'
import { getStudentResources, getKnowledgePoints } from '@/api/student/knowledge'
import { toBackendAbsoluteUrl } from '@/api/backend'
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()
const courseId = computed(() => courseStore.courseId)

const resourceTypeOptions = [
  { optionLabel: '视频', optionValue: 'video' },
  { optionLabel: '文档', optionValue: 'document' },
  { optionLabel: '外部链接', optionValue: 'link' },
  { optionLabel: '练习', optionValue: 'exercise' }
]

const resourceTypeLabelMap = {
  video: '视频',
  document: '文档',
  link: '链接',
  exercise: '练习'
}

const resourceTypeTagMap = {
  video: 'danger',
  document: '',
  link: 'warning',
  exercise: 'success'
}

/**
 * 收敛文本字段，避免模板层直接处理动态值。
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
 * 收敛标识符字段。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  return normalizeText(rawValue).trim()
}

/**
 * 收敛数值字段，避免 NaN 影响排序与展示。
 * @param {unknown} rawValue
 * @param {number} fallbackValue
 * @returns {number}
 */
const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

/**
 * 将任意 payload 收敛为数组。
 * @param {unknown} rawValue
 * @returns {Array<Record<string, unknown>>}
 */
const normalizeListFromPayload = (rawValue) => {
  return Array.isArray(rawValue) ? rawValue : []
}

/**
 * 收敛资源类型，统一页面内分支判断。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeResourceType = (rawValue) => {
  const resourceTypeText = normalizeText(rawValue).trim()
  return resourceTypeText || 'document'
}

/**
 * @typedef {Object} KnowledgePointOptionModel
 * @property {string} pointId
 * @property {string} pointName
 */

/**
 * @typedef {Object} ResourceRecordModel
 * @property {string} resourceId
 * @property {string} titleText
 * @property {string} resourceTypeText
 * @property {string} typeLabel
 * @property {string} typeTagType
 * @property {string} descriptionText
 * @property {string} resourceUrl
 * @property {string} fileUrl
 * @property {string} openUrl
 * @property {boolean} isServerHosted
 * @property {boolean} hasExternalUrl
 * @property {number} durationSeconds
 * @property {string} chapterLabel
 * @property {number} sortOrder
 * @property {string} createdAtText
 * @property {KnowledgePointOptionModel[]} knowledgePointList
 */

/**
 * 构造默认知识点选项模型。
 * @returns {KnowledgePointOptionModel}
 */
const buildDefaultKnowledgePointOption = () => ({
  pointId: '',
  pointName: ''
})

/**
 * 构造默认资源模型。
 * @returns {ResourceRecordModel}
 */
const buildDefaultResourceRecord = () => ({
  resourceId: '',
  titleText: '',
  resourceTypeText: 'document',
  typeLabel: '文档',
  typeTagType: '',
  descriptionText: '',
  resourceUrl: '',
  fileUrl: '',
  openUrl: '',
  isServerHosted: false,
  hasExternalUrl: false,
  durationSeconds: 0,
  chapterLabel: '',
  sortOrder: 0,
  createdAtText: '',
  knowledgePointList: []
})

/**
 * 将知识点数据映射为稳定选项模型。
 * @param {Record<string, unknown> | null | undefined} rawKnowledgePoint
 * @returns {KnowledgePointOptionModel}
 */
const normalizeKnowledgePointOption = (rawKnowledgePoint) => ({
  ...buildDefaultKnowledgePointOption(),
  pointId: normalizeIdentifier(rawKnowledgePoint?.point_id ?? rawKnowledgePoint?.id),
  pointName: normalizeText(rawKnowledgePoint?.point_name ?? rawKnowledgePoint?.name) || '未命名知识点'
})

/**
 * 将资源接口返回收敛为页面稳定模型。
 * @param {Record<string, unknown> | null | undefined} rawResource
 * @returns {ResourceRecordModel}
 */
const normalizeResourceRecord = (rawResource) => {
  const resourceTypeText = normalizeResourceType(rawResource?.resource_type ?? rawResource?.type)
  const resourceUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.url).trim())
  const fileUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.file).trim())
  const openUrl = resourceUrl || fileUrl

  return {
    ...buildDefaultResourceRecord(),
    resourceId: normalizeIdentifier(rawResource?.resource_id ?? rawResource?.id),
    titleText: normalizeText(rawResource?.title),
    resourceTypeText,
    typeLabel: resourceTypeLabelMap[resourceTypeText] || resourceTypeText,
    typeTagType: resourceTypeTagMap[resourceTypeText] || 'info',
    descriptionText: normalizeText(rawResource?.description),
    resourceUrl,
    fileUrl,
    openUrl,
    isServerHosted: Boolean(fileUrl && !resourceUrl),
    hasExternalUrl: Boolean(resourceUrl),
    durationSeconds: normalizeNumber(rawResource?.duration),
    chapterLabel: normalizeText(rawResource?.chapter_number ?? rawResource?.chapter),
    sortOrder: normalizeNumber(rawResource?.sort_order),
    createdAtText: normalizeText(rawResource?.created_at),
    knowledgePointList: normalizeListFromPayload(rawResource?.knowledge_points ?? rawResource?.points)
      .map((rawKnowledgePoint) => normalizeKnowledgePointOption(rawKnowledgePoint))
  }
}

/**
 * 收敛资源列表响应。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {{ records: ResourceRecordModel[], totalCount: number }}
 */
const normalizeResourceListPayload = (rawPayload) => ({
  records: normalizeListFromPayload(rawPayload?.resources)
    .map((rawResource) => normalizeResourceRecord(rawResource)),
  totalCount: normalizeNumber(rawPayload?.total)
})

/**
 * 收敛知识点列表响应。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @returns {KnowledgePointOptionModel[]}
 */
const normalizeKnowledgePointListPayload = (rawPayload) => {
  return normalizeListFromPayload(rawPayload?.points)
    .map((rawKnowledgePoint) => normalizeKnowledgePointOption(rawKnowledgePoint))
}

const loading = ref(false)
const resourceRecords = ref([])
const totalResourceCount = ref(0)
const knowledgePointOptions = ref([])
const resourceFilter = reactive({ resourceType: '', pointId: '', keyword: '', sortType: 'default' })
const pagination = reactive({ page: 1, pageSize: 12 })

const resourceTypePriority = {
  document: 0,
  video: 1,
  exercise: 2,
  link: 3
}

const parseChapterOrder = (chapterNumber) => {
  const rawText = String(chapterNumber || '').trim()
  const matchedNumber = rawText.match(/\d+/)
  return matchedNumber ? Number(matchedNumber[0]) : Number.MAX_SAFE_INTEGER
}

const sortResources = (items) => {
  return [...items].sort((leftItem, rightItem) => {
    if (resourceFilter.sortType === 'title') {
      return leftItem.titleText.localeCompare(rightItem.titleText, 'zh-CN')
    }
    if (resourceFilter.sortType === 'type') {
      return (resourceTypePriority[leftItem.resourceTypeText] ?? 99) - (resourceTypePriority[rightItem.resourceTypeText] ?? 99)
        || leftItem.titleText.localeCompare(rightItem.titleText, 'zh-CN')
    }
    if (resourceFilter.sortType === 'newest') {
      return new Date(rightItem.createdAtText || 0).getTime() - new Date(leftItem.createdAtText || 0).getTime()
    }

    return parseChapterOrder(leftItem.chapterLabel) - parseChapterOrder(rightItem.chapterLabel)
      || leftItem.sortOrder - rightItem.sortOrder
      || (resourceTypePriority[leftItem.resourceTypeText] ?? 99) - (resourceTypePriority[rightItem.resourceTypeText] ?? 99)
      || leftItem.titleText.localeCompare(rightItem.titleText, 'zh-CN')
  })
}

const formatDuration = (seconds) => {
  const totalSeconds = normalizeNumber(seconds)
  if (!totalSeconds) return ''
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return m > 0 ? `${m}分${s > 0 ? s + '秒' : ''}` : `${s}秒`
}

const handleResourceSearch = () => {
  pagination.page = 1
  void loadResources()
}

const handleResourcePageSizeChange = (pageSize) => {
  pagination.page = 1
  pagination.pageSize = pageSize
  void loadResources()
}

const handleResourcePageChange = (pageNumber) => {
  pagination.page = pageNumber
  void loadResources()
}

const loadResources = async () => {
  if (!courseId.value) {
    ElMessage.warning('请先选择课程')
    resourceRecords.value = []
    totalResourceCount.value = 0
    return
  }
  loading.value = true
  try {
    const queryParams = {
      course_id: courseId.value,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (resourceFilter.resourceType) queryParams.type = resourceFilter.resourceType
    if (resourceFilter.pointId) queryParams.point_id = resourceFilter.pointId
    if (resourceFilter.keyword) queryParams.keyword = resourceFilter.keyword
    if (resourceFilter.sortType && resourceFilter.sortType !== 'default') queryParams.sort = resourceFilter.sortType

    const resourceListPayload = normalizeResourceListPayload(await getStudentResources(queryParams))

    resourceRecords.value = sortResources(resourceListPayload.records)
    totalResourceCount.value = resourceListPayload.totalCount
  } catch (e) {
    console.error('加载资源失败:', e)
    ElMessage.error('加载资源失败')
  } finally {
    loading.value = false
  }
}

const loadKnowledgePoints = async () => {
  if (!courseId.value) {
    knowledgePointOptions.value = []
    return
  }
  try {
    knowledgePointOptions.value = normalizeKnowledgePointListPayload(
      await getKnowledgePoints(courseId.value)
    )
  } catch (e) {
    console.error('加载知识点失败:', e)
  }
}

const openResource = (resourceRecord) => {
  const target = resourceRecord.openUrl
  if (target) {
    window.open(target, '_blank')
  } else {
    ElMessage.info('该资源暂无可打开的链接')
  }
}

onMounted(() => {
  void loadResources()
  void loadKnowledgePoints()
})

watch(courseId, () => {
  void loadResources()
  void loadKnowledgePoints()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
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

.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.resource-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.resource-card:hover {
  border-color: rgba(20, 184, 166, 0.32);
  box-shadow: 0 10px 24px rgba(18, 154, 116, 0.12);
}

.resource-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: rgba(20, 184, 166, 0.08);
  border-radius: 8px;
  color: var(--accent-cyan);
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #909399;
}

.resource-desc {
  font-size: 13px;
  color: #606266;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-kps {
  margin-top: 6px;
}

.knowledge-point-tag {
  margin-right: 4px;
}
</style>

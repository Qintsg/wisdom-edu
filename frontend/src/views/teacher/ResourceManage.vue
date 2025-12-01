<template>
  <div class="resource-manage">
    <PageHero eyebrow="Resource Library" title="资源库管理" description="维护课程视频、文档与外部链接资源，并将资源精确挂接到知识点和课程上下文中。">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon>
            <Plus />
          </el-icon> 新增资源
        </el-button>
        <el-button @click="showImportDialog">
          <el-icon>
            <Upload />
          </el-icon> 批量导入
        </el-button>
      </template>
    </PageHero>

    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="resourceSearchForm">
        <el-form-item label="资源名称">
          <el-input v-model="resourceSearchForm.titleKeyword" placeholder="搜索资源名称" clearable class="filter-input" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="resourceSearchForm.resourceType" placeholder="全部" clearable class="filter-select">
            <el-option v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.optionValue"
              :label="resourceTypeOption.optionLabel" :value="resourceTypeOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联知识点">
          <el-select v-model="resourceSearchForm.pointId" placeholder="全部" clearable class="filter-select">
            <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
              :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资源列表 -->
    <el-card class="list-card">
      <el-table :data="resourceRecords" v-loading="loading" stripe>
        <el-table-column prop="titleText" label="资源名称" min-width="200" />
        <el-table-column prop="typeLabel" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.typeTagType">{{ row.typeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pointNameText" label="关联知识点" width="150" />
        <el-table-column prop="createdAtText" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAtText) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editResource(row)">编辑</el-button>
            <el-button type="primary" link @click="previewResource(row)">预览</el-button>
            <el-button type="danger" link @click="deleteResource(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        :total="totalResourceCount" layout="total, sizes, prev, pager, next" @size-change="handleResourcePageSizeChange"
        @current-change="handleResourcePageChange" />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="isResourceDialogVisible" :title="isEditingResource ? '编辑资源' : '新增资源'" width="500px">
      <el-form ref="formRef" :model="resourceForm" :rules="formRules" label-width="100px">
        <el-form-item label="资源名称" prop="titleText">
          <el-input v-model="resourceForm.titleText" placeholder="请输入资源名称" />
        </el-form-item>
        <el-form-item label="资源类型" prop="resourceType">
          <el-select v-model="resourceForm.resourceType" placeholder="请选择类型" style="width: 100%">
            <el-option v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.optionValue"
              :label="resourceTypeOption.optionLabel" :value="resourceTypeOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联知识点" prop="pointId">
          <el-select v-model="resourceForm.pointId" placeholder="请选择知识点" style="width: 100%">
            <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
              :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="resourceForm.resourceType === 'link'" label="链接地址" prop="linkUrl">
          <el-input v-model="resourceForm.linkUrl" placeholder="请输入链接地址" />
        </el-form-item>
        <el-form-item v-else label="上传文件" prop="fileObject">
          <el-upload :auto-upload="false" :on-change="handleFileChange" :before-upload="beforeFileUpload" :limit="1"
            :file-list="fileList" :accept="getAcceptTypes(resourceForm.resourceType)">
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                {{ getUploadTipText(resourceForm.resourceType) }}
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="resourceForm.descriptionText" type="textarea" :rows="3" placeholder="请输入资源描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isResourceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="批量导入资源" width="400px">
      <el-upload drag :auto-upload="false" :on-change="handleImportFile" :limit="1" accept=".xlsx,.xls,.csv">
        <el-icon class="el-icon--upload">
          <Upload />
        </el-icon>
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 xlsx, xls, csv 格式</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 教师端资源管理页
 * 将资源列表、知识点选项与编辑表单统一收敛为内部 camelCase 模型，避免模板直接消费后端动态字段。
 */
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getResources, getResourceDetail, createResource, updateResource, deleteResource as deleteResourceApi } from '@/api/teacher/knowledge'
import { getKnowledgePoints } from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'
import { toBackendAbsoluteUrl } from '@/api/backend'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload } from '@element-plus/icons-vue'
import PageHero from '@/components/common/PageHero.vue'

const route = useRoute()
const courseStore = useCourseStore()
const routeCourseId = computed(() => {
  const parsedCourseId = Number(route.params.courseId)
  return Number.isFinite(parsedCourseId) && parsedCourseId > 0 ? parsedCourseId : null
})

const resourceTypeOptions = [
  { optionLabel: '视频', optionValue: 'video' },
  { optionLabel: '文档', optionValue: 'document' },
  { optionLabel: '链接', optionValue: 'link' }
]

const resourceTypeLabelMap = {
  video: '视频',
  document: '文档',
  link: '链接'
}

const resourceTypeTagMap = {
  video: 'primary',
  document: 'success',
  link: 'warning'
}

/**
 * 收敛文本字段。
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
 * 收敛 ID 字段。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  return normalizeText(rawValue).trim()
}

/**
 * 收敛数值字段。
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
 * 收敛资源类型。
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
 * @property {string} pointId
 * @property {string} pointNameText
 * @property {string[]} pointIdList
 * @property {KnowledgePointOptionModel[]} pointOptions
 * @property {string} linkUrl
 * @property {string} fileUrl
 * @property {string} previewUrl
 * @property {string} descriptionText
 * @property {string} createdAtText
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
  typeTagType: 'success',
  pointId: '',
  pointNameText: '',
  pointIdList: [],
  pointOptions: [],
  linkUrl: '',
  fileUrl: '',
  previewUrl: '',
  descriptionText: '',
  createdAtText: ''
})

/**
 * 收敛知识点项。
 * @param {Record<string, unknown> | null | undefined} rawPoint
 * @returns {KnowledgePointOptionModel}
 */
const normalizeKnowledgePointOption = (rawPoint) => ({
  ...buildDefaultKnowledgePointOption(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.knowledge_point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

/**
 * 解析资源关联的知识点列表。
 * @param {unknown} rawPoints
 * @returns {KnowledgePointOptionModel[]}
 */
const normalizeResourcePointOptions = (rawPoints) => {
  return normalizeListFromPayload(rawPoints)
    .map((rawPoint) => normalizeKnowledgePointOption(rawPoint))
}

/**
 * 提取资源的首个知识点 ID。
 * @param {Record<string, unknown> | null | undefined} rawResource
 * @param {KnowledgePointOptionModel[]} pointOptions
 * @returns {string}
 */
const resolvePrimaryPointId = (rawResource, pointOptions) => {
  const explicitPointId = normalizeIdentifier(rawResource?.point_id ?? rawResource?.knowledge_point_id)
  if (explicitPointId) {
    return explicitPointId
  }
  return pointOptions[0]?.pointId || ''
}

/**
 * 生成知识点展示文案。
 * @param {KnowledgePointOptionModel[]} pointOptions
 * @param {unknown} rawPointName
 * @returns {string}
 */
const resolvePointNameText = (pointOptions, rawPointName) => {
  if (pointOptions.length) {
    return pointOptions.map((pointOption) => pointOption.pointName).filter(Boolean).join(', ')
  }
  return normalizeText(rawPointName)
}

/**
 * 将资源接口数据映射为稳定模型。
 * @param {Record<string, unknown> | null | undefined} rawResource
 * @returns {ResourceRecordModel}
 */
const normalizeResourceRecord = (rawResource) => {
  const pointOptions = normalizeResourcePointOptions(rawResource?.points ?? rawResource?.knowledge_points)
  const resourceTypeText = normalizeResourceType(rawResource?.resource_type ?? rawResource?.type)
  const linkUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.url).trim())
  const fileUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.file).trim())

  return {
    ...buildDefaultResourceRecord(),
    resourceId: normalizeIdentifier(rawResource?.resource_id ?? rawResource?.id),
    titleText: normalizeText(rawResource?.title),
    resourceTypeText,
    typeLabel: resourceTypeLabelMap[resourceTypeText] || resourceTypeText,
    typeTagType: resourceTypeTagMap[resourceTypeText] || 'info',
    pointId: resolvePrimaryPointId(rawResource, pointOptions),
    pointNameText: resolvePointNameText(pointOptions, rawResource?.point_name),
    pointIdList: pointOptions.map((pointOption) => pointOption.pointId).filter(Boolean),
    pointOptions,
    linkUrl,
    fileUrl,
    previewUrl: linkUrl || fileUrl,
    descriptionText: normalizeText(rawResource?.description),
    createdAtText: normalizeText(rawResource?.created_at)
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
    .map((rawPoint) => normalizeKnowledgePointOption(rawPoint))
}

/**
 * 构造默认资源表单。
 * @returns {{ resourceId: string, titleText: string, resourceType: string, pointId: string, linkUrl: string, descriptionText: string, fileObject: File | null }}
 */
const buildDefaultResourceForm = () => ({
  resourceId: '',
  titleText: '',
  resourceType: '',
  pointId: '',
  linkUrl: '',
  descriptionText: '',
  fileObject: null
})

const loading = ref(false)
const resourceRecords = ref([])
const knowledgePointOptions = ref([])
const totalResourceCount = ref(0)

const resourceSearchForm = reactive({
  titleKeyword: '',
  resourceType: '',
  pointId: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10
})

const isResourceDialogVisible = ref(false)
const isEditingResource = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const fileList = ref([])

const resourceForm = reactive(buildDefaultResourceForm())

const formRules = {
  titleText: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  resourceType: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  pointId: [{ required: true, message: '请选择关联知识点', trigger: 'change' }]
}

const importDialogVisible = ref(false)
const importing = ref(false)
const importFile = ref(null)

const ensureCourseId = async () => {
  if (routeCourseId.value) {
    return courseStore.ensureCourse(routeCourseId.value)
  }

  if (courseStore.courseId) {
    return courseStore.courseId
  }

  const courseList = await courseStore.fetchCourses()
  return courseStore.courseId || courseList?.[0]?.course_id || courseList?.[0]?.id || null
}

const resetResourceForm = () => {
  Object.assign(resourceForm, buildDefaultResourceForm())
}

// 文件类型和大小限制
const FILE_SIZE_LIMITS = {
  video: 500 * 1024 * 1024, // 500MB
  document: 50 * 1024 * 1024 // 50MB
}

const ACCEPT_TYPES = {
  video: '.mp4,.webm,.ogg',
  document: '.pdf,.doc,.docx,.ppt,.pptx'
}

const getAcceptTypes = (type) => ACCEPT_TYPES[type] || ''

const getUploadTipText = (resourceType) => {
  return resourceType === 'video'
    ? '支持 mp4, webm, ogg 格式，最大 500MB'
    : '支持 pdf, doc, docx, ppt, pptx 格式，最大 50MB'
}

const beforeFileUpload = (file) => {
  const type = resourceForm.resourceType
  const maxSize = FILE_SIZE_LIMITS[type] || 50 * 1024 * 1024

  if (file.size > maxSize) {
    const maxSizeMB = Math.round(maxSize / (1024 * 1024))
    ElMessage.error(`文件大小不能超过 ${maxSizeMB}MB`)
    return false
  }
  return true
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleDateString('zh-CN')
}

const handleSearch = () => {
  pagination.page = 1
  void fetchResources()
}

const handleResourcePageSizeChange = (pageSize) => {
  pagination.page = 1
  pagination.pageSize = pageSize
  void fetchResources()
}

const handleResourcePageChange = (pageNumber) => {
  pagination.page = pageNumber
  void fetchResources()
}

const resetSearch = () => {
  resourceSearchForm.titleKeyword = ''
  resourceSearchForm.resourceType = ''
  resourceSearchForm.pointId = ''
  handleSearch()
}

const showCreateDialog = () => {
  isEditingResource.value = false
  resetResourceForm()
  fileList.value = []
  isResourceDialogVisible.value = true
}

const editResource = async (resourceRecord) => {
  try {
    const resourceDetail = normalizeResourceRecord(
      await getResourceDetail(resourceRecord.resourceId)
    )

    isEditingResource.value = true
    Object.assign(resourceForm, {
      resourceId: resourceDetail.resourceId,
      titleText: resourceDetail.titleText,
      resourceType: resourceDetail.resourceTypeText,
      pointId: resourceDetail.pointId,
      linkUrl: resourceDetail.linkUrl,
      descriptionText: resourceDetail.descriptionText,
      fileObject: null
    })
    fileList.value = []
    isResourceDialogVisible.value = true
  } catch (error) {
    console.error('加载资源详情失败:', error)
    ElMessage.error('加载资源详情失败，请稍后重试')
  }
}

const handleFileChange = (file) => {
  resourceForm.fileObject = file.raw
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const courseId = await ensureCourseId()
    if (!courseId) {
      ElMessage.warning('请先选择课程')
      return
    }

    const formData = new FormData()
    formData.append('title', resourceForm.titleText)
    formData.append('type', resourceForm.resourceType)
    formData.append('point_id', resourceForm.pointId)
    formData.append('description', resourceForm.descriptionText || '')
    formData.append('course_id', String(courseId))

    if (resourceForm.resourceType === 'link') {
      formData.append('url', resourceForm.linkUrl)
    } else if (resourceForm.fileObject) {
      formData.append('file', resourceForm.fileObject)
    }

    if (isEditingResource.value) {
      await updateResource(resourceForm.resourceId, formData)
      ElMessage.success('更新成功')
    } else {
      await createResource(formData)
      ElMessage.success('创建成功')
    }

    isResourceDialogVisible.value = false
    await fetchResources()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const previewResource = (resourceRecord) => {
  if (resourceRecord.previewUrl) {
    window.open(resourceRecord.previewUrl, '_blank')
  } else {
    ElMessage.info('暂无预览链接')
  }
}

const deleteResource = async (resourceRecord) => {
  try {
    await ElMessageBox.confirm('确定要删除该资源吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteResourceApi(resourceRecord.resourceId)
    ElMessage.success('删除成功')
    await fetchResources()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const showImportDialog = () => {
  importFile.value = null
  importDialogVisible.value = true
}

const handleImportFile = (file) => {
  importFile.value = file.raw
}

const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  importing.value = true
  try {
    const courseId = await ensureCourseId()
    if (!courseId) {
      ElMessage.warning('请先选择课程')
      return
    }

    const formData = new FormData()
    formData.append('file', importFile.value)
    formData.append('course_id', String(courseId))
    await createResource(formData)
    ElMessage.success('导入成功')
    importDialogVisible.value = false
    await fetchResources()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    importing.value = false
  }
}

const fetchResources = async () => {
  loading.value = true
  try {
    const courseId = await ensureCourseId()
    if (!courseId) {
      resourceRecords.value = []
      totalResourceCount.value = 0
      return
    }

    const resourceListPayload = normalizeResourceListPayload(await getResources({
      course_id: courseId,
      title: resourceSearchForm.titleKeyword,
      type: resourceSearchForm.resourceType,
      point_id: resourceSearchForm.pointId,
      page: pagination.page,
      page_size: pagination.pageSize
    }))

    resourceRecords.value = resourceListPayload.records
    totalResourceCount.value = resourceListPayload.totalCount
  } catch (error) {
    console.error('获取资源列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchKnowledgePoints = async () => {
  try {
    const courseId = await ensureCourseId()
    if (!courseId) {
      knowledgePointOptions.value = []
      return
    }

    knowledgePointOptions.value = normalizeKnowledgePointListPayload(
      await getKnowledgePoints(courseId)
    )
  } catch (error) {
    console.error('获取知识点失败:', error)
  }
}

onMounted(() => {
  void fetchResources()
  void fetchKnowledgePoints()
})

watch([() => courseStore.courseId, routeCourseId], async ([newCourseId, newRouteCourseId], [oldCourseId, oldRouteCourseId]) => {
  if (newRouteCourseId && newRouteCourseId !== oldRouteCourseId) {
    await courseStore.ensureCourse(newRouteCourseId)
  }
  if (newCourseId && newCourseId !== oldCourseId) {
    await fetchResources()
    await fetchKnowledgePoints()
  }
})
</script>

<style scoped>
.resource-manage {
  display: grid;
  gap: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 20px;
}

.list-card {
  margin-bottom: 20px;
}

.filter-input {
  width: 220px;
}

.filter-select {
  width: 190px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>

import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createResource,
  deleteResource as deleteResourceApi,
  getKnowledgePoints,
  getResourceDetail,
  getResources,
  updateResource
} from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'
import {
  buildDefaultResourceForm,
  fileSizeLimits,
  formatTime,
  getAcceptTypes,
  getUploadTipText,
  normalizeKnowledgePointListPayload,
  normalizeResourceListPayload,
  normalizeResourceRecord,
  resourceTypeOptions
} from './resourceManageModels'

export function useTeacherResourceManage() {
  const route = useRoute()
  const courseStore = useCourseStore()
  const routeCourseId = computed(() => {
    const parsedCourseId = Number(route.params.courseId)
    return Number.isFinite(parsedCourseId) && parsedCourseId > 0 ? parsedCourseId : null
  })

  const loading = ref(false)
  const resourceRecords = ref([])
  const knowledgePointOptions = ref([])
  const totalResourceCount = ref(0)
  const resourceSearchForm = reactive({ titleKeyword: '', resourceType: '', pointId: '' })
  const pagination = reactive({ page: 1, pageSize: 10 })
  const isResourceDialogVisible = ref(false)
  const isEditingResource = ref(false)
  const submitting = ref(false)
  const formRef = ref(null)
  const fileList = ref([])
  const resourceForm = reactive(buildDefaultResourceForm())
  const importDialogVisible = ref(false)
  const importing = ref(false)
  const importFile = ref(null)

  const formRules = {
    titleText: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
    resourceType: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
    pointId: [{ required: true, message: '请选择关联知识点', trigger: 'change' }]
  }

  const ensureCourseId = async () => {
    if (routeCourseId.value) return courseStore.ensureCourse(routeCourseId.value)
    if (courseStore.courseId) return courseStore.courseId

    const courseList = await courseStore.fetchCourses()
    return courseStore.courseId || courseList?.[0]?.course_id || courseList?.[0]?.id || null
  }

  const resetResourceForm = () => {
    Object.assign(resourceForm, buildDefaultResourceForm())
  }

  const beforeFileUpload = (file) => {
    const type = resourceForm.resourceType
    const maxSize = fileSizeLimits[type] || 50 * 1024 * 1024

    if (file.size > maxSize) {
      const maxSizeMB = Math.round(maxSize / (1024 * 1024))
      ElMessage.error(`文件大小不能超过 ${maxSizeMB}MB`)
      return false
    }
    return true
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

  return {
    beforeFileUpload,
    deleteResource,
    editResource,
    fileList,
    formRef,
    formRules,
    formatTime,
    getAcceptTypes,
    getUploadTipText,
    handleFileChange,
    handleImportFile,
    handleResourcePageChange,
    handleResourcePageSizeChange,
    handleSearch,
    importDialogVisible,
    importing,
    isEditingResource,
    isResourceDialogVisible,
    knowledgePointOptions,
    loading,
    pagination,
    previewResource,
    resetSearch,
    resourceForm,
    resourceRecords,
    resourceSearchForm,
    resourceTypeOptions,
    showCreateDialog,
    showImportDialog,
    submitForm,
    submitImport,
    submitting,
    totalResourceCount
  }
}

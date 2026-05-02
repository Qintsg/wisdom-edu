import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createQuestion,
  deleteQuestion as apiDeleteQuestion,
  getQuestionDetail,
  getQuestions,
  updateQuestion
} from '@/api/teacher/question'
import { getKnowledgePoints } from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'
import {
  buildDefaultQuestionForm,
  difficultyOptions,
  formatScoreText,
  getDifficultyTagType,
  getOptionLabel,
  normalizeKnowledgePointListPayload,
  normalizeQuestionListPayload,
  normalizeQuestionRecord,
  normalizeText,
  questionTypeOptions,
  supportsOptions
} from './questionListModels'

export function useTeacherQuestionList() {
  const route = useRoute()
  const courseStore = useCourseStore()

  const currentCourseId = computed(() => courseStore.courseId)
  const routeCourseId = computed(() => {
    const routeCourseIdText = normalizeText(route.params.courseId)
    const parsedCourseId = Number(routeCourseIdText)
    return Number.isFinite(parsedCourseId) && parsedCourseId > 0 ? parsedCourseId : null
  })

  const loading = ref(true)
  const saveLoading = ref(false)
  const questionFilter = reactive({ questionType: '', pointId: '', keyword: '' })
  const pagination = reactive({ page: 1, pageSize: 10 })
  const totalQuestionCount = ref(0)
  const questionRecords = ref([])
  const knowledgePointOptions = ref([])
  const isQuestionDialogVisible = ref(false)
  const editingQuestionRecord = ref(null)
  const questionFormRef = ref(null)
  const questionForm = reactive(buildDefaultQuestionForm())

  const questionRules = {
    questionType: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
    contentText: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
    answerText: [{ required: true, message: '请输入正确答案', trigger: 'blur' }]
  }

  const knowledgePointNameMap = computed(() => {
    const pointNameById = {}
    knowledgePointOptions.value.forEach((knowledgePoint) => {
      pointNameById[knowledgePoint.pointId] = knowledgePoint.pointName
    })
    return pointNameById
  })

  const ensureCourseId = async () => {
    if (routeCourseId.value) return courseStore.ensureCourse(routeCourseId.value)
    if (currentCourseId.value) return currentCourseId.value

    await courseStore.fetchCourses()
    return currentCourseId.value
  }

  const resetQuestionForm = () => {
    Object.assign(questionForm, buildDefaultQuestionForm())
  }

  const openCreateDialog = () => {
    editingQuestionRecord.value = null
    resetQuestionForm()
    isQuestionDialogVisible.value = true
  }

  const loadQuestions = async () => {
    const courseId = await ensureCourseId()
    if (!courseId) {
      questionRecords.value = []
      totalQuestionCount.value = 0
      loading.value = false
      return
    }

    loading.value = true
    try {
      const queryParams = {
        course_id: courseId,
        page: pagination.page,
        size: pagination.pageSize
      }
      if (questionFilter.questionType) queryParams.type = questionFilter.questionType
      if (questionFilter.pointId) queryParams.point_id = questionFilter.pointId
      if (questionFilter.keyword) queryParams.keyword = questionFilter.keyword

      const questionListPayload = normalizeQuestionListPayload(
        await getQuestions(queryParams),
        knowledgePointNameMap.value
      )

      questionRecords.value = questionListPayload.records
      totalQuestionCount.value = questionListPayload.totalCount || questionListPayload.records.length
    } catch (error) {
      console.error('获取题目列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const loadKnowledgePoints = async () => {
    const courseId = await ensureCourseId()
    if (!courseId) {
      knowledgePointOptions.value = []
      return
    }
    try {
      knowledgePointOptions.value = normalizeKnowledgePointListPayload(
        await getKnowledgePoints(courseId)
      )
    } catch (error) {
      console.error('获取知识点列表失败:', error)
    }
  }

  const handleImportFile = async (uploadFile) => {
    const courseId = await ensureCourseId()
    const rawFile = uploadFile?.raw

    if (!courseId) {
      ElMessage.warning('请先选择课程')
      return
    }
    if (!rawFile) {
      ElMessage.warning('未检测到可导入的题目文件')
      return
    }

    const formData = new FormData()
    formData.append('file', rawFile)
    formData.append('course_id', courseId)
    try {
      const { default: request } = await import('@/api/index')
      await request.post('/api/teacher/questions/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      ElMessage.success('导入成功')
      await loadQuestions()
    } catch (error) {
      console.error('导入失败:', error)
      ElMessage.error(error?.msg || '导入失败，请检查文件格式')
    }
  }

  const handleQuestionSearch = () => {
    pagination.page = 1
    void loadQuestions()
  }

  const handleQuestionPageSizeChange = (pageSize) => {
    pagination.page = 1
    pagination.pageSize = pageSize
    void loadQuestions()
  }

  const handleQuestionPageChange = (pageNumber) => {
    pagination.page = pageNumber
    void loadQuestions()
  }

  const addOption = () => {
    questionForm.optionTextList.push('')
  }

  const removeOption = (optionIndex) => {
    questionForm.optionTextList.splice(optionIndex, 1)
  }

  const editQuestion = async (questionRecord) => {
    try {
      const questionDetail = normalizeQuestionRecord(
        await getQuestionDetail(questionRecord.questionId),
        knowledgePointNameMap.value
      )

      editingQuestionRecord.value = questionDetail
      Object.assign(questionForm, {
        questionType: questionDetail.questionTypeText,
        contentText: questionDetail.contentText,
        optionTextList: [...questionDetail.optionTextList],
        answerText: questionDetail.answerText,
        analysisText: questionDetail.analysisText,
        difficultyText: questionDetail.difficultyText,
        scoreValue: questionDetail.scoreValue ?? 1,
        pointIdList: [...questionDetail.pointIdList]
      })
      isQuestionDialogVisible.value = true
    } catch (error) {
      console.error('获取题目详情失败:', error)
      ElMessage.error('加载题目详情失败，请稍后重试')
    }
  }

  const closeCreateDialog = () => {
    isQuestionDialogVisible.value = false
    editingQuestionRecord.value = null
    resetQuestionForm()
  }

  const saveQuestion = async () => {
    if (!currentCourseId.value) {
      ElMessage.warning('请先在右上角选择课程')
      return
    }

    const questionFormElement = questionFormRef.value
    if (!questionFormElement) return

    try {
      await questionFormElement.validate()
    } catch { return }

    saveLoading.value = true
    try {
      const requestPayload = {
        course_id: currentCourseId.value,
        type: questionForm.questionType,
        content: questionForm.contentText,
        answer: questionForm.answerText,
        analysis: questionForm.analysisText,
        difficulty: questionForm.difficultyText,
        score: questionForm.scoreValue,
        points: questionForm.pointIdList
      }

      if (supportsOptions(questionForm.questionType)) {
        requestPayload.options = questionForm.optionTextList
          .map((optionText) => normalizeText(optionText).trim())
          .filter(Boolean)
          .map((contentText, optionIndex) => ({
            label: getOptionLabel(optionIndex),
            content: contentText
          }))
      }

      if (editingQuestionRecord.value) {
        await updateQuestion(editingQuestionRecord.value.questionId, requestPayload)
      } else {
        await createQuestion(requestPayload)
      }

      ElMessage.success(editingQuestionRecord.value ? '题目更新成功' : '题目创建成功')
      closeCreateDialog()
      await loadQuestions()
    } catch (error) {
      console.error('保存题目失败:', error)
      ElMessage.error('保存题目失败')
    } finally {
      saveLoading.value = false
    }
  }

  const deleteQuestion = async (questionRecord) => {
    try {
      await ElMessageBox.confirm('确定删除该题目吗？', '删除确认', { type: 'warning' })
      await apiDeleteQuestion(questionRecord.questionId)
      ElMessage.success('删除成功')
      await loadQuestions()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除题目失败:', error)
      }
    }
  }

  const initializeQuestionPage = async () => {
    await loadKnowledgePoints()
    await loadQuestions()
  }

  onMounted(() => {
    void initializeQuestionPage()
  })

  watch([currentCourseId, routeCourseId], async ([courseId, routeId], [previousCourseId, previousRouteId]) => {
    if (routeId && routeId !== previousRouteId) {
      await courseStore.ensureCourse(routeId)
    }
    if (courseId && courseId !== previousCourseId) {
      pagination.page = 1
      await initializeQuestionPage()
    }
    if (!courseId) {
      questionRecords.value = []
      knowledgePointOptions.value = []
      totalQuestionCount.value = 0
      loading.value = false
    }
  })

  return {
    addOption,
    closeCreateDialog,
    deleteQuestion,
    difficultyOptions,
    editQuestion,
    editingQuestionRecord,
    formatScoreText,
    getDifficultyTagType,
    getOptionLabel,
    handleImportFile,
    handleQuestionPageChange,
    handleQuestionPageSizeChange,
    handleQuestionSearch,
    isQuestionDialogVisible,
    knowledgePointOptions,
    loading,
    openCreateDialog,
    pagination,
    questionFilter,
    questionForm,
    questionFormRef,
    questionRecords,
    questionRules,
    questionTypeOptions,
    removeOption,
    saveLoading,
    saveQuestion,
    supportsOptions,
    totalQuestionCount
  }
}

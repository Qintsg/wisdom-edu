import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createExam as apiCreateExam,
  deleteExam as apiDeleteExam,
  getExamDetail,
  getExams,
  publishExam as apiPublishExam,
  unpublishExam as apiUnpublishExam,
  updateExam as apiUpdateExam
} from '@/api/teacher/exam'
import { getMyClasses } from '@/api/teacher/class'
import { getQuestions } from '@/api/teacher/question'
import { useCourseStore } from '@/stores/course'

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeNumber = (value, fallback = 0) => {
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : fallback
}

const normalizeIdentifier = (value) => {
  const normalizedText = normalizeText(value)
  if (!normalizedText) return null
  const parsedValue = Number(normalizedText)
  return Number.isFinite(parsedValue) ? parsedValue : normalizedText
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const parsedDate = new Date(value)
  return Number.isNaN(parsedDate.getTime()) ? '-' : parsedDate.toLocaleString('zh-CN')
}

const buildDefaultExamDetail = () => ({
  title: '',
  examTypeText: '-',
  totalScore: 0,
  passScore: 0,
  durationMinutes: 0,
  statusText: '草稿',
  statusTagType: 'info',
  questionCount: 0,
  createdAtText: '-',
  description: '',
  questions: []
})

const normalizeListFromPayload = (value, key, mapper) => {
  const payload = value && typeof value === 'object' ? value : {}
  const sourceList = Array.isArray(payload?.[key])
    ? payload[key]
    : Array.isArray(value)
      ? value
      : []
  return sourceList.map((item, index) => mapper(item, index))
}

const normalizePaginatedList = (value, key, mapper) => {
  const items = normalizeListFromPayload(value, key, mapper)
  const payload = value && typeof value === 'object' ? value : {}
  return { items, total: normalizeNumber(payload?.['total'], items.length) }
}

const examTypeLabel = (type) => ({ chapter: '章节测试', midterm: '期中作业', final: '期末作业', quiz: '随堂小测', practice: '练习' }[type] || type || '-')
const questionTypeName = (type) => ({ single: '单选', single_choice: '单选', multiple: '多选', multiple_choice: '多选', true_false: '判断', judge: '判断', fill_blank: '填空', fill: '填空', short_answer: '简答', essay: '简答' }[type] || '未知')
const questionTagType = (type) => ({ single: 'info', single_choice: 'info', multiple: 'warning', multiple_choice: 'warning', true_false: 'success', judge: 'success', fill_blank: 'info', fill: 'info', short_answer: 'danger', essay: 'danger' }[type] || 'info')

const mapExamStatus = (value) => {
  if (value === 'published') return { text: '已发布', tagType: 'success' }
  if (value === 'closed' || value === 'ended') return { text: '已结束', tagType: 'warning' }
  return { text: '草稿', tagType: 'info' }
}

const sanitizeQuestionPreview = (value) => {
  const plainText = normalizeText(value).replace(/<[^>]+>/g, '')
  return plainText.length > 80 ? `${plainText.slice(0, 80)}…` : plainText
}

const normalizeExamSummary = (value, index) => {
  const exam = value && typeof value === 'object' ? value : {}
  const status = normalizeText(exam?.['status']) || 'draft'
  const statusDisplay = mapExamStatus(status)
  const questionIds = Array.isArray(exam?.['question_ids']) ? exam['question_ids'] : []
  return {
    id: normalizeIdentifier(exam?.['exam_id'] ?? exam?.['id']) ?? index,
    title: normalizeText(exam?.['title'] ?? exam?.['exam_name']) || `作业 ${index + 1}`,
    examType: normalizeText(exam?.['exam_type'] ?? exam?.['type']) || 'chapter',
    examTypeText: examTypeLabel(exam?.['exam_type'] ?? exam?.['type'] ?? 'chapter'),
    totalScore: normalizeNumber(exam?.['total_score']),
    durationMinutes: normalizeNumber(exam?.['duration']),
    status,
    statusText: statusDisplay.text,
    statusTagType: statusDisplay.tagType,
    isDraft: status === 'draft',
    isPublished: status === 'published',
    questionIds,
    targetClassId: normalizeIdentifier(exam?.['target_class']),
    passScore: normalizeNumber(exam?.['pass_score'], 60),
    description: normalizeText(exam?.['description']),
    createdAtText: formatDateTime(exam?.['created_at'])
  }
}

const normalizeClassSummary = (value, index) => {
  const classItem = value && typeof value === 'object' ? value : {}
  return {
    id: normalizeIdentifier(classItem?.['class_id'] ?? classItem?.['id']) ?? index,
    name: normalizeText(classItem?.['class_name'] ?? classItem?.['name']) || `班级 ${index + 1}`
  }
}

const normalizeQuestionSummary = (value, index) => {
  const question = value && typeof value === 'object' ? value : {}
  const type = normalizeText(question?.['question_type'] ?? question?.['type'])
  const content = normalizeText(question?.['content'] ?? question?.['question_content'] ?? question?.['title']) || `题目 ${index + 1}`
  return {
    id: normalizeIdentifier(question?.['question_id'] ?? question?.['id']) ?? index,
    content,
    contentPreview: sanitizeQuestionPreview(content),
    type,
    typeText: questionTypeName(type),
    typeTag: questionTagType(type),
    score: normalizeNumber(question?.['score']),
    searchText: content.toLowerCase()
  }
}

const normalizeExamDetail = (value) => {
  const exam = value && typeof value === 'object' ? value : {}
  const normalizedQuestions = normalizeListFromPayload(exam, 'questions', (question, index) => normalizeQuestionSummary(question, index))
  const status = normalizeText(exam?.['status']) || 'draft'
  const statusDisplay = mapExamStatus(status)
  return {
    title: normalizeText(exam?.['title'] ?? exam?.['exam_title']) || '作业详情',
    examTypeText: examTypeLabel(exam?.['exam_type'] ?? exam?.['type'] ?? 'chapter'),
    totalScore: normalizeNumber(exam?.['total_score']),
    passScore: normalizeNumber(exam?.['pass_score'], 60),
    durationMinutes: normalizeNumber(exam?.['duration']),
    statusText: statusDisplay.text,
    statusTagType: statusDisplay.tagType,
    questionCount: normalizeNumber(exam?.['question_count'], normalizedQuestions.length),
    createdAtText: formatDateTime(exam?.['created_at']),
    description: normalizeText(exam?.['description']),
    questions: normalizedQuestions
  }
}

export function useTeacherExamManage() {
  const route = useRoute()
  const courseStore = useCourseStore()
  const currentCourseId = computed(() => courseStore.courseId)
  const routeCourseId = computed(() => {
    const routeCourseValue = normalizeIdentifier(route?.['params']?.['courseId'])
    return typeof routeCourseValue === 'number' ? routeCourseValue : null
  })

  const loading = ref(true)
  const pagination = reactive({ page: 1, pageSize: 10 })
  const examTotal = ref(0)
  const exams = ref([])
  const editingExam = ref(null)
  const classes = ref([])
  const showCreateDialog = ref(false)
  const createLoading = ref(false)
  const examFormRef = ref(null)
  const createForm = reactive({ title: '', exam_type: 'chapter', target_class: null, duration: 60, total_score: 100, pass_score: 60, questions: [], description: '' })
  const examRules = {
    title: [{ required: true, message: '请输入作业名称', trigger: 'blur' }],
    exam_type: [{ required: true, message: '请选择作业类型', trigger: 'change' }],
    questions: [{ type: 'array', required: true, min: 1, message: '请至少选择一道题目', trigger: 'change' }]
  }
  const questionList = ref([])
  const questionSearchKeyword = ref('')
  const showDetailDialog = ref(false)
  const examDetail = ref(buildDefaultExamDetail())
  const detailLoading = ref(false)

  const filteredQuestionList = computed(() => {
    const keyword = normalizeText(questionSearchKeyword.value).toLowerCase()
    return keyword ? questionList.value.filter(item => item.searchText.includes(keyword)) : questionList.value
  })
  const selectedQuestionPreview = computed(() => {
    const selectedIdSet = new Set(createForm.questions)
    return questionList.value.filter(item => selectedIdSet.has(item.id)).slice(0, 8)
  })

  const ensureCourseId = async () => {
    if (routeCourseId.value) return courseStore.ensureCourse(routeCourseId.value)
    if (currentCourseId.value) return currentCourseId.value
    await courseStore.fetchCourses()
    return currentCourseId.value
  }

  const loadExams = async () => {
    const courseId = await ensureCourseId()
    if (!courseId) {
      exams.value = []
      examTotal.value = 0
      loading.value = false
      return
    }
    loading.value = true
    try {
      const examResponse = await getExams(courseId, { page: pagination.page, page_size: pagination.pageSize })
      const normalizedExamList = normalizePaginatedList(examResponse, 'exams', (exam, index) => normalizeExamSummary(exam, index))
      exams.value = normalizedExamList.items
      examTotal.value = normalizedExamList.total
    } catch (error) {
      console.error('获取作业列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const loadClasses = async () => {
    try {
      classes.value = normalizeListFromPayload(await getMyClasses(), 'classes', (item, index) => normalizeClassSummary(item, index))
    } catch (error) {
      console.error('获取班级列表失败:', error)
    }
  }

  const loadQuestionList = async () => {
    const courseId = await ensureCourseId()
    if (!courseId) {
      questionList.value = []
      return
    }
    try {
      questionList.value = normalizeListFromPayload(
        await getQuestions({ course_id: courseId, page: 1, page_size: 100, size: 100 }),
        'questions',
        (question, index) => normalizeQuestionSummary(question, index)
      )
    } catch (error) {
      console.error('获取题目列表失败:', error)
    }
  }

  const viewExam = async (exam) => {
    showDetailDialog.value = true
    detailLoading.value = true
    try {
      examDetail.value = normalizeExamDetail(await getExamDetail(exam.id))
    } catch (error) {
      console.error('获取作业详情失败:', error)
      examDetail.value = normalizeExamDetail(exam)
    } finally {
      detailLoading.value = false
    }
  }

  const editExam = (exam) => {
    editingExam.value = exam
    Object.assign(createForm, {
      title: exam.title,
      exam_type: exam.examType,
      target_class: exam.targetClassId || null,
      duration: exam.durationMinutes,
      total_score: exam.totalScore,
      pass_score: exam.passScore || 60,
      questions: exam.questionIds || [],
      description: exam.description || ''
    })
    showCreateDialog.value = true
  }

  const resetCreateForm = () => {
    Object.assign(createForm, { title: '', exam_type: 'chapter', target_class: null, duration: 60, total_score: 100, pass_score: 60, questions: [], description: '' })
  }

  const submitExam = async () => {
    if (!currentCourseId.value) {
      ElMessage.warning('请先在右上角选择课程')
      return
    }
    try {
      await examFormRef.value.validate()
    } catch {
      return
    }
    createLoading.value = true
    try {
      const payload = {
        course_id: currentCourseId.value,
        title: createForm.title,
        exam_type: createForm.exam_type,
        target_class: createForm.target_class || undefined,
        questions: createForm.questions,
        duration: createForm.duration,
        total_score: createForm.total_score,
        pass_score: createForm.pass_score,
        description: createForm.description || undefined
      }
      if (editingExam.value) {
        await apiUpdateExam(editingExam.value.id, payload)
        ElMessage.success('作业更新成功')
      } else {
        await apiCreateExam(payload)
        ElMessage.success('作业创建成功')
      }
      showCreateDialog.value = false
      editingExam.value = null
      resetCreateForm()
      await loadExams()
    } catch (error) {
      console.error('保存作业失败:', error)
      ElMessage.error('保存作业失败')
    } finally {
      createLoading.value = false
    }
  }

  const resolvePublishClassId = async () => {
    if (!classes.value.length) await loadClasses()
    if (!classes.value.length) {
      ElMessage.warning('暂无可用班级，请先创建班级')
      return null
    }
    if (classes.value.length === 1) return classes.value[0].id
    const promptResult = await ElMessageBox.prompt(
      '请选择发布到的班级ID：\n' + classes.value.map(item => `${item.id} - ${item.name}`).join('\n'),
      '选择班级',
      { confirmButtonText: '发布', cancelButtonText: '取消', inputPlaceholder: '输入班级ID' }
    )
    const classId = Number.parseInt(normalizeText(promptResult.value), 10)
    if (!Number.isFinite(classId)) {
      ElMessage.warning('请输入有效的班级ID')
      return null
    }
    return classId
  }

  const publishExam = async (exam) => {
    try {
      const classId = await resolvePublishClassId()
      if (!classId) return
      await apiPublishExam(exam.id, { class_id: classId })
      ElMessage.success('作业发布成功')
      await loadExams()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('发布作业失败:', error)
        ElMessage.error('发布作业失败')
      }
    }
  }

  const unpublishExam = async (exam) => {
    try {
      await ElMessageBox.confirm('确定取消发布该作业吗？', '提示', { type: 'warning' })
      await apiUnpublishExam(exam.id)
      ElMessage.success('已取消发布')
      await loadExams()
    } catch (error) {
      if (error !== 'cancel') console.error('取消发布失败:', error)
    }
  }

  const deleteExam = async (exam) => {
    try {
      await ElMessageBox.confirm('确定删除该作业吗？此操作不可恢复。', '删除确认', { type: 'warning' })
      await apiDeleteExam(exam.id)
      ElMessage.success('删除成功')
      await loadExams()
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除作业失败:', error)
        ElMessage.error('删除作业失败')
      }
    }
  }

  onMounted(() => {
    loadExams()
    loadClasses()
    loadQuestionList()
  })

  watch([currentCourseId, routeCourseId], async ([courseId, routeId], [previousCourseId, previousRouteId]) => {
    if (routeId && routeId !== previousRouteId) await courseStore.ensureCourse(routeId)
    if (courseId && courseId !== previousCourseId) {
      pagination.page = 1
      await loadExams()
      await loadQuestionList()
    }
  })

  return {
    classes,
    createForm,
    createLoading,
    deleteExam,
    detailLoading,
    editExam,
    editingExam,
    examDetail,
    examFormRef,
    examRules,
    examTotal,
    exams,
    filteredQuestionList,
    loadExams,
    loading,
    pagination,
    publishExam,
    questionSearchKeyword,
    questionTagType,
    questionTypeName,
    selectedQuestionPreview,
    showCreateDialog,
    showDetailDialog,
    submitExam,
    unpublishExam,
    viewExam
  }
}

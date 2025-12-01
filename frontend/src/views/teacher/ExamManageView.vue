<template>
  <div class="exam-manage-view">
    <PageHero eyebrow="Assessment" title="作业管理" description="从当前课程题库快速组卷、发布到班级，并跟踪作业状态、题目结构与结果分析。">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon>
            <Plus />
          </el-icon> 创建作业
        </el-button>
      </template>
    </PageHero>

    <el-card shadow="hover">
      <el-table :data="exams" v-loading="loading" style="width: 100%;">
        <el-table-column prop="title" label="作业名称" />
        <el-table-column prop="examTypeText" label="类型" width="120" />
        <el-table-column prop="totalScore" label="总分" width="100" />
        <el-table-column prop="durationMinutes" label="时长(分钟)" width="100" />
        <el-table-column prop="statusText" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.statusTagType">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewExam(row)">查看</el-button>
            <el-button type="warning" link v-if="row.isDraft" @click="editExam(row)">编辑</el-button>
            <el-button type="success" link v-if="row.isDraft" @click="publishExam(row)">发布</el-button>
            <el-button type="warning" link v-if="row.isPublished" @click="unpublishExam(row)">取消发布</el-button>
            <el-button type="danger" link @click="deleteExam(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无作业，点击右上角创建" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="examTotal"
        :page-sizes="[10, 20, 50]" v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        @size-change="loadExams" @current-change="loadExams" />
    </el-card>

    <!-- 创建作业对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingExam ? '编辑作业' : '创建作业'" width="500px">
      <el-form :model="createForm" :rules="examRules" ref="examFormRef" label-width="100px">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入作业名称" />
        </el-form-item>
        <el-form-item label="作业类型" prop="exam_type">
          <el-select v-model="createForm.exam_type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="章节测试" value="chapter" />
            <el-option label="期中作业" value="midterm" />
            <el-option label="期末作业" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联班级">
          <el-select v-model="createForm.target_class" placeholder="请选择班级" style="width: 100%;" clearable>
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="作答时长">
          <el-input-number v-model="createForm.duration" :min="10" :max="300" /> 分钟
        </el-form-item>
        <el-form-item label="总分">
          <el-input-number v-model="createForm.total_score" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="及格分">
          <el-input-number v-model="createForm.pass_score" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="选择题目" prop="questions">
          <el-input v-model="questionSearchKeyword" placeholder="按题干关键词筛选题目" clearable style="margin-bottom: 8px;" />
          <el-select v-model="createForm.questions" multiple filterable collapse-tags collapse-tags-tooltip
            placeholder="请选择题目" style="width: 100%;">
            <el-option v-for="questionItem in filteredQuestionList" :key="questionItem.id" :label="questionItem.content"
              :value="questionItem.id">
              <div class="question-option-row">
                <span>{{ questionItem.content }}</span>
                <el-tag size="small" :type="questionTagType(questionItem.type)">{{ questionTypeName(questionItem.type)
                }}</el-tag>
              </div>
            </el-option>
          </el-select>
          <div v-if="createForm.questions.length" class="question-selection-summary">
            <span>已选择 {{ createForm.questions.length }} 道题目</span>
            <el-button type="primary" link @click="createForm.questions = []">清空已选</el-button>
          </div>
          <div v-if="selectedQuestionPreview.length" class="question-preview-list">
            <div v-for="questionItem in selectedQuestionPreview" :key="questionItem.id" class="question-preview-item">
              <span>{{ questionItem.content }}</span>
              <el-tag size="small" :type="questionTagType(questionItem.type)">{{ questionTypeName(questionItem.type)
              }}</el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="作业说明">
          <el-input v-model="createForm.description" type="textarea" placeholder="请输入作业说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="submitExam">{{ editingExam ? '保存' : '创建'
        }}</el-button>
      </template>
    </el-dialog>

    <!-- 作业详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="作业详情" width="720px">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="作业名称">{{ examDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="作业类型">
            <el-tag size="small">{{ examDetail.examTypeText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ examDetail.totalScore }}</el-descriptions-item>
          <el-descriptions-item label="及格分">{{ examDetail.passScore }}</el-descriptions-item>
          <el-descriptions-item label="作答时长">{{ examDetail.durationMinutes }} 分钟</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="examDetail.statusTagType">{{ examDetail.statusText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">{{ examDetail.questionCount }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ examDetail.createdAtText }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="examDetail.description" style="margin-top: 16px;">
          <strong>作业说明：</strong>
          <p style="color: #606266;">{{ examDetail.description }}</p>
        </div>

        <!-- 题目列表预览 -->
        <div v-if="(examDetail.questions || []).length" style="margin-top: 20px;">
          <h4 style="margin-bottom: 12px; font-size: 15px;">题目列表</h4>
          <el-table :data="examDetail.questions" border size="small" max-height="360">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column label="题目内容" min-width="240">
              <template #default="{ row }">
                <span>{{ row.contentPreview }}</span>
              </template>
            </el-table-column>
            <el-table-column label="题型" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.typeTag">{{ row.typeText }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="70" align="center" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 教师端 - 作业管理视图
 * 管理作业、创建作业、发布/取消发布作业等功能
 */
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHero from '@/components/common/PageHero.vue'
import {
  getExams,
  createExam as apiCreateExam,
  updateExam as apiUpdateExam,
  deleteExam as apiDeleteExam,
  publishExam as apiPublishExam,
  unpublishExam as apiUnpublishExam
} from '@/api/teacher/exam'
import { getMyClasses } from '@/api/teacher/class'
import { getQuestions } from '@/api/teacher/question'
import { useCourseStore } from '@/stores/course'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()

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
  return {
    items,
    total: normalizeNumber(payload?.['total'], items.length)
  }
}

// 题型辅助函数
const examTypeLabel = (t) => ({ chapter: '章节测试', midterm: '期中作业', final: '期末作业', quiz: '随堂小测', practice: '练习' }[t] || t || '-')
const questionTypeName = (t) => ({ single: '单选', single_choice: '单选', multiple: '多选', multiple_choice: '多选', true_false: '判断', judge: '判断', fill_blank: '填空', fill: '填空', short_answer: '简答', essay: '简答' }[t] || '未知')
const questionTagType = (t) => ({ single: 'info', single_choice: 'info', multiple: 'warning', multiple_choice: 'warning', true_false: 'success', judge: 'success', fill_blank: 'info', fill: 'info', short_answer: 'danger', essay: 'danger' }[t] || 'info')

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

// 当前课程ID
const currentCourseId = computed(() => courseStore.courseId)
const routeCourseId = computed(() => {
  const routeCourseValue = normalizeIdentifier(route?.['params']?.['courseId'])
  return typeof routeCourseValue === 'number' ? routeCourseValue : null
})

// 加载状态
const loading = ref(true)

// 分页
const pagination = reactive({ page: 1, pageSize: 10 })
const examTotal = ref(0)

// 作业列表
const exams = ref([])

// 编辑状态
const editingExam = ref(null)

// 班级列表
const classes = ref([])

// 创建对话框
const showCreateDialog = ref(false)
const createLoading = ref(false)
const examFormRef = ref(null)
const createForm = reactive({
  title: '',
  exam_type: 'chapter',
  target_class: null,
  duration: 60,
  total_score: 100,
  pass_score: 60,
  questions: [],
  description: ''
})

const examRules = {
  title: [{ required: true, message: '请输入作业名称', trigger: 'blur' }],
  exam_type: [{ required: true, message: '请选择作业类型', trigger: 'change' }],
  questions: [{ type: 'array', required: true, min: 1, message: '请至少选择一道题目', trigger: 'change' }]
}

// 题目列表（供创建作业时选择）
const questionList = ref([])
const questionSearchKeyword = ref('')
const filteredQuestionList = computed(() => {
  const keyword = normalizeText(questionSearchKeyword.value).toLowerCase()
  if (!keyword) {
    return questionList.value
  }
  return questionList.value.filter(questionItem => questionItem.searchText.includes(keyword))
})
const selectedQuestionPreview = computed(() => {
  const selectedIdSet = new Set(createForm.questions)
  return questionList.value.filter(questionItem => selectedIdSet.has(questionItem.id)).slice(0, 8)
})

const ensureCourseId = async () => {
  if (routeCourseId.value) {
    return courseStore.ensureCourse(routeCourseId.value)
  }

  if (currentCourseId.value) {
    return currentCourseId.value
  }

  await courseStore.fetchCourses()
  return currentCourseId.value
}

/**
 * 加载作业列表
 */
const loadExams = async () => {
  const courseId = await ensureCourseId()
  // 检查是否有课程ID
  if (!courseId) {
    exams.value = []
    examTotal.value = 0
    loading.value = false
    return
  }

  loading.value = true
  try {
    const examResponse = await getExams(courseId, {
      page: pagination.page,
      page_size: pagination.pageSize
    })
    const normalizedExamList = normalizePaginatedList(examResponse, 'exams', (exam, index) => normalizeExamSummary(exam, index))
    exams.value = normalizedExamList.items
    examTotal.value = normalizedExamList.total
  } catch (error) {
    console.error('获取作业列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 加载班级列表
 */
const loadClasses = async () => {
  try {
    classes.value = normalizeListFromPayload(await getMyClasses(), 'classes', (classItem, index) => normalizeClassSummary(classItem, index))
  } catch (error) {
    console.error('获取班级列表失败:', error)
  }
}

/**
 * 加载题目列表（用于创建作业时选择题目）
 */
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

/**
 * 查看考试详情 - 在对话框中显示
 */
const showDetailDialog = ref(false)
const examDetail = ref(buildDefaultExamDetail())
const detailLoading = ref(false)

const viewExam = async (exam) => {
  showDetailDialog.value = true
  detailLoading.value = true
  try {
    const { getExamDetail } = await import('@/api/teacher/exam')
    examDetail.value = normalizeExamDetail(await getExamDetail(exam.id))
  } catch (error) {
    console.error('获取作业详情失败:', error)
    examDetail.value = normalizeExamDetail(exam)
  } finally {
    detailLoading.value = false
  }
}

/**
 * 编辑作业
 */
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

/**
 * 提交创建/编辑作业
 */
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
    Object.assign(createForm, { title: '', exam_type: 'chapter', target_class: null, duration: 60, total_score: 100, pass_score: 60, questions: [], description: '' })
    await loadExams()
  } catch (error) {
    console.error('保存作业失败:', error)
    ElMessage.error('保存作业失败')
  } finally {
    createLoading.value = false
  }
}

/**
 * 发布考试 - 弹出班级选择后发布
 */
const publishExam = async (exam) => {
  try {
    // 确保有班级列表
    if (!classes.value.length) await loadClasses()
    if (!classes.value.length) {
      ElMessage.warning('暂无可用班级，请先创建班级')
      return
    }
    // 如果只有一个班级直接使用，多个则让用户选择
    const classId = classes.value.length === 1
      ? classes.value[0].id
      : Number.parseInt(normalizeText((await ElMessageBox.prompt(
        '请选择发布到的班级ID：\n' + classes.value.map(classItem => `${classItem.id} - ${classItem.name}`).join('\n'),
        '选择班级',
        { confirmButtonText: '发布', cancelButtonText: '取消', inputPlaceholder: '输入班级ID' }
      )).value), 10)
    if (!Number.isFinite(classId)) {
      ElMessage.warning('请输入有效的班级ID')
      return
    }
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

/**
 * 取消发布考试
 */
const unpublishExam = async (exam) => {
  try {
    await ElMessageBox.confirm('确定取消发布该作业吗？', '提示', { type: 'warning' })
    await apiUnpublishExam(exam.id)
    ElMessage.success('已取消发布')
    await loadExams()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消发布失败:', error)
    }
  }
}

/**
 * 删除考试
 */
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
  if (routeId && routeId !== previousRouteId) {
    await courseStore.ensureCourse(routeId)
  }
  if (courseId && courseId !== previousCourseId) {
    pagination.page = 1
    await loadExams()
    await loadQuestionList()
  }
})
</script>

<style scoped>
.exam-manage-view {
  display: grid;
  gap: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.question-option-row,
.question-preview-item,
.question-selection-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.question-option-row span,
.question-preview-item span {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.question-selection-summary {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.question-preview-list {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.question-preview-item {
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(17, 88, 69, 0.06);
}
</style>

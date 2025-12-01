<template>
  <div class="question-list-view">
    <PageHero eyebrow="Content Bank" title="题库管理" description="围绕当前课程维护题目内容、知识点关联、难度与分值，为组卷和阶段测评提供稳定题源。">
      <template #actions>
        <el-upload :auto-upload="false" :show-file-list="false" accept=".xlsx,.xls,.csv" :on-change="handleImportFile">
          <el-button plain><el-icon>
              <Upload />
            </el-icon> 批量导入</el-button>
        </el-upload>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon>
            <Plus />
          </el-icon> 添加题目
        </el-button>
      </template>
    </PageHero>

    <el-card shadow="hover">
      <div class="filter-bar">
        <el-select v-model="questionFilter.questionType" placeholder="题目类型" clearable style="width: 120px;"
          @change="handleQuestionSearch">
          <el-option v-for="typeOption in questionTypeOptions" :key="typeOption.optionValue"
            :label="typeOption.optionLabel" :value="typeOption.optionValue" />
        </el-select>
        <el-select v-model="questionFilter.pointId" placeholder="知识点" clearable style="width: 150px;"
          @change="handleQuestionSearch">
          <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
            :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
        </el-select>
        <el-input v-model="questionFilter.keyword" placeholder="搜索题目" clearable style="width: 200px;"
          @keyup.enter="handleQuestionSearch" />
        <el-button @click="handleQuestionSearch">搜索</el-button>
      </div>

      <el-table :data="questionRecords" v-loading="loading" style="width: 100%;">
        <el-table-column prop="contentText" label="题目内容" show-overflow-tooltip />
        <el-table-column prop="typeLabel" label="类型" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.typeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficultyLabel" label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="getDifficultyTagType(row.difficultyText)" size="small">
              {{ row.difficultyLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="knowledgePointText" label="知识点" width="150" />
        <el-table-column prop="scoreValue" label="分值" width="70">
          <template #default="{ row }">
            {{ formatScoreText(row.scoreValue) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="editQuestion(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteQuestion(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无题目，点击右上角添加" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="totalQuestionCount"
        :page-sizes="[10, 20, 50]" v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        @size-change="handleQuestionPageSizeChange" @current-change="handleQuestionPageChange" />
    </el-card>

    <!-- 创建/编辑题目对话框 -->
    <el-dialog v-model="isQuestionDialogVisible" :title="editingQuestionRecord ? '编辑题目' : '添加题目'" width="600px">
      <el-form :model="questionForm" :rules="questionRules" ref="questionFormRef" label-width="100px">
        <el-form-item label="题目类型" prop="questionType">
          <el-select v-model="questionForm.questionType" placeholder="请选择类型" style="width: 100%;">
            <el-option v-for="typeOption in questionTypeOptions" :key="typeOption.optionValue"
              :label="typeOption.optionLabel" :value="typeOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容" prop="contentText">
          <el-input v-model="questionForm.contentText" type="textarea" :rows="3" placeholder="请输入题目内容" />
        </el-form-item>
        <el-form-item label="选项" v-if="supportsOptions(questionForm.questionType)">
          <div v-for="(optionText, optionIndex) in questionForm.optionTextList" :key="optionIndex" class="option-item">
            <div class="option-row">
              <span class="option-label">{{ getOptionLabel(optionIndex) }}</span>
              <el-input v-model="questionForm.optionTextList[optionIndex]"
                :placeholder="`选项${getOptionLabel(optionIndex)}`" />
              <el-button v-if="questionForm.optionTextList.length > 2" type="danger" link
                @click="removeOption(optionIndex)">删除</el-button>
            </div>
          </div>
          <el-button v-if="questionForm.optionTextList.length < 8" text type="primary" @click="addOption">+
            添加选项</el-button>
        </el-form-item>
        <el-form-item label="正确答案" prop="answerText">
          <el-input v-model="questionForm.answerText" placeholder="请输入正确答案（如A或AB）" />
        </el-form-item>
        <el-form-item label="解析">
          <el-input v-model="questionForm.analysisText" type="textarea" :rows="2" placeholder="题目解析" />
        </el-form-item>
        <el-form-item label="难度" required>
          <el-select v-model="questionForm.difficultyText" style="width: 100%;">
            <el-option v-for="difficultyOption in difficultyOptions" :key="difficultyOption.optionValue"
              :label="difficultyOption.optionLabel" :value="difficultyOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="分值">
          <el-input-number v-model="questionForm.scoreValue" :min="1" :max="100" :step="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="关联知识点">
          <el-select v-model="questionForm.pointIdList" multiple placeholder="请选择知识点" style="width: 100%;">
            <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
              :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeCreateDialog">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="saveQuestion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 教师端 - 题库管理视图
 * 管理题目、添加/编辑/删除题目等功能
 */
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload } from '@element-plus/icons-vue'
import PageHero from '@/components/common/PageHero.vue'
import {
  getQuestions,
  getQuestionDetail,
  createQuestion,
  updateQuestion,
  deleteQuestion as apiDeleteQuestion
} from '@/api/teacher/question'
import { getKnowledgePoints } from '@/api/teacher/knowledge'
import { useCourseStore } from '@/stores/course'

const route = useRoute()
const courseStore = useCourseStore()

const questionTypeOptions = [
  { optionLabel: '单选题', optionValue: 'single_choice' },
  { optionLabel: '多选题', optionValue: 'multiple_choice' },
  { optionLabel: '判断题', optionValue: 'true_false' },
  { optionLabel: '填空题', optionValue: 'fill_blank' },
  { optionLabel: '简答题', optionValue: 'short_answer' },
  { optionLabel: '编程题', optionValue: 'code' }
]

const difficultyOptions = [
  { optionLabel: '简单', optionValue: 'easy' },
  { optionLabel: '中等', optionValue: 'medium' },
  { optionLabel: '困难', optionValue: 'hard' }
]

const questionTypeLabelMap = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题',
  code: '编程题'
}

const difficultyLabelMap = {
  easy: '简单',
  medium: '中等',
  hard: '困难'
}

/**
 * 收敛文本字段，避免模板直接消费动态 payload。
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
 * 收敛字符串标识符，统一页面层 ID 语义。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeIdentifier = (rawValue) => {
  return normalizeText(rawValue).trim()
}

/**
 * 收敛数值字段，避免分页与分值出现 NaN。
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
 * 收敛题目类型为稳定值。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeQuestionType = (rawValue) => {
  const questionTypeText = normalizeText(rawValue)
  return questionTypeText || 'single_choice'
}

/**
 * 收敛题目难度为稳定值。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeDifficulty = (rawValue) => {
  const difficultyText = normalizeText(rawValue)
  return difficultyText || 'medium'
}

/**
 * 收敛题目选项文本，兼容对象数组与字符串数组两种旧结构。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const normalizeQuestionOptionTextList = (rawValue) => {
  const optionTextList = normalizeListFromPayload(rawValue)
    .map((rawOption) => {
      if (rawOption && typeof rawOption === 'object') {
        return normalizeText(rawOption.content ?? rawOption.text ?? rawOption.label).trim()
      }
      return normalizeText(rawOption).trim()
    })
    .filter(Boolean)

  return optionTextList.length ? optionTextList : ['', '', '', '']
}

/**
 * 收敛题目知识点 ID 列表，兼容 ID 数组和对象数组。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const normalizeQuestionPointIdList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((rawPoint) => {
      if (rawPoint && typeof rawPoint === 'object') {
        return normalizeIdentifier(rawPoint.point_id ?? rawPoint.id ?? rawPoint.knowledge_point_id)
      }
      return normalizeIdentifier(rawPoint)
    })
    .filter(Boolean)
}

/**
 * 收敛题目答案，兼容后端可能返回对象或纯字符串。
 * @param {unknown} rawValue
 * @returns {string}
 */
const normalizeQuestionAnswerText = (rawValue) => {
  if (rawValue && typeof rawValue === 'object' && !Array.isArray(rawValue)) {
    return normalizeText(rawValue.answer ?? rawValue.value)
  }
  return normalizeText(rawValue)
}

/**
 * @typedef {Object} KnowledgePointOptionModel
 * @property {string} pointId
 * @property {string} pointName
 */

/**
 * @typedef {Object} QuestionRecordModel
 * @property {string} questionId
 * @property {string} contentText
 * @property {string} questionTypeText
 * @property {string} typeLabel
 * @property {string} difficultyText
 * @property {string} difficultyLabel
 * @property {number | null} scoreValue
 * @property {string[]} pointIdList
 * @property {string} knowledgePointText
 * @property {string[]} optionTextList
 * @property {string} answerText
 * @property {string} analysisText
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
 * 构造默认题目模型，模板层只读取该稳定结构。
 * @returns {QuestionRecordModel}
 */
const buildDefaultQuestionRecord = () => ({
  questionId: '',
  contentText: '',
  questionTypeText: 'single_choice',
  typeLabel: '单选题',
  difficultyText: 'medium',
  difficultyLabel: '中等',
  scoreValue: null,
  pointIdList: [],
  knowledgePointText: '',
  optionTextList: ['', '', '', ''],
  answerText: '',
  analysisText: ''
})

/**
 * 将后端知识点项统一映射为页面选项模型。
 * @param {Record<string, unknown> | null | undefined} rawPoint
 * @returns {KnowledgePointOptionModel}
 */
const normalizeKnowledgePointOption = (rawPoint) => ({
  ...buildDefaultKnowledgePointOption(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.knowledge_point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

/**
 * 从原始知识点对象中提取名称文本，优先使用接口已返回的 point_name/name。
 * @param {unknown} rawValue
 * @returns {string[]}
 */
const extractKnowledgePointNameList = (rawValue) => {
  return normalizeListFromPayload(rawValue)
    .map((rawPoint) => {
      if (rawPoint && typeof rawPoint === 'object') {
        return normalizeText(rawPoint.point_name ?? rawPoint.name).trim()
      }
      return ''
    })
    .filter(Boolean)
}

/**
 * 根据知识点 ID 和接口回填的对象数据生成展示文案。
 * @param {string[]} pointIdList
 * @param {Record<string, string>} pointNameById
 * @param {unknown} rawPoints
 * @returns {string}
 */
const resolveKnowledgePointText = (pointIdList, pointNameById, rawPoints) => {
  const explicitPointNames = extractKnowledgePointNameList(rawPoints)
  if (explicitPointNames.length) {
    return explicitPointNames.join(', ')
  }

  return pointIdList
    .map((pointId) => pointNameById[pointId] || '')
    .filter(Boolean)
    .join(', ')
}

/**
 * 将题目列表或详情统一映射为页面内部模型。
 * @param {Record<string, unknown> | null | undefined} rawQuestion
 * @param {Record<string, string>} pointNameById
 * @returns {QuestionRecordModel}
 */
const normalizeQuestionRecord = (rawQuestion, pointNameById) => {
  const questionTypeText = normalizeQuestionType(rawQuestion?.type ?? rawQuestion?.question_type)
  const difficultyText = normalizeDifficulty(rawQuestion?.difficulty)
  const pointIdList = normalizeQuestionPointIdList(rawQuestion?.points ?? rawQuestion?.knowledge_points)

  return {
    ...buildDefaultQuestionRecord(),
    questionId: normalizeIdentifier(rawQuestion?.question_id ?? rawQuestion?.id),
    contentText: normalizeText(rawQuestion?.content),
    questionTypeText,
    typeLabel: questionTypeLabelMap[questionTypeText] || questionTypeText,
    difficultyText,
    difficultyLabel: difficultyLabelMap[difficultyText] || difficultyText,
    scoreValue: rawQuestion?.score === undefined || rawQuestion?.score === null || rawQuestion?.score === ''
      ? null
      : normalizeNumber(rawQuestion?.score, 1),
    pointIdList,
    knowledgePointText: resolveKnowledgePointText(pointIdList, pointNameById, rawQuestion?.points ?? rawQuestion?.knowledge_points),
    optionTextList: normalizeQuestionOptionTextList(rawQuestion?.options),
    answerText: normalizeQuestionAnswerText(rawQuestion?.answer),
    analysisText: normalizeText(rawQuestion?.analysis)
  }
}

/**
 * 收敛题目列表响应，隔离 questions/total 等后端字段。
 * @param {Record<string, unknown> | null | undefined} rawPayload
 * @param {Record<string, string>} pointNameById
 * @returns {{ records: QuestionRecordModel[], totalCount: number }}
 */
const normalizeQuestionListPayload = (rawPayload, pointNameById) => ({
  records: normalizeListFromPayload(rawPayload?.questions)
    .map((rawQuestion) => normalizeQuestionRecord(rawQuestion, pointNameById)),
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
 * 构造默认题目表单，避免重置时遗漏字段。
 * @returns {{ questionType: string, contentText: string, optionTextList: string[], answerText: string, analysisText: string, difficultyText: string, scoreValue: number, pointIdList: string[] }}
 */
const buildDefaultQuestionForm = () => ({
  questionType: 'single_choice',
  contentText: '',
  optionTextList: ['', '', '', ''],
  answerText: '',
  analysisText: '',
  difficultyText: 'medium',
  scoreValue: 1,
  pointIdList: []
})

// 当前课程ID
const currentCourseId = computed(() => courseStore.courseId)
const routeCourseId = computed(() => {
  const routeCourseIdText = normalizeText(route.params.courseId)
  const parsedCourseId = Number(routeCourseIdText)
  return Number.isFinite(parsedCourseId) && parsedCourseId > 0 ? parsedCourseId : null
})

// 加载状态
const loading = ref(true)
const saveLoading = ref(false)

// 筛选条件
const questionFilter = reactive({ questionType: '', pointId: '', keyword: '' })

// 分页
const pagination = reactive({ page: 1, pageSize: 10 })
const totalQuestionCount = ref(0)

// 题目列表
const questionRecords = ref([])

// 知识点列表
const knowledgePointOptions = ref([])

// 知识点ID到名称的映射
const knowledgePointNameMap = computed(() => {
  const pointNameById = {}
  knowledgePointOptions.value.forEach((knowledgePoint) => {
    pointNameById[knowledgePoint.pointId] = knowledgePoint.pointName
  })
  return pointNameById
})

// 创建/编辑对话框
const isQuestionDialogVisible = ref(false)
const editingQuestionRecord = ref(null)
const questionFormRef = ref(null)
const questionForm = reactive(buildDefaultQuestionForm())

const questionRules = {
  questionType: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  contentText: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  answerText: [{ required: true, message: '请输入正确答案', trigger: 'blur' }]
}

/**
 * 批量导入文件处理
 */
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

const supportsOptions = (questionTypeText) => {
  return questionTypeText === 'single_choice' || questionTypeText === 'multiple_choice'
}

const getOptionLabel = (optionIndex) => {
  return String.fromCharCode(65 + optionIndex)
}

const getDifficultyTagType = (difficultyText) => {
  if (difficultyText === 'hard') {
    return 'danger'
  }
  if (difficultyText === 'medium') {
    return 'warning'
  }
  return 'success'
}

const formatScoreText = (scoreValue) => {
  return typeof scoreValue === 'number' && Number.isFinite(scoreValue)
    ? String(scoreValue)
    : '—'
}

const resetQuestionForm = () => {
  Object.assign(questionForm, buildDefaultQuestionForm())
}

const openCreateDialog = () => {
  editingQuestionRecord.value = null
  resetQuestionForm()
  isQuestionDialogVisible.value = true
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

/**
 * 统一处理查询动作，搜索时回到第一页。
 */
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

/**
 * 加载题目列表
 */
const loadQuestions = async () => {
  const courseId = await ensureCourseId()
  // 检查是否有课程ID
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

/**
 * 加载知识点列表
 */
const loadKnowledgePoints = async () => {
  const courseId = await ensureCourseId()
  if (!courseId) {
    knowledgePointOptions.value = []
    return
  }
  try {
    // 注意：getKnowledgePoints签名为(courseId, params)，第一个参数为courseId
    knowledgePointOptions.value = normalizeKnowledgePointListPayload(
      await getKnowledgePoints(courseId)
    )
  } catch (error) {
    console.error('获取知识点列表失败:', error)
  }
}

/**
 * 添加选项
 */
const addOption = () => {
  questionForm.optionTextList.push('')
}

const removeOption = (optionIndex) => {
  questionForm.optionTextList.splice(optionIndex, 1)
}

/**
 * 编辑题目
 */
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

/**
 * 关闭对话框
 */
const closeCreateDialog = () => {
  isQuestionDialogVisible.value = false
  editingQuestionRecord.value = null
  resetQuestionForm()
}

/**
 * 保存题目
 */
const saveQuestion = async () => {
  if (!currentCourseId.value) {
    ElMessage.warning('请先在右上角选择课程')
    return
  }

  const questionFormElement = questionFormRef.value
  if (!questionFormElement) {
    return
  }

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

    // 选择题传递选项 - 转换为 {label, content} 对象数组
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

    // 注意：响应拦截器已自动提取data字段
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

/**
 * 删除题目
 */
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
</script>

<style scoped>
.question-list-view {
  display: grid;
  gap: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.option-item {
  margin-bottom: 8px;
}

.option-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.option-label {
  width: 20px;
  flex-shrink: 0;
  font-weight: 600;
}
</style>

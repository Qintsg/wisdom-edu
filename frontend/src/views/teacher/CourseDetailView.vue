<template>
    <div class="course-detail-view">
        <!-- 课程信息头部 -->
        <el-card class="course-header" shadow="never">
            <div class="header-row">
                <div class="header-info">
                    <el-button text :icon="ArrowLeft" @click="$router.push('/teacher/courses')">返回课程列表</el-button>
                    <h2>{{ courseInfo.name || '课程详情' }}</h2>
                    <el-tag v-if="courseInfo.isPublic" type="success">已发布</el-tag>
                    <el-tag v-else type="info">草稿</el-tag>
                </div>
                <div class="header-actions">
                    <el-button type="primary" @click="editCourse">编辑课程</el-button>
                </div>
            </div>
            <p class="course-desc" v-if="courseInfo.description">{{ courseInfo.description }}</p>
        </el-card>

        <!-- 统计卡片 -->
        <el-row :gutter="16" class="stat-row">
            <el-col :xs="12" :sm="6">
                <el-card shadow="hover" class="stat-card">
                    <el-statistic title="班级数" :value="stats.classCount" />
                </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
                <el-card shadow="hover" class="stat-card">
                    <el-statistic title="知识点" :value="stats.knowledgeCount" />
                </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
                <el-card shadow="hover" class="stat-card">
                    <el-statistic title="题目数" :value="stats.questionCount" />
                </el-card>
            </el-col>
            <el-col :xs="12" :sm="6">
                <el-card shadow="hover" class="stat-card">
                    <el-statistic title="作业数" :value="stats.examCount" />
                </el-card>
            </el-col>
        </el-row>

        <!-- Tab 面板 -->
        <el-card shadow="hover">
            <el-tabs v-model="activeTab" type="border-card">
                <!-- 班级管理 Tab -->
                <el-tab-pane label="班级管理" name="classes">
                    <div class="tab-toolbar">
                        <el-button type="primary" size="small" @click="showCreateClassDialog = true">
                            <el-icon>
                                <Plus />
                            </el-icon> 创建班级
                        </el-button>
                    </div>
                    <el-table :data="classes" v-loading="classLoading" style="width: 100%">
                        <el-table-column prop="name" label="班级名称" />
                        <el-table-column prop="studentCount" label="学生数" width="100" />
                        <el-table-column prop="semester" label="学期" width="120" />
                        <el-table-column label="操作" width="200">
                            <template #default="{ row }">
                                <el-button type="primary" link @click="viewClass(row)">查看详情</el-button>
                                <el-button type="danger" link @click="deleteClass(row)">删除</el-button>
                            </template>
                        </el-table-column>
                        <template #empty>
                            <el-empty description="暂无班级" :image-size="60" />
                        </template>
                    </el-table>
                </el-tab-pane>

                <!-- 知识图谱 Tab -->
                <el-tab-pane label="知识图谱" name="knowledge">
                    <div class="tab-toolbar">
                        <el-button-group>
                            <el-button :type="knowledgeViewMode === 'graph' ? 'primary' : ''" size="small"
                                @click="knowledgeViewMode = 'graph'">图谱视图</el-button>
                            <el-button :type="knowledgeViewMode === 'list' ? 'primary' : ''" size="small"
                                @click="knowledgeViewMode = 'list'">列表视图</el-button>
                        </el-button-group>
                    </div>
                    <div v-if="knowledgeViewMode === 'graph'" class="graph-container" style="height: 500px;">
                        <KnowledgeGraphECharts v-if="knowledgePoints.length" :data="graphData" mode="edit" :height="500"
                            :courseId="courseId" @save="handleSaveGraph" />
                        <el-empty v-else description="暂无知识图谱数据" />
                    </div>
                    <div v-else>
                        <el-table :data="knowledgePoints" v-loading="knowledgeLoading">
                            <el-table-column prop="name" label="知识点名称" />
                            <el-table-column prop="chapter" label="章节" width="150" />
                            <el-table-column prop="difficulty" label="难度" width="80" />
                            <el-table-column prop="description" label="描述" show-overflow-tooltip />
                        </el-table>
                    </div>
                </el-tab-pane>

                <!-- 题库管理 Tab -->
                <el-tab-pane label="题库管理" name="questions">
                    <div class="tab-toolbar">
                        <el-select v-model="questionFilter.type" placeholder="题目类型" clearable size="small"
                            style="width: 120px;" @change="loadQuestions">
                            <el-option label="单选题" value="single_choice" />
                            <el-option label="多选题" value="multiple_choice" />
                            <el-option label="判断题" value="true_false" />
                            <el-option label="填空题" value="fill_blank" />
                        </el-select>
                        <el-input v-model="questionFilter.keyword" placeholder="搜索题目" clearable size="small"
                            style="width: 200px;" @keyup.enter="loadQuestions" />
                        <el-button size="small" @click="loadQuestions">搜索</el-button>
                        <el-button type="primary" size="small"
                            @click="$router.push(`/teacher/courses/${courseId}/workspace/questions`)">前往完整题库</el-button>
                    </div>
                    <el-table :data="questions" v-loading="questionLoading">
                        <el-table-column type="index" label="序号" width="60" />
                        <el-table-column label="题目内容" show-overflow-tooltip>
                            <template #default="{ row }">
                                {{ stripHtml(row.content) }}
                            </template>
                        </el-table-column>
                        <el-table-column prop="typeName" label="类型" width="100" />
                        <el-table-column prop="difficultyText" label="难度" width="80" />
                        <el-table-column prop="knowledgePointName" label="知识点" width="150" />
                        <template #empty>
                            <el-empty description="暂无题目" :image-size="60" />
                        </template>
                    </el-table>
                    <el-pagination v-if="questionTotal > 0" class="pagination" layout="total, prev, pager, next"
                        :total="questionTotal" :page-size="10" v-model:current-page="questionFilter.page"
                        @current-change="loadQuestions" />
                </el-tab-pane>

                <!-- 作业管理 Tab -->
                <el-tab-pane label="作业管理" name="exams">
                    <div class="tab-toolbar">
                        <el-button type="primary" size="small"
                            @click="$router.push('/teacher/exams')">前往完整作业管理</el-button>
                    </div>
                    <el-table :data="exams" v-loading="examLoading">
                        <el-table-column prop="title" label="作业名称" />
                        <el-table-column prop="examType" label="类型" width="120" />
                        <el-table-column prop="totalScore" label="总分" width="80" />
                        <el-table-column prop="statusText" label="状态" width="100">
                            <template #default="{ row }">
                                <el-tag :type="row.statusTagType" size="small">
                                    {{ row.statusText }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="操作" width="150">
                            <template #default="{ row }">
                                <el-button type="primary" link size="small"
                                    @click="$router.push('/teacher/exams')">管理</el-button>
                            </template>
                        </el-table-column>
                        <template #empty>
                            <el-empty description="暂无作业" :image-size="60" />
                        </template>
                    </el-table>
                </el-tab-pane>
            </el-tabs>
        </el-card>

        <!-- 创建班级对话框 -->
        <el-dialog v-model="showCreateClassDialog" title="创建班级" width="400px">
            <el-form :model="classForm" label-width="80px">
                <el-form-item label="班级名称" required>
                    <el-input v-model="classForm.name" placeholder="请输入班级名称" />
                </el-form-item>
                <el-form-item label="学期">
                    <el-input v-model="classForm.semester" placeholder="如：2025-2026第一学期" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCreateClassDialog = false">取消</el-button>
                <el-button type="primary" @click="createClass">确定</el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
/**
 * 教师端 - 课程详情视图
 * 以课程为核心，通过 Tab 管理班级、知识图谱、题库、考试
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'
import { getCourseDetail } from '@/api/teacher/course'
import { getMyClasses, createClass as apiCreateClass, deleteClass as apiDeleteClass } from '@/api/teacher/class'
import { getKnowledgePoints, getKnowledgeRelations } from '@/api/teacher/knowledge'
import { getQuestions } from '@/api/teacher/question'
import { getExams } from '@/api/teacher/exam'
import KnowledgeGraphECharts from '@/components/knowledge/KnowledgeGraphECharts.vue'

const route = useRoute()
const router = useRouter()
const courseId = computed(() => route.params['courseId'])

const normalizeText = (value) => {
    if (value === null || value === undefined) return ''
    return String(value).trim()
}

const normalizeIdentifier = (value) => {
    const normalized = normalizeText(value)
    return normalized || ''
}

const normalizeNumber = (value, fallback = 0) => {
    const parsedValue = Number(value)
    return Number.isFinite(parsedValue) ? parsedValue : fallback
}

// Utility to strip HTML tags from text
const stripHtml = (text) => {
    if (!text) return ''
    return text.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&').trim()
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const parsedDate = new Date(dateStr)
    return Number.isNaN(parsedDate.getTime()) ? '-' : parsedDate.toLocaleString('zh-CN')
}

const normalizeCourseInfo = (value) => {
    const course = value && typeof value === 'object' ? value : {}
    return {
        id: course?.['course_id'] ?? course?.['id'] ?? courseId.value,
        name: normalizeText(course?.['course_name'] ?? course?.['name']) || '课程详情',
        description: normalizeText(course?.['course_description'] ?? course?.['description']),
        isPublic: Boolean(course?.['is_public'])
    }
}

const normalizeClassSummary = (value, index) => {
    const classItem = value && typeof value === 'object' ? value : {}
    return {
        id: classItem?.['class_id'] ?? classItem?.['id'] ?? index,
        name: normalizeText(classItem?.['name'] ?? classItem?.['class_name']) || '未命名班级',
        course: normalizeText(classItem?.['course_name']) || '未关联课程',
        studentCount: normalizeNumber(classItem?.['student_count'] ?? classItem?.['studentCount']),
        semester: normalizeText(classItem?.['semester']) || '-',
        teacherName: normalizeText(classItem?.['teacher_name']) || '-',
        createdAt: formatDate(classItem?.['created_at'])
    }
}

const normalizeKnowledgePoint = (value, index) => {
    const point = value && typeof value === 'object' ? value : {}
    return {
        id: point?.['id'] ?? point?.['point_id'] ?? index,
        name: normalizeText(point?.['name'] ?? point?.['point_name']) || `知识点 ${index + 1}`,
        chapter: normalizeText(point?.['chapter_number'] ?? point?.['chapter']) || '-',
        difficulty: normalizeText(point?.['difficulty_display'] ?? point?.['difficulty']) || '-',
        description: normalizeText(point?.['description']) || '-'
    }
}

const normalizeKnowledgeRelation = (value, index) => {
    const relation = value && typeof value === 'object' ? value : {}
    return {
        id: relation?.['id'] ?? relation?.['relation_id'] ?? index,
        sourceKey: normalizeIdentifier(relation?.['source_id'] ?? relation?.['source'] ?? relation?.['pre_point_id'] ?? relation?.['pre_point']),
        sourceName: normalizeText(relation?.['source'] ?? relation?.['pre_point']),
        targetKey: normalizeIdentifier(relation?.['target_id'] ?? relation?.['target'] ?? relation?.['post_point_id'] ?? relation?.['post_point']),
        targetName: normalizeText(relation?.['target'] ?? relation?.['post_point']),
        relationType: normalizeText(relation?.['relation_type']) || 'prerequisite'
    }
}

const normalizeQuestionSummary = (value, index) => {
    const question = value && typeof value === 'object' ? value : {}
    return {
        id: question?.['question_id'] ?? question?.['id'] ?? index,
        content: normalizeText(question?.['content']) || `题目 ${index + 1}`,
        typeName: normalizeText(question?.['type_name'] ?? question?.['question_type_display'] ?? question?.['question_type'] ?? question?.['type']) || '-',
        difficultyText: normalizeText(question?.['difficulty_display'] ?? question?.['difficulty']) || '-',
        knowledgePointName: normalizeText(question?.['knowledge_point_name']) || '-'
    }
}

const mapExamStatus = (value) => {
    if (value === 'published') return { text: '已发布', tagType: 'success' }
    if (value === 'ended') return { text: '已结束', tagType: 'info' }
    return { text: '草稿', tagType: 'info' }
}

const normalizeExamSummary = (value, index) => {
    const exam = value && typeof value === 'object' ? value : {}
    const status = normalizeText(exam?.['status']) || 'draft'
    const statusDisplay = mapExamStatus(status)
    return {
        id: exam?.['exam_id'] ?? exam?.['id'] ?? index,
        title: normalizeText(exam?.['title'] ?? exam?.['exam_name'] ?? exam?.['name']) || `作业 ${index + 1}`,
        examType: normalizeText(exam?.['exam_type_display'] ?? exam?.['exam_type'] ?? exam?.['type']) || '-',
        totalScore: normalizeNumber(exam?.['total_score']),
        status,
        statusText: statusDisplay.text,
        statusTagType: statusDisplay.tagType
    }
}

const normalizeListFromPayload = (value, key, mapper) => {
    const payload = value && typeof value === 'object' ? value : {}
    const items = Array.isArray(payload?.[key])
        ? payload[key]
        : Array.isArray(value)
            ? value
            : []
    return items.map((item, index) => mapper(item, index))
}

const normalizePaginatedList = (value, key, mapper) => {
    const items = normalizeListFromPayload(value, key, mapper)
    const payload = value && typeof value === 'object' ? value : {}
    return {
        items,
        total: normalizeNumber(payload?.['total'], items.length)
    }
}

const activeTab = ref('classes')
const courseInfo = ref(normalizeCourseInfo(null))

// Stats
const stats = reactive({ classCount: 0, knowledgeCount: 0, questionCount: 0, examCount: 0 })

// Classes
const classes = ref([])
const classLoading = ref(false)
const showCreateClassDialog = ref(false)
const classForm = reactive({ name: '', semester: '' })

// Knowledge
const knowledgePoints = ref([])
const knowledgeRelations = ref([])
const knowledgeLoading = ref(false)
const knowledgeViewMode = ref('graph')

// Questions
const questions = ref([])
const questionLoading = ref(false)
const questionTotal = ref(0)
const questionFilter = reactive({ type: '', keyword: '', page: 1 })

// Exams
const exams = ref([])
const examLoading = ref(false)

// Graph data computed - 教师端不传mastery（教师端使用统一配色）
const graphData = computed(() => {
    const pointIdMap = new Map()
    const nodes = knowledgePoints.value.map((point) => {
        const normalizedId = String(point.id)
        pointIdMap.set(normalizedId, normalizedId)
        if (point.name) pointIdMap.set(point.name, normalizedId)
        return {
            id: normalizedId,
            name: point.name,
            chapter: point.chapter,
            description: point.description
        }
    })
    const edges = knowledgeRelations.value
        .map((relation) => {
            const source = pointIdMap.get(relation.sourceKey) || pointIdMap.get(relation.sourceName) || relation.sourceKey || relation.sourceName
            const target = pointIdMap.get(relation.targetKey) || pointIdMap.get(relation.targetName) || relation.targetKey || relation.targetName
            if (!source || !target) return null
            return {
                source: String(source),
                target: String(target),
                relation_type: relation.relationType
            }
        })
        .filter(Boolean)
    return { nodes, edges }
})

// Load course detail
const loadCourseDetail = async () => {
    try {
        courseInfo.value = normalizeCourseInfo(await getCourseDetail(courseId.value))
    } catch (e) {
        console.error('获取课程详情失败:', e)
    }
}

// Load classes for this course
const loadClasses = async () => {
    classLoading.value = true
    try {
        const classList = normalizePaginatedList(
            await getMyClasses({ course_id: courseId.value }),
            'classes',
            (classItem, index) => normalizeClassSummary(classItem, index)
        )
        classes.value = classList.items
        stats.classCount = classList.total
    } catch (e) {
        console.error('获取班级列表失败:', e)
    } finally {
        classLoading.value = false
    }
}

// Load knowledge points
const loadKnowledge = async () => {
    knowledgeLoading.value = true
    try {
        const [pointsRes, relationsRes] = await Promise.all([
            getKnowledgePoints(courseId.value),
            getKnowledgeRelations(courseId.value)
        ])
        knowledgePoints.value = normalizeListFromPayload(pointsRes, 'points', (point, index) => normalizeKnowledgePoint(point, index))
        knowledgeRelations.value = normalizeListFromPayload(relationsRes, 'relations', (relation, index) => normalizeKnowledgeRelation(relation, index))
        stats.knowledgeCount = knowledgePoints.value.length
    } catch (e) {
        console.error('获取知识点失败:', e)
    } finally {
        knowledgeLoading.value = false
    }
}

// Load questions
const loadQuestions = async () => {
    questionLoading.value = true
    try {
        const params = { course_id: courseId.value, page: questionFilter.page, page_size: 10 }
        if (questionFilter.type) {
            params.question_type = questionFilter.type
            params.type = questionFilter.type
        }
        const keyword = normalizeText(questionFilter.keyword)
        if (keyword) params.keyword = keyword
        const questionList = normalizePaginatedList(
            await getQuestions(params),
            'questions',
            (question, index) => normalizeQuestionSummary(question, index)
        )
        questions.value = questionList.items
        questionTotal.value = questionList.total
        stats.questionCount = questionTotal.value
    } catch (e) {
        console.error('获取题目失败:', e)
    } finally {
        questionLoading.value = false
    }
}

// Load exams
const loadExams = async () => {
    examLoading.value = true
    try {
        exams.value = normalizeListFromPayload(await getExams(courseId.value), 'exams', (exam, index) => normalizeExamSummary(exam, index))
        stats.examCount = exams.value.length
    } catch (e) {
        console.error('获取作业列表失败:', e)
    } finally {
        examLoading.value = false
    }
}

// Actions
const editCourse = () => {
    router.push(`/teacher/courses/${courseId.value}/edit`)
}

const viewClass = (cls) => {
    router.push(`/teacher/classes/${cls.id}`)
}

const createClass = async () => {
    const className = normalizeText(classForm.name)
    if (!className) {
        ElMessage.warning('请输入班级名称')
        return
    }
    try {
        await apiCreateClass({
            class_name: className,
            semester: normalizeText(classForm.semester),
            course_id: courseId.value
        })
        ElMessage.success('班级创建成功')
        showCreateClassDialog.value = false
        classForm.name = ''
        classForm.semester = ''
        await loadClasses()
    } catch (e) {
        console.error('创建班级失败:', e)
        ElMessage.error('创建班级失败')
    }
}

const deleteClass = async (cls) => {
    try {
        await ElMessageBox.confirm(`确定删除班级"${cls.name}"吗？`, '删除确认', { type: 'warning' })
        await apiDeleteClass(cls.id)
        ElMessage.success('删除成功')
        await loadClasses()
    } catch (e) {
        if (e !== 'cancel') ElMessage.error('删除失败')
    }
}

const handleSaveGraph = () => {
    ElMessage.success('图谱数据已保存')
}

onMounted(() => {
    loadCourseDetail()
    loadClasses()
    loadKnowledge()
    loadQuestions()
    loadExams()
})
</script>

<style scoped>
.course-detail-view {
    padding: 0;
}

.course-header {
    margin-bottom: 16px;
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    border: none;
    color: #fff;
}

.course-header :deep(.el-card__body) {
    padding: 20px 24px;
}

.header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-info h2 {
    margin: 0;
    font-size: 22px;
}

.header-info .el-button {
    color: rgba(255, 255, 255, 0.8);
}

.header-info .el-button:hover {
    color: #fff;
}

.header-actions .el-button {
    background: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
    color: #fff;
}

.course-desc {
    margin: 8px 0 0;
    opacity: 0.85;
    font-size: 14px;
}

.stat-row {
    margin-bottom: 16px;
}

.stat-card {
    text-align: center;
}

.tab-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}

.pagination {
    margin-top: 16px;
    justify-content: flex-end;
}

.graph-container {
    border: 1px solid #ebeef5;
    border-radius: 8px;
    overflow: hidden;
}
</style>

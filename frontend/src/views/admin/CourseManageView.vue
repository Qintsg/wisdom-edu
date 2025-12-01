<template>
  <div class="course-manage-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>课程管理</h2>
        <el-button type="primary" @click="handleAdd">
          <el-icon>
            <Plus />
          </el-icon>创建课程
        </el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" shadow="hover">
      <div class="filter-bar">
        <el-input v-model="filter.keyword" placeholder="搜索课程" clearable style="width: 200px;"
          @keyup.enter="loadCourses" />
        <el-select v-model="filter.teacherId" placeholder="负责教师" clearable style="width: 150px;" @change="loadCourses">
          <el-option v-for="t in teachers" :key="getTeacherId(t)" :label="getTeacherLabel(t)"
            :value="getTeacherId(t)" />
        </el-select>
        <el-button type="primary" @click="loadCourses">搜索</el-button>
      </div>

      <el-table :data="courses" style="width: 100%;">
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="teacherName" label="负责教师" width="120">
          <template #default="{ row }">{{ row.teacherName || '未分配' }}</template>
        </el-table-column>
        <el-table-column prop="studentCount" label="学生数" width="100">
          <template #default="{ row }">{{ row.studentCount ?? 0 }}</template>
        </el-table-column>
        <el-table-column prop="isPublic" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isPublic ? 'success' : 'info'">
              {{ row.isPublic ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" link @click="handleAssignTeacher(row)">分配教师</el-button>
            <el-button type="danger" link @click="deleteCourse(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无课程数据" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="total"
        v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" @size-change="loadCourses"
        @current-change="loadCourses" />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '创建课程'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="课程名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input type="textarea" v-model="form.description" />
        </el-form-item>
        <el-form-item label="负责教师">
          <el-select v-model="form.teacherId" placeholder="选择教师" style="width: 100%">
            <el-option v-for="t in teachers" :key="getTeacherId(t)" :label="getTeacherLabel(t)"
              :value="getTeacherId(t)" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-switch v-model="form.isPublic" active-text="发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配教师对话框 -->
    <el-dialog v-model="assignDialogVisible" title="分配教师" width="400px">
      <el-form>
        <el-form-item label="选择教师">
          <el-select v-model="assignTeacherId" placeholder="选择教师" style="width: 100%">
            <el-option v-for="t in teachers" :key="getTeacherId(t)" :label="getTeacherLabel(t)"
              :value="getTeacherId(t)" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAllCourses, createCourse, updateCourse, deleteCourse as apiDeleteCourse, assignCourseTeacher } from '@/api/admin/course'
import { getUsers } from '@/api/admin/user'

const loading = ref(false)
const filter = reactive({ keyword: '', teacherId: '' })
const pagination = reactive({ page: 1, pageSize: 10 })
const total = ref(0)
const courses = ref([])
const teachers = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null, name: '', description: '', teacherId: null, isPublic: true })

const assignDialogVisible = ref(false)
const assignCourseId = ref(null)
const assignTeacherId = ref(null)

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeBoolean = (value, defaultValue = false) => {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return value !== 0
  if (typeof value === 'string') {
    const normalizedValue = value.trim().toLowerCase()
    if (['true', '1', 'yes', 'published'].includes(normalizedValue)) return true
    if (['false', '0', 'no', 'draft'].includes(normalizedValue)) return false
  }
  return defaultValue
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const parsedDate = new Date(dateStr)
  return Number.isNaN(parsedDate.getTime()) ? '-' : parsedDate.toLocaleString('zh-CN')
}

const normalizeTeacherSummary = (value, index) => {
  const teacher = value && typeof value === 'object' ? value : {}
  return {
    id: teacher?.['user_id'] ?? teacher?.['id'] ?? index,
    username: normalizeText(teacher?.['username']),
    realName: normalizeText(teacher?.['real_name']),
    displayName: normalizeText(teacher?.['real_name'] ?? teacher?.['username']) || '未命名教师'
  }
}

const normalizeTeacherList = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawTeachers = Array.isArray(payload?.['users']) ? payload['users'] : []
  return rawTeachers.map((teacher, index) => normalizeTeacherSummary(teacher, index))
}

const normalizeCourseSummary = (value, index) => {
  const course = value && typeof value === 'object' ? value : {}
  const studentCount = Number(course?.['student_count'])
  return {
    id: course?.['id'] ?? course?.['course_id'] ?? index,
    name: normalizeText(course?.['name'] ?? course?.['course_name']) || '未命名课程',
    description: normalizeText(course?.['description'] ?? course?.['course_description']),
    teacherId: course?.['teacher_id'] ?? null,
    teacherName: normalizeText(course?.['teacher_name']),
    studentCount: Number.isFinite(studentCount) ? studentCount : 0,
    isPublic: normalizeBoolean(course?.['is_public']),
    createdAt: formatDate(course?.['created_at'])
  }
}

const normalizeCourseListResponse = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawCourses = Array.isArray(payload?.['courses']) ? payload['courses'] : []
  const items = rawCourses.map((course, index) => normalizeCourseSummary(course, index))
  const totalCount = Number(payload?.['total'] ?? items.length)
  return {
    items,
    total: Number.isFinite(totalCount) ? totalCount : items.length
  }
}

const buildCoursePayload = () => ({
  course_name: normalizeText(form.name),
  course_description: normalizeText(form.description),
  teacher_id: form.teacherId,
  is_public: form.isPublic
})

const getTeacherId = (teacher) => teacher?.id ?? null
const getTeacherLabel = (teacher) => teacher?.displayName ?? '未命名教师'

const loadTeachers = async () => {
  try {
    const teacherResponse = await getUsers({ role: 'teacher', page: 1, size: 100 })
    teachers.value = normalizeTeacherList(teacherResponse)
  } catch (error) {
    console.error('获取教师列表失败:', error)
    teachers.value = []
  }
}

const loadCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (normalizeText(filter.keyword)) params.keyword = normalizeText(filter.keyword)
    if (filter.teacherId) params.teacher_id = filter.teacherId

    const courseResponse = await getAllCourses(params)
    const courseList = normalizeCourseListResponse(courseResponse)
    courses.value = courseList.items
    total.value = courseList.total
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.id = null
  form.name = ''
  form.description = ''
  form.teacherId = null
  form.isPublic = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.description = row.description
  const matchedTeacher = teachers.value.find((teacher) => {
    const hasSameId = teacher.id !== null && row.teacherId !== null
      && String(teacher.id) === String(row.teacherId)
    return hasSameId || teacher.username === row.teacherName || teacher.realName === row.teacherName
  })
  form.teacherId = matchedTeacher ? getTeacherId(matchedTeacher) : (row.teacherId ?? null)
  form.isPublic = row.isPublic
  dialogVisible.value = true
}

const handleAssignTeacher = (row) => {
  assignCourseId.value = row.id
  assignTeacherId.value = null
  assignDialogVisible.value = true
}

const submitAssign = async () => {
  if (!assignTeacherId.value) return ElMessage.warning('请选择教师')
  try {
    await assignCourseTeacher(assignCourseId.value, assignTeacherId.value)
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    await loadCourses()
  } catch (e) {
    ElMessage.error('分配失败')
  }
}

const submitForm = async () => {
  const payload = buildCoursePayload()
  if (!payload.course_name) return ElMessage.warning('请输入课程名称')
  try {
    if (isEdit.value && form.id) {
      await updateCourse(form.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createCourse(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadCourses()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

const deleteCourse = async (course) => {
  try {
    await ElMessageBox.confirm('确定删除该课程吗？', '提示', { type: 'warning' })
    await apiDeleteCourse(course.id)
    ElMessage.success('删除成功')
    await loadCourses()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadTeachers()
  loadCourses()
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
</style>

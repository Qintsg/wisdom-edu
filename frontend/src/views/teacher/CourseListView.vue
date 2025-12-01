<template>
  <div class="course-list-view">
    <PageHero eyebrow="Teacher Workspace" title="课程管理" description="统一管理课程基本信息，并从课程详情进入题库、资源、图谱与作业工作台。">
      <template #actions>
        <el-button type="primary" @click="createCourse">
          <el-icon>
            <Plus />
          </el-icon> 创建课程
        </el-button>
        <el-button plain @click="openImportCoursePage">
          <el-icon>
            <Plus />
          </el-icon> 导入建课
        </el-button>
      </template>
    </PageHero>

    <el-card shadow="hover">
      <el-table :data="courses" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="description" label="课程描述" show-overflow-tooltip />
        <el-table-column prop="isPublic" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isPublic ? 'success' : 'info'">{{ row.isPublic ? '公开' : '未公开' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewCourse(row)">查看详情</el-button>
            <el-button type="warning" link @click="editCourse(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteCourse(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无课程，点击右上角创建" />
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 教师端 - 课程列表视图
 * 管理课程、创建课程等功能
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getMyCourses, deleteCourse as apiDeleteCourse } from '@/api/teacher/course'
import PageHero from '@/components/common/PageHero.vue'

const router = useRouter()

// 加载状态
const loading = ref(true)

// 课程列表
const courses = ref([])

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const parsedDate = new Date(value)
  if (Number.isNaN(parsedDate.getTime())) return '-'
  return parsedDate.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const normalizeCourseSummary = (value, index) => {
  const course = value && typeof value === 'object' ? value : {}
  return {
    id: course?.['course_id'] ?? course?.['id'] ?? index,
    name: normalizeText(course?.['course_name'] ?? course?.['name']) || '未命名课程',
    description: normalizeText(course?.['course_description'] ?? course?.['description']),
    isPublic: Boolean(course?.['is_public']),
    createdAt: formatDateTime(course?.['created_at'])
  }
}

/**
 * 加载课程列表
 */
const loadCourses = async () => {
  loading.value = true
  try {
    const res = await getMyCourses()
    const courseList = Array.isArray(res?.['courses']) ? res['courses'] : Array.isArray(res) ? res : []
    courses.value = courseList.map((course, index) => normalizeCourseSummary(course, index))
  } catch (error) {
    console.error('获取课程列表失败:', error)
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 创建课程
 */
const createCourse = () => router.push('/teacher/courses/create')
const openImportCoursePage = () => {
  const targetRoute = router.resolve({ path: '/teacher/courses/create', query: { entry: 'demo-import' } })
  window.open(targetRoute.href, '_blank', 'noopener')
}
const viewCourse = (course) => router.push(`/teacher/courses/${course.id}`)
const editCourse = (course) => router.push(`/teacher/courses/${course.id}/edit`)

/**
 * 删除课程
 */
const deleteCourse = async (course) => {
  try {
    await ElMessageBox.confirm('确定删除该课程吗？此操作不可恢复。', '删除确认', { type: 'warning' })

    await apiDeleteCourse(course.id)
    courses.value = courses.value.filter(c => c.id !== course.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除课程失败:', error)
      ElMessage.error('删除课程失败')
    }
  }
}

onMounted(() => {
  loadCourses()
})
</script>

<style scoped>
.course-list-view {
  display: grid;
  gap: 20px;
}
</style>

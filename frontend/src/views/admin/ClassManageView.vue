<template>
  <div class="class-manage-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>班级管理</h2>
        <el-button type="primary" @click="handleAddClass">
          <el-icon>
            <Plus />
          </el-icon>创建班级
        </el-button>
      </div>
    </el-card>

    <el-card v-loading="loading" shadow="hover">
      <div class="filter-bar">
        <el-input v-model="filter.keyword" placeholder="搜索班级" clearable style="width: 200px;"
          @keyup.enter="loadClasses" />
        <el-select v-model="filter.course" placeholder="关联课程" clearable style="width: 180px;" @change="loadClasses">
          <el-option v-for="c in courseOptions" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="loadClasses">搜索</el-button>
      </div>

      <el-table :data="classes" style="width: 100%;">
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="course" label="关联课程" width="180">
          <template #default="{ row }">{{ row.course || '未关联课程' }}</template>
        </el-table-column>
        <el-table-column prop="teacherName" label="授课教师" width="120">
          <template #default="{ row }">{{ row.teacherName || '-' }}</template>
        </el-table-column>
        <el-table-column prop="studentCount" label="学生数" width="100">
          <template #default="{ row }">{{ row.studentCount ?? 0 }}</template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">{{ row.createdAt }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewClassDetail(row)">查看</el-button>
            <el-button type="warning" link @click="handleEditClass(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteClass(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无班级数据" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="total"
        v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize" @size-change="loadClasses"
        @current-change="loadClasses" />
    </el-card>

    <!-- 创建/编辑班级 -->
    <el-dialog v-model="classDialogVisible" :title="isEditClass ? '编辑班级' : '创建班级'" width="480px">
      <el-form :model="classForm" label-width="80px">
        <el-form-item label="班级名称" required>
          <el-input v-model="classForm.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="关联课程">
          <el-select v-model="classForm.courseId" placeholder="选择课程" style="width: 100%;">
            <el-option v-for="c in courseOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="classForm.description" placeholder="班级描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="classDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitClassForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 班级详情 -->
    <el-drawer v-model="detailDrawerVisible" title="班级详情" size="40%">
      <template v-if="selectedClass">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="班级名称">{{ selectedClass.name }}</el-descriptions-item>
          <el-descriptions-item label="关联课程">{{ selectedClass.course }}</el-descriptions-item>
          <el-descriptions-item label="授课教师">{{ selectedClass.teacherName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="学生人数">{{ selectedClass.studentCount ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedClass.createdAt }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
/**
 * 管理端 - 班级管理视图
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getClassList, deleteClass as apiDeleteClass, createClass, updateClass } from '@/api/admin/class'
import { getAllCourses } from '@/api/admin/course'

const loading = ref(false)
const filter = reactive({ keyword: '', course: '' })
const pagination = reactive({ page: 1, pageSize: 10 })
const total = ref(0)
const classes = ref([])
const courseOptions = ref([])

// 创建/编辑对话框
const classDialogVisible = ref(false)
const isEditClass = ref(false)
const classForm = reactive({ id: null, name: '', courseId: null, description: '' })

// 详情抽屉
const detailDrawerVisible = ref(false)
const selectedClass = ref(null)

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const parsedDate = new Date(dateStr)
  return Number.isNaN(parsedDate.getTime()) ? '-' : parsedDate.toLocaleString('zh-CN')
}

const normalizeCourseOption = (value, index) => {
  const course = value && typeof value === 'object' ? value : {}
  return {
    id: course?.['course_id'] ?? course?.['id'] ?? index,
    name: normalizeText(course?.['course_name'] ?? course?.['name']) || '未命名课程'
  }
}

const normalizeClassSummary = (value, index) => {
  const classItem = value && typeof value === 'object' ? value : {}
  const studentCount = Number(classItem?.['student_count'])
  return {
    id: classItem?.['id'] ?? classItem?.['class_id'] ?? index,
    name: normalizeText(classItem?.['name'] ?? classItem?.['class_name']) || '未命名班级',
    course: normalizeText(classItem?.['course'] ?? classItem?.['course_name']) || '未关联课程',
    teacherName: normalizeText(classItem?.['teacher_name']) || '-',
    studentCount: Number.isFinite(studentCount) ? studentCount : 0,
    createdAt: formatDate(classItem?.['created_at']),
    courseId: classItem?.['course_id'] ?? null,
    description: normalizeText(classItem?.['description'])
  }
}

const normalizeClassListResponse = (value) => {
  const payload = value && typeof value === 'object' ? value : {}
  const rawClasses = Array.isArray(payload?.['classes']) ? payload['classes'] : []
  const items = rawClasses.map((classItem, index) => normalizeClassSummary(classItem, index))
  const totalCount = Number(payload?.['total'] ?? items.length)
  return {
    items,
    total: Number.isFinite(totalCount) ? totalCount : items.length
  }
}

const buildClassPayload = () => ({
  class_name: normalizeText(classForm.name),
  course_id: classForm.courseId,
  description: normalizeText(classForm.description)
})

/**
 * 加载课程选项
 */
const loadCourseOptions = async () => {
  try {
    const res = await getAllCourses({ page: 1, page_size: 100 })
    courseOptions.value = Array.isArray(res?.['courses'])
      ? res['courses'].map((course, index) => normalizeCourseOption(course, index))
      : []
  } catch {
    courseOptions.value = []
  }
}

/**
 * 加载班级列表
 */
const loadClasses = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filter.keyword) params.keyword = filter.keyword
    if (filter.course) params.course_id = filter.course

    const res = await getClassList(params)
    const classList = normalizeClassListResponse(res)
    classes.value = classList.items
    total.value = classList.total
  } catch (error) {
    console.error('获取班级列表失败:', error)
    ElMessage.error('获取班级列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 删除班级
 */
const deleteClass = async (cls) => {
  try {
    await ElMessageBox.confirm('确定删除该班级吗？', '删除确认', { type: 'warning' })
    await apiDeleteClass(cls.id)
    classes.value = classes.value.filter(c => c.id !== cls.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

/**
 * 创建班级
 */
const handleAddClass = () => {
  isEditClass.value = false
  classForm.id = null
  classForm.name = ''
  classForm.courseId = null
  classForm.description = ''
  classDialogVisible.value = true
}

/**
 * 编辑班级
 */
const handleEditClass = (row) => {
  isEditClass.value = true
  classForm.id = row.id
  classForm.name = row.name
  classForm.courseId = row.courseId || null
  classForm.description = row.description || ''
  classDialogVisible.value = true
}

/**
 * 查看班级详情
 */
const viewClassDetail = (row) => {
  selectedClass.value = row
  detailDrawerVisible.value = true
}

/**
 * 提交创建/编辑
 */
const submitClassForm = async () => {
  const payload = buildClassPayload()
  if (!payload.class_name) return ElMessage.warning('请输入班级名称')
  try {
    if (isEditClass.value && classForm.id) {
      await updateClass(classForm.id, payload)
      ElMessage.success('更新成功')
    } else {
      await createClass(payload)
      ElMessage.success('创建成功')
    }
    classDialogVisible.value = false
    await loadClasses()
  } catch (e) {
    ElMessage.error(isEditClass.value ? '更新失败' : '创建失败')
  }
}

onMounted(() => {
  loadCourseOptions()
  loadClasses()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
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

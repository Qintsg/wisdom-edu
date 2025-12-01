<template>
  <div class="course-edit-view">
    <el-page-header @back="goBack">
      <template #content>{{ isEdit ? '编辑课程' : '创建课程' }}</template>
    </el-page-header>

    <div class="course-edit-grid">
      <el-card class="form-card" shadow="hover">
        <template #header>
          <div class="card-title">基础信息</div>
        </template>
        <el-form :model="form" label-width="100px">
          <el-alert v-if="demoImportEntry && !isEdit" type="info" :closable="false" style="margin-bottom: 16px;"
            title="当前页适合用于答辩演示：可直接上传课程压缩包，并在创建后立即发布到班级。" />
          <el-form-item label="课程名称" required>
            <el-input v-model="form.name" placeholder="请输入课程名称" />
          </el-form-item>
          <el-form-item label="课程描述">
            <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请输入课程描述" />
          </el-form-item>
          <el-form-item v-if="!isEdit" label="发布到班级">
            <el-switch v-model="form.publishToClass" />
          </el-form-item>
          <el-form-item v-if="!isEdit && form.publishToClass" label="目标班级">
            <el-select v-model="form.publishClassId" placeholder="请选择班级" :loading="classLoading" style="width: 100%;">
              <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="资源压缩包" v-if="!isEdit">
            <el-upload drag :auto-upload="false" :limit="1" accept=".zip" :on-change="handleArchiveChange"
              :file-list="archiveFileList">
              <el-icon class="el-icon--upload">
                <Upload />
              </el-icon>
              <div class="el-upload__text">拖拽 ZIP 压缩包到此处，或 <em>点击上传</em></div>
              <template #tip>
                <div class="el-upload__tip">支持直接导入课程图谱、题库、PPT、视频、教材与作业库压缩包</div>
              </template>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="saveCourse">{{ isEdit ? '保存修改' : '创建课程' }}</el-button>
            <el-button v-if="isEdit" type="success" plain @click="goToResourceImport">前往资源导入</el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="guide-card" shadow="hover">
        <template #header>
          <div class="card-title">导入说明</div>
        </template>
        <div class="guide-content">
          <p>创建课程时可直接上传 ZIP 压缩包，系统会自动导入以下内容：</p>
          <ul>
            <li>知识图谱 Excel / JSON</li>
            <li>初始评测与作业题库</li>
            <li>PPT、视频、电子教材</li>
            <li>课程资源 JSON 与作业库</li>
          </ul>
          <p>如果暂时没有压缩包，也可以先创建课程，随后进入课程工作台继续维护题库、资源和知识图谱。</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
/**
 * 课程编辑视图
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { getCourseDetail, createCourse, updateCourse } from '@/api/teacher/course'
import { getMyClasses } from '@/api/teacher/class'
import { useCourseStore } from '@/stores/course'

const router = useRouter()
const route = useRoute()
const courseStore = useCourseStore()
const currentCourseId = computed(() => route.params['courseId'])

const loading = ref(false)
const saving = ref(false)
const classLoading = ref(false)
const isEdit = computed(() => Boolean(currentCourseId.value))
const demoImportEntry = computed(() => route.query['entry'] === 'demo-import')

const classOptions = ref([])

const form = reactive({
  name: '',
  description: '',
  publishToClass: false,
  publishClassId: null
})
const archiveFile = ref(null)
const archiveFileList = ref([])

const normalizeText = (value) => {
  if (value === null || value === undefined) return ''
  return String(value).trim()
}

const normalizeCourseDetail = (value) => {
  const course = value && typeof value === 'object' ? value : {}
  return {
    name: normalizeText(course?.['course_name'] ?? course?.['name']),
    description: normalizeText(course?.['course_description'] ?? course?.['description'])
  }
}

const normalizeClassOption = (value, index) => {
  const classItem = value && typeof value === 'object' ? value : {}
  return {
    id: classItem?.['class_id'] ?? classItem?.['id'] ?? index,
    name: normalizeText(classItem?.['name'] ?? classItem?.['class_name']) || '未命名班级',
    studentCount: Number(classItem?.['student_count'] ?? 0) || 0
  }
}

const normalizeCreatedCourse = (value) => {
  const course = value && typeof value === 'object' ? value : {}
  return {
    courseId: course?.['course_id'] ?? null,
    courseName: normalizeText(course?.['course_name'] ?? course?.['name'])
  }
}

/**
 * 加载课程详情（编辑模式）
 */
const loadCourseDetail = async () => {
  if (!isEdit.value) return

  loading.value = true
  try {
    const detail = normalizeCourseDetail(await getCourseDetail(currentCourseId.value))
    form.name = detail.name
    form.description = detail.description
  } catch (error) {
    console.error('加载课程详情失败:', error)
    ElMessage.error('加载课程详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => router.push('/teacher/courses')
const goToResourceImport = () => router.push(`/teacher/courses/${currentCourseId.value}/workspace/resources`)

const handleArchiveChange = (file) => {
  archiveFile.value = file.raw
  archiveFileList.value = file.raw ? [file] : []
}

const loadClassOptions = async () => {
  if (isEdit.value) return

  classLoading.value = true
  try {
    const response = await getMyClasses()
    const classes = Array.isArray(response?.['classes']) ? response['classes'] : []
    classOptions.value = classes.map((item, index) => normalizeClassOption(item, index))
    if (classOptions.value.length === 1) {
      form.publishToClass = true
      form.publishClassId = classOptions.value[0].id
    }
  } catch (error) {
    console.error('加载班级列表失败:', error)
  } finally {
    classLoading.value = false
  }
}

/**
 * 保存课程
 */
const saveCourse = async () => {
  const courseName = normalizeText(form.name)
  if (!courseName) {
    ElMessage.warning('请输入课程名称')
    return
  }

  if (!isEdit.value && form.publishToClass && !form.publishClassId) {
    ElMessage.warning('请选择要发布到的班级')
    return
  }

  saving.value = true
  try {
    const data = {
      course_name: courseName,
      course_description: normalizeText(form.description),
      archive: archiveFile.value,
      publish_class_id: !isEdit.value && form.publishToClass ? form.publishClassId : null
    }

    if (isEdit.value) {
      await updateCourse(currentCourseId.value, data)
      ElMessage.success('课程更新成功')
      await router.push(`/teacher/courses/${currentCourseId.value}`)
    } else {
      const createdCourse = normalizeCreatedCourse(await createCourse(data))
      if (createdCourse.courseId) {
        courseStore.addCourse({
          course_id: createdCourse.courseId,
          course_name: createdCourse.courseName || courseName,
          name: createdCourse.courseName || courseName
        })
        courseStore.setCurrentCourse({
          course_id: createdCourse.courseId,
          course_name: createdCourse.courseName || courseName,
          name: createdCourse.courseName || courseName
        })
      }
      ElMessage.success('课程创建成功')
      if (createdCourse.courseId) {
        await router.push(`/teacher/courses/${createdCourse.courseId}`)
        return
      }
    }
    await router.push('/teacher/courses')
  } catch (error) {
    console.error('保存课程失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadCourseDetail()
  loadClassOptions()
})
</script>

<style scoped>
.course-edit-view {
  padding: 0;
}

.course-edit-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.7fr);
  gap: 20px;
  margin-top: 20px;
}

.card-title {
  font-weight: 600;
}

.guide-content {
  color: #606266;
  line-height: 1.8;
}

.guide-content ul {
  margin: 12px 0;
  padding-left: 18px;
}

@media (max-width: 960px) {
  .course-edit-grid {
    grid-template-columns: 1fr;
  }
}
</style>

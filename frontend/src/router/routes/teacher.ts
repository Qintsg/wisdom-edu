/**
 * 教师端路由配置
 * 所有路由路径以 /teacher 为前缀
 */

// 懒加载教师端页面组件
const DashboardView = () => import('@/views/teacher/DashboardView.vue')
const CourseListView = () => import('@/views/teacher/CourseListView.vue')
const CourseDetailView = () => import('@/views/teacher/CourseDetailView.vue')
const CourseEditView = () => import('@/views/teacher/CourseEditView.vue')
const ClassListView = () => import('@/views/teacher/ClassListView.vue')
const ClassDetailView = () => import('@/views/teacher/ClassDetailView.vue')
const KnowledgeManageView = () => import('@/views/teacher/KnowledgeManageView.vue')
const QuestionListView = () => import('@/views/teacher/QuestionListView.vue')
const ExamManageView = () => import('@/views/teacher/ExamManageView.vue')
const ResourceManageView = () => import('@/views/teacher/ResourceManage.vue')
const StudentProfileView = () => import('@/views/teacher/StudentProfileView.vue')
const SettingsView = () => import('@/views/teacher/SettingsView.vue')

/**
 * 教师端路由配置
 * meta.requiresAuth: 需要登录认证
 * meta.role: 需要的用户角色
 * meta.title: 页面标题
 */
export default {
  path: '/teacher',
  name: 'Teacher',
  redirect: '/teacher/dashboard',
  meta: {
    requiresAuth: true,
    role: 'teacher',
    layout: 'default'
  },
  children: [
    {
      path: 'dashboard',
      name: 'TeacherDashboard',
      component: DashboardView,
      meta: {
        title: '教学中心',
        icon: 'House'
      }
    },
    {
      path: 'courses',
      name: 'CourseList',
      component: CourseListView,
      meta: {
        title: '课程管理',
        icon: 'Reading'
      }
    },
    {
      path: 'courses/create',
      name: 'CourseCreate',
      component: CourseEditView,
      meta: {
        title: '创建课程',
        icon: 'Plus',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId',
      name: 'CourseDetail',
      component: CourseDetailView,
      props: true,
      meta: {
        title: '课程详情',
        icon: 'Reading',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId/workspace/questions',
      name: 'TeacherCourseWorkspaceQuestions',
      component: QuestionListView,
      props: true,
      meta: {
        title: '课程题库',
        icon: 'Document',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId/workspace/resources',
      name: 'TeacherCourseWorkspaceResources',
      component: ResourceManageView,
      props: true,
      meta: {
        title: '课程资源',
        icon: 'FolderOpened',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId/workspace/knowledge',
      name: 'TeacherCourseWorkspaceKnowledge',
      component: KnowledgeManageView,
      props: true,
      meta: {
        title: '课程图谱',
        icon: 'Share',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId/workspace/exams',
      name: 'TeacherCourseWorkspaceExams',
      component: ExamManageView,
      props: true,
      meta: {
        title: '课程作业',
        icon: 'Notebook',
        hideInMenu: true
      }
    },
    {
      path: 'courses/:courseId/edit',
      name: 'CourseEdit',
      component: CourseEditView,
      props: true,
      meta: {
        title: '编辑课程',
        icon: 'Edit',
        hideInMenu: true
      }
    },
    {
      path: 'classes',
      name: 'ClassList',
      component: ClassListView,
      meta: {
        title: '班级管理',
        icon: 'School',
        hideInMenu: true
      }
    },
    {
      path: 'classes/:classId',
      name: 'ClassDetail',
      component: ClassDetailView,
      props: true,
      meta: {
        title: '班级详情',
        icon: 'School',
        hideInMenu: true
      }
    },
    {
      path: 'resources',
      name: 'ResourceManage',
      component: ResourceManageView,
      meta: {
        title: '资源库管理',
        icon: 'FolderOpened'
      }
    },
    {
      path: 'knowledge',
      name: 'KnowledgeManage',
      component: KnowledgeManageView,
      meta: {
        title: '知识图谱管理',
        icon: 'Share'
      }
    },
    {
      path: 'questions',
      name: 'QuestionList',
      component: QuestionListView,
      meta: {
        title: '题库管理',
        icon: 'Document'
      }
    },
    {
      path: 'exams',
      name: 'ExamManage',
      component: ExamManageView,
      meta: {
        title: '作业管理',
        icon: 'Notebook'
      }
    },
    {
      path: 'students/:studentId/profile',
      name: 'TeacherStudentProfile',
      component: StudentProfileView,
      props: true,
      meta: {
        title: '学生画像',
        icon: 'User',
        hideInMenu: true
      }
    },
    {
      path: 'settings',
      name: 'TeacherSettings',
      component: SettingsView,
      meta: {
        title: '个人设置',
        icon: 'Setting',
        hideInMenu: true
      }
    }
  ]
}

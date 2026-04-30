/**
 * 学生端路由配置
 * 所有路由路径以 /student 为前缀
 */

// 懒加载学生端页面组件
const DashboardView = () => import('@/views/student/DashboardView.vue')
const AssessmentView = () => import('@/views/student/AssessmentView.vue')
const AssessmentKnowledgeView = () => import('@/views/student/AssessmentKnowledgeView.vue')
const AssessmentAbilityView = () => import('@/views/student/AssessmentAbilityView.vue')
const AssessmentHabitView = () => import('@/views/student/AssessmentHabitView.vue')
const AssessmentReportView = () => import('@/views/student/AssessmentReportView.vue')
const ProfileView = () => import('@/views/student/ProfileView.vue')
const KnowledgeMapView = () => import('@/views/student/KnowledgeMapView.vue')
const LearningPathView = () => import('@/views/student/LearningPathView.vue')
const TaskLearningView = () => import('@/views/student/TaskLearningView.vue')
const AIAssistantView = () => import('@/views/student/AIAssistantView.vue')
const ExamView = () => import('@/views/student/ExamView.vue')
const ExamTakingView = () => import('@/views/student/ExamTakingView.vue')
const ClassesView = () => import('@/views/student/ClassesView.vue')
const ClassDetailView = () => import('@/views/student/ClassDetailView.vue')
const CourseSelectView = () => import('@/views/student/CourseSelectView.vue')
const SettingsView = () => import('@/views/student/SettingsView.vue')
const FeedbackReportView = () => import('@/views/student/FeedbackReportView.vue')
const ResourceListView = () => import('@/views/student/ResourceListView.vue')

/**
 * 学生端路由配置
 * meta.requiresAuth: 需要登录认证
 * meta.role: 需要的用户角色
 * meta.title: 页面标题
 */
export default {
  path: '/student',
  name: 'Student',
  redirect: '/student/dashboard',
  meta: {
    requiresAuth: true,
    role: 'student',
    layout: 'default'
  },
  children: [
    {
      path: 'dashboard',
      name: 'StudentDashboard',
      component: DashboardView,
      meta: {
        title: '学习中心',
        icon: 'House'
      }
    },
    {
      path: 'course-select',
      name: 'CourseSelect',
      component: CourseSelectView,
      meta: {
        title: '课程选择',
        icon: 'Reading',
        skipCourseCheck: true  // 跳过课程选择检查
      }
    },
    {
      path: 'assessment',
      name: 'Assessment',
      component: AssessmentView,
      meta: {
        title: '初始测评',
        icon: 'Notebook'
      }
    },
    {
      path: 'assessment/knowledge',
      name: 'AssessmentKnowledge',
      component: AssessmentKnowledgeView,
      meta: {
        title: '知识测评',
        icon: 'Notebook'
      }
    },
    {
      path: 'assessment/ability',
      name: 'AssessmentAbility',
      component: AssessmentAbilityView,
      meta: {
        title: '能力评测',
        icon: 'Notebook'
      }
    },
    {
      path: 'assessment/habit',
      name: 'AssessmentHabit',
      component: AssessmentHabitView,
      meta: {
        title: '习惯问卷',
        icon: 'Notebook'
      }
    },
    {
      path: 'assessment/report',
      name: 'AssessmentReport',
      component: AssessmentReportView,
      meta: {
        title: '测评报告',
        icon: 'DataAnalysis',
        hideInMenu: true
      }
    },
    {
      path: 'profile',
      name: 'StudentProfile',
      component: ProfileView,
      meta: {
        title: '学习画像',
        icon: 'User'
      }
    },
    {
      path: 'resources',
      name: 'StudentResources',
      component: ResourceListView,
      meta: {
        title: '课程资源',
        icon: 'Files'
      }
    },
    {
      path: 'knowledge-map',
      name: 'KnowledgeMap',
      component: KnowledgeMapView,
      meta: {
        title: '知识图谱',
        icon: 'Share'
      }
    },
    {
      path: 'learning-path',
      name: 'LearningPath',
      component: LearningPathView,
      meta: {
        title: '学习路径',
        icon: 'Guide'
      }
    },
    {
      path: 'task/:nodeId',
      name: 'TaskLearning',
      component: TaskLearningView,
      props: true,
      meta: {
        title: '任务学习',
        icon: 'Reading'
      }
    },
    {
      path: 'ai-assistant',
      name: 'AIAssistant',
      component: AIAssistantView,
      meta: {
        title: 'AI助手',
        icon: 'ChatDotRound'
      }
    },
    {
      path: 'exams',
      name: 'ExamList',
      component: ExamView,
      meta: {
        title: '在线作业',
        icon: 'Document'
      }
    },
    {
      path: 'exam/:examId',
      name: 'ExamTaking',
      component: ExamTakingView,
      props: true,
      meta: {
        title: '作业中',
        icon: 'Document',
        hideInMenu: true  // 不在菜单中显示
      }
    },
    {
      path: 'feedback/:reportId',
      name: 'FeedbackReport',
      component: FeedbackReportView,
      props: true,
      meta: {
        title: '反馈报告',
        icon: 'Document',
        hideInMenu: true
      }
    },
    {
      path: 'classes',
      name: 'StudentClasses',
      component: ClassesView,
      meta: {
        title: '我的班级',
        icon: 'School',
        skipCourseCheck: true
      }
    },
    {
      path: 'classes/:classId',
      name: 'StudentClassDetail',
      component: ClassDetailView,
      props: true,
      meta: {
        title: '班级详情',
        icon: 'School',
        skipCourseCheck: true,
        hideInMenu: true
      }
    },
    {
      path: 'settings',
      name: 'StudentSettings',
      component: SettingsView,
      meta: {
        title: '个人设置',
        icon: 'Setting',
        skipCourseCheck: true
      }
    }
  ]
}

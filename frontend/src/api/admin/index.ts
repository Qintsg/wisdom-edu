/**
 * 管理端API统一导出
 */
export * from './user'
export * from './activation'
export * from './log'
export * from './profile'
export {
  getOverviewStats,
  getSystemStats,
  getUserStats,
  getCourseStats as getAdminStatisticsCourseStats,
  getLearningStats,
  getExamStats,
  getActiveUserRanking,
  getSystemReport,
  exportStatistics
} from './statistics'
export {
  getAllCourses,
  getCourseDetail,
  createCourse,
  updateCourse,
  deleteCourse,
  assignCourseTeacher,
  getCourseStats
} from './course'
export * from './class'

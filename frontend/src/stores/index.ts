/**
 * Pinia状态管理统一导出
 * 创建Pinia实例并导出所有Store
 */
import { createPinia } from 'pinia'

// 创建Pinia实例
export const pinia = createPinia()

// 导出所有Store
export { useUserStore } from './user'
export { useCourseStore } from './course'
export { useAssessmentStore } from './assessment'

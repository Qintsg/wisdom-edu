/**
 * 教师端API统一导出
 * 汇聚所有教师相关的API函数
 * 
 * 教师权限包括：
 * - 班级管理（创建班级、邀请学生、查看班级成员等）
 * - 知识点管理（创建知识点、建立知识图谱等）
 * - 资源管理（上传学习资源、组织课程内容等）
 * - 题目管理（创建题目、组织答卷等）
 * - 作业管理（创建作业、设置作答参数、查看成绩等）
 * - 班级分析（查看学生学习进度、学习画像分析等）
 */

export * from './course'
export * from './class'
export * from './knowledge'
export * from './question'
export * from './exam'

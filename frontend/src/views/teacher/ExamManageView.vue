<template>
  <div class="exam-manage-view">
    <PageHero eyebrow="Assessment" title="作业管理" description="从当前课程题库快速组卷、发布到班级，并跟踪作业状态、题目结构与结果分析。">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon>
            <Plus />
          </el-icon> 创建作业
        </el-button>
      </template>
    </PageHero>

    <el-card shadow="hover">
      <el-table :data="exams" v-loading="loading" style="width: 100%;">
        <el-table-column prop="title" label="作业名称" />
        <el-table-column prop="examTypeText" label="类型" width="120" />
        <el-table-column prop="totalScore" label="总分" width="100" />
        <el-table-column prop="durationMinutes" label="时长(分钟)" width="100" />
        <el-table-column prop="statusText" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.statusTagType">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewExam(row)">查看</el-button>
            <el-button type="warning" link v-if="row.isDraft" @click="editExam(row)">编辑</el-button>
            <el-button type="success" link v-if="row.isDraft" @click="publishExam(row)">发布</el-button>
            <el-button type="warning" link v-if="row.isPublished" @click="unpublishExam(row)">取消发布</el-button>
            <el-button type="danger" link @click="deleteExam(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无作业，点击右上角创建" />
        </template>
      </el-table>

      <el-pagination class="pagination" layout="total, sizes, prev, pager, next" :total="examTotal"
        :page-sizes="[10, 20, 50]" v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        @size-change="loadExams" @current-change="loadExams" />
    </el-card>

    <!-- 创建作业对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editingExam ? '编辑作业' : '创建作业'" width="500px">
      <el-form :model="createForm" :rules="examRules" ref="examFormRef" label-width="100px">
        <el-form-item label="作业名称" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入作业名称" />
        </el-form-item>
        <el-form-item label="作业类型" prop="exam_type">
          <el-select v-model="createForm.exam_type" placeholder="请选择类型" style="width: 100%;">
            <el-option label="章节测试" value="chapter" />
            <el-option label="期中作业" value="midterm" />
            <el-option label="期末作业" value="final" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联班级">
          <el-select v-model="createForm.target_class" placeholder="请选择班级" style="width: 100%;" clearable>
            <el-option v-for="cls in classes" :key="cls.id" :label="cls.name" :value="cls.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="作答时长">
          <el-input-number v-model="createForm.duration" :min="10" :max="300" /> 分钟
        </el-form-item>
        <el-form-item label="总分">
          <el-input-number v-model="createForm.total_score" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="及格分">
          <el-input-number v-model="createForm.pass_score" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="选择题目" prop="questions">
          <el-input v-model="questionSearchKeyword" placeholder="按题干关键词筛选题目" clearable style="margin-bottom: 8px;" />
          <el-select v-model="createForm.questions" multiple filterable collapse-tags collapse-tags-tooltip
            placeholder="请选择题目" style="width: 100%;">
            <el-option v-for="questionItem in filteredQuestionList" :key="questionItem.id" :label="questionItem.content"
              :value="questionItem.id">
              <div class="question-option-row">
                <span>{{ questionItem.content }}</span>
                <el-tag size="small" :type="questionTagType(questionItem.type)">{{ questionTypeName(questionItem.type)
                }}</el-tag>
              </div>
            </el-option>
          </el-select>
          <div v-if="createForm.questions.length" class="question-selection-summary">
            <span>已选择 {{ createForm.questions.length }} 道题目</span>
            <el-button type="primary" link @click="createForm.questions = []">清空已选</el-button>
          </div>
          <div v-if="selectedQuestionPreview.length" class="question-preview-list">
            <div v-for="questionItem in selectedQuestionPreview" :key="questionItem.id" class="question-preview-item">
              <span>{{ questionItem.content }}</span>
              <el-tag size="small" :type="questionTagType(questionItem.type)">{{ questionTypeName(questionItem.type)
              }}</el-tag>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="作业说明">
          <el-input v-model="createForm.description" type="textarea" placeholder="请输入作业说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="submitExam">{{ editingExam ? '保存' : '创建'
        }}</el-button>
      </template>
    </el-dialog>

    <!-- 作业详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="作业详情" width="720px">
      <div v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="作业名称">{{ examDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="作业类型">
            <el-tag size="small">{{ examDetail.examTypeText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总分">{{ examDetail.totalScore }}</el-descriptions-item>
          <el-descriptions-item label="及格分">{{ examDetail.passScore }}</el-descriptions-item>
          <el-descriptions-item label="作答时长">{{ examDetail.durationMinutes }} 分钟</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="examDetail.statusTagType">{{ examDetail.statusText }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">{{ examDetail.questionCount }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ examDetail.createdAtText }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="examDetail.description" style="margin-top: 16px;">
          <strong>作业说明：</strong>
          <p style="color: #606266;">{{ examDetail.description }}</p>
        </div>

        <!-- 题目列表预览 -->
        <div v-if="(examDetail.questions || []).length" style="margin-top: 20px;">
          <h4 style="margin-bottom: 12px; font-size: 15px;">题目列表</h4>
          <el-table :data="examDetail.questions" border size="small" max-height="360">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column label="题目内容" min-width="240">
              <template #default="{ row }">
                <span>{{ row.contentPreview }}</span>
              </template>
            </el-table-column>
            <el-table-column label="题型" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="row.typeTag">{{ row.typeText }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="70" align="center" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import PageHero from '@/components/common/PageHero.vue'
import { useTeacherExamManage } from './useTeacherExamManage'

const {
  classes,
  createForm,
  createLoading,
  deleteExam,
  detailLoading,
  editExam,
  editingExam,
  examDetail,
  examFormRef,
  examRules,
  examTotal,
  exams,
  filteredQuestionList,
  loadExams,
  loading,
  pagination,
  publishExam,
  questionSearchKeyword,
  questionTagType,
  questionTypeName,
  selectedQuestionPreview,
  showCreateDialog,
  showDetailDialog,
  submitExam,
  unpublishExam,
  viewExam
} = useTeacherExamManage()
</script>

<style scoped src="./ExamManageView.css"></style>

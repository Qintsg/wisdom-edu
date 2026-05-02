<template>
  <div class="resource-manage">
    <PageHero eyebrow="Resource Library" title="资源库管理" description="维护课程视频、文档与外部链接资源，并将资源精确挂接到知识点和课程上下文中。">
      <template #actions>
        <el-button type="primary" @click="showCreateDialog">
          <el-icon>
            <Plus />
          </el-icon> 新增资源
        </el-button>
        <el-button @click="showImportDialog">
          <el-icon>
            <Upload />
          </el-icon> 批量导入
        </el-button>
      </template>
    </PageHero>

    <!-- 搜索筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="resourceSearchForm">
        <el-form-item label="资源名称">
          <el-input v-model="resourceSearchForm.titleKeyword" placeholder="搜索资源名称" clearable class="filter-input" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="resourceSearchForm.resourceType" placeholder="全部" clearable class="filter-select">
            <el-option v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.optionValue"
              :label="resourceTypeOption.optionLabel" :value="resourceTypeOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联知识点">
          <el-select v-model="resourceSearchForm.pointId" placeholder="全部" clearable class="filter-select">
            <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
              :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 资源列表 -->
    <el-card class="list-card">
      <el-table :data="resourceRecords" v-loading="loading" stripe>
        <el-table-column prop="titleText" label="资源名称" min-width="200" />
        <el-table-column prop="typeLabel" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.typeTagType">{{ row.typeLabel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pointNameText" label="关联知识点" width="150" />
        <el-table-column prop="createdAtText" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.createdAtText) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editResource(row)">编辑</el-button>
            <el-button type="primary" link @click="previewResource(row)">预览</el-button>
            <el-button type="danger" link @click="deleteResource(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.pageSize"
        :total="totalResourceCount" layout="total, sizes, prev, pager, next" @size-change="handleResourcePageSizeChange"
        @current-change="handleResourcePageChange" />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="isResourceDialogVisible" :title="isEditingResource ? '编辑资源' : '新增资源'" width="500px">
      <el-form ref="formRef" :model="resourceForm" :rules="formRules" label-width="100px">
        <el-form-item label="资源名称" prop="titleText">
          <el-input v-model="resourceForm.titleText" placeholder="请输入资源名称" />
        </el-form-item>
        <el-form-item label="资源类型" prop="resourceType">
          <el-select v-model="resourceForm.resourceType" placeholder="请选择类型" style="width: 100%">
            <el-option v-for="resourceTypeOption in resourceTypeOptions" :key="resourceTypeOption.optionValue"
              :label="resourceTypeOption.optionLabel" :value="resourceTypeOption.optionValue" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联知识点" prop="pointId">
          <el-select v-model="resourceForm.pointId" placeholder="请选择知识点" style="width: 100%">
            <el-option v-for="knowledgePoint in knowledgePointOptions" :key="knowledgePoint.pointId"
              :label="knowledgePoint.pointName" :value="knowledgePoint.pointId" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="resourceForm.resourceType === 'link'" label="链接地址" prop="linkUrl">
          <el-input v-model="resourceForm.linkUrl" placeholder="请输入链接地址" />
        </el-form-item>
        <el-form-item v-else label="上传文件" prop="fileObject">
          <el-upload :auto-upload="false" :on-change="handleFileChange" :before-upload="beforeFileUpload" :limit="1"
            :file-list="fileList" :accept="getAcceptTypes(resourceForm.resourceType)">
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                {{ getUploadTipText(resourceForm.resourceType) }}
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="resourceForm.descriptionText" type="textarea" :rows="3" placeholder="请输入资源描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isResourceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="批量导入资源" width="400px">
      <el-upload drag :auto-upload="false" :on-change="handleImportFile" :limit="1" accept=".xlsx,.xls,.csv">
        <el-icon class="el-icon--upload">
          <Upload />
        </el-icon>
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 xlsx, xls, csv 格式</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { Plus, Upload } from '@element-plus/icons-vue'
import PageHero from '@/components/common/PageHero.vue'
import { useTeacherResourceManage } from './useTeacherResourceManage'

const {
  beforeFileUpload,
  deleteResource,
  editResource,
  fileList,
  formRef,
  formRules,
  formatTime,
  getAcceptTypes,
  getUploadTipText,
  handleFileChange,
  handleImportFile,
  handleResourcePageChange,
  handleResourcePageSizeChange,
  handleSearch,
  importDialogVisible,
  importing,
  isEditingResource,
  isResourceDialogVisible,
  knowledgePointOptions,
  loading,
  pagination,
  previewResource,
  resetSearch,
  resourceForm,
  resourceRecords,
  resourceSearchForm,
  resourceTypeOptions,
  showCreateDialog,
  showImportDialog,
  submitForm,
  submitImport,
  submitting,
  totalResourceCount
} = useTeacherResourceManage()
</script>

<style scoped src="./ResourceManage.css"></style>

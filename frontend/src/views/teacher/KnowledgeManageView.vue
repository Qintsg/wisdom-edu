<template>
  <div class="knowledge-manage-view">
    <el-card class="page-header" shadow="never">
      <div class="header-content">
        <h2>知识图谱管理</h2>
        <div class="header-actions">
          <el-button-group>
            <el-button :type="showGraph ? 'primary' : ''" @click="showGraph = true">
              <el-icon>
                <Connection />
              </el-icon> 图谱模式
            </el-button>
            <el-button :type="!showGraph ? 'primary' : ''" @click="showGraph = false">
              <el-icon>
                <List />
              </el-icon> 列表模式
            </el-button>
          </el-button-group>
          <el-button type="primary" @click="addPoint">
            <el-icon>
              <Plus />
            </el-icon> 添加知识点
          </el-button>
          <el-button :loading="indexBuilding" @click="buildRagIndex">构建 GraphRAG 索引</el-button>
          <el-button @click="loadAll">刷新</el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">知识点总数</div>
            <div class="value">{{ stats.totalPoints }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">关系总数</div>
            <div class="value">{{ stats.totalRelations }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">章节数</div>
            <div class="value">{{ stats.totalChapters }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :md="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="label">孤立点</div>
            <div class="value">{{ stats.isolatedPoints }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图谱展示区域 -->
    <el-card v-if="showGraph" class="graph-card" shadow="hover" style="margin-bottom: 20px;">
      <template #header>
        <div class="card-title">知识图谱可视化编辑</div>
      </template>
      <div class="graph-container" style="min-height: 600px; height: calc(100vh - 300px);">
        <KnowledgeGraphECharts v-if="knowledgePoints.length" :data="graphData" mode="edit" :height="'100%'"
          @save="handleGraphSave" @node-click="handleNodeClick" />
        <el-empty v-else description="暂无知识图谱数据" />
      </div>
    </el-card>

    <el-row :gutter="16" v-show="!showGraph">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" body-style="padding: 12px 16px">
          <template #header>
            <div class="card-title">按章节展示（完整）</div>
          </template>
          <el-tree v-loading="loading" :data="knowledgeTree" :props="{ label: 'labelText', children: 'children' }"
            node-key="treeId" default-expand-all>
            <template #default="{ node, data }">
              <div class="tree-node">
                <span>{{ node.label }}</span>
                <span v-if="data.treeNodeType === 'point'" class="node-actions">
                  <el-button type="primary" link size="small" @click.stop="editPoint(data)">编辑</el-button>
                  <el-button type="danger" link size="small" @click.stop="deletePoint(data)">删除</el-button>
                </span>
              </div>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" body-style="padding: 12px 16px">
          <template #header>
            <div class="card-title">关系明细（完整）</div>
          </template>
          <el-input v-model="relationKeyword" clearable placeholder="筛选关系（知识点名）" style="margin-bottom: 12px" />
          <el-table v-loading="loading" :data="filteredRelations" size="small" stripe max-height="520">
            <el-table-column prop="fromPointName" label="前置知识点" min-width="150" show-overflow-tooltip />
            <el-table-column prop="relationTypeText" label="关系" width="110" />
            <el-table-column prop="toPointName" label="后续知识点" min-width="150" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加/编辑知识点对话框 -->
    <el-dialog v-model="pointDialogVisible" :title="editingPoint ? '编辑知识点' : '添加知识点'" width="500px">
      <el-form :model="pointForm" label-width="80px" ref="pointFormRef" :rules="pointRules">
        <el-form-item label="知识点名" prop="pointName">
          <el-input v-model="pointForm.pointName" placeholder="请输入知识点名称" />
        </el-form-item>
        <el-form-item label="所属章节" prop="chapterText">
          <el-select v-model="pointForm.chapterText" filterable allow-create clearable placeholder="选择或输入章节"
            style="width: 100%;">
            <el-option v-for="c in existingChapters" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="pointForm.descriptionText" type="textarea" :rows="3" placeholder="知识点描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pointDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPointForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { Plus, Connection, List } from '@element-plus/icons-vue'
import KnowledgeGraphECharts from '@/components/knowledge/KnowledgeGraphECharts.vue'
import { useTeacherKnowledgeManage } from './useTeacherKnowledgeManage'

const {
  addPoint,
  buildRagIndex,
  deletePoint,
  editPoint,
  editingPoint,
  existingChapters,
  filteredRelations,
  graphData,
  handleGraphSave,
  handleNodeClick,
  indexBuilding,
  knowledgePoints,
  knowledgeTree,
  loadAll,
  loading,
  pointDialogVisible,
  pointForm,
  pointFormRef,
  pointRules,
  relationKeyword,
  showGraph,
  stats,
  submitting,
  submitPointForm
} = useTeacherKnowledgeManage()
</script>

<style scoped src="./KnowledgeManageView.css"></style>

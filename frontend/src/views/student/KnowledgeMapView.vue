<template>
  <div class="knowledge-map-view fade-in-up">
    <el-card class="map-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>知识图谱</span>
          <div class="header-actions">
            <el-button-group>
              <el-button :type="viewMode === 'graph' ? 'primary' : ''" @click="viewMode = 'graph'">
                图谱视图
              </el-button>
              <el-button :type="viewMode === 'list' ? 'primary' : ''" @click="viewMode = 'list'">
                列表视图
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 图谱视图 -->
      <div v-else-if="viewMode === 'graph'" class="graph-container">
        <KnowledgeGraphECharts v-if="graphData.nodes.length" :data="graphData" :height="'calc(100vh - 220px)'"
          mode="view" :courseId="courseStore.courseId" :showDrawer="false" @node-click="handleNodeClick" />
        <el-empty v-else description="暂无知识图谱数据" />
      </div>

      <!-- 列表视图 -->
      <div v-else class="list-container">
        <el-tree :data="knowledgeTree" :props="{ label: 'labelText', children: 'children' }" node-key="treeId"
          default-expand-all>
          <template #default="{ node, data }">
            <div class="tree-node" @click="handleTreeNodeClick(data)">
              <span>{{ node.label }}</span>
              <el-progress :percentage="data.masteryPercent || 0" :stroke-width="6"
                :format="(percentage) => `${percentage}%`" style="width: 100px; margin-left: 16px;" />
            </div>
          </template>
        </el-tree>
      </div>
    </el-card>

    <!-- 知识点详情抽屉 -->
    <el-drawer v-model="drawerVisible" :title="selectedPoint?.pointName || '知识点详情'" direction="rtl" size="400px">
      <div v-if="selectedPoint" class="point-detail">
        <div class="detail-section">
          <h4>掌握程度</h4>
          <el-progress :percentage="Math.round((selectedPoint.masteryRate || 0) * 100)" :stroke-width="12"
            :color="getMasteryColor(selectedPoint.masteryRate)" />
        </div>

        <div v-if="selectedPoint.tagList.length || selectedPoint.cognitiveDimensionText || selectedPoint.categoryText"
          class="detail-section">
          <h4>属性信息</h4>
          <div class="point-attrs">
            <el-tag v-if="selectedPoint.cognitiveDimensionText" size="small" type="warning">{{
              selectedPoint.cognitiveDimensionText }}</el-tag>
            <el-tag v-if="selectedPoint.categoryText" size="small" type="success">{{ selectedPoint.categoryText
              }}</el-tag>
            <el-tag v-for="tagText in selectedPoint.tagList" :key="tagText" size="small" type="info">{{ tagText
              }}</el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.teachingGoalText" class="detail-section">
          <h4>教学目标</h4>
          <p>{{ selectedPoint.teachingGoalText }}</p>
        </div>

        <div class="detail-section">
          <h4>概念描述</h4>
          <p>{{ selectedPoint.descriptionText || '暂无描述' }}</p>
        </div>

        <div v-if="selectedPoint.graphRagSummary || selectedPoint.graphRagSourceList.length" class="detail-section">
          <h4>GraphRAG 证据</h4>
          <p>{{ selectedPoint.graphRagSummary || '当前知识点暂无额外图谱证据摘要。' }}</p>
          <div v-if="selectedPoint.graphRagSourceList.length" class="point-tags evidence-tags">
            <el-tag v-for="sourceItem in selectedPoint.graphRagSourceList" :key="sourceItem.sourceKey" size="small"
              type="success">
              {{ sourceItem.sourceTitle }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.prerequisiteList.length" class="detail-section">
          <h4>前置知识</h4>
          <div class="point-tags">
            <el-tag v-for="relatedPoint in selectedPoint.prerequisiteList" :key="relatedPoint.pointId" size="small"
              type="info" class="clickable-tag" @click="loadPointDetail(relatedPoint.pointId)">
              {{ relatedPoint.pointName }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.postrequisiteList.length" class="detail-section">
          <h4>后续知识</h4>
          <div class="point-tags">
            <el-tag v-for="relatedPoint in selectedPoint.postrequisiteList" :key="relatedPoint.pointId" size="small"
              class="clickable-tag" @click="loadPointDetail(relatedPoint.pointId)">
              {{ relatedPoint.pointName }}
            </el-tag>
          </div>
        </div>

        <div v-if="selectedPoint.resourceList.length" class="detail-section">
          <h4>相关资源</h4>
          <div class="resource-list">
            <div v-for="resourceItem in selectedPoint.resourceList" :key="resourceItem.resourceId" class="resource-item"
              @click="openResource(resourceItem)">
              <el-icon>
                <VideoPlay v-if="resourceItem.resourceType === 'video'" />
                <Document v-else-if="resourceItem.resourceType === 'document'" />
                <Edit v-else />
              </el-icon>
              <span class="resource-title">{{ resourceItem.resourceTitle }}</span>
              <span v-if="resourceItem.durationText" class="resource-duration">{{ resourceItem.durationText }}</span>
            </div>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="goToLearning">
            开始学习
          </el-button>
        </div>
      </div>
    </el-drawer>

  </div>
</template>

<script setup>
import { VideoPlay, Document, Edit } from '@element-plus/icons-vue'
import KnowledgeGraphECharts from '@/components/knowledge/KnowledgeGraphECharts.vue'
import { useStudentKnowledgeMap } from './useStudentKnowledgeMap'

const {
  courseStore,
  drawerVisible,
  getMasteryColor,
  goToLearning,
  graphData,
  handleNodeClick,
  handleTreeNodeClick,
  knowledgeTree,
  loadPointDetail,
  loading,
  openResource,
  selectedPoint,
  viewMode
} = useStudentKnowledgeMap()
</script>

<style scoped src="./KnowledgeMapView.css"></style>

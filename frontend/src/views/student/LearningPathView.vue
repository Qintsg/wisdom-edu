<template>
  <div class="learning-path-view">
    <el-alert v-if="needAssessment" type="warning" :title="assessmentHint" show-icon :closable="false"
      class="assessment-alert">
      <template #default>
        <el-button type="warning" link @click="goToAssessment">
          前往初始测评
        </el-button>
      </template>
    </el-alert>

    <!-- 头部统计卡片 -->
    <el-card class="path-header" shadow="hover">
      <div class="header-top">
        <div class="header-title-row">
          <h2>学习路径</h2>
          <el-button type="primary" plain @click="refreshPath" :disabled="needAssessment" :loading="refreshingPath"
            class="refresh-btn">
            主动刷新路径
          </el-button>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-value">{{ completedNodes }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ totalNodes }}</div>
            <div class="stat-label">总任务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ progressPercent }}%</div>
            <div class="stat-label">完成度</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 路径主内容区 -->
    <el-card class="path-content" shadow="hover">
      <!-- 路径生成中 —— DEMO_EMBED: 答辩演示伪进度条 -->
      <div v-if="showRefreshingAnimation" class="generating-container">
        <el-icon class="is-loading" :size="48" color="#667eea">
          <Loading />
        </el-icon>
        <h3>{{ aiProgressStageText }}</h3>
        <el-progress :percentage="aiProgressPercentage" :stroke-width="10" :show-text="true"
          style="width: 320px; margin: 12px 0;" />
        <p style="color: #909399;">{{ refreshingDescription }}</p>
        <el-button v-if="!refreshingPath && !isAiProgressRunning" type="primary" style="margin-top: 16px;"
          @click="loadLearningPath">刷新查看</el-button>
      </div>

      <!-- 加载状态 -->
      <div v-else-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="loadError" :description="loadError">
        <el-button type="primary" @click="loadLearningPath">重新加载</el-button>
      </el-empty>
      <el-empty v-else-if="!courseStore.courseId" description="请先在顶部选择课程" />
      <el-empty v-else-if="!pathNodes.length && needAssessment" description="请先完成初始测评以生成个性化学习路径">
        <el-button type="primary" @click="goToAssessment">前往初始测评</el-button>
      </el-empty>
      <el-empty v-else-if="!pathNodes.length" description="暂无学习路径数据" />

      <!-- 横向步骤条（地铁线路图风格） -->
      <template v-else>
        <div class="subway-track-wrapper" ref="trackWrapperRef">
          <div class="subway-track" ref="trackRef">
            <div v-for="(pathNode, idx) in pathNodes" :key="pathNode.nodeId" class="subway-station"
              :class="{ active: selectedNode?.nodeId === pathNode.nodeId }" @click="selectNode(pathNode)">
              <!-- 连接线（第一个节点前不加） -->
              <div v-if="idx > 0" class="station-line"
                :class="{ done: pathNodes[idx - 1].learningStatus === 'completed' }" />
              <!-- 站点圆圈 -->
              <div class="station-dot" :class="[pathNode.learningStatus, pathNode.nodeTypeText]">
                <el-icon v-if="pathNode.learningStatus === 'completed'" :size="14">
                  <Check />
                </el-icon>
                <el-icon v-else-if="pathNode.nodeTypeText === 'test'" :size="14">
                  <Edit />
                </el-icon>
                <span v-else class="dot-index">{{ idx + 1 }}</span>
              </div>
              <!-- 站点名称 -->
              <div class="station-label" :class="pathNode.learningStatus">
                {{ pathNode.titleText }}
              </div>
            </div>
          </div>
        </div>

        <!-- 选中节点的详情面板 -->
        <transition name="detail-fade">
          <div v-if="selectedNode" class="node-detail-panel">
            <div class="detail-header">
              <div class="detail-title-row">
                <el-icon v-if="selectedNode.nodeTypeText === 'test'" style="color: #e6a23c; font-size: 20px;">
                  <Edit />
                </el-icon>
                <h3>{{ selectedNode.titleText }}</h3>
                <el-tag v-if="selectedNode.nodeTypeText === 'test'" type="warning" size="small">测试</el-tag>
                <el-tag :type="getNodeTagType(selectedNode.learningStatus)" size="small">
                  {{ getNodeStatusText(selectedNode.learningStatus) }}
                </el-tag>
              </div>
              <div class="detail-meta">
                <span><el-icon>
                    <Clock />
                  </el-icon> 预计 {{ selectedNode.durationMinutes }} 分钟</span>
              </div>
            </div>

            <div class="detail-body">
              <p class="detail-desc">{{ selectedNode.descriptionText }}</p>
              <div v-if="selectedNode.suggestionText" class="detail-suggestion">
                <el-icon>
                  <MagicStick />
                </el-icon>
                <span>{{ selectedNode.suggestionText }}</span>
              </div>
            </div>

            <div class="detail-actions">
              <!-- 当前节点 - 测试类型 -->
              <template v-if="selectedNode.learningStatus === 'current' && selectedNode.nodeTypeText === 'test'">
                <el-button type="warning" @click="startLearning(selectedNode)">
                  <el-icon style="margin-right: 4px;">
                    <Edit />
                  </el-icon> 开始测试
                </el-button>
                <el-button plain @click="handleSkipNode(selectedNode)">跳过</el-button>
              </template>
              <!-- 当前节点 - 学习类型 -->
              <template v-else-if="selectedNode.learningStatus === 'current'">
                <el-button type="primary" @click="startLearning(selectedNode)">开始学习</el-button>
                <el-button type="success" plain @click="handleCompleteNode(selectedNode)">标记完成</el-button>
                <el-button plain @click="handleSkipNode(selectedNode)">跳过</el-button>
              </template>
              <!-- 已完成 - 测试类型 -->
              <template v-else-if="selectedNode.learningStatus === 'completed' && selectedNode.nodeTypeText === 'test'">
                <el-button type="primary" plain @click="viewTestReport(selectedNode)">查看报告</el-button>
                <el-button type="warning" plain @click="startLearning(selectedNode)">再做一次</el-button>
              </template>
              <!-- 已完成 - 学习类型 -->
              <el-button v-else-if="selectedNode.learningStatus === 'completed'" @click="reviewNode(selectedNode)">
                复习巩固
              </el-button>
              <el-button v-else-if="selectedNode.learningStatus === 'skipped'" type="warning" plain
                @click="startLearning(selectedNode)">
                返回学习
              </el-button>
              <el-button v-else disabled>待解锁</el-button>
            </div>
          </div>
        </transition>

        <!-- 未选中节点时的提示 -->
        <div v-if="!selectedNode" class="select-hint">
          <el-icon :size="32" color="#c0c4cc">
            <Pointer />
          </el-icon>
          <p>点击上方节点查看详情和操作</p>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { Clock, Edit, Check, Pointer, MagicStick, Loading } from '@element-plus/icons-vue'
import { useLearningPath } from './useLearningPath'

const {
  aiProgressPercentage,
  aiProgressStageText,
  assessmentHint,
  completedNodes,
  courseStore,
  getNodeStatusText,
  getNodeTagType,
  goToAssessment,
  handleCompleteNode,
  handleSkipNode,
  isAiProgressRunning,
  loadError,
  loadLearningPath,
  loading,
  needAssessment,
  pathNodes,
  progressPercent,
  refreshPath,
  refreshingDescription,
  refreshingPath,
  reviewNode,
  selectedNode,
  selectNode,
  showRefreshingAnimation,
  startLearning,
  totalNodes,
  trackRef,
  trackWrapperRef,
  viewTestReport
} = useLearningPath()
</script>

<style scoped src="./LearningPathView.css"></style>

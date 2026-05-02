<template>
  <div class="knowledge-graph-container" ref="containerRef">
    <!-- Toolbar keeps filtering, search, zoom, and edit actions in one stable control band. -->
    <div class="graph-toolbar glass-panel">
      <template v-if="mode === 'edit'">
        <el-button-group>
          <el-button type="primary" size="small" @click="addNode">添加节点</el-button>
          <el-button type="warning" size="small" @click="saveGraph">保存图谱</el-button>
        </el-button-group>
        <div class="toolbar-divider"></div>
      </template>

      <el-select v-model="chapterFilter" placeholder="全部章节" clearable size="small" style="width: 150px">
        <el-option v-for="chapter in chapterList" :key="chapter" :label="chapter" :value="chapter" />
      </el-select>
      <el-input v-model="searchText" placeholder="搜索知识点..." size="small" style="width: 180px" clearable />
      <el-button-group>
        <el-button size="small" @click="zoomIn" title="放大">+</el-button>
        <el-button size="small" @click="zoomOut" title="缩小">-</el-button>
        <el-button size="small" @click="fitView" title="适配">⊡</el-button>
      </el-button-group>
    </div>

    <!-- Legend swaps node meaning between learner view and graph editing view. -->
    <div class="graph-legend glass-panel">
      <template v-if="mode === 'view'">
        <span class="legend-item"><span class="legend-dot mastered"></span>已掌握</span>
        <span class="legend-item"><span class="legend-dot reinforce"></span>需巩固</span>
        <span class="legend-item"><span class="legend-dot weak"></span>薄弱</span>
        <span class="legend-item"><span class="legend-dot unknown"></span>未学习</span>
      </template>
      <template v-else>
        <span class="legend-item"><span class="legend-dot chapter"></span>章节节点</span>
      </template>
      <span class="legend-item"><span class="legend-line prerequisite"></span>先修关系</span>
      <span class="legend-item"><span class="legend-line related"></span>关联关系</span>
      <span class="legend-item"><span class="legend-line includes"></span>包含关系</span>
    </div>

    <!-- SVG stays inside a dedicated surface so resize and fit logic can read stable bounds. -->
    <div ref="graphSurfaceRef" class="graph-surface"
      :style="{ height: typeof height === 'number' ? `${height}px` : height }">
      <svg ref="svgRef" class="graph-svg"></svg>
    </div>

    <!-- Drawer shows either readonly detail or inline edit controls for the selected node. -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="30%" :destroy-on-close="true">
      <div v-if="selectedNode" class="node-drawer">
        <!-- Base node fields are always shown so selection has a predictable detail layout. -->
        <el-form label-position="top">
          <el-form-item label="名称">
            <el-input v-model="selectedNode.nodeName" :disabled="mode === 'view'" />
          </el-form-item>
          <el-form-item label="章节">
            <el-input v-model="selectedNode.chapterText" :disabled="mode === 'view'" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="selectedNode.nodeDescription" type="textarea" :rows="3" :disabled="mode === 'view'" />
          </el-form-item>
          <el-form-item v-if="mode === 'view' && selectedNode.masteryRate !== null" label="掌握度">
            <el-progress :percentage="Math.round((selectedNode.masteryRate || 0) * 100)"
              :color="getMasteryColor(selectedNode.masteryRate)" />
          </el-form-item>
        </el-form>

        <!-- Resource links are loaded lazily only for the active node in student view. -->
        <div v-if="nodeResources.length" class="resources-section">
          <h4>相关资源</h4>
          <div class="drawer-resource-list">
            <div v-for="resource in nodeResources" :key="resource.resourceId" class="drawer-resource-item">
              <span>{{ resource.resourceTitle }}</span>
              <el-link :href="resource.resourceUrl" target="_blank" type="primary">打开</el-link>
            </div>
          </div>
        </div>

        <div class="drawer-actions" v-if="mode === 'edit'">
          <el-button type="primary" @click="updateNodeData">更新节点</el-button>
          <el-button type="danger" @click="deleteNode">删除节点</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { useKnowledgeGraphD3 } from './useKnowledgeGraphD3'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({ nodes: [], edges: [] })
  },
  mode: {
    type: String,
    default: 'view'
  },
  height: {
    type: [Number, String],
    default: 600
  },
  courseId: {
    type: [Number, String],
    default: null
  },
  showDrawer: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['save', 'node-click', 'resource-link'])

const {
  addNode,
  chapterFilter,
  chapterList,
  containerRef,
  deleteNode,
  drawerTitle,
  drawerVisible,
  fitView,
  getMasteryColor,
  graphSurfaceRef,
  nodeResources,
  saveGraph,
  searchText,
  selectedNode,
  svgRef,
  updateNodeData,
  zoomIn,
  zoomOut
} = useKnowledgeGraphD3(props, emit)
</script>

<style scoped src="./KnowledgeGraphECharts.css"></style>

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
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as d3 from 'd3'
import { ElMessage } from 'element-plus'
import { getKnowledgePointDetail } from '@/api/student/knowledge'
import { toBackendAbsoluteUrl } from '@/api/backend'

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

/**
 * @typedef {{
 *   nodeId: string,
 *   pointId: string,
 *   nodeName: string,
 *   chapterText: string,
 *   nodeDescription: string,
 *   masteryRate: number | null
 * }} GraphNodeModel
 */

/**
 * @typedef {{
 *   edgeId: string,
 *   sourceNodeId: string,
 *   targetNodeId: string,
 *   relationType: string
 * }} GraphEdgeModel
 */

/**
 * @typedef {{
 *   resourceId: string,
 *   resourceTitle: string,
 *   resourceUrl: string
 * }} GraphResourceModel
 */

/**
 * 统一文本型动态值，避免模板和逻辑直接碰撞后端原始字段。
 */
function normalizeText(value, fallback = '') {
  if (Array.isArray(value)) {
    return normalizeText(value[0], fallback)
  }
  if (typeof value === 'string') {
    const trimmedValue = value.trim()
    return trimmedValue || fallback
  }
  if (typeof value === 'number') {
    return String(value)
  }
  return fallback
}

/**
 * 统一标识符，兼容数字、字符串和空值。
 */
function normalizeIdentifier(value, fallback = '') {
  if (Array.isArray(value)) {
    return normalizeIdentifier(value[0], fallback)
  }
  if (value === null || value === undefined) {
    return fallback
  }
  const normalizedValue = String(value).trim()
  return normalizedValue || fallback
}

/**
 * 统一列表载荷，保证 map/filter 只处理数组。
 */
function normalizeListFromPayload(value) {
  return Array.isArray(value) ? value : []
}

/**
 * 可选数值字段保留 null，避免把未知掌握度误判成 0。
 */
function normalizeOptionalNumber(value) {
  if (value === null || value === undefined || value === '') {
    return null
  }
  const parsedValue = Number(value)
  return Number.isFinite(parsedValue) ? parsedValue : null
}

/**
 * 节点一律转成内部 camelCase 图模型。
 * @param {Record<string, any>} node
 * @param {number} index
 * @returns {GraphNodeModel}
 */
function normalizeGraphNode(node, index) {
  return {
    nodeId: normalizeIdentifier(node?.['id'] ?? node?.['point_id'], `node-${index}`),
    pointId: normalizeIdentifier(node?.['point_id'] ?? node?.['id']),
    nodeName: normalizeText(node?.['name'] ?? node?.['point_name'], '未命名知识点'),
    chapterText: normalizeText(node?.['chapter']),
    nodeDescription: normalizeText(node?.['description']),
    masteryRate: normalizeOptionalNumber(node?.['mastery'] ?? node?.['mastery_rate'])
  }
}

/**
 * 边模型统一后，筛选和保存逻辑不再直接读 source_id/target_id。
 * @param {Record<string, any>} edge
 * @param {number} index
 * @returns {GraphEdgeModel}
 */
function normalizeGraphEdge(edge, index) {
  return {
    edgeId: normalizeIdentifier(edge?.['id'], `edge-${index}`),
    sourceNodeId: normalizeIdentifier(edge?.['source'] ?? edge?.['source_id']),
    targetNodeId: normalizeIdentifier(edge?.['target'] ?? edge?.['target_id']),
    relationType: normalizeText(edge?.['relation_type'] ?? edge?.['label'], 'related')
  }
}

/**
 * 资源项也统一成稳定字段，抽屉模板只依赖内部模型。
 * @param {Record<string, any>} resource
 * @param {number} index
 * @returns {GraphResourceModel}
 */
function normalizeResourceItem(resource, index) {
  return {
    resourceId: normalizeIdentifier(resource?.['resource_id'] ?? resource?.['id'], `resource-${index}`),
    resourceTitle: normalizeText(resource?.['title'], '未命名资源'),
    resourceUrl: toBackendAbsoluteUrl(normalizeText(resource?.['url']))
  }
}

/**
 * 详情接口返回后，抽屉节点继续沿用同一内部字段名。
 * @param {GraphNodeModel} node
 * @param {Record<string, any>} detail
 * @returns {GraphNodeModel}
 */
function normalizeNodeDetail(node, detail = {}) {
  return {
    ...node,
    nodeName: normalizeText(detail?.['point_name'] ?? detail?.['name'], node.nodeName),
    chapterText: normalizeText(detail?.['chapter'], node.chapterText),
    nodeDescription: normalizeText(detail?.['description'], node.nodeDescription),
    masteryRate: normalizeOptionalNumber(detail?.['mastery_rate'] ?? detail?.['mastery']) ?? node.masteryRate
  }
}

/**
 * 抽屉资源列表统一为内部模型。
 * @param {Record<string, any>} detail
 * @returns {GraphResourceModel[]}
 */
function normalizeNodeResources(detail) {
  return normalizeListFromPayload(detail?.['resources'])
    .map((resource, index) => normalizeResourceItem(resource, index))
}

/**
 * D3 link 在 forceSimulation 后会把 source/target 替换成对象，用 helper 统一读取坐标。
 */
function getLinkCoordinate(linkDatum, endpointKey, coordinateKey) {
  const endpoint = linkDatum?.[endpointKey]
  if (endpoint && typeof endpoint === 'object') {
    const coordinate = Number(endpoint[coordinateKey])
    return Number.isFinite(coordinate) ? coordinate : 0
  }
  return 0
}

// DOM refs for the SVG surface and its containing layout boxes.
/** @type {import('vue').Ref<HTMLDivElement | null>} */
const containerRef = ref(null)
/** @type {import('vue').Ref<HTMLDivElement | null>} */
const graphSurfaceRef = ref(null)
/** @type {import('vue').Ref<SVGSVGElement | null>} */
const svgRef = ref(null)

// UI control state lives outside the graph engine so filters redraw deterministically.
const searchText = ref('')
const chapterFilter = ref('')
const drawerVisible = ref(false)
const drawerTitle = ref('知识点详情')
/** @type {import('vue').Ref<GraphNodeModel | null>} */
const selectedNode = ref(null)
/** @type {import('vue').Ref<GraphResourceModel[]>} */
const nodeResources = ref([])

// D3 instances are stored in shallow refs because Vue does not need deep tracking here.
/** @type {import('vue').ShallowRef<any>} */
const zoomBehaviorRef = shallowRef(null)
/** @type {import('vue').ShallowRef<any>} */
const svgSelectionRef = shallowRef(null)
/** @type {import('vue').ShallowRef<any>} */
const contentLayerRef = shallowRef(null)
/** @type {import('vue').ShallowRef<any>} */
const simulationRef = shallowRef(null)
/** @type {import('vue').ShallowRef<ResizeObserver | null>} */
const resizeObserverRef = shallowRef(null)

// Local copies isolate edit mode from direct prop mutation.
/** @type {import('vue').Ref<GraphNodeModel[]>} */
const localNodes = ref([])
/** @type {import('vue').Ref<GraphEdgeModel[]>} */
const localEdges = ref([])

// D3 helpers use aliases so the IDE no longer confuses them with unknown instance methods.
const d3Select = d3['select']
const d3Zoom = d3['zoom']
const d3Drag = d3['drag']
const d3ZoomIdentity = d3['zoomIdentity']
const d3ForceLink = d3['forceLink']
const d3ForceCenter = d3['forceCenter']

const chapterList = computed(() => {
  const chapters = new Set()
  localNodes.value.forEach((node) => {
    if (node.chapterText) {
      chapters.add(node.chapterText)
    }
  })
  return [...chapters].sort()
})

// Visible nodes apply both chapter and keyword filters before the expensive redraw step.
const visibleNodes = computed(() => {
  const keyword = normalizeText(searchText.value).toLowerCase()
  return localNodes.value.filter((node) => {
    const chapterMatch = !chapterFilter.value || node.chapterText === chapterFilter.value
    const keywordMatch = !keyword || `${node.nodeName}${node.nodeDescription}`.toLowerCase().includes(keyword)
    return chapterMatch && keywordMatch
  })
})

const visibleNodeIds = computed(() => new Set(visibleNodes.value.map((node) => node.nodeId)))

// Edges are hidden unless both endpoints survive the current node filters.
const visibleEdges = computed(() =>
  localEdges.value.filter(
    (edge) =>
      visibleNodeIds.value.has(edge.sourceNodeId) &&
      visibleNodeIds.value.has(edge.targetNodeId)
  )
)

// Node colors mean mastery in student view and editability in authoring mode.
const getMasteryColor = (masteryRate) => {
  if (props.mode === 'edit') return '#2563eb'
  if (masteryRate === undefined || masteryRate === null) return '#94a3b8'
  if (masteryRate >= 0.8) return '#0f9d58'
  if (masteryRate >= 0.6) return '#d97706'
  return '#dc2626'
}

// Relation styling mirrors the legend so line meaning stays readable without labels.
const getRelationStroke = (relationType) => {
  if (relationType === 'prerequisite') {
    return { color: '#475569', dash: null, width: 1.8 }
  }
  if (relationType === 'related') {
    return { color: '#94a3b8', dash: '2 8', width: 1.4 }
  }
  return { color: '#64748b', dash: '10 6', width: 1.3 }
}

const syncLocalGraph = () => {
  // Normalize backend node shapes into a single graph schema before D3 touches them.
  localNodes.value = normalizeListFromPayload(props.data?.['nodes']).map((node, index) => normalizeGraphNode(node, index))
  // Edge endpoints are always coerced to strings because D3 link ids must match node ids exactly.
  localEdges.value = normalizeListFromPayload(props.data?.['edges']).map((edge, index) => normalizeGraphEdge(edge, index))
}

const stopSimulation = () => {
  simulationRef.value?.stop()
  simulationRef.value = null
}

const cleanupGraph = () => {
  // Every full redraw starts from a blank SVG to avoid stale nodes, markers, and listeners.
  stopSimulation()
  if (svgSelectionRef.value) {
    svgSelectionRef.value.selectAll('*').remove()
  }
}

const fitView = () => {
  if (!svgSelectionRef.value || !contentLayerRef.value || !graphSurfaceRef.value || !zoomBehaviorRef.value) {
    return
  }

  const bounds = contentLayerRef.value.node().getBBox()
  if (!bounds.width || !bounds.height) {
    return
  }

  const surfaceRect = graphSurfaceRef.value.getBoundingClientRect()
  // Clamp zoom so tiny subgraphs do not explode and large ones stay readable after filtering.
  const scale = Math.max(
    0.45,
    Math.min(
      1.25,
      0.9 / Math.max(bounds.width / surfaceRect.width, bounds.height / surfaceRect.height)
    )
  )
  const translateX = surfaceRect.width / 2 - scale * (bounds.x + bounds.width / 2)
  const translateY = surfaceRect.height / 2 - scale * (bounds.y + bounds.height / 2)

  svgSelectionRef.value
    .transition()
    .duration(260)
    .call(
      zoomBehaviorRef.value.transform,
      d3ZoomIdentity.translate(translateX, translateY).scale(scale)
    )
}

const zoomIn = () => {
  svgSelectionRef.value?.transition().duration(180).call(zoomBehaviorRef.value.scaleBy, 1.15)
}

const zoomOut = () => {
  svgSelectionRef.value?.transition().duration(180).call(zoomBehaviorRef.value.scaleBy, 0.85)
}

const handleNodeClick = async (node) => {
  emit('node-click', node)
  if (!props.showDrawer) {
    return
  }

  drawerTitle.value = node.nodeName || '知识点详情'

  if (props.mode === 'view' && props.courseId && node.pointId) {
    try {
      // Student view enriches the lightweight graph node with server-backed mastery and resources.
      const detail = await getKnowledgePointDetail(node.pointId, props.courseId)
      selectedNode.value = normalizeNodeDetail(node, detail)
      nodeResources.value = normalizeNodeResources(detail)
    } catch (error) {
      // Drawer still opens with local data so graph exploration is not blocked by detail failures.
      selectedNode.value = { ...node }
      nodeResources.value = []
      ElMessage.warning('知识点详情加载失败，已展示基础信息')
    }
  } else {
    selectedNode.value = { ...node }
    nodeResources.value = []
  }

  drawerVisible.value = true
}

const renderGraph = async () => {
  await nextTick()

  if (!svgRef.value || !graphSurfaceRef.value) {
    return
  }

  cleanupGraph()

  // D3 works against filtered clones so forces can mutate positions without polluting source state.
  const width = graphSurfaceRef.value.clientWidth || 960
  const heightValue = graphSurfaceRef.value.clientHeight || 640
  const searchKeyword = normalizeText(searchText.value).toLowerCase()
  const nodes = visibleNodes.value.map((node) => ({ ...node }))
  const edges = visibleEdges.value.map((edge) => ({
    edgeId: edge.edgeId,
    source: edge.sourceNodeId,
    target: edge.targetNodeId,
    relationType: edge.relationType
  }))

  const svg = d3Select(svgRef.value)
    .attr('viewBox', [0, 0, width, heightValue])
    .attr('width', width)
    .attr('height', heightValue)

  svgSelectionRef.value = svg

  svg.append('defs')
    .append('marker')
    .attr('id', 'graph-arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 18)
    .attr('refY', 0)
    .attr('markerWidth', 8)
    .attr('markerHeight', 8)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill', '#64748b')

  const contentLayer = svg.append('g').attr('class', 'graph-content')
  contentLayerRef.value = contentLayer

  // Zoom transforms only the content layer so the SVG viewport itself stays stable.
  const zoom = d3Zoom()
    .scaleExtent([0.35, 2.5])
    .on('zoom', (event) => {
      contentLayer.attr('transform', event.transform)
    })

  zoomBehaviorRef.value = zoom
  svg.call(zoom)

  const link = contentLayer
    .append('g')
    .attr('class', 'graph-links')
    .selectAll('line')
    .data(edges)
    .join('line')
    .attr('stroke', (edge) => getRelationStroke(edge.relationType).color)
    .attr('stroke-width', (edge) => getRelationStroke(edge.relationType).width)
    .attr('stroke-dasharray', (edge) => getRelationStroke(edge.relationType).dash)
    .attr('marker-end', 'url(#graph-arrow)')
    .attr('stroke-linecap', 'round')

  const node = contentLayer
    .append('g')
    .attr('class', 'graph-nodes')
    .selectAll('g')
    .data(nodes, (item) => item.nodeId)
    .join('g')
    .attr('class', 'graph-node')
    .style('cursor', 'pointer')
    .on('click', (_event, datum) => handleNodeClick(datum))

  node
    .append('circle')
    .attr('r', (datum) => {
      // Search hits get a slightly larger radius instead of a second highlight layer.
      const highlighted = Boolean(searchKeyword) && datum.nodeName.toLowerCase().includes(searchKeyword)
      return highlighted ? 26 : 21
    })
    .attr('fill', (datum) => getMasteryColor(datum.masteryRate))
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 2.5)

  node
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', 36)
    .attr('fill', 'var(--text-primary)')
    .attr('font-size', 12)
    .attr('font-weight', 600)
    .text((datum) => (datum.nodeName.length > 10 ? `${datum.nodeName.slice(0, 10)}…` : datum.nodeName))

  const drag = d3Drag()
    .on('start', (event, datum) => {
      if (!event.active) {
        simulation.alphaTarget(0.25).restart()
      }
      datum.fx = datum.x
      datum.fy = datum.y
    })
    .on('drag', (event, datum) => {
      datum.fx = event.x
      datum.fy = event.y
    })
    .on('end', (event, datum) => {
      if (!event.active) {
        simulation.alphaTarget(0)
      }
      // View mode releases nodes back to the force layout, while edit mode keeps manual placement.
      if (props.mode !== 'edit') {
        datum.fx = null
        datum.fy = null
      }
    })

  node.call(drag)

  const simulation = d3
    .forceSimulation(nodes)
    // Distances favor readable chapter clusters without collapsing related nodes into one blob.
    .force('link', d3ForceLink(edges).id((datum) => datum.nodeId).distance(170))
    .force('charge', d3.forceManyBody().strength(-420))
    .force('center', d3ForceCenter(width / 2, heightValue / 2))
    .force('collide', d3.forceCollide().radius(42))

  simulation.on('tick', () => {
    link
      .attr('x1', (datum) => getLinkCoordinate(datum, 'source', 'x'))
      .attr('y1', (datum) => getLinkCoordinate(datum, 'source', 'y'))
      .attr('x2', (datum) => getLinkCoordinate(datum, 'target', 'x'))
      .attr('y2', (datum) => getLinkCoordinate(datum, 'target', 'y'))

    node.attr('transform', (datum) => `translate(${datum.x},${datum.y})`)
  })

  simulationRef.value = simulation
  // Fit after the first paint so bounding boxes include the final text and marker geometry.
  requestAnimationFrame(() => fitView())
}

const addNode = () => {
  // New nodes default into the current chapter filter so edit mode feels context-aware.
  const chapterText = chapterFilter.value || chapterList.value[0] || '未分类'
  const newNode = {
    nodeId: `temp-${Date.now()}`,
    pointId: '',
    nodeName: '新知识点',
    chapterText,
    nodeDescription: '',
    masteryRate: null
  }
  localNodes.value = [...localNodes.value, newNode]
  selectedNode.value = { ...newNode }
  drawerTitle.value = '新增知识点'
  drawerVisible.value = true
}

const updateNodeData = () => {
  if (!selectedNode.value) {
    return
  }
  // Replace by id so reactive updates keep ordering and existing edge references intact.
  localNodes.value = localNodes.value.map((node) =>
    node.nodeId === selectedNode.value.nodeId
      ? {
        ...node,
        ...selectedNode.value,
        pointId: selectedNode.value.pointId || node.pointId
      }
      : node
  )
  drawerVisible.value = false
}

const deleteNode = () => {
  if (!selectedNode.value) {
    return
  }
  // Removing the node also removes connected edges to keep the saved graph consistent.
  localNodes.value = localNodes.value.filter((node) => node.nodeId !== selectedNode.value.nodeId)
  localEdges.value = localEdges.value.filter(
    (edge) => edge.sourceNodeId !== selectedNode.value.nodeId && edge.targetNodeId !== selectedNode.value.nodeId
  )
  drawerVisible.value = false
}

const saveGraph = () => {
  // Save emits a backend-friendly payload instead of leaking D3-mutated node objects upward.
  emit('save', {
    nodes: localNodes.value.map((node) => ({
      id: node.pointId || node.nodeId,
      point_id: node.pointId || node.nodeId,
      name: node.nodeName,
      point_name: node.nodeName,
      chapter: node.chapterText,
      description: node.nodeDescription
    })),
    edges: localEdges.value.map((edge) => ({
      id: edge.edgeId,
      source: edge.sourceNodeId,
      target: edge.targetNodeId,
      source_id: edge.sourceNodeId,
      target_id: edge.targetNodeId,
      relation_type: edge.relationType
    }))
  })
}

watch(
  () => props.data,
  () => {
    syncLocalGraph()
    void renderGraph()
  },
  { deep: true, immediate: true }
)

watch([chapterFilter, searchText], () => {
  // Filter changes rebuild the graph so forces and fitView reflect the smaller visible set.
  void renderGraph()
})

watch(
  () => props.height,
  () => {
    void renderGraph()
  }
)

onMounted(() => {
  // ResizeObserver catches card and layout changes that window.resize alone would miss.
  resizeObserverRef.value = new ResizeObserver(() => {
    void renderGraph()
  })
  if (graphSurfaceRef.value) {
    resizeObserverRef.value.observe(graphSurfaceRef.value)
  }
})

onBeforeUnmount(() => {
  resizeObserverRef.value?.disconnect()
  cleanupGraph()
})
</script>

<style scoped>
/* The container separates controls, legend, and drawing surface into clear layers. */
.knowledge-graph-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
}

.glass-panel {
  /* Shared glass styling keeps utility chrome visually lighter than the graph itself. */
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(18px);
}

.toolbar-divider {
  width: 1px;
  height: 28px;
  background: rgba(100, 116, 139, 0.18);
}

.graph-legend {
  gap: 18px;
  font-size: 12px;
  color: var(--text-secondary);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.legend-dot.mastered {
  background: #0f9d58;
}

.legend-dot.reinforce {
  background: #d97706;
}

.legend-dot.weak {
  background: #dc2626;
}

.legend-dot.unknown {
  background: #94a3b8;
}

.legend-dot.chapter {
  background: #2563eb;
}

.legend-line {
  width: 32px;
  border-top: 2px solid #64748b;
}

.legend-line.related {
  border-top-style: dotted;
}

.legend-line.includes {
  border-top-style: dashed;
}

.graph-surface {
  /* The subtle grid helps spatial reasoning without competing with node colors. */
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.92), rgba(241, 245, 249, 0.88)),
    linear-gradient(135deg, rgba(219, 234, 254, 0.45), rgba(255, 255, 255, 0.1));
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5), 0 20px 50px rgba(15, 23, 42, 0.08);
}

.graph-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(148, 163, 184, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

.graph-svg {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}

.node-drawer {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.resources-section h4 {
  margin: 0 0 10px;
}

.drawer-resource-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drawer-resource-item {
  /* Resource rows use a compact two-column layout so long titles still align with the action. */
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.drawer-actions {
  display: flex;
  gap: 12px;
}

@media (max-width: 768px) {
  .glass-panel {
    gap: 10px;
  }

  .graph-legend {
    gap: 12px;
  }
}
</style>

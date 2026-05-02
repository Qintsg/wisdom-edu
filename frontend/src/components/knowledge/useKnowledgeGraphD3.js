import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as d3 from 'd3'
import { ElMessage } from 'element-plus'
import { getKnowledgePointDetail } from '@/api/student/knowledge'
import {
  getLinkCoordinate,
  getRelationStroke,
  normalizeGraphEdge,
  normalizeGraphNode,
  normalizeListFromPayload,
  normalizeNodeDetail,
  normalizeNodeResources,
  normalizeText
} from './knowledgeGraphModels'

export function useKnowledgeGraphD3(props, emit) {
  const containerRef = ref(null)
  const graphSurfaceRef = ref(null)
  const svgRef = ref(null)
  const searchText = ref('')
  const chapterFilter = ref('')
  const drawerVisible = ref(false)
  const drawerTitle = ref('知识点详情')
  const selectedNode = ref(null)
  const nodeResources = ref([])
  const zoomBehaviorRef = shallowRef(null)
  const svgSelectionRef = shallowRef(null)
  const contentLayerRef = shallowRef(null)
  const simulationRef = shallowRef(null)
  const resizeObserverRef = shallowRef(null)
  const localNodes = ref([])
  const localEdges = ref([])

  const d3Select = d3['select']
  const d3Zoom = d3['zoom']
  const d3Drag = d3['drag']
  const d3ZoomIdentity = d3['zoomIdentity']
  const d3ForceLink = d3['forceLink']
  const d3ForceCenter = d3['forceCenter']

  const chapterList = computed(() => {
    const chapters = new Set()
    localNodes.value.forEach((node) => {
      if (node.chapterText) chapters.add(node.chapterText)
    })
    return [...chapters].sort()
  })

  const visibleNodes = computed(() => {
    const keyword = normalizeText(searchText.value).toLowerCase()
    return localNodes.value.filter((node) => {
      const chapterMatch = !chapterFilter.value || node.chapterText === chapterFilter.value
      const keywordMatch = !keyword || `${node.nodeName}${node.nodeDescription}`.toLowerCase().includes(keyword)
      return chapterMatch && keywordMatch
    })
  })

  const visibleNodeIds = computed(() => new Set(visibleNodes.value.map((node) => node.nodeId)))
  const visibleEdges = computed(() =>
    localEdges.value.filter(
      (edge) => visibleNodeIds.value.has(edge.sourceNodeId) && visibleNodeIds.value.has(edge.targetNodeId)
    )
  )

  const getMasteryColor = (masteryRate) => {
    if (props.mode === 'edit') return '#2563eb'
    if (masteryRate === undefined || masteryRate === null) return '#94a3b8'
    if (masteryRate >= 0.8) return '#0f9d58'
    if (masteryRate >= 0.6) return '#d97706'
    return '#dc2626'
  }

  const syncLocalGraph = () => {
    localNodes.value = normalizeListFromPayload(props.data?.['nodes']).map((node, index) => normalizeGraphNode(node, index))
    localEdges.value = normalizeListFromPayload(props.data?.['edges']).map((edge, index) => normalizeGraphEdge(edge, index))
  }

  const stopSimulation = () => {
    simulationRef.value?.stop()
    simulationRef.value = null
  }

  const cleanupGraph = () => {
    stopSimulation()
    if (svgSelectionRef.value) svgSelectionRef.value.selectAll('*').remove()
  }

  const fitView = () => {
    if (!svgSelectionRef.value || !contentLayerRef.value || !graphSurfaceRef.value || !zoomBehaviorRef.value) return

    const bounds = contentLayerRef.value.node().getBBox()
    if (!bounds.width || !bounds.height) return

    const surfaceRect = graphSurfaceRef.value.getBoundingClientRect()
    const scale = Math.max(
      0.45,
      Math.min(1.25, 0.9 / Math.max(bounds.width / surfaceRect.width, bounds.height / surfaceRect.height))
    )
    const translateX = surfaceRect.width / 2 - scale * (bounds.x + bounds.width / 2)
    const translateY = surfaceRect.height / 2 - scale * (bounds.y + bounds.height / 2)

    svgSelectionRef.value
      .transition()
      .duration(260)
      .call(zoomBehaviorRef.value.transform, d3ZoomIdentity.translate(translateX, translateY).scale(scale))
  }

  const zoomIn = () => {
    svgSelectionRef.value?.transition().duration(180).call(zoomBehaviorRef.value.scaleBy, 1.15)
  }

  const zoomOut = () => {
    svgSelectionRef.value?.transition().duration(180).call(zoomBehaviorRef.value.scaleBy, 0.85)
  }

  const handleNodeClick = async (node) => {
    emit('node-click', node)
    if (!props.showDrawer) return

    drawerTitle.value = node.nodeName || '知识点详情'

    if (props.mode === 'view' && props.courseId && node.pointId) {
      try {
        const detail = await getKnowledgePointDetail(node.pointId, props.courseId)
        selectedNode.value = normalizeNodeDetail(node, detail)
        nodeResources.value = normalizeNodeResources(detail)
      } catch (error) {
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

    if (!svgRef.value || !graphSurfaceRef.value) return

    cleanupGraph()

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
        if (!event.active) simulation.alphaTarget(0.25).restart()
        datum.fx = datum.x
        datum.fy = datum.y
      })
      .on('drag', (event, datum) => {
        datum.fx = event.x
        datum.fy = event.y
      })
      .on('end', (event, datum) => {
        if (!event.active) simulation.alphaTarget(0)
        if (props.mode !== 'edit') {
          datum.fx = null
          datum.fy = null
        }
      })

    node.call(drag)

    const simulation = d3
      .forceSimulation(nodes)
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
    requestAnimationFrame(() => fitView())
  }

  const addNode = () => {
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
    if (!selectedNode.value) return
    localNodes.value = localNodes.value.map((node) =>
      node.nodeId === selectedNode.value.nodeId
        ? { ...node, ...selectedNode.value, pointId: selectedNode.value.pointId || node.pointId }
        : node
    )
    drawerVisible.value = false
  }

  const deleteNode = () => {
    if (!selectedNode.value) return
    localNodes.value = localNodes.value.filter((node) => node.nodeId !== selectedNode.value.nodeId)
    localEdges.value = localEdges.value.filter(
      (edge) => edge.sourceNodeId !== selectedNode.value.nodeId && edge.targetNodeId !== selectedNode.value.nodeId
    )
    drawerVisible.value = false
  }

  const saveGraph = () => {
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
    void renderGraph()
  })

  watch(
    () => props.height,
    () => {
      void renderGraph()
    }
  )

  onMounted(() => {
    resizeObserverRef.value = new ResizeObserver(() => {
      void renderGraph()
    })
    if (graphSurfaceRef.value) resizeObserverRef.value.observe(graphSurfaceRef.value)
  })

  onBeforeUnmount(() => {
    resizeObserverRef.value?.disconnect()
    cleanupGraph()
  })

  return {
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
  }
}

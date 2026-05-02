import { toBackendAbsoluteUrl } from '@/api/backend'

export const resourceTypeOptions = [
  { optionLabel: '视频', optionValue: 'video' },
  { optionLabel: '文档', optionValue: 'document' },
  { optionLabel: '链接', optionValue: 'link' }
]

export const fileSizeLimits = {
  video: 500 * 1024 * 1024,
  document: 50 * 1024 * 1024
}

const acceptTypes = {
  video: '.mp4,.webm,.ogg',
  document: '.pdf,.doc,.docx,.ppt,.pptx'
}

const resourceTypeLabelMap = {
  video: '视频',
  document: '文档',
  link: '链接'
}

const resourceTypeTagMap = {
  video: 'primary',
  document: 'success',
  link: 'warning'
}

export const normalizeText = (rawValue) => {
  if (typeof rawValue === 'string') return rawValue
  if (typeof rawValue === 'number') return String(rawValue)
  return ''
}

const normalizeIdentifier = (rawValue) => normalizeText(rawValue).trim()

const normalizeNumber = (rawValue, fallbackValue = 0) => {
  const parsedValue = Number(rawValue)
  return Number.isFinite(parsedValue) ? parsedValue : fallbackValue
}

const normalizeListFromPayload = (rawValue) => Array.isArray(rawValue) ? rawValue : []

const normalizeResourceType = (rawValue) => {
  const resourceTypeText = normalizeText(rawValue).trim()
  return resourceTypeText || 'document'
}

const buildDefaultKnowledgePointOption = () => ({
  pointId: '',
  pointName: ''
})

const buildDefaultResourceRecord = () => ({
  resourceId: '',
  titleText: '',
  resourceTypeText: 'document',
  typeLabel: '文档',
  typeTagType: 'success',
  pointId: '',
  pointNameText: '',
  pointIdList: [],
  pointOptions: [],
  linkUrl: '',
  fileUrl: '',
  previewUrl: '',
  descriptionText: '',
  createdAtText: ''
})

const normalizeKnowledgePointOption = (rawPoint) => ({
  ...buildDefaultKnowledgePointOption(),
  pointId: normalizeIdentifier(rawPoint?.point_id ?? rawPoint?.knowledge_point_id ?? rawPoint?.id),
  pointName: normalizeText(rawPoint?.point_name ?? rawPoint?.name) || '未命名知识点'
})

const normalizeResourcePointOptions = (rawPoints) => {
  return normalizeListFromPayload(rawPoints)
    .map((rawPoint) => normalizeKnowledgePointOption(rawPoint))
}

const resolvePrimaryPointId = (rawResource, pointOptions) => {
  const explicitPointId = normalizeIdentifier(rawResource?.point_id ?? rawResource?.knowledge_point_id)
  return explicitPointId || pointOptions[0]?.pointId || ''
}

const resolvePointNameText = (pointOptions, rawPointName) => {
  if (pointOptions.length) {
    return pointOptions.map((pointOption) => pointOption.pointName).filter(Boolean).join(', ')
  }
  return normalizeText(rawPointName)
}

export const normalizeResourceRecord = (rawResource) => {
  const pointOptions = normalizeResourcePointOptions(rawResource?.points ?? rawResource?.knowledge_points)
  const resourceTypeText = normalizeResourceType(rawResource?.resource_type ?? rawResource?.type)
  const linkUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.url).trim())
  const fileUrl = toBackendAbsoluteUrl(normalizeText(rawResource?.file).trim())

  return {
    ...buildDefaultResourceRecord(),
    resourceId: normalizeIdentifier(rawResource?.resource_id ?? rawResource?.id),
    titleText: normalizeText(rawResource?.title),
    resourceTypeText,
    typeLabel: resourceTypeLabelMap[resourceTypeText] || resourceTypeText,
    typeTagType: resourceTypeTagMap[resourceTypeText] || 'info',
    pointId: resolvePrimaryPointId(rawResource, pointOptions),
    pointNameText: resolvePointNameText(pointOptions, rawResource?.point_name),
    pointIdList: pointOptions.map((pointOption) => pointOption.pointId).filter(Boolean),
    pointOptions,
    linkUrl,
    fileUrl,
    previewUrl: linkUrl || fileUrl,
    descriptionText: normalizeText(rawResource?.description),
    createdAtText: normalizeText(rawResource?.created_at)
  }
}

export const normalizeResourceListPayload = (rawPayload) => ({
  records: normalizeListFromPayload(rawPayload?.resources)
    .map((rawResource) => normalizeResourceRecord(rawResource)),
  totalCount: normalizeNumber(rawPayload?.total)
})

export const normalizeKnowledgePointListPayload = (rawPayload) => {
  return normalizeListFromPayload(rawPayload?.points)
    .map((rawPoint) => normalizeKnowledgePointOption(rawPoint))
}

export const buildDefaultResourceForm = () => ({
  resourceId: '',
  titleText: '',
  resourceType: '',
  pointId: '',
  linkUrl: '',
  descriptionText: '',
  fileObject: null
})

export const getAcceptTypes = (type) => acceptTypes[type] || ''

export const getUploadTipText = (resourceType) => {
  return resourceType === 'video'
    ? '支持 mp4, webm, ogg 格式，最大 500MB'
    : '支持 pdf, doc, docx, ppt, pptx 格式，最大 50MB'
}

export const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleDateString('zh-CN')
}

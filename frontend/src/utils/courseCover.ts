/**
 * 生成基于课程ID的确定性封面样式
 * @param {string|number} id - 课程ID
 * @param {string} name - 课程名称
 * @returns {Object} CSS样式对象
 */
export function generateCoverStyle(id, name) {
  const seed = (typeof id === 'number' ? id : 0) + (name ? name.length : 0)
  
  // 预定义渐变色盘 (鲜艳活泼)
  const gradients = [
    'linear-gradient(135deg, #FF9A9E 0%, #FECFEF 99%, #FECFEF 100%)', // 糖果粉
    'linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)',             // 清新蓝
    'linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%)',             // 极简灰
    'linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)',             // 薄荷绿
    'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',           // 海洋蓝
    'linear-gradient(to right, #fa709a 0%, #fee140 100%)',           // 活力橙红
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',             // 深邃紫
    'linear-gradient(to top, #a18cd1 0%, #fbc2eb 100%)',             // 梦幻紫
  ]

  // 预定义图案 (SVG Data URI)
  const patterns = [
    // 圆点
    `url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.2' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='3'/%3E%3Ccircle cx='13' cy='13' r='3'/%3E%3C/g%3E%3C/svg%3E")`,
    // 斜线
    `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.15' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40'/%3E%3C/g%3E%3C/svg%3E")`,
    // 菱形
    `url("data:image/svg+xml,%3Csvg width='36' height='36' viewBox='0 0 36 36' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%23ffffff' fill-opacity='0.15' d='M18 0l18 18-18 18L0 18z'/%3E%3C/svg%3E")`,
  ]

  const gradientIndex = seed % gradients.length
  const patternIndex = (seed * 7) % patterns.length

  return {
    background: `${patterns[patternIndex]}, ${gradients[gradientIndex]}`,
    backgroundBlendMode: 'overlay',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    overflow: 'hidden'
  }
}

/**
 * 获取随机几何装饰元素
 */
export function getGeometricDecorations(id) {
  const seed = typeof id === 'number' ? id : 1
  const shapes = ['circle', 'square', 'triangle']
  
  // 简单的伪随机
  const shape = shapes[seed % 3]
  const size = 50 + (seed * 13) % 100
  const top = (seed * 23) % 80
  const left = (seed * 37) % 80
  const rotate = (seed * 45) % 360
  
  return {
    position: 'absolute',
    width: `${size}px`,
    height: `${size}px`,
    top: `${top}%`,
    left: `${left}%`,
    transform: `rotate(${rotate}deg)`,
    background: 'rgba(255, 255, 255, 0.2)',
    borderRadius: shape === 'circle' ? '50%' : (shape === 'triangle' ? '0' : '8px'),
    zIndex: 0
  }
}

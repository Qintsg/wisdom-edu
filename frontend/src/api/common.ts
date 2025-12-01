import request from './index'

/**
 * Get dynamic menu based on user role
 */
export const getMenu = () => {
    return request.get('/api/common/menu')
}

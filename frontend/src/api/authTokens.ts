export function getAuthStorage(): Storage {
  if (localStorage.getItem('access_token') || localStorage.getItem('token')) {
    return localStorage
  }
  if (sessionStorage.getItem('access_token') || sessionStorage.getItem('token')) {
    return sessionStorage
  }
  return localStorage
}

export function getStoredAccessToken(): string | null {
  return (
    localStorage.getItem('access_token') ||
    localStorage.getItem('token') ||
    sessionStorage.getItem('access_token') ||
    sessionStorage.getItem('token')
  )
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token')
}

export function clearStoredAuthTokens(): void {
  const keys = ['access_token', 'refresh_token', 'token', 'userInfo', 'current_course']
  keys.forEach(key => {
    localStorage.removeItem(key)
    sessionStorage.removeItem(key)
  })
}

// Preserve native console methods so formatted logging never wraps itself recursively.
const ORIGINAL_CONSOLE: Record<string, (...args: any[]) => void> = {}

// Mark the runtime console once so repeated bootstraps do not stack multiple patches.
const PATCHED_FLAG = '__wisdomEduPatched'
const patchedConsole = console as Console & Record<string, any>

function formatTime(date = new Date()) {
  return date.toLocaleTimeString('zh-CN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function formatPrefix(level, scope = '前端') {
  return `${formatTime()} [${level}] ${scope} |`
}

function output(method, level, scope, args) {
  // Fall back to the saved native method first so global patching stays transparent to callers.
  const target = ORIGINAL_CONSOLE[method] || ORIGINAL_CONSOLE.log || console[method]
  target(formatPrefix(level, scope), ...args)
}

export function createLogger(scope = '前端') {
  // Keep feature logs scoped so shared infrastructure can still be filtered by module.
  return {
    debug: (...args) => output('debug', 'DEBUG', scope, args),
    info: (...args) => output('info', 'INFO', scope, args),
    warn: (...args) => output('warn', 'WARN', scope, args),
    error: (...args) => output('error', 'ERROR', scope, args)
  }
}

export function installConsoleFormat(defaultScope = '前端') {
  // Exit early when the app boot flow imports this helper more than once.
  if (patchedConsole[PATCHED_FLAG]) {
    return
  }

  // Snapshot every console entry point before overriding it with the formatted wrapper.
  ;['log', 'debug', 'info', 'warn', 'error'].forEach((method) => {
    ORIGINAL_CONSOLE[method] = console[method].bind(console)
  })

  console.log = (...args) => output('log', 'INFO', defaultScope, args)
  console.debug = (...args) => output('debug', 'DEBUG', defaultScope, args)
  console.info = (...args) => output('info', 'INFO', defaultScope, args)
  console.warn = (...args) => output('warn', 'WARN', defaultScope, args)
  console.error = (...args) => output('error', 'ERROR', defaultScope, args)
  patchedConsole[PATCHED_FLAG] = true
}

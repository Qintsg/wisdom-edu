import process from 'node:process'
import { chromium } from 'playwright'

import { parseArgs } from './browser-audit/args.mjs'
import { ensureBackendReady } from './browser-audit/api.mjs'
import { runAuditScenario } from './browser-audit/audit-scenario.mjs'
import {
  prepareDemoScenario,
  simulateDemoScenario
} from './browser-audit/demo-scenario.mjs'

const SCENARIO_HANDLERS = {
  'prepare-demo': prepareDemoScenario,
  'simulate-demo': simulateDemoScenario,
  audit: (_apiBaseUrl, browser, args) => runAuditScenario(browser, args)
}

async function main() {
  const args = parseArgs(process.argv)
  await ensureBackendReady(args.apiBaseUrl)
  const browser = await chromium.launch({ headless: !args.headed })

  try {
    const handler = SCENARIO_HANDLERS[args.scenario] || SCENARIO_HANDLERS.audit
    await handler(args.apiBaseUrl, browser, args)
  } finally {
    await browser.close()
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})

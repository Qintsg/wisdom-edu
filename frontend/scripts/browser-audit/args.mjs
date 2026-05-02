export function parseArgs(argv) {
  const args = {
    frontendUrl: 'http://edu.qintsg.xyz',
    apiBaseUrl: 'http://edu.qintsg.xyz',
    outputDir: '../output/playwright',
    headed: false,
    scenario: 'audit'
  }

  for (let index = 2; index < argv.length; index += 1) {
    const current = argv[index]
    if (current === '--frontend-url') args.frontendUrl = argv[index + 1]
    if (current === '--api-base-url') args.apiBaseUrl = argv[index + 1]
    if (current === '--output-dir') args.outputDir = argv[index + 1]
    if (current === '--scenario') args.scenario = argv[index + 1]
    if (current === '--headed') args.headed = true
  }
  return args
}

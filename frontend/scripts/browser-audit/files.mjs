import fs from 'node:fs/promises'
import path from 'node:path'

export async function ensureDir(target) {
  await fs.mkdir(target, { recursive: true })
}

export async function writeJson(filePath, data) {
  await ensureDir(path.dirname(filePath))
  await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf-8')
}

export async function readJson(filePath) {
  try {
    const raw = await fs.readFile(filePath, 'utf-8')
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function resolveDefenseDemoArchivePath(args) {
  return path.resolve(args.outputDir, '..', '答辩演示课程导入包.zip')
}

export async function ensureDefenseArchiveExists(args) {
  const archivePath = resolveDefenseDemoArchivePath(args)
  await fs.access(archivePath)
  return archivePath
}

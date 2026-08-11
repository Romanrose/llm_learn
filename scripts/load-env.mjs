import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const envPath = join(process.cwd(), '.env')

// Keep .env local and simple: existing shell variables always take precedence.
if (existsSync(envPath)) {
  for (const rawLine of readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const line = rawLine.trim()
    if (!line || line.startsWith('#')) continue
    const match = line.match(/^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/)
    if (!match) continue
    const [, key, rawValue] = match
    if (process.env[key] !== undefined) continue
    const value = rawValue.trim().replace(/^("|')([\s\S]*)\1$/, '$2')
    process.env[key] = value
  }
}

// Daily sync job for the Hurank API — Node.js 18+, no dependencies.
//
// Run it once a day (cron, a scheduled function, a queue worker). It reads only
// what changed since the previous run and applies it to your records.
//
//   HURANK_API_KEY=hk_test_... THRESHOLD=3.50 node sync.mjs
//
// Replace the three functions in "Your system" with calls to your CRM/HR tool.

import { readFile, writeFile } from 'node:fs/promises'

const BASE = process.env.HURANK_API_BASE ?? 'https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api'
const KEY = process.env.HURANK_API_KEY
const THRESHOLD = process.env.THRESHOLD ?? '3.50'
const CURSOR_FILE = process.env.CURSOR_FILE ?? '.hurank-cursor'

if (!KEY) throw new Error('Set HURANK_API_KEY (create one at https://www.hurank.com/developers/sandbox).')

// ---------------------------------------------------------------- Your system

/**
 * Store result + data. Replace the stored Hurank fields with exactly these:
 * a field missing from `data` was withdrawn and must be deleted (rule 1).
 */
async function saveOutcome(connectionId, result, data) {
  console.log(`save   ${connectionId}  ${result.padEnd(4)}  ${data.first_name} ${data.last_name}`, data)
}

/**
 * The connection ended (rejected, or disconnected by either side).
 * Rule 1: delete what you stored. Rule 2: show it as neutral, never as
 * "below threshold".
 */
async function clearPerson(connectionId) {
  console.log(`clear  ${connectionId}  (no_data: delete stored Hurank fields, show as neutral)`)
}

async function loadCursor() {
  try {
    return (await readFile(CURSOR_FILE, 'utf8')).trim() || null
  } catch {
    return null
  }
}

async function saveCursor(value) {
  if (value) await writeFile(CURSOR_FILE, value)
}

// ------------------------------------------------------------------- Hurank

async function hurank(path, init = {}) {
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(BASE + path, {
      ...init,
      headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json', ...init.headers },
    })
    if (res.status === 429 && attempt < 3) {
      const wait = Number(res.headers.get('Retry-After') ?? 10)
      await new Promise((r) => setTimeout(r, wait * 1000))
      continue
    }
    const body = await res.json()
    if (!res.ok) {
      const e = body.error ?? {}
      throw new Error(`${res.status} ${e.code}: ${e.message}`)
    }
    return body
  }
}

// --------------------------------------------------------------------- Sync

let since = await loadCursor()
let pages = 0

do {
  const query = new URLSearchParams({ threshold: THRESHOLD, limit: '500' })
  if (since) query.set('since', since)

  const page = await hurank(`/v1/status?${query}`)
  for (const s of page.data) {
    if (s.result === 'no_data') await clearPerson(s.connection_id)
    else await saveOutcome(s.connection_id, s.result, s.data)
  }

  since = page.next_since ?? since
  await saveCursor(since) // after each page: a crash halfway does not replay everything
  pages++
  if (!page.has_more) break
} while (true)

console.log(`done: ${pages} page(s), next run starts from ${since ?? 'the beginning'}`)

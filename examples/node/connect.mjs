// Request a connection — Node.js 18+, no dependencies. Works with test and live keys.
//
// Call this when someone gives you their Hurank profile code (a sign-up form,
// a candidate page, your back office). It requests the connection and tells you
// what to show to whoever typed the code.
//
//   HURANK_API_KEY=hk_live_... node connect.mjs AB12CD34
//
// With a test key use a test profile code (TESTPASS, TESTWAIT…). With a live
// key the person receives the request in the Hurank app, next to your
// organization's name, verified domain and the purpose of your key, and decides.

const BASE = process.env.HURANK_API_BASE ?? 'https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api'
const KEY = process.env.HURANK_API_KEY
const code = (process.argv[2] ?? '').trim().toUpperCase()

if (!KEY) throw new Error('Set HURANK_API_KEY (create one at https://www.hurank.com/developers/sandbox).')
if (!code) throw new Error('Pass the profile code: node connect.mjs AB12CD34')

// Ask only for what your process uses (rule 4). Never require the optional.
const fields = { required: ['profession'], optional: ['city'] }

const res = await fetch(`${BASE}/v1/connections`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${KEY}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ profile_code: code, fields }),
})
const body = await res.json()

switch (res.status) {
  case 201:
    // Store body.id next to your record: /v1/status rows carry it as connection_id.
    // body.status is "pending" until the person answers (live requests expire
    // after 7 days without an answer and become "no_access").
    console.log(`requested  ${body.id}  status=${body.status}`)
    console.log('Tell the person: "Open the Hurank app to accept the request."')
    break
  case 404:
    // A normal answer in live mode: the code was probably mistyped.
    console.log('No Hurank profile with this code. Ask the person to check it in the Hurank app (Share → profile code).')
    break
  case 409:
    // body.error.code is "connection_exists": you already have an open request
    // or connection with this person. Keep using the one you have.
    console.log(body.error.message)
    break
  case 429:
    console.log(`Rate limited: retry in ${res.headers.get('Retry-After')} s.`)
    break
  default:
    // 401/403: check the key, your organization's domain verification and the API terms.
    throw new Error(`${res.status} ${body.error?.code}: ${body.error?.message}`)
}

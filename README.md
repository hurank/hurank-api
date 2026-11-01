# Hurank API — developer kit

Build integrations between [Hurank](https://www.hurank.com) and the software
your organization already uses: a CRM, an HR platform, a staffing portal.

Hurank is a consensual reputation system — people rate each other from 1 to 5,
and only with the consent of the person being rated. With this API your system
can learn **whether a person who agreed to connect meets a rating threshold you
choose**. Nothing more.

> **Test and live.** Test keys (`hk_test_…`) work on a sandbox of fictional
> people. Live keys (`hk_live_…`) reach real people and are self-service: create
> your organization, verify your domain, accept the API terms. Same endpoints,
> same responses — a connector that works in test works in live.

## What is in this repository

| Path | What it is |
|---|---|
| [`openapi.yaml`](./openapi.yaml) | The OpenAPI 3.1 specification. Generate a client from it, or import it into Postman / Insomnia. |
| [`examples/curl.sh`](./examples/curl.sh) | Every endpoint, one `curl` at a time. Test keys only: it drives the sandbox. |
| [`examples/node/connect.mjs`](./examples/node/connect.mjs) | Request a connection from a profile code and handle every answer (including a mistyped code). Test and live. |
| [`examples/python/connect.py`](./examples/python/connect.py) | The same in Python 3.9+, standard library only. |
| [`examples/node/sync.mjs`](./examples/node/sync.mjs) | A daily sync job in Node.js 18+, no dependencies. Start your connector from here. |
| [`examples/python/sync.py`](./examples/python/sync.py) | The same job in Python 3.9+, standard library only. |
| [`CONNECTOR_RULES.md`](./CONNECTOR_RULES.md) | The rules every connector must follow. **Read them before you write code.** |

## The model in one minute

1. A person gives you their **profile code** (8 characters). There is no way to
   search for people: every connection starts from a code someone handed over.
2. You **request a connection** with that code, listing the fields you need.
   The person accepts or rejects in the Hurank app.
3. Once a day you **read what changed** and, for each person, receive `pass` or
   `fail` against your threshold — **never the score** — plus the fields they
   agreed to share.
4. The person can disconnect at any time. You then receive `no_data`, and you
   **delete** what you stored.

Why a yes/no and not the number? A number, once out, is copied forever — a
disconnection cannot take it back. A yes/no against a threshold you declared is
all you need to filter, and reveals nothing more.

## Quick start

```bash
# 1. Create a test key at https://www.hurank.com/developers/sandbox
export HURANK_API_KEY=hk_test_...
BASE=https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api

# 2. Check it
curl -s $BASE/v1/me -H "Authorization: Bearer $HURANK_API_KEY"

# 3. Connect to a test profile that accepts at once
curl -s $BASE/v1/connections \
  -H "Authorization: Bearer $HURANK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile_code":"TESTPASS","fields":{"required":["profession"],"optional":["city"]}}'

# 4. Read the outcome against your threshold
curl -s "$BASE/v1/status?threshold=3.50" -H "Authorization: Bearer $HURANK_API_KEY"
```

## Test profiles

In test mode only these codes exist. Real profile codes return `404`.

| Code | Behaviour | Simulated rating |
|---|---|---|
| `TESTPASS` | accepts at once, shares optional fields | 4.30 |
| `TESTFAIL` | accepts at once | 2.60 |
| `TESTEDGE` | accepts at once — exactly on a 3.00 threshold, which passes | 3.00 |
| `TESTNEWU` | accepts at once, has no votes yet — never passes | — |
| `TESTPART` | accepts required fields only, declines optional ones | 3.70 |
| `TESTWAIT` | stays `pending` until you accept or reject it via the sandbox endpoints | 3.90 |
| `TESTDENY` | rejects at once → `no_access` | 4.10 |

The rating is shown here because these people are fictional: it lets you test
both sides of a threshold. In live mode the API never returns it.

Use the `/v1/sandbox/...` endpoints, or the buttons in the
[sandbox](https://www.hurank.com/developers/sandbox), to simulate the person:
accept, reject, disconnect, change rating, change city.

## Going live

Live keys reach real people. Everything happens in the
[sandbox](https://www.hurank.com/developers/sandbox), and nobody approves it by hand:

1. **Create your organization** — its real name and its domain, one per Hurank
   account. People see both when you ask to connect (`Acme Staffing · acme.com ✓`).
2. **Verify the domain** with a DNS TXT record (below).
3. **Accept the [API terms](https://www.hurank.com/developers/terms)**, then create
   a live key.

Every live key carries a mandatory **purpose** — one key per system, one purpose
per key (“Driver selection for the summer season”). People read it next to your
name before they accept, so write it in their language. Each connection keeps the
purpose it was requested with.

### Verify your domain

Open the DNS panel of whoever manages your domain (registrar or hosting) and
**add** a record — don't edit the TXT records already there:

| Field | Value |
|---|---|
| Type | `TXT` |
| Name / Host | `@` — the domain itself (some panels want it empty, or the domain in full) |
| Value | `hurank-verification=<your token>` — copy it from the sandbox |
| TTL | default |

Use your registrable domain (`example.com`), not a subdomain or an address on a
shared platform (`something.vercel.app`). Propagation usually takes minutes,
sometimes up to 24–48 hours:

```bash
dig TXT example.com +short
# Windows: nslookup -type=TXT example.com
```

Then press **Verify domain** in the sandbox. **Leave the record in place**: it is
checked again every 30 days, and live keys answer `403 domain_not_verified` if it
disappears. Changing the domain resets the verification and issues a new token.

Common problems: the record was put on a subdomain (`www`), the value carries
extra quotes or a partial token, or it was added at a DNS provider your
nameservers don't point to.

### What changes in live mode

- A request stays `pending` until the person answers in the Hurank app. If nobody
  answers it **expires after 7 days** and becomes `no_access`; you may ask again.
- `404 profile_not_found` is a normal answer: the person may have mistyped their
  code. Ask them to check it and try again.
- `/v1/sandbox/...` endpoints answer `403 sandbox_only`.

## Documentation

Full reference, errors and limits: **https://www.hurank.com/developers/docs**

## License

The specification and the examples are released under the [MIT license](./LICENSE).
Writing a connector is open to anyone; reading real data requires a live key, a verified
domain and the [API terms](https://www.hurank.com/developers/terms).

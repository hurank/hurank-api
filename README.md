# Hurank API — developer kit

Build integrations between [Hurank](https://www.hurank.com) and the software
your organization already uses: a CRM, an HR platform, a staffing portal.

Hurank is a consensual reputation system — people rate each other from 1 to 5,
and only with the consent of the person being rated. With this API your system
can learn **whether a person who agreed to connect meets a rating threshold you
choose**. Nothing more.

> **Status: test mode.** Test keys (`hk_test_…`) work today on a sandbox of
> fictional people. Live keys will be issued under contract.

## What is in this repository

| Path | What it is |
|---|---|
| [`openapi.yaml`](./openapi.yaml) | The OpenAPI 3.1 specification. Generate a client from it, or import it into Postman / Insomnia. |
| [`examples/curl.sh`](./examples/curl.sh) | Every endpoint, one `curl` at a time. |
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

## Documentation

Full reference, errors and limits: **https://www.hurank.com/developers/docs**

## License

The specification and the examples are released under the [MIT license](./LICENSE).
Writing a connector is open to anyone; reading data requires a key issued by Hurank.

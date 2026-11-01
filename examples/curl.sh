#!/usr/bin/env sh
# Every Hurank API endpoint, one curl at a time.
# Usage: HURANK_API_KEY=hk_test_... sh curl.sh
# TEST KEYS ONLY: it drives the sandbox. With a live key the /v1/sandbox
# endpoints answer 403 sandbox_only, and the person answers in the Hurank app.
# Needs: curl. jq is optional, only to pretty-print and pick ids.

set -e
: "${HURANK_API_KEY:?Set HURANK_API_KEY to a test key from https://www.hurank.com/developers/sandbox}"
BASE="${HURANK_API_BASE:-https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api}"
AUTH="Authorization: Bearer $HURANK_API_KEY"
JSON="Content-Type: application/json"

echo "--- Your key"
curl -s "$BASE/v1/me" -H "$AUTH"

echo "--- Start from a clean sandbox"
curl -s -X POST "$BASE/v1/sandbox/reset" -H "$AUTH"

echo "--- Connect to a person who accepts at once"
curl -s "$BASE/v1/connections" -H "$AUTH" -H "$JSON" \
  -d '{"profile_code":"TESTPASS","fields":{"required":["profession"],"optional":["city"]}}'

echo "--- Connect to a person who has not answered yet"
WAIT=$(curl -s "$BASE/v1/connections" -H "$AUTH" -H "$JSON" -d '{"profile_code":"TESTWAIT"}')
echo "$WAIT"
WAIT_ID=$(echo "$WAIT" | sed -n 's/.*"id": "\([^"]*\)".*/\1/p' | head -n 1)

echo "--- Simulate: the person accepts"
curl -s -X POST "$BASE/v1/sandbox/connections/$WAIT_ID/accept" -H "$AUTH"

echo "--- Outcomes against a 3.50 threshold"
curl -s "$BASE/v1/status?threshold=3.50" -H "$AUTH"

echo "--- Simulate: the rating drops below your threshold"
curl -s -X POST "$BASE/v1/sandbox/connections/$WAIT_ID/rating" -H "$AUTH" -H "$JSON" -d '{"rating": 3.10}'

echo "--- Simulate: the person disconnects"
curl -s -X POST "$BASE/v1/sandbox/connections/$WAIT_ID/revoke" -H "$AUTH"

echo "--- The same connection, re-read in a batch: no_data, delete what you stored"
curl -s "$BASE/v1/status/batch" -H "$AUTH" -H "$JSON" \
  -d "{\"threshold\": 3.5, \"connection_ids\": [\"$WAIT_ID\"]}"

echo "--- All your connections"
curl -s "$BASE/v1/connections" -H "$AUTH"

"""Request a connection — Python 3.9+, standard library only. Works with test and live keys.

Call this when someone gives you their Hurank profile code (a sign-up form, a
candidate page, your back office). It requests the connection and tells you
what to show to whoever typed the code.

    HURANK_API_KEY=hk_live_... python connect.py AB12CD34

With a test key use a test profile code (TESTPASS, TESTWAIT...). With a live
key the person receives the request in the Hurank app, next to your
organization's name, verified domain and the purpose of your key, and decides.
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("HURANK_API_BASE", "https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api")
KEY = os.environ.get("HURANK_API_KEY")

if not KEY:
    raise SystemExit("Set HURANK_API_KEY (create one at https://www.hurank.com/developers/sandbox).")
if len(sys.argv) < 2:
    raise SystemExit("Pass the profile code: python connect.py AB12CD34")

code = sys.argv[1].strip().upper()

# Ask only for what your process uses (rule 4). Never require the optional.
fields = {"required": ["profession"], "optional": ["city"]}

request = urllib.request.Request(
    f"{BASE}/v1/connections",
    data=json.dumps({"profile_code": code, "fields": fields}).encode(),
    headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(request) as res:
        status, headers, body = res.status, res.headers, json.load(res)
except urllib.error.HTTPError as err:
    status, headers, body = err.code, err.headers, json.load(err)

if status == 201:
    # Store body["id"] next to your record: /v1/status rows carry it as connection_id.
    # body["status"] is "pending" until the person answers (live requests expire
    # after 7 days without an answer and become "no_access").
    print(f"requested  {body['id']}  status={body['status']}")
    print('Tell the person: "Open the Hurank app to accept the request."')
elif status == 404:
    # A normal answer in live mode: the code was probably mistyped.
    print("No Hurank profile with this code. Ask the person to check it in the Hurank app (Share → profile code).")
elif status == 409:
    # body["error"]["code"] is "connection_exists": you already have an open
    # request or connection with this person. Keep using the one you have.
    print(body["error"]["message"])
elif status == 429:
    print(f"Rate limited: retry in {headers.get('Retry-After')} s.")
else:
    # 401/403: check the key, your organization's domain verification and the API terms.
    error = body.get("error", {})
    raise SystemExit(f"{status} {error.get('code')}: {error.get('message')}")

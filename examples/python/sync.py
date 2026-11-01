"""Daily sync job for the Hurank API — Python 3.9+, standard library only.

Run it once a day (cron, a scheduled task, a worker). It reads only what
changed since the previous run and applies it to your records.

    HURANK_API_KEY=hk_test_... THRESHOLD=3.50 python sync.py

Works unchanged with a live key (hk_live_...): same endpoint, same rows.

Replace the functions in "Your system" with calls to your CRM/HR tool.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("HURANK_API_BASE", "https://oxevfjnevbitperkwcoj.supabase.co/functions/v1/hurank-api")
KEY = os.environ.get("HURANK_API_KEY")
THRESHOLD = os.environ.get("THRESHOLD", "3.50")
CURSOR_FILE = os.environ.get("CURSOR_FILE", ".hurank-cursor")

if not KEY:
    raise SystemExit("Set HURANK_API_KEY (create one at https://www.hurank.com/developers/sandbox).")


# ------------------------------------------------------------- Your system

def save_outcome(connection_id, result, data):
    """Store result + data.

    Replace the stored Hurank fields with exactly these: a field missing from
    `data` was withdrawn and must be deleted (rule 1).
    """
    print(f"save   {connection_id}  {result:<4}  {data['first_name']} {data['last_name']}", data)


def clear_person(connection_id):
    """The connection ended (rejected, or disconnected by either side).

    Rule 1: delete what you stored. Rule 2: show it as neutral, never as
    "below threshold".
    """
    print(f"clear  {connection_id}  (no_data: delete stored Hurank fields, show as neutral)")


def load_cursor():
    try:
        with open(CURSOR_FILE, encoding="utf-8") as f:
            return f.read().strip() or None
    except FileNotFoundError:
        return None


def save_cursor(value):
    if value:
        with open(CURSOR_FILE, "w", encoding="utf-8") as f:
            f.write(value)


# ------------------------------------------------------------------ Hurank

def hurank(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(4):
        req = urllib.request.Request(
            BASE + path,
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(int(e.headers.get("Retry-After", "10")))
                continue
            err = json.load(e).get("error", {})
            raise RuntimeError(f"{e.code} {err.get('code')}: {err.get('message')}") from None


# -------------------------------------------------------------------- Sync

def main():
    since = load_cursor()
    pages = 0
    while True:
        query = {"threshold": THRESHOLD, "limit": "500"}
        if since:
            query["since"] = since
        page = hurank("/v1/status?" + urllib.parse.urlencode(query))

        for s in page["data"]:
            if s["result"] == "no_data":
                clear_person(s["connection_id"])
            else:
                save_outcome(s["connection_id"], s["result"], s["data"])

        since = page.get("next_since") or since
        save_cursor(since)  # after each page: a crash halfway does not replay everything
        pages += 1
        if not page["has_more"]:
            break

    print(f"done: {pages} page(s), next run starts from {since or 'the beginning'}")


if __name__ == "__main__":
    main()

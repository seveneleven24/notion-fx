import os, requests
from datetime import datetime, timezone

TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
H = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

r = requests.post(f"https://api.notion.com/v1/databases/{DB_ID}/query", headers=H)
if not r.ok:
    raise SystemExit(f"讀取資料庫失敗：{r.status_code} {r.text}")

for p in r.json()["results"]:
    title = p["properties"]["幣別"]["title"]
    if not title:
        continue
    cur = title[0]["plain_text"].strip().upper()

    resp = requests.get(f"https://open.er-api.com/v6/latest/{cur}")
    rate = resp.json().get("rates", {}).get("TWD")
    if rate is None:
        print(f"{cur}：抓不到匯率，略過")
        continue

    u = requests.patch(
        f"https://api.notion.com/v1/pages/{p['id']}",
        headers=H,
        json={"properties": {
            "目前匯率": {"number": rate},
            "更新日期": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        }},
    )
    if not u.ok:
        raise SystemExit(f"{cur} 寫入失敗：{u.status_code} {u.text}")
    print(f"{cur} → {rate}")

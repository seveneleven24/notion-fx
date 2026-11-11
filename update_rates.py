import os, requests
from datetime import datetime, timezone

TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
H = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

pages = requests.post(
    f"https://api.notion.com/v1/databases/{DB_ID}/query", headers=H
).json()["results"]

for p in pages:
    cur = p["properties"]["幣別"]["title"][0]["plain_text"].strip()
    rate = requests.get(f"https://open.er-api.com/v6/latest/{cur}").json()["rates"]["TWD"]
    requests.patch(
        f"https://api.notion.com/v1/pages/{p['id']}",
        headers=H,
        json={"properties": {
            "目前匯率": {"number": rate},
            "更新日期": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        }},
    )

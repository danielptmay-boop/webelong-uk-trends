#!/usr/bin/env python3
"""Collect UK TikTok trend discoveries; fail closed on missing or invalid data."""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ACTOR = "parsebird~tiktok-trends-scraper"
BASE = f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "uk-tiktok-trends.json"
MAX_ITEMS = 15

def collect(token, mode):
    url = f"{BASE}?maxItems={MAX_ITEMS}&maxTotalChargeUsd=0.08&format=json&limit={MAX_ITEMS}"
    body = json.dumps({
        "trendType": mode,
        "countryCode": "GB",
        "period": 7,
        "maxResults": MAX_ITEMS
    }).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(request, timeout=295) as response:
        rows = json.load(response)
    if not isinstance(rows, list):
        raise ValueError(f"Unexpected {mode} data")
    return [r for r in rows if isinstance(r, dict) and str(r.get("countryCode", "GB")).upper() == "GB"]

def hashtags(rows):
    rows.sort(key=lambda r: (r.get("rankingScope") != "country_period", int(r.get("rank") or 9999)))
    result, seen = [], set()
    for r in rows:
        name = str(r.get("name", "")).strip().lstrip("#")
        if not re.fullmatch(r"[A-Za-z0-9_]{2,80}", name) or name.lower() in seen:
            continue
        seen.add(name.lower())
        result.append("#" + name)
        if len(result) == 6:
            break
    return result

def sounds(rows):
    rows.sort(key=lambda r: -(float(r.get("videosInSample") or 0)))
    result, seen = [], set()
    for r in rows:
        if r.get("isOriginal") is True:
            continue
        title = str(r.get("name") or "").strip()[:150]
        artist = str(r.get("soundAuthor") or "TikTok sound").strip()[:120]
        if not title or title.lower() == "original sound" or (title.lower(), artist.lower()) in seen:
            continue
        seen.add((title.lower(), artist.lower()))
        link = str(r.get("soundPlayUrl") or r.get("linkedVideoUrl") or "")
        if not link.startswith(("https://www.tiktok.com/", "https://tiktok.com/")):
            link = "https://www.tiktok.com/search?q=" + urllib.parse.quote(title + " " + artist)
        result.append({"title": title, "artist": artist, "tiktokUrl": link})
        if len(result) == 6:
            break
    return result

def main():
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing APIFY_TOKEN; old feed remains unchanged")
    tags = hashtags(collect(token, "hashtag"))
    tracks = sounds(collect(token, "sound"))
    if not tags or not tracks:
        raise RuntimeError("Incomplete UK trends; old feed remains unchanged")
    date = datetime.now(ZoneInfo("Europe/London")).date().isoformat()
    data = {
        "region": "GB",
        "chartDate": date,
        "collectedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sourceName": "UK TikTok hashtags and sampled Explore sounds via Apify",
        "sourceUrl": "https://ads.tiktok.com/creative/creativeCenter/trends?region=GB",
        "songsRankingType": "sample",
        "songs": tracks,
        "hashtags": tags
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Collected {len(tags)} hashtags and {len(tracks)} sampled sounds dated {date}")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        sys.exit(1)

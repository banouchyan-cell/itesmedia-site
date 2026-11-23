"""Թարմացնում է նախագծերի վիդեոները YouTube-ից։

Գործարկել կայքի թղթապանակից.
    py -3.12 tools/update_videos.py

Կարդում է content.js-ի projects ցանկի փլեյլիստները, YouTube-ի RSS-ից
վերցնում յուրաքանչյուրի վերջին 6 թողարկումները և գրում videos.js-ում։
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PER_PROJECT = 6
ROOT = Path(__file__).resolve().parent.parent
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def playlist_ids():
    src = (ROOT / "content.js").read_text(encoding="utf-8")
    block = src[src.index("projects:"):src.index("]", src.index("projects:"))]
    return re.findall(r'id:\s*"([\w-]+)"', block)


def fetch(pid):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={pid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    items = []
    for e in root.findall("a:entry", NS):
        items.append({
            "id": e.find("yt:videoId", NS).text,
            "title": e.find("a:title", NS).text,
            "date": e.find("a:published", NS).text[:10],
        })
    items.sort(key=lambda v: v["date"], reverse=True)
    return items[:PER_PROJECT]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    out = {}
    for pid in playlist_ids():
        try:
            out[pid] = fetch(pid)
            print(f"{pid}: {len(out[pid])} վիդեո")
        except Exception as ex:  # keep going if one playlist fails
            print(f"{pid}: ՍԽԱԼ {ex}", file=sys.stderr)
            out[pid] = []
    js = "// Ավտոմատ ստեղծված է tools/update_videos.py-ով, ձեռքով մի փոխիր։\nwindow.VIDEOS = " + \
         json.dumps(out, ensure_ascii=False, indent=1) + ";\n"
    (ROOT / "videos.js").write_text(js, encoding="utf-8")
    print("videos.js թարմացված է")


if __name__ == "__main__":
    main()

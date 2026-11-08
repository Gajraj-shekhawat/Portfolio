"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver...) that the site changed.

Bing's index also feeds ChatGPT search, Microsoft Copilot and DuckDuckGo, so this
gets updates picked up quickly. Google does not use IndexNow; it reads the sitemap
submitted in Search Console instead.
"""
import json
import pathlib
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

HOST = "gajrajshekhawat.com"
ROOT = pathlib.Path(__file__).resolve().parents[2]

key_files = [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
if not key_files:
    sys.exit("IndexNow key file not found")
key = key_files[0].stem

ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [e.text for e in ET.parse(ROOT / "sitemap.xml").getroot().findall("s:url/s:loc", ns)]
urls += [f"https://{HOST}/llms.txt"]

payload = json.dumps({
    "host": HOST,
    "key": key,
    "keyLocation": f"https://{HOST}/{key}.txt",
    "urlList": urls,
}).encode()

req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"IndexNow: HTTP {resp.status} for {len(urls)} URLs")
except urllib.error.HTTPError as e:
    # 200/202 = accepted. 403 = key not yet reachable, 422 = URL/host mismatch, 429 = too many requests.
    print(f"IndexNow: HTTP {e.code} {e.reason}")
    if e.code not in (202, 429):
        sys.exit(1)

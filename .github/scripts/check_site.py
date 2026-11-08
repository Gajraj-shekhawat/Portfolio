"""Pre-deploy checks for the portfolio. Fails the workflow if something is broken.

Checks: JSON-LD parses and has the expected types, sitemap is valid XML with
absolute https URLs, every local href/src in the HTML points to a real file,
llms.txt contains markdown links, and the IndexNow key file is present.
"""
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
errors = []

html = (ROOT / "index.html").read_text(encoding="utf-8")

# 1. Structured data
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
if not blocks:
    errors.append("No JSON-LD block found in index.html")
for b in blocks:
    try:
        data = json.loads(b)
        types = {n.get("@type") for n in data.get("@graph", [])}
        for t in ("Person", "ProfilePage", "FAQPage"):
            if t not in types:
                errors.append(f"JSON-LD is missing {t}")
    except json.JSONDecodeError as e:
        errors.append(f"JSON-LD does not parse: {e}")

# 2. Basic SEO tags
for needle in ('<link rel="canonical"', 'name="description"', 'property="og:image"', "<title>"):
    if needle not in html:
        errors.append(f"index.html is missing {needle}")

# 3. Sitemap
try:
    tree = ET.parse(ROOT / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [e.text for e in tree.getroot().findall("s:url/s:loc", ns)]
    if not locs:
        errors.append("sitemap.xml has no <loc> entries")
    for loc in locs:
        if not loc.startswith("https://"):
            errors.append(f"sitemap URL is not absolute https: {loc}")
except ET.ParseError as e:
    errors.append(f"sitemap.xml is not valid XML: {e}")

# 4. Local links and assets exist
for page in [ROOT / "404.html", *ROOT.rglob("index.html")]:
    text = page.read_text(encoding="utf-8")
    for ref in re.findall(r'(?:href|src|srcset)="([^"]+)"', text):
        if re.match(r"^(https?:|mailto:|tel:|#|data:)", ref):
            continue
        path = ROOT / ref.split("#")[0].split("?")[0].lstrip("/")
        if not path.exists():
            errors.append(f"{page.name}: missing file for {ref}")

# 5. llms.txt
llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
if not llms.startswith("# ") or not re.search(r"\[[^\]]+\]\(https://", llms):
    errors.append("llms.txt must start with '# ' and contain markdown links")

# 6. IndexNow key file
if not [p for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]:
    errors.append("IndexNow key file (<32 hex>.txt) not found at repo root")

if errors:
    print("Site checks FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("All site checks passed.")

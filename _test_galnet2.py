import httpx, re, json

h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://community.elitedangerous.com"

# 1. Get Galnet page and extract article UIDs
print("=== GALNET PAGE ===")
r = httpx.get(f"{BASE}/galnet", headers=h, timeout=15)
uids = re.findall(r'href="/galnet/uid/([a-f0-9]+)"', r.text)
print(f"Found {len(uids)} article UIDs")
for uid in uids[:3]:
    print(f"  /galnet/uid/{uid}")

# 2. Try RSS
print("\n=== RSS FEED ===")
r2 = httpx.get(f"{BASE}/galnet.rss", headers=h, timeout=15)
print(f"Status: {r2.status_code}, len: {len(r2.content)}, type: {r2.headers.get('content-type','')[:40]}")
if r2.status_code == 200:
    print(f"<item> count: {r2.text.count('<item>')}")
    print(f"First 600 chars:\n{r2.text[:600]}")

# 3. Try JSON format on main page
print("\n=== JSON MAIN ===")
r3 = httpx.get(f"{BASE}/galnet?_format=json", headers=h, timeout=15)
print(f"Status: {r3.status_code}, type: {r3.headers.get('content-type','')[:40]}")
if r3.status_code == 200 and len(r3.content) > 100:
    d = r3.json()
    if isinstance(d, dict):
        print(f"Keys: {list(d.keys())}")
        for k, v in d.items():
            vstr = str(v)
            if len(vstr) > 200:
                vstr = vstr[:200] + "..."
            print(f"  {k}: {vstr}")
    elif isinstance(d, list):
        print(f"List with {len(d)} items")
        if d:
            print(f"First item: {json.dumps(d[0], ensure_ascii=False)[:500]}")

# 4. Try JSON on single article
if uids:
    print(f"\n=== JSON ARTICLE (/galnet/uid/{uids[0]}) ===")
    r4 = httpx.get(f"{BASE}/galnet/uid/{uids[0]}?_format=json", headers=h, timeout=15)
    print(f"Status: {r4.status_code}, type: {r4.headers.get('content-type','')[:40]}")
    if r4.status_code == 200 and len(r4.content) > 100:
        d = r4.json()
        if isinstance(d, dict):
            print(f"Keys: {list(d.keys())}")
            for k, v in d.items():
                vstr = str(v)
                if len(vstr) > 200:
                    vstr = vstr[:200] + "..."
                print(f"  {k}: {vstr}")

# 5. Try /api/galnet path
print("\n=== API PATH ===")
r5 = httpx.get(f"{BASE}/api/galnet?_format=json", headers=h, timeout=15)
print(f"Status: {r5.status_code}, type: {r5.headers.get('content-type','')[:40]}")

print("\n=== DONE ===")
import os; os.remove(__file__)

"""Publish scheduled resource articles.

Files in scheduled/ are named YYYY-MM-DD__slug.html. On or after that date
(US Eastern), the file moves to resources/slug.html, a rewrite is added to
vercel.json and a URL is added to sitemap.xml.
"""
import json, os, re, datetime, zoneinfo

today = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date()
published = []
names = sorted(os.listdir("scheduled")) if os.path.isdir("scheduled") else []
for name in names:
    m = re.match(r"(\d{4}-\d{2}-\d{2})__([a-z0-9-]+)\.html$", name)
    if not m:
        continue
    if datetime.date.fromisoformat(m.group(1)) > today:
        continue
    slug = m.group(2)
    os.replace(os.path.join("scheduled", name), os.path.join("resources", slug + ".html"))
    published.append(slug)

if published:
    v = json.load(open("vercel.json"))
    have = {r["source"] for r in v["rewrites"]}
    for slug in published:
        src = "/resources/" + slug
        if src not in have:
            v["rewrites"].append({"source": src, "destination": src + ".html"})
    open("vercel.json", "w").write(json.dumps(v, indent=2) + "\n")
    sm = open("sitemap.xml").read()
    add = "".join(
        f"  <url><loc>https://www.checkoffbooks.com/resources/{s}</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>\n"
        for s in published if f"/resources/{s}<" not in sm)
    open("sitemap.xml", "w").write(sm.replace("</urlset>", add + "</urlset>"))

print("published:", published)
with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as f:
    f.write(f"count={len(published)}\n")

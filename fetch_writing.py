#!/usr/bin/env python3
"""Snapshot the latest Substack posts into data/writing.json. Run before build.py to refresh the Writing page."""
import re, html, json, urllib.request, email.utils, datetime
FEED = "https://jpenberth.substack.com/feed"
xml = urllib.request.urlopen(urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (compatible; site-build)"}), timeout=40).read().decode("utf8", "ignore")
posts = []
for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
    g = lambda t: html.unescape((re.search(rf"<{t}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{t}>", it, re.S) or [0, ""])[1].strip())
    d = email.utils.parsedate_to_datetime(g("pubDate")).date().isoformat()
    posts.append(dict(title=g("title"), url=g("link"), date=d, blurb=re.sub(r"\s+", " ", g("description"))))
json.dump(posts[:12], open("data/writing.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print("saved", len(posts[:12]), "posts")

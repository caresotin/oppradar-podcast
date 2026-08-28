#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OppRadar Signals 播客 RSS 生成器 (2026-08-27)
功能: 扫描 audio/ 目录的 mp3 → 生成标准播客 RSS feed.xml
用法: python gen_rss.py   (音频放 audio/ 目录, 命名 EP1_xxx.mp3, EP2_xxx.mp3 ...)
"""
import os, re, datetime, subprocess

BASE = r"D:\oppradar-podcast"
AUDIO_DIR = os.path.join(BASE, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

BASE_URL = "https://caresotin.github.io/oppradar-podcast/"

# 节目信息
SHOW = {
    "title": "OppRadar Signals",
    "description": "AI opportunities for one-person companies — from a 20-year export veteran, in 3 minutes. Real signals, no noise. Full data at oppradar.dev",
    "link": "https://oppradar.dev",
    "language": "en",
    "category": "Technology",
    "subcategory": "Tech News",
    "owner_name": "OppRadar Signals",
    "owner_email": "caresotin@gmail.com",
    "image": BASE_URL + "cover.jpg",
    "author": "OppRadar Signals",
}

def parse_ep(title):
    """从文件名解析期数和标题: EP1_codex_agency_agents → (1, 'Codex Agency Agents')"""
    m = re.match(r"EP(\d+)_(.+)", title)
    if m:
        num = int(m.group(1))
        name = m.group(2).replace("_", " ").title()
        return num, name
    return None, title

def fmt_date(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

def get_duration(path):
    """用 ffprobe 读音频真实时长, 格式化为 HH:MM:SS"""
    try:
        import shutil
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return "00:01:30"
        r = subprocess.run([ffprobe, "-v", "quiet", "-show_entries", "format=duration",
                            "-of", "csv=p=0", path], capture_output=True, text=True, timeout=15)
        secs = float(r.stdout.strip())
        h = int(secs // 3600); m = int(secs % 3600 // 60); s = int(secs % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
    except Exception:
        return "00:01:30"

def gen_rss():
    items = []
    files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
    for f in files:
        path = os.path.join(AUDIO_DIR, f)
        size = os.path.getsize(path)
        num, name = parse_ep(f.replace(".mp3", ""))  # 去掉后缀再解析
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc)
        ep_title = f"EP{num}: {name}" if num else name
        items.append(f"""    <item>
      <title>{ep_title}</title>
      <description>{name} — curated and verified by OppRadar Signals. Find opportunities worth your time at https://oppradar.dev</description>
      <pubDate>{fmt_date(mtime)}</pubDate>
      <enclosure url="{BASE_URL}audio/{f}" length="{size}" type="audio/mpeg"/>
      <guid isPermaLink="true">{BASE_URL}audio/{f}</guid>
      <itunes:title>{ep_title}</itunes:title>
      <itunes:summary>{name} — curated and verified. Full data at oppradar.dev</itunes:summary>
      <itunes:duration>{get_duration(path)}</itunes:duration>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW['title']}</title>
    <link>{SHOW['link']}</link>
    <description>{SHOW['description']}</description>
    <language>{SHOW['language']}</language>
    <category>{SHOW['category']}</category>
    <itunes:author>{SHOW['author']}</itunes:author>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{SHOW['image']}"/>
    <itunes:category text="{SHOW['category']}">
      <itunes:category text="{SHOW['subcategory']}"/>
    </itunes:category>
    <itunes:owner>
      <itunes:name>{SHOW['owner_name']}</itunes:name>
      <itunes:email>{SHOW['owner_email']}</itunes:email>
    </itunes:owner>
    <atom:link href="{BASE_URL}feed.xml" rel="self" type="application/rss+xml"/>
    {chr(10).join(items)}
  </channel>
</rss>
"""
    with open(os.path.join(BASE, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"✅ RSS 生成: {len(files)} 期音频, feed.xml 就绪")

if __name__ == "__main__":
    gen_rss()

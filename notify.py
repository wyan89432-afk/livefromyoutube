#!/usr/bin/env python3
import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

CHANNEL_ID = "UC6eaAhHjGRrHTiM9yznbBpw"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "@happydayfor"
STATE_FILE = "last_video.txt"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
NS = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def latest_video():
    req = urllib.request.Request(RSS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    entry = root.find("atom:entry", NS)
    if entry is None:
        return None
    video_id = entry.findtext("yt:videoId", default="", namespaces=NS)
    link_el = entry.find("atom:link", NS)
    link = link_el.attrib.get("href", "") if link_el is not None else f"https://youtu.be/{video_id}"
    return video_id, link


def send_link(link):
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN is missing", file=sys.stderr)
        sys.exit(1)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": link, "disable_web_page_preview": "false"}).encode()
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
    if '"ok":true' not in body:
        print(body, file=sys.stderr)
        sys.exit(1)


def main():
    item = latest_video()
    if not item:
        print("No video found")
        return
    video_id, link = item
    old = ""
    if os.path.exists(STATE_FILE):
        old = open(STATE_FILE, encoding="utf-8").read().strip()
    if video_id == old:
        print("No new video")
        return
    send_link(link)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(video_id)
    print("Sent:", link)


if __name__ == "__main__":
    main()

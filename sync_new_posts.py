#!/usr/bin/env python3
"""
Fetches the 12 most recent Instagram posts (no auth required) and creates
Jekyll posts + downloads images for any that don't exist locally yet.

Designed to run daily via GitHub Actions.
"""

import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


MAX_RETRIES = 3
INSTAGRAM_URL = "https://i.instagram.com/api/v1/users/web_profile_info/?username=zij.was.eens"
HEADERS = {
    "x-ig-app-id": "936619743392459",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
}

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"
POSTS_DIR = ROOT / "_posts"


def fetch_recent_posts():
    """Fetch the 12 most recent posts from Instagram (no auth needed)."""
    for attempt in range(MAX_RETRIES):
        try:
            req = Request(INSTAGRAM_URL, headers=HEADERS)
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
            user = data["data"]["user"]
            edges = user["edge_owner_to_timeline_media"]["edges"]
            return [e["node"] for e in edges]
        except HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                wait = 30 * (attempt + 1)
                print(f"Rate limited (429), retrying in {wait}s... (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait)
            else:
                raise
    return []


def get_existing_codes():
    """Get set of Instagram shortcodes already present locally."""
    codes = set()
    for img in os.listdir(IMAGES_DIR):
        code = img.rsplit("_", 1)[0]
        codes.add(code)
    return codes


def slugify(text):
    """Create a URL-friendly slug from text."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:50].rstrip("-")


def extract_title(caption_text):
    """Extract person name or event title from caption."""
    if not caption_text:
        return "zijwaseens"

    patterns = [
        r"Vandaag \d+ jaar geleden is (.+?) (geboren|overleden|onthoofd|ge[eë]xecuteerd|verbrand|ontspoorde)",
        r"Vandaag \d+ jaar geleden is (.+?) in ",
        r"^(.+?) is geboren",
        r"^(.+?) is in \d",
    ]
    for pattern in patterns:
        m = re.search(pattern, caption_text, re.MULTILINE)
        if m:
            name = m.group(1).strip()
            name = re.sub(r"\s*\(.*?\)\s*", " ", name).strip()
            if len(name) < 60 and re.match(r"^[A-ZÀ-Ÿ]", name):
                return name

    first_line = caption_text.split("\n")[0][:60]
    return first_line if first_line else "zijwaseens"


def download_image(url, filepath):
    """Download image from URL using stdlib only."""
    try:
        req = Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
        with urlopen(req, timeout=30) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def create_post(node):
    """Create a Jekyll post and download images for an Instagram post node."""
    code = node.get("shortcode", node.get("code", ""))
    taken_at = node.get("taken_at_timestamp", node.get("taken_at", 0))
    dt = datetime.fromtimestamp(taken_at) if taken_at else datetime.now()

    caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
    if caption_edges:
        caption_text = caption_edges[0].get("node", {}).get("text", "")
    else:
        caption_text = ""

    title = extract_title(caption_text)
    slug = slugify(title) or "zijwaseens"

    # Collect image URLs
    image_urls = []
    sidecar = node.get("edge_sidecar_to_children", {}).get("edges", [])
    if sidecar:
        for child in sidecar:
            url = child.get("node", {}).get("display_url", "")
            if url:
                image_urls.append(url)
    else:
        url = node.get("display_url", "")
        if url:
            image_urls.append(url)

    # Download images
    downloaded = []
    for i, url in enumerate(image_urls):
        ext = ".webp" if "webp" in url else ".jpg"
        filename = f"{code}_{i}{ext}"
        filepath = IMAGES_DIR / filename
        if download_image(url, filepath):
            downloaded.append(filename)
        time.sleep(0.3)

    header_image = f"/images/{downloaded[0]}" if downloaded else ""

    # Build markdown
    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    date_prefix = dt.strftime("%Y-%m-%d")

    md = f"""---
layout: post
title: "{title}"
date: {date_str}
header_image: {header_image}
---

{caption_text}
"""
    for img in downloaded:
        md += f"\n![Image](/images/{img})"
    md += "\n"

    post_filename = f"{date_prefix}-{slug}.md"
    post_path = POSTS_DIR / post_filename
    if post_path.exists():
        post_filename = f"{date_prefix}-{slug}-{code[-4:]}.md"
        post_path = POSTS_DIR / post_filename

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(md)

    return post_filename, len(downloaded)


def main():
    print("Fetching recent posts from Instagram...")
    try:
        posts = fetch_recent_posts()
    except HTTPError as e:
        print(f"Instagram API error: {e.code} {e.reason}")
        sys.exit(1)
    print(f"Got {len(posts)} posts")

    existing = get_existing_codes()
    print(f"Existing local shortcodes: {len(existing)}")

    new_count = 0
    for node in posts:
        code = node.get("shortcode", "")
        if code in existing:
            continue

        filename, img_count = create_post(node)
        print(f"  New: {filename} ({img_count} images)")
        new_count += 1

    if new_count == 0:
        print("No new posts found.")
    else:
        print(f"\nCreated {new_count} new post(s).")


if __name__ == "__main__":
    main()

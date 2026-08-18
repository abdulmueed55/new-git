#!/usr/bin/env python3
"""
WordPress Image Watermarker v2
Uploads watermarked images as new media, updates posts to reference them,
and deletes old media items.
"""

import requests
import sys
import os
import io
import time
import re
from datetime import datetime, timedelta
from PIL import Image, ImageEnhance

WP_SITE = os.environ.get("WP_SITE", "")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASS = os.environ.get("WP_APP_PASS", "")
API_BASE = f"{WP_SITE}/wp-json/wp/v2"
AUTH = None

DAYS_BACK = int(os.environ.get("DAYS_BACK", "5"))
WATERMARK_PATH = os.environ.get("WATERMARK_PATH", "watermark.png")
WATERMARK_SCALE = float(os.environ.get("WATERMARK_SCALE", "0.35"))
WATERMARK_OPACITY = float(os.environ.get("WATERMARK_OPACITY", "1.0"))
WATERMARK_POSITION = os.environ.get("WATERMARK_POSITION", "top-right")
WATERMARK_PADDING = int(os.environ.get("WATERMARK_PADDING", "20"))


def load_watermark(path):
    return Image.open(path).convert("RGBA")


def apply_watermark(image_bytes, watermark_img, mime_type):
    base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    base_w, base_h = base.size

    shorter_side = min(base_w, base_h)
    wm_target = int(shorter_side * WATERMARK_SCALE)
    wm_w, wm_h = watermark_img.size
    ratio = wm_target / max(wm_w, wm_h)
    wm_resized = watermark_img.resize(
        (int(wm_w * ratio), int(wm_h * ratio)), Image.LANCZOS
    )

    if WATERMARK_OPACITY < 1.0:
        alpha = wm_resized.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(WATERMARK_OPACITY)
        wm_resized.putalpha(alpha)

    wm_rw, wm_rh = wm_resized.size
    pad = WATERMARK_PADDING
    positions = {
        "bottom-right": (base_w - wm_rw - pad, base_h - wm_rh - pad),
        "bottom-left": (pad, base_h - wm_rh - pad),
        "top-right": (base_w - wm_rw - pad, pad),
        "top-left": (pad, pad),
        "center": ((base_w - wm_rw) // 2, (base_h - wm_rh) // 2),
    }
    pos = positions.get(WATERMARK_POSITION, positions["top-right"])

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(wm_resized, pos, wm_resized)
    composite = Image.alpha_composite(base, layer)

    fmt_map = {
        "image/jpeg": ("JPEG", "RGB"),
        "image/jpg": ("JPEG", "RGB"),
        "image/png": ("PNG", "RGBA"),
        "image/webp": ("WEBP", "RGBA"),
    }
    fmt, mode = fmt_map.get(mime_type, ("JPEG", "RGB"))
    output = composite.convert(mode)

    buf = io.BytesIO()
    save_kwargs = {"format": fmt}
    if fmt == "JPEG":
        save_kwargs["quality"] = 92
    output.save(buf, **save_kwargs)
    buf.seek(0)
    return buf.getvalue()


def fetch_recent_media(days):
    after = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    all_media = []
    page = 1
    while True:
        print(f"  Fetching page {page}...")
        resp = requests.get(
            f"{API_BASE}/media", auth=AUTH,
            params={"after": after, "per_page": 50, "page": page, "media_type": "image"},
            timeout=60,
        )
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_media.extend(data)
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return all_media


def fetch_all_posts():
    all_posts = []
    page = 1
    while True:
        resp = requests.get(
            f"{API_BASE}/posts", auth=AUTH,
            params={"per_page": 100, "page": page, "status": "publish,draft,pending,private"},
            timeout=60,
        )
        if resp.status_code == 400:
            break
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_posts.extend(data)
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1
    return all_posts


def upload_new_media(image_data, filename, mime_type, title=""):
    resp = requests.post(
        f"{API_BASE}/media", auth=AUTH,
        headers={
            "Content-Type": mime_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
        data=image_data,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def delete_media(media_id):
    resp = requests.delete(
        f"{API_BASE}/media/{media_id}",
        auth=AUTH,
        params={"force": True},
        timeout=30,
    )
    return resp.status_code in (200, 204)


def update_post(post_id, data):
    resp = requests.post(
        f"{API_BASE}/posts/{post_id}",
        auth=AUTH,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_url_variants(source_url):
    base = source_url.rsplit('.', 1)
    if len(base) != 2:
        return [source_url]
    name, ext = base
    name_noscale = name.replace('-scaled', '')
    variants = set()
    variants.add(source_url)
    variants.add(name_noscale + '.' + ext)
    variants.add(name + '-scaled.' + ext)
    for size in ['150x150', '300x200', '300x300', '768x512', '1024x683', '1024x1024', '1536x1024', '2048x1365']:
        variants.add(f"{name_noscale}-{size}.{ext}")
    return list(variants)


def main():
    global AUTH
    if not WP_SITE or not WP_USER or not WP_APP_PASS:
        print("ERROR: Set WP_SITE, WP_USER, WP_APP_PASS environment variables")
        sys.exit(1)
    AUTH = (WP_USER, WP_APP_PASS)

    if not os.path.exists(WATERMARK_PATH):
        print(f"ERROR: Watermark not found: {WATERMARK_PATH}")
        sys.exit(1)

    watermark = load_watermark(WATERMARK_PATH)
    print(f"Watermark: {watermark.size}")

    print(f"\nFetching images from last {DAYS_BACK} days...")
    media_items = fetch_recent_media(DAYS_BACK)
    print(f"  Found {len(media_items)} images")

    if not media_items:
        print("No images found.")
        return

    print("\nFetching all posts...")
    all_posts = fetch_all_posts()
    print(f"  Found {len(all_posts)} posts")

    success = 0
    failed = 0

    for i, item in enumerate(media_items, 1):
        old_id = item["id"]
        old_url = item.get("source_url", "")
        mime = item.get("mime_type", "image/jpeg")
        slug = item.get("slug", f"image-{old_id}")
        title = item.get("title", {}).get("rendered", slug)

        ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
        ext = ext_map.get(mime, ".jpg")
        filename = f"{slug}-wm{ext}"

        if slug.endswith("-wm") or "-wm." in old_url:
            print(f"\n[{i}/{len(media_items)}] ID={old_id} | {title}")
            print(f"  Skipping (already watermarked)")
            continue

        print(f"\n[{i}/{len(media_items)}] ID={old_id} | {title}")
        print(f"  Old URL: {old_url}")

        try:
            print("  Downloading...", end=" ", flush=True)
            resp = requests.get(old_url, auth=AUTH, timeout=120)
            resp.raise_for_status()
            img_data = resp.content
            print(f"{len(img_data)//1024} KB")

            print("  Watermarking...", end=" ", flush=True)
            wm_data = apply_watermark(img_data, watermark, mime)
            print(f"{len(wm_data)//1024} KB")

            print("  Uploading new...", end=" ", flush=True)
            new_media = upload_new_media(wm_data, filename, mime, title)
            new_id = new_media["id"]
            new_url = new_media["source_url"]
            print(f"ID={new_id}")

            url_variants = get_url_variants(old_url)
            posts_updated = 0
            for post in all_posts:
                pid = post["id"]
                content_raw = post.get("content", {}).get("rendered", "")
                featured = post.get("featured_media", 0)
                needs_update = False
                update_data = {}

                if featured == old_id:
                    update_data["featured_media"] = new_id
                    needs_update = True

                for variant in url_variants:
                    if variant in content_raw:
                        needs_update = True
                        break

                if needs_update:
                    if "featured_media" not in update_data:
                        update_data["featured_media"] = post.get("featured_media", 0)
                    try:
                        post_full = requests.get(
                            f"{API_BASE}/posts/{pid}",
                            auth=AUTH,
                            params={"context": "edit"},
                            timeout=30,
                        ).json()
                        raw_content = post_full.get("content", {}).get("raw", "")
                        new_content = raw_content
                        for variant in url_variants:
                            new_content = new_content.replace(variant, new_url)
                        if new_content != raw_content:
                            update_data["content"] = new_content
                        update_post(pid, update_data)
                        posts_updated += 1
                        print(f"  Updated post {pid}")
                    except Exception as e:
                        print(f"  Failed updating post {pid}: {e}")

            print(f"  Deleting old media {old_id}...", end=" ", flush=True)
            if delete_media(old_id):
                print("OK")
            else:
                print("FAILED (non-critical)")

            print(f"  Done! New URL: {new_url} | Posts updated: {posts_updated}")
            success += 1

        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

        if i < len(media_items):
            time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"Done! Success: {success} | Failed: {failed} | Total: {len(media_items)}")


if __name__ == "__main__":
    main()

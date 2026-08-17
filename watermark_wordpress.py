#!/usr/bin/env python3
"""
WordPress Image Watermarker
Fetches recent images from WordPress, adds a watermark logo, and re-uploads them.
"""

import requests
import sys
import os
import io
import time
from datetime import datetime, timedelta
from PIL import Image, ImageEnhance

# ── Configuration ──────────────────────────────────────────────
WP_SITE = os.environ.get("WP_SITE", "")
WP_USER = os.environ.get("WP_USER", "")
WP_APP_PASS = os.environ.get("WP_APP_PASS", "")
API_BASE = f"{WP_SITE}/wp-json/wp/v2"

DAYS_BACK = int(os.environ.get("DAYS_BACK", "5"))
WATERMARK_PATH = os.environ.get("WATERMARK_PATH", "watermark.png")

# Watermark size as percentage of the shorter side of the image
WATERMARK_SCALE = float(os.environ.get("WATERMARK_SCALE", "0.20"))
# Opacity: 0.0 = invisible, 1.0 = fully opaque
WATERMARK_OPACITY = float(os.environ.get("WATERMARK_OPACITY", "0.5"))
# Position: bottom-right, bottom-left, top-right, top-left, center
WATERMARK_POSITION = os.environ.get("WATERMARK_POSITION", "bottom-right")
# Padding from edge in pixels
WATERMARK_PADDING = int(os.environ.get("WATERMARK_PADDING", "20"))


def load_watermark(path):
    wm = Image.open(path).convert("RGBA")
    return wm


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
    pos = positions.get(WATERMARK_POSITION, positions["bottom-right"])

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(wm_resized, pos)
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
            f"{API_BASE}/media",
            auth=(WP_USER, WP_APP_PASS),
            params={
                "after": after,
                "per_page": 50,
                "page": page,
                "media_type": "image",
            },
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


def download_image(url):
    resp = requests.get(url, auth=(WP_USER, WP_APP_PASS), timeout=120)
    resp.raise_for_status()
    return resp.content


def upload_replacement(media_id, image_data, filename, mime_type):
    resp = requests.post(
        f"{API_BASE}/media/{media_id}",
        auth=(WP_USER, WP_APP_PASS),
        headers={"Content-Type": mime_type, "Content-Disposition": f'attachment; filename="{filename}"'},
        data=image_data,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    if not WP_SITE or not WP_USER or not WP_APP_PASS:
        print("ERROR: Set environment variables WP_SITE, WP_USER, and WP_APP_PASS")
        print("Example:")
        print('  WP_SITE="https://yoursite.com" WP_USER="admin" WP_APP_PASS="xxxx" python3 watermark_wordpress.py')
        sys.exit(1)

    if not os.path.exists(WATERMARK_PATH):
        print(f"ERROR: Watermark file not found: {WATERMARK_PATH}")
        print("Set WATERMARK_PATH environment variable or place watermark.png in the current directory.")
        sys.exit(1)

    print(f"Loading watermark from: {WATERMARK_PATH}")
    watermark = load_watermark(WATERMARK_PATH)
    print(f"  Watermark size: {watermark.size}")

    print(f"\nFetching images uploaded in the last {DAYS_BACK} days from {WP_SITE}...")
    media_items = fetch_recent_media(DAYS_BACK)
    print(f"  Found {len(media_items)} images\n")

    if not media_items:
        print("No images found in the specified period. Nothing to do.")
        return

    success = 0
    failed = 0

    for i, item in enumerate(media_items, 1):
        mid = item["id"]
        title = item.get("title", {}).get("rendered", "untitled")
        src = item.get("source_url", "")
        mime = item.get("mime_type", "image/jpeg")
        slug = item.get("slug", f"image-{mid}")
        ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
        ext = ext_map.get(mime, ".jpg")
        filename = f"{slug}{ext}"

        print(f"[{i}/{len(media_items)}] ID={mid} | {title}")
        print(f"  Source: {src}")

        try:
            print("  Downloading...", end=" ", flush=True)
            img_data = download_image(src)
            print(f"{len(img_data) / 1024:.0f} KB")

            print("  Adding watermark...", end=" ", flush=True)
            watermarked = apply_watermark(img_data, watermark, mime)
            print(f"{len(watermarked) / 1024:.0f} KB")

            print("  Uploading replacement...", end=" ", flush=True)
            result = upload_replacement(mid, watermarked, filename, mime)
            new_url = result.get("source_url", "done")
            print(f"OK -> {new_url}")

            success += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

        if i < len(media_items):
            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Done! Success: {success} | Failed: {failed} | Total: {len(media_items)}")


if __name__ == "__main__":
    main()

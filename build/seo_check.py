#!/usr/bin/env python3
"""Audit the built site for the things that get pages demoted.

Checks every page in docs/ for:
  - over-used words and phrases (keyword stuffing)
  - near-duplicate pages (the doorway-page problem)
  - title and meta description length
  - a single, unique h1
  - thin content

    python3 build/seo_check.py           # report
    python3 build/seo_check.py --strict  # exit 1 on any error, for CI
"""
import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Thresholds. Density is share of total words on the page.
MAX_WORD_DENSITY = 0.035      # 3.5% for a single word
MAX_BIGRAM_DENSITY = 0.020    # 2.0% for a two-word phrase
MAX_PHRASE_REPEATS = 20       # only counts alongside density, see below
MAX_SIMILARITY = 0.80         # near-duplicate pages
MIN_WORDS = 280
TITLE_RANGE = (25, 70)
DESC_RANGE = (105, 165)

STOP = set("""a an and are as at be been but by can could do does for from had has have he her his
how i if in into is it its may might must no not of on or our she should so some such than that the
their them then there these they this those to too up was we were what when where which who why will
with would you your yours it's don't""".split())


def main_text(html):
    """Only the content between <main> tags, as plain words."""
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S | re.I)
    body = m.group(1) if m else html
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"&[a-z]+;|&#\d+;", " ", body)
    return re.sub(r"\s+", " ", body).strip()


def words(text):
    return re.findall(r"[a-z][a-z'-]{1,}", text.lower())


def shingles(ws, n=5):
    return {" ".join(ws[i:i + n]) for i in range(max(0, len(ws) - n + 1))}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def attr(html, pattern):
    m = re.search(pattern, html, re.I | re.S)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    pages = sorted(DOCS.rglob("*.html"))
    errors, warnings = [], []
    titles, h1s, shingle_map = {}, {}, {}

    for path in pages:
        rel = path.relative_to(DOCS).as_posix()
        html = path.read_text(encoding="utf-8")
        text = main_text(html)
        ws = words(text)
        total = len(ws)

        title = attr(html, r"<title>(.*?)</title>")
        desc = attr(html, r'<meta name="description" content="(.*?)"')
        heads = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)

        if not TITLE_RANGE[0] <= len(title) <= TITLE_RANGE[1]:
            warnings.append(f"{rel}: title is {len(title)} chars (aim {TITLE_RANGE[0]}-{TITLE_RANGE[1]})")
        if desc and not DESC_RANGE[0] <= len(desc) <= DESC_RANGE[1]:
            warnings.append(f"{rel}: meta description is {len(desc)} chars (aim {DESC_RANGE[0]}-{DESC_RANGE[1]})")
        elif not desc:
            errors.append(f"{rel}: no meta description")

        if len(heads) != 1:
            errors.append(f"{rel}: {len(heads)} h1 tags, expected exactly 1")
        else:
            h1 = re.sub(r"<[^>]+>", "", heads[0]).strip()
            if h1 in h1s:
                errors.append(f"{rel}: h1 duplicates {h1s[h1]} ({h1!r})")
            else:
                h1s[h1] = rel
        if title in titles:
            errors.append(f"{rel}: title duplicates {titles[title]}")
        else:
            titles[title] = rel

        # Index pages are listings; the cards carry the value, not prose.
        if total < MIN_WORDS and not rel.endswith("index.html"):
            warnings.append(f"{rel}: only {total} words of content")

        if total >= 150:
            counts = collections.Counter(w for w in ws if w not in STOP and len(w) > 3)
            for word, n in counts.most_common(3):
                if n / total > MAX_WORD_DENSITY:
                    errors.append(f"{rel}: '{word}' used {n}x = {n / total:.1%} of the page "
                                  f"(over {MAX_WORD_DENSITY:.1%})")
            bigrams = collections.Counter(
                f"{a} {b}" for a, b in zip(ws, ws[1:])
                if a not in STOP and b not in STOP
            )
            for phrase, n in bigrams.most_common(3):
                # A topic term appearing often on a long page is normal writing;
                # stuffing shows up as density, so the count alone never fails a page.
                dense = n / total > MAX_BIGRAM_DENSITY
                repeated = n > MAX_PHRASE_REPEATS and n / total > 0.015
                if dense or repeated:
                    errors.append(f"{rel}: phrase '{phrase}' used {n}x = {n / total:.1%} "
                                  f"of the page (over {MAX_BIGRAM_DENSITY:.1%})")

        if total >= 200:
            shingle_map[rel] = shingles(ws)

    names = sorted(shingle_map)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sim = jaccard(shingle_map[a], shingle_map[b])
            if sim > MAX_SIMILARITY:
                errors.append(f"near-duplicate pages ({sim:.0%} identical): {a}  <->  {b}")

    print(f"Checked {len(pages)} pages.\n")
    if errors:
        print(f"{len(errors)} ERROR(S):")
        for e in errors:
            print("  " + e)
        print()
    if warnings:
        print(f"{len(warnings)} warning(s):")
        for w in warnings[:40]:
            print("  " + w)
        if len(warnings) > 40:
            print(f"  ... and {len(warnings) - 40} more")
        print()
    if not errors and not warnings:
        print("Clean.")
    elif not errors:
        print("No errors.")

    if args.strict and errors:
        sys.exit(1)


if __name__ == "__main__":
    main()

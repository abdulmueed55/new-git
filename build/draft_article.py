#!/usr/bin/env python3
"""Draft a guide with the Gemini API.

The draft lands in content/drafts/ and is NOT published. Review it, then:

    python3 build/publish_draft.py <slug>

This two-step design is deliberate. Google's spam policy treats unreviewed,
mass-produced AI content as "scaled content abuse", which costs sites their
index position and their AdSense account. A draft that a human has read and
corrected is not that.

Usage:
    GEMINI_API_KEY=...  python3 build/draft_article.py
    GEMINI_API_KEY=...  python3 build/draft_article.py --topic "How to raise your rates"

Environment:
    GEMINI_API_KEY   required
    GEMINI_MODEL     optional, defaults to gemini-2.5-flash
"""
import argparse
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "content" / "drafts"
ARTICLES = ROOT / "content" / "articles"
TOPICS = ROOT / "build" / "topics.txt"
TOPICS_DONE = ROOT / "build" / "topics-done.txt"

ENDPOINT = ("https://generativelanguage.googleapis.com/v1beta/models/"
            "{model}:generateContent?key={key}")

STYLE = """You write for FreelanceFigures, a site of free money calculators for freelancers
and small businesses. Your readers are self-employed people in the US, UK, Canada and
Australia who are competent at their craft and inexperienced at the business side.

VOICE
- Direct, specific, unsentimental. Short sentences carry the important points.
- Lead with the thing that costs the reader money. No throat-clearing introductions,
  no "In today's fast-paced world", no "Let's dive in".
- Use real numbers in every explanation. "A $2,500 invoice 74 days late accrues $92.50"
  beats "late fees add up".
- Never use: unleash, delve, navigate the landscape, game-changer, in conclusion,
  it's important to note, leverage (as a verb), supercharge, robust.
- British or American spelling is fine, but be consistent inside one article.
- Address the reader as "you". Never refer to yourself or to AI.

ACCURACY
- Do not invent statistics, studies, survey results or sources. If you want to cite a
  figure you are not certain of, write it as a range and label it as typical rather
  than measured.
- Tax rules differ by country. Say which country a rule applies to, every time.
- Never state a current-year tax rate, threshold or interest rate as fact. Describe how
  the rule works and tell the reader to check the current figure.

FORMAT
- Output ONLY the article file, starting with the front matter block, nothing else.
- No markdown. No code fences. Plain HTML fragment: h2, h3, p, ul, ol, li, table, tr,
  th, td, strong, em, a. No h1 (the template adds it). No <html>, <head> or <body>.
- 900-1400 words. Four to seven h2 sections.
- Include at least one table or one <div class="note"> block containing a formula.
- Use &mdash; &ndash; &pound; &amp; and other HTML entities rather than raw characters.

INTERNAL LINKS
- Link naturally to two or three of the site's calculators where they genuinely help.
- Use the exact URLs given below. Never invent a URL. Never link to an external site.
"""

FRONT_MATTER = """The file must start with exactly this shape, then a line containing only ---

title: <60-70 characters, specific, no colon-subtitle pattern>
description: <one sentence, 140-160 characters, becomes the meta description>
date: {date}
tags: <two or three lowercase comma-separated tags>
---
"""


def site_context():
    """Give the model the real tool URLs so it cannot invent links."""
    sys.path.insert(0, str(ROOT / "build"))
    import generate  # noqa: E402
    lines = ["CALCULATORS ON THE SITE (use these exact URLs):"]
    for t in generate.TOOLS:
        lines.append("- /tools/%s.html  — %s" % (t["slug"], generate.strip_tags(t["card"])))
    existing = sorted(p.stem for p in ARTICLES.glob("*.html"))
    if existing:
        lines.append("")
        lines.append("GUIDES ALREADY PUBLISHED (do not repeat these; link with /guides/<slug>.html):")
        lines += ["- " + s for s in existing]
    return "\n".join(lines)


def next_topic():
    if not TOPICS.exists():
        return None
    done = set()
    if TOPICS_DONE.exists():
        done = {l.strip() for l in TOPICS_DONE.read_text(encoding="utf-8").splitlines() if l.strip()}
    for line in TOPICS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line not in done:
            return line
    return None


def mark_done(topic):
    with TOPICS_DONE.open("a", encoding="utf-8") as fh:
        fh.write(topic + "\n")


def call_gemini(prompt, model, key):
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT.format(model=model, key=key),
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        sys.exit(f"Gemini returned HTTP {e.code}.\n{detail}\n\n"
                 f"If the model name is wrong, set GEMINI_MODEL to one your key can use.")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach the Gemini API: {e.reason}")

    try:
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except (KeyError, IndexError):
        sys.exit("Unexpected response from Gemini:\n" + json.dumps(data, indent=2)[:1200])


def slugify(title):
    s = re.sub(r"&[a-z]+;", " ", title.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70]


def clean(text):
    """Strip code fences and any preamble before the front matter."""
    text = re.sub(r"^\s*```(?:html)?\s*", "", text)
    text = re.sub(r"\s*```\s*$", "", text)
    idx = text.find("title:")
    return text[idx:].strip() if idx > 0 else text.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", help="Topic to write about. Defaults to the next line in build/topics.txt")
    ap.add_argument("--model", default=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("Set GEMINI_API_KEY first.")

    topic = args.topic or next_topic()
    if not topic:
        print("No topics left in build/topics.txt. Add some and run again.")
        return

    today = datetime.date.today().isoformat()
    prompt = "\n\n".join([
        STYLE,
        site_context(),
        FRONT_MATTER.format(date=today),
        "Write the article now. The topic is:\n\n" + topic,
    ])

    print(f"Drafting: {topic}\n  model: {args.model}")
    text = clean(call_gemini(prompt, args.model, key))

    m = re.search(r"^title:\s*(.+)$", text, re.M)
    if not m:
        sys.exit("The model did not return a front matter block. Nothing written.\n\n" + text[:800])
    slug = slugify(m.group(1))

    DRAFTS.mkdir(parents=True, exist_ok=True)
    path = DRAFTS / f"{slug}.html"
    path.write_text(text + "\n", encoding="utf-8")
    if not args.topic:
        mark_done(topic)

    words = len(re.sub(r"<[^>]+>", " ", text).split())
    print(f"\nDraft written: {path.relative_to(ROOT)}  ({words} words)")
    print("\nRead it, fix anything wrong, then publish with:")
    print(f"    python3 build/publish_draft.py {slug}")


if __name__ == "__main__":
    main()

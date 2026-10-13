#!/usr/bin/env python3
"""Move a reviewed draft into the published guides and rebuild the site.

    python3 build/publish_draft.py <slug>
    python3 build/publish_draft.py --list
"""
import argparse
import datetime
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "content" / "drafts"
ARTICLES = ROOT / "content" / "articles"

REQUIRED = ("title:", "description:", "date:", "\n---\n")
BANNED = ("delve", "unleash", "game-changer", "in conclusion", "supercharge",
          "it's important to note", "navigate the landscape")


def check(text):
    """Catch the problems that are cheap to catch before publishing."""
    problems = []
    for token in REQUIRED:
        if token not in text:
            problems.append(f"missing {token.strip()} in the front matter")
    body = text.partition("\n---\n")[2]
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    if words < 500:
        problems.append(f"body is only {words} words — too thin to rank")
    if "<h1" in body:
        problems.append("contains an <h1>; the template already adds one")
    if "```" in text:
        problems.append("contains a markdown code fence")
    low = text.lower()
    for word in BANNED:
        if word in low:
            problems.append(f"contains banned filler phrase: {word!r}")
    for href in re.findall(r'href="([^"]+)"', body):
        if href.startswith("http"):
            problems.append(f"external link found: {href}")
        elif not href.startswith(("/tools/", "/guides/", "#")):
            problems.append(f"suspicious link: {href}")
    return problems, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--list", action="store_true", help="show drafts waiting for review")
    ap.add_argument("--force", action="store_true", help="publish despite warnings")
    ap.add_argument("--today", action="store_true", help="reset the date to today")
    args = ap.parse_args()

    drafts = sorted(DRAFTS.glob("*.html"))
    if args.list or not args.slug:
        if not drafts:
            print("No drafts waiting. Run build/draft_article.py to make one.")
            return
        print("Drafts waiting for review:\n")
        for d in drafts:
            title = ""
            for line in d.read_text(encoding="utf-8").splitlines():
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                    break
            print(f"  {d.stem}\n      {title}\n")
        return

    src = DRAFTS / f"{args.slug}.html"
    if not src.exists():
        sys.exit(f"No draft called {args.slug}. Run with --list to see what is waiting.")

    text = src.read_text(encoding="utf-8")
    problems, words = check(text)
    if problems:
        print(f"Checks on {args.slug} ({words} words):")
        for p in problems:
            print("  - " + p)
        if not args.force:
            sys.exit("\nNot published. Fix the draft, or pass --force if these are acceptable.")
        print("\n--force given, publishing anyway.")

    if args.today:
        text = re.sub(r"^date:.*$", "date: " + datetime.date.today().isoformat(),
                      text, count=1, flags=re.M)

    ARTICLES.mkdir(parents=True, exist_ok=True)
    (ARTICLES / f"{args.slug}.html").write_text(text, encoding="utf-8")
    src.unlink()
    print(f"Published content/articles/{args.slug}.html ({words} words)")

    subprocess.run([sys.executable, str(ROOT / "build" / "generate.py")], check=True)


if __name__ == "__main__":
    main()

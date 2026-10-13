# FreelanceFigures — free calculator site (AdSense-funded)

A static, ad-supported tool site aimed at US/UK/CA/AU freelancers. Six calculators plus a
growing library of guides. Everything runs in the visitor's browser: no server, no database,
no API costs, so hosting is effectively free and pages load in well under a second — which is
itself a ranking factor.

The existing `index.html` at the repo root (the Vybrex agency page) is untouched. This site
lives entirely in `docs/`.

```
build/generate.py        the generator — templates and the nine calculators
build/data.py            countries and professions; each entry becomes a page
build/keywords.py        writes the keyword plan
build/seo_check.py       audits the built site before it goes live
content/articles/*.html  one file per guide; drop a new one in and rebuild
content/keywords.csv     6,767 keywords mapped to the page that serves them
docs/                    the generated site — this is what you upload
```

96 pages: 9 calculators, 35 country tax pages, 40 profession rate pages, guides,
two hub pages and the legal pages AdSense asks for.

## Build

```bash
python3 build/generate.py
```

No dependencies beyond Python 3. It regenerates every page, the sitemap and robots.txt.

## Deploying to Hostinger

1. Run the build.
2. Upload **the contents of `docs/`** (not the folder itself) into `public_html` on your
   Hostinger account, via hPanel's File Manager or FTP.
3. Point your domain at it. The site is pure HTML/CSS/JS — no PHP, no database, nothing to configure.

If your Hostinger plan has Git deployment, point it at this repository and set the deploy
directory to `docs`, and every push publishes automatically.

Alternatively, GitHub Pages serves `docs/` directly — useful for a free staging URL while you
wait for AdSense approval. Settings → Pages → Branch: your branch, Folder: `/docs`.

## Turning on AdSense

1. Buy a real domain (a `.github.io` subdomain is usually rejected). About $10/year.
2. Publish the site and let Google index it. Submit `https://yourdomain.com/sitemap.xml`
   in Google Search Console on day one.
3. Apply to AdSense once the site has 15–25 solid pages. It already has the three pages
   reviewers check for: privacy policy, terms, and a contact page.
4. When approved, open `docs/assets/js/site.js` and set:

   ```js
   var ADSENSE_CLIENT = 'ca-pub-XXXXXXXXXXXXXXXX';
   ```

   Until that line has a value, every ad slot stays hidden — so the site never shows empty
   boxes while you are waiting.
5. Create your ad units in AdSense and paste each slot ID into the matching
   `data-slot="..."` attribute, or leave them and let Auto Ads place them.
6. Replace `docs/ads.txt` with the line AdSense gives you. Without it, Google throttles
   your revenue.

## Daily automation

Two GitHub Actions workflows run this site.

**`.github/workflows/daily-draft.yml`** runs every weekday morning, takes the next topic from
`build/topics.txt`, drafts a guide with the Gemini API and commits it to `content/drafts/`.
It deliberately does **not** publish.

**`.github/workflows/build.yml`** runs on every push and fails if `docs/` does not match what
the generator produces, so a hand-edited page cannot drift out of sync.

To switch the drafting on, add under Settings → Secrets and variables → Actions:

| Kind | Name | Value |
|---|---|---|
| Secret | `GEMINI_API_KEY` | your key from aistudio.google.com |
| Variable (optional) | `GEMINI_MODEL` | defaults to `gemini-2.5-flash` |

Then review and publish:

```bash
python3 build/publish_draft.py --list        # what is waiting
python3 build/publish_draft.py <slug>        # publish it and rebuild
```

`publish_draft.py` refuses a draft that is under 500 words, contains an `<h1>`, links to an
external site, or uses the filler phrases that make AI writing obvious. Override with `--force`
only when you have read it.

### Why there is a review step

Google's spam policy treats unreviewed, mass-produced AI content as *scaled content abuse*. Sites
caught doing it lose their rankings and their AdSense account. A draft that a person has read and
corrected is not that — and the review usually takes five minutes, because the draft is already
in the house style.

Run it by hand any time:

```bash
GEMINI_API_KEY=... python3 build/draft_article.py
GEMINI_API_KEY=... python3 build/draft_article.py --topic "How to raise your rates"
```

## Adding a guide by hand

Create one file in `content/articles/`, named with the URL slug you want:

```
content/articles/how-to-raise-your-rates.html
```

```
title: How to Raise Your Rates Without Losing Clients
description: One sentence that becomes the meta description and the card text.
date: 2026-10-14
tags: pricing
---
<p>Body goes here as plain HTML — h2, h3, p, ul, ol, table.</p>
```

Then run `python3 build/generate.py`. The generator will:

- create `docs/guides/<slug>.html` with full Article schema,
- add it to the guides index and the homepage,
- add it to `sitemap.xml`,
- link it from every calculator page under "Related reading", and
- **auto-link** mentions of things like "hourly rate calculator" or "self-employment tax"
  in the body to the matching tool page, first mention only, never inside a heading or an
  existing link.

That last part is the internal linking engine. Add new phrase → URL pairs to `LINK_MAP` in
`build/generate.py` as the site grows.

## Programmatic pages

`build/data.py` holds 35 countries and 40 professions. Each entry becomes its own page, and each
entry carries its own facts: Germany's small-business exemption, Canada's province-by-province
rate, Pakistan's provincial services tax, a photographer's equipment burden, a voice actor's
unpaid audition time.

That per-entry detail is the whole point. A template with one word swapped is a doorway page, and
Google removes those. Adding a country or a profession means writing real content for it — if you
cannot say something true and specific about an entry, it should not have a page.

## Keywords

```bash
python3 build/keywords.py        # writes content/keywords.csv
```

6,767 keywords, each mapped to the page meant to serve it and tiered:

| Tier | Meaning | Count |
|---|---|---|
| 1 | a page for it exists today | 1,275 |
| 2 | the page is planned | 5,136 |
| 3 | needs a new page first | 356 |

No search volumes are included, because inventing them would be worse than useless. Import the CSV
into Google Keyword Planner, Ahrefs or Semrush for real volume and difficulty numbers.

**The file is a plan, not something to paste into pages.** A keyword earns its place in a page by
being what the page genuinely answers. Keywords pasted into markup are keyword stuffing, which is
what the audit below exists to catch.

## The SEO audit

```bash
python3 build/seo_check.py           # report
python3 build/seo_check.py --strict  # exit 1 on any error, used in CI
```

It fails the build on:

- **over-used words** — any single word above 3.5% of a page, any two-word phrase above 2%
- **near-duplicate pages** — any two pages more than 80% identical
- **duplicate titles or h1s** across the site
- **missing or malformed meta descriptions**
- **thin content** — under 280 words outside index pages

It has already earned its place: it found a guide whose meta description was silently truncated to
seven characters because the text contained a double quote, and a hub page that repeated the same
two words forty times.

## Getting traffic

See [TRAFFIC.md](TRAFFIC.md) for the week-one checklist and the channel-by-channel plan.

## What actually makes this earn

The money is in the niche, not the traffic. General utility tools earn roughly $2 per 1,000
pageviews; money, tax and business calculators earn $12–25, because the advertisers bidding
on them sell accounting software and financial services. That is why $500/month here needs
roughly 25,000–40,000 monthly pageviews rather than 250,000.

Realistic timeline with consistent publishing: 6–10 months. The levers, in order of impact:

1. **Publish regularly.** Two to three guides a week beats twenty in one weekend.
2. **Target questions, not keywords.** "How much should I charge as a freelance designer"
   is winnable. "Freelance calculator" is not.
3. **Build one more calculator per month.** Each is a new page that can rank on its own.
4. **Keep pages fast.** This build is already near-perfect on Core Web Vitals; do not add
   heavy frameworks, large images, or tracking scripts.

## Local preview

```bash
cd docs && python3 -m http.server 8000
```

Then open http://localhost:8000.

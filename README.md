# FreelanceFigures — free calculator site (AdSense-funded)

A static, ad-supported tool site aimed at US/UK/CA/AU freelancers. Six calculators plus a
growing library of guides. Everything runs in the visitor's browser: no server, no database,
no API costs, so hosting is effectively free and pages load in well under a second — which is
itself a ranking factor.

The existing `index.html` at the repo root (the Vybrex agency page) is untouched. This site
lives entirely in `docs/`.

```
build/generate.py        the generator — all page content and templates live here
content/articles/*.html  one file per guide; drop a new one in and rebuild
docs/                    the generated site — this is what you upload
```

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

## Adding a guide (the daily content loop)

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

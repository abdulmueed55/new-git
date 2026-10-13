# Getting the first visitors

The honest shape of this: SEO is the engine, but it does not start for months. Everything in
Phase 1 exists to keep the site alive while Google makes up its mind, and to produce the early
signals (real visits, real links) that make Google decide faster.

Do not buy traffic. Paid clicks on an AdSense site are the fastest route to an account ban,
because the clicks arrive without intent and the ad engagement looks fraudulent.

---

## Phase 0 — the week you launch (do all of it, it is two hours)

- [ ] **Buy a real domain.** A free subdomain usually fails AdSense review. ~$10/year.
- [ ] **Deploy** the contents of `docs/` to the host.
- [ ] **Google Search Console** — add the domain, verify, submit `/sitemap.xml`.
      Then use "URL Inspection → Request indexing" on the homepage and the three strongest
      calculator pages. This is the single highest-value thing on this list.
- [ ] **Bing Webmaster Tools** — add and submit the same sitemap. Bing indexes new sites far
      faster than Google, and Bing feeds ChatGPT search and DuckDuckGo.
- [ ] **Analytics** — Google Analytics or Plausible. You cannot improve what you cannot see.
- [ ] **Check mobile** on a real phone. More than 60% of this traffic will be mobile.
- [ ] **PageSpeed Insights** on one tool page. This build should score in the high 90s; if it
      does not, something was added that should not have been.

## Phase 1 — weeks 1 to 6: borrow an audience

The rule for every channel below: **answer the question first, link second, and only when the
link genuinely helps.** Drive-by link drops get removed, get you banned, and send visitors who
bounce in four seconds — which teaches Google the page is bad.

### Reddit — the highest-yield channel, and the easiest to get banned from
Subreddits: r/freelance, r/graphic_design, r/webdev, r/smallbusiness, r/Entrepreneur,
r/digitalnomad, r/consulting, r/copywriting.

- Spend the first two weeks commenting with no links at all. Build comment karma.
- Sort by new. Answer "how much should I charge" and "client won't pay" threads properly —
  three or four paragraphs of actual help.
- Only then, where it fits: "I built a calculator for exactly this, free, no sign-up: <link>".
  Roughly one link per ten genuine comments.
- Read each subreddit's self-promotion rule before posting. Several ban links outright.

### Quora
Search "freelance rate", "self employment tax", "late invoice". Answer thoroughly. Quora
answers rank in Google for years and keep sending trickles of traffic long after you write them.

### Indie Hackers / Hacker News / Product Hunt
- Indie Hackers: a build-log post about making a free calculator site does well.
- Hacker News: one "Show HN" post. One. A second looks like spam.
- Product Hunt: launch once the site has 20+ pages. Good for links, not for lasting traffic.

### Facebook and LinkedIn groups
Freelancer groups are full of exactly these questions every single day. Same rule: answer
properly, link when relevant.

### Pinterest — underrated for calculators
Make a simple image for each calculator ("What should a freelancer charge? Free calculator")
and pin it. Calculator and money content performs unusually well there, and the audience is
largely US, which is the highest-paying ad market.

### Free tool directories
Submit to directories that list free online tools. Low traffic each, but they are real
backlinks, and early backlinks shorten the time Google takes to trust a new domain.

## Phase 2 — months 2 to 8: let SEO compound

This is where the actual money comes from.

- **Publish two to three guides a week.** Use `build/draft_article.py`, review, publish.
  Consistency beats volume: ten articles a month every month beats forty in one weekend.
- **Add one calculator a month.** Each is a new page that can rank on its own and a new reason
  for someone to link to you.
- **Target questions, not keywords.** "How much should I charge as a freelance designer" is
  winnable for a new site. "Freelance calculator" is not, and will not be for years.
- **Watch Search Console every week.** The Performance report shows what you are already
  ranking for on page two. Those queries are the cheapest wins on the internet: write a guide
  aimed precisely at one, or add a section to the page that already half-ranks.
- **Earn a few links.** Answer journalist requests on HARO or Qwoted, get listed in "best free
  tools for freelancers" roundups, write one or two genuine guest posts. Never buy links.

## Phase 3 — once traffic is real

- Tune ad placement. One ad above the fold, one mid-content, one at the end. More than that
  hurts both rankings and revenue per visitor.
- At roughly 10,000 sessions a month, Ezoic becomes worth testing against AdSense.
- At 50,000 sessions, Mediavine pays substantially more than AdSense and is worth switching to.

---

## What the numbers need to be

At the RPM this niche earns ($12&ndash;25 per 1,000 pageviews), $500/month needs roughly
25,000&ndash;40,000 monthly pageviews. For a site publishing consistently, that is typically
month 6 to month 10. Anyone promising it in week four is selling something.

A realistic trajectory:

| Month | Pages | Monthly pageviews | Revenue |
|---|---|---|---|
| 1 | 20 | 100&ndash;500 | $0 (not yet approved) |
| 3 | 45 | 1,500&ndash;4,000 | $20&ndash;60 |
| 6 | 80 | 8,000&ndash;15,000 | $120&ndash;300 |
| 9 | 110 | 25,000&ndash;40,000 | $400&ndash;800 |
| 12 | 140 | 50,000+ | $800&ndash;1,500 |

The variance is enormous and depends almost entirely on whether the publishing actually happens
every week. The sites that fail are not the ones with bad content. They are the ones that
stopped in month three because nothing had happened yet.

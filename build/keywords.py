#!/usr/bin/env python3
"""Build the keyword plan.

Writes content/keywords.csv: every keyword this site could reasonably target,
mapped to the page that serves it, with a priority tier.

This is a research asset, not something to paste into pages. Keywords belong in
a page because the page genuinely answers that query. A keyword list dumped into
markup is keyword stuffing, which Google penalises and which this file exists to
make unnecessary.

No search volumes are included, because inventing them would be worse than
useless. Export this list into Google Keyword Planner, Ahrefs or Semrush to get
real volume and difficulty figures.

    python3 build/keywords.py
"""
import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "build"))
import data as site_data  # noqa: E402

OUT = ROOT / "content" / "keywords.csv"

# Tier 1 = a page for it exists today
# Tier 2 = the page is planned and the topic is in build/topics.txt
# Tier 3 = future; needs a new page before it is worth chasing
rows = []
seen = set()


def add(keyword, cluster, intent, target, tier):
    k = " ".join(keyword.lower().split())
    if k in seen or len(k) < 8:
        return
    seen.add(k)
    rows.append({
        "keyword": k,
        "cluster": cluster,
        "intent": intent,
        "target_page": target,
        "tier": tier,
    })


# ---------------------------------------------------------------- professions
PROF_PATTERNS = [
    ("how much should a freelance {p} charge", "informational"),
    ("freelance {p} hourly rate", "commercial"),
    ("freelance {p} rates", "commercial"),
    ("average freelance {p} rate", "informational"),
    ("{p} rate calculator", "transactional"),
    ("freelance {p} pricing guide", "informational"),
    ("what to charge as a freelance {p}", "informational"),
    ("freelance {p} day rate", "commercial"),
    ("{p} hourly rate calculator", "transactional"),
    ("how to price {p} work", "informational"),
    ("freelance {p} salary vs contract", "informational"),
    ("setting rates as a freelance {p}", "informational"),
    ("{p} freelance rate per hour", "commercial"),
    ("how much do freelance {p}s make", "informational"),
    ("starting rate for a freelance {p}", "informational"),
    ("raising rates as a freelance {p}", "informational"),
]
PROF_GEO = ["uk", "usa", "canada", "australia", "ireland", "germany", "india", "south africa"]
PROF_LEVEL = ["junior", "senior", "beginner", "experienced"]
PROF_UNIT = ["per hour", "per day", "per project", "per month"]

for pr in site_data.PROFESSIONS:
    name = pr["name"].lower()
    page = f"/freelance-rates/{pr['slug']}.html"
    for pattern, intent in PROF_PATTERNS:
        add(pattern.format(p=name), "profession rates", intent, page, 1)
    for geo in PROF_GEO:
        add(f"freelance {name} rates {geo}", "profession rates", "commercial", page, 2)
        add(f"how much do freelance {name}s charge in {geo}", "profession rates", "informational", page, 2)
        add(f"freelance {name} hourly rate {geo}", "profession rates", "commercial", page, 2)
    for lvl in PROF_LEVEL:
        add(f"{lvl} freelance {name} rates", "profession rates", "informational", page, 2)
    for unit in PROF_UNIT:
        add(f"freelance {name} rate {unit}", "profession rates", "commercial", page, 2)
    add(f"freelance {name} invoice template", "profession ops", "transactional", "/tools/invoice-late-fee-calculator.html", 3)
    add(f"freelance {name} contract", "profession ops", "informational", "/guides/", 3)
    add(f"freelance {name} business expenses", "profession ops", "informational", page, 3)
    add(f"is freelance {name} work profitable", "profession rates", "informational", page, 3)
    add(f"freelance {name} tax deductions", "profession ops", "informational", "/tools/freelance-take-home-pay-calculator.html", 3)

# ---------------------------------------------------------------- countries
CTRY_PATTERNS = [
    ("{tax} calculator {c}", "transactional", 1),
    ("{c} {tax} calculator", "transactional", 1),
    ("how to calculate {tax} in {c}", "informational", 1),
    ("{tax} rate in {c}", "informational", 1),
    ("how to remove {tax} from a price in {c}", "informational", 1),
    ("add {tax} to a price {c}", "transactional", 1),
    ("{tax} registration threshold {c}", "informational", 1),
    ("do freelancers pay {tax} in {c}", "informational", 2),
    ("when to register for {tax} in {c}", "informational", 2),
    ("{tax} return deadline {c}", "informational", 3),
    ("reverse {tax} calculator {c}", "transactional", 1),
    ("{tax} inclusive or exclusive {c}", "informational", 2),
    ("how much {tax} do i charge in {c}", "informational", 2),
    ("{tax} for self employed in {c}", "informational", 2),
]
for c in site_data.COUNTRIES:
    cname = c["name"].replace("the ", "")
    tax = c["tax"].split(" (")[0].lower()
    page = f"/vat-calculator/{c['slug']}.html"
    for pattern, intent, tier in CTRY_PATTERNS:
        add(pattern.format(tax=tax, c=cname), "country tax", intent, page, tier)
        add(pattern.format(tax=tax, c=c["adj"].lower()), "country tax", intent, page, tier)
    if not c["verify_rate"]:
        add(f"{c['rate']} percent {tax} calculator", "country tax", "transactional", page, 2)
        add(f"remove {c['rate']}% {tax}", "country tax", "transactional", page, 2)
        add(f"add {c['rate']}% {tax} to a price", "country tax", "transactional", page, 2)

# ---------------------------------------------------------------- core tools
CORE = [
    ("/tools/freelance-hourly-rate-calculator.html", "hourly rate", [
        "freelance hourly rate calculator", "how to calculate freelance hourly rate",
        "what should i charge as a freelancer", "freelance rate calculator",
        "how much should i charge per hour freelance", "freelance pricing calculator",
        "minimum hourly rate freelancer", "break even rate calculator freelance",
        "how to work out your freelance day rate", "billable hours calculator freelance",
        "freelance rate formula", "how many hours can a freelancer bill",
        "freelance utilisation rate", "what is a good freelance hourly rate",
        "freelance rate too low", "how to calculate a day rate from a salary",
    ]),
    ("/tools/self-employment-tax-calculator.html", "us se tax", [
        "self employment tax calculator", "how much self employment tax do i owe",
        "15.3 percent self employment tax", "schedule se calculator",
        "self employment tax on 1099 income", "social security tax self employed",
        "medicare tax self employed", "self employment tax deduction calculator",
        "92.35 percent self employment tax", "additional medicare tax calculator",
        "social security wage base self employed", "do i pay self employment tax on a loss",
        "self employment tax vs income tax", "1099 tax calculator",
        "how much tax does a 1099 contractor pay", "s corp vs sole proprietor tax savings",
    ]),
    ("/tools/invoice-late-fee-calculator.html", "late payment", [
        "invoice late fee calculator", "late payment interest calculator",
        "how to calculate late fees on an invoice", "1.5 percent per month late fee",
        "statutory interest calculator uk", "late payment of commercial debts interest",
        "late payment compensation uk", "can i charge interest on an overdue invoice",
        "how much late fee can i charge", "overdue invoice interest rate",
        "freelance late payment fee", "what to do when a client doesn't pay",
        "demand letter for unpaid invoice", "late fee clause for contracts",
    ]),
    ("/tools/project-quote-calculator.html", "quoting", [
        "project quote calculator", "how to quote a freelance project",
        "fixed price project calculator", "how much deposit should i ask for",
        "how to price a project instead of hourly", "project pricing calculator freelance",
        "rush fee percentage freelance", "revision buffer pricing",
        "how to estimate project hours", "scope creep pricing",
        "freelance proposal pricing", "how to quote a website build",
    ]),
    ("/tools/freelance-take-home-pay-calculator.html", "take home", [
        "freelance take home pay calculator", "what do freelancers actually keep",
        "self employed take home pay", "1099 take home pay calculator",
        "freelance net income calculator", "contractor take home pay",
        "effective tax rate calculator self employed", "freelance income after tax",
        "is freelancing worth it financially", "freelance vs salary comparison",
    ]),
    ("/tools/quarterly-tax-savings-calculator.html", "set aside", [
        "quarterly tax calculator self employed", "how much to set aside for taxes freelance",
        "estimated tax payment calculator", "what percentage to save for taxes self employed",
        "safe harbor rule estimated taxes", "quarterly tax deadlines",
        "how much should i save from each invoice for tax", "underpayment penalty calculator",
        "freelance tax savings account", "do i have to pay quarterly taxes",
    ]),
    ("/tools/salary-to-freelance-rate-converter.html", "salary convert", [
        "salary to hourly rate converter freelance", "what freelance rate equals my salary",
        "convert salary to contract rate", "employee vs freelance rate comparison",
        "how much more should a contractor charge than an employee",
        "true cost of an employee calculator", "salary to day rate converter",
        "should i double my salary as a freelancer", "contractor rate vs salary calculator",
    ]),
    ("/tools/vat-sales-tax-calculator.html", "vat general", [
        "vat calculator", "sales tax calculator", "gst calculator",
        "how to remove vat from a price", "how to add vat to a price",
        "reverse vat calculator", "vat inclusive vs exclusive",
        "divide by 1.2 to remove vat", "net to gross calculator tax",
        "gross to net price calculator",
    ]),
    ("/tools/profit-margin-calculator.html", "margin", [
        "profit margin calculator", "markup calculator",
        "margin vs markup difference", "how to convert markup to margin",
        "how to price for a 50 percent margin", "selling price calculator from cost",
        "gross margin calculator", "what profit margin should a freelancer have",
        "cost plus pricing calculator", "how to calculate profit on a project",
    ]),
]
for page, cluster, keys in CORE:
    for k in keys:
        add(k, cluster, "transactional" if "calculator" in k else "informational", page, 1)

# ---------------------------------------------------------------- modifiers
MODIFIERS = ["free", "online", "simple", "uk", "usa", "australia", "canada",
             "for freelancers", "for small business", "for self employed", "with examples"]
base_rows = [r for r in rows if r["tier"] == 1 and "calculator" in r["keyword"]]
for r in base_rows:
    for m in MODIFIERS:
        add(f"{r['keyword']} {m}", r["cluster"], r["intent"], r["target_page"], 2)

# ---------------------------------------------------------------- guides
GUIDE_KEYS = [
    "how to raise freelance rates", "freelance rate increase email template",
    "how to handle scope creep", "freelance contract essentials",
    "retainer vs project pricing", "how to fire a client politely",
    "freelance emergency fund how much", "irregular income budgeting",
    "first year freelancing checklist", "freelance business expenses list",
    "sole trader vs limited company", "do freelancers need insurance",
    "how to chase an unpaid invoice", "freelance payment terms explained",
    "should freelancers take a deposit", "how to say no to a client",
    "freelance pricing mistakes", "why hourly billing caps your income",
]
for k in GUIDE_KEYS:
    add(k, "guides", "informational", "/guides/", 2)
    for m in ["uk", "usa", "2026", "for beginners", "template"]:
        add(f"{k} {m}", "guides", "informational", "/guides/", 3)

rows.sort(key=lambda r: (r["tier"], r["cluster"], r["keyword"]))
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["keyword", "cluster", "intent", "target_page", "tier"])
    w.writeheader()
    w.writerows(rows)

tiers = {}
for r in rows:
    tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
print(f"{len(rows)} keywords written to {OUT.relative_to(ROOT)}")
for t in sorted(tiers):
    label = {1: "page exists", 2: "page planned", 3: "needs a new page"}[t]
    print(f"  tier {t} ({label}): {tiers[t]}")

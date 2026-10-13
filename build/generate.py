#!/usr/bin/env python3
"""Static site generator for FreelanceFigures.

Renders every page in ../docs from the definitions below. Run it after
editing content:  python3 build/generate.py
"""
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"

SITE_NAME = "FreelanceFigures"
DOMAIN = "https://freelancefigures.com"
TAGLINE = "Free money calculators for freelancers and small businesses"

NAV = [
    ("Tools", "/#tools"),
    ("Guides", "/#guides"),
    ("About", "/about.html"),
    ("Contact", "/contact.html"),
]


def head(title, desc, path, schemas=(), scripts=()):
    canonical = DOMAIN + path
    s = "\n".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(x, separators=(",", ":"))
        for x in schemas
    )
    extra = "\n".join('<script src="/assets/js/%s" defer></script>' % x for x in scripts)
    depth = path.count("/") - 1
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/css/main.css">
<script src="/assets/js/theme-init.js"></script>
<script src="/assets/js/site.js" defer></script>
{extra}
{s}
</head>
<body>
"""


def header(current=""):
    links = "\n".join(
        '<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if label == current else "", label)
        for label, href in NAV
    )
    return f"""<header class="site-head">
<div class="wrap head-row">
<a class="logo" href="/"><span class="logo-mark" aria-hidden="true">FF</span>{SITE_NAME}</a>
<button class="menu-btn" aria-label="Open menu" aria-expanded="false">&#9776;</button>
<nav class="nav" aria-label="Main">
{links}
</nav>
<button class="theme-btn" type="button" aria-label="Switch theme">&#9790;</button>
</div>
</header>
<main>
"""


def ad(slot_id, fmt="auto"):
    return (
        f'<div class="ad-slot" data-slot="{slot_id}" data-format="{fmt}">'
        f'<div class="ad-label">Advertisement</div></div>'
    )


def footer(tools):
    tool_links = "\n".join(
        '<li><a href="/tools/%s.html">%s</a></li>' % (t["slug"], t["nav"]) for t in tools
    )
    return f"""</main>
<footer class="site-foot">
<div class="wrap">
<div class="foot-grid">
<div>
<a class="logo" href="/"><span class="logo-mark" aria-hidden="true">FF</span>{SITE_NAME}</a>
<p style="color:var(--text-mute);margin:10px 0 0;max-width:38ch;font-size:14.5px;">
{TAGLINE}. No sign-up, no paywall, nothing leaves your browser.</p>
</div>
<div>
<h4>Calculators</h4>
<ul>
{tool_links}
</ul>
</div>
<div>
<h4>Site</h4>
<ul>
<li><a href="/about.html">About</a></li>
<li><a href="/contact.html">Contact</a></li>
<li><a href="/privacy.html">Privacy policy</a></li>
<li><a href="/terms.html">Terms of use</a></li>
<li><a href="/disclaimer.html">Disclaimer</a></li>
</ul>
</div>
</div>
<div class="foot-bottom">
<span>&copy; 2026 {SITE_NAME}. All rights reserved.</span>
<span>Figures are estimates, not professional tax advice.</span>
</div>
</div>
</footer>
</body>
</html>
"""


def write(path, content):
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def faq_block(faqs):
    items = "\n".join(
        f"""<details class="faq"><summary>{q}</summary><div class="faq-body">{a}</div></details>"""
        for q, a in faqs
    )
    return f"""<section class="prose">
<h2>Frequently asked questions</h2>
{items}
</section>"""


def faq_schema(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)},
            }
            for q, a in faqs
        ],
    }


def strip_tags(html):
    out, depth = [], 0
    for ch in html:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out).strip()


def currency_field():
    opts = [
        ("USD", "USD &ndash; US dollar"),
        ("EUR", "EUR &ndash; Euro"),
        ("GBP", "GBP &ndash; British pound"),
        ("CAD", "CAD &ndash; Canadian dollar"),
        ("AUD", "AUD &ndash; Australian dollar"),
        ("NZD", "NZD &ndash; New Zealand dollar"),
        ("SGD", "SGD &ndash; Singapore dollar"),
        ("AED", "AED &ndash; UAE dirham"),
        ("INR", "INR &ndash; Indian rupee"),
        ("PKR", "PKR &ndash; Pakistani rupee"),
        ("ZAR", "ZAR &ndash; South African rand"),
    ]
    o = "\n".join(f'<option value="{c}">{n}</option>' for c, n in opts)
    return f"""<div class="field">
<label for="currency">Currency</label>
<select id="currency" name="currency">
{o}
</select>
</div>"""


def field(fid, label, hint="", pre="", post="", value="", ftype="number", step="any",
          minimum="0", wrapper_id="", select=None, extra=""):
    hint_html = f'<span class="hint">{hint}</span>' if hint else ""
    if select is not None:
        opts = "\n".join(
            f'<option value="{v}"{" selected" if sel else ""}>{t}</option>' for v, t, sel in select
        )
        control = f'<select id="{fid}" name="{fid}">\n{opts}\n</select>'
    else:
        attrs = f'type="{ftype}"'
        if ftype == "number":
            attrs += f' step="{step}" min="{minimum}" inputmode="decimal"'
        if value != "":
            attrs += f' value="{value}"'
        control = f'<input id="{fid}" name="{fid}" {attrs}{extra}>'
    if pre or post:
        pre_html = f'<span class="affix pre">{pre}</span>' if pre else ""
        post_html = f'<span class="affix post">{post}</span>' if post else ""
        control = f'<div class="input-wrap">{pre_html}{control}{post_html}</div>'
    wid = f' id="{wrapper_id}"' if wrapper_id else ""
    return f'<div class="field"{wid}><label for="{fid}">{label}</label>{hint_html}{control}</div>'


def pill(label, vid):
    return f'<div class="pill"><div class="k">{label}</div><div class="v" id="{vid}">&mdash;</div></div>'


def result_shell(headline_label, sub_id, headline_id, pills, table_rows, foot=""):
    pill_html = "\n".join(pills)
    rows = "\n".join(table_rows)
    return f"""<div class="result" id="result" hidden>
<div class="headline-label">{headline_label}</div>
<div class="headline" id="{headline_id}">&mdash;</div>
<p class="headline-sub" id="{sub_id}"></p>
<div class="pill-row">
{pill_html}
</div>
<table class="breakdown">
{rows}
</table>
{foot}
</div>"""


def row(label, vid, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<tr{c}><td>{label}</td><td id="{vid}">&mdash;</td></tr>'


TOOLS = []

# ---------------------------------------------------------------- tool 1
TOOLS.append(dict(
    slug="freelance-hourly-rate-calculator",
    nav="Freelance hourly rate",
    script="tool-hourly-rate.js",
    title="Freelance Hourly Rate Calculator &mdash; What Should You Charge?",
    meta_title="Freelance Hourly Rate Calculator | What Should You Charge?",
    meta_desc="Work out the hourly rate you actually need to charge as a freelancer, "
              "after tax, business expenses, unpaid time off and non-billable hours. Free, instant, no sign-up.",
    h1="Freelance Hourly Rate Calculator",
    intro="Most freelancers pick a rate by copying someone else, then wonder why the money never "
          "adds up. This calculator works backwards from the life you want: the income you need to "
          "take home, the costs of running your business, and the honest number of hours you can "
          "actually bill.",
    card="Work backwards from the income you want to the rate you must charge.",
    form=[
        field("targetIncome", "Income you want to take home", "After tax, per year. The money that reaches your personal account.", pre="$", value="60000"),
        field("expenses", "Annual business expenses", "Software, hardware, insurance, accountant, coworking, marketing.", pre="$", value="6000"),
        '<div class="row2">'
        + field("billableHours", "Billable hours per week", "Be honest. Most full-time freelancers bill 20&ndash;25.", post="hrs", value="25")
        + field("taxRate", "Estimated tax rate", "Income tax plus self-employment / national insurance.", post="%", value="28")
        + "</div>",
        '<div class="row2">'
        + field("vacationWeeks", "Weeks of holiday per year", "Unpaid — you earn nothing these weeks.", post="wks", value="4")
        + field("holidayDays", "Public holidays per year", "", post="days", value="8")
        + "</div>",
        '<div class="row2">'
        + field("sickDays", "Sick / buffer days", "Days you will lose to illness and life.", post="days", value="5")
        + field("profitMargin", "Profit buffer", "A cushion for bad debts, scope creep and reinvestment.", post="%", value="10")
        + "</div>",
        currency_field(),
    ],
    result=result_shell(
        "Your minimum hourly rate", "outSub", "outRate",
        [pill("Day rate (8 hrs)", "outDay"), pill("Week rate", "outWeek"),
         pill("Monthly revenue", "outMonth"), pill("Billable hours / yr", "outHours")],
        [row("Take-home income target", "bTarget"),
         row("Tax to cover on top", "bTaxUp"),
         row("Business expenses", "bExpenses"),
         row("Profit buffer", "bProfit"),
         row("Revenue you must invoice", "bTotal", "total"),
         row("Working weeks per year", "bWeeks", "sub"),
         row("Utilisation", "bUtil", "sub"),
         row("Break-even rate (no profit buffer)", "bMin", "sub")],
    ),
    prose="""
<h2>How this calculator works</h2>
<p>The arithmetic that sinks most freelancers is simple: they divide the salary they used to earn
by 2,080 hours and call it a rate. That number is always too low, for three reasons. An employer
pays for your holidays, your sick days and the hours you spend in meetings that nobody invoices.
When you work for yourself, you pay for all of it.</p>
<p>So this tool runs the calculation in the order money actually moves:</p>
<ol>
<li><strong>Start with take-home pay.</strong> The income figure you enter is what you want to keep,
not what you want to invoice.</li>
<li><strong>Gross it up for tax.</strong> If you want to keep $60,000 and lose 28% to tax, you need
$60,000 &divide; 0.72 = $83,333 of taxable profit, not $76,800. Grossing up and discounting are not
the same operation, and this is where most back-of-envelope sums go wrong.</li>
<li><strong>Add business expenses.</strong> Your laptop, your accountant and your insurance come out
of revenue, so revenue has to cover them.</li>
<li><strong>Add a profit buffer.</strong> Some invoices get paid late, some never get paid, and some
projects run 20% over. A 10% cushion is not greed, it is survival.</li>
<li><strong>Divide by hours you can really bill.</strong> Not 40 a week. After holidays, public
holidays, sick days, admin, sales calls, proposals and invoicing, 25 billable hours in a 40-hour
week is a good week.</li>
</ol>

<h2>The formula</h2>
<div class="note">
<p><strong>Billable hours per year</strong> = weekly billable hours &times; (52 &minus; holiday weeks
&minus; public holidays &divide; 5 &minus; sick days &divide; 5)</p>
<p><strong>Revenue needed</strong> = (take-home &divide; (1 &minus; tax rate)) + expenses</p>
<p><strong>Hourly rate</strong> = revenue needed &times; (1 + profit buffer) &divide; billable hours</p>
</div>

<h2>A worked example</h2>
<p>Say you want $60,000 in your pocket, you spend $6,000 a year running the business, you lose 28%
to tax, and you can bill 25 hours a week. You take four weeks off, eight public holidays and allow
five sick days.</p>
<table>
<tr><th>Step</th><th>Figure</th></tr>
<tr><td>Working weeks</td><td>52 &minus; 4 &minus; 1.6 &minus; 1 = 45.4 weeks</td></tr>
<tr><td>Billable hours</td><td>25 &times; 45.4 = 1,135 hours</td></tr>
<tr><td>Revenue for take-home</td><td>$60,000 &divide; 0.72 = $83,333</td></tr>
<tr><td>Plus expenses</td><td>$89,333</td></tr>
<tr><td>Plus 10% buffer</td><td>$98,267</td></tr>
<tr><td><strong>Hourly rate</strong></td><td><strong>$86.58 &rarr; quote $90</strong></td></tr>
</table>
<p>If you had used the naive method &mdash; $60,000 &divide; 2,080 &mdash; you would have charged
$28.85 an hour and gone out of business inside two years.</p>

<h2>What to do with the number</h2>
<p>Treat it as a floor, not a ceiling. It is the rate below which you are subsidising your clients.
Three things to remember when you quote it:</p>
<ul>
<li><strong>Round up, never down.</strong> $86.58 becomes $90. No client has ever walked away over 4%,
and an odd number looks like you are negotiating against yourself.</li>
<li><strong>Quote projects, not hours, once you can.</strong> Hourly billing punishes you for getting
faster. Use this rate to price the project, then quote the project.</li>
<li><strong>Raise it every year.</strong> Your costs rise. If your rate does not, you take a pay cut
annually without noticing.</li>
</ul>
<p>Once you have a rate, run it through the <a href="/tools/project-quote-calculator.html">project quote
calculator</a> to turn it into a fixed price, and the
<a href="/tools/freelance-take-home-pay-calculator.html">take-home pay calculator</a> to check what
actually lands in your account.</p>
""",
    faqs=[
        ("What is a realistic number of billable hours per week?",
         "<p>Between 20 and 27 for most full-time freelancers. The rest of a 40-hour week goes to "
         "proposals, invoicing, email, bookkeeping, marketing and learning. Agencies plan for 60&ndash;70% "
         "utilisation on salaried staff and they have administrators; a solo freelancer doing their own "
         "admin should not plan for more.</p>"),
        ("Should I charge the same rate to every client?",
         "<p>No. The figure here is your minimum. Rush work, difficult stakeholders, unclear scope and "
         "high-stakes projects all justify a premium, and the calculator has a rush and complexity "
         "multiplier in the project quote tool for exactly that. What should never happen is going "
         "<em>below</em> this number, because then the work costs you money to do.</p>"),
        ("Does this work outside the United States?",
         "<p>Yes. The maths is country-neutral &mdash; pick your currency and enter your own combined tax "
         "rate. A UK sole trader would enter income tax plus Class 4 National Insurance; a German "
         "freelancer would enter Einkommensteuer plus their health insurance contribution; a Canadian "
         "would enter federal plus provincial plus CPP.</p>"),
        ("Why does the calculator add a profit buffer on top of my salary?",
         "<p>Because your salary is a cost of the business, not its profit. The buffer is what absorbs "
         "the invoice that gets paid 90 days late, the client that disappears, the project that runs "
         "over, and the new laptop you did not budget for. Freelancers who skip it end up funding those "
         "events out of their own take-home pay.</p>"),
        ("Is my data sent anywhere?",
         "<p>No. Every calculation on this site runs in your browser with JavaScript. Nothing you type "
         "is uploaded, stored or logged by us.</p>"),
    ],
))

# ---------------------------------------------------------------- tool 2
TOOLS.append(dict(
    slug="self-employment-tax-calculator",
    nav="Self-employment tax (US)",
    script="tool-se-tax.js",
    title="Self-Employment Tax Calculator &mdash; Social Security &amp; Medicare",
    meta_title="Self-Employment Tax Calculator | Social Security + Medicare",
    meta_desc="Calculate the 15.3% US self-employment tax on your net profit, including the "
              "Social Security wage cap, Additional Medicare tax and your quarterly payment. Free and instant.",
    h1="Self-Employment Tax Calculator",
    intro="If you are self-employed in the United States you pay both halves of Social Security and "
          "Medicare &mdash; 15.3% &mdash; before a single dollar of income tax is worked out. This "
          "calculator applies the 92.35% adjustment, the Social Security wage cap and the Additional "
          "Medicare surtax, and shows what to send the IRS each quarter.",
    card="The 15.3% you owe before income tax, with the wage cap applied properly.",
    form=[
        field("netProfit", "Net profit from self-employment",
              "Business income minus deductible business expenses &mdash; the bottom line of Schedule C.",
              pre="$", value="80000"),
        field("w2Wages", "W-2 wages from a job (if any)",
              "Wages already taxed for Social Security this year. These use up the wage cap first.",
              pre="$", value="0"),
        field("filingStatus", "Filing status", "Sets the Additional Medicare threshold.", select=[
            ("single", "Single", True),
            ("mfj", "Married filing jointly", False),
            ("mfs", "Married filing separately", False),
            ("hoh", "Head of household", False),
        ]),
        '<div class="row2">'
        + field("wageBase", "Social Security wage base",
                "Set by the SSA each year &mdash; check the current figure and edit if needed.",
                pre="$", value="184500")
        + field("ssRate", "Social Security rate", "12.4% combined employer + employee.", post="%", value="12.4")
        + "</div>",
        field("medRate", "Medicare rate", "2.9% combined, with no upper limit.", post="%", value="2.9"),
    ],
    result=result_shell(
        "Self-employment tax owed", "outSub", "outTotal",
        [pill("Each quarter", "outQuarter"), pill("Income-tax deduction", "outDeduct"),
         pill("Effective rate", "outEff")],
        [row("Net profit", "bProfit"),
         row("&times; 92.35% = SE tax base", "bSeBase", "sub"),
         row("Subject to Social Security", "bSsTaxable", "sub"),
         row("Social Security portion", "bSs"),
         row("Medicare portion", "bMed"),
         row("Additional Medicare (0.9%)", "bAddl"),
         row("Total self-employment tax", "bTotal", "total")],
        foot='<p class="headline-sub" id="capNote" hidden></p>',
    ),
    prose="""
<h2>What self-employment tax actually is</h2>
<p>An employee and their employer each pay 7.65% of wages into Social Security and Medicare. When you
are self-employed you are both parties, so you pay the full 15.3%. This is <em>separate from and in
addition to</em> federal income tax &mdash; which is why a freelancer earning $80,000 can be shocked by
a tax bill that an employee earning $80,000 never sees.</p>
<p>It breaks into three pieces:</p>
<table>
<tr><th>Component</th><th>Rate</th><th>Applies to</th></tr>
<tr><td>Social Security (OASDI)</td><td>12.4%</td><td>Earnings up to the annual wage base, then nothing</td></tr>
<tr><td>Medicare</td><td>2.9%</td><td>Every dollar, no ceiling</td></tr>
<tr><td>Additional Medicare</td><td>0.9%</td><td>Earnings above $200k single / $250k married filing jointly</td></tr>
</table>

<h2>The 92.35% rule nobody explains</h2>
<p>You do not pay SE tax on your full net profit. You pay it on 92.35% of it. The reasoning is that an
employer's half of payroll tax is a deductible business expense, so the law gives the self-employed an
equivalent adjustment by shrinking the base. On $80,000 of profit, the taxable base is $73,880, and
15.3% of that is $11,303.64 &mdash; not $12,240.</p>
<div class="note">
<p><strong>SE tax base</strong> = net profit &times; 0.9235<br>
<strong>Social Security</strong> = min(SE base, wage base &minus; W-2 wages) &times; 12.4%<br>
<strong>Medicare</strong> = SE base &times; 2.9%<br>
<strong>Additional Medicare</strong> = (SE base + W-2 wages &minus; threshold) &times; 0.9%</p>
</div>

<h2>The wage cap, and why a side job changes your bill</h2>
<p>Social Security stops at a ceiling that the Social Security Administration resets every year. Above
it, you keep paying Medicare but the 12.4% disappears &mdash; so very high earners have a lower
<em>effective</em> SE rate than middle earners.</p>
<p>The catch that surprises people with both a job and a side business: your W-2 wages fill that cap
first. If you already earned $150,000 at a job and the cap is $184,500, only $34,500 of your freelance
profit faces Social Security tax. Enter your W-2 wages above and the calculator handles it.</p>

<h2>Half of it comes back as a deduction</h2>
<p>You can deduct one half of your self-employment tax when calculating your adjusted gross income. It
is an above-the-line deduction, so you get it whether or not you itemise. The 0.9% Additional Medicare
surtax is not deductible. The calculator shows the deductible figure separately &mdash; it typically
knocks a few hundred to a few thousand dollars off your income tax.</p>

<h2>Paying it: quarterly, not in April</h2>
<p>The IRS expects estimated payments four times a year, generally 15 April, 15 June, 15 September and
15 January. Miss them and you owe an underpayment penalty even if you pay the full amount later. The
safest approach for most freelancers is the safe-harbour rule: pay 100% of last year's total tax
(110% if your prior-year AGI was over $150,000) and you cannot be penalised, however well this year
goes.</p>
<p>Use the <a href="/tools/quarterly-tax-savings-calculator.html">quarterly set-aside calculator</a> to
work out what to move into a savings account from each invoice, and the
<a href="/tools/freelance-take-home-pay-calculator.html">take-home pay calculator</a> to see SE tax and
income tax together.</p>
""",
    faqs=[
        ("Do I owe self-employment tax if I only made a few thousand dollars?",
         "<p>You owe it once your net earnings from self-employment reach $400 for the year. Below that "
         "threshold there is no SE tax, although the income may still be reportable for income tax.</p>"),
        ("Is self-employment tax the same as income tax?",
         "<p>No, and this is the single most expensive misunderstanding in freelancing. SE tax funds "
         "Social Security and Medicare and is calculated on your business profit. Income tax is "
         "calculated separately on your taxable income after deductions. You pay both.</p>"),
        ("Does forming an S corporation reduce this?",
         "<p>It can. An S corp lets you split your profit into a reasonable salary (which pays payroll "
         "tax) and a distribution (which does not). The saving only outweighs the payroll, filing and "
         "accounting costs at a certain profit level &mdash; commonly cited as somewhere above $80,000 to "
         "$100,000 of net profit, but it depends on your state and your reasonable salary. Talk to a CPA "
         "before restructuring.</p>"),
        ("Why is the wage base an editable field?",
         "<p>Because the Social Security Administration raises it every year with average wage growth, "
         "and a hard-coded figure in a calculator goes stale the moment it changes. Check the current "
         "year's number on the SSA website and type it in &mdash; the rest of the maths adapts.</p>"),
        ("What if I had a loss this year?",
         "<p>No self-employment tax is due on a loss. The calculator needs a positive net profit to "
         "produce a figure. A business loss may offset other income for income-tax purposes, which is "
         "worth raising with a tax preparer.</p>"),
    ],
))

# ---------------------------------------------------------------- tool 3
TOOLS.append(dict(
    slug="invoice-late-fee-calculator",
    nav="Invoice late fee",
    script="tool-late-fee.js",
    title="Invoice Late Fee Calculator &mdash; Interest on Overdue Invoices",
    meta_title="Invoice Late Fee Calculator | Interest on Overdue Invoices",
    meta_desc="Calculate late payment interest and fees on an overdue invoice: monthly percentage, "
              "annual rate, flat fee, or UK statutory interest with fixed compensation. Free, instant.",
    h1="Invoice Late Fee Calculator",
    intro="An invoice that is 60 days late is a loan you did not agree to make. Work out exactly what "
          "the client owes you in interest and fees, so the figure on your reminder is a calculation "
          "rather than a guess &mdash; including UK statutory interest under the Late Payment of "
          "Commercial Debts Act.",
    card="Interest and fees on an overdue invoice, including UK statutory rates.",
    form=[
        field("invoiceAmount", "Invoice amount", "The unpaid balance, excluding any fees already added.",
              pre="$", value="2500"),
        '<div class="row2">'
        + field("dueDate", "Payment was due", "The date on the invoice, not the date you sent it.", ftype="date")
        + field("asOfDate", "Calculate up to", "Usually today, or the date you expect payment.", ftype="date")
        + "</div>",
        field("method", "Late fee method", "Use whatever your contract specifies.", select=[
            ("monthly", "Percentage per month (most common)", True),
            ("annual", "Annual interest rate", False),
            ("flat", "Flat fee only", False),
            ("flatmonthly", "Flat fee + monthly percentage", False),
            ("uk", "UK statutory interest (base + 8%)", False),
        ]),
        field("monthlyRate", "Monthly late fee rate", "1.5% per month (18% a year) is the common contract term.",
              post="%", value="1.5", wrapper_id="f-monthly"),
        field("proration", "How to count part months", "", wrapper_id="f-proration", select=[
            ("daily", "Prorate daily (fairer, harder to argue with)", True),
            ("month", "Charge a full month once a month starts", False),
        ]),
        field("annualRate", "Annual interest rate", "", post="%", value="8", wrapper_id="f-annual"),
        field("flatFee", "Flat late fee", "", pre="$", value="50", wrapper_id="f-flat"),
        field("ukBaseRate", "Bank of England base rate",
              "Statutory interest is the base rate plus 8%. Check the current base rate and edit.",
              post="%", value="4.0", wrapper_id="f-ukbase"),
        currency_field(),
    ],
    result=result_shell(
        "Total now owed", "outSub", "outTotal",
        [pill("Days overdue", "outDays"), pill("Interest per day", "outPerDay"),
         pill("Late charges", "outFee")],
        [row("Original invoice", "bAmount"),
         row("Flat fee / compensation", "bFlat"),
         row("Interest", "bInterest"),
         row("Total payable", "bTotal", "total"),
         row("Method", "bLabel", "sub"),
         row("Calculated over", "bBasis", "sub")],
    ),
    prose="""
<h2>Can you actually charge a late fee?</h2>
<p>In most countries, yes &mdash; but only if you can point to a term the client agreed to, or to a
statute. Three routes exist, and they are not equally strong:</p>
<ul>
<li><strong>Your contract or your invoice terms.</strong> The strongest position. A line such as
&ldquo;overdue amounts accrue interest at 1.5% per month&rdquo; in a signed agreement is enforceable in
most jurisdictions. A line that appears for the first time on the invoice is weaker, because the client
never agreed to it, but it is still worth having.</li>
<li><strong>Statute.</strong> Several countries give you a right to interest even with no contract term
at all. The UK's Late Payment of Commercial Debts (Interest) Act and the EU Late Payment Directive both
do this for business-to-business debts.</li>
<li><strong>Nothing in writing anywhere.</strong> You can still ask, and clients often pay to keep the
relationship. You just have little leverage if they refuse.</li>
</ul>

<h2>The three ways to calculate it</h2>
<h3>Monthly percentage</h3>
<p>The freelancer standard: 1.5% per month, which is 18% a year. On a $2,500 invoice that is $37.50 a
month, or $1.23 a day. Decide whether a part month counts as a whole month &mdash; charging a full
month's interest on day 31 is legal if your terms say so, but prorating daily is much harder for a
client to argue with, and this calculator does either.</p>
<h3>Annual rate</h3>
<p>Interest &times; days &divide; 365. Used where contracts quote an annual figure, and the basis for
almost every statutory scheme.</p>
<h3>UK statutory interest</h3>
<p>For business-to-business debts, the rate is the Bank of England base rate plus 8 percentage points,
calculated daily. You can also claim fixed compensation on top, as a flat sum per invoice:</p>
<table>
<tr><th>Debt size</th><th>Fixed compensation</th></tr>
<tr><td>Up to &pound;999.99</td><td>&pound;40</td></tr>
<tr><td>&pound;1,000 to &pound;9,999.99</td><td>&pound;70</td></tr>
<tr><td>&pound;10,000 or more</td><td>&pound;100</td></tr>
</table>
<p>Select the UK statutory option above and the calculator applies the right compensation band and
daily interest automatically.</p>

<h2>A worked example</h2>
<p>A $2,500 invoice, due 1 March, still unpaid on 14 May &mdash; 74 days late, with 1.5% per month in
the contract:</p>
<table>
<tr><th>Step</th><th>Figure</th></tr>
<tr><td>Months overdue (prorated)</td><td>74 &divide; 30 = 2.47 months</td></tr>
<tr><td>Interest</td><td>$2,500 &times; 1.5% &times; 2.47 = $92.50</td></tr>
<tr><td><strong>Total payable</strong></td><td><strong>$2,592.50</strong></td></tr>
</table>

<h2>Getting paid, not just getting owed</h2>
<p>The fee is leverage, not income. Freelancers who get paid fastest tend to do the same four things:</p>
<ol>
<li><strong>Put the term in the contract</strong>, not just the invoice, and say it out loud at kickoff
so it is never a surprise.</li>
<li><strong>Chase on day one, politely.</strong> Most late payments are an unopened email or a missing
purchase-order number, not a refusal to pay.</li>
<li><strong>Send the calculation, not a complaint.</strong> &ldquo;As of today the balance is $2,592.50,
including $92.50 of contractual interest&rdquo; moves an invoice up the queue in a way that
&ldquo;just checking in&rdquo; never does.</li>
<li><strong>Take a deposit next time.</strong> The <a href="/tools/project-quote-calculator.html">project
quote calculator</a> works out a deposit amount for you. A client who will not pay 40% up front is
telling you something useful.</li>
</ol>
""",
    faqs=[
        ("What is a reasonable late fee percentage?",
         "<p>1% to 1.5% per month is the usual range for freelancers and small agencies, equal to 12% to "
         "18% a year. Going much higher risks a court treating the term as a penalty rather than genuine "
         "compensation, which can make it unenforceable. Some US states also cap the interest a business "
         "may charge, so check your state's usury rules before writing 2% or more into a contract.</p>"),
        ("Do I charge the late fee on the invoice total including sales tax or VAT?",
         "<p>Normally yes &mdash; the client owes the gross amount, so interest runs on the gross amount. "
         "Under the UK statutory scheme interest runs on the full debt including VAT. The fee itself is "
         "generally treated as compensation rather than a supply, so you usually do not add VAT to the "
         "interest; confirm with your accountant for your country.</p>"),
        ("When does the clock start?",
         "<p>The day after the payment due date, not the invoice date. If your terms are net 30 and you "
         "invoiced on 1 March, payment is due 31 March and interest starts 1 April. Where no terms were "
         "agreed, many jurisdictions default to 30 days after the client received the invoice or the "
         "goods, whichever is later.</p>"),
        ("Should I waive the fee if the client finally pays?",
         "<p>Often, yes &mdash; and say so explicitly: &ldquo;I have waived the $92.50 interest this "
         "time.&rdquo; You keep the relationship, and you have established that the fee is real, which "
         "makes it credible the next time. Waiving it silently teaches the client that the term is "
         "decorative.</p>"),
        ("Is this legal advice?",
         "<p>No. This is a calculator and a general explanation. Late payment rules vary by country, "
         "state and contract, and nothing here is a substitute for advice from a lawyer in your "
         "jurisdiction.</p>"),
    ],
))

# ---------------------------------------------------------------- tool 4
TOOLS.append(dict(
    slug="project-quote-calculator",
    nav="Project quote",
    script="tool-quote.js",
    title="Project Quote Calculator &mdash; Price a Fixed-Fee Project",
    meta_title="Project Quote Calculator | Price a Fixed-Fee Project",
    meta_desc="Turn an hours estimate into a fixed project price with complexity, revisions, rush fees, "
              "expenses, discount, tax and a deposit figure. Free quoting calculator for freelancers.",
    h1="Project Quote Calculator",
    intro="Hourly billing punishes you for being good at your job: the faster you work, the less you "
          "earn. Fixed-fee quoting fixes that &mdash; but only if the number covers revisions, scope "
          "creep and the parts of the job nobody mentioned in the brief. This builds that number.",
    card="Turn an hours estimate into a defensible fixed price, with a deposit figure.",
    form=[
        '<div class="row2">'
        + field("hours", "Estimated hours", "Your honest best estimate of focused working time.", post="hrs", value="40")
        + field("rate", "Your hourly rate", "Not sure? Use the hourly rate calculator first.", pre="$", value="90")
        + "</div>",
        field("complexity", "Complexity multiplier", "How much harder than routine work is this?", select=[
            ("1", "1.00 &times; &mdash; routine work you have done many times", False),
            ("1.25", "1.25 &times; &mdash; some unfamiliar elements", True),
            ("1.5", "1.50 &times; &mdash; new domain, unclear brief, many stakeholders", False),
            ("2", "2.00 &times; &mdash; high risk, legacy mess, or difficult client", False),
        ]),
        '<div class="row2">'
        + field("revisionBuffer", "Revision buffer", "Rounds of feedback always cost more than you think.", post="%", value="20")
        + field("rushFee", "Rush fee", "Charge for displacing other work and for evenings.", post="%", value="0")
        + "</div>",
        '<div class="row2">'
        + field("expenses", "Pass-through expenses", "Stock photos, fonts, hosting, plugins, travel.", pre="$", value="0")
        + field("discount", "Discount", "Long contracts or a retainer may earn one. Nothing else should.", post="%", value="0")
        + "</div>",
        '<div class="row2">'
        + field("taxRate", "Sales tax / VAT / GST", "Added on top of the quote if you are registered.", post="%", value="0")
        + field("depositPct", "Deposit required", "40&ndash;50% up front is normal and protects you.", post="%", value="40")
        + "</div>",
        currency_field(),
    ],
    result=result_shell(
        "Quote this price", "outSub", "outTotal",
        [pill("Deposit up front", "outDeposit"), pill("Balance on delivery", "outBalance"),
         pill("Effective hourly", "outEffective"), pill("Realistic hours", "outHours")],
        [row("Base work", "bBase"),
         row("", "bBaseNote", "sub"),
         row("Revision buffer", "bRev"),
         row("Rush premium", "bRush"),
         row("Expenses", "bExp"),
         row("Subtotal", "bSub"),
         row("Discount", "bDisc"),
         row("Tax / VAT", "bTax"),
         row("Total quote", "bTotal", "total")],
    ),
    prose="""
<h2>Why hours &times; rate is not a quote</h2>
<p>An estimate of 40 hours at $90 gives you $3,600. Then the client asks for a third round of changes,
the brand assets arrive in the wrong format, and two stakeholders disagree about the homepage. You
deliver in 58 hours and earned $62 an hour, not $90.</p>
<p>A quote is not a prediction of hours. It is a price for an outcome, carrying the risk that the
outcome takes longer than planned. Everything this calculator adds on top of base hours is a price for
that risk.</p>

<h2>What each input is doing</h2>
<h3>Complexity multiplier</h3>
<p>Work you have done fifty times is genuinely cheaper for you to deliver than work you have never done.
Unfamiliar domains, legacy systems, five-stakeholder approval chains and vague briefs all inflate the
real hours in ways your estimate cannot see. Be honest here &mdash; it is the single biggest lever on
whether a project is profitable.</p>
<h3>Revision buffer</h3>
<p>Twenty percent is a sensible default for two rounds of feedback. If you have not written a revision
limit into your contract, use more. The sentence that saves careers is: <em>&ldquo;The quote includes
two rounds of revisions; further rounds are billed at my hourly rate.&rdquo;</em></p>
<h3>Rush fee</h3>
<p>A rush job is not just overtime, it is displacement &mdash; you are pushing other clients back to fit
it in. 25% to 50% is standard. Charging nothing teaches clients that your calendar is free.</p>
<h3>Deposit</h3>
<p>Forty to fifty percent before work starts is normal professional practice, not an insult. It funds
the work, it filters out clients who were never going to pay, and it means a disappearing client costs
you half a project rather than all of it. If an invoice does go unpaid, the
<a href="/tools/invoice-late-fee-calculator.html">late fee calculator</a> works out what they owe.</p>

<h2>A worked example</h2>
<p>A 40-hour website build at $90 an hour, somewhat unfamiliar (1.25&times;), with a 20% revision buffer
and $200 of stock assets:</p>
<table>
<tr><th>Line</th><th>Amount</th></tr>
<tr><td>Base: 40 &times; $90 &times; 1.25</td><td>$4,500</td></tr>
<tr><td>Revision buffer (20%)</td><td>$900</td></tr>
<tr><td>Expenses</td><td>$200</td></tr>
<tr><td><strong>Quote</strong></td><td><strong>$5,600</strong></td></tr>
<tr><td>Deposit at 40%</td><td>$2,240</td></tr>
</table>
<p>Note the effective hourly figure the calculator shows. It is the rate you earn if the pessimistic
case happens &mdash; complexity and revisions both land in full. If that number is below your target
rate, the quote is too low no matter how good $5,600 sounds.</p>

<h2>How to present it</h2>
<ul>
<li><strong>Send one number.</strong> An itemised breakdown invites line-by-line negotiation. Keep the
breakdown for yourself.</li>
<li><strong>Offer three options, not one price.</strong> A reduced scope, the recommended scope and an
expanded scope. Clients who are given three options choose between them instead of choosing whether to
hire you.</li>
<li><strong>Never discount without removing scope.</strong> If the price drops, something must come out.
Otherwise you have taught the client that your first number was not real.</li>
<li><strong>Put the expiry date on it.</strong> &ldquo;This quote is valid for 30 days&rdquo; prevents a
client from accepting last spring's price next autumn.</li>
</ul>
""",
    faqs=[
        ("Should I show the client my hourly rate?",
         "<p>Generally no. Once a client knows your hourly rate, every conversation becomes about hours "
         "rather than outcomes, and efficiency starts to look like overcharging. Quote the project. Keep "
         "the rate as the private tool you use to check the quote is worth doing.</p>"),
        ("What if I estimate the hours badly?",
         "<p>Everyone does, almost always downward. Two defences: the complexity multiplier here, and a "
         "written scope that says exactly what is included. Over time, track actual hours against your "
         "estimates &mdash; most freelancers find a personal correction factor somewhere between 1.3 and "
         "1.8 and start applying it automatically.</p>"),
        ("Is a 40% deposit really normal?",
         "<p>Yes, across design, development, writing and consulting. Common structures are 50/50, "
         "40/30/30 across milestones, or 30% up front with monthly billing on longer engagements. The "
         "clients who object loudest to deposits are, reliably, the clients who later pay late.</p>"),
        ("How do I handle scope creep after the quote is accepted?",
         "<p>With a change order, not with resentment. &ldquo;Happy to add that &mdash; it is about six "
         "hours, so $540, and it moves delivery to the 14th. Shall I send a revised quote?&rdquo; Said "
         "early and without drama, this almost never damages a relationship; silently absorbing the work "
         "always damages the project.</p>"),
        ("Does the calculator store my quotes?",
         "<p>No. Everything runs in your browser and disappears when you close the tab. Use the copy "
         "button to paste the breakdown into your own notes or proposal.</p>"),
    ],
))

# ---------------------------------------------------------------- tool 5
TOOLS.append(dict(
    slug="freelance-take-home-pay-calculator",
    nav="Freelance take-home pay",
    script="tool-take-home.js",
    title="Freelance Take-Home Pay Calculator &mdash; What You Actually Keep",
    meta_title="Freelance Take-Home Pay Calculator | What You Actually Keep",
    meta_desc="See what you really keep from freelance revenue after business expenses, self-employment "
              "tax, income tax, retirement contributions and health insurance. Free monthly take-home calculator.",
    h1="Freelance Take-Home Pay Calculator",
    intro="Invoicing $120,000 does not mean earning $120,000. Between business costs, self-employment "
          "tax, income tax, retirement savings and your own health insurance, the number that reaches "
          "your personal account is a different animal entirely. This shows you which one.",
    card="From invoiced revenue to the money that actually reaches your account.",
    form=[
        '<div class="row2">'
        + field("grossRevenue", "Revenue you will invoice", "Everything clients pay you this year.", pre="$", value="120000")
        + field("businessExpenses", "Business expenses", "Software, equipment, insurance, travel, fees.", pre="$", value="15000")
        + "</div>",
        '<div class="row2">'
        + field("seRate", "Self-employment / social tax", "US: 15.3%. UK Class 4: ~6%. Edit for your country.", post="%", value="15.3")
        + field("federalRate", "Income tax rate", "Your effective rate, not your top bracket.", post="%", value="16")
        + "</div>",
        '<div class="row2">'
        + field("stateRate", "State / provincial / local tax", "Zero in nine US states. Enter 0 if it does not apply.", post="%", value="5")
        + field("retirementPct", "Retirement contribution", "Still your money &mdash; just not spendable today.", post="%", value="10")
        + "</div>",
        field("healthMonthly", "Health insurance per month", "The premium an employer would otherwise pay for you.", pre="$", value="450"),
        currency_field(),
    ],
    result=result_shell(
        "Take-home per month", "outSub", "outMonthly",
        [pill("Take-home per year", "outYear"), pill("Total tax", "outTax"),
         pill("Effective tax rate", "outEff"), pill("Into retirement", "outRetire")],
        [row("Revenue invoiced", "bGross"),
         row("Business expenses", "bExp"),
         row("Net profit", "bNet", "total"),
         row("Self-employment tax", "bSe"),
         row("Income tax", "bFed"),
         row("State / local tax", "bState"),
         row("Retirement contribution", "bRetire"),
         row("Health insurance", "bHealth"),
         row("Take-home pay", "bTake", "total")],
    ),
    prose="""
<h2>The gap nobody warns you about</h2>
<p>The reason experienced freelancers tell beginners to charge double their old salary is not greed.
It is this gap. An employee sees a gross salary and a net salary, and the distance between them is tax.
A freelancer has four layers of distance:</p>
<ol>
<li><strong>Business expenses</strong> come out before anything is yours.</li>
<li><strong>Self-employment tax</strong> &mdash; you pay both the employee and employer halves of social
contributions. In the US that is 15.3% rather than 7.65%.</li>
<li><strong>Income tax</strong>, with no employer withholding it for you, which is why the bill feels
so much larger even when the rate is identical.</li>
<li><strong>Benefits you now buy yourself:</strong> health insurance, retirement, paid leave, disability
cover. An employer's contribution to these is typically worth 20&ndash;30% of salary.</li>
</ol>
<p>Run the numbers and a freelancer invoicing $120,000 commonly lands somewhere near $65,000&ndash;$72,000
of genuine take-home pay. That is a good living. It is not $120,000.</p>

<h2>How the calculation runs</h2>
<div class="note">
<p><strong>Net profit</strong> = revenue &minus; business expenses<br>
<strong>SE tax</strong> = net profit &times; 92.35% &times; your social tax rate<br>
<strong>Taxable income</strong> = net profit &minus; half the SE tax &minus; retirement &minus; health premiums<br>
<strong>Take-home</strong> = net profit &minus; all taxes &minus; retirement &minus; health premiums</p>
</div>
<p>Two deliberate simplifications. First, income tax uses a single effective rate rather than progressive
brackets, because an effective rate is the honest way to think about a whole year and brackets differ by
country. Second, the retirement contribution is subtracted from take-home even though it remains your
money &mdash; it is shown separately in the results so you can see both views. For precise
self-employment tax including the wage cap, use the
<a href="/tools/self-employment-tax-calculator.html">self-employment tax calculator</a>.</p>

<h2>What an effective tax rate actually is</h2>
<p>Your marginal rate is what the next dollar costs. Your effective rate is total tax divided by total
income, and it is always lower. A US freelancer in the 24% bracket typically has an effective federal
rate near 14&ndash;17%, because the early portions of income were taxed at 10% and 12%. Entering your
top bracket here will make the picture look much worse than reality &mdash; use last year's return to
find your real effective rate.</p>

<h2>Three ways to widen the gap in your favour</h2>
<ul>
<li><strong>Claim every legitimate expense.</strong> Home office, phone, internet, software, courses,
professional insurance, bank fees, accounting. Each dollar of genuine expense saves you both income tax
and self-employment tax &mdash; roughly 30&ndash;40 cents on the dollar.</li>
<li><strong>Use the retirement accounts you are entitled to.</strong> In the US a SEP-IRA or solo 401(k)
lets a self-employed person shelter far more than a regular IRA. The contribution reduces taxable income
today and stays yours.</li>
<li><strong>Raise your rate before raising your hours.</strong> Ten percent more revenue at the same
hours flows almost entirely to profit. Ten percent more hours costs you ten percent of your life. The
<a href="/tools/freelance-hourly-rate-calculator.html">hourly rate calculator</a> shows where you should
be.</li>
</ul>
""",
    faqs=[
        ("Why is my retirement contribution subtracted from take-home pay?",
         "<p>Because it is not money you can spend this month. It is still yours &mdash; which is why the "
         "results show it as its own figure. Think of take-home as spendable cash and the retirement line "
         "as savings you have already made, rather than money lost.</p>"),
        ("What effective income tax rate should I enter?",
         "<p>The most reliable source is last year's tax return: divide total tax by total income. If you "
         "have no return yet, a US freelancer with $80,000&ndash;$120,000 of net profit is often in the "
         "13&ndash;18% effective federal range. Enter your top bracket and the result will be unduly "
         "pessimistic.</p>"),
        ("Does this work for UK, Canadian or Australian freelancers?",
         "<p>Yes, with your own rates. A UK sole trader would enter roughly 6% for Class 4 National "
         "Insurance and their effective income tax rate, with 0% state tax. A Canadian would use CPP "
         "contributions plus federal and provincial rates. An Australian sole trader would enter 0% for "
         "social tax and their effective rate, plus superannuation in the retirement field.</p>"),
        ("Should I use this to decide between freelancing and a job offer?",
         "<p>It is a good starting point, as long as you compare like with like. Against a $95,000 salary, "
         "compare your freelance <em>take-home plus retirement plus health premiums</em>, because the "
         "employer was paying for those too. Also price the things this calculator cannot: unpaid leave, "
         "income volatility, and the time you spend selling rather than working.</p>"),
        ("Is any of this stored or sent to a server?",
         "<p>No. The calculation is JavaScript running in your own browser. Nothing is transmitted, saved "
         "or logged.</p>"),
    ],
))

# ---------------------------------------------------------------- tool 6
TOOLS.append(dict(
    slug="quarterly-tax-savings-calculator",
    nav="Quarterly tax set-aside",
    script="tool-set-aside.js",
    title="Quarterly Tax Set-Aside Calculator &mdash; How Much to Save From Each Invoice",
    meta_title="Quarterly Tax Set-Aside Calculator | How Much to Save Per Invoice",
    meta_desc="Work out how much of every freelance payment to move into savings for tax, and what each "
              "quarterly estimated payment should be. Free calculator, no sign-up.",
    h1="Quarterly Tax Set-Aside Calculator",
    intro="The freelancer's classic disaster is spending money that was never theirs. The fix is "
          "mechanical, not moral: the day a client pays, a fixed percentage moves to a separate account "
          "and stops existing. This works out that percentage and what each quarterly payment will be.",
    card="How much of each payment to move into savings so tax season is boring.",
    form=[
        field("mode", "Work it out from", "", select=[
            ("annual", "My expected profit for the year", True),
            ("invoice", "A typical invoice amount", False),
        ]),
        field("annualProfit", "Expected net profit this year", "Revenue minus business expenses.",
              pre="$", value="90000", wrapper_id="f-annual"),
        '<div class="row2" id="f-invoice">'
        + field("invoiceAmount", "Typical invoice amount", "", pre="$", value="4000")
        + field("invoicesPerYear", "Invoices per year", "", post="inv", value="24")
        + "</div>",
        field("taxRate", "Set-aside rate",
              "25&ndash;30% suits most freelancers. 35&ndash;40% if you are in a high-tax state or bracket.",
              post="%", value="30"),
        field("alreadyPaid", "Estimated tax already paid this year", "Payments you have made so far.",
              pre="$", value="0"),
        currency_field(),
    ],
    result=result_shell(
        "Each quarterly payment", "outSub", "outQuarter",
        [pill("Tax for the year", "outYear"), pill("Per month", "outMonth"),
         pill("Set-aside rate", "outPct")],
        [row("Expected net profit", "bAnnual"),
         row("Set-aside rate", "bRate", "sub"),
         row("Total tax to cover", "bTotal"),
         row("Already paid", "bPaid"),
         row("Still to pay", "bRemain"),
         row("Per quarter", "bQuarter", "total")],
        foot='<div class="pill-row" id="invoiceRow" hidden>'
             + pill("Move aside per invoice", "outInvoice") + "</div>",
    ),
    prose="""
<h2>Why a separate account beats willpower</h2>
<p>Nobody overspends their tax money on purpose. It happens because a $4,000 payment lands in the same
account as everything else and, for three months, it looks like $4,000 of available money. By the time
the quarterly payment is due, some of it is a new laptop.</p>
<p>The freelancers who never have this problem all do the same thing: a second savings account, and a
standing habit that the moment a client payment clears, a fixed percentage moves out of reach. It takes
thirty seconds and it removes an entire category of anxiety from your year.</p>

<h2>What percentage should you set aside?</h2>
<table>
<tr><th>Situation</th><th>Suggested set-aside</th></tr>
<tr><td>Low profit, no state income tax</td><td>20&ndash;25%</td></tr>
<tr><td>Typical US freelancer, moderate state tax</td><td>28&ndash;32%</td></tr>
<tr><td>High earner, or a high-tax state such as California or New York</td><td>35&ndash;40%</td></tr>
<tr><td>UK sole trader, basic rate</td><td>25&ndash;30%</td></tr>
</table>
<p>Set it against <em>profit</em>, not revenue. If you invoice $10,000 and spend $2,500 running the
business, the 30% applies to $7,500. Setting aside a percentage of revenue is simpler and over-saves,
which is a pleasant problem; just be consistent about which one you are doing.</p>

<h2>The quarterly deadlines</h2>
<p>US estimated tax payments are due four times a year, usually on these dates (they shift to the next
business day when one falls on a weekend or holiday):</p>
<table>
<tr><th>Quarter</th><th>Income period</th><th>Usually due</th></tr>
<tr><td>Q1</td><td>1 January &ndash; 31 March</td><td>15 April</td></tr>
<tr><td>Q2</td><td>1 April &ndash; 31 May</td><td>15 June</td></tr>
<tr><td>Q3</td><td>1 June &ndash; 31 August</td><td>15 September</td></tr>
<tr><td>Q4</td><td>1 September &ndash; 31 December</td><td>15 January, next year</td></tr>
</table>
<p>Note that the quarters are not equal lengths &mdash; Q2 covers two months and Q3 covers three. It is
a quirk of the tax code, not a mistake.</p>

<h2>The safe-harbour rule, which removes the guesswork</h2>
<p>You cannot know this year's income in April. The US tax code solves that: if you pay at least 100% of
last year's total tax across your four estimated payments &mdash; 110% if your prior-year adjusted gross
income was above $150,000 &mdash; you cannot be charged an underpayment penalty, no matter how much you
end up earning. Take last year's total tax, divide by four, and pay that. Any extra is settled in April.</p>
<div class="note">
<p><strong>First year freelancing?</strong> There is no prior year to copy, so estimate forwards and set
aside generously. Over-saving costs you a little interest; under-saving costs you a penalty and a very
unpleasant April.</p>
</div>

<h2>Keep the money working</h2>
<p>Tax money sitting in a current account earns nothing while you hold it for up to a year. A
high-yield savings account or money market fund keeps it liquid and pays interest &mdash; on an average
balance of $9,000 at 4%, that is a few hundred dollars a year for no work. Do not lock it up or invest
it in anything that can fall; this money has a deadline.</p>
<p>To refine your set-aside rate, run your figures through the
<a href="/tools/self-employment-tax-calculator.html">self-employment tax calculator</a> and the
<a href="/tools/freelance-take-home-pay-calculator.html">take-home pay calculator</a>.</p>
""",
    faqs=[
        ("Do I have to pay quarterly, or can I just pay in April?",
         "<p>In the US, if you expect to owe $1,000 or more in tax for the year, the IRS expects quarterly "
         "estimated payments. Paying it all in April means an underpayment penalty on top, calculated as "
         "interest on what you should have paid earlier. The penalty is not enormous, but it is entirely "
         "avoidable.</p>"),
        ("What if my income is wildly unpredictable?",
         "<p>Use the per-invoice mode and set a percentage aside from every payment as it arrives. Your "
         "savings then track your income automatically, with no forecasting. At each quarterly deadline, "
         "pay what the safe-harbour rule requires and leave the rest in the account.</p>"),
        ("Should I set aside from revenue or from profit?",
         "<p>Profit is correct, because that is what is taxed. Setting aside from revenue is simpler and "
         "deliberately over-saves, which many freelancers prefer in their first couple of years. Pick one "
         "and apply it the same way every time.</p>"),
        ("Does this apply outside the United States?",
         "<p>The percentage logic applies everywhere; the deadlines do not. UK self-assessment uses "
         "payments on account due 31 January and 31 July. Canada uses 15 March, June, September and "
         "December. Australia uses quarterly BAS or PAYG instalments. Set your own reminders for your "
         "country's dates.</p>"),
        ("Where should I keep the money?",
         "<p>A separate high-yield savings account at a bank different from your main one &mdash; the "
         "extra friction is a feature. Keep it liquid and keep it safe. Tax money is not an investment "
         "fund; it has a due date and it is not really yours.</p>"),
    ],
))

# =====================================================================
#  Articles: drop a file in content/articles/ and it appears everywhere
# =====================================================================
CONTENT = ROOT / "content" / "articles"

# Phrases that get auto-linked the first time they appear in article text.
LINK_MAP = [
    ("freelance hourly rate calculator", "/tools/freelance-hourly-rate-calculator.html"),
    ("self-employment tax calculator", "/tools/self-employment-tax-calculator.html"),
    ("invoice late fee calculator", "/tools/invoice-late-fee-calculator.html"),
    ("project quote calculator", "/tools/project-quote-calculator.html"),
    ("take-home pay calculator", "/tools/freelance-take-home-pay-calculator.html"),
    ("quarterly tax set-aside calculator", "/tools/quarterly-tax-savings-calculator.html"),
    ("hourly rate calculator", "/tools/freelance-hourly-rate-calculator.html"),
    ("self-employment tax", "/tools/self-employment-tax-calculator.html"),
    ("late fee calculator", "/tools/invoice-late-fee-calculator.html"),
    ("estimated tax payments", "/tools/quarterly-tax-savings-calculator.html"),
]

SKIP_INSIDE = ("a", "h1", "h2", "h3", "code", "pre", "script", "style", "summary")


def autolink(html):
    """Link the first mention of each known phrase, never inside a link or heading."""
    import re
    tokens = re.split(r"(<[^>]+>)", html)
    depth = {t: 0 for t in SKIP_INSIDE}
    used = set()
    out = []
    for tok in tokens:
        if tok.startswith("<"):
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
            if m:
                name = m.group(1).lower()
                if name in depth:
                    depth[name] += -1 if tok.startswith("</") else 1
                    if depth[name] < 0:
                        depth[name] = 0
            out.append(tok)
            continue
        if any(v > 0 for v in depth.values()):
            out.append(tok)
            continue
        text = tok
        for phrase, href in LINK_MAP:
            if phrase in used:
                continue
            m = re.search(re.escape(phrase), text, re.I)
            if m:
                text = (text[:m.start()] + '<a href="' + href + '">' + m.group(0)
                        + "</a>" + text[m.end():])
                used.add(phrase)
        out.append(text)
    return "".join(out)


def load_articles():
    """Read content/articles/*.html. Front matter is key: value lines, then a '---' line."""
    articles = []
    if not CONTENT.exists():
        return articles
    for path in sorted(CONTENT.glob("*.html")):
        raw = path.read_text(encoding="utf-8")
        meta, _, body = raw.partition("\n---\n")
        data = {"slug": path.stem, "body": body.strip()}
        for line in meta.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip()
        data.setdefault("title", path.stem.replace("-", " ").title())
        data.setdefault("description", "")
        data.setdefault("date", "2026-01-01")
        data["tags"] = [t.strip() for t in data.get("tags", "").split(",") if t.strip()]
        articles.append(data)
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def pretty_date(iso):
    import datetime
    try:
        d = datetime.date.fromisoformat(iso)
        return d.strftime("%d %B %Y").lstrip("0")
    except ValueError:
        return iso


# =====================================================================
#  Page renderers
# =====================================================================
def render_tool(tool, tools, articles):
    form = "\n".join(tool["form"])
    related = [t for t in tools if t["slug"] != tool["slug"]][:3]
    rel_cards = "\n".join(
        f'<a class="card" href="/tools/{t["slug"]}.html"><span class="tag">Calculator</span>'
        f'<h3>{t["nav"]}</h3><p>{t["card"]}</p></a>'
        for t in related
    )
    rel_articles = ""
    if articles:
        items = "\n".join(
            f'<li><a href="/guides/{a["slug"]}.html">{a["title"]}</a></li>' for a in articles[:4]
        )
        rel_articles = f"""<section class="prose narrow wrap" style="padding:0;">
<h2>Related reading</h2>
<ul>
{items}
</ul>
</section>"""

    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": strip_tags(tool["h1"]),
            "url": DOMAIN + f"/tools/{tool['slug']}.html",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "description": tool["meta_desc"],
        },
        faq_schema(tool["faqs"]),
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": "Calculators", "item": DOMAIN + "/#tools"},
                {"@type": "ListItem", "position": 3, "name": strip_tags(tool["nav"])},
            ],
        },
    ]

    html = head(tool["meta_title"], tool["meta_desc"], f"/tools/{tool['slug']}.html",
                schemas, [tool["script"]])
    html += header("Tools")
    html += f"""<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/#tools">Calculators</a> &rsaquo; {tool['nav']}</nav>
<section class="hero" style="padding:26px 0 0;margin-bottom:24px;">
<h1>{tool['h1']}</h1>
<p>{tool['intro']}</p>
</section>

<form class="calc" id="calcForm" autocomplete="off">
{form}
<p class="headline-sub" id="warn" hidden style="color:var(--danger);"></p>
<div class="btn-row">
<button class="btn" type="submit">Calculate</button>
<button class="btn btn-ghost" type="button" id="copyBtn">Copy result</button>
<button class="btn btn-ghost" type="button" id="resetBtn">Reset</button>
</div>
{tool['result']}
</form>

{ad('1111111111')}

<article class="prose">
{autolink(tool['prose'])}
</article>

{ad('2222222222', 'fluid')}

{faq_block(tool['faqs'])}
</div>

<div class="wrap">
<section style="margin-top:46px;">
<h2 style="font-size:24px;margin-bottom:14px;">Other calculators</h2>
<div class="grid">
{rel_cards}
</div>
</section>
{rel_articles}
</div>

{ad('3333333333')}
"""
    html += footer(tools)
    return html


def render_article(article, tools, articles):
    others = [a for a in articles if a["slug"] != article["slug"]][:4]
    more = "\n".join(
        f'<li><a href="/guides/{a["slug"]}.html">{a["title"]}</a></li>' for a in others
    )
    more_block = f"<h2>More guides</h2>\n<ul>\n{more}\n</ul>" if more else ""
    tool_cards = "\n".join(
        f'<a class="card" href="/tools/{t["slug"]}.html"><span class="tag">Free calculator</span>'
        f'<h3>{t["nav"]}</h3><p>{t["card"]}</p></a>'
        for t in tools[:3]
    )
    schemas = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article["description"],
        "datePublished": article["date"],
        "dateModified": article.get("updated", article["date"]),
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "mainEntityOfPage": DOMAIN + f"/guides/{article['slug']}.html",
    }]
    html = head(article["title"] + " | " + SITE_NAME, article["description"],
                f"/guides/{article['slug']}.html", schemas)
    html += header("Guides")
    html += f"""<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/guides/">Guides</a> &rsaquo; {article['title']}</nav>
<section class="hero" style="padding:26px 0 18px;">
<h1>{article['title']}</h1>
<p>{article['description']}</p>
<p style="font-size:14px;color:var(--text-mute);margin:0;">Published {pretty_date(article['date'])}</p>
</section>
{ad('4444444444')}
<article class="prose">
{autolink(article['body'])}
</article>
{ad('5555555555', 'fluid')}
<section class="prose">
{more_block}
</section>
</div>
<div class="wrap">
<section style="margin-top:40px;">
<h2 style="font-size:24px;margin-bottom:14px;">Run the numbers</h2>
<div class="grid">
{tool_cards}
</div>
</section>
</div>
"""
    html += footer(tools)
    return html


def render_index(tools, articles):
    cards = "\n".join(
        f'<a class="card" href="/tools/{t["slug"]}.html"><span class="tag">Free calculator</span>'
        f'<h3>{t["nav"]}</h3><p>{t["card"]}</p></a>'
        for t in tools
    )
    guide_cards = "\n".join(
        f'<a class="card" href="/guides/{a["slug"]}.html"><span class="tag">Guide &middot; {pretty_date(a["date"])}</span>'
        f'<h3>{a["title"]}</h3><p>{a["description"]}</p></a>'
        for a in articles[:6]
    )
    guides_section = f"""<section id="guides">
<h2 style="font-size:28px;letter-spacing:-.6px;margin-bottom:6px;">Guides</h2>
<p style="color:var(--text-mute);margin:0 0 18px;">Plain-English explanations of the money side of
working for yourself. New ones added regularly.</p>
<div class="grid">
{guide_cards}
</div>
<p style="margin-top:16px;"><a href="/guides/">See all guides &rarr;</a></p>
</section>""" if articles else ""

    schemas = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": SITE_NAME,
            "url": DOMAIN + "/",
            "description": TAGLINE,
        },
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": strip_tags(t["nav"]),
                 "url": DOMAIN + f"/tools/{t['slug']}.html"}
                for i, t in enumerate(tools)
            ],
        },
    ]
    html = head(
        f"{SITE_NAME} &mdash; Free Money Calculators for Freelancers",
        "Free calculators for freelancers and small businesses: hourly rate, self-employment tax, "
        "invoice late fees, project quotes, take-home pay and quarterly tax set-aside. No sign-up.",
        "/", schemas)
    html += header("Tools")
    html += f"""<div class="wrap">
<section class="hero">
<span class="eyebrow">Free &middot; No sign-up &middot; Nothing leaves your browser</span>
<h1>The money side of freelancing,<br>worked out properly.</h1>
<p>Six calculators for the questions that decide whether working for yourself actually pays: what to
charge, what you owe, what you keep, and what a client owes you when they pay late.</p>
<div class="btn-row">
<a class="btn" href="/tools/freelance-hourly-rate-calculator.html">Find your hourly rate</a>
<a class="btn btn-ghost" href="#tools">Browse all calculators</a>
</div>
</section>

{ad('6666666666')}

<section id="tools">
<h2 style="font-size:28px;letter-spacing:-.6px;margin-bottom:6px;">Calculators</h2>
<p style="color:var(--text-mute);margin:0 0 18px;">Every one runs in your browser. Nothing is uploaded,
nothing is stored, and there is no account to create.</p>
<div class="grid">
{cards}
</div>
</section>

{guides_section}

<section class="prose narrow" style="margin:0 auto;">
<h2>Why these six</h2>
<p>Most freelancers do not fail because the work is bad. They fail because of arithmetic: a rate set by
copying somebody else, a tax bill nobody saved for, a project quoted at the optimistic estimate, and an
invoice sitting unpaid for ninety days because chasing it felt rude.</p>
<p>Each calculator here deals with one of those failures, and each one explains the reasoning rather
than just returning a number &mdash; because the number is only useful if you can defend it in front of
a client or an accountant.</p>
<h3>Honest limits</h3>
<p>These are estimators. They use effective rates and sensible defaults rather than modelling every
bracket, deduction, credit and local rule in every country. For filing a return, planning a
restructure, or anything where being wrong is expensive, take the output to a qualified accountant in
your own jurisdiction. See the <a href="/disclaimer.html">full disclaimer</a>.</p>
</section>
</div>

{ad('7777777777')}
"""
    html += footer(tools)
    return html


def render_guides_index(tools, articles):
    cards = "\n".join(
        f'<a class="card" href="/guides/{a["slug"]}.html"><span class="tag">{pretty_date(a["date"])}</span>'
        f'<h3>{a["title"]}</h3><p>{a["description"]}</p></a>'
        for a in articles
    ) or '<p style="color:var(--text-mute);">The first guides are on their way.</p>'
    html = head(
        "Freelance Money Guides | " + SITE_NAME,
        "Practical guides to rates, tax, invoicing and getting paid as a freelancer. "
        "Plain English, no jargon, updated regularly.",
        "/guides/")
    html += header("Guides")
    html += f"""<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; Guides</nav>
<section class="hero" style="padding:26px 0 22px;">
<h1>Guides</h1>
<p>Everything the calculators assume you already know, explained properly.</p>
</section>
{ad('8888888888')}
<div class="grid">
{cards}
</div>
</div>
"""
    html += footer(tools)
    return html


STATIC_PAGES = {
    "about.html": ("About", "About " + SITE_NAME, """
<h1>About {SITE}</h1>
<p>{SITE} is a small, free set of calculators for people who work for themselves. It exists because the
financial advice aimed at freelancers tends to arrive in two unhelpful forms: vague encouragement
(&ldquo;know your worth!&rdquo;) or a 40-page tax document written for accountants.</p>
<p>What was missing was the middle: a tool that does the arithmetic, and an explanation of why the
arithmetic is shaped that way, so you can argue for the number in front of a client.</p>
<h2>How the site is built</h2>
<p>Every calculator is plain JavaScript running inside your browser. There is no server doing the
sums, which means three things: it is fast, it works on a bad connection, and nothing you type about
your income ever leaves your device. We could not read your figures if we wanted to.</p>
<h2>How it is paid for</h2>
<p>The site carries advertising through Google AdSense. That is the entire business model. There is no
premium tier, no email capture, no course at the end of a funnel, and no affiliate links dressed up as
recommendations. Ads pay for the hosting and the time; you get the tools.</p>
<h2>Accuracy and corrections</h2>
<p>The calculators use published rates and standard formulas, and where a figure changes every year
&mdash; the Social Security wage base, the Bank of England base rate &mdash; it is left as an editable
field rather than hard-coded, so the tool does not quietly go stale.</p>
<p>If you spot an error, tell us. Corrections are made quickly and gratefully. Use the
<a href="/contact.html">contact page</a>.</p>
<h2>What this is not</h2>
<p>It is not tax advice, legal advice or financial advice, and no relationship is created by using it.
Tax rules vary by country, state and personal circumstance. For decisions that matter, talk to a
qualified professional where you live. The <a href="/disclaimer.html">disclaimer</a> sets this out in
full.</p>
"""),
    "contact.html": ("Contact", "Contact " + SITE_NAME, """
<h1>Contact</h1>
<p>Questions, corrections and suggestions are all welcome &mdash; particularly corrections.</p>
<h2>Email</h2>
<p>Write to <strong>hello@freelancefigures.com</strong> and you will normally get a reply within two
working days.</p>
<h2>Useful things to include</h2>
<ul>
<li><strong>Reporting a wrong result?</strong> Send the page address and the exact numbers you entered,
so the calculation can be reproduced.</li>
<li><strong>Suggesting a calculator?</strong> Describe the decision you are trying to make, not just the
tool &mdash; it usually leads to a better tool.</li>
<li><strong>Advertising or partnership enquiries?</strong> Advertising is handled entirely through Google
AdSense; direct placements and sponsored posts are not accepted.</li>
</ul>
<h2>What cannot be answered</h2>
<p>Personal tax questions. Not because of unhelpfulness, but because answering them properly requires
knowing your full circumstances and being licensed where you live &mdash; and answering them improperly
could cost you money. For those, find an accountant or tax adviser in your own country.</p>
"""),
    "privacy.html": ("Privacy", "Privacy Policy | " + SITE_NAME, """
<h1>Privacy policy</h1>
<p><em>Last updated: 13 October 2026</em></p>
<h2>The short version</h2>
<p>The numbers you type into the calculators never leave your browser. We do not ask you to register,
we do not collect your name or email unless you choose to write to us, and we do not sell data. The
site does use Google AdSense and Google Analytics, and those services set cookies &mdash; details below.</p>
<h2>Calculator data</h2>
<p>Every calculation on this site runs locally in JavaScript. Your income, expenses, invoice amounts and
tax rates are processed on your own device and are never transmitted to or stored on our servers. When
you close the tab, they are gone. The only thing stored on your device is your light or dark theme
preference, kept in your browser's local storage.</p>
<h2>Advertising cookies</h2>
<p>This site is funded by advertising served through Google AdSense.</p>
<ul>
<li>Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this
and other websites.</li>
<li>Google's use of advertising cookies enables it and its partners to serve ads to you based on your
visits to this site and other sites on the internet.</li>
<li>You may opt out of personalised advertising by visiting
<a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google Ads Settings</a>.</li>
<li>You can opt out of third-party vendors' use of cookies for personalised advertising at
<a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info/choices</a>.</li>
</ul>
<h2>Analytics</h2>
<p>Aggregate analytics may be used to understand which pages are read and which calculators are used.
This data is aggregated and does not identify you personally.</p>
<h2>Visitors in the European Economic Area and the UK</h2>
<p>Where required, a consent banner asks for your permission before non-essential cookies, including
advertising cookies, are set. You may withdraw consent at any time through your browser settings. Our
lawful basis for processing is consent for advertising and analytics cookies, and legitimate interest
for the basic security and delivery of the website.</p>
<h2>Visitors in California</h2>
<p>We do not sell personal information as defined by the California Consumer Privacy Act. You have the
right to know what personal information is collected and to request its deletion; contact us to make
such a request.</p>
<h2>Children</h2>
<p>This site is intended for adults running a business. It is not directed at children under 13 and we
do not knowingly collect information from them.</p>
<h2>Your rights and contact</h2>
<p>To ask what data relates to you, or to ask for deletion, email
<strong>hello@freelancefigures.com</strong>. Because the calculators store nothing, such requests are
usually answered quickly and in the negative &mdash; there is rarely anything to delete.</p>
<h2>Changes</h2>
<p>If this policy changes, the date at the top of this page changes with it.</p>
"""),
    "terms.html": ("Terms", "Terms of Use | " + SITE_NAME, """
<h1>Terms of use</h1>
<p><em>Last updated: 13 October 2026</em></p>
<h2>1. Agreement</h2>
<p>By using {SITE} you accept these terms. If you do not accept them, please do not use the site.</p>
<h2>2. What the site is</h2>
<p>{SITE} provides free, informational calculators and written guides about the financial side of
self-employment. It is a reference tool, not a professional service, and using it does not create a
client relationship of any kind.</p>
<h2>3. No professional advice</h2>
<p>Nothing on this site is tax, legal, accounting or financial advice. Outputs are estimates produced
from the figures you enter and from general formulas that cannot account for your personal
circumstances or the rules of your jurisdiction. Always confirm with a qualified professional before
acting.</p>
<h2>4. Accuracy</h2>
<p>Reasonable care is taken to keep the formulas and explanations correct and current, but no warranty
is given that they are accurate, complete or up to date. Tax rates, statutory interest rates and
thresholds change, sometimes mid-year.</p>
<h2>5. Limitation of liability</h2>
<p>To the fullest extent permitted by law, {SITE} and its operators are not liable for any loss or
damage &mdash; including lost profits, underpaid or overpaid tax, penalties, or mispriced work &mdash;
arising from use of or reliance on this site.</p>
<h2>6. Acceptable use</h2>
<p>You may use the calculators freely for personal and commercial purposes, including quoting clients.
You may not scrape the site at a rate that degrades it for others, republish its written content as your
own, or attempt to interfere with its operation or security.</p>
<h2>7. Intellectual property</h2>
<p>The text, design and code of this site are owned by its operators. Results you generate from your own
figures are yours to use however you wish, with no attribution required.</p>
<h2>8. Third-party links and advertising</h2>
<p>The site displays advertising supplied by Google AdSense and may link to external sites. We do not
control and are not responsible for third-party content, products or practices.</p>
<h2>9. Changes</h2>
<p>These terms may be updated. Continued use after a change means you accept the revised terms.</p>
"""),
    "disclaimer.html": ("Disclaimer", "Disclaimer | " + SITE_NAME, """
<h1>Disclaimer</h1>
<p><em>Last updated: 13 October 2026</em></p>
<h2>Estimates, not filings</h2>
<p>Every figure produced on this site is an estimate. The calculators apply standard, published formulas
to the numbers you type in. They do not know your deductions, credits, filing status quirks, local
surcharges, treaty positions or business structure, and they do not attempt to model a full tax return.</p>
<h2>Rates change</h2>
<p>Tax rates, contribution ceilings, statutory interest rates and thresholds are revised regularly, often
annually and occasionally mid-year. Where a figure is known to move &mdash; such as the Social Security
wage base or the Bank of England base rate &mdash; it is presented as an editable field precisely so you
can enter the current value. Check the current figure with the relevant authority before relying on a
result.</p>
<h2>Jurisdiction</h2>
<p>Several calculators use United States rules, which are labelled as such. Others are deliberately
country-neutral and ask you to supply your own rates. Nothing here is tailored to the law of any
particular country, state or province.</p>
<h2>No professional relationship</h2>
<p>Using this site does not make us your accountant, tax adviser, lawyer or financial adviser, and no
duty of care arises from your use of it. For filings, disputes, restructures, or any decision where
being wrong carries a cost, consult a qualified professional licensed where you live.</p>
<h2>Your responsibility</h2>
<p>You remain solely responsible for the figures you enter, for how you interpret the outputs, and for
every pricing, tax and business decision you make. If a result looks surprising, it is more likely that
an input needs checking than that the surprise is correct &mdash; check it before acting.</p>
"""),
}


def render_static(filename, nav_label, title, body, tools):
    html = head(title, strip_tags(body.split("</p>")[0])[:155].replace('"', "&quot;") or title,
                "/" + filename)
    html += header(nav_label)
    html += f"""<div class="wrap narrow">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; {nav_label}</nav>
<article class="prose" style="padding-top:18px;">
{body.replace('{SITE}', SITE_NAME)}
</article>
</div>
{ad('9999999999')}
"""
    html += footer(tools)
    return html


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0f766e"/>
<text x="32" y="43" font-family="system-ui,sans-serif" font-size="30" font-weight="700"
 fill="#ffffff" text-anchor="middle">FF</text>
</svg>"""


def main():
    tools = TOOLS
    articles = load_articles()

    write("index.html", render_index(tools, articles))
    for t in tools:
        write(f"tools/{t['slug']}.html", render_tool(t, tools, articles))
    write("guides/index.html", render_guides_index(tools, articles))
    for a in articles:
        write(f"guides/{a['slug']}.html", render_article(a, tools, articles))
    for fname, (nav, title, body) in STATIC_PAGES.items():
        write(fname, render_static(fname, nav, title, body, tools))
    write("favicon.svg", FAVICON)

    urls = ["/", "/guides/"] + [f"/tools/{t['slug']}.html" for t in tools] \
        + [f"/guides/{a['slug']}.html" for a in articles] \
        + ["/" + f for f in STATIC_PAGES]
    entries = "\n".join(
        "  <url><loc>%s%s</loc><changefreq>%s</changefreq><priority>%s</priority></url>"
        % (DOMAIN, u, "weekly" if u.startswith(("/tools", "/")) else "monthly",
           "1.0" if u == "/" else ("0.9" if u.startswith("/tools") else "0.6"))
        for u in urls
    )
    write("sitemap.xml",
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + entries + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    write("ads.txt", "# Replace with the line Google AdSense gives you after approval.\n"
                     "# google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0\n")
    write(".nojekyll", "")

    print(f"Built {len(tools)} calculators, {len(articles)} guides, "
          f"{len(STATIC_PAGES)} static pages into {OUT}")


if __name__ == "__main__":
    main()

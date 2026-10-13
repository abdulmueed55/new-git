# Tool roadmap

314 tools across 12 categories. Each category gets its own section of the site, its own hub
page and its own URL prefix, so a visitor who lands on a fuel calculator stays inside the
vehicle section instead of being thrown at tax tools.

## URL structure

```
/money/<tool>.html        already built, 9 tools live
/vehicle/<tool>.html
/health/<tool>.html
/convert/<tool>.html
/date/<tool>.html
/math/<tool>.html
/text/<tool>.html
/dev/<tool>.html
/image/<tool>.html
/home/<tool>.html
/study/<tool>.html
/everyday/<tool>.html
```

Each prefix also has an index page listing its tools, and the homepage lists the categories
rather than 290 links.

## Build order, and why

Ad rates differ by category by a factor of twenty. The order below is by revenue per visitor,
not by how interesting the tool is to build.

| # | Category | Tools | Typical RPM | Build |
|---|---|---|---|---|
| 1 | Money &amp; business | 48 | $12&ndash;25 | 9 live, rest next |
| 2 | Home &amp; DIY | 24 | $8&ndash;15 | phase 2 |
| 3 | Vehicle &amp; fuel | 28 | $6&ndash;15 | phase 2 |
| 4 | Health &amp; fitness | 30 | $5&ndash;12 | phase 3 |
| 5 | Study &amp; grades | 16 | $4&ndash;10 | phase 3 |
| 6 | Date &amp; time | 22 | $2&ndash;5 | phase 4 |
| 7 | Everyday | 20 | $2&ndash;5 | phase 4 |
| 8 | Maths | 32 | $1&ndash;4 | phase 5 |
| 9 | Unit converters | 30 | $1&ndash;3 | phase 5 |
| 10 | Text &amp; writing | 24 | $1&ndash;3 | phase 5 |
| 11 | Image &amp; file | 16 | $1&ndash;3 | phase 6 |
| 12 | Developer | 24 | $0.50&ndash;2 | phase 6 |

The low-RPM categories are still worth building. They bring volume, they bring links, and a
visitor who arrives for a unit converter sometimes stays. They are simply not where the first
six months of effort should go.

---

## 1. Money &amp; business — 48 tools

**Live (9):** freelance hourly rate · self-employment tax · invoice late fee · project quote ·
freelance take-home pay · quarterly tax set-aside · salary to freelance rate · VAT &amp; sales
tax · profit margin &amp; markup

**To build (39):** compound interest · simple interest · loan EMI · mortgage repayment ·
mortgage affordability · car loan · personal loan · savings goal · emergency fund · retirement
savings · inflation · currency converter · tip · bill split · discount &amp; sale price ·
US sales tax by state · break-even point · ROI · CAGR · payback period · hourly to annual
salary · overtime pay · paycheck / net pay · net worth · debt snowball · debt avalanche ·
credit card payoff · rent vs buy · business runway &amp; burn rate · customer lifetime value ·
customer acquisition cost · churn rate · cost per unit · employee cost to employer · per diem ·
per-word rate · commission · royalty · zakat

## 2. Home &amp; DIY — 24 tools

paint quantity · wallpaper rolls · floor tiles · flooring area · carpet · concrete volume ·
mortar &amp; cement · screed · roof area · roof pitch · gravel &amp; aggregate · topsoil &amp;
mulch · lumber &amp; timber · fence panels · decking boards · insulation R-value · air
conditioner BTU size · heater size · appliance running cost · solar panel output · water tank
capacity · swimming pool volume · stair rise &amp; run · brick quantity

## 3. Vehicle &amp; fuel — 28 tools

**fuel average (km per litre)** · miles per gallon · L/100km converter · fuel cost for a trip ·
monthly fuel cost · fuel cost split between passengers · mileage improvement · CNG vs petrol
running cost · diesel vs petrol · EV charging cost · EV vs petrol cost per km · car loan EMI ·
lease vs buy · car depreciation · total cost of ownership · insurance estimate · registration
&amp; road tax · tyre size comparison · tyre pressure converter · speed, distance and time ·
0&ndash;100 km/h estimate · power to weight ratio · engine displacement · gear ratio · towing
capacity · road trip cost with tolls · oil change interval · odometer km to miles

## 4. Health &amp; fitness — 30 tools

BMI · BMI for children · BMR · TDEE · body fat percentage · lean body mass · ideal weight ·
waist-to-hip ratio · waist-to-height ratio · calorie deficit · macro split · protein intake ·
water intake · calories burned by activity · steps to kilometres · running pace · race time
predictor · heart rate zones · maximum heart rate · VO2 max estimate · one-rep max · training
volume · sleep cycle bedtime · pregnancy due date · ovulation window · menstrual cycle ·
smoking cost · alcohol units · dog age in human years · cat age in human years

*Every page in this category carries a prominent line stating it is a general estimate and
not medical advice, and none of them diagnoses anything.*

## 5. Study &amp; grades — 16 tools

GPA · CGPA · percentage to GPA · GPA to percentage · weighted grade · final exam grade needed ·
semester grade · attendance percentage · exam countdown · study time planner · reading time for
a textbook · student loan repayment · scholarship value · tuition cost · APA citation · MLA
citation

## 6. Date &amp; time — 22 tools

age · age in days, weeks and months · date difference · add or subtract days · working days
between dates · deadline from working days · week number · leap year · days until a date ·
countdown timer · time zone converter · meeting time across zones · duration between two times ·
time card / timesheet · overtime hours · decimal hours converter · next birthday · retirement
date · Hijri to Gregorian date · Gregorian to Hijri date · day of the week for any date ·
unix timestamp to date

## 7. Everyday — 20 tools

tip · bill split with tip · discount · double discount · random number · dice roller · coin
flip · random name picker · team picker · random letter · pomodoro timer · stopwatch · alarm
in X minutes · shoe size converter · clothing size converter · ring size · bra size · zodiac
sign · Chinese zodiac · name day

## 8. Maths — 32 tools

percentage · percentage increase or decrease · percentage of a number · what percent is X of Y ·
fraction · decimal to fraction · fraction to decimal · ratio · proportion · mean, median, mode ·
standard deviation · variance · GCD · LCM · prime checker · factorial · quadratic equation ·
slope · distance between two points · midpoint · area of a circle · area of a triangle · area of
a rectangle · volume of a cylinder · volume of a sphere · circumference · triangle solver ·
Pythagorean theorem · exponent · logarithm · combination and permutation · significant figures

## 9. Unit converters — 30 tools

length · weight &amp; mass · temperature · area · volume · speed · time · pressure · energy ·
power · force · torque · density · data storage · data transfer rate · angle · frequency ·
fuel economy · cooking measurements · oven temperature · paper sizes · screen size &amp; aspect
ratio · DPI and PPI · pixels to inches · bits and bytes · roman numerals · number base
(binary, octal, decimal, hex) · scientific notation · acreage · metric to imperial

## 10. Text &amp; writing — 24 tools

word count · character count · reading time · speaking time · case converter · title case ·
sentence case · remove duplicate lines · sort lines · find and replace · lorem ipsum · text
diff · URL slug · reverse text · remove line breaks · remove extra spaces · word frequency ·
readability score · strip HTML tags · markdown to HTML · HTML to text · CSV to table ·
text to columns · palindrome checker

## 11. Image &amp; file — 16 tools

image resize · image compress · image crop · PNG to JPG · JPG to PNG · image to WebP · WebP to
PNG · image to base64 · favicon generator · image to PDF · PDF merge · PDF split · PDF compress ·
colour extractor from an image · EXIF viewer · add watermark

*All of these run in the browser with the Canvas and File APIs. Nothing is uploaded, which is a
genuine selling point against every competitor that requires an upload.*

## 12. Developer — 24 tools

JSON formatter · JSON validator · JSON to CSV · base64 encode and decode · URL encode and
decode · HTML entity encode · MD5 hash · SHA-256 hash · UUID generator · password generator ·
QR code generator · colour converter (HEX, RGB, HSL) · gradient generator · box-shadow
generator · CSS unit converter · regex tester · cron expression builder · JWT decoder · unix
timestamp converter · user agent parser · meta tag generator · robots.txt generator · htaccess
redirect generator · IP subnet calculator

---

## Rules for every tool

These are what separate a site Google keeps from one it removes.

1. **One page per tool, with real explanation.** A calculator with no words around it is a thin
   page. Every tool needs the formula, a worked example and the mistake people make. 600 words
   minimum, and it has to be worth reading.
2. **No two pages alike.** `build/seo_check.py` fails the build if two pages are more than 80%
   identical, or if a single word exceeds 3.5% of a page. That rule does not relax as the site
   grows.
3. **Everything runs in the browser.** No server, no API cost, no upload. This is why hosting
   stays free at 314 tools, and it is a real privacy claim competitors cannot make.
4. **Categories stay separate.** Related links point inside the same category, not across the
   whole site. A person converting fuel economy does not want a GPA calculator.
5. **Build the money categories first.** Twenty unit converters earn what two finance tools do.

## Realistic pace

At 3 to 5 tools a week with proper write-ups, 314 tools is roughly 18 months. That is normal —
calculator.net took years. The site earns long before the list is finished, because the first
60 tools in the high-RPM categories carry most of the revenue.

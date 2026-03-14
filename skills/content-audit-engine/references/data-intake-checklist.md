# Data Intake Checklist

## Required Data Sources

| # | Source | Export Path | Required Columns | Format |
|---|---|---|---|---|
| 1 | Site URL | User provides | — | Plain text |
| 2 | Sitemap | `yourdomain.com/sitemap.xml` | — | XML or URL list |
| 3 | GSC Pages | GSC → Performance → Pages tab (6mo) | Page, Clicks, Impressions, CTR, Average Position | CSV |
| 4 | GSC Queries | GSC → Performance → Queries tab (6mo) | Query, Clicks, Impressions, CTR, Position | CSV |
| 5 | Competitors | User provides | — | Domain list (3–5) |
| 6 | Target Keywords | User provides | — | Keyword list (5–10) |

## Strongly Recommended

| # | Source | Export Path | Required Columns | Format |
|---|---|---|---|---|
| 7 | GA4 Landing Pages | GA4 → Engagement → Landing Page (6mo) | Landing Page, Sessions, Engaged Sessions, Engagement Rate, Avg Engagement Time, Conversions | CSV |
| 8 | Ahrefs Organic KWs | Site Explorer → Organic Keywords | Keyword, Volume, Position, URL, Traffic | CSV |

## Optional Enrichment

| # | Source | Purpose |
|---|---|---|
| 9 | Screaming Frog crawl | Full page inventory with word count, H1, H2, title, meta, inlinks |
| 10 | Ahrefs Content Gap | Keywords competitors rank for that client doesn't |
| 11 | Ahrefs Competing Domains | Auto-detected organic competitors for scope validation |
| 12 | Ahrefs Top Pages | Competitor's top traffic pages by estimated visits |

---

## GSC Export Instructions (give to user verbatim if they don't know how)

**Pages export:**
1. Go to Google Search Console → Your property
2. Click "Performance" in the left menu
3. Set date range to "Last 6 months"
4. Click the "Pages" tab
5. Click "Export" → "CSV"
6. Save as `gsc-pages.csv`

**Queries export:**
1. Same steps above but click the "Queries" tab
2. Export → CSV → Save as `gsc-queries.csv`

**Note:** If the site has less than 1,000 impressions/month, GSC data may be very sparse. Flag this and proceed with web search + Ahrefs as primary data.

---

## GA4 Export Instructions

1. Go to Google Analytics 4 → Your property
2. Click "Reports" → "Engagement" → "Landing page"
3. Set date range to match GSC (last 6 months)
4. Click the download icon → "Export to CSV"
5. Save as `ga4-landing-pages.csv`

**Important:** If the user has conversion tracking set up, ask them to include "Key events" or "Conversions" in the export — this is critical for identifying high-business-impact pages.

---

## Ahrefs Export Instructions

**Organic Keywords (for client domain):**
1. Go to Ahrefs → Site Explorer
2. Enter client's domain
3. Click "Organic keywords"
4. Set filter: Position ≤ 50 (to include pages in striking distance)
5. Export → CSV → Save as `ahrefs-organic-kws.csv`

**For competitor analysis:**
Same steps, repeat for each competitor domain.

---

## CSV Validation Steps

For every CSV received, Claude must:

1. **Parse check** — confirm the file opens without errors
2. **Column validation** — check that required columns are present:
   - If column names differ, attempt auto-mapping (see csv-processor.py)
   - Report mapping applied: "Mapped 'Top pages' → 'url', 'Average position' → 'avg_position'"
3. **Row count** — report total rows processed and skipped
4. **Date range detection** — extract min/max dates from data and report
5. **Null check** — flag any critical columns with >20% null values
6. **Data type check** — confirm numeric columns are numeric (clicks, impressions, position)

### Report format (present to user after each CSV is processed):

```
GSC Pages CSV — Validated ✅
  Rows: 298 pages with data
  Date range: Jan 1 – Jun 30, 2026
  Columns mapped: Page → url, Clicks → clicks, Impressions → impressions, CTR → ctr, Average position → avg_position
  Issues: None
  Coverage: 298/347 sitemap URLs have GSC data (49 pages have no impressions)
```

---

## Standard Normalized Schema

After processing, all data uses these column names:

| Standard Column | Source | Definition |
|---|---|---|
| `url` | All sources | Page URL, absolute |
| `keyword` | GSC Queries, Ahrefs | Query or keyword string |
| `clicks` | GSC | Clicks from search results |
| `impressions` | GSC | Times appeared in search |
| `ctr` | GSC | Click-through rate (decimal or %) |
| `avg_position` | GSC, Ahrefs | Average ranking position |
| `sessions` | GA4 | Total sessions |
| `engaged_sessions` | GA4 | Sessions with >10s engagement |
| `engagement_rate` | GA4 | engaged_sessions / sessions |
| `avg_engagement_time` | GA4 | Average session engagement time |
| `conversions` | GA4 | Goal completions / key events |
| `search_volume` | Ahrefs | Monthly search volume |
| `traffic` | Ahrefs | Estimated monthly traffic |
| `word_count` | Screaming Frog | Page word count |
| `title` | Screaming Frog | Page title tag |
| `h1` | Screaming Frog | First H1 |
| `inlinks` | Screaming Frog | Internal inlink count |

---

## Handling Missing Data

| Missing Data | Impact | Mitigation |
|---|---|---|
| No GSC data | Cannot measure actual search performance | Use web search + Ahrefs position data as proxy |
| No GA4 data | Cannot assess engagement quality | Depth scoring relies 100% on on-page signals |
| No Ahrefs data | Cannot get keyword volumes or position data | Use GSC positions + web search for volume estimates |
| No sitemap | Incomplete page inventory | Use web search `site:domain.com` to discover sections |
| Sparse GSC (<500 clicks/month) | Weak statistical signal | Flag all GSC-based findings as directional only |
| No competitor list | Cannot do gap analysis | Ask user for 2–3 competitors minimum, or auto-discover via Ahrefs |
| No target keywords | Cannot do SERP analysis | Infer from GSC top-performing queries or ask user |

Always tell the user explicitly: "Without [data source], [specific impact on accuracy]."
Never silently skip data quality issues.

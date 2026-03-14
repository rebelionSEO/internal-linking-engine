---
name: content-audit-engine
version: "1.0.0"
description: >
  Perform a comprehensive content audit analyzing a website's content architecture,
  topical depth, coverage gaps, content quality, and competitive positioning. Use this
  skill whenever the user asks about content audits, content strategy audits, content
  gap analysis, topical authority assessment, content inventory, editorial calendar
  planning, content performance analysis, content benchmarking against competitors,
  or any request to evaluate what content a site has, what it's missing, and what
  it should create next. Also trigger when the user provides GSC, GA4, or Ahrefs CSV
  exports and mentions content performance, content gaps, or content strategy. This
  skill works with Screaming Frog MCP for crawl data, Ahrefs MCP for keyword and
  competitor data, web search for SERP and AI overview analysis, and manually
  uploaded CSV exports as the primary data input method.
license: Apache-2.0
metadata:
  author: rebelionSEO
  tags:
    - seo
    - content audit
    - content strategy
    - topical authority
    - competitor analysis
    - content gaps
    - editorial planning
---

# Content Audit Engine

## Purpose

This skill transforms content auditing from a scattered, subjective process into a
structured, data-anchored workflow that produces actionable findings. It analyzes a
client site's content inventory, maps topical architecture, scores content depth and
quality, benchmarks against competitors, identifies SERP and AI overview patterns,
and surfaces gaps that become experiments for a content roadmap.

The core principle: **Data first, opinions second.** Every finding must be tied to
a specific data point — a URL, a metric, a SERP result, a competitor page. No
generic "you should create more content" recommendations.

---

## Architecture Overview

The skill operates in 7 sequential phases. Each phase produces an output that the
user reviews before the next phase begins. Never skip phases or combine them
without user approval.

```
Phase 0: Data Intake & Qualification
Phase 1: Client Site Architecture Mapping
Phase 2: Content Classification & Depth Scoring
Phase 3: Competitor Discovery & Content Mapping
Phase 4: SERP & AI Overview Pattern Analysis
Phase 5: Gap Analysis & Opportunity Mapping
Phase 6: Executive Summary Generation (DOCX, max 12 pages)
```

---

## Data Sources

### What Claude Needs From the User

Before starting any analysis, present this data request exactly:

> **To give you the most accurate audit, here's what I need:**
>
> **Required (minimum to proceed):**
> 1. **Your site URL** — the domain being audited
> 2. **Sitemap URL** — usually at `yourdomain.com/sitemap.xml`
> 3. **GSC Pages export** — GSC → Performance → Pages tab, last 6 months:
>    Page, Clicks, Impressions, CTR, Average Position
> 4. **GSC Queries export** — GSC → Performance → Queries tab, last 6 months:
>    Query, Clicks, Impressions, CTR, Position
> 5. **Top 3–5 competitors** — domains competing for the same audience
> 6. **Top 5–10 target keywords** — keywords most important to the business
>
> **Strongly recommended:**
> 7. **GA4 Landing Page report** — GA4 → Engagement → Landing Page, last 6 months:
>    Landing Page, Sessions, Engaged Sessions, Engagement Rate, Avg Engagement Time
> 8. **Ahrefs Organic Keywords export** — Site Explorer → Organic Keywords:
>    Keyword, Volume, Position, URL, Traffic
>
> **Helpful context:**
> 9. Primary services/products
> 10. Target audience
> 11. Current content types published
> 12. Known pain points ("our blog gets no traffic", "no conversions from content")

### Tool Priority for Data Access

1. **User-uploaded CSVs** — primary data source for GSC, GA4, Ahrefs
2. **Screaming Frog MCP** — crawl data if connected
3. **Ahrefs MCP** — keyword and competitor data if connected
4. **Web search** — SERP analysis, AI overview detection, competitor discovery
5. **Web fetch** — reading competitor pages, extracting content structure

### CSV Normalization

See `scripts/csv-processor.py`. Before processing any CSV:
1. Detect source tool from column headers (GSC, GA4, Ahrefs, Screaming Frog)
2. Normalize column names to standard schema (see references/data-intake-checklist.md)
3. Strip header rows, summary rows, blank rows
4. Validate data types
5. Report parsing issues before proceeding

---

## Phase 0: Data Intake & Qualification

**Goal:** Collect and validate all data before any analysis begins.

### Steps

1. Present the data request checklist (above)
2. As files arrive, validate each:
   - Confirm CSV parses correctly
   - Report row counts, date ranges, column coverage
   - Flag missing critical columns
3. If sitemap URL provided, fetch and parse it
4. If no sitemap: request Screaming Frog crawl export OR use web search to discover content sections
5. Confirm scope with user before proceeding

### Phase 0 Output

Present a validated data inventory table:

```
Data Source       | Status     | Records | Date Range   | Notes
------------------|------------|---------|--------------|-------------------
Sitemap           | ✅ Loaded   | 347 URLs| —            | —
GSC Pages         | ✅ Loaded   | 298 rows| Jan–Jun 2026 | —
GSC Queries       | ✅ Loaded   | 1,204   | Jan–Jun 2026 | —
GA4 Landing Pages | ✅ Loaded   | 312 rows| Jan–Jun 2026 | Missing conversions
Ahrefs Keywords   | ❌ Missing  | —       | —            | Proceeding without
Competitors       | ✅ 3 listed | —       | —            | [domain list]
Target Keywords   | ✅ 8 listed | —       | —            | [keyword list]
```

**Do NOT proceed to Phase 1 until the user confirms the data inventory.**

---

## Phase 1: Client Site Architecture Mapping

**Goal:** Map topical organization — not technical structure. Understand what
clusters exist, where pillars live, how content is grouped by topic.

### Process

1. **URL pattern analysis** — group URLs by path to identify content sections
2. **Section inventory** — for each section: path pattern, page count, avg word
   count (if crawl data available), traffic share, example URLs
3. **Cluster identification** — use the combination of:
   - Page titles and H1s (primary topic signal)
   - GSC query data (what keywords each page actually ranks for)
   - URL path patterns (structural hints, not definitive)
   - Meta descriptions and H2 inferences
4. **Pillar identification** — within each cluster, identify pillar by:
   highest traffic + broadest keyword coverage + highest word count + most inlinks
5. **Architecture summary** — present cluster map:

```
Cluster: [Topic Name]
├── Pillar: [URL] — [title] — [traffic] — [keyword count]
├── Supporting: [URL] — [title] — [traffic]
└── Supporting: [URL] — [title] — [traffic]
```

### User Validation

Ask: "Here's how I see your site's content organized into topical clusters.
Does this match your understanding? Any clusters I'm missing or pages
miscategorized?"

**Do NOT proceed to Phase 2 until clusters are validated.**

---

## Phase 2: Content Classification & Depth Scoring

See `references/classification-rules.md` for full taxonomy and edge cases.
See `references/scoring-rubrics.md` for scoring criteria and metric thresholds.

### Content Type (assign exactly ONE)

| Type | Definition |
|---|---|
| Blog Post | Informational article, topical content |
| Guide/Resource | Long-form educational, structured H2s, 2000+ words |
| Case Study | Client/project success story with results |
| Landing Page | Conversion-focused, service/product page |
| Tool/Calculator | Interactive utility |
| Comparison | vs-style or alternatives content |
| Glossary/Definition | Short definitional content, "what is" pattern |
| News/Update | Time-sensitive, event-specific |
| Hub/Index | Category index page, links to other content |

### Content Format (assign exactly ONE)

Text-heavy · Listicle · How-to · Data-driven · Interview/Q&A · Visual/Infographic · Video-led

### Topical Depth Score (1–5 per page)

| Score | Definition | Primary Signal |
|---|---|---|
| 1 — Thin | Surface-level, no unique value | < 300 words |
| 2 — Basic | Covers intro level only | 300–800 words |
| 3 — Adequate | Solid coverage, meets intent | 800–1,500 words |
| 4 — Strong | Above-average depth, original value | 1,500–3,000 words |
| 5 — Authoritative | Best-in-class, reference quality | 3,000+ words + original insights |

Scoring weights: word count (30%) + H2 subtopic coverage (30%) + GSC keyword breadth (20%) + traffic vs cluster peers (10%) + GA4 engagement (10% if available).

### Topical Coverage Score (1–5 per cluster)

| Score | Definition |
|---|---|
| 1 — Minimal | 1–2 pages, surface coverage |
| 2 — Partial | 3–5 pages, missing major subtopics |
| 3 — Moderate | 6–10 pages, core covered, gaps exist |
| 4 — Strong | 10–20 pages, comprehensive |
| 5 — Dominant | 20+ pages, full subtopic depth |

### Performance Tier (per page)

| Tier | Criteria |
|---|---|
| ⭐ Top Performer | Top 10% by traffic, strong engagement |
| ✅ Performing | Above median traffic, decent engagement |
| ⚠️ Underperforming | Impressions exist but low CTR or engagement |
| 🔻 Declining | Traffic dropped >30% vs prior period |
| ❌ Dead Weight | Zero or near-zero traffic, no keyword rankings |

### Phase 2 Output

Full classification table:
```
| URL | Cluster | Type | Format | Depth | Coverage | Tier | Top Keywords |
```

Cluster-level summary:
```
| Cluster | Pages | Avg Depth | Coverage Score | Traffic Share | Top Performer | Biggest Gap |
```

Ask: "Review the classifications and scores. Any adjustments before I analyze competitors?"

---

## Phase 3: Competitor Discovery & Content Mapping

**Goal:** Understand what competitors publish, how they structure content,
and where they have coverage the client lacks.

### Process (per competitor, max 5)

1. **Find content sections** via web search:
   - `site:competitor.com blog`
   - `site:competitor.com resources OR guides`
   - Fetch `competitor.com/sitemap.xml`
2. **Map inventory**: content type counts per section, topical clusters
3. **Deep-dive overlapping clusters**: read 3–5 top competitor pages (web fetch)
   - Word count, format, H2 structure, depth estimate
   - Original data? Case studies? Tools? Video?
   - Subtopics covered that client doesn't cover
4. **Ahrefs enrichment** (if available): competitor top pages, gap keywords

### Competitor Content Profile

```
Competitor: [domain]
Content Volume: ~[X] blog posts, ~[Y] guides, ~[Z] landing pages
Primary Clusters: [list]
Formats Used: [list]
Avg Content Depth: [1–5 estimate]
Notable Strengths: [e.g., "strong case study library", "original research"]
Notable Weaknesses: [e.g., "no comparison content", "thin blog posts"]
Client Overlap: [which clusters overlap]
```

### Phase 3 Output

Competitor comparison matrix:
```
| Dimension         | Client | Comp A | Comp B | Comp C |
|---|---|---|---|---|
| Blog volume       | 45     | ~80    | ~30    | ~120   |
| Guides/resources  | 3      | ~12    | ~5     | ~20    |
| Case studies      | 2      | ~8     | 0      | ~15    |
| Tools             | 0      | 2      | 0      | 1      |
| Avg depth score   | 2.8    | 3.5    | 2.2    | 4.1    |
| Clusters covered  | 5      | 8      | 4      | 10     |
```

Ask: "Here's the competitive landscape. Dig deeper into any competitor, or proceed to SERP analysis?"

---

## Phase 4: SERP & AI Overview Pattern Analysis

**Goal:** For each target keyword, analyze what actually ranks and what AI
overviews cite — then identify content patterns that win.

### Process (per keyword, top 5–10 target keywords)

1. Search the keyword via web search
2. Analyze top 5–10 organic results:
   - Who ranks (client, competitor, other)?
   - Content type and format
   - Estimated length (from snippets + fetched pages)
   - Dominant tone (educational, commercial, technical)
   - Subtopics covered (from titles, descriptions, sampled H2s)
3. AI Overview analysis (if present):
   - Does an AI overview appear?
   - What sources are cited?
   - What format (summary, list, comparison, step-by-step)?
   - Is client cited? Are competitors cited?

### Phase 4 Output

Per-keyword analysis:
```
Keyword: [keyword] | Volume: [X] | Client Position: [Y or "not ranking"]
Top 3 Results:
  1. [URL] — [type] — [format] — [est. length] — [source]
  2. [URL] — [type] — [format] — [est. length] — [source]
  3. [URL] — [type] — [format] — [est. length] — [source]
AI Overview: [Yes/No] — [format] — Client cited: [Yes/No]
Pattern: [dominant type + format + depth]
Client Gap: [what's missing to compete]
```

Cross-keyword pattern summary:
```
| Pattern Dimension          | Finding |
|---|---|
| Dominant content type      | [e.g., "Long-form guides dominate 7/10 keywords"] |
| Dominant format            | [e.g., "How-to for informational, comparison for commercial"] |
| Avg ranking content length | [e.g., "2,000–3,500 words for top 3 positions"] |
| AI Overview presence       | [e.g., "Appears for 6/10 keywords"] |
| AI citation pattern        | [e.g., "Cites authoritative guides with structured headers"] |
| Client in top 10           | [X/10 keywords] |
| Competitor frequency       | [most appearing competitors] |
| Biggest format gap         | [e.g., "No comparison content — all competitors have it"] |
```

---

## Phase 5: Gap Analysis & Opportunity Mapping

**Goal:** Cross-reference all phases → produce prioritized actionable gaps.

### Gap Types

| Gap Type | Source | Definition |
|---|---|---|
| Topic Gap | Phase 3 vs Phase 1 | Topics competitors cover, client has zero pages |
| Depth Gap | Phase 2 scores < 3 | Topics covered but at insufficient depth |
| Format Gap | Phase 4 patterns vs Phase 2 formats | Client doesn't use formats SERPs reward |
| Cluster Gap | Phase 2 coverage < 3 | Entire topical clusters underdeveloped |
| Conversion Path Gap | Phase 1 architecture | Supporting content exists, no landing page to drive to |
| AI Overview Gap | Phase 4 citations | AI overviews exist but client not cited |
| Declining Content | Phase 2 🔻 tier | Pages losing traffic — refresh candidates |

### Opportunity Scoring

Score each opportunity (1–10 per dimension):
- **Traffic Potential** (40%) — keyword volume + current competition
- **Competitive Advantage** (30%) — how feasible to win (competitor weakness + client strength)
- **Business Impact** (30%) — connects to revenue-generating service/product

Final score = weighted average. Rank all opportunities high → low.

### Phase 5 Output

```
| # | Opportunity | Type | Cluster | Score | Effort | Action |
|---|---|---|---|---|---|---|
```

Grouped into:
- **Quick Wins** — high score, low effort (refreshes, format upgrades, depth improvements)
- **Strategic Builds** — high score, high effort (new pillars, new clusters, new formats)
- **Experimental** — uncertain score, low effort (test formats, test topics, AI overview optimization)

Ask: "Here are the prioritized opportunities. Adjust any priorities before I generate the executive summary?"

---

## Phase 6: Executive Summary Generation

**Maximum 12 pages.** Use the docx skill for file generation (read its SKILL.md first).
See `references/executive-summary-template.md` for exact section specs and formatting.

### Page Allocation

| Section | Pages | Content |
|---|---|---|
| Cover | 1 | Title, domain, date, "Content Audit — Executive Summary" |
| Audit Scope & Data | 0.5 | Sources used, date ranges, data gaps |
| Site Architecture | 1.5 | Cluster map, content volume, pillar identification |
| Content Quality Assessment | 2 | Depth scores, performance tiers, top/bottom performers |
| Competitive Landscape | 2 | Competitor matrix, client advantages and gaps |
| SERP & AI Overview Patterns | 2 | Per-keyword findings, cross-keyword summary |
| Gap Analysis & Opportunities | 2 | Prioritized opportunity list, grouped by type |
| Recommended Experiments | 1 | Top 5–7 specific experiments for the roadmap |

### Formatting Rules

- Every claim tied to a specific data point
- Include actual URLs analyzed, not descriptions
- No filler text, no generic advice
- Tables over paragraphs wherever possible
- Experiments framed as hypotheses with success metrics

---

## Handling Large Sites

| Site Size | Approach |
|---|---|
| < 100 pages | Full analysis, all phases |
| 100–300 pages | Batch classification (50 pages at a time), top 3 competitors, top 10 keywords, cap at 20 opportunities |
| 300+ pages | Alert user, ask for priority clusters. Deep-classify priority clusters only. Top 3 competitors against priority clusters. Top 5 keywords. Focus opportunities on priority areas. |

For 300+ page sites, say: "Your site has [X] pages. I recommend focusing the deep analysis
on your top 3–5 clusters. I'll map the full architecture but depth scoring and competitor
comparison will focus on your priority areas. Which topics or sections matter most?"

---

## User Interaction Rules

1. **Present the data checklist first.** Never start analysis without knowing data availability.
2. **Validate at every phase transition.** Present findings → confirm → proceed.
3. **Be transparent about data gaps.** "Without GA4, I can't assess engagement quality. Depth scoring will rely more on on-page signals."
4. **Quantify everything.** "Competitor A has ~80 blog posts across 8 clusters vs your 45 posts across 5 clusters" — never vague comparisons.
5. **Connect gaps to business outcomes.** "Competitor A ranks for 12 keywords in the [topic] cluster (~3,400 monthly visits). You have zero pages here, and it maps directly to your [service]."
6. **Propose experiments, not mandates.** Frame as hypotheses: "If we create a comparison guide for [keyword], we could capture [estimated traffic] based on SERP patterns."
7. **Respect phased execution.** If user wants to skip to the summary, redirect: "The summary quality depends on the analysis phases. Can we at least do a quick version of the competitor and SERP phases first?"

---

## Quick Reference: Rules Engine

```
DATA INTAKE
├── Always present full checklist first
├── Validate every CSV (row count, date range, column check)
├── Minimum: site URL + GSC + competitors + target keywords
├── Flag data gaps and their impact on accuracy
└── Confirm scope before Phase 1

ARCHITECTURE
├── Cluster by semantic topic, NOT URL folder
├── GSC query data is primary clustering signal
├── Every cluster should map to a service/product when possible
├── Pillar = highest traffic + broadest keywords + depth + inlinks
└── User validates all assignments before scoring

CLASSIFICATION
├── One content type + one format per page
├── Depth scoring uses weighted signals, not just word count
├── Performance tiers require actual traffic + engagement data
└── Flag all declining pages for refresh consideration

COMPETITOR ANALYSIS
├── Max 5 competitors
├── Discover sections via web search, not assumptions
├── Deep-dive only overlapping clusters
├── Sample 3–5 pages per competitor per cluster
└── Estimate, never claim exact competitor metrics

SERP ANALYSIS
├── Analyze actual current SERPs
├── Note AI overview presence and citation patterns
├── Identify format patterns across multiple keywords
├── Find differentiation: what no ranking page does well
└── Connect patterns to actionable format recommendations

GAP ANALYSIS
├── Every gap references specific data (URLs, keywords, metrics)
├── Score on traffic potential + competitive advantage + business impact
├── Group: Quick Wins / Strategic Builds / Experimental
├── No generic recommendations — every suggestion is specific
└── Frame as experiments with hypotheses

OUTPUT
├── Executive summary maximum 12 pages
├── Every finding tied to a data point
├── Actual URLs analyzed, not descriptions
├── Use docx skill for file generation
└── Experiments feed an experimentation roadmap
```

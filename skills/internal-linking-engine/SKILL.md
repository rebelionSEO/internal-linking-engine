---
name: internal-linking-engine
license: Apache-2.0
description: 'Analyze a website internal linking structure and generate strategic recommendations based on topical clustering, funnel stage logic, and conversion path optimization. Use when the user asks about internal linking audits, internal linking strategy, link mapping, topical authority, orphan page detection, link equity distribution, conversion path analysis, content silos, hub pages, pillar-cluster structure, or link gap analysis. Works with Screaming Frog MCP, manually uploaded CSV exports, or Claude web scraping as a fallback for sites without a crawl available.'
compatibility: "Claude Code >=1.0. Optional: Screaming Frog MCP for direct crawl access."
metadata:
  author: gmejia
  tags:
    - seo
    - internal linking
    - site architecture
    - topical authority
    - funnel optimization
    - link equity
---

# Internal Linking Opportunity Engine

## Purpose

This skill transforms internal linking from a manual, error-prone task into a structured,
phased workflow with human validation at every strategic decision point. It analyzes a site's
content inventory, classifies pages by role and funnel stage, proposes topical clusters, detects
linking gaps, and generates prioritized linking recommendations — each with explicit reasoning,
directional logic, and conversion path awareness.

The core principle: **Claude does the grunt work, the user makes the strategic calls.**
Claude never autonomously decides cluster assignments or linking strategy. Every classification
and cluster proposal is presented for user validation before recommendations are generated.

---

## Architecture Overview

The skill operates in 6 sequential phases. Each phase produces an output that the user reviews
before the next phase begins. Never skip phases or combine them without user approval.

```
Phase 0: Clean Crawl & Data Filtering
Phase 1: Deep Content Inventory & Page Classification
Phase 2: Topical Cluster Proposals (user validates)
Phase 3: Funnel Stage Assignment & Directional Rules
Phase 4: Gap Detection on Validated Structure
Phase 5: Prioritized Link Recommendations + Visual Map
```

---

## Data Sources

### Primary: Screaming Frog MCP (preferred)

If Screaming Frog MCP is connected, use it to pull data directly:

1. **List available crawls** using `screaming-frog:list_crawls`
2. **Export crawl data** using `screaming-frog:export_crawl` with these tabs:
   - `Internal:All` -> full URL inventory with status codes, indexability, word count
   - `Page Titles:All` -> title tags per URL
   - `H1:All` -> H1 headings per URL
   - `H2:All` -> H2 headings per URL (critical for topical depth analysis)
   - `Meta Description:All` -> meta descriptions per URL
   - `Canonicals:All` -> canonical tag data for deduplication
   - `Directives:All` -> noindex/nofollow directives
   - Bulk exports: `All Inlinks,All Outlinks` -> the actual link graph
3. **Read the exported data** using `screaming-frog:read_crawl_data`

### Secondary: Manual CSV Uploads

If MCP is not available, request these CSV files from the user:
- Screaming Frog Internal HTML export
- Screaming Frog All Inlinks export
- Screaming Frog All Outlinks export
- Sitemap URL list (XML or plain text)

### Tertiary: Claude Web Scraping (fallback only)

> ⚠️ **DISCLAIMER — read before using this mode:**
> Web scraping via Claude has significant limitations. Use it ONLY when the user has no sitemap
> and no Screaming Frog crawl available. Always present this disclaimer to the user:
>
> _"Claude will attempt to crawl this site by fetching pages with WebFetch. Results will be
> incomplete and may contain inaccuracies. JavaScript-rendered content (React, Vue, Next.js SPAs)
> will not be captured. The link graph extracted from HTML will miss dynamically injected links.
> Topical classifications based on scraped content are estimates — verify before acting on them.
> For production-grade analysis, run a Screaming Frog crawl or export your XML sitemap first."_

**When to offer scraping mode:** Only when the user explicitly says they have no sitemap and no
SF crawl, AND the site appears to be a small content site (under ~200 pages).

**Scraping procedure (small sites only):**
1. Fetch `https://[domain]/sitemap.xml` and `https://[domain]/sitemap_index.xml` first —
   if either returns a valid XML sitemap, parse URLs from it (do not scrape)
2. If no sitemap, fetch the homepage and extract all `<a href>` internal links
3. Fetch each discovered URL (up to 150 pages max), extracting:
   - `<title>`, `<h1>`, `<h2>` tags
   - `<meta name="description">` content
   - All `<a href>` internal links (for link graph)
   - Approximate word count from `<body>` text
4. After each batch of 20 pages, pause and report progress to the user
5. Deduplicate URLs, strip query parameters, skip non-HTML resources

**Hard limits for scraping mode:**
- Maximum 150 pages — stop and warn the user if the site is larger
- Do not scrape pages behind login, CAPTCHA, or rate-limiting (respect 429 responses)
- Do not attempt to scrape e-commerce sites with product catalogs (see large-site guidance below)

### Large Site Guidance (E-commerce & Enterprise)

> ⚠️ **For sites with 1,000+ pages (Shopify, WooCommerce, Magento, enterprise CMS):**
> Claude web scraping is not appropriate. The data volume, JavaScript rendering requirements,
> and faceted URL explosion (filters, sort parameters, pagination) make scraping unreliable
> and incomplete. Use one of these approaches instead:

| Approach | Best For | How |
|---|---|---|
| **Screaming Frog + sitemap crawl** | Any large site | SF → Config → Crawl from sitemap → export Internal, Inlinks |
| **Screaming Frog with URL list** | Known page sets | Paste priority URLs into SF → Mode: List → crawl targeted subset |
| **GSC Sitemap report** | Quick URL export | GSC → Index → Sitemaps → click sitemap → download URL list |
| **SF crawl with JavaScript rendering** | SPAs / Next.js / Nuxt | SF → Config → Spider → Rendering → JavaScript |
| **Crawl budget: by section** | Very large catalogs | Crawl `/blog/`, `/services/`, `/case-studies/` separately, merge exports |

**Recommended Screaming Frog settings for large sites:**
- Set crawl limit to 5,000 URLs for initial audit (SF → Config → Limits)
- Enable "Store HTML" only if you need content analysis (uses more memory)
- Export `internal_all.csv` + `all_inlinks.csv` — these two files are sufficient for this skill
- For sites over 50k pages: use SF's "Crawl from sitemap" mode to target indexable pages only

### Optional Enrichment (significantly improves accuracy)

- **GSC query data** (CSV export, last 3-6 months) -> reveals what keywords each page actually
  ranks for, making topical clustering much sharper than relying on on-page elements alone
- **GA4 landing page data** (CSV export) -> enables traffic-weighted prioritization so
  high-traffic pages with poor linking get fixed first

---

## Phase 0: Clean Crawl & Data Filtering

Before any analysis, apply strict filters to eliminate noise. This phase is fully automated
with no user input required.

### Mandatory Inclusion Criteria

Only retain pages that meet ALL of these conditions:
- HTTP status code is `200`
- Content type is `text/html`
- Page is indexable (no `noindex` directive in meta robots or X-Robots-Tag)
- Page is the canonical version (canonical URL points to itself, or no canonical tag present)
- URL does not contain query parameters (`?sort=`, `?page=`, `?filter=`, `?utm_`, etc.)

### Mandatory Exclusion Criteria

Remove any page matching ANY of these patterns:
- Utility pages: URLs containing `/privacy`, `/terms`, `/legal`, `/cookie`, `/login`,
  `/register`, `/cart`, `/checkout`, `/account`, `/wp-admin`, `/wp-login`
- Pagination pages: URLs matching `/page/2/`, `/page/3/`, etc.
- Tag/archive pages: URLs containing `/tag/`, `/author/`, `/archive/`
- Media/asset pages: URLs ending in image, PDF, or document extensions
- Staging/dev pages: URLs on subdomains like `staging.`, `dev.`, `test.`
- Cloudflare challenge pages, maintenance pages, or error templates
- Pages with word count below 100 (likely thin/placeholder content)

### Output of Phase 0

A clean URL list with columns:
`URL | Title | H1 | H2s | Meta Description | Word Count | Inlinks Count | Outlinks Count | Indexable | Canonical`

Report to user: "Filtered [X] raw URLs down to [Y] content pages. Removed [Z] non-indexable,
[N] non-canonical, [M] utility/thin pages. Ready for Phase 1?"

---

## Phase 1: Deep Content Inventory & Page Classification

### What to Analyze Per Page

Do NOT rely solely on title tags. Analyze all available signals:

| Signal | What It Tells Us |
|---|---|
| URL path structure | Structural role (blog, service, product, resource) |
| Title tag | Primary topic |
| H1 | Content focus (may differ from title) |
| H2 headings | Subtopic coverage and content depth |
| Meta description | User intent signal — what the page promises |
| Word count | Depth indicator — thin pages cannot be pillars |
| Inlinks count | Current internal authority received |
| Outlinks count | Current linking generosity |

### Page Role Classification

Assign each page exactly ONE role:

| Role | Definition | Typical Signals |
|---|---|---|
| **Pillar** | Broad topic hub, comprehensive coverage | High word count (1500+), broad H2 coverage, multiple subtopics addressed |
| **Supporting** | Deep dive on a specific subtopic | Focused H2s, moderate word count (500+), narrow topic scope |
| **Conversion** | Action page — service, product, pricing, contact, demo | URL contains /services/, /products/, /pricing/, /contact/, /get-started/, /demo/ |
| **Utility** | Functional pages — about, team, FAQ, careers | Not part of topical clusters, low linking priority |
| **Dead Weight** | Thin content, outdated, duplicate-intent pages | Word count below 300, no unique keyword target, duplicate H1s |

### Confidence Scoring

Every classification gets a confidence level:
- **High** — signals are clear and consistent (e.g., /services/seo/ with transactional title)
- **Medium** — mixed signals, reasonable classification but could go either way
- **Low** — ambiguous, user MUST review and decide

### Output of Phase 1

A classification table presented to the user for review:

```
| URL | Title | Proposed Role | Confidence | Reasoning |
|-----|-------|---------------|------------|-----------|
```

Explicitly flag every Medium and Low confidence classification.
Ask: "Review the classifications above. Adjust any that don't match your strategy, especially
the Medium/Low confidence ones. Once confirmed, we move to cluster proposals."

**Do NOT proceed to Phase 2 until the user confirms or adjusts classifications.**

---

## Phase 2: Topical Cluster Proposals

### Clustering Logic

Group pages into topical clusters based on semantic meaning, NOT just URL folder structure.
Pages in different folders can (and often do) belong to the same cluster.

Analyze the combination of title + H1 + H2s + meta description to identify shared topic themes.

**Example of correct cross-folder clustering:**
```
Cluster: "Local SEO"
+-- /blog/what-is-local-seo/           (Supporting — Awareness)
+-- /blog/google-business-profile-tips/ (Supporting — Consideration)
+-- /case-studies/local-seo-restaurant/ (Supporting — Consideration)
+-- /services/local-seo/               (Conversion — Decision)
```
These pages live in 3 different folders but form one coherent topical cluster.

### Two-Way Validation

**Option A — Claude proposes, user validates:**
Present each proposed cluster with its member pages and ask the user to confirm, merge,
split, or reassign pages.

**Option B — User provides clusters, Claude validates:**
If the user provides their own pillar/cluster definitions, cross-reference them against the
crawl data and flag:
- Pages the user may have missed
- Pages that don't fit where the user placed them
- Clusters with too few supporting pages
- Clusters without a clear conversion page target

### Cluster Requirements

Each valid cluster MUST have:
- At least 1 pillar page (or a page that should become the pillar)
- At least 2 supporting pages
- At least 1 conversion page target (can be shared across clusters if relevant)

If a cluster lacks any of these, flag it and propose solutions (create content, reassign pages,
merge with another cluster).

### Output of Phase 2

```
CLUSTER: [Cluster Name]
  Pillar: [URL] — [Title]
  Supporting:
    - [URL] — [Title] — [Funnel Stage TBD]
    - [URL] — [Title] — [Funnel Stage TBD]
  Conversion Target: [URL] — [Title]

FLAGGED:
  - [URL] could belong to Cluster A or Cluster B — user decision needed
  - Cluster [Name] has no clear conversion page — content gap?
```

**Do NOT proceed to Phase 3 until the user confirms or adjusts clusters.**

---

## Phase 3: Funnel Stage Assignment & Directional Rules

### Funnel Stage Classification

Assign every page in validated clusters to exactly ONE funnel stage:

| Stage | Definition | Typical Signals |
|---|---|---|
| **Awareness** | "What is this?" — educational, introductory | Titles with "what is", "guide to", "introduction", "101", "explained" |
| **Consideration** | "How do I choose/do this?" — evaluative, comparative | Titles with "how to", "best", "vs", "tips", "checklist", "comparison" |
| **Decision** | "I'm ready to act" — transactional, conversion-oriented | Service pages, product pages, pricing, contact, demo, free trial |

### THE CRITICAL DIRECTIONAL RULES

These rules are the core differentiator of this skill. They prevent the most common and
damaging internal linking mistake: sending users BACKWARDS in the funnel away from conversion.

#### Rule 1: Never Link Backwards as Primary Path

A page at a later funnel stage must NEVER have its primary contextual link pointing to an
earlier funnel stage.

```
BLOCKED: Consideration -> Awareness (as primary/contextual link)
   Example: "Local SEO Tips" linking to "What is Local SEO?" as the next step

ALLOWED: Consideration -> Decision (forward movement)
   Example: "Local SEO Tips" linking to "Local SEO Services"

ALLOWED: Awareness -> Consideration -> Decision (forward progression)
   Example: "What is Local SEO?" -> "Local SEO Tips" -> "Local SEO Services"
```

#### Rule 2: Authority Links vs User Path Links — Separate Them

A supporting page CAN link back to its pillar for SEO authority flow purposes, but this
link must be tagged as an **authority link**, NOT a **user path link**.

- **User path link**: Contextual link within the content body that guides the reader to
  their logical next step. This is what the user clicks. MUST move forward or to conversion.
- **Authority link**: Structural link (breadcrumb, sidebar, related posts section, or
  in-content reference) that passes topical authority. Can point in any direction.

The skill must distinguish these in its output.

#### Rule 3: Every Cluster Must Have a Conversion Shortcut

Even from awareness-stage pages, there must always be at least one direct path to the
conversion page. A user reading "What is Local SEO?" might already be ready to buy — they
should never be forced through 3 intermediate pages to reach the service page.

```
Required minimum paths per cluster:
  Awareness -> Conversion (direct shortcut, always available)
  Awareness -> Consideration -> Conversion (progressive path)
  Consideration -> Conversion (direct, primary path)
```

#### Rule 4: Maximum 2 Clicks to Conversion

No page within a cluster should be more than 2 clicks away from the cluster's conversion
page. If a page requires 3+ clicks to reach conversion, that's a **critical gap**.

#### Rule 5: Anti-Pattern Detection

The skill must actively scan for and flag these harmful patterns:

| Anti-Pattern | Description | Severity |
|---|---|---|
| **Funnel Regression** | Consideration page's primary link goes to Awareness page | [CRITICAL] |
| **Conversion Detour** | 3+ clicks required from any page to reach conversion | [CRITICAL] |
| **Dead-End Content** | Page has outlinks only to same-stage or earlier-stage content | [HIGH] |
| **Missing Shortcut** | Awareness page has no direct path to conversion | [HIGH] |
| **Orphan in Cluster** | Page belongs to a cluster but receives 0 inlinks from cluster members | [HIGH] |
| **Cross-Cluster Leak** | Page links heavily outside its cluster while ignoring cluster siblings | [MEDIUM] |

---

## Phase 4: Gap Detection on Validated Structure

Run gap analysis ONLY on the user-validated cluster structure from Phase 2 with the funnel
stage assignments from Phase 3.

### Gap Types to Detect

1. **Pillar <- Supporting (missing)**: Supporting page does not link to its pillar.
   Impact: Weakens hub authority concentration.

2. **Pillar -> Supporting (missing)**: Pillar does not link down to a supporting page.
   Impact: Supporting page is orphaned from the hub.

3. **Supporting -> Conversion (missing)**: No forward path from supporting content to the
   conversion page. Impact: User journey dead-ends at informational content.

4. **Awareness -> Conversion shortcut (missing)**: Awareness pages have no direct link to
   conversion. Impact: Ready-to-buy users are forced through unnecessary steps.

5. **Cross-cluster bridge (opportunity)**: Two clusters share a natural user journey connection
   but have no links between them. Example: "CRM Software" cluster and "Sales Automation"
   cluster — a user in one is likely interested in the other.

6. **Orphan pages**: Pages that belong to a cluster but receive zero internal links from
   any other page in that cluster.

7. **Over-linked pages**: Pages receiving disproportionately many internal links relative to
   their role — may be cannibalizing link equity from more important pages.

### Prioritization Logic

Rank all gaps by business impact:

| Priority | Criteria |
|---|---|
| [CRITICAL] | Conversion page receives 0 links from its cluster. Funnel regression detected. |
| [HIGH] | Supporting page doesn't link to pillar. No conversion shortcut from awareness. Dead-end page. |
| [MEDIUM] | Missing cross-cluster bridge. Over-linked non-critical page. |
| [LOW] | Minor authority flow optimization. Anchor text improvements on existing links. |

---

## Phase 5: Prioritized Link Recommendations + Visual Map

### Recommendation Format

Every recommendation includes ALL of the following columns. No exceptions.

```
| # | Source URL | Target URL | Suggested Anchor Text | Link Type | Direction | Priority | Reasoning |
```

**Column definitions:**

- **Link Type**: `User Path` (contextual, in-content, guides the reader) or `Authority`
  (structural, sidebar, breadcrumb, passes equity)
- **Direction**: Must indicate funnel movement. One of:
  - `Forward -> Conversion` (Consideration/Awareness page linking to Decision page)
  - `Forward -> Consideration` (Awareness page linking to Consideration page)
  - `Up -> Pillar` (Supporting page linking to its hub)
  - `Down -> Supporting` (Pillar linking to its supporting pages)
  - `Lateral -> Same Stage` (Same-stage pages in the same cluster)
  - `Bridge -> Cross-Cluster` (Connecting related clusters)
- **Priority**: [CRITICAL], [HIGH], [MEDIUM], [LOW]
- **Reasoning**: One sentence explaining WHY this link should exist. Always reference the
  funnel logic or topical authority logic. Never generic.

### What to NEVER Recommend

- A user-path link from Consideration to Awareness content
- A user-path link from Decision to Awareness content
- Links to non-indexable, non-canonical, or dead-weight pages
- Anchor text that is generic ("click here", "read more", "learn more")
- Anchor text that exactly matches the target page's title tag (over-optimization risk)
- More than 3-5 new internal links per source page (diminishing returns, link dilution)

### Visual Map Output

Generate a React artifact (interactive node graph) with:
- Each node = one page, sized by relative importance (inlinks + word count)
- Color-coded by cluster membership
- Node shape or border indicates funnel stage (circle = awareness, square = consideration,
  diamond = conversion)
- **Solid lines** = existing internal links
- **Dashed lines in highlight color** = recommended new links
- Cluster grouping visible (nodes in same cluster are spatially grouped)
- Click a cluster to isolate and inspect its internal structure
- Legend explaining all visual encodings

Use a force-directed graph layout (d3-force or similar). Ensure conversion pages are
visually prominent — larger, distinct color, positioned centrally within their cluster.

---

## Handling Large Sites

Internal linking analysis can hit context window limits on large sites. Apply these rules:

### Sites under 100 pages
- Process all phases in a single flow.

### Sites 100-500 pages
- Phase 0 and 1: Process all pages for classification.
- Phase 2 onward: Process one cluster at a time. Complete all phases for Cluster A before
  moving to Cluster B.
- Final visual map: Generate after all clusters are processed.

### Sites 500+ pages
- Phase 0: Process all pages for filtering.
- Phase 1: Process in batches of 100 URLs. Present classification batches for user review.
- Phase 2 onward: Process one cluster at a time.
- Recommend the user prioritize their top 3-5 clusters first rather than attempting the
  full site at once.
- Alert the user: "This site has [X] content pages. I recommend we focus on your highest-
  priority clusters first and expand later. Which topics matter most to your business?"

---

## User Interaction Guidelines

1. **Always present, never decide.** Classifications, clusters, and funnel stages are
   proposals. The user confirms before the skill proceeds.

2. **Flag ambiguity explicitly.** If a page could belong to two clusters, or its funnel
   stage is unclear, say so. Never silently pick one.

3. **Explain every recommendation.** No black-box suggestions. If a user disagrees with a
   recommendation, the reasoning is right there for evaluation.

4. **Accept user overrides gracefully.** If the user reclassifies a page or moves it to a
   different cluster, adjust all downstream analysis accordingly without questioning unless
   the override creates a logical conflict (e.g., assigning a blog post as a conversion page).

5. **Ask about business context early.** Before Phase 2, ask: "What are your primary
   service/product categories? What pages are your most important conversion targets?"
   This context shapes everything downstream.

6. **Respect the phased workflow.** If the user tries to jump to recommendations before
   validating clusters, gently redirect: "I want to make sure the cluster structure is
   right before generating recommendations — wrong clusters mean wrong links. Can we
   confirm these first?"

---

## Quick Reference: The Rules Engine

```
FILTERING RULES
+-- Only 200-status, indexable, canonical, HTML pages with real content
+-- Exclude utility, pagination, parameter, staging, thin pages
+-- Minimum 100 word count to qualify

CLASSIFICATION RULES
+-- Every page gets exactly ONE role (Pillar/Supporting/Conversion/Utility/Dead Weight)
+-- Every classification gets a confidence score (High/Medium/Low)
+-- Medium and Low confidence MUST be flagged for user review

CLUSTER RULES
+-- Group by semantic meaning, NOT by URL folder
+-- Every cluster needs: 1+ pillar, 2+ supporting, 1+ conversion target
+-- User validates all clusters before gap analysis runs
+-- Two-way validation: Claude proposes OR user provides, other side validates

DIRECTIONAL RULES (most critical)
+-- User path links MUST move forward in funnel or direct to conversion
+-- NEVER recommend consideration -> awareness as a user path link
+-- Authority links (pillar reinforcement) can go any direction — tag them separately
+-- Every cluster must have a direct awareness -> conversion shortcut
+-- Maximum 2 clicks from any page to its cluster's conversion page
+-- Flag all funnel regressions, conversion detours, and dead-end content

RECOMMENDATION RULES
+-- Every link recommendation includes: source, target, anchor, type, direction, priority, reasoning
+-- Never suggest generic anchor text
+-- Never suggest links to non-indexable or dead-weight pages
+-- Max 3-5 new links recommended per source page
+-- Prioritize by business impact: conversion gaps first, authority flow second
```

---

## Implementation Notes (from azariangrowthagency.com test run, 2026-03-11)

### filter.py fixes applied
- **NUL bytes in SF exports**: Wrap CSV reads with `csv.DictReader(line.replace('\x00', '') for line in f)` and use `errors='replace'` in `open()`. Both `load_h2s()` and main loop need this.
- **Python 3.9 compatibility**: Avoid `str | None` union syntax in type hints (requires 3.10+). Use bare `def filter_reason(row: dict, url: str):` with no return annotation.
- **Blog pagination pattern**: Updated `PAGINATION_PATTERN` to catch `/blog/\d+/` in addition to `/page/\d+/`.

### Key findings pattern (likely repeatable on agency sites)
- **Zero editorial inlinks to conversion pages** is a near-universal issue on content-heavy B2B agency sites. The pillar page absorbs all equity; conversion pages survive only on nav links.
- **"Explore Our Case Studies" regression pattern**: Any page with a case-study showcase section will link backward to Consideration from Decision. Reclassify as Authority links; add forward CTAs in the same section.
- **Webinars as independent pillar**: Webinar/event format pages warrant their own cluster, separate from blog/podcast Consideration content, due to distinct funnel behavior and page structure.
- **PE/VC cluster**: Thin content clusters should still be modeled — they define the lead qualification filter even when few pages exist. Prioritize building out over deprioritizing.
- **Tools/Calculators**: One hub page is sufficient for all calculator tools; avoids diluted authority across multiple thin hub pages.

### SF export field names (confirmed)
- Internal: `Address`, `Status Code`, `Content Type`, `Indexability`, `Indexability Status`, `Title 1`, `H1-1`, `H2-1`, `H2-2`, `Meta Description 1`, `Word Count`, `Inlinks`, `Unique Inlinks`, `Outlinks`, `Canonical Link Element 1`, `Meta Robots 1`
- All Inlinks: `Source`, `Destination`, `Anchor`, `Link Position`, `Follow`
- H2 export: `Address`, `H2-1` (one row per H2; use `load_h2s()` to aggregate)

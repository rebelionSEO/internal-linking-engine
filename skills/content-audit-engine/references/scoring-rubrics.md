# Scoring Rubrics

## Topical Depth Score (1–5 per page)

### Scoring Inputs and Weights

| Input | Weight | How to Measure |
|---|---|---|
| Word count | 30% | From Screaming Frog export, or estimate from web fetch |
| H2 subtopic coverage | 30% | Count of H2s that address distinct relevant subtopics |
| GSC keyword breadth | 20% | Number of distinct queries the page ranks for (any position) |
| Traffic vs cluster peers | 10% | Percentile rank within the cluster by clicks |
| GA4 engagement | 10% | Engaged session rate vs site average (skip if no GA4) |

### Score Definitions with Full Criteria

**Score 1 — Thin**
- Word count: < 300 words
- H2s: 0–1, covering only the most obvious angle
- GSC queries: 0–3 keywords ranked
- Characteristics: Could be replaced by a paragraph, no unique insights, reads like an AI stub or placeholder
- Examples: Landing page with just a tagline + CTA, short news blurb, stub article

**Score 2 — Basic**
- Word count: 300–800 words
- H2s: 1–3, covering intro-level aspects
- GSC queries: 3–10 keywords ranked
- Characteristics: Answers the primary question at surface level, no depth on edge cases or subtopics, introductory tone
- Examples: Short blog post covering "what is X", thin how-to with 3 steps

**Score 3 — Adequate**
- Word count: 800–1,500 words
- H2s: 3–5, covering core subtopics
- GSC queries: 10–30 keywords ranked
- Characteristics: Meets user intent, provides actionable value, some original perspective, covers the topic without going deep
- Examples: Standard blog post on a specific tactic, solid service page, basic guide with examples

**Score 4 — Strong**
- Word count: 1,500–3,000 words
- H2s: 5–8, including edge cases and nuanced subtopics
- GSC queries: 30–100 keywords ranked
- Characteristics: Above-average depth, includes original data or unique insight, covers the topic more comprehensively than most competing pages, expert-level perspective visible
- Examples: Long-form how-to guide, detailed comparison post, case study with deep analysis

**Score 5 — Authoritative**
- Word count: 3,000+ words
- H2s: 8+, comprehensive subtopic coverage including edge cases, FAQs, related topics
- GSC queries: 100+ keywords ranked
- Characteristics: Best-in-class for this topic, includes original research or data, becomes a reference others cite, comprehensive enough to replace multiple thinner articles
- Examples: Ultimate guide, original research report, comprehensive resource hub, authoritative pillar page

### Depth Score Without Crawl Data

If no Screaming Frog data and no web fetch available:
1. Use GSC keyword breadth as the primary signal (60% weight)
2. Use traffic tier as secondary signal (40% weight)
3. Mark score as `[inferred]` in the output
4. Web fetch the page if it ranks in positions 1–20 on a target keyword

### Depth Score Calibration Rule

After scoring the first 20–30 pages, recalibrate if needed:
- If > 60% of pages score 4 or 5, the bar may be set too low — raise it
- If > 60% of pages score 1 or 2, the bar may be too high — verify by sampling
- The distribution across a typical site with mixed content should approximate: 20% (1–2), 50% (3), 30% (4–5)

---

## Topical Coverage Score (1–5 per cluster)

### Coverage Score Definitions

**Score 1 — Minimal**
- 1–2 pages total in the cluster
- Only covers the broadest angle of the topic
- Missing: most subtopics, most audience angles, most content formats
- Action: Major content build needed

**Score 2 — Partial**
- 3–5 pages in the cluster
- Covers 2–3 subtopics but major gaps remain
- Missing: depth pages, consideration-stage content, case studies
- Action: Prioritize 3–5 specific subtopic additions

**Score 3 — Moderate**
- 6–10 pages in the cluster
- Core subtopics covered, pillar exists, some supporting content
- Missing: long-tail coverage, niche audience angles, format diversity
- Action: Identify top 3–5 gaps from competitor analysis

**Score 4 — Strong**
- 10–20 pages in the cluster
- Comprehensive coverage of main and most secondary subtopics
- Pillar + multiple supporting pages + at least one case study or data piece
- Missing: possibly comparison content, FAQ content, or very specific niches
- Action: Optimize existing content depth, fill remaining niche gaps

**Score 5 — Dominant**
- 20+ pages in the cluster
- Full subtopic depth, multiple content formats, multiple audience angles
- Pillar + supporting + case studies + tools + comparison pages
- Action: Maintain quality, monitor competitor moves, refresh aging content

### Coverage Score Inputs

| Signal | How to Measure |
|---|---|
| Total pages in cluster | Count from Phase 1 cluster map |
| Subtopic breadth | Compare cluster H2s against "what subtopics should this topic cover" (use web search for top competitor H2 structure) |
| Format diversity | Count distinct formats represented in cluster |
| Audience angle diversity | Does the cluster address different use cases/personas? |
| Funnel stage coverage | Are all three stages (Awareness/Consideration/Decision) represented? |

---

## Performance Tier Criteria

### Tier Definitions with Specific Thresholds

**⭐ Top Performer**
- Clicks: Top 10% of all pages in the site by click volume
- Impressions: Top 20% by impression volume
- If GA4 available: Engagement rate > 55% AND avg engagement time > 90 seconds
- Note: A page can be a top performer by traffic even with mediocre engagement

**✅ Performing**
- Clicks: Between 25th and 90th percentile
- Impressions: Any meaningful impression volume (> 100/month)
- If GA4 available: Engagement rate between 35–55%
- Position: At least one keyword in top 20

**⚠️ Underperforming**
- Impressions: > 500/month (visible in SERPs) BUT clicks < 50/month
- CTR: Below 2% on queries with > 500 impressions (indicates title/meta issue)
- OR: Position 5–20 on target keyword with low traffic (ranking but not converting clicks)
- Action priority: Title/meta optimization, depth improvement

**🔻 Declining**
- Requires: Date-segmented GSC data (compare H1 vs H2 of the 6-month window)
- Traffic dropped > 30% half-over-half OR position dropped > 5 spots on primary keyword
- Flag if formerly a Top Performer or Performing page
- Action priority: Content refresh — likely outdated information

**❌ Dead Weight**
- Clicks: < 5/month
- Impressions: < 50/month (practically invisible)
- No keywords ranked in top 50
- Page age: > 6 months (new pages excluded)
- Action: Prune (301 redirect to relevant page) or refresh with significant new content

### Performance Tier Without GA4

If no GA4 data:
- Remove engagement from tier criteria entirely
- Weight GSC clicks and impressions at 70%, position data at 30%
- Mark all tiers as `[traffic-only]` to indicate engagement not assessed
- Upgrade pages to "Underperforming" if CTR < 1.5% with > 1,000 impressions

---

## Opportunity Score Calculation

### Scoring Formula

```
Opportunity Score = (Traffic Potential × 0.4) + (Competitive Advantage × 0.3) + (Business Impact × 0.3)
```

Each dimension scored 1–10.

### Traffic Potential (1–10)

| Score | Criteria |
|---|---|
| 9–10 | Target keyword > 5,000 monthly searches, position > 20 or not ranking |
| 7–8 | Target keyword 1,000–5,000 searches, position > 10 or not ranking |
| 5–6 | Target keyword 200–1,000 searches, moderate competition |
| 3–4 | Target keyword < 200 searches OR already ranking well (position 1–5) |
| 1–2 | Very niche, unclear search demand, or already captured |

Use keyword volume from Ahrefs if available, otherwise estimate from GSC impressions or web search results.

### Competitive Advantage (1–10)

| Score | Criteria |
|---|---|
| 9–10 | Competitors' content is thin (avg depth < 3), client has genuine expertise here |
| 7–8 | Competitors cover this but not comprehensively, client can differentiate with depth or format |
| 5–6 | Competitors have solid content, but client has a unique angle or data point |
| 3–4 | Competitors have strong, well-ranking content, client has no obvious differentiator |
| 1–2 | Dominated by authoritative competitors (major publications, Wikipedia), very hard to compete |

### Business Impact (1–10)

| Score | Criteria |
|---|---|
| 9–10 | Directly maps to a primary service/product, high purchase intent keyword |
| 7–8 | Maps to a secondary service, mid-funnel content that drives consideration |
| 5–6 | Builds brand authority in core topic area, indirect revenue connection |
| 3–4 | Topically relevant but weak revenue connection |
| 1–2 | Tangential topic, no clear path to conversion |

### Effort Estimate

| Effort | Definition |
|---|---|
| Low | Can be done in < 4 hours: title refresh, depth addition to existing page, add 1–2 H2s |
| Medium | 4–16 hours: significant rewrite, new 1,500-word page on known topic, format change |
| High | > 16 hours: new pillar page, original research, new content format (tool/calculator) |

### Opportunity Categories

After scoring all opportunities:

**Quick Wins** — Score ≥ 6.0 AND Effort = Low
- Typically: refresh existing pages, add depth to underperforming content,
  fix title/meta for pages with high impressions + low CTR, internal linking improvements

**Strategic Builds** — Score ≥ 6.0 AND Effort = Medium or High
- New pillar pages, new cluster build-outs, original research pieces,
  tools/calculators, comparison content

**Experimental** — Score 3.0–5.9 AND Effort = Low
- Test new formats, test AI overview optimization tactics,
  create thin version of uncertain-demand content to validate before full investment

**Deprioritized** — Score < 3.0 OR (Score < 5.0 AND Effort = High)
- Not worth pursuing in the current roadmap cycle
- Flag but don't include in top recommendations

---

## Scoring Output Templates

### Page-Level Output
```
URL: /blog/saas-email-marketing/
Cluster: SaaS Growth
Type: Blog Post | Format: How-to
Depth Score: 3/5 (Adequate)
  - Word count: 1,100 (signal: 3)
  - H2 coverage: 4 subtopics (signal: 3)
  - GSC keywords: 18 queries ranked (signal: 3)
  - Traffic tier: 45th percentile in cluster (signal: 2)
  - GA4 engagement: 51% engaged sessions (signal: 3)
Performance Tier: ✅ Performing
Top Keywords: "saas email marketing" (pos 11), "email marketing for saas" (pos 14)
Action: Depth improvement — add 3 H2s on segmentation, drip sequences, metrics
```

### Cluster-Level Output
```
Cluster: SaaS Growth Marketing
Pages: 12 total
Avg Depth Score: 2.8/5
Coverage Score: 3/5 (Moderate)
Traffic Share: 18% of site total clicks
Top Performer: /blog/saas-growth-hacking/ (340 clicks/mo)
Performance Distribution: 1 Top Performer, 4 Performing, 5 Underperforming, 2 Dead Weight
Biggest Gap: No comparison content, no case studies, no decision-stage landing page
```

### Opportunity-Level Output
```
# | Opportunity | Cluster | Type | Score | Effort
1 | Create "HubSpot vs Salesforce for SaaS" comparison | SaaS Growth | Topic Gap | 7.8 | Medium
  - Traffic Potential: 8/10 (keyword vol ~2,400/mo, client not ranking)
  - Competitive Advantage: 7/10 (competitors have comparison pages but thin)
  - Business Impact: 9/10 (high purchase intent, directly maps to CRM consulting service)
  - Hypothesis: Comparison page targeting "hubspot vs salesforce saas" could reach position 5–8
    based on SERP patterns showing comparison content ranks for this keyword type
  - Action: Create 2,500-word comparison guide, target "best crm for saas" cluster
```

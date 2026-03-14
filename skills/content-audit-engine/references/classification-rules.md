# Classification Rules

## Content Type Taxonomy

### Decision Tree — Assign Exactly ONE Type

```
START → Is the primary goal of this page to get a conversion (form, purchase, contact)?
  YES → Landing Page
  NO  → Is it a specific client story with measurable results?
          YES → Case Study
          NO  → Is it primarily an interactive utility (calculator, tool, generator)?
                  YES → Tool/Calculator
                  NO  → Is it comparing two or more products/services/approaches?
                          YES → Comparison
                          NO  → Is it defining a single term or concept (< 600 words)?
                                  YES → Glossary/Definition
                                  NO  → Is it a time-sensitive company/industry announcement?
                                          YES → News/Update
                                          NO  → Is it primarily a list of links to other content?
                                                  YES → Hub/Index
                                                  NO  → Is it 2,000+ words with 5+ structured H2s?
                                                          YES → Guide/Resource
                                                          NO  → Blog Post
```

### Content Types — Full Definitions

| Type | Definition | URL Signals | Content Signals |
|---|---|---|---|
| **Blog Post** | Informational article on a topical subject | `/blog/`, date-based slug | Conversational, 300–2000 words, 2–4 H2s |
| **Guide/Resource** | Long-form educational content, comprehensive coverage | `/guide/`, `/resource/`, `/how-to/` | 2000+ words, 5+ H2s, structured, reference material |
| **Case Study** | Client or project success story with specific results | `/case-study/`, `/case-studies/`, client name in URL | Named client, specific metrics (%, $, timeframes), before/after narrative |
| **Landing Page** | Conversion-focused page for service, product, or campaign | `/services/`, `/products/`, `/solutions/`, geo-targeted slugs | Has CTA button/form, pricing section, or "Contact us" as primary action |
| **Tool/Calculator** | Interactive utility that processes user input | `/tools/`, `/calculator/`, `/generator/` | Interactive element, input fields, computed output |
| **Comparison** | Direct comparison between options | "vs" in URL or title, "alternative" in URL | Side-by-side structure, feature comparison tables |
| **Glossary/Definition** | Short definitional entry | `/glossary/`, "what-is" in slug | < 600 words, single concept, definitional structure |
| **News/Update** | Time-sensitive announcement or event coverage | Date in URL, `/news/`, `/press/`, `/announcements/` | Recent date, event-specific, company or industry news |
| **Hub/Index** | Category or topic index that links to other content | `/topics/`, `/category/`, section root URLs | Mostly links, minimal original prose, organized listing |

---

## Edge Cases and Tie-Breaking Rules

### Blog Post vs Guide/Resource
- Word count < 2,000 AND H2 count < 5 → **Blog Post**
- Word count ≥ 2,000 AND H2 count ≥ 5 → **Guide/Resource**
- Word count ≥ 2,000 but only 2–3 H2s (prose-heavy) → **Blog Post** (not structured enough to be a guide)
- Word count < 2,000 but has 6+ H2s (checklist format) → **Blog Post**
- If in doubt and content is clearly meant as a reference document → **Guide/Resource**

### Landing Page vs Blog Post with commercial intent
- Has a form, pricing, or "get a quote" CTA → **Landing Page** regardless of content length
- Is informational but ends with a CTA → **Blog Post** (CTA doesn't make it a landing page)
- `/services/` URL with long educational content → **Landing Page** (URL and intent override content length)

### Case Study vs Blog Post about a client
- Named client with verifiable specific results (% lift, $ revenue, time to result) → **Case Study**
- Client mentioned in passing with no specific outcome → **Blog Post**
- Anonymized "a Fortune 500 client" with results → **Case Study** (results are what matter)

### Hub/Index vs Pillar Page
- Mostly links to other pages, < 500 words of original prose → **Hub/Index**
- 1,500+ words of original educational content PLUS links to subtopics → **Guide/Resource** (it's a pillar)
- Category archive pages (date-ordered blog listing) → **Hub/Index**

### Ambiguous Cases
When a page could be two types:
1. Assign the type that better reflects user intent (what would a user arriving from search expect?)
2. Note the confidence level: `Guide/Resource (high)` vs `Guide/Resource (medium — could be Blog Post)`
3. Flag ambiguous pages in the Phase 2 output for user review

---

## Content Format Taxonomy

### Format Types — Assign Exactly ONE

| Format | Definition | Key Signals |
|---|---|---|
| **Text-heavy** | Primarily prose, minimal list structure | Long paragraphs, few bullet points, essay structure |
| **Listicle** | Organized around a numbered or bulleted list | "X ways to...", "Top X...", numbered H2s |
| **How-to** | Step-by-step instructional | "How to...", "Step 1/2/3" H2s, sequential structure |
| **Data-driven** | Built around statistics, research, or original data | Charts, stats cited, research methodology, "according to our study" |
| **Interview/Q&A** | Question-and-answer structure | Q: ... A: ... format, named interviewee |
| **Visual/Infographic** | Image or visual is the primary content vehicle | Low text, high image reference, infographic embed |
| **Video-led** | Embedded video is primary, text is secondary | Video embed prominent, transcript or summary below |

### Format Decision Notes

- A "10 best tools" post with detailed tool reviews = **Listicle** (even if long and detailed)
- A comprehensive 5,000-word guide with multiple numbered sections = **How-to** if the sections are sequential steps, **Text-heavy** if they're independent topics
- A post with 12 statistics cited = **Data-driven** only if the data is the structure (not just supporting evidence)
- A post with one embedded video and 800 words of explanation = **Text-heavy** (video is supplementary)

---

## Classification Confidence Levels

Use these when presenting classifications for user review:

| Confidence | When to Use |
|---|---|
| `(confirmed)` | URL pattern AND content signals align clearly |
| `(high)` | One signal is ambiguous but the other is clear |
| `(medium)` | Two possible types — made a judgment call, needs user review |
| `(low)` | Significant ambiguity — flag explicitly for user input |

Example output format:
```
/blog/saas-email-marketing-guide/
  Type: Guide/Resource (high — 3,200 words, 8 H2s, but URL says /blog/)
  Format: How-to (confirmed — sequential step structure)
  Flag: URL in /blog/ folder but content qualifies as guide — may want to move or treat as pillar
```

---

## Pillar vs Supporting Classification

Within a cluster, after content type is assigned, classify each page as:

| Role | Criteria |
|---|---|
| **Pillar** | Highest inlinks received within cluster + broadest keyword footprint + highest traffic + 4–5 depth score |
| **Primary Supporting** | Directly supports pillar topic, 3–4 depth score, moderate traffic |
| **Secondary Supporting** | Specific subtopic, 2–3 depth score, lower traffic |
| **Thin/Dead Weight** | Depth score 1–2, near-zero traffic, no keyword rankings |

**Pillar identification rule:** There should be exactly ONE pillar per cluster. If two pages could both be pillars, the one with more inlinks received wins. Flag this to the user.

**Dead Weight identification rule:** A page is Dead Weight if ALL of:
- Traffic tier: ❌ Dead Weight
- Depth score: 1 or 2
- No keywords ranking in top 50 in GSC
- Age: published more than 6 months ago (if date available)

Pages that are new (< 6 months old) with low traffic are NOT automatically Dead Weight — they may just be indexing.

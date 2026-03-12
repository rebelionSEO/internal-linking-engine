# Internal Linking Engine

A Claude skill for analyzing and improving a website's internal linking structure. Built for SEO professionals and agencies who want a repeatable, strategic process — not just a list of suggestions.

The skill runs a 6-phase workflow where Claude does the grunt work and you make the strategic calls. Every classification and cluster assignment is proposed, not assumed, and waits for your confirmation before moving forward.

---

## What it does

- **Phase 0** — Filters a raw Screaming Frog crawl down to clean, indexable content pages
- **Phase 1** — Classifies every page by role (Pillar, Supporting, Conversion, Utility, Dead Weight) and confidence level
- **Phase 2** — Proposes topical clusters based on semantic meaning, not folder structure — you validate or adjust
- **Phase 3** — Assigns funnel stages (Awareness / Consideration / Decision) and enforces directional link rules
- **Phase 4** — Detects linking gaps: orphan pages, zero-inlink conversion pages, funnel regressions
- **Phase 5** — Generates prioritized recommendations with anchor text, link type, and reasoning, plus an interactive React + SVG visual map

---

## Data sources

| Source | When to use |
|---|---|
| **Screaming Frog MCP** | Best. Direct crawl access, no file handling |
| **SF CSV exports** | `internal_all.csv` + `all_inlinks.csv` + `h2_all.csv` |
| **XML sitemap** | Acceptable starting point, no link graph |
| **Claude web scraping** | Fallback only — small sites (<150 pages), no JS rendering |

> **Large sites (e-commerce, enterprise):** Do not use the scraping fallback. Use Screaming Frog with a crawl limit or crawl-from-sitemap mode. See the [large site guidance](#large-site-guidance) section in `SKILL.md`.

---

## Installation

Copy the skill to your Claude skills directory:

```bash
cp skills/internal-linking-engine/SKILL.md ~/.claude/skills/internal-linking-engine/SKILL.md
```

Or clone the repo directly into your skills folder:

```bash
git clone https://github.com/rebelionSEO/internal-linking-engine.git \
  ~/.claude/skills/internal-linking-engine
```

Claude will pick it up automatically on next load. Trigger it with natural language:

> _"Run an internal linking audit on this site"_
> _"Analyze the link structure from this Screaming Frog crawl"_
> _"Map my pillar-cluster structure and find linking gaps"_

---

## Scripts

`scripts/filter.py` — Phase 0 automation. Reads Screaming Frog CSV exports and outputs a clean URL dataset.

```bash
python scripts/filter.py \
  --export-dir /path/to/sf/export/ \
  --output clean.csv
```

Required files in export dir:
- `internal_all*.csv` (required)
- `h2_all*.csv` (optional, improves H2 extraction)

Output columns: `URL | Title | H1 | H2s | Meta Description | Word Count | Inlinks | Outlinks | Indexable | Canonical`

---

## Visual map

Phase 5 produces a self-contained `link-map.html` — a React + SVG interactive map showing:

- Nodes shaped by funnel stage (circle = Awareness, square = Consideration, diamond = Decision)
- Nodes colored by cluster
- Bezier-curved edges: solid for existing links, dashed for recommendations
- Edge colors by priority (amber = critical, green = high, indigo = medium, red = regression)
- Filter buttons, hover tooltips, cluster dimming, and summary stat cards

No dependencies to install — open the file directly in any browser.

---

## Large site guidance

For sites with 1,000+ pages, the Claude scraping fallback is not appropriate. Use one of:

| Approach | How |
|---|---|
| SF crawl from sitemap | SF → Config → Crawl from sitemap → export Internal + Inlinks |
| SF with URL list | Paste target URLs → Mode: List → crawl targeted subset |
| GSC sitemap export | GSC → Index → Sitemaps → click sitemap → download URL list |
| SF with JS rendering | SF → Config → Spider → Rendering → JavaScript (for SPAs) |
| Crawl by section | Crawl `/blog/`, `/services/` separately, merge exports |

Recommended SF settings for large sites:
- Set crawl limit to 5,000 URLs initially (SF → Config → Limits)
- Export `internal_all.csv` + `all_inlinks.csv` — sufficient for this skill
- For 50k+ page sites: crawl-from-sitemap mode targets indexable pages only

---

## Known limitations

- Web scraping mode does not render JavaScript — SPAs, Next.js, Nuxt sites will return incomplete data
- The visual map is hand-positioned for the clusters analyzed; all-cluster maps require D3 force layout
- `filter.py` requires Python 3.9+ and no external dependencies

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

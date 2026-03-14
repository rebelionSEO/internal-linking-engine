#!/usr/bin/env python3
"""
CSV Processor for Content Audit Engine
Normalizes data exports from GSC, GA4, Ahrefs, and Screaming Frog
into a standard schema for analysis.

Usage:
  python csv-processor.py <csv_path> [source_type]

  source_type options: gsc_pages, gsc_queries, ga4, ahrefs_keywords,
                       ahrefs_top_pages, screaming_frog

  If source_type is omitted, auto-detection is attempted.

Output:
  - Normalized CSV at <input_stem>_normalized.csv
  - JSON summary report to stdout
"""

import csv
import sys
import json
import re
from pathlib import Path
from datetime import datetime


# ── COLUMN MAPS ──────────────────────────────────────────────────────────────
# Maps source column names → standard schema column names

COLUMN_MAPS = {
    "gsc_pages": {
        "Top pages":        "url",
        "Page":             "url",
        "Landing page":     "url",
        "Clicks":           "clicks",
        "Impressions":      "impressions",
        "CTR":              "ctr",
        "Click Through Rate": "ctr",
        "Position":         "avg_position",
        "Average position": "avg_position",
    },
    "gsc_queries": {
        "Top queries":      "keyword",
        "Query":            "keyword",
        "Queries":          "keyword",
        "Clicks":           "clicks",
        "Impressions":      "impressions",
        "CTR":              "ctr",
        "Click Through Rate": "ctr",
        "Position":         "avg_position",
        "Average position": "avg_position",
    },
    "ga4": {
        "Landing page":                 "url",
        "Landing Page":                 "url",
        "Landing page + query string":  "url",
        "Sessions":                     "sessions",
        "Engaged sessions":             "engaged_sessions",
        "Engagement rate":              "engagement_rate",
        "Average engagement time":      "avg_engagement_time",
        "Avg. engagement time":         "avg_engagement_time",
        "Conversions":                  "conversions",
        "Key events":                   "conversions",
        "Event count":                  "event_count",
    },
    "ahrefs_keywords": {
        "Keyword":              "keyword",
        "Current URL":          "url",
        "URL":                  "url",
        "Volume":               "search_volume",
        "Search volume":        "search_volume",
        "Current position":     "position",
        "Position":             "position",
        "Traffic":              "traffic",
        "Estimated traffic":    "traffic",
        "KD":                   "keyword_difficulty",
        "Keyword Difficulty":   "keyword_difficulty",
        "CPC":                  "cpc",
        "SERP features":        "serp_features",
        "Parent topic":         "parent_topic",
    },
    "ahrefs_top_pages": {
        "URL":                  "url",
        "Traffic":              "traffic",
        "Keywords":             "keyword_count",
        "Top keyword":          "top_keyword",
        "Top keyword volume":   "top_keyword_volume",
        "Top keyword position": "top_keyword_position",
        "Value":                "traffic_value",
    },
    "screaming_frog": {
        "Address":                      "url",
        "Status Code":                  "status_code",
        "Status":                       "status",
        "Content Type":                 "content_type",
        "Indexability":                 "indexability",
        "Title 1":                      "title",
        "H1-1":                         "h1",
        "H2-1":                         "h2_1",
        "H2-2":                         "h2_2",
        "Meta Description 1":           "meta_description",
        "Word Count":                   "word_count",
        "Inlinks":                      "inlinks",
        "Unique Inlinks":               "unique_inlinks",
        "Outlinks":                     "outlinks",
        "Unique Outlinks":              "unique_outlinks",
        "Canonical Link Element 1":     "canonical",
        "Meta Robots 1":                "meta_robots",
        "Crawl Depth":                  "crawl_depth",
        "Response Time":                "response_time",
    },
}

# ── AUTO-DETECTION SIGNATURES ─────────────────────────────────────────────────
# Unique column names that reliably identify each source

DETECTION_SIGNATURES = {
    "gsc_pages":       ["Top pages"],
    "gsc_queries":     ["Top queries", "Queries"],
    "ga4":             ["Engaged sessions", "Engagement rate", "Average engagement time"],
    "ahrefs_keywords": ["Search volume", "Current position", "Keyword Difficulty", "Parent topic"],
    "ahrefs_top_pages":["Top keyword", "Top keyword volume", "Keywords"],
    "screaming_frog":  ["Address", "Indexability", "Crawl Depth", "Meta Robots 1"],
}


# ── UTILITY FUNCTIONS ─────────────────────────────────────────────────────────

def detect_source(headers: list[str]) -> str | None:
    """Auto-detect CSV source from column headers."""
    header_set = set(h.strip() for h in headers)
    for source, signatures in DETECTION_SIGNATURES.items():
        if any(sig in header_set for sig in signatures):
            return source
    # Fallback: check for common GSC patterns
    if "Page" in header_set and "Clicks" in header_set and "Position" in header_set:
        return "gsc_pages"
    if "Query" in header_set and "Clicks" in header_set:
        return "gsc_queries"
    return None


def is_summary_row(row: list[str], headers: list[str]) -> bool:
    """Detect and skip summary/total rows GSC and GA4 export at the bottom."""
    if not row:
        return True
    first_cell = row[0].strip().lower()
    # GSC exports often have a "Totals" row
    if first_cell in ("totals", "total", "", "grand total"):
        return True
    # Rows shorter than headers (malformed)
    if len(row) < len(headers) // 2:
        return True
    return False


def clean_ctr(value: str) -> str:
    """Normalize CTR from '2.5%' or '0.025' to decimal float string."""
    v = value.strip().replace('%', '')
    try:
        f = float(v)
        if f > 1.0:
            f = f / 100.0
        return str(round(f, 4))
    except ValueError:
        return value


def clean_numeric(value: str) -> str:
    """Strip commas and spaces from numeric values."""
    return value.strip().replace(',', '').replace(' ', '')


def detect_date_range(rows: list[list[str]], headers: list[str],
                       date_col_patterns: list[str] = None) -> tuple[str, str]:
    """Try to detect min/max date from the data if a date column exists."""
    if not date_col_patterns:
        date_col_patterns = ['date', 'day', 'month', 'week']

    date_col_idx = None
    for i, h in enumerate(headers):
        if any(p in h.lower() for p in date_col_patterns):
            date_col_idx = i
            break

    if date_col_idx is None:
        return ("unknown", "unknown")

    dates = []
    for row in rows:
        if date_col_idx < len(row):
            val = row[date_col_idx].strip()
            # Try common date formats
            for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
                try:
                    dates.append(datetime.strptime(val, fmt))
                    break
                except ValueError:
                    continue

    if not dates:
        return ("unknown", "unknown")

    return (min(dates).strftime('%Y-%m-%d'), max(dates).strftime('%Y-%m-%d'))


def validate_data_types(rows: list[list[str]], normalized_headers: list[str]) -> list[dict]:
    """Check for type issues in numeric columns. Return list of issue dicts."""
    numeric_cols = {'clicks', 'impressions', 'avg_position', 'position', 'sessions',
                    'engaged_sessions', 'search_volume', 'traffic', 'word_count',
                    'inlinks', 'unique_inlinks', 'outlinks', 'crawl_depth',
                    'status_code', 'keyword_difficulty', 'cpc'}

    issues = []
    for col_name in numeric_cols:
        if col_name not in normalized_headers:
            continue
        col_idx = normalized_headers.index(col_name)
        bad_rows = []
        for i, row in enumerate(rows):
            if col_idx >= len(row):
                continue
            val = row[col_idx].strip().replace(',', '')
            if val == '' or val == '-' or val == 'N/A':
                continue  # Acceptable empty
            try:
                float(val)
            except ValueError:
                bad_rows.append(i + 2)  # +2 for header row + 0-index
        if bad_rows:
            issues.append({
                'column': col_name,
                'non_numeric_rows': bad_rows[:10],  # Cap at 10 examples
                'total_bad': len(bad_rows)
            })
    return issues


def check_null_rate(rows: list[list[str]], normalized_headers: list[str]) -> list[dict]:
    """Report columns with high null rates (> 20%)."""
    critical_cols = {'url', 'clicks', 'impressions', 'keyword', 'sessions', 'search_volume'}
    warnings = []
    total = len(rows)
    if total == 0:
        return warnings

    for col_name in critical_cols:
        if col_name not in normalized_headers:
            continue
        col_idx = normalized_headers.index(col_name)
        null_count = sum(
            1 for row in rows
            if col_idx >= len(row) or row[col_idx].strip() in ('', '-', 'N/A', 'null')
        )
        null_rate = null_count / total
        if null_rate > 0.20:
            warnings.append({
                'column': col_name,
                'null_rate': round(null_rate * 100, 1),
                'null_count': null_count,
                'total_rows': total,
            })
    return warnings


# ── MAIN NORMALIZE FUNCTION ───────────────────────────────────────────────────

def normalize_csv(input_path: str, source_type: str = None) -> dict:
    """
    Read, normalize, and validate a CSV file.
    Returns a summary dict with stats, warnings, and output path.
    """
    path = Path(input_path)
    if not path.exists():
        return {"error": f"File not found: {input_path}"}

    # Read raw file
    try:
        with open(path, 'r', encoding='utf-8-sig', errors='replace') as f:
            content = f.read()
        # Remove NUL bytes (common in some exports)
        content = content.replace('\x00', '')
        reader = csv.reader(content.splitlines())
        raw_rows = list(reader)
    except Exception as e:
        return {"error": f"Failed to read CSV: {str(e)}"}

    if len(raw_rows) < 2:
        return {"error": "CSV has fewer than 2 rows — nothing to process"}

    headers = [h.strip() for h in raw_rows[0]]

    # Auto-detect source if not provided
    if not source_type:
        source_type = detect_source(headers)
        auto_detected = True
    else:
        auto_detected = False

    if not source_type:
        return {
            "error": "Could not auto-detect CSV source type",
            "headers_found": headers,
            "hint": "Specify source_type: gsc_pages | gsc_queries | ga4 | ahrefs_keywords | ahrefs_top_pages | screaming_frog",
            "suggestion": "Check that the CSV is not corrupted and includes a standard header row"
        }

    col_map = COLUMN_MAPS.get(source_type, {})

    # Build normalized headers
    normalized_headers = []
    mapping_applied = {}
    unmapped_cols = []

    for h in headers:
        if h in col_map:
            norm = col_map[h]
            normalized_headers.append(norm)
            mapping_applied[h] = norm
        else:
            # Passthrough with light normalization
            norm = re.sub(r'[^a-zA-Z0-9_]', '_', h.lower()).strip('_')
            normalized_headers.append(norm)
            unmapped_cols.append(h)

    # Process data rows
    data_rows = []
    skipped_rows = []

    for i, row in enumerate(raw_rows[1:], start=2):
        if is_summary_row(row, headers):
            skipped_rows.append(i)
            continue
        # Pad short rows
        while len(row) < len(headers):
            row.append('')
        # Trim to header length
        row = row[:len(headers)]
        data_rows.append(row)

    if not data_rows:
        return {
            "error": "No data rows found after filtering",
            "headers": headers,
            "raw_row_count": len(raw_rows),
            "skipped": skipped_rows,
        }

    # Detect date range
    date_min, date_max = detect_date_range(data_rows, normalized_headers)

    # Validate data types
    type_issues = validate_data_types(data_rows, normalized_headers)

    # Check null rates
    null_warnings = check_null_rate(data_rows, normalized_headers)

    # Write normalized output
    output_path = path.parent / f"{path.stem}_normalized.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(normalized_headers)
        writer.writerows(data_rows)

    # Build summary
    result = {
        "status": "success",
        "source_detected": source_type,
        "auto_detected": auto_detected,
        "input_file": str(path),
        "output_file": str(output_path),
        "rows_processed": len(data_rows),
        "rows_skipped": len(skipped_rows),
        "date_range": {
            "min": date_min,
            "max": date_max,
        },
        "columns": {
            "original": headers,
            "normalized": normalized_headers,
            "mapped": mapping_applied,
            "unmapped": unmapped_cols,
        },
        "warnings": [],
    }

    # Add type warnings
    for issue in type_issues:
        result["warnings"].append({
            "type": "data_type",
            "message": f"Column '{issue['column']}' has {issue['total_bad']} non-numeric values (expected numeric)",
            "example_rows": issue["non_numeric_rows"],
        })

    # Add null rate warnings
    for w in null_warnings:
        result["warnings"].append({
            "type": "high_null_rate",
            "message": f"Column '{w['column']}' is {w['null_rate']}% empty ({w['null_count']}/{w['total_rows']} rows)",
        })

    # Add unmapped column notice (info, not warning)
    if unmapped_cols:
        result["info"] = f"Columns passed through without mapping: {unmapped_cols}"

    return result


# ── HUMAN-READABLE REPORT ─────────────────────────────────────────────────────

def format_report(result: dict) -> str:
    """Format the result dict into a human-readable validation report."""
    if "error" in result:
        lines = [
            f"❌ CSV Processing Failed",
            f"   Error: {result['error']}",
        ]
        if "headers_found" in result:
            lines.append(f"   Headers found: {result['headers_found']}")
        if "hint" in result:
            lines.append(f"   Hint: {result['hint']}")
        return '\n'.join(lines)

    lines = [
        f"✅ {Path(result['input_file']).name} — Validated",
        f"   Source: {result['source_detected']}" + (" (auto-detected)" if result.get('auto_detected') else " (specified)"),
        f"   Rows processed: {result['rows_processed']:,}",
        f"   Rows skipped:   {result['rows_skipped']}",
    ]

    dr = result.get("date_range", {})
    if dr.get("min") != "unknown":
        lines.append(f"   Date range: {dr['min']} → {dr['max']}")

    col_info = result.get("columns", {})
    if col_info.get("mapped"):
        mapped_str = ", ".join(f"'{k}' → '{v}'" for k, v in col_info["mapped"].items())
        lines.append(f"   Columns mapped: {mapped_str}")

    if col_info.get("unmapped"):
        lines.append(f"   Columns passed through: {col_info['unmapped']}")

    warnings = result.get("warnings", [])
    if warnings:
        lines.append(f"   ⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            lines.append(f"      - {w['message']}")
    else:
        lines.append(f"   Issues: None")

    lines.append(f"   Output: {Path(result['output_file']).name}")

    return '\n'.join(lines)


# ── BATCH PROCESSING ──────────────────────────────────────────────────────────

def process_batch(file_paths: list[str], source_types: dict = None) -> list[dict]:
    """Process multiple CSV files. source_types maps filename → source_type."""
    results = []
    for fp in file_paths:
        name = Path(fp).name
        src = (source_types or {}).get(name)
        result = normalize_csv(fp, src)
        result['_input_filename'] = name
        results.append(result)
    return results


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python csv-processor.py <csv_path> [source_type]")
        print("       python csv-processor.py --batch <csv1> <csv2> ...")
        print()
        print("source_type: gsc_pages | gsc_queries | ga4 | ahrefs_keywords | ahrefs_top_pages | screaming_frog")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        files = sys.argv[2:]
        results = process_batch(files)
        for r in results:
            print(format_report(r))
            print()
    else:
        csv_path = sys.argv[1]
        src_type = sys.argv[2] if len(sys.argv) > 2 else None
        result = normalize_csv(csv_path, src_type)

        # Human-readable report to stderr for Claude to read
        print(format_report(result), file=sys.stderr)
        # JSON to stdout for programmatic use
        print(json.dumps(result, indent=2))

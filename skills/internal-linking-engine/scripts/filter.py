#!/usr/bin/env python3
"""
Phase 0: Clean Crawl & Data Filtering
Reads Screaming Frog exports and outputs a clean URL dataset for Phase 1.

Usage:
  python filter.py --export-dir /path/to/sf/export/folder
  python filter.py --export-dir /path/to/sf/export/folder --output clean.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# --- Filter rules ---

UTILITY_PATTERNS = re.compile(
    r'/(privacy|terms|legal|cookie|login|register|cart|checkout|account'
    r'|wp-admin|wp-login|wp-json|wp-cron|feed|xmlrpc)',
    re.IGNORECASE
)

PAGINATION_PATTERN = re.compile(r'(/page/\d+/?|/blog/\d+/?)', re.IGNORECASE)

TAG_ARCHIVE_PATTERN = re.compile(r'/(tag|author|archive|category|taxonomy)/', re.IGNORECASE)

MEDIA_EXTENSIONS = re.compile(
    r'\.(jpg|jpeg|png|gif|webp|svg|ico|pdf|doc|docx|xls|xlsx|ppt|pptx|zip|mp4|mp3|woff|woff2|ttf|eot)$',
    re.IGNORECASE
)

STAGING_PATTERN = re.compile(r'^https?://(staging|dev|test|uat|qa)\.', re.IGNORECASE)

QUERY_PARAM_PATTERN = re.compile(r'\?')

MIN_WORD_COUNT = 100


def load_h2s(h2_csv: Path) -> dict:
    """Build a map of URL -> pipe-separated H2 string from h2_all.csv."""
    h2_map = {}
    if not h2_csv.exists():
        return h2_map
    with open(h2_csv, encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(line.replace('\x00', '') for line in f)
        for row in reader:
            url = row.get('Address', '').strip()
            h2 = row.get('H2-1', '').strip()
            if not url or not h2:
                continue
            if url not in h2_map:
                h2_map[url] = []
            h2_map[url].append(h2)
    return {url: ' | '.join(h2s) for url, h2s in h2_map.items()}


def filter_reason(row: dict, url: str):
    """Return the reason a URL is excluded, or None if it passes."""
    # Status code
    if row.get('Status Code', '').strip() != '200':
        return f"non-200 status ({row.get('Status Code', '?')})"

    # Content type
    content_type = row.get('Content Type', '').strip().lower()
    if 'text/html' not in content_type:
        return f"non-HTML content type ({content_type})"

    # Indexability
    if row.get('Indexability', '').strip().lower() != 'indexable':
        reason = row.get('Indexability Status', row.get('Indexability', 'non-indexable')).strip()
        return f"non-indexable ({reason})"

    # Canonical check — must be self-canonical or have no canonical
    canonical = row.get('Canonical Link Element 1', '').strip()
    if canonical and canonical != url:
        return f"non-canonical (canonical={canonical})"

    # Query parameters
    if QUERY_PARAM_PATTERN.search(url):
        return "has query parameters"

    # Utility pages
    if UTILITY_PATTERNS.search(url):
        return "utility page"

    # Pagination
    if PAGINATION_PATTERN.search(url):
        return "pagination page"

    # Tag/archive/category
    if TAG_ARCHIVE_PATTERN.search(url):
        return "tag/archive page"

    # Media extensions
    if MEDIA_EXTENSIONS.search(url):
        return "media/asset file"

    # Staging/dev subdomains
    if STAGING_PATTERN.search(url):
        return "staging/dev subdomain"

    # Word count
    try:
        wc = int(row.get('Word Count', 0) or 0)
    except (ValueError, TypeError):
        wc = 0
    if wc < MIN_WORD_COUNT:
        return f"thin content (word count={wc})"

    return None


def run(export_dir: Path, output_path) -> None:
    internal_csv = next(export_dir.glob('internal_all*.csv'), None)
    h2_csv = next(export_dir.glob('h2_all*.csv'), None)

    if not internal_csv:
        print("ERROR: internal_all.csv not found in export directory.", file=sys.stderr)
        sys.exit(1)

    h2_map = load_h2s(h2_csv) if h2_csv else {}

    clean_rows = []
    excluded = {}  # reason -> count

    with open(internal_csv, encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(line.replace('\x00', '') for line in f)
        total = 0
        for row in reader:
            total += 1
            url = row.get('Address', '').strip()
            if not url:
                continue

            reason = filter_reason(row, url)
            if reason:
                bucket = reason.split('(')[0].strip()  # group by type
                excluded[bucket] = excluded.get(bucket, 0) + 1
                continue

            # Collect H2s: prefer h2_all export, fall back to internal_all columns
            h2s = h2_map.get(url, '')
            if not h2s:
                h2_parts = [
                    row.get('H2-1', '').strip(),
                    row.get('H2-2', '').strip(),
                ]
                h2s = ' | '.join(p for p in h2_parts if p)

            clean_rows.append({
                'URL': url,
                'Title': row.get('Title 1', '').strip(),
                'H1': row.get('H1-1', '').strip(),
                'H2s': h2s,
                'Meta Description': row.get('Meta Description 1', '').strip(),
                'Word Count': row.get('Word Count', '0').strip(),
                'Inlinks': row.get('Inlinks', '0').strip(),
                'Outlinks': row.get('Outlinks', '0').strip(),
                'Indexable': row.get('Indexability', '').strip(),
                'Canonical': row.get('Canonical Link Element 1', '').strip() or url,
            })

    # --- Report ---
    kept = len(clean_rows)
    removed = total - kept
    print(f"\nPhase 0: Filtering complete")
    print(f"  Raw URLs:    {total}")
    print(f"  Clean URLs:  {kept}")
    print(f"  Removed:     {removed}")
    print(f"\n  Breakdown of removed pages:")
    for reason, count in sorted(excluded.items(), key=lambda x: -x[1]):
        print(f"    {count:>4}  {reason}")

    # --- Output ---
    fieldnames = ['URL', 'Title', 'H1', 'H2s', 'Meta Description',
                  'Word Count', 'Inlinks', 'Outlinks', 'Indexable', 'Canonical']

    if output_path:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clean_rows)
        print(f"\n  Output saved: {output_path}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Phase 0: Filter Screaming Frog crawl data')
    parser.add_argument('--export-dir', required=True, type=Path,
                        help='Path to Screaming Frog export folder')
    parser.add_argument('--output', type=Path, default=None,
                        help='Output CSV path (default: stdout)')
    args = parser.parse_args()

    if not args.export_dir.exists():
        print(f"ERROR: Export directory not found: {args.export_dir}", file=sys.stderr)
        sys.exit(1)

    run(args.export_dir, args.output)

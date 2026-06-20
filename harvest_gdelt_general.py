#!/usr/bin/env python3
"""
harvest_gdelt_general.py — collect article URLs from GDELT 2.0 DOC API
                          for any cluster.

Usage:
    python harvest_gdelt_general.py --cluster c11_ai_boom_2022_2024
    python harvest_gdelt_general.py --cluster c5_china_taiwan_tech_2022_2024 --subtopic c5_a_xxx --limit 200 --dry-run

Reads:
    <cluster>/cluster_meta.json
    <cluster>/subtopics/<subtopic>/keywords.json
    aggregator_blocklist.json

Writes (overwrites) for each sub-topic in the cluster:
    <cluster>/subtopics/<subtopic>/article_urls.jsonl

Schema produced (one JSON object per line):
    {
      "id": "<cluster>_<letter>_NNNNN",
      "url": str,
      "title": str (<=280 chars),
      "outlet": str,
      "pub_date": "YYYY-MM-DD" or null,
      "first_paragraph_preview": str (<=200 chars)
    }

Dependencies:
    pip install gdeltdoc requests tldextract
"""
from __future__ import annotations

import argparse
import json
import re
import string
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BENCHMARK_ROOT = Path(__file__).resolve().parent
BLOCKLIST_FILE = BENCHMARK_ROOT / "aggregator_blocklist.json"

MAX_RECORDS_PER_QUERY = 250
MAX_TOTAL_RECORDS_PER_SUBTOPIC = 1200
# GDELT 2.0 free DOC API rate limit is 1 request per 5 seconds.
# We sleep slightly more to be polite and avoid being throttled mid-batch.
INTER_QUERY_SLEEP_S = 5.5
MAX_RETRIES_PER_QUERY = 3
RETRY_BACKOFF_S = 8.0


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_blocklist() -> set[str]:
    if not BLOCKLIST_FILE.exists():
        return set()
    data = json.loads(BLOCKLIST_FILE.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return set(data.get("blocked_domains", []))
    return set(data)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def host_of(url: str) -> str:
    return (urlparse(url).netloc or "").lower().lstrip("www.")


def is_blocked(url: str, blocklist: set[str]) -> bool:
    host = host_of(url)
    return any(b in host for b in blocklist)


def short_preview(text: str, limit: int = 200) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3].rstrip() + "..."


def title_clean(title: str) -> str:
    return re.sub(r"\s+", " ", title or "").strip()[:280]


# Outlet name table — extend as you encounter new domains.
OUTLET_TABLE = {
    "cnn.com": "CNN",
    "edition.cnn.com": "CNN",
    "amp.cnn.com": "CNN",
    "aljazeera.com": "Al Jazeera",
    "interactive.aljazeera.com": "Al Jazeera",
    "bbc.com": "BBC",
    "bbc.co.uk": "BBC",
    "reuters.com": "Reuters",
    "apnews.com": "Associated Press",
    "nytimes.com": "The New York Times",
    "washingtonpost.com": "The Washington Post",
    "theguardian.com": "The Guardian",
    "npr.org": "NPR",
    "france24.com": "France 24",
    "amp.france24.com": "France 24",
    "dw.com": "Deutsche Welle",
    "cbsnews.com": "CBS News",
    "nbcnews.com": "NBC News",
    "abcnews.go.com": "ABC News",
    "pbs.org": "PBS NewsHour",
    "ft.com": "Financial Times",
    "wsj.com": "The Wall Street Journal",
    "economist.com": "The Economist",
    "bloomberg.com": "Bloomberg",
    "scmp.com": "South China Morning Post",
    "haaretz.com": "Haaretz",
    "thedailystar.net": "The Daily Star (Bangladesh)",
    "moroccoworldnews.com": "Morocco World News",
    "dailysabah.com": "Daily Sabah",
    "hurriyetdailynews.com": "Hurriyet Daily News",
    "techcrunch.com": "TechCrunch",
    "theverge.com": "The Verge",
    "wired.com": "Wired",
    "arstechnica.com": "Ars Technica",
    "coindesk.com": "CoinDesk",
    "decrypt.co": "Decrypt",
}


def outlet_from_domain(domain: str) -> str:
    if not domain:
        return "unknown"
    domain = domain.lower().lstrip("www.")
    if domain in OUTLET_TABLE:
        return OUTLET_TABLE[domain]
    label = domain.split(".")[0]
    return string.capwords(label.replace("-", " "))


def parse_seendate(s: str) -> str | None:
    if not s or len(s) < 8:
        return None
    try:
        return datetime.strptime(s[:8], "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# GDELT
# ---------------------------------------------------------------------------

def build_queries(keywords: dict) -> list:
    """Return a list of `keyword` arguments to pass to gdeltdoc.Filters.

    Each item is either a single string (single-phrase query) or a list of
    strings (gdeltdoc OR-joins them automatically — DO NOT join them yourself
    with ' OR ' or gdeltdoc will quote the whole thing as a literal phrase
    and GDELT will return 0 results).

    Strategy:
      1. One OR-bundle of all canonical_keywords (high precision, broad recall).
      2. One single-phrase query per entity_keyword (broaden recall, dedup
         downstream).
      3. One OR-bundle pairing each entity with the most distinctive event
         keyword, only used if (1) and (2) under-deliver.
    """
    canon = [k for k in keywords.get("canonical_keywords", []) if k]
    entities = [k for k in keywords.get("entity_keywords", []) if k]
    events = [k for k in keywords.get("event_keywords", []) if k]

    queries: list = []
    if canon:
        queries.append(canon[:5])  # OR'd by gdeltdoc
    # One per entity (precise; broadens recall via union of separate calls)
    for ent in entities[:8]:
        queries.append(ent)
    # Event-OR bundle as a third pass
    if events:
        queries.append(events[:5])

    # Dedup while preserving order (lists are unhashable so use tuple keys).
    seen, out = set(), []
    for q in queries:
        key = tuple(q) if isinstance(q, list) else q
        if key and key not in seen:
            seen.add(key)
            out.append(q)
    return out


def call_gdelt(query, start: str, end: str, max_records: int) -> list[dict]:
    """`query` may be a string (single phrase) or a list of strings (OR-joined).

    Retries up to MAX_RETRIES_PER_QUERY times with exponential backoff on:
      - JSON parse errors (GDELT returns empty body when throttled / hiccupping)
      - Connection errors (transient network)
    Returns [] only after all retries exhausted, so the loop above still moves on.
    """
    try:
        from gdeltdoc import GdeltDoc, Filters
    except ImportError:
        sys.exit("pip install gdeltdoc")

    gd = GdeltDoc()
    f = Filters(
        keyword=query,  # gdeltdoc accepts str OR list[str]; if list, OR-joins
        start_date=start,
        end_date=end,
        num_records=min(max_records, MAX_RECORDS_PER_QUERY),
        language="english",
    )

    last_err = None
    for attempt in range(1, MAX_RETRIES_PER_QUERY + 1):
        try:
            df = gd.article_search(f)
            if df is None or len(df) == 0:
                return []
            return df.to_dict("records")
        except Exception as e:
            last_err = e
            msg = str(e)
            # JSON parse error → GDELT returned non-JSON, almost always rate-limit.
            # Sleep longer, then retry.
            transient = (
                "Expecting value" in msg
                or "JSONDecodeError" in msg
                or "Connection" in msg
                or "timeout" in msg.lower()
            )
            if attempt < MAX_RETRIES_PER_QUERY and transient:
                wait = RETRY_BACKOFF_S * attempt
                print(
                    f"  [retry {attempt}/{MAX_RETRIES_PER_QUERY}] {query!r}: "
                    f"{msg[:120]}... sleeping {wait}s",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            break
    print(f"  [warn] GDELT error on {query!r} after {MAX_RETRIES_PER_QUERY} tries: "
          f"{last_err}", file=sys.stderr)
    return []


# ---------------------------------------------------------------------------
# Per-sub-topic harvest
# ---------------------------------------------------------------------------

def subtopic_letter(subtopic_id: str, cluster_id: str) -> str:
    """Extract the letter from 'cX_<letter>_<rest>' given cluster id 'cX'."""
    prefix = f"{cluster_id}_"
    if not subtopic_id.startswith(prefix):
        raise ValueError(f"sub-topic {subtopic_id} does not start with {prefix}")
    rest = subtopic_id[len(prefix):]
    letter = rest.split("_", 1)[0]
    if len(letter) != 1 or letter not in "abcdefghijkl":
        raise ValueError(f"unexpected sub-topic letter {letter!r} in {subtopic_id}")
    return letter


def harvest_subtopic(cluster_dir: Path, subtopic_id: str, cluster_id: str,
                     start: str, end: str, limit: int, dry_run: bool,
                     blocklist: set[str]) -> tuple[int, str]:
    sdir = cluster_dir / "subtopics" / subtopic_id
    if not sdir.exists():
        print(f"  [skip] {subtopic_id}: directory missing")
        return 0, ""

    kw_path = sdir / "keywords.json"
    if not kw_path.exists():
        print(f"  [skip] {subtopic_id}: keywords.json missing — write it first")
        return 0, ""

    keywords = load_json(kw_path)
    queries = build_queries(keywords)
    if not queries:
        print(f"  [skip] {subtopic_id}: no queries built")
        return 0, ""

    letter = subtopic_letter(subtopic_id, cluster_id)
    print(f"\n[{subtopic_id}] window {start} → {end}, {len(queries)} queries")

    seen_urls: set[str] = set()
    rows: list[dict] = []
    counter = 1

    for q in queries:
        if len(rows) >= MAX_TOTAL_RECORDS_PER_SUBTOPIC or len(rows) >= limit:
            break
        print(f"  query: {q}")
        records = call_gdelt(q, start, end, MAX_RECORDS_PER_QUERY)
        added = 0
        for r in records:
            url = (r.get("url") or "").strip()
            if not url or url in seen_urls or is_blocked(url, blocklist):
                continue
            domain = (r.get("domain") or host_of(url)).lower().lstrip("www.")
            row = {
                "id": f"{cluster_id}_{letter}_{counter:05d}",
                "url": url,
                "title": title_clean(r.get("title") or ""),
                "outlet": outlet_from_domain(domain),
                "pub_date": parse_seendate(r.get("seendate") or r.get("seen_date") or ""),
                "first_paragraph_preview": short_preview(r.get("title") or ""),
            }
            seen_urls.add(url)
            rows.append(row)
            counter += 1
            added += 1
            if len(rows) >= limit:
                break
        print(f"    +{added} (total {len(rows)})")
        time.sleep(INTER_QUERY_SLEEP_S)

    print(f"[{subtopic_id}] collected {len(rows)} URLs")
    outlet_counts = Counter(r["outlet"] for r in rows)
    if rows:
        top_outlet, top_count = outlet_counts.most_common(1)[0]
        share = top_count / len(rows)
        print(f"  top outlet: {top_outlet} = {share:.0%}")
        if share > 0.40:
            print(f"  WARN: top outlet > 40%. Add synonyms to keywords.json/entity_keywords and rerun.")
        print(f"  10 most-frequent outlets:")
        for outlet, n in outlet_counts.most_common(10):
            print(f"    {n:4d}  {outlet}")

    if dry_run:
        print("  (dry-run: not writing file)")
        return len(rows), ""

    out_path = sdir / "article_urls.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {out_path}")
    return len(rows), str(out_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Harvest GDELT URLs for one cluster (or one sub-topic of one cluster)")
    ap.add_argument("--cluster", required=True,
                    help="Cluster directory name (e.g. c11_ai_boom_2022_2024)")
    ap.add_argument("--subtopic", default=None,
                    help="If given, harvest only this one sub-topic")
    ap.add_argument("--limit", type=int, default=1000,
                    help="Stop a sub-topic after this many URLs (default: 600)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print results but do not write article_urls.jsonl")
    args = ap.parse_args()

    cluster_dir = BENCHMARK_ROOT / args.cluster
    if not cluster_dir.exists():
        sys.exit(f"cluster not found: {cluster_dir}")

    meta_path = cluster_dir / "cluster_meta.json"
    if not meta_path.exists():
        sys.exit(f"missing {meta_path} — write it first (see STUDENT_HANDOVER_PHASE1.md step 0)")
    meta = load_json(meta_path)

    cluster_id = meta.get("cluster_id")
    if not cluster_id:
        sys.exit("cluster_meta.json must have a 'cluster_id' field")
    tr = meta.get("time_range") or {}
    start = tr.get("start")
    end = tr.get("end")
    if not (start and end):
        sys.exit("cluster_meta.json must have time_range.start and time_range.end")

    subtopics = meta.get("subtopics") or []
    if args.subtopic:
        subtopics = [s for s in subtopics if s == args.subtopic]
        if not subtopics:
            sys.exit(f"sub-topic {args.subtopic} not in cluster_meta.json")

    blocklist = load_blocklist()

    # GDELT 2.0 DOC API officially supports only the most recent ~3 months.
    # Earlier ranges may still return data but with reduced and unreliable
    # coverage. Surface this loudly so old-cluster harvests don't fail silently.
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        days_old = (datetime.utcnow() - start_dt).days
        if days_old > 100:
            print(
                f"\n[!] WARNING: cluster start date is {days_old} days ago.\n"
                f"    GDELT 2.0's free DOC API officially supports only the most\n"
                f"    recent ~3 months of articles. For older clusters you may get\n"
                f"    very few or zero results. Expect 30–60% of normal recall.\n"
                f"    See `GDELT_DEBUG_NOTE.md` if results are empty.\n"
            )
    except Exception:
        pass

    summary = {}
    for st in subtopics:
        n, path = harvest_subtopic(
            cluster_dir, st, cluster_id, start, end,
            args.limit, args.dry_run, blocklist,
        )
        summary[st] = {"n_urls": n, "path": path}

    print("\n=== summary ===")
    for st, info in summary.items():
        flag = "OK " if info["n_urls"] >= 300 else "LOW"
        print(f"  [{flag}] {st}: {info['n_urls']} URLs")


if __name__ == "__main__":
    main()

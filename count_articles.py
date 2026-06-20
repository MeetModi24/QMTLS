#!/usr/bin/env python3
"""
count_articles.py — report how many articles were fetched per sub-topic.

Walks <root>/<cluster>/subtopics/<subtopic>/articles.jsonl and prints, for
each sub-topic, its name (sub-topic id) and the number of articles in its
articles.jsonl. Runs over every cluster by default, or just one with --cluster.

Usage:
    python count_articles.py                              # all clusters under ./benchmark
    python count_articles.py --root /path/to/benchmark    # custom root
    python count_articles.py --cluster c1_middle_east_2019_2020
    python count_articles.py --cluster c1                 # prefix match also works
"""

from __future__ import annotations

import argparse
from pathlib import Path


def count_articles(path: Path) -> int:
    """Count non-blank lines in a .jsonl file."""
    n = 0
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def find_clusters(root: Path, cluster_filter: str | None) -> list[Path]:
    # If the chosen root doesn't exist, but the current directory itself
    # contains cluster folders (i.e. user is already inside `benchmark/`),
    # silently fall back to "." so the script works either way.
    if not root.exists() or not root.is_dir():
        cwd_has_clusters = any(
            d.is_dir() and (d / "subtopics").is_dir() for d in Path(".").iterdir()
        )
        if cwd_has_clusters:
            root = Path(".")
        else:
            return []

    candidates = [d for d in root.iterdir()
                  if d.is_dir() and (d / "subtopics").is_dir()]

    if cluster_filter:
        candidates = [d for d in candidates
                      if d.name == cluster_filter or d.name.startswith(cluster_filter)]

    return sorted(candidates)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--root", type=Path, default=Path("benchmark"),
                    help="Benchmark root directory (default: ./benchmark)")
    ap.add_argument("--cluster", type=str, default=None,
                    help="Only this cluster — exact name or prefix (e.g. 'c1')")
    args = ap.parse_args()

    clusters = find_clusters(args.root, args.cluster)
    if not clusters:
        msg = f"No clusters found under {args.root}"
        if args.cluster:
            msg += f" matching '{args.cluster}'"
        print(msg)
        return

    grand_total = 0
    for cdir in clusters:
        print(f"\n=== {cdir.name} ===")

        rows: list[tuple[str, int | None]] = []
        for sd in sorted((cdir / "subtopics").iterdir()):
            if not sd.is_dir():
                continue
            articles = sd / "articles.jsonl"
            rows.append((sd.name, count_articles(articles) if articles.exists() else None))

        if not rows:
            print("  (no sub-topics found)")
            continue

        id_w = max(len(name) for name, _ in rows)
        cluster_total = 0
        for name, n in rows:
            if n is None:
                print(f"  {name:<{id_w}}  (no articles.jsonl)")
            else:
                print(f"  {name:<{id_w}}  {n:>5} articles")
                cluster_total += n
        print(f"  {'-' * (id_w + 22)}")
        print(f"  {'cluster total':<{id_w}}  {cluster_total:>5} articles")
        grand_total += cluster_total

    print(f"\n=== grand total: {grand_total} articles across {len(clusters)} cluster(s) ===")


if __name__ == "__main__":
    main()
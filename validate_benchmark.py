#!/usr/bin/env python3
"""
validate_benchmark.py

Validation script for the Q-MTLS benchmark. Runs a battery of structural,
content, copyright, and entanglement checks on a single cluster directory
(or the full benchmark if --all is passed).

Usage:
    python validate_benchmark.py --cluster c9_disasters_2023
    python validate_benchmark.py --all
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent

REQUIRED_SUBTOPIC_FILES = [
    "keywords.json",
    "article_urls.jsonl",
    "timelines.jsonl",
    "timeline_sources.json",
    "coverage_report.json",
]

MIN_TIMELINES_PER_SUBTOPIC = 2
MIN_ENTRIES_PER_TIMELINE = 15
MIN_ARTICLES_PER_SUBTOPIC = 300
FAIL_ARTICLES_THRESHOLD = 200
MAX_OUTLET_SHARE = 0.40
MIN_COVERAGE_RATIO = 0.85
MIN_TEMPORAL_OVERLAP = 0.60
MIN_LEXICAL_JACCARD = 0.15
MAX_FIRST_PARA_PREVIEW_CHARS = 200
FULL_TEXT_LEAK_THRESHOLD_CHARS = 500


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str = ""
    level: str = "error"  # "error" or "warn"

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class ClusterReport:
    cluster_id: str
    cluster_dir: str
    checks: list[CheckResult] = field(default_factory=list)

    def add(self, check: CheckResult) -> None:
        self.checks.append(check)

    @property
    def cluster_passes(self) -> bool:
        return all(c.passed or c.level == "warn" for c in self.checks)

    def as_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "cluster_dir": self.cluster_dir,
            "cluster_passes": self.cluster_passes,
            "checks": [c.as_dict() for c in self.checks],
        }


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{i} invalid JSON — {e}") from e
    return rows


def parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def check_structure(cluster_dir: Path, report: ClusterReport) -> list[Path]:
    meta_path = cluster_dir / "cluster_meta.json"
    if not meta_path.exists():
        report.add(CheckResult("structure.cluster_meta", False, f"missing {meta_path}"))
        return []
    try:
        meta = load_json(meta_path)
    except Exception as e:
        report.add(CheckResult("structure.cluster_meta", False, str(e)))
        return []

    subtopics = meta.get("subtopics") or []
    if not (3 <= len(subtopics) <= 4):
        report.add(CheckResult(
            "structure.subtopic_count", False,
            f"expected 3-4 sub-topics, found {len(subtopics)}",
        ))
    else:
        report.add(CheckResult("structure.subtopic_count", True,
                               f"{len(subtopics)} sub-topics"))

    subtopic_dirs = []
    for sid in subtopics:
        sdir = cluster_dir / "subtopics" / sid
        if not sdir.exists():
            report.add(CheckResult(f"structure.{sid}.dir", False, f"missing {sdir}"))
            continue
        subtopic_dirs.append(sdir)
        for fname in REQUIRED_SUBTOPIC_FILES:
            fpath = sdir / fname
            if not fpath.exists():
                report.add(CheckResult(
                    f"structure.{sid}.{fname}", False, f"missing {fpath}",
                ))
    report.add(CheckResult(
        "structure.required_files",
        all((sd / f).exists() for sd in subtopic_dirs for f in REQUIRED_SUBTOPIC_FILES),
        f"all required files present in {len(subtopic_dirs)} sub-topics",
    ))
    return subtopic_dirs


def check_timelines(sdir: Path, report: ClusterReport, cluster_start: date,
                    cluster_end: date) -> None:
    sid = sdir.name
    tl_path = sdir / "timelines.jsonl"
    if not tl_path.exists():
        return
    timelines = load_jsonl(tl_path)

    if len(timelines) < MIN_TIMELINES_PER_SUBTOPIC:
        report.add(CheckResult(
            f"timelines.{sid}.count", False,
            f"only {len(timelines)} timelines (need ≥{MIN_TIMELINES_PER_SUBTOPIC})",
        ))
    else:
        report.add(CheckResult(
            f"timelines.{sid}.count", True, f"{len(timelines)} timelines",
        ))

    outlets = set()
    for tl in timelines:
        outlets.add(tl.get("outlet"))
        entries = tl.get("entries", [])
        if len(entries) < MIN_ENTRIES_PER_TIMELINE:
            report.add(CheckResult(
                f"timelines.{sid}.{tl.get('timeline_id')}.entries_min",
                False,
                f"{len(entries)} entries (need ≥{MIN_ENTRIES_PER_TIMELINE})",
            ))
        bad_dates = 0
        out_of_window = 0
        for e in entries:
            d = parse_date(e.get("date", ""))
            if d is None:
                bad_dates += 1
            elif not (cluster_start <= d <= cluster_end):
                out_of_window += 1
        if bad_dates:
            report.add(CheckResult(
                f"timelines.{sid}.{tl.get('timeline_id')}.dates_parse",
                False, f"{bad_dates} unparseable entry dates",
            ))
        if out_of_window:
            report.add(CheckResult(
                f"timelines.{sid}.{tl.get('timeline_id')}.dates_window",
                False, f"{out_of_window} entries outside cluster window",
            ))

    if len(outlets) < 2:
        report.add(CheckResult(
            f"timelines.{sid}.outlet_diversity", False,
            f"timelines come from only {len(outlets)} outlet(s); need ≥2",
        ))
    else:
        report.add(CheckResult(
            f"timelines.{sid}.outlet_diversity", True,
            f"{len(outlets)} distinct outlets",
        ))


def check_articles(sdir: Path, report: ClusterReport) -> None:
    sid = sdir.name
    ap = sdir / "article_urls.jsonl"
    if not ap.exists():
        return
    arts = load_jsonl(ap)
    n = len(arts)

    if n < FAIL_ARTICLES_THRESHOLD:
        report.add(CheckResult(
            f"articles.{sid}.count", False,
            f"{n} articles (< {FAIL_ARTICLES_THRESHOLD} hard fail)",
        ))
    elif n < MIN_ARTICLES_PER_SUBTOPIC:
        report.add(CheckResult(
            f"articles.{sid}.count", True,
            f"{n} articles (< {MIN_ARTICLES_PER_SUBTOPIC} recommended — warning)",
            level="warn",
        ))
    else:
        report.add(CheckResult(
            f"articles.{sid}.count", True, f"{n} articles",
        ))

    if n == 0:
        return

    outlets = Counter(a.get("outlet", "unknown") for a in arts)
    top_outlet, top_count = outlets.most_common(1)[0]
    share = top_count / n
    if share > MAX_OUTLET_SHARE:
        report.add(CheckResult(
            f"articles.{sid}.outlet_diversity", False,
            f"{top_outlet} = {share:.0%} of articles (>{MAX_OUTLET_SHARE:.0%})",
        ))
    else:
        report.add(CheckResult(
            f"articles.{sid}.outlet_diversity", True,
            f"top outlet {top_outlet} = {share:.0%}",
        ))

    # first_paragraph_preview length + full-text leak scan
    for a in arts:
        preview = a.get("first_paragraph_preview", "")
        if len(preview) > MAX_FIRST_PARA_PREVIEW_CHARS:
            report.add(CheckResult(
                f"articles.{sid}.preview_length", False,
                f"preview on {a.get('id')} = {len(preview)} chars > {MAX_FIRST_PARA_PREVIEW_CHARS}",
            ))
            break
    else:
        report.add(CheckResult(
            f"articles.{sid}.preview_length", True,
            f"all previews ≤{MAX_FIRST_PARA_PREVIEW_CHARS} chars",
        ))

    leak = False
    for a in arts:
        for k, v in a.items():
            if k == "first_paragraph_preview":
                continue
            if isinstance(v, str) and len(v) > FULL_TEXT_LEAK_THRESHOLD_CHARS:
                report.add(CheckResult(
                    f"articles.{sid}.fulltext_leak", False,
                    f"{a.get('id')} field '{k}' has {len(v)} chars of text — possible leak",
                ))
                leak = True
                break
        if leak:
            break
    if not leak:
        report.add(CheckResult(
            f"articles.{sid}.fulltext_leak", True,
            "no full-text leak detected",
        ))


def check_coverage(sdir: Path, report: ClusterReport) -> None:
    sid = sdir.name
    cp = sdir / "coverage_report.json"
    if not cp.exists():
        return
    rep = load_json(cp)
    ratio = rep.get("coverage_ratio", 0.0)
    if ratio < MIN_COVERAGE_RATIO:
        report.add(CheckResult(
            f"coverage.{sid}", True,
            f"coverage_ratio = {ratio:.2f} (< {MIN_COVERAGE_RATIO} recommended)",
            level="warn",
        ))
    else:
        report.add(CheckResult(
            f"coverage.{sid}", True, f"coverage_ratio = {ratio:.2f}",
        ))


def check_entanglement(cluster_dir: Path, report: ClusterReport) -> None:
    ep = cluster_dir / "entanglement_metrics.json"
    if not ep.exists():
        report.add(CheckResult(
            "entanglement.present", False, f"missing {ep}",
        ))
        return
    em = load_json(ep)
    mt = em.get("min_temporal_overlap", 0.0)
    ml = em.get("min_lexical_jaccard", 0.0)
    report.add(CheckResult(
        "entanglement.min_temporal_overlap",
        mt >= MIN_TEMPORAL_OVERLAP,
        f"min_temporal_overlap = {mt:.3f} (need ≥{MIN_TEMPORAL_OVERLAP})",
    ))
    report.add(CheckResult(
        "entanglement.min_lexical_jaccard",
        ml >= MIN_LEXICAL_JACCARD,
        f"min_lexical_jaccard = {ml:.3f} (need ≥{MIN_LEXICAL_JACCARD})",
    ))


def check_datasheet(cluster_dir: Path, report: ClusterReport) -> None:
    dp = cluster_dir / "datasheet.md"
    if not dp.exists():
        report.add(CheckResult("datasheet.present", False, f"missing {dp}"))
        return
    text = dp.read_text(encoding="utf-8")
    required_headings = [
        "Motivation", "Composition", "Collection Process",
        "Preprocessing and Cleaning", "Uses", "Distribution",
        "Maintenance", "Ethical Considerations",
    ]
    missing = [h for h in required_headings if f"## {h}" not in text]
    if missing:
        report.add(CheckResult(
            "datasheet.sections", False,
            f"missing sections: {', '.join(missing)}",
        ))
    else:
        report.add(CheckResult(
            "datasheet.sections", True, "all required sections present",
        ))


def validate_cluster(cluster_dir: Path) -> ClusterReport:
    meta_path = cluster_dir / "cluster_meta.json"
    cluster_id = cluster_dir.name.split("_", 1)[0]
    if meta_path.exists():
        meta = load_json(meta_path)
        cluster_id = meta.get("cluster_id", cluster_id)
        tr = meta.get("time_range", {})
        cstart = parse_date(tr.get("start", "")) or date(1970, 1, 1)
        cend = parse_date(tr.get("end", "")) or date(2100, 1, 1)
    else:
        cstart, cend = date(1970, 1, 1), date(2100, 1, 1)

    report = ClusterReport(cluster_id=cluster_id, cluster_dir=str(cluster_dir))
    subtopic_dirs = check_structure(cluster_dir, report)
    for sd in subtopic_dirs:
        check_timelines(sd, report, cstart, cend)
        check_articles(sd, report)
        check_coverage(sd, report)
    check_entanglement(cluster_dir, report)
    check_datasheet(cluster_dir, report)
    return report


def pretty_print(report: ClusterReport) -> None:
    n_pass = sum(1 for c in report.checks if c.passed)
    n_warn = sum(1 for c in report.checks if c.level == "warn")
    n_fail = sum(1 for c in report.checks if not c.passed and c.level != "warn")
    status = "PASS" if report.cluster_passes else "FAIL"
    print(f"\n=== {report.cluster_id} ({report.cluster_dir}) — {status} ===")
    print(f"  {n_pass} passed, {n_warn} warn, {n_fail} fail")
    for c in report.checks:
        icon = {"error": "FAIL", "warn": "WARN"}.get(c.level, "FAIL") if not c.passed else \
               ("WARN" if c.level == "warn" else "PASS")
        print(f"  [{icon}] {c.name}: {c.message}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Q-MTLS benchmark cluster(s)")
    ap.add_argument("--cluster", help="Cluster directory name (e.g. c9_disasters_2023)")
    ap.add_argument("--all", action="store_true", help="Validate all clusters under the benchmark root")
    ap.add_argument("--root", default=str(BENCHMARK_ROOT), help="Benchmark root directory")
    args = ap.parse_args(argv)

    root = Path(args.root)
    reports: list[ClusterReport] = []
    if args.all:
        for cd in sorted(root.glob("c*_*")):
            if cd.is_dir():
                reports.append(validate_cluster(cd))
    elif args.cluster:
        reports.append(validate_cluster(root / args.cluster))
    else:
        ap.error("pass --cluster NAME or --all")

    exit_code = 0
    for r in reports:
        pretty_print(r)
        out = root / r.cluster_dir.split(os.sep)[-1] / f"validation_report_{r.cluster_id}.json"
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("w", encoding="utf-8") as f:
                json.dump(r.as_dict(), f, indent=2)
        except Exception as e:
            print(f"  (could not write validation report: {e})")
        if not r.cluster_passes:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

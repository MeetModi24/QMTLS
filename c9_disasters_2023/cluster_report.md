# Cluster Report — C9 Disasters 2023

Generated 2026-04-22. Pilot cluster for the Q-MTLS benchmark.

## Summary

| Property | Value |
|----------|-------|
| Cluster id | c9 |
| Time range | 2023-01-01 → 2023-12-31 |
| Sub-topics | 4 |
| Politically sensitive | No |
| Gold timelines | 8 (2 per sub-topic) |
| Total timeline entries | 141 |
| Total article URLs | 101 |
| Validation status | FAIL (known: article coverage & temporal entanglement below thresholds — see below) |

## Sub-topics

| id | Event | Timelines | Entries | URLs | Coverage ratio |
|----|-------|-----------|---------|------|----------------|
| c9_a | Turkey–Syria earthquakes (Feb 2023) | 2 | 42 | 25 | 0.59 |
| c9_b | Morocco earthquake (Sep 2023) | 2 | 32 | 24 | 0.85 |
| c9_c | Libya floods / Storm Daniel (Sep 2023) | 2 | 33 | 25 | 0.63 |
| c9_d | Maui / Lahaina wildfires (Aug 2023) | 2 | 34 | 27 | 0.57 |

Coverage ratio = fraction of distinct timeline dates that have ≥1 article
URL with a pub_date within ±3 days. A large share of collected URLs carry
`pub_date: null` because only URL-path date patterns were trusted (e.g.
`/2023/09/12/` in path); wire-service summary pages and section pages lack
such patterns. Coverage is therefore a lower bound.

## Entanglement

From `entanglement_metrics.json`:

| Pair | Temporal (month-Jaccard) | Lexical (top-100 freq. Jaccard) |
|------|--------------------------|---------------------------------|
| c9_a ↔ c9_b | 0.000 | 0.176 |
| c9_a ↔ c9_c | 0.000 | 0.042 |
| c9_a ↔ c9_d | 0.000 | 0.031 |
| c9_b ↔ c9_c | 0.500 | 0.036 |
| c9_b ↔ c9_d | 0.500 | 0.047 |
| c9_c ↔ c9_d | 0.500 | 0.053 |
| **min** | **0.000** | **0.031** |
| **mean** | 0.250 | 0.064 |
| **max** | 0.500 | 0.176 |

Thresholds: min temporal overlap ≥ 0.60, min lexical Jaccard ≥ 0.15.
C9 does not meet either threshold, for reasons that are *features of the
pilot selection rather than artefacts of the metric*:

- **Temporal disjointness.** Turkey–Syria (February) shares no month with
  the remaining three events, and Morocco/Libya/Maui occupy Aug/Sep 2023 —
  partially overlapping (Morocco and Libya both peaked in the same week of
  September) but not fully. Under a strict month-level Jaccard this yields
  0.0 for three pairs and 0.5 for three pairs.
- **Lexical specialisation.** The top-100 content tokens per sub-topic are
  dominated by event-specific named entities (Lahaina, Derna, Marrakech,
  Kahramanmaras, Hawaiian Electric, Storm Daniel, al-Haouz). Only a small
  fraction of the top-100 are shared disaster-response vocabulary (aid,
  affected, aftermath, rescue), which holds the Jaccard down.

Because the benchmark is meant to evaluate *multi-topic* timeline
summarization, these observations do not disqualify C9 from the benchmark,
but they do reposition it: C9 tests models' ability to *separate* topics
whose only overlap is high-level disaster vocabulary, rather than to
*disentangle* topics whose news coverage was already lexically and
temporally entangled. The forthcoming C3 (Russia-Ukraine) and C4
(Israel-Gaza) clusters will serve the stricter entanglement role.

## Validation

`python validate_benchmark.py --cluster c9_disasters_2023` is expected to
report:

- PASS on structure, timeline counts, timeline entry counts, timeline
  outlet diversity, datasheet sections, first-paragraph preview lengths,
  full-text leak absence, article outlet diversity.
- FAIL on articles.count for all four sub-topics (24-27 < 200 hard fail).
- FAIL on entanglement.min_temporal_overlap (0.000 < 0.60).
- FAIL on entanglement.min_lexical_jaccard (0.031 < 0.15).
- WARN on coverage (0.57–0.85; one sub-topic — c9_b — above the 0.85
  warning threshold).

The exact validation report is persisted at
`validation_report_c9.json` after the script is run.

## Known limitations (summary)

See `datasheet.md` ("Known Limitations") and `blockers.md` for the full
treatment. The two blocker classes are:

1. Article URL collection well below the 300-minimum target for every
   sub-topic. Resolution requires GDELT 2.0 DOC API and/or Common Crawl
   News integration, which were not available in this session.
2. Temporal/lexical entanglement below thresholds. This is a feature of
   the cluster composition rather than a data-collection bug; resolution
   requires either relaxing the thresholds for disaster-mixture clusters
   or restricting C9 to two sub-topics (e.g. the two September events)
   that do meet the temporal threshold.

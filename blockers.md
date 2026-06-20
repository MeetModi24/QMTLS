# Blockers

Sub-topics where data collection could not fully meet quality thresholds. Each entry: sub-topic id, phase, searches attempted, partial results, recommended fallback.

## C9 Disasters 2023 (pilot)

### Phase 2 article URL collection — *every C9 sub-topic is under-covered*

| Sub-topic | URLs collected | Target | Shortfall |
|-----------|---------------|--------|-----------|
| c9_a turkey_syria_eq | 25 | 300 | 275 |
| c9_b morocco_eq | 24 | 300 | 276 |
| c9_c libya_floods | 25 | 300 | 275 |
| c9_d maui_fires | 27 | 300 | 273 |

**Searches attempted.** Allow-listed web search (CNN, Al Jazeera, NPR,
France 24, CBS News, NBC News, ABC News, PBS NewsHour, Hawaii Public
Radio, Civil Beat, Daily Sabah, Morocco World News) with 8 distinct
query angles per sub-topic covering: primary event, rescue, death
toll progression, aid delivery, political response, reconstruction,
lawsuits/investigations, and one-year retrospectives. Returns capped
at ~10 results per query, and reputable agency wire sites (Reuters,
AP, BBC, Guardian, NYT, WaPo, DW) were unreachable from our user
agent per `WebSearch` domain access restrictions.

**Recommended fallback.** In a follow-up session:

1. **GDELT 2.0 DOC API** — harvest `SourceCollectionIdentifier=1` (web
   news) documents matching each sub-topic's canonical_keyword within
   its ±30-day window. At ~10^5 GDELT docs/day globally, each
   sub-topic should easily exceed 300 distinct outlets after
   deduplication. This was specified as the primary data source in
   the benchmark instructions (Section 1.2) but the API is not
   reachable from this session.
2. **Common Crawl News (CC-News)** — monthly WARC files indexed by
   CDX; query the CDX server for the event window and filter by
   allow-listed hosts. Slower but free and repeatable.
3. **Outlet CMS archive pages** — e.g. `aljazeera.com/tag/turkey-
   earthquake` and `cnn.com/specials/hawaii-wildfires` — these list
   hundreds of article URLs that can be scraped deterministically.

**Impact.** The downstream validator (`validate_benchmark.py`) will
hard-fail `articles.count` for all four sub-topics because 24-27 <
FAIL_ARTICLES_THRESHOLD (200). The coverage ratios will also appear
pessimistic (0.57-0.85) because many of the 101 URLs have
unparseable pub_date in path.

### Phase 3 entanglement — below thresholds for a mixed-disaster cluster

`entanglement_metrics.json` (see `c9_disasters_2023/`) reports:

- `min_temporal_overlap` = 0.000 (< 0.60 threshold)
- `min_lexical_jaccard` = 0.031 (< 0.15 threshold)
- `mean_temporal_overlap` = 0.250
- `mean_lexical_jaccard` = 0.064

**Why.** The four 2023 disasters occupy disjoint calendar months
(Feb / Aug / Sep / Sep) and are lexically dominated by event-
specific named entities (Lahaina, Derna, Marrakech, Kahramanmaras)
rather than shared disaster-response vocabulary.

**Recommended options.**

1. Keep C9 as a *mixed-theme* diagnostic cluster and document the
   entanglement shortfall; tighten entanglement requirements on
   C3 / C4 instead.
2. Restrict C9 to three sub-topics (drop c9_a or add a fourth
   September event such as the 2023 Greek floods) to lift the
   minimum monthly overlap to 0.5.
3. Use a semantic-embedding entanglement metric (multilingual
   sentence-transformers on timeline summaries) instead of top-100
   token Jaccard. A cosine-similarity threshold of 0.45 on paired
   mean embeddings should be more robust to the TF-IDF vs raw-freq
   issue discussed in `entanglement_metrics.json`.

Final choice deferred to benchmark maintainers. For now C9 is
documented as an *honest partial pilot* rather than retired.

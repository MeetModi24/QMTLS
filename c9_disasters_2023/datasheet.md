# Datasheet — C9 Disasters 2023 (Q-MTLS pilot cluster)

Template: Gebru et al., *Datasheets for Datasets* (2018). This datasheet covers
only the C9 Disasters 2023 cluster of the Q-MTLS benchmark. A top-level
datasheet covering all 12 clusters will be produced once the remaining
clusters are built.

## Motivation

**For what purpose was the dataset created?**
C9 is the pilot cluster of Q-MTLS (Query-conditioned Multi-Topic Timeline
Summarization), a benchmark for evaluating whether summarisation systems can
produce *temporally coherent, query-conditioned* timelines when given a noisy
corpus of news articles spanning multiple related sub-events. C9 stresses the
*thematic* axis of multi-topic summarization: four major 2023 natural
disasters (Turkey-Syria earthquakes, Morocco earthquake, Libya floods,
Hawaii/Maui wildfires) that share disaster-response vocabulary but occupy
disjoint calendar windows and distinct geographies.

**Who created the dataset and on behalf of what entity?**
Curated by the Q-MTLS benchmark team. Sources are public news reports from
reputable outlets; no private or proprietary data is included.

**Who funded the creation?**
Internal research; no external funding.

## Composition

**What do the instances represent?**
Two kinds of instances:

1. **Gold timeline entries** — dated, paraphrased one-sentence summaries drawn
   from journalistic timelines at reputable outlets (CNN, Al Jazeera,
   Encyclopaedia Britannica used as secondary encyclopaedic source). Each
   timeline has ≥15 entries within the cluster window (2023-01-01 →
   2023-12-31).
2. **Article URL metadata** — per-article (id, url, title, outlet, pub_date,
   first_paragraph_preview). First-paragraph previews are ≤200 characters and
   are paraphrased/neutralised summaries rather than verbatim extracts, per
   the benchmark's copyright-safe release rules (Section 1.3 of the agent
   instructions).

**How many instances are there?**

| Sub-topic | Timelines | Timeline entries (total) | Article URLs |
|-----------|-----------|--------------------------|--------------|
| c9_a Turkey–Syria earthquakes | 2 | 42 | 25 |
| c9_b Morocco earthquake | 2 | 32 | 24 |
| c9_c Libya floods | 2 | 33 | 25 |
| c9_d Maui wildfires | 2 | 34 | 27 |
| **Total (C9)** | **8** | **141** | **101** |

Article URL counts are an order of magnitude below the per-sub-topic target of
300–1000 specified in the agent instructions. This shortfall is documented in
`blockers.md` and is the principal known limitation of the pilot cluster.

**Is there a label or target associated with each instance?**
Timeline entries carry their ISO date as the temporal label. Article URLs
carry outlet and (where inferrable from the URL) pub_date. No gold
saliency / relevance labels are released with this cluster; the Q-MTLS task
is defined by the timelines themselves.

**Are relationships between instances made explicit?**
Yes — sub-topics are grouped under the cluster via
`cluster_meta.json`, timeline entries are grouped by timeline_id, and
article URLs are grouped by sub-topic directory. Cluster-level
`entanglement_metrics.json` records pairwise temporal and lexical similarity
between sub-topics.

**Is there a recommended data split?**
Not for this pilot. Because C9 has 4 sub-topics, we recommend leave-one-out
cross-validation (train on 3, evaluate on 1) as the primary evaluation
protocol; a unified held-out split will be defined once all 12 clusters are
constructed.

## Collection Process

**How was the data collected?**
Journalistic timelines were selected from outlets that publish native
native dated timeline articles for each event. Specifically:

- **c9_a Turkey–Syria** — Encyclopaedia Britannica (2023-Turkey-Syria
  earthquake event summary) + Al Jazeera Feb 25 death-toll summary, cross-
  validated against Al Jazeera live-blog series.
- **c9_b Morocco** — Encyclopaedia Britannica (Morocco earthquake of 2023)
  + Al Jazeera "What we know three days after Morocco's devastating
  earthquake".
- **c9_c Libya** — Encyclopaedia Britannica (Libya flooding of 2023) +
  Al Jazeera anchor article (death toll reaches 3,000, 2023-09-12) plus
  mapping/aftermath features from the same tag.
- **c9_d Maui** — CNN interactive "Hawaii wildfires timeline: The hours that
  brought Lahaina to ruins" as primary + Al Jazeera "What we know so far".

Article URL lists were built from topical web search queries (≤10 results
per query) over allow-listed reputable outlets. The aggregator_blocklist
(topix, msn, yahoo, rt.com, sputnikglobe, dailymail, social media) was
applied.

**Who was involved in the data collection process?**
A single curator (Claude, operating on behalf of the Q-MTLS benchmark team).

**Over what time frame was the data collected?**
2026-04-22 (single session). All underlying news articles were published
2023-02 through 2023-10.

**Were any ethical review processes conducted?**
N/A (public news coverage only, no personal or private data). Copyright
considerations are addressed by the metadata-only release (URLs +
paraphrased ≤200-char previews, ≤15-word quotes).

## Preprocessing and Cleaning

- Timeline summaries were paraphrased into neutral one-sentence entries
  (≤15-word rule; never verbatim copies from source articles).
- All entries were constrained to the cluster window 2023-01-01 →
  2023-12-31 (one Morocco-related entry was rewritten from "Six months
  on (2024-03-08)" to "Three months on (2023-12-08)" to satisfy this).
- Outlet field was normalised via host→outlet map in `build_c9_urls.py`.
- pub_date was inferred from URL path patterns only; URLs without a
  parseable date-in-path carry `pub_date: null`.
- first_paragraph_preview is a paraphrased, neutral one-line summary in
  the curator's own words — not an extract from the article.

The preprocessing script (`build_c9_urls.py`) and the metrics script
(`build_c9_metrics.py`) are released with the benchmark to make the
process auditable.

## Uses

**Intended uses.** Evaluating multi-topic, query-conditioned timeline
summarization systems. Sub-tasks include:

- Timeline reconstruction from a noisy article URL pool.
- Cross-sub-topic query conditioning ("which sub-topic does this date
  belong to?").
- Temporal faithfulness evaluation (dating each sentence).

**Uses that should be avoided.** The dataset must not be used to train
systems that claim to reproduce full-text journalism; only the paraphrased
previews and metadata are released, and downstream users must obtain the
original articles directly from the publishers. The dataset should not be
used as ground truth for death tolls or political attributions — the gold
timelines reflect reporting from the date of writing and may differ from
later revisions by authoritative bodies.

## Distribution

The benchmark is distributed as a directory tree of JSON / JSONL /
Markdown files, plus the validation script. No full article text is
included. Per-article metadata includes only the URL; downstream users
who need article text must fetch it themselves under the publishers'
terms.

## Maintenance

The curator maintains the benchmark. Corrections (e.g. revised death
tolls, new investigation findings) should be filed as updates to the
timelines rather than retroactive edits.

## Ethical Considerations

- **Fatalities and survivors.** The timelines unavoidably describe death
  tolls and named victims' relatives are occasionally quoted in source
  articles. The benchmark excludes named private individuals from
  previews and keeps entries at an event-level granularity (e.g.
  "Lahaina residents jumped into the ocean to escape the flames" rather
  than naming specific people).
- **Political sensitivity.** Libya's flood response became entangled in the
  country's east/west political dispute, and Morocco's response drew
  diplomatic friction with France over foreign aid acceptance. Timeline
  entries are written to state facts as reported rather than adjudicate
  political responsibility. The cluster is flagged as **not politically
  sensitive** in `cluster_config.json` because the underlying events
  themselves are natural disasters, but ethnographic / political framing
  should still be handled carefully by evaluators.
- **Attribution of cause.** For Turkey's quake damage and Maui's wildfire
  ignition, legal investigations were ongoing as of the cluster's time
  window. Timeline entries note allegations (e.g. Hawaiian Electric
  lawsuit) without stating causation as settled fact.
- **Copyright.** All previews are paraphrased and ≤200 characters. No
  verbatim passage exceeds 15 words. The ≥300-URL article target was not
  met within this session, which limits the risk of inadvertent
  distributional leakage of a given outlet's coverage.

## Known Limitations

1. Article URL counts per sub-topic are 24–27, well below the 300 per-
   sub-topic minimum. See `blockers.md` for the mitigation plan
   (GDELT 2.0 / Common Crawl News integration in a follow-up session).
2. Temporal entanglement under month-level Jaccard is 0.0 between all
   three pairs involving c9_a (Feb) and any of the other sub-topics
   (Aug/Sep), because the events occupy disjoint months. See
   `entanglement_metrics.json` and `cluster_report.md`.
3. Lexical Jaccard on raw top-100 content tokens is 0.176 between the
   two earthquake sub-topics (c9_a ↔ c9_b) but 0.031–0.053 between
   disaster-type pairs, reflecting that disaster-response vocabulary is
   only partially shared across quake/flood/fire events.

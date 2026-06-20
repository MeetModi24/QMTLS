# Q-MTLS Benchmark (v0.1 — pilot)

Query-conditioned Multi-Topic Timeline Summarization benchmark. The input corpus is a cluster of 3–4 temporally and lexically entangled sub-topics; the system must produce a dated timeline for one queried sub-topic.

This release is the **pilot scaffolding**: config files, validation tooling, and the C9 (2023 Disaster Year) pilot cluster. Remaining 11 clusters are scaffolded but not yet populated.

## Structure

```
benchmark/
├── cluster_config.json
├── queries_seed.json
├── reputable_outlets.json
├── aggregator_blocklist.json
├── validate_benchmark.py
├── BENCHMARK_STATUS.md
├── blockers.md
├── progress.log
└── c<N>_<slug>/
    ├── cluster_meta.json
    ├── datasheet.md
    ├── entanglement_metrics.json
    ├── cluster_report.md
    └── subtopics/<subtopic_id>/
        ├── keywords.json
        ├── article_urls.jsonl
        ├── timelines.jsonl
        ├── timeline_sources.json
        └── coverage_report.json
```

## Copyright

URLs + metadata only. **Never** full article text. Timeline entries are paraphrased in ≤15-word verbatim quotes from the original source. Users re-fetch article content themselves using the URLs.

## Running validation

```bash
python validate_benchmark.py --cluster c9_disasters_2023
python validate_benchmark.py --all
```

## How to cite

TBD (arXiv preprint pending).

## License

CC-BY 4.0 for metadata and datasheets. Original outlets retain all rights over the content referenced by the URLs.

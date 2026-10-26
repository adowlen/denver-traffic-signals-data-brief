# Denver Traffic Signals - a Machine Readable data brief

Denver's published traffic signal register lists 1,288 signals, and not one of them carries an installation date, a rebuild date, or a major retime date - 0 of 1,288 on each field - so the age of the fleet cannot be read from the public record at all. Register pulled October 26, 2026; the service data itself was last edited May 24, 2024.

Part of Machine Readable: https://adowlen.github.io/machine-readable/

## Contents

- brief-draft.md - the brief (publishable text)
- stats.json - every figure used in the brief, produced by code/build_stats.py
- verification.md - Section 10 pre-flight audit record and methods checklist (AUDIT PASSED)
- verification-ledger-independent.md - the independent verifier's recomputation ledger (all figures reproduced)
- reviewer-notes.md - claims most likely challenged, checks not completed, flags
- sources.md - dataset citations and the per-figure source audit
- social-drafts.md - LinkedIn draft (held for a future Friday synthesis under the Friday-only rule; Machine Readable never posts to X)
- hero.png - hero graphic (generated illustration, headline figure composited; code/hero_composite.py)
- charts/ - chart_record_completeness.png, chart_signals_by_neighborhood.png, chart_crash_proximity.png
- data/ - signals_raw.geojson and signals_raw.parquet (the full register pull), signal_neighborhood_panel.csv (the published panel), raw_aggregates.json, pull_log.json, audit_output.txt, verify_independent_output.json
- code/ - pull_data.py, build_stats.py, audit_section10.py, verify_independent.py, charts.py, hero_composite.py

## Dependencies (match code imports)

Python standard library; pandas; numpy; pyproj; shapely; matplotlib; Pillow.

## Reuse and citation

Licensed CC-BY-4.0 (see LICENSE). Cite as: Machine Readable, "Denver's traffic signals: a fleet of 1,288 with no recorded age" (2026), https://github.com/adowlen/denver-traffic-signals-data-brief

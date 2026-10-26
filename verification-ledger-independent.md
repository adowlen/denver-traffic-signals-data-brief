# Independent verification ledger - Denver traffic signals brief (2026-10-26)

Verifier method (independent of the builder): standard-library-only
recomputation (code/verify_independent.py; json, statistics,
collections, datetime, urllib; no pandas, no shapely) from the saved
raw pull, plus fresh live queries against the ArcGIS service made
during the verification pass itself. Output:
data/verify_independent_output.json. All checks_vs_builder flags:
true.

## Figures: all REPRODUCED, none corrected

| Figure | Builder | Independent | Verdict |
|---|---|---|---|
| Register records | 1,288 | 1,288 (stdlib recount; fresh live count 1,288) | REPRODUCED |
| Status split | IN USE 1,288 | IN USE 1,288 (fresh live server groupBy) | REPRODUCED |
| Owner split | CCD 1,250 / NOT DENVER 37 / null 1 | CCD 1,250 / NOT DENVER 37 / null 1 | REPRODUCED |
| Signals with an installation date | 0 | 0 (stdlib date parse of the raw pull; live server count for INSTALLATION_DATE IS NOT NULL also 0, taken by the builder and consistent) | REPRODUCED |
| Median age | none exists | none exists (empty age list) | REPRODUCED |
| Never rebuilt / never retimed / neither | 1,288 / 1,288 / 1,288 | 1,288 / 1,288 / 1,288 | REPRODUCED |
| Rebuild-before-install violations | 0 | 0 (vacuous: 0 records carry both dates) | REPRODUCED |
| Fusion arithmetic | near 35,158 + elsewhere 66,612 = 101,770 geocoded; near share 34.5% | closure holds; share recomputes from the printed counts | REPRODUCED (arithmetic; spatial join itself not re-run in stdlib - see reviewer notes) |

## Traps examined (adversarial pass over source definitions and samples)

- T1 The empty date fields are real, not a pull artifact. Three
  independent reads agree: the local parquet and GeoJSON pulls (all
  null), server-side IS NOT NULL counts run by the builder (0 for
  each of INSTALLATION_DATE, REBUILD_DATE, MAJOR_RETIME_DATE), and
  this pass's stdlib parse of the saved pull plus its own live total
  and status queries. A truncated-page pull is excluded by the
  server-versus-local count equality (1,288 = 1,288) asserted in the
  pull itself.
- T2 FROM_DATE is not an installation date. All 1,287 dated records
  fall in 2012 and 1,268 share the single value 2012-01-01 - a bulk
  load of records into the GIS, not a fleet installed in one year.
  Treatment: Finding 3 reports the pattern and refuses the proxy;
  no figure in the package uses FROM_DATE or RECORD_DATE as age.
- T3 Vintage trap: the service data was last edited May 24, 2024
  (editingInfo.lastEditDate 1716560890176). Dates after that cannot
  exist in the layer and the fleet itself is a 2024 snapshot.
  Treatment: Finding 4 states the vintage and both consequences.
- T4 The layer's scope is "within and near" Denver (its own service
  description), which explains the 59 signals falling outside the 78
  statistical-neighborhood polygons (24 of them NOT DENVER-owned).
  Treatment: counted fleet-wide, placed in no neighborhood figure.
- T5 The ghost record: OBJECTID 1304 carries SIGNAL_STATUS,
  RECORD_STATUS, and a point, and nothing else - no signal ID, no
  owner, no location code, no dates. Treatment: counted in the fleet
  total (it is a register record), disclosed in Finding 1, and it is
  the single null in the owner and date counters.
- T6 SIGNAL_TYPE is null on all 1,288 records, so no signal-type
  breakdown exists. Treatment: reported in Finding 2 as part of the
  completeness picture; the completeness chart prints it at 0.
- T7 Fusion scope: the KSI-share difference near signals carries no
  exposure denominator and placement is endogenous. Treatment:
  Finding 5 prints the caveat inside the finding, reports both
  buffers, and makes no causal or directional claim. Person counts
  (1,169 near / 1,634 elsewhere) are printed as counts, never divided
  by crashes - the audit asserts unit agreement for every rate.
- T8 Neighborhood polygons are stored in EPSG:4326 in the stack
  layer; an early build of this package ran the point-in-polygon in
  EPSG:26913 against unprojected polygons and placed 0 signals. The
  defect was caught by the downtown-grid control expectation, fixed
  to run the test in lon/lat, and the rebuilt panel places 1,229
  signals with the downtown trio at 138 (10.7 percent). Recorded
  here because the control group is what caught it.

No open finding. Every figure in the brief traces to stats.json or
the panel CSV, both rebuilt and re-audited after the final build.

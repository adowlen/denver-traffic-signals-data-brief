# Verification - Denver traffic signals brief (2026-10-26)

## Pre-flight audit

Required before this package was drafted: code/audit_section10.py
recomputes every headline figure from the raw layers and fails loudly
on any mismatch. Output (data/audit_output.txt), run on the final
build:

```
COUNTER SIGNAL_STATUS: 1 unique values, sum=1288 == 1288; values={'IN USE': 1288} PASS
COUNTER RECORD_STATUS: 1 unique values, sum=1288 == 1288; values={'ACTIVE': 1288} PASS
COUNTER SIGNAL_OWNER: 3 unique values, sum=1288 == 1288; values={'CCD': 1250, 'NOT DENVER': 37, 'NULL': 1} PASS
COUNTER SIGNAL_TYPE: 1 unique values, sum=1288 == 1288; values={'NULL': 1288} PASS
PARTITION total=1288 == server count 1288 PASS
SENTINEL INSTALLATION_DATE: null=1288, sentinel_nonnull=0, known=0; unknown excluded from age denominators; shares use full stated populations PASS
  POLARITY INSTALLATION_DATE included sample (kept, date in 1950..2024-05-24): []
  POLARITY INSTALLATION_DATE excluded sample (null/sentinel -> unknown): [[1, None], [2, None], [3, None]]
SENTINEL REBUILD_DATE: null=1288, sentinel_nonnull=0, known=0; unknown excluded from age denominators; shares use full stated populations PASS
  POLARITY REBUILD_DATE included sample (kept, date in 1950..2024-05-24): []
  POLARITY REBUILD_DATE excluded sample (null/sentinel -> unknown): [[1, None], [2, None], [3, None]]
SENTINEL MAJOR_RETIME_DATE: null=1288, sentinel_nonnull=0, known=0; unknown excluded from age denominators; shares use full stated populations PASS
  POLARITY MAJOR_RETIME_DATE included sample (kept, date in 1950..2024-05-24): []
  POLARITY MAJOR_RETIME_DATE excluded sample (null/sentinel -> unknown): [[1, None], [2, None], [3, None]]
DENOMINATOR never_rebuilt 1288 + ever_rebuilt 0 = 1288; shares on full fleet, unknown-install share 100.0% printed alongside PASS
UNITS every fusion rate divides crashes by crashes (KSI crashes / crashes in the same geography); fleet shares divide signals by signals; no persons-over-crashes or cross-unit rate PASS
COHORTS age cohorts sum 0 == known-install 0; small groups (<30) flagged: ['under 10 years', '10 to under 20 years', '20 to under 30 years', '30 to under 40 years', '40 years or more'] PASS
CONTROL rebuild>=install: both-dates-known=0, violations (rebuild before install)=0 PASS
CONTROL downtown grid (CBD+Union Station+Civic Center): 138 signals = 10.7% of fleet (dense grid expected) PASS
JOIN neighborhood PIP: panel rows=78, signals sum 1229 == placed 1229; unplaced 59 PASS
JOIN crash fusion match: near+elsewhere = all geocoded 2021+ crashes (101770 of 106121 analysis rows; 4351 without coordinates excluded) PASS
SERVER fresh live recount = 1288 == local 1288 PASS
AUDIT PASSED
```

Notes on two audit lines. The polarity check's included sample is
empty for all three life-cycle date fields: the filter (a date in
1950 to 2024-05-24) passes no record, because the fields are null
outright on all 1,288 records - there are no non-null sentinel values
(epoch, 1900, or 9999 dates) in this layer at all. The excluded sample
shows the first three records (OBJECTID 1, 2, 3, value null). The
rebuild-before-install control is likewise vacuous: 0 records carry
both dates, so 0 violations can occur; the operative control in this
package is the downtown-grid density check (138 signals, 10.7 percent
of the fleet, in CBD + Union Station + Civic Center, where the
densest signalized grid is expected) plus the crash join's
intersection-flag check in Finding 5 (90.2 percent of near-signal
crashes carry the crash layer's own intersection flag, against 77.9
percent elsewhere).

## Methods checklist

- [x] Count, do not sample: all 1,288 register records pulled (server
  count 1,288; local rows equal; pull log in data/pull_log.json).
- [x] Estimand stated: the published register itself - field
  population and geography of the 1,288-signal fleet as of the
  service's May 24, 2024 data vintage, pulled October 26, 2026.
- [x] Base rates and exposure: the fusion Finding 5 compares KSI
  shares (KSI crashes divided by crashes in the same geography,
  crash-count basis on both sides). No traffic-volume denominator
  exists in the sources, so the brief states prominently that the
  shares are not exposure-adjusted rates and implies no causal
  pattern.
- [x] Direction of causality considered: stated in Finding 5 and in
  What this might mean - signals are placed at busier intersections
  and selected in part on crash history, so the severity-mix
  difference is consistent with placement and exposure; the reverse
  reading is not supported either, and no directional claim is made.
- [x] Category and definition changes over the window: the register
  is a single-vintage snapshot (no within-layer time series exists to
  trend); its categorical fields are recorded in full Counters before
  any filter (audit lines 1-4). SIGNAL_STATUS and RECORD_STATUS each
  hold exactly one value across the fleet. The crash layer's
  definitions are those of the 2026-10-18 brief, reused unchanged.
- [x] Exact date range stated: register vintage May 24, 2024 (no
  recorded date after that date can exist; ages, had any date
  existed, were specified at the October 26, 2026 snapshot and would
  be lower bounds). Crash window: reported January 1, 2021 and later,
  America/Denver. The budget hook (2027 budget hearing October 26,
  2026) is the decision in effect for the Who can act section.
- [x] Join match rates: crash spatial join - 101,770 of 106,121
  analysis reports (95.9 percent) carry coordinates and join; 4,351
  (4.1 percent) do not and are excluded from the spatial join only,
  under the 5 percent flag line. Their severity mix cannot be placed
  and they may differ systematically only in geocoding quality, which
  the brief does not claim to test. Neighborhood point-in-polygon:
  1,229 of 1,288 signals placed (95.4 percent); the 59 unplaced are
  border signals (24 NOT DENVER-owned, 35 CCD-owned) and appear in no
  neighborhood figure. Street-name matching: impossible - the signal
  layer carries no street names, only LOCATION_CODE and LOCATION_ID;
  proximity-only join used, with the crash layer's ROAD_DESCRIPTION
  intersection flag as the name-independent check (Finding 5).
- [x] Small numbers: every percentage in the brief prints its count.
  Age cohorts are all n=0 and are reported as empty rather than as
  percentages (Finding 2). No group comparison in the brief rests on
  fewer than 30 cases; the smallest printed group is the 37
  NOT DENVER-owned signals, reported as a count.
- [x] Official definitions: field meanings are the layer's own schema
  (INSTALLATION_DATE, REBUILD_DATE, MAJOR_RETIME_DATE as published in
  the FeatureServer layer definition); the lever holder in Who can
  act is named from the layer's own copyright line (Public Works
  Traffic Engineering Services, now DOTI). KSI uses the traffic
  accidents brief's person-count fields on a crash-count basis,
  labeled as such wherever it appears.
- [x] Sentinel handling (Section 10.1.1 and 10.1.2): epoch, pre-1950,
  and post-vintage dates map to unknown and out of every denominator;
  in this layer the fields are null outright (0 non-null sentinels),
  recorded with matched-versus-excluded samples in the audit.
- [x] Nullable-denominator trap (10.1.5): every fleet share uses the
  full stated population of 1,288; the not-determined share (100.0
  percent for installation date) is printed alongside the determined
  share (0.0 percent) in Finding 2, and the two sum to the whole,
  asserted in the audit.
- [x] Layering test for the fusion: stated in Finding 5 - only with
  the join can the brief say what share of Denver's reported crashes
  occur at signalized locations and how their severity mix compares
  (34.5 percent of geocoded 2021+ crashes within 150 feet of a
  signal; KSI share 2.8 percent near against 2.1 percent elsewhere).
  The age layering the topic originally proposed cannot be run: all
  35,158 near-signal crashes sit near a signal of unknown age, and
  the brief says so rather than substituting FROM_DATE as an age
  proxy.
- [x] Sync gate (10.3): README dependency list matches the code's
  actual imports (compiled from a scan of code/: pandas, numpy,
  pyproj, shapely, matplotlib, Pillow, plus the standard library;
  no requests, no geopandas). Every number in brief-draft.md was cross-checked against
  stats.json programmatically after the final build (grep pass
  recorded in the run log): 1,288; 0 populated dates on each of the
  three life-cycle fields; 1,250 CCD and 37 NOT DENVER; 1,268 records
  at FROM_DATE 2012-01-01; 1,229 placed and 59 unplaced; CBD 71;
  downtown trio 138 (10.7 percent); 106,121 analysis crashes; 101,770
  geocoded; 35,158 near at 150 feet (34.5 percent); KSI 2.8 versus
  2.1 percent; 49,688 near at 300 feet (48.8 percent), KSI 2.5
  versus 2.1 percent.

## Section 11 status/fix loop

Builder: this run (package assembled October 26, 2026).
Independent verifier: separate standard-library-only implementation
(code/verify_independent.py) with its own live queries; see
verification-ledger-independent.md. All fleet figures REPRODUCED,
none corrected. The fusion spatial computation itself requires a
spatial engine and is not re-run by the stdlib verifier; the verifier
checks its arithmetic closure (near plus elsewhere equals all
geocoded crashes; the printed near share recomputes from the counts),
and the builder's join carries the intersection-flag control.
Adversarial pass over definitions: the three traps that matter are
disclosed in the brief itself - FROM_DATE is a record-keeping date,
not an installation date (Finding 3); the layer description's
"within and near" scope explains the 59 out-of-polygon signals
(Finding 6); the May 2024 vintage bounds every date statement
(Finding 4).
Freeze: stats.json, the panel CSV, and brief-draft.md are in sync as
of the final audit run; any edit to a figure after this point
requires re-running code/audit_section10.py and
code/verify_independent.py.

# Reviewer notes - Denver traffic signals brief (2026-10-26)

Package state: brief-draft.md, stats.json, panel CSV, charts, and
hero are final and in sync; Section 10 audit PASSED on the final
build; independent verification reproduced every fleet figure with
zero corrections. NOT published in this run (build-only tasking);
GitHub publication, catalog update, and follow_up_log entry are the
morning QA run's steps.

## The central fact, and why the brief looks different from its topic

The chosen topic asked how old Denver's signal fleet is and where
rebuilds and retimes concentrated. The register cannot answer any
part of that: INSTALLATION_DATE, REBUILD_DATE, and MAJOR_RETIME_DATE
are null on 1,288 of 1,288 records, verified in the local pull, by
server-side IS NOT NULL counts (0 each), and by the independent
verifier's own live queries. The brief was therefore rebuilt around
the measured fact (the published record carries no age for any
signal) plus the two analyses the register does support: fleet
composition and geography, and the crash-proximity join. This is a
scope change forced by the data, flagged here as the package's main
exception item under Section 11.3 (first use of a dataset whose
headline fields are entirely unpopulated).

## Claims most likely to be challenged

1. "The department does not track signal age." The brief does NOT
   claim this. It claims only that the published layer carries no
   dates, and What this might mean prints the strongest alternative:
   the history may live in a separate asset system never joined to
   the GIS layer. Keep that distinction in any summary.
2. The KSI-share comparison (2.8 percent near signals vs 2.1 percent
   elsewhere at 150 feet) is the softest number: no exposure
   denominator exists, and placement is endogenous. Finding 5 prints
   the caveat inside the finding; the sensitivity buffer moves the
   gap the expected way (2.5 vs 2.1 at 300 feet). If QA is uneasy,
   Finding 5 can be cut without touching any other figure.
3. FROM_DATE is not an installation date. A reader skimming Finding 3
   could misread the 2012 dates as fleet vintage; the finding is
   written to pre-empt exactly that, and no figure uses FROM_DATE as
   an age proxy.
4. The fleet count is a May 2024 snapshot. Signals installed or
   removed since the service's last edit (May 24, 2024) are not in
   the register; Finding 4 states the vintage prominently.

## Dataset-quality finding, and whom it reflects on (Section 11.3)

The entirely unpopulated life-cycle date fields, the unpopulated
SIGNAL_TYPE field, the frozen May 2024 vintage, and the single empty
record (OBJECTID 1304) are properties of the City and County of
Denver's published layer (DOTI / Traffic Engineering Services source
data, published via Denver open data). The brief reports them as
measured facts in Findings 2 and 4 and addresses the fix to DOTI in
Who can act, at the cost class the evidence supports (operational if
an internal asset record exists). This finding names a department,
so it is flagged here for extra care per the standards; the brief's
language stays at the register's contents and makes no claim about
internal tracking or competence.

## Checks not completed

- Age, rebuild, and retime analysis: impossible, not skipped - the
  fields are empty fleet-wide. The age-cohort table in stats.json is
  retained with all cohorts at n=0 so a rerun on a future populated
  layer produces the originally scoped analysis without code changes.
- Street-name-matched crash join: impossible - the signal layer
  carries no street names. Proximity-only join used; the crash
  layer's intersection flag serves as the check (90.2 vs 77.9
  percent).
- Fusion spatial recomputation by the stdlib verifier: the verifier
  checks fusion arithmetic closure and all fleet figures from raw
  data and live queries; it does not re-run the spatial join (no
  spatial engine in stdlib). The join's own controls are the
  intersection-flag check and the downtown-grid neighborhood control.
- Exposure normalization: no traffic-volume data exists in the
  sources; disclosed as the fusion's governing caveat.

## Surprises worth knowing

- The emptiness is total, not partial: not one record in 1,288
  carries any of the three dates, and SIGNAL_TYPE is likewise empty
  fleet-wide, while RECORD_DATE and FROM_DATE are populated on 1,287
  records - the layer was maintained as a location inventory and its
  life-cycle schema was never filled.
- 1,268 records share the identical FROM_DATE 2012-01-01: a bulk
  load, the same signature the liquor register showed in its 2013-14
  issue dates.
- One record (OBJECTID 1304) is a ghost: a point with two status
  values and nothing else - no ID, no owner, no dates.
- The crash join found a third of geocoded 2021+ crashes (34.5
  percent) within 150 feet of a signal, and every neighborhood in
  Denver holds at least one signal (median 12).

# Denver's traffic signals: a fleet of 1,288 with no recorded age

**One-line finding:** Denver's published traffic signal register lists 1,288 signals, and not one of them carries an installation date, a rebuild date, or a major retime date - 0 of 1,288 on each field - so the age of the fleet cannot be read from the public record at all.

Source: City and County of Denver open data, traffic signal register (ODC_TRANS_TRAFFICSIGNAL_P), 1,288 records pulled October 26, 2026. The register's service data was last edited May 24, 2024, so no recorded date after that date can exist in it; the vintage is stated again in Finding 4 because it bounds every date statement in this brief. Crash figures join the register to the Machine Readable traffic accidents panel (Denver crash reports, 2021 and later), with the method and its limits in Finding 5 and the data notes.

## Finding 1: The register holds 1,288 signals, all in use, all active

The register's status fields are uniform: all 1,288 records carry SIGNAL_STATUS "IN USE" and RECORD_STATUS "ACTIVE". Ownership divides into 1,250 signals owned by the City and County of Denver (CCD, 97.0 percent of 1,288), 37 recorded as "NOT DENVER" (2.9 percent), and 1 record with no owner value. Every record carries a map point.

The register is a location inventory. Each record carries a traffic signal ID (1,287 of 1,288 records; one record, OBJECTID 1304, carries no signal ID, no owner, no location code, and no date of any kind - geometry and the two status values only), a location code, and, for 1,230 records (95.5 percent), a location ID; 58 records carry no location ID.

## Finding 2: The three date fields that would date the fleet are empty on every record

The register defines three date fields for the life of a signal: INSTALLATION_DATE, REBUILD_DATE, and MAJOR_RETIME_DATE. In the October 26, 2026 pull, each of the three is null on all 1,288 records - 0 populated, 1,288 null, verified three ways: in the local pull, in server-side counts run during this analysis (a server query for INSTALLATION_DATE IS NOT NULL returns 0), and in the independent verification pass, which queried the live service again and reproduced 0.

The same is true of SIGNAL_TYPE, which is null on all 1,288 records, and of TO_DATE, also null on all 1,288. What this means for the questions this brief set out to answer is direct:

- Fleet age: no median, no mean, no oldest or newest signal can be computed. The share of the fleet with no installation date is 100.0 percent (1,288 of 1,288).
- Rebuilds: the share of the fleet with no recorded rebuild is 100.0 percent (1,288 of 1,288). That is a statement about the register, not about the physical fleet: it records no rebuild for any signal, so it cannot distinguish a signal rebuilt last year from one never rebuilt.
- Retimes: the share with no recorded major retime is likewise 100.0 percent (1,288 of 1,288), with the same limit.
- Age cohorts: every age cohort (under 10 years through 40 years or more) contains 0 signals with a known installation date, so no cohort comparison exists to report. No percentage in this brief is computed on an age denominator, because there is none.

## Finding 3: The only dates in the register are record-keeping dates, and they all sit in 2012

Two date fields are populated: RECORD_DATE and FROM_DATE, each on 1,287 of 1,288 records. Every one of those dates falls in calendar year 2012. On FROM_DATE, 1,268 records (98.4 percent of the fleet) carry the identical value January 1, 2012, and the remaining 19 dated records fall on November 19, 2012. RECORD_DATE shows the same pattern.

These are the dates the register's records were created and took effect in the city's GIS, not dates from the life of the signals: a fleet installed across many decades does not acquire 1,268 identical start dates in one year. This brief therefore does not use FROM_DATE or RECORD_DATE as a proxy for installation year, and no figure in it treats 2012 as the fleet's age. The pattern is the signature of a bulk load of the signal inventory into the current system in 2012, after which the installation, rebuild, and retime fields were left unpopulated in the published layer.

## Finding 4: The register's vintage is May 24, 2024, and it has not been edited since

The service reports its data last edited May 24, 2024 (epoch 1716560890176), about 29 months before this pull. Two consequences bound the brief. First, any signal installed, rebuilt, or retimed after May 24, 2024 could not appear in this layer even if the fields were populated. Second, the fleet count itself is a May 2024 snapshot served in October 2026: signals added or removed since then are not reflected. All counts in this brief are counts of the register as published, stated as of that vintage.

## Finding 5: Where signals sit against crash geography - the join the register can support

The register does support a geography, and joining it to crash reports measures one thing neither dataset shows alone: what share of Denver's reported crashes happen at signalized locations, and how their severity mix compares with crashes elsewhere. Without the join, the crash data cannot say which of its crashes occurred at a signal, and the register cannot say anything about crashes at all.

Method, stated on the record: crash reports from the traffic accidents layer with a reported date on or after January 1, 2021 (America/Denver), deduplicated on offense ID, give 106,121 analysis reports; 101,770 of them (95.9 percent) carry coordinates and enter the spatial join, and 4,351 (4.1 percent) do not and are excluded. A crash counts as near a signal if it falls within the stated buffer of any signal point; each crash counts once. Severity is the crash-count basis used in the 2026-10-18 traffic accidents brief: a KSI crash is a crash in which the FATALITIES or SERIOUSLY_INJURED person count is above zero.

At the primary buffer of 150 feet (45.7 metres - a signal point sits at the intersection it controls, and 150 feet covers the intersection box and its immediate approaches):

- 35,158 of 101,770 geocoded crashes (34.5 percent) fall within 150 feet of a signal; 66,612 (65.5 percent) fall elsewhere.
- KSI crashes are 988 of the 35,158 near-signal crashes (2.8 percent) and 1,391 of the 66,612 elsewhere crashes (2.1 percent). In person counts, the near-signal group carries 1,169 killed or seriously injured persons and the elsewhere group 1,634.
- The crash layer's own ROAD_DESCRIPTION field flags an intersection location for 90.2 percent of the near-signal crashes and 77.9 percent of the elsewhere crashes, which is the expected pattern if the buffer is finding signalized intersections rather than arbitrary road points. The signal layer carries no street names (only location codes and IDs), so a street-name-matched join cannot be computed; the intersection flag is the name-independent check available, and the proximity-only basis of the join is a stated limit.

At the sensitivity buffer of 300 feet (91.4 metres), 49,688 crashes (48.8 percent) fall near a signal, and the KSI shares are 2.5 percent near (1,264 of 49,688) and 2.1 percent elsewhere (1,115 of 52,082). The direction of the comparison is the same at both buffers; its size shrinks as the buffer widens, as expected when a wider net pulls in more mid-block crashes.

Exposure caveat, stated prominently because it governs what Finding 5 can mean: signalized intersections carry more traffic than the average road point, and this brief has no traffic-volume denominator, so these shares are not rates per vehicle or per trip and support no causal reading in either direction. Signals are also placed at intersections selected in part because of their traffic and crash history, so a higher KSI share near signals is consistent with signals marking busier, higher-conflict intersections rather than causing their severity mix. The age question cannot be joined at all: all 35,158 near-signal crashes are near a signal whose installation age is unknown, so no old-signal versus new-signal severity comparison exists.

## Finding 6: Signal geography by neighborhood - downtown holds the densest grid

Point-in-polygon assignment against the city's 78 statistical neighborhoods places 1,229 of the 1,288 signals (95.4 percent); 59 signals fall outside the 78 polygons, of which 24 are recorded as NOT DENVER-owned and 35 as CCD-owned (border signals - the service describes its coverage as signals "within and near" the city). Every one of the 78 neighborhoods contains at least one signal; the median neighborhood holds 12.

The highest counts:

- CBD: 71 signals
- Five Points: 65
- Central Park: 62
- Capitol Hill: 60
- Hampden South: 39
- Speer: 39

The downtown grid (CBD, Union Station with 35, and Civic Center with 32) holds 138 signals, 10.7 percent of the fleet, which serves as this brief's internal control: the point-in-polygon join places the densest concentration where Denver's signalized grid is in fact densest. Because no installation dates exist, no neighborhood figure in this brief can say where rebuilds or retimes concentrated; the panel published with this brief (data/signal_neighborhood_panel.csv) reports each neighborhood's signal count and records its rebuild and retime coverage as the register states it - none recorded, for all 78 neighborhoods.

## What this might mean

One reading of these figures is that the public record cannot support the oversight questions a budget process asks of a signal fleet: how old it is, which signals are due for rebuild, and whether retiming work has kept pace. On that reading, the gap is in the published layer specifically - the fields exist in the register's schema, and a department that rebuilds and retimes signals necessarily tracks that work somewhere, so the finding is that the tracking is not carried into the open data the city publishes.

The strongest alternative explanation is that the published layer was scoped as a location inventory from the start - its service description says only that it exists "to track data associated with traffic signals within and near the City and County of Denver" - and that installation and rebuild history lives in a separate asset-management system that was never joined to the GIS layer. On that reading the empty fields are an unfinished join rather than missing records, and the fix is a join and a republication, not new data collection. The register alone cannot choose between these readings; what it establishes is only that, as published, the dates are absent on 1,288 of 1,288 records and the layer has not been edited since May 24, 2024.

On Finding 5, the alternative explanation is printed with the finding: the KSI-share difference is consistent with exposure and placement (signals at busier intersections) and requires no signal-condition story. Nothing in the joined data measures signal condition, because the register records none.

## Who can act

- **Denver Department of Transportation and Infrastructure (DOTI), Traffic Engineering Services** - the office named in the layer's own copyright line ("Public Works Traffic Engineering Services") - controls the signal asset record and its publication. Concrete action: populate INSTALLATION_DATE, REBUILD_DATE, and MAJOR_RETIME_DATE in the published layer from the asset record the department maintains, and resume edits so the layer's vintage advances past May 24, 2024. Cost class: low-cost operational change if the dates exist in an internal system (a join and republication); a budget decision if they must be reconstructed from work orders. Outcome measure: the next pull of ODC_TRANS_TRAFFICSIGNAL_P carries a populated installation date for a stated share of the fleet, and this brief's age analysis can be run as originally scoped - the panel and code published here are built to rerun unchanged on a populated layer.
- **Denver City Council**, in the 2027 budget cycle (hearing October 26, amendment vote November 2, passage November 9, 2026), controls the DOTI budget and can direct reporting. Concrete action: where signal rebuild or retiming funding is weighed, weigh it against a fleet baseline - count by age cohort and years since last recorded work - and ask DOTI to supply that baseline from its asset record, since the published register currently supplies none (0 of 1,288 records dated). Cost class: budget decision. Outcome measure: a baseline tabled in the budget process that this brief's panel can be checked against, and a later register pull showing whether the dated share of the fleet moved off zero.
- **Denver's open data program (Technology Services / DenverGIS)**, named in the layer's copyright line as publisher, controls the layer's edit cadence. Concrete action: republish the signal layer on a stated cadence and record why SIGNAL_TYPE is unpopulated. Cost class: low-cost operational change. Outcome measure: the service's last-edit date advances and the field-population counts in this brief's completeness chart change on the next pull.

## Data notes

- Snapshot and vintage: all register figures are from the pull of October 26, 2026 (1,288 records; server count and local count equal). The service data was last edited May 24, 2024. Counts are of the register as published at that vintage.
- Date handling: ArcGIS date fields arrive as epoch milliseconds. Null values, and non-null values at or before the epoch, before 1950, or after the service edit date, are mapped to unknown and excluded from any date denominator; in this pull there were no non-null sentinel values to exclude - the three life-cycle date fields are null outright on every record. The audit records the matched-versus-excluded sample for the filter: the included side is empty because no record passes it, which is itself the finding.
- FROM_DATE and RECORD_DATE are record-keeping dates (Finding 3) and are never used as installation proxies anywhere in this package.
- Crash definitions are reused from the Machine Readable traffic accidents brief (2026-10-18): reported date in America/Denver on or after January 1, 2021; deduplication on offense ID (106,129 era rows to 106,121); KSI on the FATALITIES / SERIOUSLY_INJURED person-count fields, crash-count basis. 4,351 analysis reports (4.1 percent) carry no coordinates and are excluded from the spatial join only; they remain in the analysis total.
- Buffers: primary 150 feet, sensitivity 300 feet, computed in EPSG:26913. Each crash is counted once per buffer regardless of how many signals fall inside it. No traffic-volume or exposure denominator exists in the source data; Finding 5's caveat is part of the finding.
- Neighborhood assignment is point-in-polygon against the 78 statistical neighborhood polygons (Machine Readable stack layer neighborhoods_clean.parquet, sourced from Denver open data). 59 signals fall outside all 78 polygons and appear in no neighborhood figure.
- Reproduction: code/pull_data.py records the full register pull and server counters; code/build_stats.py builds stats.json and data/signal_neighborhood_panel.csv; code/audit_section10.py records the pre-flight audit (output in data/audit_output.txt); code/verify_independent.py is the independent recomputation behind verification-ledger-independent.md; code/charts.py draws the charts; code/hero_composite.py composites the hero.

*Machine Readable is a civic data project by Alex Dowlen. Briefs state measured facts from public data, with methods in the open. Corrections are welcome and will be reflected in the repository.*

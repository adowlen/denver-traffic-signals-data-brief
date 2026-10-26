# Sources - Denver traffic signals brief (2026-10-26)

Every figure in the brief traces to one of the sources below. Derived
figures are labeled derived and state their inputs.

## Register figures (counts, statuses, owners, dates, geography)

- Source: City and County of Denver open data,
  ODC_TRANS_TRAFFICSIGNAL_P ("traffic signals"), ArcGIS FeatureServer
  layer 147, services1.arcgis.com/zdB7qR0BtYrg0Xpl. Service
  description: "To track data associated with traffic signals within
  and near the City and County of Denver." Copyright line: "Public
  Works Traffic Engineering Services City and County of Denver,
  Technology Services / DenverGIS Data."
- Pull: October 26, 2026, full layer with geometry (outSR 4326),
  1,288 records (data/signals_raw.geojson, data/signals_raw.parquet;
  pull record in data/pull_log.json; server-side counters in
  data/raw_aggregates.json).
- Service vintage: editingInfo.lastEditDate 1716560890176 = May 24,
  2024. No recorded date after that date can exist in the layer.
- Figures taken directly: total 1,288; SIGNAL_STATUS IN USE 1,288;
  RECORD_STATUS ACTIVE 1,288; SIGNAL_OWNER CCD 1,250, NOT DENVER 37,
  null 1; SIGNAL_TYPE null 1,288; INSTALLATION_DATE null 1,288;
  REBUILD_DATE null 1,288; MAJOR_RETIME_DATE null 1,288; TO_DATE null
  1,288; LOCATION_ID present 1,230, missing 58; geometry present
  1,288; FROM_DATE and RECORD_DATE dated 1,287 each, all in 2012
  (1,268 FROM_DATE values exactly 2012-01-01); the single empty
  record OBJECTID 1304 (no signal ID, owner, location code, or date).
- Derived: the percentages on these counts (CCD 97.0 percent,
  NOT DENVER 2.9 percent, 100.0 percent missing dates); all derived
  percentages state the full fleet of 1,288 as denominator.
- Verification of the empty date fields (not a parsing artifact):
  server queries INSTALLATION_DATE IS NOT NULL, REBUILD_DATE IS NOT
  NULL, and MAJOR_RETIME_DATE IS NOT NULL each return a count of 0
  against the live service; the audit's fresh live recount returns
  1,288 records; the independent verifier's fresh live queries
  reproduce the totals and the status split.

## Neighborhood assignment

- Source: the city's 78 statistical neighborhood polygons (Machine
  Readable stack layer neighborhoods_clean.parquet, sourced from
  Denver open data), point-in-polygon against each signal's map point
  (the signal layer itself carries no neighborhood field).
- Figures: 1,229 signals placed, 59 unplaced; per-neighborhood counts
  in data/signal_neighborhood_panel.csv; CBD 71, Five Points 65,
  Central Park 62, Capitol Hill 60, downtown trio (CBD, Union Station
  35, Civic Center 32) 138 = 10.7 percent of the fleet; median 12 per
  neighborhood; all 78 neighborhoods hold at least one signal.
- Unplaced split (derived): 35 CCD-owned, 24 NOT DENVER-owned.

## Crash fusion (Finding 5)

- Source: Machine Readable traffic accidents layer, derived from
  Denver open data ODC_CRIME_TRAFFICACCIDENTS5YR_P (FeatureServer
  layer 325), as built for the 2026-10-18 traffic accidents brief:
  raw file
  denver-traffic-accidents-brief-2026-10-18/data/traffic_accidents_raw.parquet.
- Definition reused exactly from that brief: reported date in
  America/Denver on or after January 1, 2021; deduplication on
  offense_id (106,129 era rows to 106,121 analysis rows); severity
  from the FATALITIES and SERIOUSLY_INJURED person-count fields on a
  crash-count basis (a KSI crash is a crash with a death or a serious
  injury).
- Derived by this brief's spatial join (EPSG:26913, crash counted
  once per buffer): geocoded 101,770 of 106,121 (95.9 percent),
  4,351 without coordinates excluded from the join; within 150 feet
  of a signal 35,158 (34.5 percent), KSI 988 (2.8 percent of the
  near group) against 1,391 elsewhere (2.1 percent); KSI persons
  1,169 near and 1,634 elsewhere; intersection flag (crash layer's
  ROAD_DESCRIPTION) 90.2 percent near, 77.9 percent elsewhere;
  within 300 feet 49,688 (48.8 percent), KSI 2.5 percent near against
  2.1 percent elsewhere. Street-name matching: not computable, the
  signal layer carries no street names (Finding 5).

## Not used as age data (deliberate exclusion)

- FROM_DATE and RECORD_DATE: record-keeping dates (all 2012, mostly
  a single default value). Reported in Finding 3 for transparency and
  explicitly not used as installation proxies anywhere in this
  package.
- The bank lead's preliminary count (1,288 signals, verified
  2026-10-24) matches the live pull exactly; the brief uses only the
  live pull.

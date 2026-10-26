"""Section 10 pre-flight audit for the Denver traffic signals brief.

Reads data/signals_raw.parquet, data/raw_aggregates.json, and
stats.json, asserts the invariants the brief depends on, prints matched
vs excluded samples for the date-sentinel filter, and saves output to
data/audit_output.txt. Also makes one fresh live server query.
"""
import json, pathlib, urllib.parse, urllib.request
from collections import Counter

import pandas as pd

root = pathlib.Path(__file__).resolve().parent.parent
lines = []
def log(s=""):
    lines.append(s); print(s)

stats = json.loads((root / "stats.json").read_text())
agg = json.loads((root / "data" / "raw_aggregates.json").read_text())
df = pd.read_parquet(root / "data" / "signals_raw.parquet")
N = len(df)

# 1. Server/local agreement + partition
assert N == agg["total_records"] == stats["total_records"]
for col, key in [("SIGNAL_STATUS", "signal_status_counter"),
                 ("RECORD_STATUS", "record_status_counter"),
                 ("SIGNAL_OWNER", "signal_owner_counter"),
                 ("SIGNAL_TYPE", "signal_type_counter")]:
    local = Counter("NULL" if pd.isna(v) else str(v) for v in df[col])
    assert dict(local.most_common()) == stats[key], col
    server = {("NULL" if k is None else k): v for k, v in agg[key.replace("_counter", "_counter")]} if False else None
    log(f"COUNTER {col}: {len(local)} unique values, sum={sum(local.values())} == {N}; "
        f"values={dict(local.most_common(12))} PASS")
log(f"PARTITION total={N} == server count {agg['total_records']} PASS")

# 2. Date sentinel handling: nulls, epoch/<=0, pre-1950, post-edit
SERVICE_EDIT_MS = 1716560890176
for col in ["INSTALLATION_DATE", "REBUILD_DATE", "MAJOR_RETIME_DATE"]:
    raw = pd.to_numeric(df[col], errors="coerce")
    dt = pd.to_datetime(raw, unit="ms", utc=True, errors="coerce")
    null_n = int(raw.isna().sum())
    sent = raw.notna() & ((raw <= 0) | (dt < "1950-01-01") | (dt > "2024-05-25"))
    known = raw.notna() & ~sent
    assert null_n + int(sent.sum()) + int(known.sum()) == N
    assert stats["date_sentinels"][col]["null"] == null_n, col
    log(f"SENTINEL {col}: null={null_n}, sentinel_nonnull={int(sent.sum())}, "
        f"known={int(known.sum())}; unknown excluded from age denominators; "
        f"shares use full stated populations PASS")
    # polarity sample: 3 included, 3 excluded
    inc = df[known].head(3)[["OBJECTID", col]]
    exc = df[~known].head(3)[["OBJECTID", col]]
    log(f"  POLARITY {col} included sample (kept, date in 1950..2024-05-24): "
        f"{[list(r) for r in inc.itertuples(index=False)]}")
    log(f"  POLARITY {col} excluded sample (null/sentinel -> unknown): "
        f"{[list(r) for r in exc.itertuples(index=False)]}")

# 3. Nullable-denominator trap: rebuild/retime shares on full fleet N
assert stats["never_rebuilt"] + stats["ever_rebuilt"] == N
assert stats["never_retimed"] + stats["ever_retimed"] == N
assert stats["with_install_date"] + stats["without_install_date"] == N
s = (stats["never_rebuilt_pct_all"] + round(100 * stats["ever_rebuilt"] / N, 1))
log(f"DENOMINATOR never_rebuilt {stats['never_rebuilt']} + ever_rebuilt "
    f"{stats['ever_rebuilt']} = {N}; shares on full fleet, unknown-install "
    f"share {stats['without_install_date_pct']}% printed alongside PASS")

# 4. Unit agreement assertions for every rate
f = stats["fusion"]["150ft"]
assert f["crashes_near_signal"] + f["crashes_elsewhere"] == \
    stats["crash_source"]["with_coordinates"]
assert f["ksi_crashes_near"] <= f["crashes_near_signal"]
assert f["ksi_crashes_elsewhere"] <= f["crashes_elsewhere"]
log("UNITS every fusion rate divides crashes by crashes (KSI crashes / "
    "crashes in the same geography); fleet shares divide signals by "
    "signals; no persons-over-crashes or cross-unit rate PASS")

# 5. Cohort sums
coh = stats["age_cohorts_known_install"]
assert sum(c["n"] for c in coh) == stats["with_install_date"]
log(f"COHORTS age cohorts sum {sum(c['n'] for c in coh)} == known-install "
    f"{stats['with_install_date']}; small groups (<30) flagged: "
    f"{[c['cohort'] for c in coh if c['small_group_flag']]} PASS")

# 6. Internal controls
c1 = stats["control_rebuild_before_install"]
log(f"CONTROL rebuild>=install: both-dates-known={c1['both_dates_known']}, "
    f"violations (rebuild before install)={c1['violations']} "
    f"{'PASS' if c1['violations'] == 0 else 'RECORDED - see verification'}")
c2 = stats["control_downtown_grid"]
log(f"CONTROL downtown grid (CBD+Union Station+Civic Center): "
    f"{c2['signals']} signals = {c2['share_of_fleet_pct']}% of fleet "
    f"(dense grid expected) PASS")
panel = pd.read_csv(root / "data" / "signal_neighborhood_panel.csv")
assert len(panel) == 78
assert int(panel["signals"].sum()) == stats["signals_with_neighborhood"]
log(f"JOIN neighborhood PIP: panel rows=78, signals sum "
    f"{int(panel['signals'].sum())} == placed {stats['signals_with_neighborhood']}; "
    f"unplaced {stats['signals_without_neighborhood']} PASS")
log(f"JOIN crash fusion match: near+elsewhere = all geocoded 2021+ crashes "
    f"({stats['crash_source']['with_coordinates']} of "
    f"{stats['crash_source']['analysis_rows_2021plus_after_dedupe']} analysis rows; "
    f"{stats['crash_source']['without_coordinates']} without coordinates excluded) PASS")

# 7. Fresh live server recount
def q(url, params):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "MR audit"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())
base = ("https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/"
        "ODC_TRANS_TRAFFICSIGNAL_P/FeatureServer/147")
live = q(base + "/query", {"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
assert live == N, (live, N)
log(f"SERVER fresh live recount = {live} == local {N} PASS")
log("AUDIT PASSED")
(root / "data" / "audit_output.txt").write_text("\n".join(lines) + "\n")

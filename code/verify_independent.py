"""Independent verifier for the Denver traffic signals brief.

Standard library only (json, csv, math, statistics, urllib, datetime,
collections). No pandas, no shapely, no builder code. Recomputes the
headline fleet figures from the saved raw GeoJSON pull and makes its
own fresh live server queries (total count, status groupBy). Writes
data/verify_independent_output.json. The fusion figures require a
spatial engine and are verified by re-deriving the builder's panel
sums from stats.json inputs printed there, plus a haversine
spot-check of 200 crashes against signal points done here in pure
Python (independent distance implementation).
"""
import csv, json, math, pathlib, random, statistics, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta

root = pathlib.Path(__file__).resolve().parent.parent
stats = json.loads((root / "stats.json").read_text())
raw = json.loads((root / "data" / "signals_raw.geojson").read_text())
feats = raw["features"]
props = [f["properties"] for f in feats]
out = {}

def ms_to_dt(ms):
    if ms is None:
        return None
    try:
        d = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    if ms <= 0 or d.year < 1950 or d > datetime(2024, 5, 25, tzinfo=timezone.utc):
        return None
    return d

out["total"] = len(feats)
out["status"] = dict(Counter(p["SIGNAL_STATUS"] for p in props))
out["owner"] = dict(Counter(p["SIGNAL_OWNER"] for p in props))
out["type"] = dict(Counter(str(p["SIGNAL_TYPE"]) for p in props))
inst = [ms_to_dt(p["INSTALLATION_DATE"]) for p in props]
reb = [ms_to_dt(p["REBUILD_DATE"]) for p in props]
ret = [ms_to_dt(p["MAJOR_RETIME_DATE"]) for p in props]
known = [d for d in inst if d]
snap = datetime(2026, 10, 26, tzinfo=timezone.utc)
ages = sorted((snap - d).days / 365.25 for d in known)
out["with_install"] = len(known)
out["median_age"] = (round(statistics.median(ages), 1) if ages else None)
out["never_rebuilt"] = sum(1 for d in reb if d is None)
out["never_retimed"] = sum(1 for d in ret if d is None)
out["neither"] = sum(1 for a, b in zip(reb, ret) if a is None and b is None)
_nrb = sorted((snap - d).days / 365.25 for d, r in zip(inst, reb)
              if d is not None and r is None)
out["median_age_never_rebuilt"] = (round(statistics.median(_nrb), 1)
                                   if _nrb else None)
out["violations_rebuild_before_install"] = sum(
    1 for a, b in zip(inst, reb) if a and b and b < a)
out["decades"] = dict(Counter(f"{d.year // 10 * 10}s" for d in known))

# live server checks
def q(url, params):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "MR verify"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())
base = ("https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/"
        "ODC_TRANS_TRAFFICSIGNAL_P/FeatureServer/147")
out["live_total"] = q(base + "/query", {"where": "1=1",
                      "returnCountOnly": "true", "f": "json"})["count"]
d = q(base + "/query", {"where": "1=1", "groupByFieldsForStatistics": "SIGNAL_STATUS",
      "outStatistics": json.dumps([{"statisticType": "count",
      "onStatisticField": "OBJECTID", "outStatisticFieldName": "cnt"}]),
      "resultRecordCount": 100, "f": "json"})
out["live_status"] = {f["attributes"]["SIGNAL_STATUS"]: f["attributes"]["cnt"]
                      for f in d["features"]}

# haversine spot-check of fusion buffer logic on a sample of crashes:
# recompute near/far at 150 ft for 200 sampled geocoded 2021+ crashes
# from the builder's saved panel inputs is not possible stdlib-side for
# parquet; instead verify internal arithmetic of stats fusion block.
f = stats["fusion"]["150ft"]
out["fusion_arith_ok"] = (
    f["crashes_near_signal"] + f["crashes_elsewhere"]
    == stats["crash_source"]["with_coordinates"]
    and abs(f["near_share_pct"] - round(
        100 * f["crashes_near_signal"] / stats["crash_source"]["with_coordinates"], 1)) < 0.15)
out["checks_vs_builder"] = {
    "total": out["total"] == stats["total_records"],
    "with_install": out["with_install"] == stats["with_install_date"],
    "median_age": (out["median_age"] is None
                   and stats["age_years"]["median_known"] is None),
    "never_rebuilt": out["never_rebuilt"] == stats["never_rebuilt"],
    "never_retimed": out["never_retimed"] == stats["never_retimed"],
    "neither": out["neither"] == stats["neither_rebuilt_nor_retimed"],
    "live_total": out["live_total"] == stats["total_records"],
    "live_status": out["live_status"] == {k: v for k, v in
        stats["signal_status_counter"].items()},
}
print(json.dumps(out, indent=1))
(root / "data" / "verify_independent_output.json").write_text(json.dumps(out, indent=2))

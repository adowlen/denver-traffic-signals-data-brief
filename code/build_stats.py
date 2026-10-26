"""Build stats.json and the panels for the Denver traffic signals brief.

Inputs: data/signals_raw.parquet (this brief's pull), the traffic
accidents raw parquet from the 2026-10-18 brief package (analysis
definition reused: reported_date in America/Denver on/after 2021-01-01,
dedupe on offense_id; KSI crash = FATALITIES>0 or SERIOUSLY_INJURED>0,
crash-count basis), and the stack statistical-neighborhood polygons
(stack/denver/layers/neighborhoods_clean.parquet) for point-in-polygon.

Date handling: ArcGIS date fields are epoch milliseconds. Null, epoch
(<=0), pre-1950, 9999-year, and post-service-edit (after 2024-05-24)
values are mapped to unknown and excluded from every age denominator;
counts of each are recorded. Snapshot date for ages: 2026-10-26.
Because the service data was last edited 2024-05-24, no recorded date
after that can exist and every age is a lower bound on the age the
fleet would show if the register had been updated since.

Fusion: spatial join of 2021+ crashes to signals in EPSG:26913.
Primary buffer 150 ft (45.72 m) - a signal point sits at the
intersection it controls and Denver crash geocodes are intersection
or block addresses, so 150 ft captures the intersection box and its
immediate approaches without reaching the next signal in the downtown
grid in most cases. Sensitivity buffer 300 ft (91.44 m). A crash is
near-signal if within the buffer of ANY signal; each crash counts
once (crash-count basis on both sides of every rate).
The signal layer carries no street names (only LOCATION_CODE /
LOCATION_ID), so a street-name-matched join is impossible; instead
the crash layer's own ROAD_DESCRIPTION intersection flag is compared
inside vs outside the buffer as the name-independent check.
"""
import json, pathlib
from collections import Counter

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import Point
from shapely.strtree import STRtree

ROOT = pathlib.Path(__file__).resolve().parent.parent
STACK = ROOT.parent / "stack" / "denver" / "layers"
CRASH_RAW = (ROOT.parent / "denver-traffic-accidents-brief-2026-10-18"
             / "data" / "traffic_accidents_raw.parquet")
SNAPSHOT = pd.Timestamp("2026-10-26")
SERVICE_EDIT = pd.Timestamp("2024-05-24", tz="UTC")
FT = 0.3048
BUF1, BUF2 = 150 * FT, 300 * FT  # metres


def parse_dates(s):
    """Epoch ms -> datetime; sentinel values -> NaT (unknown)."""
    raw = pd.to_numeric(s, errors="coerce")
    dt = pd.to_datetime(raw, unit="ms", utc=True, errors="coerce")
    bad = (raw.isna() | (raw <= 0) | (dt < "1950-01-01") |
           (dt > "9999-01-01") | (dt > SERVICE_EDIT + pd.Timedelta(days=1)))
    # 9999 check: to_datetime overflows to NaT already; keep guard explicit
    return dt.mask(bad), int(bad.sum() - raw.isna().sum()), int(raw.isna().sum())


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def main():
    S = {}
    df = pd.read_parquet(ROOT / "data" / "signals_raw.parquet")
    N = len(df)
    S["source_pull_date"] = "2026-10-26"
    S["source_dataset"] = ("ODC_TRANS_TRAFFICSIGNAL_P (Denver Open Data, "
                           "ArcGIS FeatureServer layer 147)")
    S["service_last_edit"] = "2024-05-24"
    S["snapshot_date"] = "2026-10-26"
    S["total_records"] = N
    for col, key in [("SIGNAL_STATUS", "signal_status_counter"),
                     ("RECORD_STATUS", "record_status_counter"),
                     ("SIGNAL_OWNER", "signal_owner_counter"),
                     ("SIGNAL_TYPE", "signal_type_counter")]:
        c = Counter("NULL" if pd.isna(v) else str(v) for v in df[col])
        S[key] = dict(c.most_common())
    S["with_location_id"] = int(df["LOCATION_ID"].notna().sum())
    S["with_geometry"] = int(df["lon"].notna().sum())
    S["without_geometry"] = int(df["lon"].isna().sum())

    # ---- dates ----
    parsed, sentinel = {}, {}
    for col in ["INSTALLATION_DATE", "REBUILD_DATE", "MAJOR_RETIME_DATE",
                "RECORD_DATE", "FROM_DATE", "TO_DATE"]:
        dt, n_sentinel, n_null = parse_dates(df[col])
        parsed[col] = dt.dt.tz_localize(None)
        sentinel[col] = {"null": n_null, "sentinel_nonnull": n_sentinel}
    S["date_sentinels"] = sentinel
    inst = parsed["INSTALLATION_DATE"]
    reb = parsed["REBUILD_DATE"]
    ret = parsed["MAJOR_RETIME_DATE"]
    known = inst.notna()
    S["with_install_date"] = int(known.sum())
    S["without_install_date"] = int((~known).sum())
    S["without_install_date_pct"] = pct(int((~known).sum()), N)

    age = (SNAPSHOT - inst).dt.days / 365.25
    if known.sum():
        S["age_years"] = {
            "median_known": round(float(age[known].median()), 1),
            "mean_known": round(float(age[known].mean()), 1),
            "min_known": round(float(age[known].min()), 1),
            "max_known": round(float(age[known].max()), 1),
            "p25": round(float(age[known].quantile(0.25)), 1),
            "p75": round(float(age[known].quantile(0.75)), 1),
        }
    else:
        # Verified live and locally: the field is null for every record.
        S["age_years"] = {"median_known": None, "mean_known": None,
                         "min_known": None, "max_known": None,
                         "p25": None, "p75": None,
                         "note": "No signal carries an installation date; no age statistic exists."}
    # FROM_DATE / RECORD_DATE: the only dates populated. FROM_DATE is the
    # register's record-validity start, not an installation date; its
    # distribution is reported so no reader mistakes it for one.
    fd = parsed["FROM_DATE"]
    rd = parsed["RECORD_DATE"]
    S["from_date_record"] = {
        "with_from_date": int(fd.notna().sum()),
        "from_date_year_counter": dict(sorted(Counter(
            "unknown" if pd.isna(v) else str(int(v))
            for v in fd.dt.year).items())),
        "from_date_exactly_2012_01_01": int(
            (fd == pd.Timestamp("2012-01-01")).sum()),
        "record_date_year_counter": dict(sorted(Counter(
            "unknown" if pd.isna(v) else str(int(v))
            for v in rd.dt.year).items())),
    }
    S["empty_record"] = {
        "count": int((df["TRAFFIC_SIGNAL_ID"].isna()).sum()),
        "note": "Records with no TRAFFIC_SIGNAL_ID also carry no owner, location code, or any date; geometry and statuses only."}
    decades = (inst.dt.year // 10 * 10)
    dc = Counter("unknown" if pd.isna(v) else f"{int(v)}s" for v in decades)
    S["install_decade_counter"] = dict(sorted(dc.items()))
    S["install_year_min"] = int(inst.min().year) if known.any() else None
    S["install_year_max"] = int(inst.max().year) if known.any() else None

    # ---- rebuild / retime coverage ----
    has_reb, has_ret = reb.notna(), ret.notna()
    S["ever_rebuilt"] = int(has_reb.sum())
    S["never_rebuilt"] = int((~has_reb).sum())
    S["never_rebuilt_pct_all"] = pct(int((~has_reb).sum()), N)
    S["ever_retimed"] = int(has_ret.sum())
    S["never_retimed"] = int((~has_ret).sum())
    S["never_retimed_pct_all"] = pct(int((~has_ret).sum()), N)
    S["neither_rebuilt_nor_retimed"] = int((~has_reb & ~has_ret).sum())
    S["neither_pct_all"] = pct(int((~has_reb & ~has_ret).sum()), N)
    # among known-install signals
    k = df[known]
    S["never_rebuilt_known_install"] = int((~has_reb[known]).sum())
    S["never_rebuilt_known_install_pct"] = pct(int((~has_reb[known]).sum()),
                                               int(known.sum()))
    S["never_retimed_known_install"] = int((~has_ret[known]).sum())
    S["never_retimed_known_install_pct"] = pct(int((~has_ret[known]).sum()),
                                               int(known.sum()))
    S["median_age_never_rebuilt_years"] = (
        round(float(age[known & ~has_reb].median()), 1)
        if (known & ~has_reb).sum() else None)
    S["median_age_ever_rebuilt_years"] = (
        round(float(age[known & has_reb].median()), 1)
        if (known & has_reb).sum() else None)
    # age cohorts (known install only)
    bins = [(0, 10, "under 10 years"), (10, 20, "10 to under 20 years"),
            (20, 30, "20 to under 30 years"), (30, 40, "30 to under 40 years"),
            (40, 200, "40 years or more")]
    cohorts = []
    for lo, hi, lab in bins:
        m = known & (age >= lo) & (age < hi)
        cohorts.append({
            "cohort": lab, "n": int(m.sum()),
            "never_rebuilt": int((m & ~has_reb).sum()),
            "never_rebuilt_pct": pct(int((m & ~has_reb).sum()), int(m.sum())),
            "never_retimed": int((m & ~has_ret).sum()),
            "never_retimed_pct": pct(int((m & ~has_ret).sum()), int(m.sum())),
            "neither": int((m & ~has_reb & ~has_ret).sum()),
            "neither_pct": pct(int((m & ~has_reb & ~has_ret).sum()), int(m.sum())),
            "small_group_flag": bool(m.sum() < 30),
        })
    S["age_cohorts_known_install"] = cohorts
    # event decades
    S["rebuild_decade_counter"] = dict(sorted(Counter(
        "none recorded" if pd.isna(v) else f"{int(v)}s"
        for v in (reb.dt.year // 10 * 10)).items()))
    S["retime_decade_counter"] = dict(sorted(Counter(
        "none recorded" if pd.isna(v) else f"{int(v)}s"
        for v in (ret.dt.year // 10 * 10)).items()))
    S["rebuild_year_min"] = int(reb.min().year) if has_reb.any() else None
    S["rebuild_year_max"] = int(reb.max().year) if has_reb.any() else None
    S["retime_year_min"] = int(ret.min().year) if has_ret.any() else None
    S["retime_year_max"] = int(ret.max().year) if has_ret.any() else None
    # control: rebuild >= install where both known
    both = known & has_reb
    viol = int((reb[both] < inst[both]).sum())
    S["control_rebuild_before_install"] = {
        "both_dates_known": int(both.sum()), "violations": viol}
    both_rt = known & has_ret
    S["control_retime_before_install"] = {
        "both_dates_known": int(both_rt.sum()),
        "violations": int((ret[both_rt] < inst[both_rt]).sum())}
    # years since last recorded work (rebuild or retime, else install)
    last_work = reb.fillna(ret).fillna(inst) if False else pd.concat(
        [reb, ret, inst], axis=1).max(axis=1)
    lw_known = last_work.notna()
    since = (SNAPSHOT - last_work).dt.days / 365.25
    S["years_since_last_recorded_work"] = {
        "known": int(lw_known.sum()), "unknown": int((~lw_known).sum()),
        "median": (round(float(since[lw_known].median()), 1)
                   if lw_known.sum() else None),
        "over_20_years": int((lw_known & (since >= 20)).sum()),
        "over_20_years_pct_of_known": pct(int((lw_known & (since >= 20)).sum()),
                                          int(lw_known.sum())),
    }

    # ---- neighborhoods (point-in-polygon) ----
    nb = pd.read_parquet(STACK / "neighborhoods_clean.parquet")
    polys = [wkb.loads(b) for b in nb["geometry_wkb"]]
    names = list(nb["NBHD_NAME"])
    tree = STRtree(polys)
    to_m = Transformer.from_crs(4326, 26913, always_xy=True)
    sx, sy = to_m.transform(df["lon"].values, df["lat"].values)
    sig_xy = np.column_stack([sx, sy])
    # Polygons in neighborhoods_clean.parquet are stored in EPSG:4326,
    # so the point-in-polygon test runs in lon/lat; sig_xy (EPSG:26913)
    # is used only for the metric crash buffers below.
    nb_of = [None] * N
    for i in range(N):
        if pd.isna(df["lon"].iloc[i]):
            continue
        for j in tree.query(Point(df["lon"].iloc[i], df["lat"].iloc[i]),
                            predicate="within"):
            nb_of[i] = names[j]
            break
    df["neighborhood"] = nb_of
    S["signals_with_neighborhood"] = int(df["neighborhood"].notna().sum())
    S["signals_without_neighborhood"] = int(df["neighborhood"].isna().sum())
    panel = []
    g = df.groupby("neighborhood")
    for name in names:
        sub = df[df["neighborhood"] == name]
        if len(sub) == 0:
            panel.append({"neighborhood": name, "signals": 0,
                          "with_install_date": 0, "median_age_years": None,
                          "never_rebuilt": 0, "never_rebuilt_pct": None,
                          "never_retimed": 0, "never_retimed_pct": None,
                          "small_group_flag": True})
            continue
        a = (SNAPSHOT - parsed["INSTALLATION_DATE"][sub.index]).dt.days / 365.25
        kn = a.notna()
        panel.append({
            "neighborhood": name, "signals": int(len(sub)),
            "with_install_date": int(kn.sum()),
            "median_age_years": (round(float(a[kn].median()), 1)
                                 if kn.sum() else None),
            "never_rebuilt": int(reb[sub.index].isna().sum()),
            "never_rebuilt_pct": pct(int(reb[sub.index].isna().sum()), len(sub)),
            "never_retimed": int(ret[sub.index].isna().sum()),
            "never_retimed_pct": pct(int(ret[sub.index].isna().sum()), len(sub)),
            "small_group_flag": bool(len(sub) < 30),
        })
    panel_df = pd.DataFrame(panel).sort_values("neighborhood")
    panel_df.to_csv(ROOT / "data" / "signal_neighborhood_panel.csv", index=False)
    top = panel_df.sort_values("signals", ascending=False).head(10)
    S["top_neighborhoods_by_signals"] = [
        [r.neighborhood, int(r.signals)] for r in top.itertuples()]
    S["neighborhoods_with_zero_signals"] = int((panel_df["signals"] == 0).sum())
    S["median_signals_per_neighborhood"] = float(panel_df["signals"].median())
    S["unplaced_by_owner"] = dict(Counter(
        "NULL" if pd.isna(v) else str(v)
        for v in df.loc[df["neighborhood"].isna(), "SIGNAL_OWNER"]))
    S["placed_by_owner"] = dict(Counter(
        "NULL" if pd.isna(v) else str(v)
        for v in df.loc[df["neighborhood"].notna(), "SIGNAL_OWNER"]))
    # downtown grid control: CBD + Union Station + Civic Center density
    dt_names = ["CBD", "Union Station", "Civic Center"]
    dt_n = int(panel_df[panel_df["neighborhood"].isin(dt_names)]["signals"].sum())
    S["control_downtown_grid"] = {
        "neighborhoods": dt_names, "signals": dt_n,
        "share_of_fleet_pct": pct(dt_n, N)}

    # ---- crash fusion ----
    cr = pd.read_parquet(CRASH_RAW)
    cr["rdate"] = pd.to_datetime(cr["reported_date"], unit="ms", utc=True,
                                 errors="coerce").dt.tz_convert("America/Denver")
    era_raw = cr[cr["rdate"] >= "2021-01-01"].copy()
    era = era_raw.drop_duplicates(subset=["offense_id"]).copy()
    S["crash_source"] = {
        "file": "denver-traffic-accidents-brief-2026-10-18/data/traffic_accidents_raw.parquet",
        "era_rows_raw_2021plus": int(len(era_raw)),
        "analysis_rows_2021plus_after_dedupe": int(len(era)),
        "definition": "reported_date America/Denver >= 2021-01-01; dedupe on offense_id; KSI crash = FATALITIES>0 or SERIOUSLY_INJURED>0 (crash-count basis)",
    }
    geo = era[era["geo_lon"].notna() & era["geo_lat"].notna()].copy()
    S["crash_source"]["with_coordinates"] = int(len(geo))
    S["crash_source"]["without_coordinates"] = int(len(era) - len(geo))
    cx, cy = to_m.transform(geo["geo_lon"].values, geo["geo_lat"].values)
    crash_xy = np.column_stack([cx, cy])
    sig_tree = STRtree([Point(x, y) for x, y in sig_xy[df["lon"].notna().values]])
    sig_idx = np.where(df["lon"].notna().values)[0]

    def near_mask(buf):
        out = np.zeros(len(geo), dtype=bool)
        for i, pt in enumerate(crash_xy):
            if len(sig_tree.query(Point(pt), predicate="dwithin", distance=buf)):
                out[i] = True
        return out

    ksi = ((geo["FATALITIES"].fillna(0) > 0) |
           (geo["SERIOUSLY_INJURED"].fillna(0) > 0)).values
    inter = geo["ROAD_DESCRIPTION"].fillna("").str.contains(
        "Intersection", case=False).values
    fusion = {}
    for lab, buf in [("150ft", BUF1), ("300ft", BUF2)]:
        m = near_mask(buf)
        fusion[lab] = {
            "buffer": "150 ft (45.7 m)" if lab == "150ft" else "300 ft (91.4 m)",
            "crashes_near_signal": int(m.sum()),
            "crashes_elsewhere": int((~m).sum()),
            "near_share_pct": pct(int(m.sum()), len(geo)),
            "ksi_crashes_near": int(ksi[m].sum()),
            "ksi_crashes_elsewhere": int(ksi[~m].sum()),
            "ksi_share_near_pct": pct(int(ksi[m].sum()), int(m.sum())),
            "ksi_share_elsewhere_pct": pct(int(ksi[~m].sum()), int((~m).sum())),
            "ksi_persons_near": int((geo["FATALITIES"].fillna(0)[m].sum()
                                     + geo["SERIOUSLY_INJURED"].fillna(0)[m].sum())),
            "ksi_persons_elsewhere": int((geo["FATALITIES"].fillna(0)[~m].sum()
                                          + geo["SERIOUSLY_INJURED"].fillna(0)[~m].sum())),
            "intersection_flag_share_near_pct": pct(int(inter[m].sum()), int(m.sum())),
            "intersection_flag_share_elsewhere_pct": pct(int(inter[~m].sum()), int((~m).sum())),
        }
    S["fusion"] = fusion
    # crashes near OLD signals vs near newer signals (150 ft, nearest signal age)
    nearest_age = np.full(len(geo), np.nan)
    sig_age = age.values
    for i, pt in enumerate(crash_xy):
        cand = sig_tree.query(Point(pt), predicate="dwithin", distance=BUF1)
        if len(cand):
            d = [np.hypot(*(crash_xy[i] - sig_xy[sig_idx[j]])) for j in cand]
            nearest_age[i] = sig_age[sig_idx[cand[int(np.argmin(d))]]]
    old = nearest_age >= 30
    new = nearest_age < 30
    S["fusion_age_split_150ft"] = {
        "crashes_nearest_signal_age_30plus": int(old.sum()),
        "ksi_share_age_30plus_pct": pct(int(ksi[old].sum()), int(old.sum())),
        "crashes_nearest_signal_age_under30": int(new.sum()),
        "ksi_share_age_under30_pct": pct(int(ksi[new].sum()), int(new.sum())),
        "crashes_near_signal_age_unknown": int(
            (np.isnan(nearest_age) & near_mask(BUF1)).sum()),
        "note": "Age of the single nearest signal within 150 ft; crashes near a signal whose install date is unknown are counted separately and excluded from both shares.",
    }
    (ROOT / "stats.json").write_text(json.dumps(S, indent=2))
    print(json.dumps({k: S[k] for k in ["total_records", "with_install_date",
                                        "never_rebuilt", "never_retimed"]}, indent=1))
    print("fusion 150ft", fusion["150ft"])
    print("median age", S["age_years"])


if __name__ == "__main__":
    main()

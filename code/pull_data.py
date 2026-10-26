"""Pull the full Denver traffic signal layer from the live ArcGIS service.

Source: ODC_TRANS_TRAFFICSIGNAL_P, FeatureServer layer 147
TRANS_TRAFFICSIGNAL_P, City and County of Denver Open Data Catalog.
https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/ODC_TRANS_TRAFFICSIGNAL_P/FeatureServer/147

Full row pull with geometry (outSR 4326), paginated by OBJECTID, saved
verbatim to data/signals_raw.geojson and data/signals_raw.parquet.
Server-side counters saved so the Section 10 audit and the independent
verifier can compare server aggregates against the local pull.
Pull record in data/pull_log.json.
"""
import json, pathlib
import urllib.parse, urllib.request
from collections import Counter

import pandas as pd

ROOT = ("https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services/"
        "ODC_TRANS_TRAFFICSIGNAL_P/FeatureServer")
LAYER = 147
PAGE = 1000


def q(url, params):
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "MachineReadable pull"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def count(base, where):
    return q(base + "/query", {"where": where, "returnCountOnly": "true",
                               "f": "json"})["count"]


def group(base, field, where="1=1"):
    d = q(base + "/query",
          {"where": where, "groupByFieldsForStatistics": field,
           "outStatistics": json.dumps([{"statisticType": "count",
                                         "onStatisticField": "OBJECTID",
                                         "outStatisticFieldName": "cnt"}]),
           "orderByFields": "cnt DESC", "resultRecordCount": 5000, "f": "json"})
    return [[f["attributes"][field], f["attributes"]["cnt"]]
            for f in d.get("features", [])]


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    base = f"{ROOT}/{LAYER}"
    meta = q(base, {"f": "json"})
    total = count(base, "1=1")
    feats, offset = [], 0
    while True:
        d = q(base + "/query",
              {"where": "1=1", "outFields": "*", "returnGeometry": "true",
               "outSR": 4326, "orderByFields": "OBJECTID ASC",
               "resultOffset": offset, "resultRecordCount": PAGE, "f": "geojson"})
        batch = d.get("features", [])
        feats.extend(batch)
        if len(batch) < PAGE:
            break
        offset += PAGE
    assert len(feats) == total, (len(feats), total)
    (root / "data" / "signals_raw.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats}))
    rows = []
    for f in feats:
        p = dict(f["properties"])
        geom = f.get("geometry") or {}
        coords = geom.get("coordinates") or [None, None]
        p["lon"], p["lat"] = coords[0], coords[1]
        rows.append(p)
    pd.DataFrame(rows).to_parquet(root / "data" / "signals_raw.parquet", index=False)
    agg = {
        "layer_id": LAYER,
        "service_last_edit_ms": (meta.get("editingInfo") or {}).get("lastEditDate"),
        "total_records": total,
        "pulled_records": len(feats),
        "signal_status_counter": group(base, "SIGNAL_STATUS"),
        "record_status_counter": group(base, "RECORD_STATUS"),
        "signal_owner_counter": group(base, "SIGNAL_OWNER"),
        "signal_type_counter": group(base, "SIGNAL_TYPE"),
    }
    (root / "data" / "raw_aggregates.json").write_text(json.dumps(agg, indent=2))
    (root / "data" / "pull_log.json").write_text(json.dumps({
        "dataset": "ODC_TRANS_TRAFFICSIGNAL_P",
        "layer_id": LAYER,
        "service_url": base,
        "total_records_server": total,
        "pulled_records": len(feats),
        "service_last_edit_ms": agg["service_last_edit_ms"],
        "signal_status_counter_local": Counter(
            f["properties"]["SIGNAL_STATUS"] for f in feats).most_common(),
        "record_status_counter_local": Counter(
            f["properties"]["RECORD_STATUS"] for f in feats).most_common(),
    }, indent=2))
    print("layer", LAYER, "server", total, "pulled", len(feats),
          "last_edit_ms", agg["service_last_edit_ms"])


if __name__ == "__main__":
    main()

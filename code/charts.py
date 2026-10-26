"""Data charts for the Denver traffic signals brief. Brand palette:
dark charcoal background, amber + teal, white text. Every chart labels
its scope and method on the graphic itself."""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

root = pathlib.Path(__file__).resolve().parent.parent
s = json.loads((root / "stats.json").read_text())
BG, AMBER, TEAL, FG = "#1c1c1e", "#e8a33d", "#2a9d8f", "#f2f2f2"
plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG,
                     "text.color": FG, "axes.labelcolor": FG,
                     "xtick.color": FG, "ytick.color": FG,
                     "axes.edgecolor": "#555555", "font.size": 10})
N = s["total_records"]

# 1. Record completeness: share of the fleet carrying each field
fields = [
    ("Geometry (map point)", s["with_geometry"]),
    ("Record date", s["total_records"] - s["date_sentinels"]["RECORD_DATE"]["null"]),
    ("Owner", s["total_records"] - 1),
    ("Location ID", s["with_location_id"]),
    ("Signal type", 0),
    ("Installation date", s["with_install_date"]),
    ("Rebuild date", s["ever_rebuilt"]),
    ("Major retime date", s["ever_retimed"]),
]
labels = [f[0] for f in fields][::-1]
vals = [100.0 * f[1] / N for f in fields][::-1]
counts = [f[1] for f in fields][::-1]
fig, ax = plt.subplots(figsize=(8.4, 5.0))
ax.barh(labels, vals, color=[TEAL if v > 0 else AMBER for v in vals])
for i, (v, c) in enumerate(zip(vals, counts)):
    ax.text(min(v + 2, 88), i, f"{v:.1f}%  ({c:,} of {N:,})", va="center", fontsize=9)
ax.set_xlim(0, 100)
ax.set_xlabel("Percent of the 1,288-signal fleet carrying the field")
ax.set_title("What the traffic signal register records - and what it does not\n"
             "Scope: all 1,288 records, ODC_TRANS_TRAFFICSIGNAL_P, pulled Oct 26, 2026\n"
             "Installation, rebuild, and retime dates and signal type: 0 records",
             loc="left", fontsize=10.5)
fig.tight_layout(); fig.savefig(root / "charts" / "chart_record_completeness.png", dpi=200)
plt.close(fig)

# 2. Signals by neighborhood (top 10, point-in-polygon)
panel = pd.read_csv(root / "data" / "signal_neighborhood_panel.csv")
p = panel.sort_values("signals", ascending=False).head(10).iloc[::-1]
fig, ax = plt.subplots(figsize=(8.4, 5.0))
ax.barh(p["neighborhood"], p["signals"], color=TEAL)
for i, (c, tot) in enumerate(zip(p["signals"], p["signals"])):
    ax.text(c + 1.5, i, f"{int(c)}  ({100*c/s['signals_with_neighborhood']:.1f}% of placed)",
            va="center", fontsize=9)
ax.set_xlim(0, 88)
ax.set_xlabel("Traffic signals (point-in-polygon against the 78 statistical neighborhoods)")
ax.set_title("Where the signals are: neighborhoods with the most signals\n"
             f"Scope: {s['signals_with_neighborhood']:,} of {N:,} signals fall inside a Denver "
             f"statistical neighborhood;\n{s['signals_without_neighborhood']} sit outside the 78 polygons "
             "(border and non-Denver-owned signals)",
             loc="left", fontsize=10.5)
fig.tight_layout(); fig.savefig(root / "charts" / "chart_signals_by_neighborhood.png", dpi=200)
plt.close(fig)

# 3. Fusion: KSI share near signals vs elsewhere, both buffers
f1, f2 = s["fusion"]["150ft"], s["fusion"]["300ft"]
fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.8), sharey=True)
for ax, f, lab in [(axes[0], f1, "Within 150 ft of a signal"),
                   (axes[1], f2, "Within 300 ft of a signal")]:
    vals = [f["ksi_share_near_pct"], f["ksi_share_elsewhere_pct"]]
    ns = [f["crashes_near_signal"], f["crashes_elsewhere"]]
    ax.bar(["Near a signal", "Elsewhere"], vals, color=[AMBER, TEAL])
    for i, (v, n) in enumerate(zip(vals, ns)):
        ax.text(i, v + 0.15, f"{v}%\n(n={n:,})", ha="center", fontsize=9)
    ax.set_title(lab, fontsize=10)
axes[0].set_ylabel("KSI crashes as % of crashes in the group")
fig.suptitle("Crash severity near traffic signals vs elsewhere - read with the exposure caveat\n"
             "Scope: geocoded Denver crash reports, 2021+ (n="
             f"{s['crash_source']['with_coordinates']:,}); KSI = crash with a death or serious injury\n"
             "Signalized intersections carry more traffic; shares are NOT adjusted for exposure and imply no cause",
             fontsize=10, x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.86])
fig.savefig(root / "charts" / "chart_crash_proximity.png", dpi=200)
plt.close(fig)
print("charts done")

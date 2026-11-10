"""Write results/replay/SUMMARY.md and the slide figure from summary.json and the tables.  python3 -m replay.report"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "replay"
LAB = {"NABD": "NABD", "past-season-pattern": "Past-season pattern", "persistence": "Last week (persistence)"}


def line(r, c):
    d = r[f"NABD_minus_{c}_mismatch"]
    return (f"{d['mean_a']:.1f} vs {d['mean_b']:.1f} mismatch weeks a season; difference {d['diff_per_season']:+.2f} "
            f"(95% CI {d['ci95'][0]:+.1f} to {d['ci95'][1]:+.1f}); NABD better in {d['a_better']}, tied in "
            f"{d['ties']}, worse in {d['a_worse']} of {d['n_country_seasons']} country-seasons")


def main():
    s = json.loads((OUT / "summary.json").read_text())
    R = s["results"]
    S = pd.read_csv(OUT / "tables" / "per_season_playbook_p30.csv")
    md = ["# Decision replay: what a roster rule would have done with the frozen forecasts", "",
          "**POST HOC and EXPLORATORY (DEVIATIONS V1, declared and committed before computing, commit f4c6195).** "
          "The forecasts are the frozen Gulf forward-in-time forecasts of G12, regenerated with full quantiles and "
          "checked equal to the locked scores (12,027 cells, differences below 1e-14). Their accuracy had already "
          "been seen. This is a scenario about decisions, not a confirmatory result and not a measured saving.", "",
          "**Rule (fixed in advance).** Each week, for the target week two weeks after issue: roster surge capacity "
          "if the forecast gives at least a 30% chance (the playbook's `p_act`) that positivity passes the playbook "
          "tier (flu 15%, RSV 10%). A *missed* week is a surge week with no roster; a *wasted* week is a roster "
          "with no surge. The same rule is applied to every forecaster.", "",
          "## Headline (Gulf: Oman, Qatar, Saudi Arabia; playbook thresholds; p* = 0.30; +2 weeks after issue)", "",
          "| Pathogen | Country-seasons | Forecaster | Missed | Wasted | Mismatch weeks | Per season |", "|---|---|---|---|---|---|---|"]
    for ser, name in [("flu", "Influenza"), ("rsv", "RSV")]:
        r = R[f"GCC|{ser}|playbook|p30|h2"]
        n = r["n_country_seasons"]
        for m in ["NABD", "past-season-pattern", "persistence", "never-roster", "always-roster"]:
            t = r["totals"][m]
            md.append(f"| {name} | {n} | {LAB.get(m, m)} | {t['missed']} | {t['wasted']} | {t['mismatch']} | "
                      f"{t['mismatch']/n:.1f} |")
    f, v = R["GCC|flu|playbook|p30|h2"], R["GCC|rsv|playbook|p30|h2"]
    md += ["", "- **Influenza, NABD vs past-season pattern:** " + line(f, "past-season-pattern") + ". Almost all "
           "of the gain is fewer wasted surge weeks.",
           "- **Influenza, NABD vs last week:** " + line(f, "persistence") + ". **No advantage over simply "
           "carrying last week forward** under this rule.",
           "- **RSV, NABD vs past-season pattern:** " + line(v, "past-season-pattern") + ". The interval includes "
           "zero, and **NABD missed more RSV surge weeks than the pattern did** "
           f"({v['totals']['NABD']['missed']} vs {v['totals']['past-season-pattern']['missed']}); it wasted fewer "
           f"({v['totals']['NABD']['wasted']} vs {v['totals']['past-season-pattern']['wasted']}).",
           "- **RSV, NABD vs last week:** " + line(v, "persistence") + ".", "",
           "## Where NABD loses or ties (playbook thresholds, +2 weeks)", ""]
    s2 = S[(S.horizon == 2) & S.location.isin(["OMN", "QAT", "SAU"])]
    p = s2.pivot_table(index=["target", "location", "season"], columns="model", values="mismatch")
    for c, lab in [("past-season-pattern", "past-season pattern"), ("persistence", "last week")]:
        bad = p[p["NABD"] >= p[c]]
        items = [f"{i[1]} {i[2]}/{str(i[2]+1)[2:]} {'flu' if 'flu' in i[0] else 'RSV'} "
                 f"({int(r_['NABD'])} vs {int(r_[c])})" for i, r_ in bad.iterrows()]
        md.append(f"- Not better than {lab}: " + ("; ".join(items) if items else "none") + ".")
    md += ["- Saudi Arabia RSV 2024/25 had no week above 10%, so every forecaster scored zero mismatches there.", "",
           "## Sensitivity (declared; never the headline)", "",
           "| Setting | Flu: NABD minus pattern (95% CI) | Flu: NABD minus last week | RSV: NABD minus pattern | RSV: NABD minus last week |",
           "|---|---|---|---|---|"]

    def cell(key, c):
        d = R[key][f"NABD_minus_{c}_mismatch"]
        return f"{d['diff_per_season']:+.2f} ({d['ci95'][0]:+.1f} to {d['ci95'][1]:+.1f})"
    for lab, kind, p_, h in [("Headline", "playbook", 30, 2), ("p* = 0.20", "playbook", 20, 2),
                             ("p* = 0.50", "playbook", 50, 2), ("Country-relative threshold (own 75th percentile)",
                                                               "country_q75", 30, 2),
                             ("Nowcast week", "playbook", 30, 0), ("+1 week", "playbook", 30, 1),
                             ("+3 weeks", "playbook", 30, 3)]:
        md.append(f"| {lab} | " + " | ".join(cell(f"GCC|{ser}|{kind}|p{p_}|h{h}", c) for ser in ["flu", "rsv"]
                                             for c in ["past-season-pattern", "persistence"]) + " |")
    md += ["", "## UAE folds (POST HOC, n = 2 seasons, descriptive only)", ""]
    for ser in ["flu", "rsv"]:
        t = R[f"UAE_posthoc_n2|{ser}|playbook|p30|h2"]["totals"]
        md.append(f"- {ser.upper() if ser == 'rsv' else 'Influenza'}: mismatch weeks over two seasons: NABD "
                  f"{t['NABD']['mismatch']}, past-season pattern {t['past-season-pattern']['mismatch']}, last week "
                  f"{t['persistence']['mismatch']} (NABD missed {t['NABD']['missed']}, last week missed "
                  f"{t['persistence']['missed']}).")
    md += ["- On the UAE's two folds NABD **missed far more surge weeks than last week did** and wasted fewer. Two "
           "seasons cannot support a claim either way.", ""]
    a = s.get("aed_scenario_rsv_tawam_sized_unit")
    if a:
        md += ["## AED scenario for a Tawam-sized paediatric unit (RSV only; SCENARIO, not a saving)", "",
               "AED a season = mismatch weeks avoided (NABD vs past-season pattern, RSV) x mis-planned bed-days per "
               "mismatch week x AED 2,057 per bed-day.", "",
               "| Case | Weeks avoided a season | Mis-planned bed-days per mismatch week | Bed-days a season | AED a season |",
               "|---|---|---|---|---|"]
        for c in ["low", "central", "high"]:
            b = a["by_case"][c]
            md.append(f"| {c} | {a['mismatch_weeks_avoided_per_season'][c]:+.1f} | "
                      f"{b['misplanned_bed_days_per_mismatch_week']} | {b['bed_days_per_season']:,} | "
                      f"{b['aed_per_season']:,} |")
        md += ["", "**Read this as a range from about zero to about AED 3 million, central about AED 0.4 million.** "
               "The low case is slightly negative because the interval for weeks avoided includes zero.", "",
               "Assumptions, all visible:",
               "- RSV bed-days a year 1,160 / 1,970 / 3,822 (Tawam study 2,189 admissions over five years; length "
               "of stay 4.0 / 4.5 / 5.8 days).",
               "- Share of bed-days in surge weeks 0.7 / 0.8 / 0.9 (ASSUMPTION).",
               f"- Surge weeks a season 14 / 10.75 / 7: UAE sentinel weeks with RSV above 10% in 2022/23–2025/26 "
               f"({a['inputs']['uae_rsv_weeks_over_10pct_by_season']}).",
               "- AED 2,057 a bed-day = US$560 (Dubai claims median US$2,241 over about 4 days) x 3.6725.",
               "- Gulf-country mismatch rates transfer to an Abu Dhabi hospital (ASSUMPTION).",
               "- Positivity tiers map to bed pressure; one mismatch week mis-plans one week of the surge "
               "increment (ASSUMPTION).",
               "- The bed-day figure is the scale of resource mis-planned. **It is not cash saved.**",
               "- No influenza AED figure: there is no sourced paediatric flu bed-day cost.", ""]
    md += ["## Files", "", "- `forecasts/*.csv.gz`: the frozen forecasts with all 23 quantiles (contract format).",
           "- `truth.csv`, `thresholds_country_q75.csv`.",
           "- `tables/weekly_decisions.csv.gz`: every weekly decision. `tables/per_season_*.csv`: per country-season.",
           "- Reproduce: `python3 -m replay.regen && python3 -m replay.run && python3 -m replay.report`. Another "
           "model: `python3 -m replay.run --extra its_forecasts.csv` (contract format).", ""]
    (OUT / "SUMMARY.md").write_text("\n".join(md))
    figure(R)


def figure(R):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=False)
    for ax, (ser, name) in zip(axes, [("flu", "Influenza (12 country-seasons)"), ("rsv", "RSV (10 country-seasons)")]):
        r = R[f"GCC|{ser}|playbook|p30|h2"]
        n = r["n_country_seasons"]
        ms = ["NABD", "persistence", "past-season-pattern"]
        missed = [r["totals"][m]["missed"] / n for m in ms]
        wasted = [r["totals"][m]["wasted"] / n for m in ms]
        x = range(len(ms))
        ax.bar(x, wasted, color="#2b7a78", label="Wasted surge weeks (rostered, no surge)")
        ax.bar(x, missed, bottom=wasted, color="#c0392b", label="Missed surge weeks (surge, no roster)")
        for i, (a, b) in enumerate(zip(wasted, missed)):
            ax.text(i, a + b + 0.25, f"{a + b:.1f}", ha="center", fontsize=13, fontweight="bold")
        ax.set_xticks(list(x))
        ax.set_xticklabels(["NABD", "Last week", "Past-season\npattern"], fontsize=12)
        ax.set_title(name, fontsize=13)
        ax.set_ylabel("Mismatch weeks per season", fontsize=11)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle("Roster-rule replay on out-of-sample Gulf seasons (post hoc scenario; rule fixed in advance)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "replay_mismatch_weeks.png", dpi=150)


if __name__ == "__main__":
    main()

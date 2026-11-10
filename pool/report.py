"""Writes results/pool/SUMMARY.md from summary.json and the tables (wording only; computes no score)."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "pool"


def f(r):
    return "n/a" if not r else f"{r['rel_wis']:.3f} (95% CI {r['ci95'][0]:.3f}–{r['ci95'][1]:.3f}; {r['unit_wins']} countries better)"


def main():
    s = json.loads((OUT / "summary.json").read_text())
    inc = pd.read_csv(OUT / "tables" / "inclusion.csv")
    L = ["# Borrowed strength: NABD-Pool on held-out countries (confirmatory)", "",
         f"_{s['label']}._", "",
         "Plan: `docs/PREREG-POOL.md`. Lock #1 (plan and country lists) was made before any new data were downloaded; "
         "lock #2 (model, configuration, development data) was made before any held-out row was extracted. "
         "Both locks are self-attested in local git until externally timestamped. Scored once.", ""]
    if "PRIMARY_flu_pool_vs_local_v1" not in s:
        L += [f"**Primary: {s['PRIMARY_verdict']}**"]
        (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")
        return
    p, sec = s["PRIMARY_flu_pool_vs_local_v1"], s["secondary"]
    L += [f"## Primary (influenza): **{s['PRIMARY_verdict']}**",
          f"- Pooled model vs each country's own-record model (local v1), relative WIS: **{f(p)}**. Below 1 means the pooled model had less error.",
          f"- Held-out countries listed: {len(inc)}; included by the pre-set data rules: **{s['n_included']}** ({', '.join(s['included_countries'])}).",
          f"- Chosen model (development countries only): `{s['chosen_model']}`.", "",
          "## Key secondaries",
          f"1. Short-history stratum (country-seasons with ≤ 2 own earlier seasons): {f(sec.get('short_history_pool_vs_v1'))}.",
          f"2. Simulated short record (every country cut to its last 2 seasons): {f((s.get('simulated_short_record') or {}).get('pool_vs_NABD-UAE-v1'))}.",
          f"3. Pooled vs persistence: {f(sec.get('pool_vs_persistence'))}. Pooled vs past-season pattern: {f(sec.get('pool_vs_seasonal-analog'))}.",
          f"   For reference, local v1 vs persistence on the same cells: {f(sec.get('v1_vs_persistence'))}.", "",
          "## Other secondaries",
          f"- EMRO only: {f(sec.get('EMRO_pool_vs_v1'))}. Other regions: {f(sec.get('other_regions_pool_vs_v1'))}.",
          f"- Geometric mean of per-country ratios: {p['mean_log_ratio']:.3f}. Country-seasons where pooled beat local: {sec['country_season_wins_pool_vs_v1']}.",
          f"- By horizon (1–4 data weeks), pooled vs local: {sec['by_horizon_pool_vs_v1']}.",
          f"- Coverage (50% / 95% intervals): " + "; ".join(f"{m}: {v['cov50']:.2f} / {v['cov95']:.2f}" for m, v in sec["coverage"].items()) + "."]
    r = s.get("rsv") or {}
    if r.get("included"):
        L += [f"- RSV (secondary; {len(r['included'])} countries: {', '.join(r['included'])}): pooled vs local {f(r.get('pool_vs_NABD-UAE-v1'))}; vs persistence {f(r.get('pool_vs_persistence'))}."]
    else:
        L += [f"- RSV: {r.get('note') or r.get('error') or 'not assessable'}."]
    per = pd.read_csv(OUT / "tables" / "per_country_flu.csv")
    L += ["", "## Every included country (influenza, mean WIS in percentage points)", "",
          "| Country | Pooled | Local v1 | Persistence | Past-season pattern | Pooled / local | Pooled / persistence |", "|---|---|---|---|---|---|---|"]
    for _, x in per.sort_values("pool/v1").iterrows():
        L.append(f"| {x.country} | {x['NABD-Pool']:.2f} | {x['NABD-UAE-v1']:.2f} | {x['persistence']:.2f} | {x['seasonal-analog']:.2f} | {x['pool/v1']:.2f} | {x['pool/persistence']:.2f} |")
    L += ["", "## Excluded held-out countries (pre-set rules, applied mechanically)", ""]
    for _, x in inc[~inc.included].iterrows():
        L.append(f"- {x.country}: {x.reason}")
    nc = OUT / "dev" / "per_country_chosen.csv"
    if nc.exists():
        d = pd.read_csv(nc).set_index("country")
        L += ["", "## Already-seen countries (NON-CONFIRMATORY)",
              "These countries were in the development set and their data had been seen before this test. Figures come "
              "from development cross-fitting, with the country left out of the pooled fit. They are not evidence for H1.", ""]
        for c in ("ARE", "OMN", "QAT", "SAU"):
            if c in d.index:
                L.append(f"- {c}: pooled / local v1 = {d.loc[c, 'pool/v1']:.2f}; pooled / persistence = {d.loc[c, 'pool/persistence']:.2f}")
    L += ["", "## Limits", "- Finalised (revised) FluNet data; no real-time versions exist.",
          "- Positivity, not hospital load. The season boundary (ISO week 27) is a northern-hemisphere convention applied to all countries.",
          "- Deviation P1 (relaxed rule for the pooled model's training rows) was declared before any pooled fit; see `docs/DEVIATIONS.md`."]
    (OUT / "SUMMARY.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()

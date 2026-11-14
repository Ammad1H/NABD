"""Build the static NABD web front-end.

  python -m web.build            # writes web/dist/{index.html, styles.css, app.js, data.js}
  python -m http.server 8600 --directory web/dist     # or just open web/dist/index.html

Every number on the page is read here from results/, ledger/ and data/raw/ through the same loaders the
Streamlit app uses (app.data_io, app.cardcheck). Nothing is typed by hand in the page. The page is static,
so it can be hosted anywhere; the approval log in it is a browser-session demo, the audited path is the
Streamlit app / API.
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import cardcheck, data_io  # noqa: E402
from playbook.validate import load_playbook  # noqa: E402

SRC, DIST = ROOT / "web" / "src", ROOT / "web" / "dist"
RES, LEDGER = ROOT / "results", ROOT / "ledger"
QSHOW = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]
HEADLINE, POOL, PERS = "NABD-UAE-v1", "NABD-Pool", "persistence"
COUNTRY = {  # ISO3 -> (English, Arabic)
    "ARE": ("United Arab Emirates", "الإمارات"), "OMN": ("Oman", "عُمان"), "QAT": ("Qatar", "قطر"),
    "SAU": ("Saudi Arabia", "السعودية"), "BGD": ("Bangladesh", "بنغلاديش"), "CRI": ("Costa Rica", "كوستاريكا"),
    "ECU": ("Ecuador", "الإكوادور"), "EGY": ("Egypt", "مصر"), "ETH": ("Ethiopia", "إثيوبيا"), "GHA": ("Ghana", "غانا"),
    "IDN": ("Indonesia", "إندونيسيا"), "IRN": ("Iran", "إيران"), "KEN": ("Kenya", "كينيا"), "LKA": ("Sri Lanka", "سريلانكا"),
    "MYS": ("Malaysia", "ماليزيا"), "NPL": ("Nepal", "نيبال"), "PAK": ("Pakistan", "باكستان"), "PER": ("Peru", "بيرو"),
    "PHL": ("Philippines", "الفلبين"), "PRY": ("Paraguay", "باراغواي"), "SEN": ("Senegal", "السنغال"),
    "VNM": ("Vietnam", "فيتنام"),
}


def _j(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def _r(x, n=2):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def observed_block(obs: pd.DataFrame) -> dict:
    o = obs.dropna(subset=["specimens"]).copy()
    iso = [pd.Timestamp(d).isocalendar() for d in o.week_end]
    return dict(week_end=[str(pd.Timestamp(d).date()) for d in o.week_end], iso_week=[int(c[1]) for c in iso],
                season=[int(c[0] if c[1] >= 27 else c[0] - 1) for c in iso],
                flu=[_r(v, 2) for v in o.flu], rsv=[_r(v, 2) for v in o.rsv], specimens=[int(v) for v in o.specimens])


def fan(fc: pd.DataFrame, target: str) -> list[dict]:
    g = fc[fc.target == target]
    out = []
    for te, x in g.groupby("target_end_date"):
        qs = {round(float(q), 3): float(v) for q, v in zip(x.q, x.value)}
        out.append(dict(te=str(te), q={str(q): _r(qs[q], 2) for q in QSHOW}))
    return sorted(out, key=lambda r: r["te"])


def card_block(pb: dict, fc: pd.DataFrame, obs: pd.DataFrame, issue: dt.date, col: str) -> dict:
    target = data_io.UAE_TARGETS[col]
    res = cardcheck.build_card(pb, target, "ARE", fc[fc.target == target], obs[col], issue)
    out = dict(renderable=bool(res.renderable), problems=list(res.problems), last=_r(res.last_value, 1),
               prev=_r(res.prev_value, 1), level=float(res.level), p_act=float(res.p_act), trend=res.trend,
               trend_ratio=_r(res.trend_ratio, 2), observed_trend=res.observed_trend,
               trend_txt={k: cardcheck.TREND_TXT[res.trend][k] for k in ("en", "ar")},
               obs_trend_txt={k: cardcheck.TREND_TXT[res.observed_trend][k] for k in ("en", "ar")},
               sentence={k: cardcheck.card_sentence(res, k, data_io.display_horizon(res.level_row.target_end_date, issue, None, k))
                         for k in ("en", "ar")},
               max_p={f"{k:g}": _r(v, 3) for k, v in res.max_p.items()}, exceed=[])
    if res.exceed is not None:
        for i, d in enumerate(res.exceed_dates):
            out["exceed"].append(dict(
                te=str(d), week={k: data_io.week_ending_label(d, k) for k in ("en", "ar")},
                horizon={k: data_io.horizon_label(d, issue, k) for k in ("en", "ar")},
                p={f"{T:g}": cardcheck.fmt_p(float(res.exceed[T].iloc[i])) for T in res.exceed.columns},
                praw={f"{T:g}": _r(float(res.exceed[T].iloc[i]), 3) for T in res.exceed.columns}))
    if res.band is not None:
        b = res.band
        out["band"] = dict(id=b["id"], tier=int(b["tier"]), label={k: cardcheck.band_label(b, k) for k in ("en", "ar")},
                           actions={r: b["actions"][r] for r in pb["roles"] if r in b["actions"]})
    return out


def current_round(obs: pd.DataFrame, pb: dict) -> dict:
    fc, pers, meta, demo = data_io.load_uae_forecasts(obs)
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    models = {HEADLINE: fc, PERS: pers}
    pfc, _, pmeta, _ = data_io.load_uae_forecasts(obs, model=POOL)
    if pmeta.get("model") == POOL and pmeta.get("round_stamp") == meta.get("round_stamp"):
        models[POOL] = pfc
    out = dict(demo=bool(demo), headline=meta.get("model"), issue_date=issue.isoformat(), round_stamp=meta.get("round_stamp"),
               round_file=meta.get("round_file"), sha256=meta.get("sha256"), forecasts={}, cards={})
    for name, f in models.items():
        if f is None:
            continue
        out["forecasts"][name] = {c: fan(f, data_io.UAE_TARGETS[c]) for c in ("rsv", "flu")}
        if name != PERS:
            out["cards"][name] = {c: card_block(pb, f, obs, issue, c) for c in ("rsv", "flu")}
    return out


def evidence() -> dict:
    ev = {}
    psum, ptabs, _ = data_io.load_pool()
    ph = data_io.pool_headline(psum)
    if ph:
        pc = ptabs["per_country_flu"]
        inc = ptabs.get("inclusion")
        ev["pool"] = dict(
            verdict=ph["verdict"], primary=ph["primary"], short=ph["short"], vs_persistence=ph["vs_persistence"],
            vs_pattern=ph["vs_pattern"], local_vs_persistence=ph["local_vs_persistence"], n=ph["n"],
            simulated_short=psum["simulated_short_record"]["pool_vs_NABD-UAE-v1"],
            by_horizon=psum["secondary"]["by_horizon_pool_vs_v1"], coverage=psum["secondary"]["coverage"],
            n_named=int(len(inc)) if inc is not None else None,
            per_country=[dict(c=r.country, pool=_r(r["NABD-Pool"]), local=_r(r["NABD-UAE-v1"]), pers=_r(r["persistence"]),
                              ratio=_r(r["pool/v1"], 3), ratio_pers=_r(r["pool/persistence"], 3), n=int(r.n_cells))
                         for _, r in pc.sort_values("pool/v1").iterrows()],
            excluded=[] if inc is None else [dict(c=r.country, reason=str(r.reason)) for _, r in inc[~inc.included].iterrows()])
    fm = _j(RES / "fm" / "summary.json")
    if fm:
        R = fm["results"]
        ev["fm"] = dict(model=fm["model"], revision=fm["weights_revision"][:12], n_cells=fm["n_cells_common"],
                        fm_vs_pool=R["Chronos-2 (zero-shot)"]["vs_NABD-Pool"], fm_vs_local=R["Chronos-2 (zero-shot)"]["vs_NABD-UAE-v1"],
                        fm_vs_persistence=R["Chronos-2 (zero-shot)"]["vs_persistence"], ens_vs_pool=R["Pool+FM"]["vs_NABD-Pool"],
                        mean_wis={k: fm["mean_wis"][k] for k in ["NABD-Pool", "Chronos-2 (zero-shot)", "Pool+FM", "NABD-UAE-v1",
                                                                 "persistence", "seasonal-analog"]})
    gcc, _, _ = data_io.load_gcc()
    if isinstance(gcc, dict):
        r = gcc["results"]
        ev["gcc"] = dict(verdict=r.get("PRIMARY_verdict"), countries=gcc.get("included_countries"),
                         vs_persistence=r["PRIMARY_flu_v1_vs_persistence"], vs_pattern=r["flu_NABD-UAE-v1_vs_seasonal-analog"])
    us = data_io.load_us_summary()
    if us:
        league, _ = data_io.load_league()
        lt = league.get("league_table")
        ranks = []
        if lt is not None:
            nab = lt[lt.model.astype(str).str.startswith("NABD") & (lt.variant == "excluding ensembles")]
            ranks = [dict(season=r.season, rank=int(r.rank), n=int(r.n_models)) for r in nab.sort_values("season").itertuples()]
        ev["us"] = dict(verdict=us.get("primary_verdict"), rel_wis=_r(us["primary"]["rel_wis"], 2),
                        ci95=[_r(v, 2) for v in us["primary"]["ci95"]], margin=us["primary"]["margin"], ranks=ranks)
    fit = data_io.load_uae_forward_in_time()
    if fit:
        ev["uae"] = {k: dict(rel_wis=v["rel_wis"], ci95=v["ci95_date_cluster"]) for k, v in fit.items()}
    rp = data_io.replay_headline(data_io.load_replay()[0], "flu")
    if rp:
        ev["replay_gulf"] = dict(n=rp["n"], vs_pattern=rp["vs_pattern"], vs_last_week=rp["vs_last_week"])
    rsum = data_io.load_replay()[0] or {}
    if rsum.get("aed_scenario_rsv_tawam_sized_unit"):
        ev["aed"] = rsum["aed_scenario_rsv_tawam_sized_unit"]["by_case"]
    prh = data_io.pool_replay_headline(data_io.load_pool_replay()[0])
    if prh:
        ev["replay_pool"] = prh
    return ev


def _unit(g: pd.DataFrame, source: str, names: dict) -> dict:
    g = g.sort_values("target_end_date")
    first = g[g.model == g.model.iloc[0]]
    u = dict(source=source, location=str(first.location.iloc[0]), series="rsv" if "rsv" in first.target.iloc[0] else "flu",
             season=int(first.season.iloc[0]), T=_r(first["T"].iloc[0], 1), te=list(first.target_end_date.astype(str)),
             obs=[_r(v, 1) for v in first.obs], models={})
    for m, x in g.groupby("model"):
        if m not in names:
            continue
        x = x.set_index("target_end_date").reindex(first.target_end_date)
        u["models"][names[m]] = dict(med=[_r(v, 1) for v in x["median"]], lo=[_r(v, 1) for v in x.q10],
                                     hi=[_r(v, 1) for v in x.q90], p=[_r(v, 2) for v in x.p_exceed],
                                     roster=[int(bool(v)) for v in x.roster])
    return u


def replay_block() -> list[dict]:
    units = []
    f = RES / "replay" / "tables" / "weekly_decisions.csv.gz"
    if f.exists():
        W = pd.read_csv(f)
        W = W[(W.threshold_kind == "playbook") & (W.horizon == 2)]
        names = {"NABD": "local", "past-season-pattern": "pattern", "persistence": "last"}
        for _, g in W[W.location.isin(["OMN", "QAT", "SAU"])].groupby(["location", "target", "season"]):
            units.append(_unit(g, "gulf", names))
    f = RES / "replay" / "pool" / "weekly_decisions.csv.gz"
    if f.exists():
        W = pd.read_csv(f)
        W = W[W.horizon == 2]
        names = {"NABD-Pool": "pool", "NABD-UAE-v1": "local", "seasonal-analog": "pattern", "persistence": "last"}
        for _, g in W.groupby(["location", "target", "season"]):
            units.append(_unit(g, "heldout", names))
    return units


def ledger_block() -> dict:
    rounds, files = [], {}
    for m in sorted(LEDGER.glob("*.meta.json")):
        meta = json.loads(m.read_text())
        csv = m.with_name(m.name.replace(".meta.json", ".csv"))
        dtw = meta.get("data_through_week")
        rounds.append(dict(round=meta.get("round"), issued_utc=meta.get("issued_utc"), model=meta.get("model"), file=csv.name,
                           sha256=meta.get("sha256"), data_through=max(dtw.values()) if isinstance(dtw, dict) else str(dtw)))
        files[csv.name] = csv.read_text()
    manifests = []
    for d in sorted((LEDGER / "rounds").glob("*")):
        mj = _j(d / "MANIFEST.json")
        if mj:
            manifests.append(dict(round=d.name.split("_")[-1], dir=d.name, merkle_root=mj["merkle_root"], n_files=len(mj["files"])))
    scores = LEDGER / "scores.csv"
    n_scored = 0
    if scores.exists():
        try:
            sc = pd.read_csv(scores)
            n_scored = int(sc["realised"].notna().sum()) if "realised" in sc else 0
        except Exception:  # noqa: BLE001
            n_scored = 0
    live = _j(LEDGER / "live_test.json") or {}
    lock = _j(ROOT / "docs" / "LOCK-LIVE.json") or {}
    return dict(rounds=rounds, files=files, manifests=manifests, n_scored=n_scored,
                live_test=dict(rounds=live.get("rounds_issued", []), scored=live.get("scored_cells_per_model", 0),
                               status=live.get("status"), lock_root=(lock.get("digest") or {}).get("root"),
                               locked_utc=lock.get("locked_utc_self_attested"), final_from="2027-04-15",
                               last_target="2027-03-28"))


def build() -> dict:
    obs = data_io.load_uae_observed()
    pb = load_playbook()
    data = dict(
        built_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        freshness=data_io.freshness(obs), observed=observed_block(obs), current=current_round(obs, pb),
        playbook=dict(version=pb["version"], status=pb.get("status"), roles=pb["roles"], reason_codes=pb["reason_codes"],
                      p_act=pb["rules"]["decision"]["p_act"]),
        evidence=evidence(), replay=replay_block(), ledger=ledger_block(), countries={k: dict(en=v[0], ar=v[1]) for k, v in COUNTRY.items()},
    )
    DIST.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S")
    for f in SRC.glob("*"):
        if f.is_file():
            shutil.copy2(f, DIST / f.name)
    html = (SRC / "index.html").read_text(encoding="utf-8")          # cache-busting so a rebuilt page is never stale
    for name in ("styles.css", "data.js", "app.js"):
        html = html.replace(f'"{name}"', f'"{name}?v={stamp}"')
    (DIST / "index.html").write_text(html, encoding="utf-8")
    (DIST / "data.js").write_text("window.NABD = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                                  encoding="utf-8")
    return data


if __name__ == "__main__":
    d = build()
    size = (DIST / "data.js").stat().st_size
    print(f"built web/dist ({size / 1024:.0f} kB data): round {d['current']['round_stamp']}, headline {d['current']['headline']}, "
          f"{len(d['replay'])} replay seasons, {len(d['ledger']['rounds'])} ledger files")

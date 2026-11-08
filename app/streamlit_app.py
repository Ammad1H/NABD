"""NABD Streamlit app. Run:  streamlit run app/streamlit_app.py

Reads only interface-contract paths (docs/BUILD-SPEC.md v1.1–v1.4). Rules:
- Results panels (US proof, alerts, GCC, feed removal, explanations) show "not yet computed" when
  their file is missing. They never show demo numbers.
- Only the weekly card can fall back to DEMO forecasts (when no ledger round or retrospective file
  exists), and then a DEMO DATA banner is shown.
- Every weekly card passes the consistency gate in app/cardcheck.py (G14) before its action renders.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import altair as alt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app import audit, cardcheck, data_io  # noqa: E402
from app.i18n import t  # noqa: E402
from app.workforce import secure_aggregate, synthetic_employers  # noqa: E402
from playbook.validate import load_playbook  # noqa: E402

TEAL, SLATE, SAND, ROSE, GREEN = "#1f7a8c", "#334155", "#e2d4b7", "#b4505b", "#2e7d5b"

st.set_page_config(page_title="NABD", page_icon="🫀", layout="wide")

lang = st.sidebar.radio("Language / اللغة", ["en", "ar"], format_func=lambda x: "English" if x == "en" else "العربية")
rtl = lang == "ar"
st.markdown(f"""
<style>
  .stApp {{ background: #f7f9fb; }}
  h1, h2, h3 {{ color: {SLATE}; }}
  .nabd-banner {{ background:#fff4e5; border-left:6px solid #e0a100; padding:.6rem 1rem; border-radius:4px; margin-bottom:.8rem; }}
  .nabd-sim {{ background:#fde8ea; border:2px dashed {ROSE}; color:{ROSE}; font-weight:700; text-align:center;
               padding:.4rem; letter-spacing:.3em; border-radius:4px; }}
  .nabd-badge-ok {{ background:#e6f4f1; color:{TEAL}; padding:.25rem .6rem; border-radius:12px; font-weight:600; }}
  .nabd-badge-warn {{ background:#fde8ea; color:{ROSE}; padding:.25rem .6rem; border-radius:12px; font-weight:600; }}
  .nabd-card {{ background:white; border:1px solid #e5e7eb; border-radius:8px; padding:1rem; }}
  .nabd-verdict-bad {{ background:#fde8ea; border:2px solid {ROSE}; color:#7a1f2b; border-radius:8px; padding:1rem; }}
  .nabd-verdict-good {{ background:#e6f4f1; border:2px solid {GREEN}; color:#1d4d39; border-radius:8px; padding:1rem; }}
  .nabd-pill {{ display:inline-block; background:{ROSE}; color:white; font-weight:800; padding:.2rem .7rem;
                border-radius:6px; letter-spacing:.08em; margin-right:.5rem; }}
  .nabd-pill-good {{ background:{GREEN}; }}
  .nabd-explore {{ background:#f1f5f9; border-left:6px solid #64748b; padding:.5rem 1rem; border-radius:4px; }}
  {"section.main .block-container, .stMarkdown, .stRadio, .stSelectbox, .stTextInput {direction: rtl; text-align: right;}" if rtl else ""}
</style>""", unsafe_allow_html=True)

PAGES = ["nav_card", "nav_alerts", "nav_us", "nav_gcc", "nav_ledger", "nav_ablation", "nav_workforce", "nav_about"]
page = st.sidebar.radio("Page", PAGES, format_func=lambda k: t(k, lang))
st.sidebar.caption("NABD prototype · Future Health Digital Innovation Challenge 2026 · Statement 06")

st.title(t("title", lang))
st.caption(t("subtitle", lang))


def demo_banner():
    st.markdown(f'<div class="nabd-banner"><b>⚠ {t("demo_banner", lang)}</b></div>', unsafe_allow_html=True)


def not_computed(what: str, path: str):
    st.info(f"**{t('not_computed', lang)}:** {what}  \nExpected file: `{path}`")


def sim_watermark():
    st.markdown(f'<div class="nabd-sim">{t("simulated", lang)} · {t("simulated", "en" if rtl else "ar")}</div>',
                unsafe_allow_html=True)


def exploratory_note():
    st.markdown(f'<div class="nabd-explore"><b>{t("exploratory", lang)}</b></div>', unsafe_allow_html=True)


@st.cache_data(ttl=300)
def _observed():
    return data_io.load_uae_observed()


observed = _observed()


# ------------------------------------------------------------------ helpers
def fan_frame(fc: pd.DataFrame, target: str) -> pd.DataFrame:
    g = fc[fc.target == target]
    piv = g.pivot_table(index="target_end_date", columns="q", values="value").reset_index()
    piv.columns = [c if isinstance(c, str) else round(float(c), 3) for c in piv.columns]
    return piv


def _qcols(df: pd.DataFrame) -> pd.DataFrame:
    """Vega-Lite treats dots in field names as nested access, so rename 0.025 -> q025 etc."""
    return df.rename(columns={c: f"q{int(round(c * 1000)):03d}" for c in df.columns if isinstance(c, float)})


def fan_chart(col: str, target: str, fc: pd.DataFrame, pers: pd.DataFrame, issue: dt.date):
    hist = observed[["week_end", col]].dropna().tail(16).rename(columns={col: "value"})
    hist["week_end"] = pd.to_datetime(hist.week_end)
    f = _qcols(fan_frame(fc, target))
    f["target_end_date"] = pd.to_datetime(f.target_end_date)
    f["horizon"] = [data_io.horizon_label(d.date(), issue) for d in f.target_end_date]
    p = _qcols(fan_frame(pers, target))
    p["target_end_date"] = pd.to_datetime(p.target_end_date)
    base = alt.Chart(f).encode(x=alt.X("target_end_date:T", title="Week ending"))
    band95 = base.mark_area(opacity=0.18, color=TEAL).encode(y=alt.Y("q025:Q", title="%"), y2="q975:Q")
    band80 = base.mark_area(opacity=0.35, color=TEAL).encode(y="q100:Q", y2="q900:Q")
    med = base.mark_line(color=TEAL, strokeWidth=3, point=True).encode(
        y="q500:Q", tooltip=[alt.Tooltip("target_end_date:T", title="week end"), "horizon:N",
                             alt.Tooltip("q100:Q", format=".1f", title="10%"), alt.Tooltip("q500:Q", format=".1f", title="median"),
                             alt.Tooltip("q900:Q", format=".1f", title="90%")])
    pers_line = alt.Chart(p).mark_line(color=SLATE, strokeDash=[6, 4], point=True).encode(
        x="target_end_date:T", y="q500:Q", tooltip=[alt.Tooltip("q500:Q", format=".1f", title="persistence median")])
    h = alt.Chart(hist).mark_line(color=SLATE, point=alt.OverlayMarkDef(size=18)).encode(
        x="week_end:T", y="value:Q", tooltip=[alt.Tooltip("week_end:T"), alt.Tooltip("value:Q", format=".1f")])
    issue_rule = alt.Chart(pd.DataFrame({"d": [pd.Timestamp(issue)]})).mark_rule(color=ROSE, strokeDash=[2, 2]).encode(x="d:T")
    return (band95 + band80 + h + pers_line + med + issue_rule).properties(height=300)


def context_lines(col: str) -> list[str]:
    s = observed.dropna(subset=[col])
    last3 = s[col].tail(3).round(1).tolist()
    spec = s.specimens.tail(2).tolist()
    spec_chg = 100 * (spec[-1] - spec[0]) / spec[0] if spec[0] else 0
    hist_peak = (observed.assign(season=np.where(observed.ISO_WEEK >= 27, observed.ISO_YEAR, observed.ISO_YEAR - 1))
                 .dropna(subset=[col]).groupby("season").apply(lambda g: int(g.loc[g[col].idxmax(), "ISO_WEEK"]),
                                                              include_groups=False))
    hist_peak = hist_peak.iloc[:-1]  # drop the current, incomplete season
    return [f"Last 3 published weeks: {' → '.join(map(str, last3))}%",
            f"Testing volume change (last week): {spec_chg:+.0f}%" + (" ⚠ >30%: interpret positivity with care" if abs(spec_chg) > 30 else ""),
            f"Peak week (ISO) in previous seasons: {', '.join(map(str, hist_peak.tolist()[-4:]))}"]


def explain_panel(col: str, ex: pd.DataFrame | None, ex_date: str | None, issue: dt.date, default_wk: float):
    st.markdown(f"**{t('why', lang)}**")
    if ex is None or ex.empty:
        not_computed("per-signal contributions for this forecast (UAE v2, linear on the logit scale)",
                     "results/uae/explain/<issue_date>_<target>.csv")
        return
    if ex_date != issue.isoformat():
        st.caption(f"Explanation file is for issue date {ex_date}, not this card's issue date {issue.isoformat()}.")
    ex = ex.copy()
    horizons = list(pd.unique(ex["horizon"]))
    # Default to the horizon matching the card's level horizon when the file stores weeks; else the first.
    default = 0
    for i, h in enumerate(horizons):
        try:
            if float(h) == default_wk or (float(h) == 0 and default == 0):
                default = i
        except (TypeError, ValueError):
            continue
    h = st.selectbox("Horizon", horizons, index=default, key=f"exh_{col}")
    g = ex[ex["horizon"] == h].copy()
    g["contribution"] = pd.to_numeric(g["contribution"], errors="coerce")
    g = g.dropna(subset=["contribution"])
    g["abs"] = g.contribution.abs()
    g = g.sort_values("abs", ascending=False)
    unit = str(g["unit"].iloc[0]) if "unit" in g.columns and len(g) else ""
    g["direction"] = np.where(g.contribution >= 0, "pushes up", "pushes down")
    ch = alt.Chart(g).mark_bar().encode(
        y=alt.Y("feature:N", sort=list(g.feature), title=None),
        x=alt.X("contribution:Q", title=f"contribution ({unit})" if unit else "contribution"),
        color=alt.Color("direction:N", scale=alt.Scale(domain=["pushes up", "pushes down"], range=[ROSE, TEAL]), legend=None),
        tooltip=["feature", "value", alt.Tooltip("contribution:Q", format="+.3f")]).properties(height=28 * max(len(g), 3))
    st.altair_chart(ch, width="stretch")
    skip = ("intercept", "const", "baseline", "base")
    top = [r for r in g.itertuples() if not str(r.feature).lower().startswith(skip)][:3]
    for r in top:
        verb = "pushed the forecast up" if r.contribution >= 0 else "pushed the forecast down"
        st.markdown(f"- **{r.feature}** (value {r.value}) {verb} by {abs(r.contribution):.2f}{(' ' + unit) if unit else ''}.")
    st.caption("Exact additive contributions of each signal to the model's linear predictor; they sum to the forecast "
               "median on the model scale. They describe the model, not causes.")


# ------------------------------------------------------------------ pages
if page == "nav_card":
    fc, pers, meta, is_demo = data_io.load_uae_forecasts(observed)
    if is_demo:
        demo_banner()
    fr = data_io.freshness(observed)
    issue = dt.date.fromisoformat(str(meta.get("issue_date") or meta.get("reference_date")))
    c1, c2, c3 = st.columns([2, 2, 3])
    c1.metric(t("last_week", lang), fr["last_week"])
    c2.metric(t("lag", lang), f'{fr["lag_days"]} {t("days", lang)}', f'{t("expected", lang)} ~{fr["expected_lag_days"]}', delta_color="off")
    badge = "nabd-badge-warn" if fr["stale"] else "nabd-badge-ok"
    c3.markdown(f'<br><span class="{badge}">{t("freshness", lang)}: {t("stale" if fr["stale"] else "fresh", lang)}</span>'
                f'<br><small>Issued {issue.isoformat()} · model: <b>{meta.get("model")}</b> · source: {meta.get("source")}'
                + (f'<br>round <code>{meta["round_file"]}</code> · SHA-256 <code>{meta["sha256"][:16]}…</code>' if meta.get("round_file") else "")
                + '</small>', unsafe_allow_html=True)

    pb = load_playbook()
    explain, ex_date = data_io.load_uae_explain(issue.isoformat())
    for col in ("rsv", "flu"):
        target = data_io.UAE_TARGETS[col]
        st.subheader(t(col, lang))
        res = cardcheck.build_card(pb, target, "ARE", fc[fc.target == target], observed[col], issue)
        left, right = st.columns([3, 2])
        with left:
            st.altair_chart(fan_chart(col, target, fc, pers, issue), width="stretch")
            st.caption(f"Teal: forecast median with 80% / 95% bands · dashed slate: {t('persistence', lang)} · red rule: issue date")
            f = fan_frame(fc, target)
            pe = fan_frame(pers, target)
            tbl = pd.DataFrame({
                t("horizon", lang): [data_io.horizon_label(d, issue) for d in f.target_end_date],
                "week end": f.target_end_date.astype(str),
                t("median", lang): f[0.5].round(1),
                t("band80", lang): [f"{a:.1f}–{b:.1f}" for a, b in zip(f[0.1], f[0.9])],
                t("persistence_short", lang): f.target_end_date.map(dict(zip(pe.target_end_date, pe[0.5].round(1)))).values,
            })
            st.dataframe(tbl, hide_index=True, width="stretch")
            st.caption(t("horizon_note", lang))
            explain_panel(col, explain.get(col), ex_date, issue, res.level_horizon_wk)
        with right:
            st.markdown(f"**{t('card_facts', lang)}**")
            st.markdown(f'<div class="nabd-card">{cardcheck.card_sentence(res, lang)}'
                        + (f'<br><small>P(above the high-pressure level {res.high_threshold:g}%) at '
                           f'+{res.level_horizon_wk:g} wk: {res.p_high:.0%}</small>' if res.p_high is not None else "")
                        + '</div>', unsafe_allow_html=True)
            st.markdown(f"**{t('action', lang)}**")
            st.caption(f"⚠ {t('illustrative', lang)} · playbook v{pb['version']}")
            if not res.renderable:
                st.error(t("blocked", lang) + "\n\n" + "\n".join(f"- {p}" for p in res.problems))
            else:
                band = res.band
                st.markdown(f'<div class="nabd-card">Tier {band["tier"]} · band <code>{band["id"]}</code> '
                            f'(median {res.level_row[0.5]:.1f}% at +{res.level_horizon_wk:g} wk; forecast path '
                            f'{cardcheck.TREND_TXT[res.trend][lang]}, ratio {res.trend_ratio:.2f})<br><br>'
                            f'<b>{pb["roles"]["hospital_ops"][lang]}:</b> {band["actions"]["hospital_ops"][lang]}<br>'
                            f'<b>{pb["roles"]["adphc_duty"][lang]}:</b> {band["actions"]["adphc_duty"][lang]}</div>',
                            unsafe_allow_html=True)
                st.caption("✓ Card passed the consistency check (band, forecast direction and action agree).")
                with st.form(f"decide_{col}"):
                    role = st.selectbox(t("role", lang), list(pb["roles"]), format_func=lambda r: pb["roles"][r][lang])
                    approver = st.text_input(t("approver", lang))
                    decision = st.radio(t("decision", lang), ["APPROVE", "MODIFY", "DISMISS"], horizontal=True,
                                        format_func=lambda d: t(d.lower(), lang))
                    codes = {rc["code"]: rc[lang] for rc in pb["reason_codes"]}
                    reason = st.selectbox(t("reason", lang), list(codes), format_func=lambda c: codes[c])
                    modified = st.text_input(t("modified", lang))
                    note = st.text_area(t("note", lang), height=60)
                    if st.form_submit_button(t("submit", lang)):
                        try:
                            rec = audit.append_decision(
                                approver=approver, role=role, decision=decision, reason_code=reason, note=note,
                                band_id=band["id"], proposed_action=band["actions"][role]["en"],
                                modified_action=modified if decision == "MODIFY" else None,
                                forecast_ref={"model": meta.get("model"), "reference_date": issue.isoformat(),
                                              "target": target, "target_end_date": str(res.level_row.target_end_date),
                                              "median": round(float(res.level_row[0.5]), 2), "trend": res.trend,
                                              "forecast_key": res.kit.forecast_key, "demo": is_demo},
                                playbook_version=pb["version"], valid_reason_codes=set(codes))
                            st.success(f"{t('recorded', lang)} · #{rec['seq']} · {rec['hash'][:16]}…")
                        except audit.AuditError as e:
                            st.error(str(e))
            st.markdown(f"**{t('context', lang)}**")
            for d in context_lines(col):
                st.markdown(f"- {d}")
    with st.expander(t("audit", lang)):
        ok, msg = audit.verify_chain()
        (st.success if ok else st.error)(msg)
        recs = audit.read_records()
        if recs:
            st.dataframe(pd.DataFrame(recs)[["seq", "ts_utc", "approver", "role", "decision", "reason_code",
                                             "band_id", "hash"]], hide_index=True, width="stretch")

elif page == "nav_alerts":
    st.subheader(t("nav_alerts", lang))
    st.markdown("Statement 06 asks for alert lead time, sensitivity, PPV, false alarms, data latency and behaviour "
                "when a feed is missing. The honest headline: **no forecast here, NABD's or the CDC's, warns of surge "
                "onset earlier than a simple threshold on the latest counts** (median lead about 0 weeks). The value we "
                "can show is precision (how often an alert is real) and magnitude (how big and how long).")
    alerts = data_io.load_alerts()
    us = alerts.get("US alerts_us")
    if us is None:
        not_computed("US alert metrics", "results/tables/alerts_us.csv")
    else:
        st.markdown("#### US state flu admissions (2024/25, 2025/26)")
        thr = sorted(us["T_per_100k"].unique())
        T = st.radio("Onset threshold (per 100k)", thr, index=thr.index(3.0) if 3.0 in thr else 0, horizontal=True)
        g = us[us.T_per_100k == T].copy()
        show = g[["season", "rule", "eligible_loc_seasons", "sensitivity_lead0to4", "median_lead_weeks_timely",
                  "ppv", "false_alarms_per_loc_season", "premature_gt4"]].rename(columns={
                      "eligible_loc_seasons": "eligible", "sensitivity_lead0to4": "sensitivity (lead 0–4 wk)",
                      "median_lead_weeks_timely": "median lead (wk)", "false_alarms_per_loc_season": "false alarms / loc-season",
                      "premature_gt4": "premature (>4 wk)"})
        st.dataframe(show.round(3), hide_index=True, width="stretch")
        ch = alt.Chart(g).mark_bar().encode(x=alt.X("rule:N", title=None), y=alt.Y("ppv:Q", title="PPV", scale=alt.Scale(domain=[0, 1])),
                                            color=alt.Color("rule:N", legend=None), column=alt.Column("season:N", title=None))
        st.altair_chart(ch.properties(width=180, height=200))
        st.caption("Rule D3 (docs/DEVIATIONS.md). Its thresholds were informed by probes that touched the test seasons "
                   "before the freeze (DEVIATIONS D5), so these metrics are **diagnostic**, not confirmatory.")
        for key, label in (("US latency_us", "Data latency (input-to-issue lag, stale rounds)"),
                           ("US dropout_us", "Missing-feed behaviour: WIS when inputs are truncated by 1–2 extra weeks")):
            if key in alerts:
                with st.expander(label):
                    st.dataframe(alerts[key], hide_index=True, width="stretch")
    st.markdown("#### UAE sentinel positivity (n = 4 seasons, descriptive)")
    uae_keys = [k for k in alerts if k.startswith("UAE ")]
    if not uae_keys:
        not_computed("UAE alert metrics under the pre-declared UAE alert rule", "results/uae/tables/alert*.csv")
    for k in uae_keys:
        st.markdown(f"**{k[4:]}**")
        st.dataframe(alerts[k], hide_index=True, width="stretch")
    if uae_keys:
        st.caption("Four seasons only: these are descriptive counts, not estimates with useful confidence intervals.")

elif page == "nav_us":
    summary = data_io.load_us_summary()
    tables = data_io.load_us_tables()
    st.subheader(t("verdict", lang))
    st.markdown("NABD-ensemble vs the CDC FluSight-ensemble on US state weekly flu admissions. Vintage-correct inputs, "
                "same truth for every model, relative WIS with bootstrap 95% CI, non-inferiority margin 1.15. The protocol "
                "was frozen before any test-season score (docs/FREEZE.md).")
    verdict, vtext = data_io.us_verdict(summary)
    if verdict is None:
        not_computed("pre-registered US primary endpoint", "results/summary.json")
    else:
        good = str(verdict).strip().upper() == "MET"
        st.markdown(f'<div class="{"nabd-verdict-good" if good else "nabd-verdict-bad"}" style="font-size:1.15rem">'
                    f'<span class="nabd-pill {"nabd-pill-good" if good else ""}">{verdict}</span>'
                    f'{vtext or ""}</div>', unsafe_allow_html=True)
        st.caption("Shown verbatim from results/summary.json. We set the bar at the CDC's best; v1 missed it.")
        s1 = (summary or {}).get("S1_vs_baseline")
        if isinstance(s1, dict) and s1.get("rel_wis") is not None:
            ci = s1.get("ci95") or [np.nan, np.nan]
            st.markdown(f"Secondary (S1), NABD vs FluSight-baseline (persistence): relative WIS **{s1['rel_wis']:.3f}** "
                        f"(95% CI {ci[0]:.3f}–{ci[1]:.3f}). The CI includes 1, so NABD is not shown to beat persistence.")
        ch2 = (summary or {}).get("chronos2")
        if ch2:
            st.caption(f"Chronos-2 foundation model: {ch2}")
    ep = tables.get("endpoints")
    if ep is not None:
        st.markdown("#### All pre-registered endpoints")
        cols = [c for c in ["analysis", "A", "B", "n_cells", "rel_wis", "ci_lo", "ci_hi", "cov50_A", "cov95_A"] if c in ep.columns]
        st.dataframe(ep[cols].round(3), hide_index=True, width="stretch")
    figs = [f for f in data_io.list_figures() if not f.name.startswith("league")]
    for fig in figs:
        st.image(str(fig), caption=fig.name)

    st.markdown("#### Where NABD v1 ranks among individual CDC FluSight hub models")
    league, lfigs = data_io.load_league()
    if not league:
        not_computed("league table (method declared before computing: docs/DEVIATIONS.md D7)", "results/tables/league*.csv")
    for name, df in league.items():
        st.markdown(f"**{name}**")
        st.dataframe(df, hide_index=True, width="stretch")
    for fig in lfigs:
        st.image(str(fig), caption=fig.name)

    sens = {k: v for k, v in tables.items() if any(s in k for s in ("sensitivity", "block", "per_location", "national", "sens_"))}
    if sens:
        with st.expander("Sensitivity analyses (declared in docs/DEVIATIONS.md D6; they do not change the verdict)"):
            for name, df in sens.items():
                st.markdown(f"**{name}**")
                st.dataframe(df, hide_index=True, width="stretch")
    expl = {k: v for k, v in tables.items() if "exploratory" in k}
    expl_summary = {k: v for k, v in (summary or {}).items() if isinstance(v, dict) and v.get("exploratory")}
    if expl or expl_summary:
        with st.expander("EXPLORATORY analyses (post hoc; not pre-registered; never a claim)"):
            exploratory_note()
            st.markdown("Phases in E1 are defined from realised truth, so the split favours wider intervals in rising cells. "
                        "It is **not** evidence that NABD 'does better in surges' (docs/DEVIATIONS.md E1).")
            for name, df in expl.items():
                st.dataframe(df, hide_index=True, width="stretch")
            if expl_summary:
                st.json(expl_summary, expanded=False)
    skip = set(sens) | set(expl) | set(league) | {"endpoints"} | {k for k in tables if k.startswith(("alerts_us", "latency_us", "dropout_us"))}
    tech = {k: v for k, v in tables.items() if k not in skip}
    if tech:
        with st.expander("Technical tables (cell coverage, vintage flags, tuning)"):
            for name, df in tech.items():
                st.markdown(f"**{name}**")
                st.dataframe(df, hide_index=True, width="stretch")

    st.divider()
    st.subheader("UAE retrospective (leave-one-season-out, n = 4 seasons)")
    uae = data_io.load_uae_summary()
    if uae is None:
        not_computed("UAE retrospective", "results/uae/summary.json")
    else:
        st.caption("Shown verbatim from results/uae/summary.json. Only 4 seasons: indicative, not definitive. "
                   "This is a retrospective evaluation, not pre-registered.")
        for key in [k for k in uae if k.startswith("rel_wis")]:
            block = uae[key]
            if not isinstance(block, dict):
                continue
            rows = [{"comparison": k, "rel_wis": v.get("rel_wis"), "ci95_low": (v.get("ci95") or [None, None])[0],
                     "ci95_high": (v.get("ci95") or [None, None])[1], "n_reference_dates": v.get("n_reference_dates")}
                    for k, v in block.items() if isinstance(v, dict)]
            if rows:
                st.markdown(f"**{key}**")
                st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
        st.json(uae, expanded=False)
        for name, df in data_io.load_uae_tables().items():
            if name == "ablation" or name.startswith("alert"):
                continue
            with st.expander(f"Table: {name}"):
                st.dataframe(df, hide_index=True, width="stretch")
        for fig in data_io.list_figures("uae"):
            st.image(str(fig), caption=fig.name)

elif page == "nav_gcc":
    st.subheader(t("nav_gcc", lang))
    st.markdown("Does the UAE method work on Gulf countries it was never tuned on? The frozen UAE method is run on other "
                "GCC/EMRO countries' WHO FluNet data. Inclusion rules were fixed and locked **before** that data was "
                "downloaded, and every included country is reported, losses included (BUILD-SPEC G12, docs/PREREG-GCC.md).")
    summary, tabs, figs = data_io.load_gcc()
    if summary is None and not tabs:
        not_computed("GCC out-of-sample test", "results/gcc/summary.json")
    else:
        if isinstance(summary, dict):
            v = summary.get("primary_verdict") or summary.get("verdict")
            txt = summary.get("primary_text") or summary.get("text")
            if v or txt:
                good = str(v).strip().upper() in {"MET", "PASS", "SUCCESS"}
                st.markdown(f'<div class="{"nabd-verdict-good" if good else "nabd-verdict-bad"}">'
                            + (f'<span class="nabd-pill {"nabd-pill-good" if good else ""}">{v}</span>' if v else "")
                            + f'{txt or ""}</div>', unsafe_allow_html=True)
            st.caption("Shown verbatim from results/gcc/summary.json. WHO FluNet values are final, revised data "
                       "(no vintages exist), so this is retrospective.")
            st.json(summary, expanded=False)
        for name, df in tabs.items():
            st.markdown(f"**{name}**")
            st.dataframe(df, hide_index=True, width="stretch")
        for fig in figs:
            st.image(str(fig), caption=fig.name)

elif page == "nav_ledger":
    rounds, scored, l_demo = data_io.load_ledger(observed)
    if l_demo:
        demo_banner()
    st.subheader(t("nav_ledger", lang))
    st.markdown("Every forecast round is committed **before** its target weeks are published. The hash below is "
                "recomputed from the file now and must match the recorded hash. Timestamps are self-attested until "
                "the repository is pushed publicly and the manifest is anchored outside the team (see ledger/README.md).")
    st.dataframe(rounds[[c for c in ["model", "issued_utc", "hash_matches", "git_commit_time", "sha256", "round_file"]
                         if c in rounds.columns]], hide_index=True, width="stretch")
    st.caption("hash_matches = recomputed SHA-256 equals the hash recorded at issue.")
    if not scored.empty:
        sc = scored.copy()
        for c in ("q10", "median", "q90"):
            sc[c] = pd.to_numeric(sc[c], errors="coerce").round(1)
        sc.insert(0, "model", sc.round_file.str.extract(r"Z_(.+)\.csv$")[0])
        sc = sc.drop(columns=["round_file"])
        sc["status"] = sc.inside_80pct_band.map({True: "inside 80% band", False: "outside 80% band", None: "awaiting data"})
        st.dataframe(sc, hide_index=True, width="stretch")
        n = sc.inside_80pct_band.notna().sum()
        if n:
            st.metric("Scored points inside 80% band", f"{int(sc.inside_80pct_band.sum())}/{int(n)}")
        st.caption("The ledger is an integrity device, not statistical evidence: counts at submission are small.")

elif page == "nav_ablation":
    st.subheader(t("nav_ablation", lang))
    st.markdown("What does each signal family add? The UAE model is re-run without one feed at a time "
                "(same protocol, leave-one-season-out), and the change in score is shown.")
    abl = data_io.load_uae_ablation()
    if abl is None or abl.empty:
        not_computed("UAE feed-removal ablation", "results/uae/tables/ablation.csv")
    else:
        metrics = list(pd.unique(abl["metric"])) if "metric" in abl.columns else []
        m = st.radio("Metric", metrics, horizontal=True) if metrics else None
        g = abl[abl.metric == m].copy() if m is not None else abl.copy()
        g["delta"] = pd.to_numeric(g.get("delta"), errors="coerce")
        if "full" in g.columns and "without" in g.columns:
            full = pd.to_numeric(g["full"], errors="coerce")
            g["pct_change"] = 100 * (pd.to_numeric(g["without"], errors="coerce") - full) / full
        ch = alt.Chart(g).mark_bar().encode(
            y=alt.Y("feed:N", sort="-x", title="feed removed"),
            x=alt.X("delta:Q", title=f"change in {m} when removed" if m else "change when removed"),
            color=alt.condition("datum.delta > 0", alt.value(ROSE), alt.value(TEAL)),
            tooltip=list(g.columns)).properties(height=40 * max(len(g), 3))
        st.altair_chart(ch, width="stretch")
        for r in g.itertuples():
            pct = getattr(r, "pct_change", np.nan)
            if pd.notna(r.delta):
                st.markdown(f"- Removing **{r.feed}** changes {m or 'the score'} by {r.delta:+.3f}"
                            + (f" ({pct:+.1f}%)" if pd.notna(pct) else "") + ".")
        st.caption("For error metrics such as WIS, a positive change means the forecast got worse without that feed, "
                   "so the feed was useful. Four seasons only.")
        st.dataframe(abl, hide_index=True, width="stretch")

elif page == "nav_workforce":
    sim_watermark()
    st.subheader(t("nav_workforce", lang))
    st.markdown("Synthetic employers report weekly respiratory sickness-absence counts. Each count is split into "
                "additive secret shares across three non-colluding servers, so **no server sees any employer's number**. "
                "A district total is released only if at least *k* employers contributed. **This module uses synthetic "
                "data only and feeds no forecast.**")
    k = st.slider("k (minimum employers per released cell)", 3, 25, 10)
    n = st.slider("Synthetic employers", 20, 200, 60, step=10)
    emp = synthetic_employers(n_employers=n)
    table, one_server = secure_aggregate(emp, k=k)
    table["status"] = table.released.map({True: "released", False: f"SUPPRESSED (<{k} employers)"})
    st.dataframe(table.drop(columns=["released"]), hide_index=True, width="stretch")
    with st.expander("What one aggregation server sees (random-looking share sums)"):
        st.dataframe(pd.DataFrame(one_server), hide_index=True)
    sim_watermark()

else:
    st.subheader(t("nav_about", lang))
    st.markdown("""
**What NABD is.** The UAE has no public respiratory forecasting hub. NABD is one: probabilistic RSV and influenza
forecasts for the UAE, with horizons stated relative to the issue date, held to the CDC FluSight standard in public,
and playbook actions that a named person must approve.

**What NABD does not claim.**
- It does not warn of surge *onset* earlier than a simple threshold on the latest counts (US alert analysis: median lead
  about 0 weeks).
- It did **not** meet its pre-registered US bar: non-inferiority to the CDC FluSight ensemble was NOT MET.
- No Abu Dhabi hospital, district or daily data are used. Every Abu Dhabi operational claim is a pilot hypothesis.
""")
    uae = data_io.load_uae_summary() or {}
    has = lambda p: (ROOT / p).exists()  # noqa: E731
    explain_built = has("results/uae/explain") and any((ROOT / "results/uae/explain").glob("*.csv"))
    rows = [
        ("WHO FluNet UAE sentinel flu and RSV positivity", "REAL", "data/raw (cached WHO FluNet)"),
        ("NABD-UAE forecasts, leave-one-season-out (n = 4 seasons)", "REAL", "results/uae/"),
        ("US back-test vs the CDC FluSight ensemble (verdict NOT MET)", "REAL", "results/summary.json"),
        ("Live forecast ledger round with SHA-256", "REAL (local until pushed and anchored)", "ledger/"),
        ("Hash-chained audit log of approve/modify/dismiss decisions", "REAL", "app/audit/audit.jsonl"),
        ("Card consistency gate (band, direction and action must agree)", "REAL", "app/cardcheck.py"),
        ("Per-signal explanations (UAE)", "REAL" if explain_built else "NOT YET COMPUTED", "results/uae/explain/"),
        ("Feed-removal ablation (UAE)", "REAL" if has("results/uae/tables/ablation.csv") else "NOT YET COMPUTED",
         "results/uae/tables/ablation.csv"),
        ("GCC out-of-sample test", "REAL" if has("results/gcc/summary.json") else "NOT YET COMPUTED", "results/gcc/"),
        ("League table among CDC hub models", "REAL" if list((ROOT / "results/tables").glob("league*.csv")) else "NOT YET COMPUTED",
         "results/tables/league*.csv"),
        ("Weather inputs (Abu Dhabi)", "USED" if any("weather" in str(x).lower() for x in (uae.get("signals") or []))
         else "NOT USED (not obtainable in the build environment)", "adapters/weather"),
        ("Playbook thresholds and actions", "ILLUSTRATIVE (not reviewed by a clinician or official)", "playbook/playbook.yaml"),
        ("Employer sickness-absence feed (secure aggregation)", "SIMULATED (synthetic data, feeds no forecast)", "app/workforce.py"),
        ("Abu Dhabi hospital, district or daily data", "NOT BUILT (pilot only)", "n/a"),
        ("Chronos-2 foundation model", "NOT RUN (weights unavailable here; reported only if run)", "models/chronos2.py"),
        ("Online calibration (ACI)", "NOT USED in v1", "models/config.yaml"),
        ("ED syndromic / geospatial inputs for NABD", "NOT BUILT", "n/a"),
    ]
    st.markdown("#### What's real / simulated / not built")
    st.dataframe(pd.DataFrame(rows, columns=["component", "status", "where"]), hide_index=True, width="stretch")
    st.markdown("""
**Other limitations.** UAE evaluation covers only 4 seasons (2022/23 is low-volume). WHO FluNet data are used for
public-health evaluation only (non-commercial terms); a hospital product would run on the hospital's own data.
Publication lags (FluNet about 10–11 days; NHSN weekly) are estimates. The ledger has few scored points at submission:
it is an integrity device, not statistical evidence.

**Card rules.** Direction labels need at least 60% probability (otherwise "uncertain"); "stable" means within ±10%
(minimum 1 percentage point) of the last published value. The playbook band uses the forecast level at the first
target week after issue and the forecast path (furthest median vs last value: rising ≥ 1.15×, falling ≤ 0.87×).

**Governance.** Aggregate data only; adapters reject person-level fields. Every decision is written to an append-only,
hash-chained audit log. Simulated layers carry a permanent watermark.
""")
